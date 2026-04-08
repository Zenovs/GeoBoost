#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::{Child, Command};
use std::sync::Mutex;
use std::path::PathBuf;
use std::time::Duration;
use std::thread;
use tauri::{Emitter, Manager};

struct BackendProcess(Mutex<Option<Child>>);

/// Walk up from `start` until we find `backend/main.py`
fn find_project_root(start: &PathBuf) -> Option<PathBuf> {
    let mut dir = start.clone();
    for _ in 0..10 {
        if dir.join("backend").join("main.py").exists() {
            return Some(dir);
        }
        if !dir.pop() {
            break;
        }
    }
    None
}

fn find_python(project_root: &PathBuf) -> String {
    let candidates = [
        project_root.join("venv").join("bin").join("python3"),
        project_root.join("venv").join("bin").join("python"),
        project_root.join("venv").join("Scripts").join("python.exe"),
    ];
    for c in &candidates {
        if c.exists() {
            return c.to_string_lossy().to_string();
        }
    }
    for py in &["python3", "python3.12", "python3.11", "python3.10", "python"] {
        if Command::new(py).arg("--version").output()
            .map(|o| o.status.success()).unwrap_or(false)
        {
            return py.to_string();
        }
    }
    "python3".to_string()
}

fn start_backend(project_root: &PathBuf) -> Option<Child> {
    let main_py = project_root.join("backend").join("main.py");
    if !main_py.exists() {
        eprintln!("[GeoBoost] ERROR: backend/main.py not found at {:?}", main_py);
        return None;
    }

    let python = find_python(project_root);
    eprintln!("[GeoBoost] python  = {}", python);
    eprintln!("[GeoBoost] main.py = {:?}", main_py);

    let mut cmd = Command::new(&python);
    cmd.arg(&main_py).current_dir(project_root);

    // On macOS, ensure Homebrew libs are in the dyld path for WeasyPrint
    #[cfg(target_os = "macos")]
    {
        let brew_lib = "/opt/homebrew/lib";
        let existing = std::env::var("DYLD_LIBRARY_PATH").unwrap_or_default();
        if !existing.contains(brew_lib) {
            let new_path = if existing.is_empty() {
                brew_lib.to_string()
            } else {
                format!("{}:{}", brew_lib, existing)
            };
            cmd.env("DYLD_LIBRARY_PATH", new_path);
        }
    }

    match cmd.spawn() {
        Ok(child) => {
            eprintln!("[GeoBoost] Backend started (PID {})", child.id());
            Some(child)
        }
        Err(e) => {
            eprintln!("[GeoBoost] Failed to start backend: {}", e);
            None
        }
    }
}

fn wait_for_backend(secs: u64) -> bool {
    let url = "http://127.0.0.1:8765/api/health";
    for _ in 0..(secs * 4) {
        if reqwest::blocking::get(url)
            .map(|r| r.status().is_success())
            .unwrap_or(false)
        {
            return true;
        }
        thread::sleep(Duration::from_millis(250));
    }
    false
}

#[tauri::command]
fn check_backend() -> bool {
    reqwest::blocking::get("http://127.0.0.1:8765/api/health")
        .map(|r| r.status().is_success())
        .unwrap_or(false)
}

#[tauri::command]
fn restart_backend(app_handle: tauri::AppHandle) -> bool {
    // 1. Kill current child
    if let Some(mut child) = app_handle
        .state::<BackendProcess>()
        .0.lock().unwrap().take()
    {
        let _ = child.kill();
        let _ = child.wait();
        eprintln!("[GeoBoost] Old backend killed for restart.");
    }
    // Also kill any stray processes
    let _ = Command::new("pkill").args(["-f", "backend/main.py"]).output();
    thread::sleep(Duration::from_millis(500));

    // 2. Find project root and restart
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(PathBuf::from))
        .unwrap_or_else(|| PathBuf::from("."));

    let project_root = find_project_root(&exe_dir)
        .or_else(|| find_project_root(&std::env::current_dir().unwrap_or(PathBuf::from("."))))
        .unwrap_or_else(|| std::env::current_dir().unwrap_or(PathBuf::from(".")));

    let child = start_backend(&project_root);
    {
        *app_handle.state::<BackendProcess>().0.lock().unwrap() = child;
    }

    // 3. Wait and notify UI
    let handle = app_handle.clone();
    thread::spawn(move || {
        let ready = wait_for_backend(20);
        eprintln!("[GeoBoost] Backend restarted, ready = {}", ready);
        if let Some(window) = handle.get_webview_window("main") {
            let _ = window.emit("backend-ready", ready);
        }
    });

    true
}

#[tauri::command]
fn open_pdf(path: String) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    Command::new("open").arg(&path).spawn().map_err(|e| e.to_string())?;
    #[cfg(target_os = "windows")]
    Command::new("cmd").args(["/C", "start", "", &path]).spawn().map_err(|e| e.to_string())?;
    #[cfg(target_os = "linux")]
    Command::new("xdg-open").arg(&path).spawn().map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .manage(BackendProcess(Mutex::new(None)))
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Resolve project root
            let exe_dir = std::env::current_exe()
                .ok()
                .and_then(|p| p.parent().map(PathBuf::from))
                .unwrap_or_else(|| PathBuf::from("."));

            let project_root = find_project_root(&exe_dir)
                .or_else(|| find_project_root(&std::env::current_dir().unwrap_or(PathBuf::from("."))))
                .unwrap_or_else(|| {
                    eprintln!("[GeoBoost] WARNING: Could not find project root, using cwd");
                    std::env::current_dir().unwrap_or(PathBuf::from("."))
                });

            eprintln!("[GeoBoost] project root = {:?}", project_root);

            // Kill any leftover backend from a previous session
            let _ = Command::new("pkill").args(["-f", "backend/main.py"]).output();
            thread::sleep(Duration::from_millis(200));

            // Start backend and store handle
            let child = start_backend(&project_root);
            {
                let state = app.state::<BackendProcess>();
                *state.0.lock().unwrap() = child;
            }

            // Wait for backend in background, then notify UI
            let handle = app.handle().clone();
            thread::spawn(move || {
                let ready = wait_for_backend(20);
                eprintln!("[GeoBoost] Backend ready = {}", ready);
                if let Some(window) = handle.get_webview_window("main") {
                    let _ = window.emit("backend-ready", ready);
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![check_backend, open_pdf, restart_backend])
        .build(tauri::generate_context!())
        .expect("error building tauri app")
        .run(|app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                if let Some(mut child) = app_handle
                    .state::<BackendProcess>()
                    .0.lock().unwrap().take()
                {
                    let _ = child.kill();
                    eprintln!("[GeoBoost] Backend stopped.");
                }
            }
        });
}

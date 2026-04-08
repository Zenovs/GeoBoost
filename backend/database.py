"""
GeoBoost – SQLite Datenbank
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent.parent / "config" / "geoboost.db"


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS audits (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id       INTEGER,
                    title            TEXT NOT NULL DEFAULT '',
                    client_name      TEXT NOT NULL DEFAULT '',
                    website_url      TEXT NOT NULL DEFAULT '',
                    status           TEXT NOT NULL DEFAULT 'draft',
                    current_step     INTEGER NOT NULL DEFAULT 0,
                    step0_kickoff    TEXT,
                    step1_website    TEXT,
                    step2_crawl      TEXT,
                    step3_semrush    TEXT,
                    step4_lighthouse TEXT,
                    step5_notes      TEXT,
                    pdf_path         TEXT,
                    created_at       TEXT DEFAULT (datetime('now')),
                    updated_at       TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    website_url TEXT NOT NULL,
                    ga4_property_id TEXT,
                    kickoff_data TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    checks_config TEXT,
                    status TEXT DEFAULT 'pending',
                    current_step TEXT DEFAULT '',
                    progress INTEGER DEFAULT 0,
                    status_message TEXT DEFAULT '',
                    error TEXT DEFAULT '',
                    results TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    completed_at TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );
            """)

    # ── Projects ──────────────────────────────────────────────────────────────

    def create_or_get_project(
        self,
        name: str,
        website_url: str,
        ga4_property_id: str,
        kickoff_data: dict,
    ) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM projects WHERE website_url = ? ORDER BY id DESC LIMIT 1",
                (website_url,),
            ).fetchone()
            if row:
                # Update kickoff data
                conn.execute(
                    "UPDATE projects SET name=?, ga4_property_id=?, kickoff_data=?, updated_at=datetime('now') WHERE id=?",
                    (name, ga4_property_id, json.dumps(kickoff_data), row["id"]),
                )
                return row["id"]
            cur = conn.execute(
                "INSERT INTO projects (name, website_url, ga4_property_id, kickoff_data) VALUES (?,?,?,?)",
                (name, website_url, ga4_property_id, json.dumps(kickoff_data)),
            )
            return cur.lastrowid

    def list_projects(self) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT p.*, COUNT(a.id) as analysis_count,
                       MAX(a.created_at) as last_analysis
                FROM projects p
                LEFT JOIN analyses a ON a.project_id = p.id
                GROUP BY p.id
                ORDER BY p.updated_at DESC
                """
            ).fetchall()
        return [dict(r) for r in rows]

    def get_project(self, project_id: int) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id=?", (project_id,)
            ).fetchone()
            if not row:
                return None
            project = dict(row)
            if project.get("kickoff_data"):
                project["kickoff_data"] = json.loads(project["kickoff_data"])
            analyses = conn.execute(
                "SELECT id, status, progress, status_message, created_at, completed_at FROM analyses WHERE project_id=? ORDER BY id DESC",
                (project_id,),
            ).fetchall()
            project["analyses"] = [dict(a) for a in analyses]
        return project

    def delete_project(self, project_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM analyses WHERE project_id=?", (project_id,))
            conn.execute("DELETE FROM projects WHERE id=?", (project_id,))

    # ── Analyses ──────────────────────────────────────────────────────────────

    def create_analysis(self, project_id: int, checks_config: dict) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO analyses (project_id, checks_config, status) VALUES (?,?,?)",
                (project_id, json.dumps(checks_config), "running"),
            )
            return cur.lastrowid

    def update_analysis_status(
        self, analysis_id: int, step: str, progress: int, message: str, error: str = ""
    ):
        status = "done" if progress >= 100 else ("error" if error else "running")
        completed_at = "datetime('now')" if progress >= 100 else "NULL"
        with self._conn() as conn:
            conn.execute(
                f"""UPDATE analyses
                    SET current_step=?, progress=?, status_message=?, error=?, status=?,
                        completed_at={"datetime('now')" if progress >= 100 else "completed_at"}
                    WHERE id=?""",
                (step, progress, message, error, status, analysis_id),
            )

    def get_analysis_status(self, analysis_id: int) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT current_step, progress, status_message, error, status FROM analyses WHERE id=?",
                (analysis_id,),
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            return {
                "step": d["current_step"],
                "progress": d["progress"],
                "message": d["status_message"],
                "error": d.get("error", ""),
                "done": d["progress"] >= 100,
            }

    def save_analysis_results(self, analysis_id: int, results: dict):
        with self._conn() as conn:
            conn.execute(
                "UPDATE analyses SET results=?, status='done', completed_at=datetime('now') WHERE id=?",
                (json.dumps(results), analysis_id),
            )

    def get_analysis_results(self, analysis_id: int) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM analyses WHERE id=?", (analysis_id,)
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            if d.get("results"):
                d["results"] = json.loads(d["results"])
            if d.get("checks_config"):
                d["checks_config"] = json.loads(d["checks_config"])
        return d


    # ── Audits ────────────────────────────────────────────────────────────────

    def create_audit(self, title: str, client_name: str = "", website_url: str = "",
                     project_id: int = None) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO audits (title, client_name, website_url, project_id) VALUES (?,?,?,?)",
                (title, client_name, website_url, project_id),
            )
            return cur.lastrowid

    def list_audits(self) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, title, client_name, website_url, status, current_step, "
                "pdf_path, created_at, updated_at FROM audits ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_audit(self, audit_id: int) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM audits WHERE id=?", (audit_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            for step in ["step0_kickoff", "step1_website", "step2_crawl",
                         "step3_semrush", "step4_lighthouse", "step5_notes"]:
                if d.get(step):
                    try:
                        d[step] = json.loads(d[step])
                    except Exception:
                        pass
        return d

    def update_audit_step(self, audit_id: int, step: int, data: dict):
        col_map = {
            0: "step0_kickoff", 1: "step1_website", 2: "step2_crawl",
            3: "step3_semrush", 4: "step4_lighthouse", 5: "step5_notes",
        }
        col = col_map.get(step)
        if col is None:
            return
        # Update client_name / website_url from kickoff step for display
        extra = ""
        params = [json.dumps(data)]
        if step == 0:
            extra = ", client_name=?, website_url=?"
            params += [data.get("client_name", ""), data.get("website_url", "")]
        status = "in_progress" if step > 0 else "draft"
        params += [status, audit_id]
        with self._conn() as conn:
            conn.execute(
                f"UPDATE audits SET {col}=?, status=?, current_step=MAX(current_step, ?), "
                f"updated_at=datetime('now'){extra} WHERE id=?",
                [json.dumps(data), status, step] + (
                    [data.get("client_name", ""), data.get("website_url", "")] if step == 0 else []
                ) + [audit_id],
            )

    def save_audit_pdf(self, audit_id: int, pdf_path: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE audits SET pdf_path=?, status='complete', updated_at=datetime('now') WHERE id=?",
                (pdf_path, audit_id),
            )

    def delete_audit(self, audit_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM audits WHERE id=?", (audit_id,))


# Type aliases for IDE hints
Project = dict
Analysis = dict

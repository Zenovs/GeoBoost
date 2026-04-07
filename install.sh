#!/bin/bash

# GA4 SEO Analyzer Installation Script

echo "Installing GA4 SEO Analyzer..."

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "Unsupported OS"
    exit 1
fi

echo "Detected OS: $OS"

# Install Python if not present
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    if [[ "$OS" == "macos" ]]; then
        brew install python
    elif [[ "$OS" == "linux" ]]; then
        sudo apt update && sudo apt install -y python3 python3-pip
    fi
fi

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    if [[ "$OS" == "macos" ]]; then
        brew install node
    elif [[ "$OS" == "linux" ]]; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
fi

# Install Rust if not present
if ! command -v cargo &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
fi

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    if [[ "$OS" == "macos" ]]; then
        brew install ollama
    elif [[ "$OS" == "linux" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
    ollama pull llama3.1:8b
fi

# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Install Playwright browsers
playwright install

# Build the app
cd ..
npm install
npm run tauri build

echo "Installation complete! Run the app with: npm run tauri dev"
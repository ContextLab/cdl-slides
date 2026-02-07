#!/usr/bin/env bash
set -euo pipefail

# Install system dependencies required for cdl-slides (manim rendering)
# Usage: ./scripts/install-system-deps.sh

case "$(uname -s)" in
    Linux*)
        if command -v apt-get &> /dev/null; then
            echo "Installing system dependencies via apt-get..."
            sudo apt-get update
            sudo apt-get install -y libpango1.0-dev libcairo2-dev ffmpeg
        elif command -v dnf &> /dev/null; then
            echo "Installing system dependencies via dnf..."
            sudo dnf install -y pango-devel cairo-devel ffmpeg
        elif command -v pacman &> /dev/null; then
            echo "Installing system dependencies via pacman..."
            sudo pacman -S --noconfirm pango cairo ffmpeg
        else
            echo "Error: Could not detect package manager (apt-get, dnf, or pacman)"
            exit 1
        fi
        ;;
    Darwin*)
        if command -v brew &> /dev/null; then
            echo "Installing system dependencies via Homebrew..."
            brew install pango cairo ffmpeg
        else
            echo "Error: Homebrew not found. Install from https://brew.sh"
            exit 1
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "Windows detected. System dependencies are bundled with Python packages."
        echo "No additional installation required."
        ;;
    *)
        echo "Error: Unsupported operating system: $(uname -s)"
        exit 1
        ;;
esac

echo "System dependencies installed successfully."

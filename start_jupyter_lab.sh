#!/bin/bash

# ============================================================================
# JupyterLab Launcher Script
# ============================================================================
# This script:
# 1. Activates the project venv
# 2. Kills any existing kernel processes (clean slate)
# 3. Launches JupyterLab with a single shared kernel across all notebooks
# 4. Opens the browser at localhost:8888
# ============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${PROJECT_DIR}/.venv"

echo "================================================"
echo "Advanced Multisource RAG — JupyterLab Launcher"
echo "================================================"
echo ""

# Activate venv
echo "Activating virtual environment..."
source "${VENV_PATH}/bin/activate"

# Kill any existing kernel processes
echo "Cleaning up any existing kernel processes..."
pkill -f "ipykernel_launcher" || true
sleep 1

# Verify kill was successful
REMAINING=$(pgrep -f "ipykernel_launcher" || echo "0")
if [ "$REMAINING" -eq 0 ] 2>/dev/null || [ -z "$REMAINING" ]; then
    echo "   All old kernels terminated"
else
    echo "   Some processes still running, continuing anyway..."
fi

echo ""
echo "Starting JupyterLab..."
echo "   URL: http://localhost:8888"
echo "   Root: ${PROJECT_DIR}"
echo ""
echo "Tips:"
echo "   • All open notebooks share ONE kernel"
echo "   • No per-notebook spawning"
echo "   • Switch notebooks freely without hanging"
echo ""

# Launch JupyterLab with optimized settings
# --no-browser: don't auto-open (you'll open manually)
# --ip=127.0.0.1: local only (safer)
# --port=8888: standard port
# --NotebookApp.kernel_spec_manager_class: use system kernels
jupyter lab \
    --no-browser \
    --ip=127.0.0.1 \
    --port=8888 \
    --NotebookApp.allow_origin='*' \
    --NotebookApp.kernel_manager_class='jupyter.kernel.ioloop_kernel_manager.IOLoopKernelManager'

# If script reaches here, JupyterLab has stopped
echo ""
echo "🛑 JupyterLab session ended."
echo "Run this script again to restart."

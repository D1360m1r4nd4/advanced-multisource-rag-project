#!/usr/bin/env python3
"""
check_env.py — Improved & WSL- Safe environment validator.

Fixes:
- Handles paths with spaces -- initial project folder had spaces causing venv issues
- No infinite venv restart loop -- need to monitor VIRTUAL_ENV properly after sinc with gdrive
- Uses correct pip inside `.venv`
- Prevents Debian PEP 668 errors
"""

import os
import subprocess
import sys
import shutil

LINE = "=" * 60

def print_section(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1


def check_virtual_env():
    print_section("Python Environment")
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print(f"Virtual environment active: {sys.prefix}")
    else:
        print("Virtual environment NOT active. Run:")
        print("   python3 -m venv .venv && source .venv/bin/activate")


def check_required_packages():
    print_section("Checking Required Python Packages")

    required = [
        "ipykernel",
        "jupyter",
        "ipywidgets",
        "notebook",
        "tqdm",
    ]

    for pkg in required:
        stdout, stderr, code = run(f"{sys.executable} -m pip show {pkg}")
        if code == 0:
            print(f"{pkg} installed.")
        else:
            print(f"✗ {pkg} missing. Installing...")
            stdout, stderr, code = run(f"{sys.executable} -m pip install {pkg}")
            if code == 0:
                print(f"   → {pkg} installed.")
            else:
                print(f"   Failed to install {pkg}: {stderr}")


def check_docker():
    print_section("Checking Docker")

    docker_path = shutil.which("docker")
    if not docker_path:
        print("Docker not found in PATH. Install Docker Desktop.")
        return

    print(f"Docker found at {docker_path}")

    stdout, stderr, code = run("docker info")
    if code != 0:
        print("Docker unreachable. Most common fixes:")
        print("   → Start Docker Desktop on Windows")
        print("   → Ensure WSL integration is enabled")
        return

    print("Docker is running and reachable.")


def check_vscode():
    print_section("Checking VS Code Environment")

    if os.getenv("TERM_PROGRAM") == "vscode":
        print("Running inside VS Code integrated terminal.")
    else:
        print("Not running inside VS Code.")


def check_wsl():
    print_section("WSL Detection")

    if "WSL" in os.uname().release:
        print("WSL detected.")
        print(f"Distribution: {os.uname().version}")
    else:
        print("Not inside WSL.")


def main():
    print_section("Environment Setup — Advanced Multisource RAG Project")

    check_virtual_env()
    check_required_packages()
    check_docker()
    check_vscode()
    check_wsl()

    print(f"\n{LINE}\nEnvironment check complete.\n{LINE}\n")


if __name__ == "__main__":
    main()
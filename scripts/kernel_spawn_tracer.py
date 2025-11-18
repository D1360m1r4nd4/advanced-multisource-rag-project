#!/usr/bin/env python3
"""
kernel_spawn_tracer.py

Polls for new `ipykernel_launcher` processes and logs parentage and cmdlines.
Useful to capture what is auto-spawning kernels (e.g. VS Code helpers).

Logs appended to ~/.cache/kernel_spawn_traces.log
"""
import os
import time
import subprocess
import shutil
from datetime import datetime

LOG = os.path.expanduser("~/.cache/kernel_spawn_traces.log")
MATCH = "ipykernel_launcher"
_NOTIFY = shutil.which("notify-send")


def now():
    return datetime.utcnow().isoformat() + 'Z'


def write(msg: str):
    line = f"[{now()}] {msg}\n"
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(line, end="")


def cmdline(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().replace(b"\0", b" ").decode(errors="replace").strip()
    except Exception:
        return ""


def ppid_for(pid: int) -> int:
    try:
        out = subprocess.check_output(["ps", "-p", str(pid), "-o", "ppid="], text=True)
        return int(out.strip())
    except Exception:
        return 0


def notify(title: str, msg: str):
    if not _NOTIFY:
        return
    try:
        subprocess.Popen([_NOTIFY, title, msg])
    except Exception:
        pass


def list_ipykernel_pids():
    try:
        out = subprocess.check_output(["pgrep", "-f", MATCH], text=True)
        return [int(l.strip()) for l in out.splitlines() if l.strip().isdigit()]
    except subprocess.CalledProcessError:
        return []


def main(poll_interval=2):
    seen = set()
    write("Starting kernel_spawn_tracer (match=%s)" % MATCH)
    try:
        while True:
            pids = list_ipykernel_pids()
            for pid in pids:
                if pid in seen:
                    continue
                seen.add(pid)
                cl = cmdline(pid)
                ppid = ppid_for(pid)
                parent_cl = cmdline(ppid) if ppid else ""
                msg = f"NEW KERNEL PID={pid} PPID={ppid} CMD='{cl}' PARENT_CMD='{parent_cl}'"
                write(msg)
                try:
                    notify("Kernel spawned", f"PID={pid} PPID={ppid}")
                except Exception:
                    pass
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        write("kernel_spawn_tracer stopped by user")


if __name__ == '__main__':
    main()

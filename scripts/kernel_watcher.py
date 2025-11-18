#!/usr/bin/env python3
"""
kernel_watcher.py

Monitor Jupyter kernel connection files and ipykernel processes. Actions:
 - Remove stale kernel-*.json files that are not referenced by any running ipykernel process
 - Detect long-running ipykernel processes (by elapsed time) and attempt a gentle shutdown

Usage (example):
  python scripts/kernel_watcher.py --runtime /run/user/1000/jupyter/runtime --interval 10 --max-age 300 --log ~/.cache/kernel_watcher.log --force-kill

Run with nohup to keep it in background:
  nohup python scripts/kernel_watcher.py &>/dev/null &

This script avoids extra dependencies and uses /proc and ps for process info.
"""
import argparse
import os
import signal
import subprocess
import time
import shutil
from datetime import datetime


def now():
    return datetime.utcnow().isoformat() + 'Z'


def log(msg, logfile=None):
    line = f"[{now()}] {msg}"
    print(line)
    if logfile:
        try:
            with open(logfile, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


# Desktop notify helper (uses notify-send if available)
_NOTIFY_CMD = shutil.which("notify-send")
def notify(title: str, message: str):
    if not _NOTIFY_CMD:
        return
    try:
        # fire-and-forget
        subprocess.Popen([_NOTIFY_CMD, title, message])
    except Exception:
        pass


def list_kernel_jsons(runtime_dir):
    try:
        return sorted([os.path.join(runtime_dir, f) for f in os.listdir(runtime_dir) if f.startswith("kernel-") and f.endswith('.json')])
    except FileNotFoundError:
        return []


def get_ipykernel_pids(match_cmd_substr='ipykernel_launcher'):
    # Use pgrep to find processes and filter by commandline contents
    pids = []
    try:
        out = subprocess.check_output(["pgrep", "-f", match_cmd_substr], text=True)
        for l in out.splitlines():
            line = l.strip()
            if line.isdigit():
                pids.append(int(line))
    except subprocess.CalledProcessError:
        # pgrep returns non-zero when no matches
        pass
    return pids


def cmdline_for_pid(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            data = f.read().replace(b"\0", b" ")
            return data.decode(errors='replace').strip()
    except Exception:
        return ""


def etimes_for_pid(pid):
    # etimes gives elapsed seconds for a pid from ps
    try:
        out = subprocess.check_output(["ps", "-p", str(pid), "-o", "etimes="], text=True)
        return int(out.strip())
    except Exception:
        return 0


def delete_file(path, logfile=None):
    try:
        os.remove(path)
        log(f"Deleted stale file: {path}", logfile)
        try:
            notify("Kernel watcher — deleted file", os.path.basename(path))
        except Exception:
            pass
    except Exception as e:
        log(f"Failed to delete {path}: {e}", logfile)


def gentle_shutdown(pid, logfile=None, wait=4, force=False):
    try:
        os.kill(pid, signal.SIGINT)
        log(f"SIGINT sent to {pid}", logfile)
        try:
            notify("Kernel watcher — shutting down", f"SIGINT sent to {pid}")
        except Exception:
            pass
    except ProcessLookupError:
        log(f"Process {pid} does not exist (already exited)", logfile)
        return
    except PermissionError:
        log(f"Permission denied sending SIGINT to {pid}", logfile)
        return

    # wait
    time.sleep(wait)
    # check
    try:
        os.kill(pid, 0)
        still_alive = True
    except ProcessLookupError:
        still_alive = False

    if not still_alive:
        log(f"Process {pid} exited after SIGINT", logfile)
        return

    # Try SIGTERM
    try:
        os.kill(pid, signal.SIGTERM)
        log(f"SIGTERM sent to {pid}", logfile)
    except Exception as e:
        log(f"Failed to send SIGTERM to {pid}: {e}", logfile)

    time.sleep(wait)

    try:
        os.kill(pid, 0)
        still_alive = True
    except ProcessLookupError:
        still_alive = False

    if still_alive and force:
        try:
            os.kill(pid, signal.SIGKILL)
            log(f"SIGKILL sent to {pid}", logfile)
        except Exception as e:
            log(f"Failed to SIGKILL {pid}: {e}", logfile)
    elif still_alive:
        log(f"Process {pid} still alive after SIGTERM; not killing (force disabled)", logfile)
    else:
        log(f"Process {pid} exited after SIGTERM", logfile)


def referenced_jsons_from_procs(pids, runtime_dir):
    refs = set()
    for pid in pids:
        cl = cmdline_for_pid(pid)
        # try to extract kernel-*.json path or base
        if runtime_dir in cl:
            # get basename
            parts = cl.split()
            for part in parts:
                if 'kernel-' in part and part.endswith('.json'):
                    refs.add(os.path.basename(part))
    return refs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default="/run/user/1000/jupyter/runtime", help="Jupyter runtime directory to watch")
    parser.add_argument("--interval", type=int, default=10, help="Polling interval in seconds")
    parser.add_argument("--max-age", type=int, default=300, help="Max elapsed seconds before kernel considered long-running")
    parser.add_argument("--log", default=os.path.expanduser("~/.cache/kernel_watcher.log"), help="Log file path")
    parser.add_argument("--force-kill", action="store_true", help="If set, send SIGKILL to processes that ignore SIGTERM")
    parser.add_argument("--match-cmd", default="ipykernel_launcher", help="Substring to match ipykernel processes (pgrep -f)")
    args = parser.parse_args()

    logfile = args.log
    runtime = args.runtime

    log(f"Starting kernel_watcher (runtime={runtime}, interval={args.interval}, max_age={args.max_age})", logfile)

    try:
        while True:
            # list kernel jsons
            jsons = list_kernel_jsons(runtime)

            # list ipykernel pids
            pids = get_ipykernel_pids(args.match_cmd)

            # referenced
            refs = referenced_jsons_from_procs(pids, runtime)

            # delete unreferenced jsons
            for j in jsons:
                base = os.path.basename(j)
                if base not in refs:
                    delete_file(j, logfile)

            # check long-running kernels
            for pid in pids:
                # confirm owned by current user
                try:
                    stat = os.stat(f"/proc/{pid}")
                    if stat.st_uid != os.getuid():
                        continue
                except Exception:
                    continue

                # Determine if this pid is associated with an active kernel JSON (i.e. referenced by a frontend)
                cl = cmdline_for_pid(pid)
                kernel_basename = None
                if runtime in cl:
                    parts = cl.split()
                    for part in parts:
                        if 'kernel-' in part and part.endswith('.json'):
                            kernel_basename = os.path.basename(part)
                            break

                # If the kernel is still referenced by a frontend (its kernel-*.json is in refs), skip shutdown
                if kernel_basename and kernel_basename in refs:
                    # active kernel — skip
                    continue

                et = etimes_for_pid(pid)
                if et >= args.max_age:
                    log(f"PID {pid} running for {et}s (>= {args.max_age}s) — attempting gentle shutdown (unreferenced)", logfile)
                    try:
                        notify("Kernel watcher — long-running kernel", f"PID {pid} running for {et}s (unreferenced)")
                    except Exception:
                        pass
                    gentle_shutdown(pid, logfile, wait=4, force=args.force_kill)

            time.sleep(args.interval)
    except KeyboardInterrupt:
        log("kernel_watcher stopped by user", logfile)


if __name__ == '__main__':
    main()

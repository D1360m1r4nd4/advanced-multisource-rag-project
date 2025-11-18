Kernel Watcher
===============

What it does
------------
- Watches the Jupyter runtime directory (default: `/run/user/1000/jupyter/runtime`).
- Removes stale `kernel-*.json` files that are not referenced by any running ipykernel process.
- Detects ipykernel processes running longer than a configurable threshold and attempts a gentle shutdown (SIGINT → SIGTERM → optional SIGKILL).

Quick start
-----------
Run once in background (example):

```bash
nohup python scripts/kernel_watcher.py --interval 10 --max-age 300 --log ~/.cache/kernel_watcher.log &
```

Run it manually:

```bash
python scripts/kernel_watcher.py --runtime /run/user/1000/jupyter/runtime --interval 10 --max-age 300
```

Options
-------
- `--runtime`: path to Jupyter runtime dir (default `/run/user/1000/jupyter/runtime`).
- `--interval`: poll interval in seconds (default 10).
- `--max-age`: elapsed seconds after which a kernel is considered long-running (default 300).
- `--log`: path to log file (default `~/.cache/kernel_watcher.log`).
- `--force-kill`: if present, the watcher will send SIGKILL to any process that ignores SIGTERM.
- `--match-cmd`: substring used to locate ipykernel processes (default `ipykernel_launcher`).

Systemd (optional)
-------------------
If you want the watcher to run continuously as a systemd user service, create a unit file `~/.config/systemd/user/kernel_watcher.service` with:

```
[Unit]
Description=Jupyter Kernel Watcher

[Service]
ExecStart=/usr/bin/env python /home/USERNAME/advanced-multisource-rag-project/scripts/kernel_watcher.py --interval 10 --max-age 300 --log /home/USERNAME/.cache/kernel_watcher.log
Restart=always

[Install]
WantedBy=default.target
```

Replace `USERNAME` with your user. Then enable and start with:

```bash
systemctl --user daemon-reload
systemctl --user enable --now kernel_watcher.service
```

Notes
-----
- The script is conservative: it only targets processes owned by the current user and uses `pgrep -f` to find ipykernel processes.
- It's intended as a helper to auto-recover from stuck kernels; it is not a substitute for investigating root causes (long-running cells, heavy embeddings, or extension auto-launchers).

If you'd like, I can:
- Install a systemd unit file for you (requires the correct username path).
- Run the watcher now in the background for testing.
- Add an option to email/notify when an action happens.

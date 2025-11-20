#!/usr/bin/env python3
"""
journal.py — Append timestamped entries to JOURNAL.md automatically.
"""

import sys
from datetime import datetime
from pathlib import Path

JOURNAL_FILE = Path("JOURNAL.md")

def main():
    if len(sys.argv) < 2:
        print("Usage: python journal.py \"Your entry text here\"")
        sys.exit(1)

    entry_text = " ".join(sys.argv[1:])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"\n---\n### 📝 {timestamp}\n{entry_text}\n"

    with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print("✅ Journal updated!")

if __name__ == "__main__":
    main()
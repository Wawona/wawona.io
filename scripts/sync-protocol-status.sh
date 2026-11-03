#!/usr/bin/env bash
# Copy Wawona docs/protocol-status.md into the Zola contributor page and
# turn Implementation paths into GitHub blob/master links.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WAWONA_REPO="${WAWONA_REPO:-$(cd "$ROOT/../Wawona" && pwd)}"
SRC="$WAWONA_REPO/docs/protocol-status.md"
OUT="$ROOT/content/docs/contributor/protocols.md"
test -f "$SRC" || { echo "missing $SRC" >&2; exit 1; }
python3 - "$SRC" "$OUT" <<'PY'
import re, sys
from pathlib import Path
from datetime import date

src, out = Path(sys.argv[1]), Path(sys.argv[2])
body = src.read_text()
lines = body.splitlines()
if lines and lines[0].startswith("# "):
    lines = lines[1:]
    if lines and lines[0] == "":
        lines = lines[1:]
body = "\n".join(lines).rstrip() + "\n"

BASE = "https://github.com/Wawona/Wawona/blob/master/"
pat = re.compile(r"(\| `[^=|]+` \| [^|]+ \| [^|]+ \| )`([^`]+)`( \| )")

def repl(m):
    prefix, cell, suffix = m.group(1), m.group(2), m.group(3)
    note = ""
    path = cell
    if " (" in cell and cell.endswith(")"):
        path, _, rest = cell.partition(" (")
        note = " (" + rest
    path = path.strip()
    if not path.startswith("src/"):
        return f"{prefix}`{cell}`{suffix}"
    link = f"[`{path}`]({BASE}{path})"
    return f"{prefix}{link}{note}{suffix}"

body, n = pat.subn(repl, body)
if n < 1:
    raise SystemExit("no Implementation cells linked")

today = date.today().isoformat()
fm = f"""+++
aliases = ["docs/protocols"]
title = "Protocol Support"
description = "Advertised Wayland globals from the live registry. Do not hand-edit this page."
weight = 24
date = {today}

+++

<!-- Generated from Wawona/docs/protocol-status.md (master). Implementation paths link to GitHub. -->

"""
out.write_text(fm + body)
print(f"wrote {out} ({n} implementation links)")
PY

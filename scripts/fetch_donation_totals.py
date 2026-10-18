#!/usr/bin/env python3
"""Write data/donation.json from Ko-fi goal progress plus GitHub Sponsors.

Raised dollars are:

    Ko-fi public goal progress
    + GitHub Sponsors lifetime amount received by aspauldingcode

Ko-fi has no read API. The public page prints whole-percent progress of the
active goal ("2% of $10000 goal"). That percent times the goal is the Ko-fi
figure. Cloudflare blocks plain curl, so the fetch uses a curl-impersonate
Chrome wrapper (CURL_IMPERSONATE, or curl_chrome* on PATH).

GitHub lifetime receipts are GraphQL lifetimeReceivedSponsorshipValues
(amountInCents, summed). Pass GH_TOKEN, GITHUB_TOKEN, or SPONSORS_READ_TOKEN.
SPONSORS_READ_TOKEN wins when set, so a maintainer token can be used in CI
without replacing the default Actions token.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "donation.json"

GITHUB_USER = "aspauldingcode"
KOFI_URL = "https://ko-fi.com/aspauldingcode"
GRAPHQL_URL = "https://api.github.com/graphql"

KOFI_GOAL_RE = re.compile(
    r'<span class="kfds-font-bold">\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*</span>\s*'
    r'<span class="goal-label"[^>]*>\s*of\s*\$([0-9][0-9,]*)\s*goal',
    re.IGNORECASE,
)

CHROME_WRAPPERS = (
    "curl_chrome146",
    "curl_chrome145",
    "curl_chrome142",
    "curl_chrome136",
    "curl_chrome133a",
    "curl_chrome131",
    "curl_safari260",
    "curl_safari184",
)

LIFETIME_QUERY = """
query($cursor: String) {
  user(login: "%s") {
    lifetimeReceivedSponsorshipValues(first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { amountInCents }
    }
  }
}
""" % GITHUB_USER


def dollars_to_cents(dollars: Decimal) -> int:
    return int((dollars * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cents_to_dollars(cents: int) -> int:
    return int(
        (Decimal(cents) / Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def parse_kofi_goal(html: str) -> tuple[Decimal, Decimal]:
    match = KOFI_GOAL_RE.search(html)
    if not match:
        raise ValueError("Ko-fi page has no public goal progress")
    percent = Decimal(match.group(1))
    goal = Decimal(match.group(2).replace(",", ""))
    if percent < 0 or goal < 0:
        raise ValueError("Ko-fi goal progress is negative")
    return percent, goal


def kofi_raised_cents(percent: Decimal, goal_usd: Decimal) -> int:
    return dollars_to_cents(percent * goal_usd / Decimal(100))


def sum_sponsor_cents(pages: list[list[dict]]) -> int:
    total = 0
    for nodes in pages:
        for node in nodes:
            amount = node.get("amountInCents")
            if amount is None:
                continue
            if amount < 0:
                raise ValueError("negative GitHub Sponsors amount")
            total += int(amount)
    return total


def impersonate_bin() -> str:
    chosen = os.environ.get("CURL_IMPERSONATE", "").strip()
    if chosen:
        path = Path(chosen)
        if path.is_file():
            return str(path)
        found = shutil.which(chosen)
        if found:
            return found
        raise SystemExit(f"CURL_IMPERSONATE is not executable: {chosen}")
    for name in CHROME_WRAPPERS:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(
        "curl-impersonate Chrome wrapper not on PATH. "
        "Set CURL_IMPERSONATE to curl_chrome146 (or another curl_chrome* binary)."
    )


def fetch_kofi_html(url: str = KOFI_URL) -> str:
    binary = impersonate_bin()
    # Write to a file. This curl build returns exit 27 when stdout is a pipe,
    # and it cannot overwrite a NamedTemporaryFile that Python still locked.
    fd, name = tempfile.mkstemp(prefix="wawona-kofi-", suffix=".html")
    os.close(fd)
    destination = Path(name)
    # CURL_IMPERSONATE is the wrapper path for this script. The child library
    # reads that same variable as a browser name and exits 27 if it is a path.
    child_env = os.environ.copy()
    child_env.pop("CURL_IMPERSONATE", None)
    completed = subprocess.run(
        [binary, "-sS", "-L", "--max-time", "60", "-o", str(destination), url],
        capture_output=True,
        check=False,
        env=child_env,
    )
    html = destination.read_text(encoding="utf-8", errors="replace") if destination.exists() else ""
    destination.unlink(missing_ok=True)
    if completed.returncode != 0 or "profileGoalTotal" not in html:
        err = (completed.stderr or b"").decode("utf-8", "replace").strip()
        raise SystemExit(
            f"Ko-fi fetch failed ({binary}, exit {completed.returncode}): {err or 'no goal widget'}"
        )
    return html


def github_env() -> dict[str, str]:
    env = os.environ.copy()
    # A maintainer token, when present, must win over the Actions token.
    # gh itself reads GH_TOKEN, so park the default and point GH_TOKEN at it.
    sponsor = env.get("SPONSORS_READ_TOKEN", "").strip()
    if sponsor:
        env["GH_TOKEN"] = sponsor
    return env


def github_graphql(variables: dict) -> dict:
    body = json.dumps({"query": LIFETIME_QUERY, "variables": variables}).encode()
    gh = shutil.which("gh")
    if gh:
        completed = subprocess.run(
            [gh, "api", "graphql", "--input", "-"],
            input=body,
            capture_output=True,
            env=github_env(),
            check=False,
        )
        if completed.returncode != 0:
            err = (completed.stderr or completed.stdout).decode("utf-8", "replace").strip()
            raise SystemExit(f"GitHub Sponsors query failed: {err}")
        return json.loads(completed.stdout.decode("utf-8"))
    token = os.environ.get("GH_TOKEN", "").strip() or os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise SystemExit("gh is not on PATH and GH_TOKEN is unset.")
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "wawona-io-donation-totals",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise SystemExit(f"GitHub GraphQL HTTP {exc.code}: {detail}") from exc


def github_lifetime_cents() -> int:
    pages: list[list[dict]] = []
    cursor: str | None = None
    while True:
        payload = github_graphql({"cursor": cursor})
        if payload.get("errors"):
            message = payload["errors"][0].get("message", "GraphQL error")
            raise SystemExit(f"GitHub Sponsors query failed: {message}")
        connection = (
            payload.get("data", {})
            .get("user", {})
            .get("lifetimeReceivedSponsorshipValues")
        )
        if not connection:
            raise SystemExit("GitHub Sponsors lifetime connection was empty")
        pages.append(connection.get("nodes") or [])
        page = connection.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
        if not cursor:
            break
    return sum_sponsor_cents(pages)


def build_record(kofi_html: str, github_cents: int) -> dict:
    percent, goal = parse_kofi_goal(kofi_html)
    kofi_cents = kofi_raised_cents(percent, goal)
    raised_cents = kofi_cents + github_cents
    return {
        "raised_usd": cents_to_dollars(raised_cents),
        "raised_cents": raised_cents,
        "kofi_usd": cents_to_dollars(kofi_cents),
        "kofi_cents": kofi_cents,
        "kofi_percent": float(percent),
        "kofi_goal_usd": int(goal),
        "github_sponsors_usd": cents_to_dollars(github_cents),
        "github_sponsors_cents": github_cents,
        "github_sponsors_user": GITHUB_USER,
        "kofi_url": KOFI_URL,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    html = fetch_kofi_html()
    record = build_record(html, github_lifetime_cents())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + "\n")
    print(
        f"wrote {OUT.relative_to(ROOT)} "
        f"raised_usd={record['raised_usd']} "
        f"kofi_usd={record['kofi_usd']} "
        f"github_sponsors_usd={record['github_sponsors_usd']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

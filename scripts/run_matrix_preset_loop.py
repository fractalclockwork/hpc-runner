#!/usr/bin/env python3
"""
Repeatedly load a saved Run Matrix preset from the HPC Regression API and submit the
same solver×system cells as the Run Matrix **Run selected** action.

Prerequisites
-------------
- **API running** and reachable (e.g. ``make api`` on the project host — default
  ``http://localhost:8000``).
- The preset label must already exist in the API database (save from the Run Matrix
  UI or ``PUT /api/matrix_presets/{label}``). The default label is ``all-solver``.

Environment
-----------
- ``HPC_API_URL`` — Base URL of the API (no trailing slash). Defaults to
  ``http://localhost:8000``.

Examples
--------
::

    export HPC_API_URL=http://localhost:8000
    python3 scripts/run_matrix_preset_loop.py --preset all-solver --sleep 60

    # Run each full matrix synchronously (one HTTP call per iteration; jobs run
    # sequentially inside the API) then pause 10s:
    python3 scripts/run_matrix_preset_loop.py --sync --sleep 10 --count 3

    # Background mode (default): wait until no active invocations before sleeping:
    python3 scripts/run_matrix_preset_loop.py --wait-idle --wait-timeout 7200

Stop an infinite loop with Ctrl+C.

This file is **standalone**: Python 3.10+ and the standard library only (no repo
packages or third-party dependencies). Copy it anywhere you can reach the API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def _default_base_url() -> str:
    return (os.environ.get("HPC_API_URL") or "http://localhost:8000").rstrip("/")


def _http_request(
    method: str,
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 120.0,
) -> tuple[int, bytes]:
    h = dict(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode() or 200, resp.read()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return e.code, body


def _json_loads(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def fetch_preset(base: str, label: str) -> tuple[str, list[dict[str, Any]]]:
    path = f"/api/matrix_presets/{urllib.parse.quote(label, safe='')}"
    status, body = _http_request("GET", base + path)
    if status == 404:
        print(f"error: preset not found: {label!r} (GET {path})", file=sys.stderr)
        sys.exit(1)
    if status != 200:
        text = body[:500].decode("utf-8", errors="replace")
        print(f"error: GET {path} failed: HTTP {status}\n{text}", file=sys.stderr)
        sys.exit(1)
    data = _json_loads(body)
    if not isinstance(data, dict):
        print("error: invalid JSON from matrix_presets", file=sys.stderr)
        sys.exit(1)
    cells = data.get("cells")
    if not isinstance(cells, list):
        print("error: preset response missing 'cells' list", file=sys.stderr)
        sys.exit(1)
    out: list[dict[str, Any]] = []
    for item in cells:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        system = (item.get("system") or "").strip()
        if name and system:
            out.append({"name": name, "system": system})
    lab = (data.get("label") or label).strip() or label
    return lab, out


def post_run_solvers(
    base: str,
    solvers: list[dict[str, Any]],
    *,
    background: bool,
    session_label: str | None,
) -> tuple[int, Any]:
    payload: dict[str, Any] = {
        "solvers": solvers,
        "background": background,
    }
    if session_label:
        payload["session_label"] = session_label
    raw = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    status, body = _http_request(
        "POST",
        base + "/api/run_solvers",
        data=raw,
        headers=headers,
        timeout=86400.0 if not background else 120.0,
    )
    return status, _json_loads(body)


def get_active_invocations(base: str) -> list[Any]:
    url = base + "/api/invocations?" + urllib.parse.urlencode({"active_only": "true"})
    status, body = _http_request("GET", url, timeout=60.0)
    if status != 200:
        return []
    data = _json_loads(body)
    return data if isinstance(data, list) else []


def wait_until_idle(
    base: str,
    *,
    poll_interval: float,
    timeout_sec: float,
) -> bool:
    """Poll until no active invocations or timeout. Returns True if idle, False if timed out."""
    start = time.monotonic()
    while True:
        rows = get_active_invocations(base)
        if len(rows) == 0:
            return True
        if timeout_sec > 0 and (time.monotonic() - start) >= timeout_sec:
            return False
        remaining = timeout_sec - (time.monotonic() - start) if timeout_sec > 0 else poll_interval
        time.sleep(min(poll_interval, max(remaining, 0.5)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Loop: load a Run Matrix preset and POST /api/run_solvers repeatedly.",
    )
    parser.add_argument(
        "--preset",
        default="all-solver",
        help="Saved preset label (default: all-solver)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        metavar="N",
        help="Number of iterations (0 = infinite until Ctrl+C)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        metavar="SEC",
        help="Seconds to sleep after each successful iteration (default: 0)",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="POST with background=false (sequential jobs in one request); default is background mode (202)",
    )
    parser.add_argument(
        "--no-session-label",
        action="store_true",
        help="Do not send session_label in the run_solvers body",
    )
    parser.add_argument(
        "--session-label",
        default=None,
        metavar="TEXT",
        help="Override session_label (default: preset label from API)",
    )
    parser.add_argument(
        "--wait-idle",
        action="store_true",
        help="After each background run, wait until no active invocations before sleeping",
    )
    parser.add_argument(
        "--wait-timeout",
        type=float,
        default=0.0,
        metavar="SEC",
        help="Max seconds to wait for idle (0 = no limit; only with --wait-idle)",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=4.0,
        metavar="SEC",
        help="Seconds between invocations polls when using --wait-idle (default: 4)",
    )
    args = parser.parse_args(argv)

    use_background = not args.sync  # default: background=true like Run Matrix
    if args.wait_idle and not use_background:
        print("warning: --wait-idle applies to background mode only; ignoring", file=sys.stderr)

    base = _default_base_url()
    iteration = 0

    while True:
        if args.count > 0 and iteration >= args.count:
            break
        iteration += 1

        preset_label, solvers = fetch_preset(base, args.preset)
        if not solvers:
            print(
                f"error: preset {preset_label!r} has no valid cells (name+system pairs)",
                file=sys.stderr,
            )
            return 1

        if args.no_session_label:
            session: str | None = None
        elif args.session_label is not None:
            session = args.session_label.strip() or None
        else:
            session = preset_label

        status, resp = post_run_solvers(
            base,
            solvers,
            background=use_background,
            session_label=session,
        )

        ok = (use_background and status == 202) or (not use_background and status == 200)
        snippet = resp
        if isinstance(resp, (dict, list)):
            snippet_str = json.dumps(resp, indent=2)[:2000]
        else:
            snippet_str = str(resp)[:2000]

        print(f"[{iteration}] POST /api/run_solvers HTTP {status} background={use_background}")
        print(snippet_str)

        if not ok:
            print("error: run_solvers request failed", file=sys.stderr)
            return 1

        if args.wait_idle and use_background:
            if not wait_until_idle(
                base,
                poll_interval=max(0.5, args.poll_interval),
                timeout_sec=max(0.0, args.wait_timeout),
            ):
                print(
                    f"error: timed out after {args.wait_timeout}s waiting for idle invocations",
                    file=sys.stderr,
                )
                return 1

        if args.sleep > 0:
            time.sleep(args.sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the repository-local Markdown terminology checker and retain diagnostics."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("audit", "enforce"), default="audit")
    parser.add_argument("--scope", choices=("full", "changed", "files"), default="full")
    parser.add_argument("--files", nargs="*", default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def git_head(root: Path) -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def main() -> int:
    args = parse_args()
    script = Path(__file__).resolve()
    root = script.parents[3]
    checker = script.with_name("check-markdown-whitelist-sudachi.py")
    output = args.output_dir.resolve()
    if output.exists():
        print(f"--output-dir must not already exist: {output}", file=sys.stderr)
        return 2
    output.mkdir(parents=True)

    command = [sys.executable, str(checker), "--list-unknown"]
    if args.scope == "changed":
        command.append("--changed")
    elif args.scope == "files":
        if not args.files:
            print("--files is required when --scope files is selected.", file=sys.stderr)
            return 2
        command.extend(["--files", *args.files])

    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        encoding="utf-8",
        capture_output=True,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    (output / "stdout.log").write_text(result.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(result.stderr, encoding="utf-8")

    if result.returncode == 0:
        state = "pass"
    elif result.returncode == 1 and "Markdown whitelist violations:" in result.stderr:
        state = "needs_user_review"
    else:
        state = "failed"

    summary = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "scope": args.scope,
        "files": args.files,
        "repository": str(root),
        "head_sha": git_head(root),
        "checker_exit_code": result.returncode,
        "state": state,
        "stdout": "stdout.log",
        "stderr": "stderr.log",
        "command": command,
    }
    (output / "result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print(f"result={state}; diagnostics={output}")

    if state == "failed":
        return result.returncode or 2
    if args.mode == "enforce" and state == "needs_user_review":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

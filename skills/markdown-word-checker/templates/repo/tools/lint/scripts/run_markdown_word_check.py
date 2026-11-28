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
    command = [sys.executable, str(checker), "--list-unknown"]
    if args.scope == "changed":
        command.append("--changed")
    elif args.scope == "files":
        if not args.files:
            print("--files is required when --scope files is selected.", file=sys.stderr)
            return 2
        command.extend(["--files", *args.files])

    if args.files and args.scope != "files":
        print("--files is only allowed with --scope files.", file=sys.stderr)
        return 2
    try:
        output = args.output_dir.resolve()
        diagnostics_root = root / "tools" / "lint" / "artifacts"
        relative = output.relative_to(diagnostics_root)
        if not relative.parts or args.output_dir.is_symlink():
            raise ValueError("use a new directory inside tools/lint/artifacts/")
        output.mkdir(parents=True)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Diagnostics output rejected: {error}", file=sys.stderr)
        return 2

    checked_head = None
    try:
        checked_head = git_head(root)
        if checked_head is None:
            raise OSError("Git HEAD could not be identified.")
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            encoding="utf-8",
            capture_output=True,
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )
    except (OSError, UnicodeError) as error:
        result = subprocess.CompletedProcess(command, 2, "", f"Checker could not run: {error}\n")

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
        "head_sha": checked_head,
        "checker_exit_code": result.returncode,
        "state": state,
        "stdout": "stdout.log",
        "stderr": "stderr.log",
        "command": command,
    }
    try:
        (output / "stdout.log").write_text(result.stdout, encoding="utf-8")
        (output / "stderr.log").write_text(result.stderr, encoding="utf-8")
        (output / "result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Could not save complete diagnostics: {error}", file=sys.stderr)
        return 2

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

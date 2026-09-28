#!/usr/bin/env python3
"""Install repository-local Markdown terminology tooling into a target Git worktree."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
CODEXSKILL_ROOT = SCRIPT_PATH.parents[3]
SKILL_ROOT = SCRIPT_PATH.parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "templates" / "repo"
CHECKER_SOURCE = CODEXSKILL_ROOT / "skills" / "review-enforcer" / "scripts" / "check-markdown-whitelist-sudachi.py"
CHECKER_DESTINATION = Path("tools/lint/scripts/check-markdown-whitelist-sudachi.py")
CI_PATH = Path(".github/workflows/markdown-word-check.yml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="Target repository worktree root.")
    parser.add_argument("--with-ci", action="store_true", help="Also install the audit-mode GitHub Actions workflow.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned files without writing them.")
    return parser.parse_args()


def resolve_git_root(target: Path) -> Path:
    target = target.resolve()
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Target is not a Git worktree: {target}\n{result.stderr.strip()}")
    git_root = Path(result.stdout.strip()).resolve()
    if git_root != target:
        raise RuntimeError(f"--target must be the Git worktree root. resolved={git_root}")
    return git_root


def template_files(with_ci: bool) -> list[tuple[Path, Path]]:
    rows: list[tuple[Path, Path]] = []
    for source in sorted(TEMPLATE_ROOT.rglob("*")):
        if not source.is_file():
            continue
        if "__pycache__" in source.parts or source.suffix in {".pyc", ".pyo"}:
            continue
        relative = source.relative_to(TEMPLATE_ROOT)
        if relative == CI_PATH and not with_ci:
            continue
        rows.append((source, relative))
    rows.append((CHECKER_SOURCE, CHECKER_DESTINATION))
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    if not TEMPLATE_ROOT.is_dir():
        print(f"Missing bootstrap template: {TEMPLATE_ROOT}", file=sys.stderr)
        return 2
    if not CHECKER_SOURCE.is_file():
        print(f"Missing canonical checker: {CHECKER_SOURCE}", file=sys.stderr)
        return 2

    try:
        target = resolve_git_root(args.target)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2

    plan = template_files(args.with_ci)
    conflicts = [relative for _, relative in plan if (target / relative).exists()]
    if conflicts:
        print("Bootstrap stopped because target files already exist:", file=sys.stderr)
        for relative in conflicts:
            print(f"- {relative.as_posix()}", file=sys.stderr)
        return 3

    print(f"target={target}")
    print(f"checker_sha256={sha256(CHECKER_SOURCE)}")
    for _, relative in plan:
        print(f"create {relative.as_posix()}")

    if args.dry_run:
        print("dry-run: no files written")
        return 0

    for source, relative in plan:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    print(f"created={len(plan)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

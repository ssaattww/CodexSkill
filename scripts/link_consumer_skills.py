#!/usr/bin/env python3
"""Create a consumer repository symlink to this CodexSkill checkout's skills directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "consumer_repo",
        type=Path,
        help="Consumer repository root that should receive .agents/skills.",
    )
    args = parser.parse_args()

    codexskill_root = Path(__file__).resolve().parents[1]
    source = (codexskill_root / "skills").resolve()
    consumer = args.consumer_repo.resolve()
    link = consumer / ".agents" / "skills"

    if not source.is_dir():
        print(f"CodexSkill skills directory does not exist: {source}", file=sys.stderr)
        return 2
    if not consumer.is_dir():
        print(f"Consumer repository does not exist: {consumer}", file=sys.stderr)
        return 2

    if link.is_symlink():
        try:
            current_target = link.resolve(strict=True)
        except OSError as error:
            print(f"Existing skill symlink is broken: {link}: {error}", file=sys.stderr)
            return 2
        if current_target == source:
            print(f"Skill symlink already configured: {link} -> {source}")
            return 0
        print(
            f"Refusing to replace existing skill symlink: {link} -> {current_target}",
            file=sys.stderr,
        )
        return 2

    if link.exists():
        print(
            f"Refusing to replace existing non-symlink path: {link}",
            file=sys.stderr,
        )
        return 2

    try:
        link.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(
            f"Failed to prepare consumer skill link directory {link.parent}: {error}",
            file=sys.stderr,
        )
        return 2

    try:
        link.symlink_to(source, target_is_directory=True)
    except OSError as error:
        if os.name == "nt" and getattr(error, "winerror", None) == 1314:
            print(
                "Windows denied symbolic-link creation. Run from an elevated shell "
                "or enable Windows Developer Mode.",
                file=sys.stderr,
            )
        else:
            print(f"Failed to create skill symlink: {error}", file=sys.stderr)
        return 2

    if not link.is_symlink() or link.resolve(strict=True) != source:
        print(f"Skill symlink verification failed: {link}", file=sys.stderr)
        return 2

    print(f"Created skill symlink: {link} -> {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

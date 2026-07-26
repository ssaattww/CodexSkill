#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

IGNORED_NAMES = {".DS_Store", "__pycache__"}
LEGACY_GENERATED_FILES = {"references/handoff-contract.md"}
GENERATED_DIRECTORY = Path("references/shared")


def find_committed_generated_copies(repo_root: Path) -> list[Path]:
    violations: list[Path] = []
    skills_root = repo_root / "skills"

    for skill_file in sorted(skills_root.glob("chat-*/SKILL.md")):
        skill_dir = skill_file.parent

        generated_root = skill_dir / GENERATED_DIRECTORY
        if generated_root.exists():
            violations.extend(
                path
                for path in generated_root.rglob("*")
                if path.is_file() and path.name not in IGNORED_NAMES
            )

        for relative in LEGACY_GENERATED_FILES:
            legacy_copy = skill_dir / relative
            if legacy_copy.is_file():
                violations.append(legacy_copy)

    return sorted(set(violations))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    violations = find_committed_generated_copies(repo_root)
    if not violations:
        print(
            "Verified: ChatGPT Skill shared dependencies exist only in shared/ "
            "and are generated during bundle staging."
        )
        return 0

    print(
        "error: generated ChatGPT Skill dependency copies must not be committed; "
        "keep the canonical files under shared/ and let the release builder copy "
        "them into its temporary staging directory:",
        file=sys.stderr,
    )
    for path in violations:
        print(f"- {path.relative_to(repo_root).as_posix()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

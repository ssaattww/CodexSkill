#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

MARKDOWN_LINK_RE = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\()"
    r"(?P<target>[^)\s]+)"
    r"(?P<suffix>(?:\s+[\"'][^\"']*[\"'])?\))"
)
FENCED_CODE_RE = re.compile(r"^\s*```.*?^\s*```\s*$", re.MULTILINE | re.DOTALL)
MARKDOWN_SUFFIXES = {".md", ".markdown"}
IGNORED_NAMES = {".DS_Store", "__pycache__"}
FORBIDDEN_RUNTIME_ROOTS = (
    Path("shared/workflow"),
    Path("shared/chat-worker"),
)
FORBIDDEN_LINK_PARTS = (
    "shared/workflow/",
    "shared/chat-worker/",
)
REQUIRED_RELEASE_SKILLS = {
    "chat-handoff-manager",
    "chat-implementation-worker",
    "chat-report-writer",
    "chat-review-worker",
    "implementation-worker",
    "progress-sync-manager",
    "report-writer",
    "review-worker",
    "task-breakdown-planner",
    "task-consistency-manager",
    "work-context-manager",
}
WRAPPER_DEPENDENCIES = {
    "chat-implementation-worker": {
        "work-context-manager",
        "task-consistency-manager",
        "task-breakdown-planner",
        "implementation-worker",
        "progress-sync-manager",
        "report-writer",
        "chat-handoff-manager",
    },
    "chat-review-worker": {
        "work-context-manager",
        "review-worker",
        "report-writer",
        "chat-handoff-manager",
    },
    "chat-report-writer": {
        "work-context-manager",
        "report-writer",
        "chat-handoff-manager",
    },
    "implementation-executor": {
        "work-context-manager",
        "implementation-worker",
    },
    "review-enforcer": {
        "work-context-manager",
        "review-worker",
        "report-writer",
        "report-output-manager",
    },
    "report-output-manager": {
        "work-context-manager",
        "report-writer",
    },
    "tdd-executor": {
        "work-context-manager",
        "implementation-executor",
        "implementation-worker",
    },
    "development-orchestrator": {
        "work-context-manager",
        "implementation-executor",
        "review-enforcer",
        "report-output-manager",
    },
}


class ValidationError(RuntimeError):
    pass


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def split_anchor(target: str) -> tuple[str, str]:
    if "#" not in target:
        return target, ""
    path_part, anchor = target.split("#", 1)
    return path_part, anchor


def read_skill_name(skill_file: Path) -> str:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValidationError(f"{skill_file}: missing YAML front matter")

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()

    raise ValidationError(f"{skill_file}: front matter has no name")


def iter_active_markdown(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []

    for relative in (Path("README.md"), Path("AGENTS.md")):
        path = repo_root / relative
        if path.is_file():
            candidates.append(path)

    for root_name in ("design", "skills", "tasks"):
        root = repo_root / root_name
        if not root.is_dir():
            continue
        candidates.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.suffix.lower() in MARKDOWN_SUFFIXES
            and path.name not in IGNORED_NAMES
        )

    return sorted(set(candidates))


def validate_skill_inventory(repo_root: Path) -> list[str]:
    errors: list[str] = []
    skills_root = repo_root / "skills"
    discovered: dict[str, Path] = {}

    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        skill_dir = skill_file.parent
        try:
            declared_name = read_skill_name(skill_file)
        except ValidationError as error:
            errors.append(str(error))
            continue

        if declared_name != skill_dir.name:
            errors.append(
                f"{skill_file.relative_to(repo_root)}: declared name "
                f"{declared_name!r} does not match directory {skill_dir.name!r}"
            )
        if declared_name in discovered:
            errors.append(
                f"duplicate Skill name {declared_name!r}: "
                f"{discovered[declared_name].relative_to(repo_root)} and "
                f"{skill_file.relative_to(repo_root)}"
            )
        discovered[declared_name] = skill_file

        for path in skill_dir.rglob("*"):
            if path.is_symlink():
                errors.append(
                    f"{path.relative_to(repo_root)}: symlinks are not allowed in Skills"
                )

    missing_release = sorted(REQUIRED_RELEASE_SKILLS - discovered.keys())
    if missing_release:
        errors.append(f"missing required release Skills: {missing_release}")

    for wrapper_name, dependencies in sorted(WRAPPER_DEPENDENCIES.items()):
        wrapper_file = discovered.get(wrapper_name)
        if wrapper_file is None:
            errors.append(f"missing wrapper Skill: {wrapper_name}")
            continue
        content = wrapper_file.read_text(encoding="utf-8")
        for dependency in sorted(dependencies):
            if dependency not in discovered:
                errors.append(
                    f"{wrapper_file.relative_to(repo_root)}: dependency Skill "
                    f"{dependency!r} is not installed in the repository"
                )
            if f"`{dependency}`" not in content:
                errors.append(
                    f"{wrapper_file.relative_to(repo_root)}: required dependency "
                    f"{dependency!r} is not declared by Skill name"
                )

    return errors


def validate_markdown_links(repo_root: Path) -> list[str]:
    errors: list[str] = []
    repo_root = repo_root.resolve()

    for markdown_file in iter_active_markdown(repo_root):
        content = markdown_file.read_text(encoding="utf-8")
        active_content = FENCED_CODE_RE.sub("", content)

        for match in MARKDOWN_LINK_RE.finditer(active_content):
            target = match.group("target")
            if (
                target.startswith(("http://", "https://", "mailto:", "#", "/"))
                or "://" in target
            ):
                continue

            path_part, _anchor = split_anchor(target)
            if not path_part:
                continue

            normalized_target = path_part.replace("\\", "/")
            if any(part in normalized_target for part in FORBIDDEN_LINK_PARTS):
                errors.append(
                    f"{markdown_file.relative_to(repo_root)}: forbidden runtime "
                    f"dependency link: {target}"
                )

            unresolved = markdown_file.parent / path_part
            if unresolved.is_symlink():
                errors.append(
                    f"{markdown_file.relative_to(repo_root)}: linked path is a "
                    f"symlink: {target}"
                )
                continue

            resolved = unresolved.resolve()
            if not is_relative_to(resolved, repo_root):
                errors.append(
                    f"{markdown_file.relative_to(repo_root)}: relative Markdown "
                    f"link escapes repository: {target}"
                )
                continue

            if not resolved.exists():
                errors.append(
                    f"{markdown_file.relative_to(repo_root)}: broken relative "
                    f"Markdown link: {target}"
                )

    return errors


def validate_removed_architecture(repo_root: Path) -> list[str]:
    errors: list[str] = []

    for relative in FORBIDDEN_RUNTIME_ROOTS:
        path = repo_root / relative
        if path.exists():
            errors.append(
                f"{relative.as_posix()}: deleted shared-runtime architecture "
                "must not be reintroduced"
            )

    obsolete_validator = repo_root / "scripts/verify_no_committed_chatgpt_skill_copies.py"
    if obsolete_validator.exists():
        errors.append(
            "scripts/verify_no_committed_chatgpt_skill_copies.py: obsolete "
            "shared-copy validator must be removed"
        )

    return errors


def validate_design_sync(repo_root: Path) -> list[str]:
    canonical = repo_root / "design/skill-hierarchy-design.md"
    mirrored = repo_root / "skills/design/skill-hierarchy-design.md"
    if not canonical.is_file() or not mirrored.is_file():
        return ["both hierarchy design files must exist"]
    if canonical.read_bytes() != mirrored.read_bytes():
        return [
            "design/skill-hierarchy-design.md and "
            "skills/design/skill-hierarchy-design.md must be byte-identical"
        ]
    return []


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    errors.extend(validate_skill_inventory(repo_root))
    errors.extend(validate_markdown_links(repo_root))
    errors.extend(validate_removed_architecture(repo_root))
    errors.extend(validate_design_sync(repo_root))

    if errors:
        print("error: Skill repository validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Verified: Skill names and dependencies are consistent, active relative "
        "Markdown links resolve, deleted shared-runtime paths are absent, no Skill "
        "uses symlinks, and hierarchy designs are synchronized."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

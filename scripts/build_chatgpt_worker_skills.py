#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

CORE_SKILLS = {
    "work-context-manager",
    "implementation-worker",
    "review-worker",
    "report-writer",
}
TASK_TRACKING_SKILLS = {
    "task-breakdown-planner",
    "task-consistency-manager",
    "progress-sync-manager",
}
IGNORED_NAMES = {"__pycache__", ".DS_Store"}


class BundleError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build one ChatGPT Skill-set ZIP containing every chat-* wrapper, "
            "the parent-independent core Skills they invoke, and the task "
            "tracking Skills required to update repository task state."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("chatgpt-worker-skills.zip"),
    )
    return parser.parse_args()


def read_skill_name(skill_file: Path) -> str:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise BundleError(f"{skill_file}: missing YAML front matter")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    raise BundleError(f"{skill_file}: front matter has no name")


def discover_skill_dirs(repo_root: Path) -> list[Path]:
    skills_root = repo_root / "skills"
    names = {
        path.parent.name
        for path in skills_root.glob("chat-*/SKILL.md")
    } | CORE_SKILLS | TASK_TRACKING_SKILLS

    skill_dirs: list[Path] = []
    for name in sorted(names):
        skill_dir = skills_root / name
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            raise BundleError(f"Required Skill is missing: {skill_file}")
        declared_name = read_skill_name(skill_file)
        if declared_name != name:
            raise BundleError(
                f"{skill_file}: declared name {declared_name!r} "
                f"does not match directory {name!r}"
            )
        skill_dirs.append(skill_dir)
    return skill_dirs


def verify_source_skill(skill_dir: Path) -> None:
    for path in skill_dir.rglob("*"):
        if path.is_symlink():
            raise BundleError(f"{path}: symlinks are not allowed")
        if not path.is_file():
            continue
        if path.name in IGNORED_NAMES:
            continue
        if path.suffix.lower() in {".md", ".markdown"}:
            content = path.read_text(encoding="utf-8")
            if "../../shared/" in content or "../shared/" in content:
                raise BundleError(
                    f"{path}: Skill depends on repository-external shared files"
                )


def copy_skill(skill_dir: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in IGNORED_NAMES}

    shutil.copytree(skill_dir, destination, ignore=ignore)


def write_reproducible_zip(stage_root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(p for p in stage_root.rglob("*") if p.is_file()):
            relative = path.relative_to(stage_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def verify_archive(output: Path, expected_skills: list[str]) -> None:
    with zipfile.ZipFile(output, "r") as archive:
        names = archive.namelist()
        roots = sorted({name.split("/", 1)[0] for name in names if "/" in name})
        if roots != sorted(expected_skills):
            raise BundleError(
                f"ZIP roots {roots!r} do not match Skills {sorted(expected_skills)!r}"
            )
        for skill in expected_skills:
            if f"{skill}/SKILL.md" not in names:
                raise BundleError(f"ZIP is missing {skill}/SKILL.md")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output = args.output
    if not output.is_absolute():
        output = (Path.cwd() / output).resolve()

    skill_dirs = discover_skill_dirs(repo_root)
    skill_names = [path.name for path in skill_dirs]

    with tempfile.TemporaryDirectory(prefix="chatgpt-skills-") as temp_dir:
        stage_root = Path(temp_dir)
        for skill_dir in skill_dirs:
            verify_source_skill(skill_dir)
            copy_skill(skill_dir, stage_root / skill_dir.name)
        write_reproducible_zip(stage_root, output)

    verify_archive(output, skill_names)
    print(f"Built {output}")
    for name in skill_names:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BundleError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

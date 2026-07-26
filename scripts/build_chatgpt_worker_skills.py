#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

MARKDOWN_LINK_RE = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\()"
    r"(?P<target>[^)\s]+)"
    r"(?P<suffix>(?:\s+[\"'][^\"']*[\"'])?\))"
)
MARKDOWN_SUFFIXES = {".md", ".markdown"}
IGNORED_NAMES = {"__pycache__", ".DS_Store"}


class BundleError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build one ChatGPT multi-Skill ZIP from every skills/chat-*/SKILL.md, "
            "package referenced shared dependencies inside each Skill, and reject "
            "ChatGPT-specific shared runtime files that would be omitted."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("chatgpt-worker-skills.zip"),
        help="Output ZIP path.",
    )
    return parser.parse_args()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES
    )


def read_skill_name(skill_file: Path) -> str:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
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
    skill_files = sorted(skills_root.glob("chat-*/SKILL.md"))
    if not skill_files:
        raise BundleError("No ChatGPT Skills matched skills/chat-*/SKILL.md")

    skill_dirs: list[Path] = []
    seen_names: set[str] = set()
    for skill_file in skill_files:
        skill_dir = skill_file.parent
        declared_name = read_skill_name(skill_file)
        if declared_name != skill_dir.name:
            raise BundleError(
                f"{skill_file}: declared name {declared_name!r} "
                f"does not match directory {skill_dir.name!r}"
            )
        if declared_name in seen_names:
            raise BundleError(f"Duplicate ChatGPT Skill name: {declared_name}")
        seen_names.add(declared_name)
        skill_dirs.append(skill_dir)
    return skill_dirs


def copy_skill_source(skill_dir: Path, staged_skill_dir: Path) -> None:
    for path in skill_dir.rglob("*"):
        if path.is_symlink():
            raise BundleError(f"{path}: symlinks are not allowed in ChatGPT Skills")

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in IGNORED_NAMES}

    shutil.copytree(skill_dir, staged_skill_dir, ignore=ignore)


def split_anchor(target: str) -> tuple[str, str]:
    if "#" not in target:
        return target, ""
    path_part, anchor = target.split("#", 1)
    return path_part, f"#{anchor}"


def package_shared_dependencies(
    repo_root: Path,
    skill_dir: Path,
    staged_skill_dir: Path,
) -> set[Path]:
    repo_root = repo_root.resolve()
    shared_root = (repo_root / "shared").resolve()
    skill_dir = skill_dir.resolve()

    source_to_stage: dict[Path, Path] = {}
    queue: list[tuple[Path, Path]] = []
    packaged_shared_paths: set[Path] = set()

    for source_path in iter_markdown_files(skill_dir):
        relative = source_path.relative_to(skill_dir)
        staged_path = staged_skill_dir / relative
        source_to_stage[source_path.resolve()] = staged_path
        queue.append((source_path.resolve(), staged_path))

    processed: set[Path] = set()

    while queue:
        source_path, staged_path = queue.pop(0)
        if source_path in processed:
            continue
        processed.add(source_path)

        content = source_path.read_text(encoding="utf-8")

        def rewrite(match: re.Match[str]) -> str:
            target = match.group("target")
            if (
                target.startswith(("http://", "https://", "mailto:", "#", "/"))
                or "://" in target
            ):
                return match.group(0)

            path_part, anchor = split_anchor(target)
            if not path_part:
                return match.group(0)

            unresolved = source_path.parent / path_part
            if unresolved.is_symlink():
                raise BundleError(
                    f"{source_path}: dependency is a symlink and cannot be packaged: "
                    f"{target}"
                )

            resolved = unresolved.resolve()
            if not resolved.exists():
                raise BundleError(
                    f"{source_path}: referenced path does not exist: {target}"
                )
            if resolved.is_dir():
                raise BundleError(
                    f"{source_path}: directory links are not package dependencies: "
                    f"{target}"
                )

            if is_relative_to(resolved, skill_dir):
                destination = staged_skill_dir / resolved.relative_to(skill_dir)
            elif is_relative_to(resolved, shared_root):
                packaged_shared_paths.add(resolved)
                destination = (
                    staged_skill_dir
                    / "references"
                    / "shared"
                    / resolved.relative_to(shared_root)
                )
                if resolved not in source_to_stage:
                    if destination.exists():
                        raise BundleError(
                            f"{source_path}: packaged dependency collides with "
                            f"existing Skill content: {destination}"
                        )
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(resolved, destination)
                    source_to_stage[resolved] = destination
                    if resolved.suffix.lower() in MARKDOWN_SUFFIXES:
                        queue.append((resolved, destination))
            elif is_relative_to(resolved, repo_root):
                raise BundleError(
                    f"{source_path}: ChatGPT Skill depends on repo-local file "
                    f"outside its Skill directory and shared/: {target}"
                )
            else:
                raise BundleError(
                    f"{source_path}: dependency escapes the repository: {target}"
                )

            relative_target = os.path.relpath(
                destination, start=staged_path.parent
            ).replace(os.sep, "/")
            return (
                match.group("prefix")
                + relative_target
                + anchor
                + match.group("suffix")
            )

        rewritten = MARKDOWN_LINK_RE.sub(rewrite, content)
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        staged_path.write_text(rewritten, encoding="utf-8")

    return packaged_shared_paths


def verify_chat_runtime_coverage(
    repo_root: Path,
    packaged_shared_paths: set[Path],
) -> None:
    chat_runtime_root = (repo_root / "shared" / "chat-worker").resolve()
    if not chat_runtime_root.is_dir():
        raise BundleError(
            "Missing ChatGPT runtime dependency directory: shared/chat-worker"
        )

    runtime_files = {
        path.resolve()
        for path in chat_runtime_root.rglob("*")
        if path.is_file() and path.name not in IGNORED_NAMES
    }
    omitted = sorted(runtime_files - packaged_shared_paths)
    if omitted:
        relative = [path.relative_to(repo_root).as_posix() for path in omitted]
        raise BundleError(
            "ChatGPT-specific shared runtime files are not referenced by any "
            f"packaged Skill: {relative}"
        )


def verify_staged_skill(staged_skill_dir: Path) -> None:
    skill_file = staged_skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise BundleError(f"{staged_skill_dir}: missing SKILL.md")

    for markdown_file in iter_markdown_files(staged_skill_dir):
        content = markdown_file.read_text(encoding="utf-8")
        if "../../shared/" in content:
            raise BundleError(
                f"{markdown_file}: unresolved repository shared link remains"
            )
        for match in MARKDOWN_LINK_RE.finditer(content):
            target = match.group("target")
            if (
                target.startswith(("http://", "https://", "mailto:", "#", "/"))
                or "://" in target
            ):
                continue
            path_part, _anchor = split_anchor(target)
            if not path_part:
                continue
            resolved = (markdown_file.parent / path_part).resolve()
            if not resolved.exists():
                raise BundleError(
                    f"{markdown_file}: packaged link is missing: {target}"
                )
            if not is_relative_to(resolved, staged_skill_dir.resolve()):
                raise BundleError(
                    f"{markdown_file}: packaged link escapes Skill directory: {target}"
                )


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
        files = sorted(path for path in stage_root.rglob("*") if path.is_file())
        for path in files:
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
                f"ZIP root directories {roots!r} do not match Skills "
                f"{sorted(expected_skills)!r}"
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
    skill_names = [skill_dir.name for skill_dir in skill_dirs]
    packaged_shared_paths: set[Path] = set()

    with tempfile.TemporaryDirectory(prefix="chatgpt-skills-") as temp_dir:
        stage_root = Path(temp_dir)
        for skill_dir in skill_dirs:
            staged_skill_dir = stage_root / skill_dir.name
            copy_skill_source(skill_dir, staged_skill_dir)
            packaged_shared_paths.update(
                package_shared_dependencies(repo_root, skill_dir, staged_skill_dir)
            )
            verify_staged_skill(staged_skill_dir)

        verify_chat_runtime_coverage(repo_root, packaged_shared_paths)
        write_reproducible_zip(stage_root, output)

    verify_archive(output, skill_names)

    print(f"Built {output}")
    for name in skill_names:
        print(f"- {name}")
    print(
        f"Packaged {len(packaged_shared_paths)} unique shared dependencies; "
        "all shared/chat-worker files are included."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BundleError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

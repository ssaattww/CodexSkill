#!/usr/bin/env python3
"""Codex PostToolUse hook helper for markdown-word-checker.

The helper reads Codex hook JSON from stdin, extracts Markdown files touched by
apply_patch/Edit/Write style tools, and runs focused Markdown lint with the
target repository's own lint configuration when that configuration exists.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SUPPORTED_TOOLS = {"apply_patch", "edit", "write"}
PATH_KEYS = {
    "file",
    "filename",
    "fileName",
    "file_path",
    "filePath",
    "filepath",
    "path",
    "target",
    "target_file",
    "targetFile",
    "target_path",
    "targetPath",
}
PATCH_FILE_RE = re.compile(r"^\*\*\* (Add|Update|Delete) File: (.+)$")
PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$")
OUTPUT_LIMIT = 4000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--codexskill-root",
        default=str(Path(__file__).resolve().parents[3]),
        help="CodexSkill repository root. Defaults to the helper location.",
    )
    args = parser.parse_args()

    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        return emit(
            state="unsupported",
            message="markdown-word-checker hook could not parse hook JSON.",
            details={"error": str(exc)},
            decision="block",
        )

    cwd = Path(event.get("cwd") or os.getcwd()).expanduser()
    if not cwd.exists():
        return emit(
            state="unsupported",
            message="markdown-word-checker hook received a missing cwd.",
            details={"cwd": str(cwd)},
            decision="block",
        )

    repo_root = find_repo_root(cwd)
    tool_name = normalize_tool_name(event.get("tool_name"))
    hook_event_name = event.get("hook_event_name")

    if hook_event_name and hook_event_name != "PostToolUse":
        return emit(
            state="skip",
            message="markdown-word-checker hook skipped a non-PostToolUse event.",
            details={"hook_event_name": hook_event_name},
        )

    if tool_name not in SUPPORTED_TOOLS:
        return emit(
            state="skip",
            message="markdown-word-checker hook skipped an unsupported tool.",
            details={"tool_name": event.get("tool_name")},
        )

    extraction = extract_paths(event, tool_name)
    if extraction["state"] == "unsupported":
        return emit(
            state="unsupported",
            message="markdown-word-checker hook could not extract touched files.",
            details=extraction,
            decision="block",
        )

    markdown_files = normalize_markdown_files(
        extraction["candidates"],
        extraction["deleted"],
        cwd,
        repo_root,
    )

    if not markdown_files:
        return emit(
            state="skip",
            message="markdown-word-checker hook found no existing repo-local Markdown files.",
            details={
                "tool_name": event.get("tool_name"),
                "repo_root": str(repo_root),
                "extraction": extraction["reason"],
            },
        )

    lint_result = run_focused_lint(Path(args.codexskill_root), repo_root, markdown_files)
    decision = "block" if lint_result["state"] in {"unsupported", "failed gate", "needs user review"} else None
    message = lint_result["message"]

    return emit(
        state=lint_result["state"],
        message=message,
        details={
            "repo_root": str(repo_root),
            "target_files": markdown_files,
            "classification": lint_result["state"],
            "reason": lint_result["reason"],
            "commands": lint_result["commands"],
            "risk": lint_result["risk"],
        },
        decision=decision,
    )


def normalize_tool_name(value: Any) -> str:
    tool_name = str(value or "").split(".")[-1]
    return tool_name.lower()


def find_repo_root(cwd: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return cwd.resolve()


def extract_paths(event: dict[str, Any], tool_name: str) -> dict[str, Any]:
    tool_input = event.get("tool_input", {})

    if tool_name == "apply_patch":
        patch_text = find_patch_text(tool_input)
        if not patch_text:
            return {
                "state": "unsupported",
                "reason": "apply_patch input did not contain a parseable patch payload.",
                "candidates": [],
                "deleted": [],
            }

        candidates, deleted = parse_apply_patch(patch_text)
        return {
            "state": "ok",
            "reason": "apply_patch payload parsed.",
            "candidates": sorted(candidates),
            "deleted": sorted(deleted),
        }

    candidates = sorted(collect_path_values(tool_input))
    if not candidates:
        return {
            "state": "unsupported",
            "reason": f"{tool_name} input did not expose a recognized file path field.",
            "candidates": [],
            "deleted": [],
        }

    return {
        "state": "ok",
        "reason": f"{tool_name} path fields parsed.",
        "candidates": candidates,
        "deleted": [],
    }


def find_patch_text(value: Any) -> str | None:
    for text in collect_strings(value):
        if "*** Begin Patch" in text and "*** End Patch" in text:
            return text
    return None


def collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(collect_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(collect_strings(item))
        return strings
    return []


def collect_path_values(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PATH_KEYS or key.lower() in PATH_KEYS:
                paths.update(flatten_path_values(item))
            else:
                paths.update(collect_path_values(item))
    elif isinstance(value, list):
        for item in value:
            paths.update(collect_path_values(item))
    return paths


def flatten_path_values(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        paths: set[str] = set()
        for item in value:
            paths.update(flatten_path_values(item))
        return paths
    return set()


def parse_apply_patch(patch_text: str) -> tuple[set[str], set[str]]:
    candidates: set[str] = set()
    deleted: set[str] = set()
    current_path: str | None = None
    current_kind: str | None = None

    for line in patch_text.splitlines():
        file_match = PATCH_FILE_RE.match(line)
        if file_match:
            current_kind, current_path = file_match.groups()
            if current_kind == "Delete":
                deleted.add(current_path)
            else:
                candidates.add(current_path)
            continue

        move_match = PATCH_MOVE_RE.match(line)
        if move_match and current_path:
            new_path = move_match.group(1)
            if current_kind == "Update":
                candidates.discard(current_path)
                deleted.add(current_path)
            candidates.add(new_path)
            current_path = new_path
            current_kind = "Update"

    return candidates, deleted


def normalize_markdown_files(candidates: list[str], deleted: list[str], cwd: Path, repo_root: Path) -> list[str]:
    deleted_paths = {resolve_candidate(path, cwd, repo_root) for path in deleted}
    files: set[str] = set()

    for candidate in candidates:
        resolved = resolve_candidate(candidate, cwd, repo_root)
        if resolved is None or resolved in deleted_paths:
            continue
        if resolved.suffix.lower() != ".md" or not resolved.exists() or not resolved.is_file():
            continue
        try:
            relative = resolved.relative_to(repo_root)
        except ValueError:
            continue
        files.add(relative.as_posix())

    return sorted(files)


def resolve_candidate(raw_path: str, cwd: Path, repo_root: Path) -> Path | None:
    cleaned = raw_path.strip().strip('"').strip("'")
    if not cleaned:
        return None

    candidate = Path(cleaned).expanduser()
    if not candidate.is_absolute():
        candidate = cwd / candidate
    resolved = candidate.resolve(strict=False)

    try:
        resolved.relative_to(repo_root)
    except ValueError:
        return None
    return resolved


def run_focused_lint(codexskill_root: Path, repo_root: Path, markdown_files: list[str]) -> dict[str, Any]:
    scripts_root = codexskill_root / "skills" / "review-enforcer" / "scripts"
    required_paths = {
        "package.json": repo_root / "package.json",
        "markdown-targets.json": repo_root / "tools" / "lint" / "markdown-targets.json",
        "markdown-whitelist.yaml": repo_root / "tools" / "lint" / "markdown-whitelist.yaml",
    }
    missing = [name for name, path in required_paths.items() if not path.exists()]
    if missing:
        return lint_result(
            state="unsupported",
            message="markdown-word-checker hook could not run focused lint because repo-local lint configuration is incomplete.",
            reason=f"Missing required focused-lint inputs: {', '.join(missing)}.",
            commands=[],
            risk="This is not a pass. The caller must record unsupported Markdown lint or run the repository gate another way.",
        )

    target_command = ["node", str(scripts_root / "list-markdown-targets.js"), "--files", *markdown_files]
    target_result = run_command(target_command, repo_root)
    commands = [target_result]
    if target_result["exit_status"] != 0:
        return lint_result(
            state="failed gate",
            message="markdown-word-checker hook failed while resolving focused Markdown targets.",
            reason="Target resolution command failed.",
            commands=commands,
            risk="The edit remains applied; hook feedback asks the model to continue from the failure.",
        )

    filtered_files = [line for line in target_result["stdout"].splitlines() if line.strip()]
    if not filtered_files:
        return lint_result(
            state="skip",
            message="markdown-word-checker hook found no files inside repo Markdown lint targets.",
            reason="All extracted Markdown files were excluded by markdown-targets.json.",
            commands=commands,
            risk="Skipped because the repo target configuration excluded the edited files.",
        )

    whitelist_command = ["node", str(scripts_root / "check-markdown-whitelist.js"), "--files", *filtered_files]
    whitelist_result = run_command(whitelist_command, repo_root)
    commands.append(whitelist_result)

    failed = [command for command in commands if command["exit_status"] != 0]
    if failed:
        return lint_result(
            state="failed gate",
            message="markdown-word-checker hook focused lint failed.",
            reason="One or more focused Markdown lint commands returned a non-zero exit status.",
            commands=commands,
            risk="The edit remains applied; fix the Markdown body or route exact repo-local lint setting changes to user review.",
        )

    cspell_config = repo_root / "cspell.config.jsonc"
    cspell_bin = repo_root / "node_modules" / ".bin" / ("cspell.cmd" if os.name == "nt" else "cspell")
    if cspell_config.exists() and not cspell_bin.exists():
        return lint_result(
            state="unsupported",
            message="markdown-word-checker hook could not run configured cspell lint.",
            reason=f"cspell.config.jsonc exists, but {cspell_bin.relative_to(repo_root).as_posix()} is missing.",
            commands=commands,
            risk="This is not a pass. Install repository lint dependencies or run the configured Markdown gate another way.",
        )

    if cspell_config.exists():
        cspell_command = ["node", str(scripts_root / "run-cspell-markdown.js"), *filtered_files]
        commands.append(run_command(cspell_command, repo_root))

    failed = [command for command in commands if command["exit_status"] != 0]
    if failed:
        return lint_result(
            state="failed gate",
            message="markdown-word-checker hook focused lint failed.",
            reason="One or more focused Markdown lint commands returned a non-zero exit status.",
            commands=commands,
            risk="The edit remains applied; fix the Markdown body or route exact repo-local lint setting changes to user review.",
        )

    return lint_result(
        state="pass",
        message="markdown-word-checker hook focused lint passed.",
        reason="Focused Markdown lint commands completed successfully.",
        commands=commands,
        risk="PostToolUse interception is not a complete enforcement boundary; review-enforcer still owns final gate disposition.",
    )


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        return {
            "command": " ".join(command),
            "exit_status": result.returncode,
            "stdout": trim(result.stdout),
            "stderr": trim(result.stderr),
        }
    except FileNotFoundError as exc:
        return {
            "command": " ".join(command),
            "exit_status": 127,
            "stdout": "",
            "stderr": str(exc),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "exit_status": 124,
            "stdout": trim(exc.stdout or ""),
            "stderr": trim(exc.stderr or "command timed out"),
        }


def lint_result(state: str, message: str, reason: str, commands: list[dict[str, Any]], risk: str) -> dict[str, Any]:
    return {
        "state": state,
        "message": message,
        "reason": reason,
        "commands": commands,
        "risk": risk,
    }


def emit(state: str, message: str, details: dict[str, Any], decision: str | None = None) -> int:
    payload: dict[str, Any] = {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": {
                "markdownWordChecker": {
                    "state": state,
                    **details,
                }
            },
        },
    }

    if decision:
        payload["decision"] = decision
        payload["reason"] = message

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def trim(value: str) -> str:
    if len(value) <= OUTPUT_LIMIT:
        return value
    return value[:OUTPUT_LIMIT] + "\n... [truncated]"


if __name__ == "__main__":
    raise SystemExit(main())

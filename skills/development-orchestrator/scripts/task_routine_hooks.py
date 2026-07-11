"""Codex hook handling and hook configuration for the task routine."""

from __future__ import annotations

import json
import os
import re
import shlex
import tempfile
from pathlib import Path
from typing import Any, Mapping

from task_routine_state import *

CONTENTS_API_COMMIT_TOOLS = {"create_file", "update_file", "delete_file"}
TRACKING_TOOLS = {
    "create_issue",
    "update_issue",
    "add_comment_to_issue",
    "add_review_to_pr",
}
PR_CREATE_TOOLS = {"create_pull_request", "open_pull_request"}
PR_BODY_REQUIRED_SECTIONS = {
    "task routine": "## Task routine evidence",
    "skill action": "## Skill action",
    "tool action": "## Tool action",
}
PR_BODY_PLACEHOLDERS = {"", "-", "n/a", "none", "tbd", "todo", "未記入", "未定"}


def tool_token(name: Any) -> str:
    token = str(name or "")
    for separator in (".", "/", ":"):
        token = token.split(separator)[-1]
    if "__" in token:
        token = token.rsplit("__", 1)[-1]
    return token.lower().replace("-", "_")


def strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    return []


def classify_shell_command(command: str) -> str:
    if GIT_SUBMIT.search(command):
        return "submission"
    if any(pattern.search(command) for pattern in (GIT_MUTATE, FILE_MUTATE, GH_MUTATE, REDIRECT)):
        return "edit"
    return "other"


def mutation(event: Mapping[str, Any]) -> str | None:
    token = tool_token(event.get("tool_name"))
    if token in CONTENTS_API_COMMIT_TOOLS or token in SUBMIT_TOOLS:
        return "submission"
    if token in TRACKING_TOOLS:
        return None
    if token in EDIT_TOOLS:
        return "edit"
    if token not in SHELL_TOOLS:
        return None
    command = "\n".join(strings(event.get("tool_input", {})))
    classified = classify_shell_command(command)
    return None if classified == "other" else classified


def pr_body_missing_sections(event: Mapping[str, Any]) -> list[str]:
    if tool_token(event.get("tool_name")) not in PR_CREATE_TOOLS:
        return []
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, Mapping):
        return list(PR_BODY_REQUIRED_SECTIONS)
    body = tool_input.get("body")
    if not isinstance(body, str):
        return list(PR_BODY_REQUIRED_SECTIONS)

    missing: list[str] = []
    for label, heading in PR_BODY_REQUIRED_SECTIONS.items():
        match = re.search(rf"(?mi)^\s*{re.escape(heading)}\s*$", body)
        if match is None:
            missing.append(label)
            continue
        remainder = body[match.end():]
        next_heading = re.search(r"(?m)^\s*##\s+", remainder)
        evidence = remainder[: next_heading.start() if next_heading else None].strip()
        if evidence.casefold() in PR_BODY_PLACEHOLDERS:
            missing.append(label)
    return missing


def context(root: Path, state: Mapping[str, Any] | None) -> str:
    if state is None:
        return "TASK ROUTINE: active taskなし。repositoryを変更する前に task_routine.py start を実行すること。"
    task, nxt = state["task"], next_step(state)
    if task["status"] == "paused":
        return f"TASK ROUTINE: task {task['id']} は paused。変更前にresumeが必要。"
    if task["status"] != "active":
        return f"TASK ROUTINE: task {task['id']} は {task['status']}。変更前に新しいtaskの開始が必要。"
    return f"TASK ROUTINE: {task['id']} / {task['summary']}。next required step: {nxt or 'none'}。skill/tool/feedback判定を省略しないこと。state={state_path(root)}"


def hook_output(event_name: str, additional: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": additional}}


def handle_hook(event_data: Mapping[str, Any]) -> dict[str, Any] | None:
    event_name = str(event_data.get("hook_event_name") or "")
    root = repo_root(Path(str(event_data.get("cwd") or os.getcwd())))
    if root is None:
        return None
    try:
        state = load(root)
        state_error = None
    except RoutineError as exc:
        state = None
        state_error = str(exc)
    if event_name in {"SessionStart", "UserPromptSubmit"}:
        if state_error:
            return hook_output(event_name, f"TASK ROUTINE state error: {state_error}. 変更を開始せずstateを修復すること。")
        return hook_output(event_name, context(root, state))
    if event_name == "PreToolUse":
        kind = mutation(event_data)
        if not kind:
            return None
        reason: str | None = None
        if state_error:
            reason = f"task routine stateが壊れています: {state_error}"
        elif state is None:
            reason = "active task routineがありません。task_routine.py start --id <id> --summary <summary> を先に実行してください。"
        elif state["task"]["status"] != "active":
            reason = f"task routineは {state['task']['status']} です。resumeまたは新task開始が必要です。"
        elif kind == "edit" and any(not complete(state, name) for name in EARLY):
            missing = [name for name in EARLY if not complete(state, name)]
            reason = f"編集前stepが未完了です: {', '.join(missing)}"
        elif kind == "submission" and any(not complete(state, name) for name in SUBMISSION_PREREQUISITES):
            missing = [name for name in SUBMISSION_PREREQUISITES if not complete(state, name)]
            reason = f"submission前stepが未完了です: {', '.join(missing)}"
        elif tool_token(event_data.get("tool_name")) in PR_CREATE_TOOLS:
            missing_sections = pr_body_missing_sections(event_data)
            if missing_sections:
                reason = (
                    "PR本文の必須証跡が不足しています: "
                    f"{', '.join(missing_sections)}。"
                    "## Task routine evidence / ## Skill action / ## Tool action "
                    "を記入してください。"
                )
        if reason:
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
        return None
    if event_name == "Stop" and bool(event_data.get("stop_hook_active")):
        if state_error:
            return {"systemMessage": f"task routine state error remains after continuation: {state_error}"}
        return None
    if event_name == "Stop" and state_error:
        return {"decision": "block", "reason": f"task routine stateが壊れています: {state_error}. stateを修復してください。"}
    if event_name == "Stop" and state and state["task"]["status"] == "active" and next_step(state):
        nxt = next_step(state)
        return {"decision": "block", "reason": f"task {state['task']['id']} は未完了です。次に {nxt}: {DESCRIPTIONS[nxt]} を実施し、証跡を記録してください。pause/abort時は専用commandを使ってください。"}
    return None


def hook_groups(command: str) -> dict[str, list[dict[str, Any]]]:
    handler = {"type": "command", "command": command, "timeout": 10, "statusMessage": "task routineを確認中"}
    return {name: [{"hooks": [handler]}] for name in ("SessionStart", "UserPromptSubmit", "PreToolUse", "Stop")}


def handler_commands(group: Any) -> list[str]:
    if not isinstance(group, dict):
        return []
    return [str(item.get("command", "")) for item in group.get("hooks", []) if isinstance(item, dict)]


def install(scope: str, root: Path | None, target: Path | None, script: Path | None, remove: bool = False) -> tuple[Path, bool]:
    if target:
        path = target.expanduser().resolve(strict=False)
    elif scope == "project":
        if root is None:
            raise RoutineError("project hook installにはGit repositoryが必要です")
        path = root / ".codex" / "hooks.json"
    else:
        path = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser() / "hooks.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"hooks": {}}
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutineError(f"hooks.jsonを読めません: {exc}") from exc
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise RoutineError("hooks.jsonのhooksがobjectではありません")
    changed = False
    for name in list(hooks):
        groups = hooks[name]
        if isinstance(groups, list) and remove:
            kept = [group for group in groups if not any("task_routine.py" in cmd for cmd in handler_commands(group))]
            changed |= len(kept) != len(groups)
            if kept:
                hooks[name] = kept
            else:
                hooks.pop(name, None)
    if not remove:
        script_command = f"python3 {shlex.quote(str((script or Path(__file__).with_name('task_routine.py')).expanduser().resolve()))} hook"
        for name, groups in hook_groups(script_command).items():
            current = hooks.setdefault(name, [])
            if not isinstance(current, list):
                raise RoutineError(f"hooks.{name}がarrayではありません")
            if not any(any("task_routine.py" in cmd for cmd in handler_commands(group)) for group in current):
                current.extend(groups)
                changed = True
    if changed or not path.exists():
        write_json(path, config)
    return path, changed


def install_hooks(scope: str, root: Path | None, target: Path | None, script: Path | None, dry_run: bool) -> tuple[Path, bool, dict[str, Any]]:
    if dry_run:
        # Merge through a temporary copy to preserve the real target.
        with tempfile.TemporaryDirectory() as tmp:
            preview = Path(tmp) / "hooks.json"
            if target and target.exists():
                preview.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
            path, changed = install(scope, root, preview, script)
            return target or path, changed, json.loads(preview.read_text(encoding="utf-8"))
    path, changed = install(scope, root, target, script)
    return path, changed, json.loads(path.read_text(encoding="utf-8"))


def require_root(value: str | None) -> Path:
    root = repo_root(Path(value or os.getcwd()))
    if root is None:
        raise RoutineError("Git repositoryを特定できません")
    return root


def require_state(root: Path) -> dict[str, Any]:
    state = load(root)
    if state is None:
        raise RoutineError("active task routine stateがありません")
    return state

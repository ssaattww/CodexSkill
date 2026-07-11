"""Persistent state and ordered operations for one development task."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

STEPS = (
    "intake",
    "skill_scan",
    "task_definition",
    "plan",
    "implementation",
    "verification",
    "review",
    "skill_reflection",
    "tool_reflection",
    "feedback_tracking",
    "progress_sync",
    "git_submission",
)
STEP_NAMES = STEPS

DESCRIPTIONS = {
    "intake": "依頼、issue要件、確認境界を確定する",
    "skill_scan": "関連skillと既存自動化手段を確認する",
    "task_definition": "今回の1 taskの範囲と完了条件を固定する",
    "plan": "実装、検証、レビュー、提出の順序を決める",
    "implementation": "設計・コード・資料の変更を実施する",
    "verification": "test、lint、build等の証拠を取得する",
    "review": "独立レビューと指摘の裁定を完了する",
    "skill_reflection": "skill改善要否を判定し、必要なら反映する",
    "tool_reflection": "反復出力のtool化要否を判定し、必要なら反映する",
    "feedback_tracking": "FP/issueの重複確認と追跡先を記録する",
    "progress_sync": "reportと進捗管理を実状態へ同期する",
    "git_submission": "commit、push、PR作成まで完了する",
}
STRUCTURED = {"skill_reflection", "tool_reflection", "feedback_tracking"}
EARLY = STEPS[:4]
SUBMISSION_PREREQUISITES = STEPS[:-1]
DONE = {"done", "not_applicable"}
SKILL_DECISIONS = {"none", "update-existing", "propose-new"}
TOOL_DECISIONS = {"none", "update-existing", "create-internal", "propose-external"}
FEEDBACK_DECISIONS = {"none", "merged", "issue", "commit-backed"}

EDIT_TOOLS = {
    "apply_patch", "edit", "write", "edit_file", "write_file", "create_file",
    "update_file", "delete_file", "replace_file", "move_file", "rename_file",
    "multi_edit", "multiedit", "notebook_edit", "create_blob", "create_tree",
    "create_branch", "delete_branch", "create_issue", "update_issue",
    "add_comment_to_issue", "add_review_to_pr",
}
SUBMIT_TOOLS = {
    "create_pull_request", "open_pull_request", "merge_pull_request",
    "mark_pull_request_ready", "create_commit", "push_branch", "update_ref",
    "update_pull_request", "enable_auto_merge",
}
SHELL_TOOLS = {"bash", "shell", "exec", "exec_command", "command", "terminal"}
GIT_SUBMIT = re.compile(r"(?:^|[;&|]\s*)(?:git\s+(?:add|commit|push|tag)|gh\s+pr\s+(?:create|ready|merge))\b", re.I)
GIT_MUTATE = re.compile(r"(?:^|[;&|]\s*)git\s+(?:checkout|switch|branch|merge|rebase|reset|restore|stash|cherry-pick|revert|clean|worktree)\b", re.I)
FILE_MUTATE = re.compile(
    r"(?:^|[;&|]\s*)(?:rm|mv|cp|mkdir|rmdir|touch|truncate|install|ln|chmod|chown|tee)\b"
    r"|\bsed\s+-[^\n;]*i\b|\b(?:npm|pnpm|yarn)\s+(?:install|add|remove|uninstall|version)\b"
    r"|\b(?:cargo\s+fmt|go\s+fmt|gofmt|ruff\s+format|black|prettier\s+--write)\b",
    re.I,
)
GH_MUTATE = re.compile(r"(?:^|[;&|]\s*)gh\s+(?:issue\s+(?:create|edit|close|reopen|comment)|release\s+create)\b", re.I)
REDIRECT = re.compile(r"(?<![<>])(?:>>|>)\s*(?!&?\d\b)(?!/dev/null\b)\S+", re.I)


class RoutineError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(cwd), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def repo_root(cwd: Path) -> Path | None:
    result = git(cwd.expanduser().resolve(), "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 and result.stdout.strip() else None


def git_path(root: Path, relative: str) -> Path:
    result = git(root, "rev-parse", "--git-path", relative)
    if result.returncode != 0 or not result.stdout.strip():
        raise RoutineError(f"Git state pathを解決できません: {result.stderr.strip()}")
    path = Path(result.stdout.strip())
    return (path if path.is_absolute() else root / path).resolve(strict=False)


def state_path(root: Path) -> Path:
    return git_path(root, "codex-task-routine/state.json")


def routine_state_path(root: Path) -> Path:
    return state_path(root)


def routine_history_dir(root: Path) -> Path:
    return git_path(root, "codex-task-routine/history")


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    os.chmod(temp, 0o600)
    temp.replace(path)


def validate(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict) or state.get("version") != 1:
        raise RoutineError("task routine stateの形式またはversionが不正です")
    task, steps = state.get("task"), state.get("steps")
    if not isinstance(task, dict) or not isinstance(steps, dict):
        raise RoutineError("task routine stateのtask/stepsが不正です")
    for name in STEPS:
        if not isinstance(steps.get(name), dict) or steps[name].get("status") not in {"pending", *DONE}:
            raise RoutineError(f"step {name}の状態が不正です")
    return state


def load(root: Path) -> dict[str, Any] | None:
    path = state_path(root)
    if not path.exists():
        return None
    try:
        return validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutineError(f"task routine stateを読めません: {exc}") from exc


def save(root: Path, state: dict[str, Any]) -> None:
    state["task"]["updated_at"] = now()
    write_json(state_path(root), validate(state))


def event(state: dict[str, Any], event_type: str, **detail: Any) -> None:
    state.setdefault("events", []).append({"at": now(), "type": event_type, "detail": detail})
    state["events"] = state["events"][-200:]


def fresh(task_id: str, summary: str) -> dict[str, Any]:
    timestamp = now()
    return {
        "version": 1,
        "task": {"id": task_id, "summary": summary, "status": "active", "started_at": timestamp, "updated_at": timestamp},
        "steps": {name: {"status": "pending", "evidence": None, "metadata": {}, "updated_at": None} for name in STEPS},
        "events": [{"at": timestamp, "type": "task-started", "detail": {"id": task_id, "summary": summary}}],
    }


def complete(state: Mapping[str, Any], name: str) -> bool:
    return state["steps"][name]["status"] in DONE


def step_is_complete(state: Mapping[str, Any], name: str) -> bool:
    return complete(state, name)


def next_step(state: Mapping[str, Any]) -> str | None:
    return next((name for name in STEPS if not complete(state, name)), None)


def prior_incomplete(state: Mapping[str, Any], name: str) -> list[str]:
    return [item for item in STEPS[: STEPS.index(name)] if not complete(state, item)]


def require_active(state: Mapping[str, Any]) -> None:
    if state["task"]["status"] != "active":
        raise RoutineError(f"task statusがactiveではありません: {state['task']['status']}")


def archive(root: Path, state: Mapping[str, Any]) -> None:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", str(state["task"]["id"])).strip("-.") or "task"
    stamp = now().replace(":", "").replace("-", "")
    write_json(git_path(root, f"codex-task-routine/history/{stamp}-{safe}.json"), state)


def start(root: Path, task_id: str, summary: str) -> dict[str, Any]:
    old = load(root)
    if old and old["task"]["status"] not in {"completed", "aborted"}:
        raise RoutineError(f"未完了taskが既にあります: {old['task']['id']}")
    if old:
        archive(root, old)
    state = fresh(task_id, summary)
    save(root, state)
    return state


def mark(root: Path, state: dict[str, Any], name: str, status: str, evidence: str, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
    require_active(state)
    if name in STRUCTURED:
        raise RoutineError(f"{name}は専用commandで記録してください")
    missing = prior_incomplete(state, name)
    if missing:
        raise RoutineError(f"先に完了すべきstepがあります: {', '.join(missing)}")
    state["steps"][name] = {"status": status, "evidence": evidence, "metadata": dict(metadata or {}), "updated_at": now()}
    event(state, "step-updated", step=name, status=status, evidence=evidence)
    if next_step(state) is None:
        state["task"]["status"] = "completed"
        state["task"]["completed_at"] = now()
        event(state, "task-completed")
    save(root, state)
    return state


def reopen_step(root: Path, state: dict[str, Any], name: str, reason: str) -> dict[str, Any]:
    if name not in STEPS:
        raise RoutineError(f"unknown step: {name}")
    require_active(state)
    for item in STEPS[STEPS.index(name):]:
        state["steps"][item] = {"status": "pending", "evidence": None, "metadata": {}, "updated_at": None}
    state["task"].pop("completed_at", None)
    event(state, "step-reopened", step=name, reason=reason)
    save(root, state)
    return state


def start_task(root: Path, task_id: str, summary: str) -> dict[str, Any]:
    return start(root, task_id, summary)


def load_state(root: Path) -> dict[str, Any] | None:
    return load(root)


def complete_step(root: Path, state: dict[str, Any], name: str, evidence: str) -> dict[str, Any]:
    return mark(root, state, name, "done", evidence)


def reflect(root: Path, state: dict[str, Any], kind: str, decision: str, target: str | None, evidence: str) -> dict[str, Any]:
    return reflection(root, state, kind, decision, target, evidence)


def record_feedback(root: Path, state: dict[str, Any], decision: str, target: str | None, evidence: str) -> dict[str, Any]:
    return feedback(root, state, decision, target, evidence)


def pause_task(root: Path, state: dict[str, Any], reason: str) -> dict[str, Any]:
    return pause(root, state, reason)


def reflection(root: Path, state: dict[str, Any], kind: str, decision: str, target: str | None, evidence: str) -> dict[str, Any]:
    name = f"{kind}_reflection"
    allowed = SKILL_DECISIONS if kind == "skill" else TOOL_DECISIONS
    if decision not in allowed:
        raise RoutineError(f"{kind} decisionが不正です: {decision}")
    if decision != "none" and not target:
        raise RoutineError("変更・提案decisionにはtargetが必要です")
    missing = prior_incomplete(state, name)
    if missing:
        raise RoutineError(f"先に完了すべきstepがあります: {', '.join(missing)}")
    require_active(state)
    state["steps"][name] = {"status": "done", "evidence": evidence, "metadata": {"decision": decision, "target": target}, "updated_at": now()}
    event(state, "reflection-recorded", kind=kind, decision=decision, target=target, evidence=evidence)
    save(root, state)
    return state


def feedback(root: Path, state: dict[str, Any], decision: str, target: str | None, evidence: str) -> dict[str, Any]:
    if decision not in FEEDBACK_DECISIONS:
        raise RoutineError(f"feedback decisionが不正です: {decision}")
    if decision != "none" and not target:
        raise RoutineError("追跡decisionにはtargetが必要です")
    name = "feedback_tracking"
    missing = prior_incomplete(state, name)
    if missing:
        raise RoutineError(f"先に完了すべきstepがあります: {', '.join(missing)}")
    require_active(state)
    state["steps"][name] = {"status": "done", "evidence": evidence, "metadata": {"decision": decision, "target": target}, "updated_at": now()}
    event(state, "feedback-recorded", decision=decision, target=target, evidence=evidence)
    save(root, state)
    return state


def pause(root: Path, state: dict[str, Any], reason: str, abort: bool = False) -> dict[str, Any]:
    if state["task"]["status"] in {"completed", "aborted"}:
        raise RoutineError("完了済みtaskはpause/abortできません")
    state["task"]["status"] = "aborted" if abort else "paused"
    state["task"]["reason"] = reason
    event(state, "task-aborted" if abort else "task-paused", reason=reason)
    save(root, state)
    return state


def resume(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    if state["task"]["status"] != "paused":
        raise RoutineError("paused taskだけresumeできます")
    state["task"]["status"] = "active"
    state["task"].pop("reason", None)
    event(state, "task-resumed")
    save(root, state)
    return state


def render(state: Mapping[str, Any] | None, root: Path) -> str:
    if state is None:
        return f"task routine: none\nrepo: {root}\nnext: task_routine.py start --id <id> --summary <summary>"
    task, nxt = state["task"], next_step(state)
    lines = [f"task: {task['id']} - {task['summary']}", f"status: {task['status']}", f"repo: {root}"]
    for name in STEPS:
        marker = "x" if complete(state, name) else " "
        lines.append(f"[{marker}] {name}: {DESCRIPTIONS[name]}")
    lines.append(f"next: {nxt or 'none'}")
    return "\n".join(lines)



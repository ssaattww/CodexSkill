#!/usr/bin/env python3
"""Stop hook guard for flow-enforcement."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from flow_enforcement_common import FlowError, compose_runtime_flow, find_current_and_next, has_unresolved_workflow_mutations, load_current_workflow, load_flow_state, load_progress, read_json_stdin, resolve_roots_from_env_or_config, write_json_stdout


def _has_unprocessed_input(state):
    return any(item.get("status") in {"unclassified", "classified", "needs_confirmation"} for item in state.get("input_journal") or [])


def _derived_state_conflict(state: dict[str, Any], current: dict[str, Any] | None, next_node: dict[str, Any] | None) -> str | None:
    if state.get("mode") == "cancelled":
        return None
    current_task = state.get("current_task") or {}
    cursor = state.get("workflow_cursor") or {}
    expected_current = current["node_path"] if current else None
    expected_next = next_node["node_path"] if next_node else None
    actual_current = current_task.get("current_node_path")
    actual_next = current_task.get("next_node_path")
    cursor_current = cursor.get("current_node_path")
    cursor_next = cursor.get("next_node_path")

    if expected_current is None:
        if current_task.get("status") not in {None, "completed"}:
            return "derived flow_state current_task.status conflicts with completed progress"
        if actual_current is not None or actual_next is not None or cursor_current is not None or cursor_next is not None:
            return "derived flow_state cursor conflicts with completed progress"
        return None

    if current_task.get("status") == "completed":
        return "derived flow_state current_task.status conflicts with incomplete progress"
    if actual_current != expected_current:
        return "derived flow_state current_task.current_node_path conflicts with progress"
    if actual_next != expected_next:
        return "derived flow_state current_task.next_node_path conflicts with progress"
    if cursor_current != expected_current:
        return "derived flow_state workflow_cursor.current_node_path conflicts with progress"
    if cursor_next != expected_next:
        return "derived flow_state workflow_cursor.next_node_path conflicts with progress"
    return None


def main() -> int:
    try:
        payload = read_json_stdin()
        roots = resolve_roots_from_env_or_config(payload.get("cwd"))
        state = load_flow_state(roots)
        progress = load_progress(roots)
        workflow = load_current_workflow(roots, state)
        flow = compose_runtime_flow(workflow, roots)
        if state.get("mode") == "pending_user_intent":
            write_json_stdout({"decision": "block", "reason": "ユーザー入力の意図を確認してください。"})
            return 0
        if state.get("mode") == "pending_workflow_mutation" or has_unresolved_workflow_mutations(state):
            write_json_stdout({"decision": "block", "reason": "workflow mutation の確認または適用が未完了です。"})
            return 0
        if _has_unprocessed_input(state):
            write_json_stdout({"decision": "block", "reason": "未処理のユーザー入力分類があります。"})
            return 0
        if state.get("mode") == "interrupted":
            write_json_stdout({"decision": "block", "reason": "割り込み作業中です。完了後に戻り先へ復帰してください。"})
            return 0
        current, next_node = find_current_and_next(state, progress, flow)
        stale_reason = _derived_state_conflict(state, current, next_node)
        if stale_reason:
            write_json_stdout({"decision": "block", "reason": stale_reason})
            return 0
        if current and state.get("mode") != "cancelled":
            write_json_stdout({"decision": "block", "reason": f"未完了 node があります。次に {current['node_path']} を実行してください。"})
            return 0
        write_json_stdout({"decision": "approve", "reason": "flow completed or cancelled."})
        return 0
    except FlowError as exc:
        write_json_stdout({"decision": "block", "reason": f"Flow State validation failed: {exc.code}: {exc.message}"})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

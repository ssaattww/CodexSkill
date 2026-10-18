#!/usr/bin/env python3
"""PostToolUse hook helper for flow-enforcement."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from flow_enforcement_common import FlowError, compose_runtime_flow, load_current_workflow, load_flow_state, load_progress, make_response, read_json_stdin, resolve_roots_from_env_or_config, write_json_stdout
from sync_flow_state import sync_derived_state_operation
from update_progress import mark_completed_nodes


def _tool_name(payload):
    return payload.get("tool_name") or payload.get("tool") or ""


def _tool_input(payload):
    return payload.get("tool_input") or payload.get("input") or {}


def _matches_evidence(payload, step):
    evidence_items = step.get("evidence") or []
    tool_name = _tool_name(payload)
    tool_input = _tool_input(payload)
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    for evidence in evidence_items:
        if evidence.get("tool") and evidence.get("tool") != tool_name:
            continue
        if evidence.get("command_contains") and evidence["command_contains"] not in command:
            continue
        if evidence.get("tool") or evidence.get("command_contains"):
            return True
    return False


def _detect_completed_nodes(payload, roots, state):
    workflow = load_current_workflow(roots, state)
    flow = compose_runtime_flow(workflow, roots)
    current_path = (state.get("current_task") or {}).get("current_node_path")
    if not current_path or current_path not in flow["index"]:
        return []
    node = flow["index"][current_path]
    if node.get("node_kind") == "step" and _matches_evidence(payload, node.get("step") or {}):
        return [{"node_path": current_path, "evidence": {"tool_name": _tool_name(payload), "tool_input": _tool_input(payload)}}]
    return []


def main() -> int:
    try:
        payload = read_json_stdin()
        roots = resolve_roots_from_env_or_config(payload.get("cwd"))
        state = load_flow_state(roots)
        load_progress(roots)
        completed_nodes = _detect_completed_nodes(payload, roots, state)
        progress_request = {
            "operation": "mark_completed_nodes",
            "request_id": payload.get("request_id"),
            "actor": "PostToolUse",
            "state_root": str(roots.state_root),
            "workflow_root": str(roots.workflow_root),
            "step_root": str(roots.step_root),
            "completed_nodes": completed_nodes,
        }
        progress_response, progress_exit = mark_completed_nodes(progress_request)
        if progress_exit not in (0,):
            write_json_stdout(progress_response)
            return progress_exit
        sync_response, sync_exit = sync_derived_state_operation(
            {
                "operation": "sync_derived_state",
                "request_id": f"{payload.get('request_id')}-sync",
                "actor": "PostToolUse",
                "state_root": str(roots.state_root),
                "workflow_root": str(roots.workflow_root),
                "step_root": str(roots.step_root),
            }
        )
        summary = sync_response.get("state_summary", {})
        message = (
            "[Flow State]\n"
            f"今回実行した作業: {_tool_name(payload)}\n"
            f"現在の node: {summary.get('current_node_path')}\n"
            f"次の node: {summary.get('next_node_path')}"
        )
        write_json_stdout(
            {
                "decision": "approve",
                "systemMessage": message,
                "hookSpecificOutput": {"additionalContext": {"progress": progress_response, "sync": sync_response}},
            }
        )
        return sync_exit
    except FlowError as exc:
        write_json_stdout(
            make_response(ok=False, operation="PostToolUse", request_id=None, errors=[{"code": exc.code, "message": exc.message}])
        )
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

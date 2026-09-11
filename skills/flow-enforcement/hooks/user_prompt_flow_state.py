#!/usr/bin/env python3
"""UserPromptSubmit hook helper for flow-enforcement."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from flow_enforcement_common import FlowError, load_flow_state, make_response, read_json_stdin, resolve_roots_from_env_or_config, write_json_stdout
from update_input_journal import record_user_prompt


def _extract_prompt(payload):
    for key in ("prompt", "user_prompt", "input", "text"):
        if isinstance(payload.get(key), str):
            return payload[key]
    return ""


def main() -> int:
    try:
        payload = read_json_stdin()
        roots = resolve_roots_from_env_or_config(payload.get("cwd"))
        state = load_flow_state(roots)
        current_task = state.get("current_task") or {}
        if current_task.get("status") != "active":
            write_json_stdout({"decision": "approve", "systemMessage": "Flow enforcement: no active flow."})
            return 0
        request = {
            "operation": "record_user_prompt",
            "request_id": payload.get("request_id"),
            "actor": "UserPromptSubmit",
            "state_root": str(roots.state_root),
            "workflow_root": str(roots.workflow_root),
            "step_root": str(roots.step_root),
            "record_user_prompt": {"text": _extract_prompt(payload), "source": "UserPromptSubmit"},
        }
        result, _ = record_user_prompt(request)
        input_id = result["state_summary"]["input_id"]
        message = (
            "[Flow State]\n"
            f"input_id: {input_id}\n"
            f"current_task: {current_task.get('task_node_path')}\n"
            "ユーザー入力を分類し、update_input_journal.py classify_input に input_id 付きで渡してください。"
        )
        write_json_stdout(
            {
                "decision": "approve",
                "systemMessage": message,
                "hookSpecificOutput": {"additionalContext": {"input_id": input_id, "mode": state.get("mode")}},
            }
        )
        return 0
    except FlowError as exc:
        write_json_stdout(
            make_response(
                ok=False,
                operation="UserPromptSubmit",
                request_id=None,
                errors=[{"code": exc.code, "message": exc.message}],
            )
        )
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

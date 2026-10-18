#!/usr/bin/env python3
"""Update progress.json completed_nodes through the flow-enforcement contract."""

from __future__ import annotations

from typing import Any

from flow_enforcement_common import (
    EXIT_CODES,
    FlowError,
    compose_runtime_flow,
    evidence_requires_agent_action,
    load_current_workflow,
    load_flow_state,
    load_progress,
    main_wrapper,
    make_response,
    resolve_roots,
    save_progress,
    state_lock,
    utc_now,
    validate_state_root_contract,
)


def mark_completed_nodes(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    roots = resolve_roots(request)
    completed_nodes = request.get("completed_nodes")
    if not isinstance(completed_nodes, list):
        raise FlowError("invalid_request_schema", "completed_nodes must be a list")
    with state_lock(roots.state_root):
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        progress = load_progress(roots)
        workflow = load_current_workflow(roots, state)
        flow = compose_runtime_flow(workflow, roots)
        existing = {
            node.get("node_path")
            for node in progress.get("completed_nodes", [])
            if isinstance(node, dict) and isinstance(node.get("node_path"), str)
        }
        blocked: list[str] = []
        required_codes: list[str] = []
        added: list[str] = []
        for candidate in completed_nodes:
            if not isinstance(candidate, dict) or not isinstance(candidate.get("node_path"), str):
                raise FlowError("invalid_request_schema", "completed node must include node_path")
            node_path = candidate["node_path"]
            if node_path not in flow["index"]:
                raise FlowError("validation_failed", "completed node does not exist", {"node_path": node_path})
            evidence = candidate.get("evidence") or {}
            needs_action, codes = evidence_requires_agent_action(evidence)
            if needs_action:
                blocked.append(node_path)
                required_codes.extend(codes)
                continue
            if node_path in existing:
                continue
            runtime_node = flow["index"][node_path]
            progress.setdefault("completed_nodes", []).append(
                {
                    "node_path": node_path,
                    "node_kind": runtime_node.get("node_kind", "node"),
                    "completed_at": utc_now(),
                    "source": request.get("actor"),
                    "evidence": evidence,
                }
            )
            existing.add(node_path)
            added.append(node_path)

        if blocked:
            return (
                make_response(
                    ok=False,
                    operation="mark_completed_nodes",
                    request_id=request.get("request_id"),
                    errors=[
                        {
                            "code": code,
                            "node_path": node_path,
                            "reason": "review evidence requires workflow or design follow-up",
                        }
                        for node_path in blocked
                        for code in sorted(set(required_codes))
                    ],
                    state_summary={"mode": state.get("mode")},
                    required_agent_action=(
                        "propose_workflow_mutation を update_workflow.py に渡し、"
                        "ユーザー確認待ち state を作ってください"
                    ),
                    blocked_nodes=blocked,
                ),
                EXIT_CODES["evidence_rejected"],
            )

        if added:
            save_progress(roots, progress)
    return (
        make_response(
            ok=True,
            operation="mark_completed_nodes",
            request_id=request.get("request_id"),
            updated_files=["progress.json"] if added else [],
            state_summary={"completed_nodes_added": added},
        ),
        EXIT_CODES["success"],
    )


def handle(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    if request.get("operation") != "mark_completed_nodes":
        raise FlowError("unsupported_operation", "unsupported operation", {"operation": request.get("operation")})
    return mark_completed_nodes(request)


if __name__ == "__main__":
    main_wrapper(handle)

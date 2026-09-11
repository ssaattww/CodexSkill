#!/usr/bin/env python3
"""Validate flow-enforcement state, progress, workflow, and step references."""

from __future__ import annotations

from typing import Any

from flow_enforcement_common import (
    EXIT_CODES,
    FlowError,
    compose_runtime_flow,
    completed_node_paths,
    find_current_and_next,
    has_unresolved_workflow_mutations,
    load_current_workflow,
    load_flow_state,
    load_progress,
    main_wrapper,
    make_response,
    resolve_roots,
    validate_state_root_contract,
)


def collect_validation_errors(request: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    try:
        roots = resolve_roots(request)
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        progress = load_progress(roots)
        workflow = load_current_workflow(roots, state)
        flow = compose_runtime_flow(workflow, roots)
        for node_path in completed_node_paths(progress):
            if node_path not in flow["index"]:
                errors.append({"code": "completed_node_missing", "node_path": node_path})
        current, next_node = find_current_and_next(state, progress, flow)
        current_task = state.get("current_task") or {}
        cursor = state.get("workflow_cursor") or {}
        expected_current = current["node_path"] if current else None
        expected_next = next_node["node_path"] if next_node else None
        for field_owner, actual_current, actual_next in [
            ("current_task", current_task.get("current_node_path"), current_task.get("next_node_path")),
            ("workflow_cursor", cursor.get("current_node_path"), cursor.get("next_node_path")),
        ]:
            if actual_current is not None and actual_current != expected_current:
                errors.append(
                    {
                        "code": "derived_cache_mismatch",
                        "field_owner": field_owner,
                        "field": "current_node_path",
                        "actual": actual_current,
                        "expected": expected_current,
                    }
                )
            if actual_next is not None and actual_next != expected_next:
                errors.append(
                    {
                        "code": "derived_cache_mismatch",
                        "field_owner": field_owner,
                        "field": "next_node_path",
                        "actual": actual_next,
                        "expected": expected_next,
                    }
                )
        if has_unresolved_workflow_mutations(state) and state.get("mode") != "pending_workflow_mutation":
            errors.append({"code": "unresolved_workflow_mutation_mode_mismatch"})
        if state.get("mode") == "pending_workflow_mutation" and not has_unresolved_workflow_mutations(state):
            errors.append({"code": "pending_mode_without_unresolved_workflow_mutation"})
    except FlowError as exc:
        errors.append({"code": exc.code, "message": exc.message, **exc.details})
    return errors


def validate(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    errors = collect_validation_errors(request)
    ok = not errors
    return (
        make_response(
            ok=ok,
            operation="validate",
            request_id=request.get("request_id"),
            errors=errors,
            state_summary={"error_count": len(errors)},
        ),
        EXIT_CODES["success"] if ok else EXIT_CODES["validation_failed"],
    )


def handle(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    if request.get("operation") != "validate":
        raise FlowError("unsupported_operation", "unsupported operation", {"operation": request.get("operation")})
    return validate(request)


if __name__ == "__main__":
    main_wrapper(handle)

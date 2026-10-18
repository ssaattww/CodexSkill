#!/usr/bin/env python3
"""Synchronize flow_state.json derived cursor fields."""

from __future__ import annotations

from typing import Any

from flow_enforcement_common import (
    EXIT_CODES,
    FlowError,
    load_current_workflow,
    load_flow_state,
    load_progress,
    main_wrapper,
    make_response,
    resolve_roots,
    save_flow_state,
    state_lock,
    sync_derived_state,
    validate_state_root_contract,
)


def sync_derived_state_operation(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    roots = resolve_roots(request)
    with state_lock(roots.state_root):
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        progress = load_progress(roots)
        workflow = load_current_workflow(roots, state)
        new_state, summary = sync_derived_state(state, progress, workflow, roots, request.get("confirmed_overrides"))
        save_flow_state(roots, new_state)
    return (
        make_response(
            ok=True,
            operation="sync_derived_state",
            request_id=request.get("request_id"),
            updated_files=["flow_state.json"],
            state_summary=summary,
        ),
        EXIT_CODES["success"],
    )


def handle(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    if request.get("operation") != "sync_derived_state":
        raise FlowError("unsupported_operation", "unsupported operation", {"operation": request.get("operation")})
    return sync_derived_state_operation(request)


if __name__ == "__main__":
    main_wrapper(handle)

#!/usr/bin/env python3
"""Persist and apply repository workflow mutations."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from flow_enforcement_common import (
    EXIT_CODES,
    FlowError,
    atomic_write_json,
    compose_runtime_flow,
    has_unresolved_workflow_mutations,
    load_current_workflow,
    load_flow_state,
    load_progress,
    main_wrapper,
    make_response,
    normalize_workflow,
    resolve_roots,
    save_flow_state,
    state_lock,
    sync_derived_state,
    utc_now,
    validate_state_root_contract,
)


SUPPORTED_APPLY_OPS = {"add_node", "add_dependency"}


def _mutation_entry(mutation: dict[str, Any]) -> dict[str, Any]:
    entry = copy.deepcopy(mutation)
    entry.setdefault("mutation_id", f"mutation-{utc_now()}")
    entry["status"] = "proposed"
    entry["confirmation"] = "missing"
    entry.setdefault("classified_by", "codex_body")
    entry.setdefault("applied_at", None)
    entry.setdefault("applied_operations", [])
    return entry


def propose_workflow_mutation(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    roots = resolve_roots(request)
    mutation = request.get("mutation")
    if not isinstance(mutation, dict) or not isinstance(mutation.get("operations"), list):
        raise FlowError("invalid_request_schema", "mutation.operations must be specified")
    with state_lock(roots.state_root):
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        entry = _mutation_entry(mutation)
        state.setdefault("workflow_mutations", []).append(entry)
        state["mode"] = "pending_workflow_mutation"
        save_flow_state(roots, state)
    return (
        make_response(
            ok=False,
            operation="propose_workflow_mutation",
            request_id=request.get("request_id"),
            updated_files=["flow_state.json"],
            errors=[{"code": "user_confirmation_required", "mutation_id": entry.get("mutation_id")}],
            state_summary={"mode": state.get("mode"), "mutation_id": entry.get("mutation_id")},
            required_agent_action="workflow mutation の内容をユーザーに確認してください",
        ),
        EXIT_CODES["user_confirmation_required"],
    )


def _find_workflow_node(workflow: dict[str, Any], node_path: str) -> dict[str, Any]:
    def visit(node: dict[str, Any]) -> dict[str, Any] | None:
        if node.get("node_path") == node_path:
            return node
        for child in node.get("children") or []:
            found = visit(child)
            if found is not None:
                return found
        return None

    for root_node in workflow.get("nodes") or []:
        found = visit(root_node)
        if found is not None:
            return found
    raise FlowError("validation_failed", "workflow node does not exist", {"node_path": node_path})


def _add_node(workflow: dict[str, Any], operation: dict[str, Any]) -> None:
    node = operation.get("node")
    if not isinstance(node, dict) or not isinstance(node.get("id"), str):
        raise FlowError("invalid_request_schema", "add_node.node.id is required")
    parent_path = operation.get("parent_node_path")
    if parent_path in (None, ""):
        siblings = workflow.setdefault("nodes", [])
        new_path = node["id"]
    else:
        parent = _find_workflow_node(workflow, str(parent_path))
        siblings = parent.setdefault("children", [])
        new_path = f"{parent['node_path']}/{node['id']}"
    if any(child.get("id") == node["id"] for child in siblings):
        raise FlowError("validation_failed", "workflow node already exists", {"node_path": new_path})
    siblings.append(copy.deepcopy(node))


def _add_dependency(workflow: dict[str, Any], operation: dict[str, Any]) -> None:
    target = operation.get("target_node_path")
    depends_on = operation.get("depends_on")
    if not isinstance(target, str) or not isinstance(depends_on, list):
        raise FlowError("invalid_request_schema", "add_dependency requires target_node_path and depends_on list")
    if "#" in target:
        runtime_dependencies = workflow.setdefault("runtime_dependencies", {})
        current = runtime_dependencies.setdefault(target, [])
        for dependency in depends_on:
            if dependency not in current:
                current.append(dependency)
        return
    node = _find_workflow_node(workflow, target)
    current = node.setdefault("depends_on", [])
    for dependency in depends_on:
        if dependency not in current:
            current.append(dependency)


def _apply_operations(workflow: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    mutable = copy.deepcopy(workflow)
    mutable.pop("_node_index", None)
    for operation in operations:
        op = operation.get("op")
        if op not in SUPPORTED_APPLY_OPS:
            raise FlowError("unsupported_operation", "unsupported workflow mutation operation", {"operation": op})
        normalized = normalize_workflow(mutable)
        mutable = normalized
        if op == "add_node":
            _add_node(mutable, operation)
        elif op == "add_dependency":
            normalized = normalize_workflow(mutable)
            mutable = normalized
            _add_dependency(mutable, operation)
    mutable.pop("_node_index", None)
    return normalize_workflow(mutable)


def apply_workflow_mutation(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    roots = resolve_roots(request)
    mutation_id = request.get("mutation_id")
    confirmation = request.get("confirmation")
    if not isinstance(mutation_id, str):
        raise FlowError("invalid_request_schema", "mutation_id is required")
    if confirmation != "explicit_user_confirmed":
        raise FlowError("user_confirmation_required", "explicit_user_confirmed confirmation is required")

    with state_lock(roots.state_root):
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        mutation = next((item for item in state.get("workflow_mutations", []) if item.get("mutation_id") == mutation_id), None)
        if mutation is None:
            raise FlowError("validation_failed", "mutation_id does not exist", {"mutation_id": mutation_id})
        if mutation.get("status") != "proposed":
            raise FlowError(
                "validation_failed",
                "mutation status must be proposed before apply",
                {"mutation_id": mutation_id, "status": mutation.get("status")},
            )
        operations = mutation.get("operations")
        if not isinstance(operations, list):
            raise FlowError("invalid_request_schema", "stored mutation.operations must be a list")
        if "operations" in request and request.get("operations") != operations:
            raise FlowError(
                "validation_failed",
                "request operations must match stored mutation.operations",
                {"mutation_id": mutation_id},
            )
        workflow = load_current_workflow(roots, state)
        updated_workflow = _apply_operations(workflow, operations)
        progress = load_progress(roots)
        compose_runtime_flow(updated_workflow, roots)
        workflow_path = Path(updated_workflow["_workflow_path"])
        writable_workflow = copy.deepcopy(updated_workflow)
        writable_workflow.pop("_workflow_path", None)
        writable_workflow.pop("_node_index", None)
        atomic_write_json(workflow_path, writable_workflow)

        mutation["status"] = "active"
        mutation["confirmation"] = confirmation
        mutation["confirmed_by_input_id"] = request.get("confirmed_by_input_id")
        mutation["applied_at"] = utc_now()
        mutation["applied_operations"] = [operation.get("op") for operation in operations]
        state["mode"] = "pending_workflow_mutation" if has_unresolved_workflow_mutations(state) else "normal"
        state, summary = sync_derived_state(state, progress, updated_workflow, roots)
        if has_unresolved_workflow_mutations(state):
            state["mode"] = "pending_workflow_mutation"
        save_flow_state(roots, state)

    return (
        make_response(
            ok=True,
            operation="apply_workflow_mutation",
            request_id=request.get("request_id"),
            updated_files=["flow_state.json", str(workflow_path)],
            state_summary={**summary, "mutation_id": mutation_id},
        ),
        EXIT_CODES["success"],
    )


def handle(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    operation = request.get("operation")
    if operation == "propose_workflow_mutation":
        return propose_workflow_mutation(request)
    if operation == "apply_workflow_mutation":
        return apply_workflow_mutation(request)
    raise FlowError("unsupported_operation", "unsupported operation", {"operation": operation})


if __name__ == "__main__":
    main_wrapper(handle)

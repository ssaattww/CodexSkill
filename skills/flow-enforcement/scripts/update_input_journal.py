#!/usr/bin/env python3
"""Update input_journal entries through the flow-enforcement contract."""

from __future__ import annotations

from typing import Any

from flow_enforcement_common import (
    EXIT_CODES,
    FlowError,
    load_flow_state,
    main_wrapper,
    make_response,
    new_input_id,
    resolve_roots,
    save_flow_state,
    state_lock,
    utc_now,
    validate_state_root_contract,
)


def record_user_prompt(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    roots = resolve_roots(request)
    prompt = request.get("record_user_prompt")
    if request.get("classify_input") is not None or not isinstance(prompt, dict):
        raise FlowError("invalid_request_schema", "record_user_prompt must be specified alone")
    text = prompt.get("text")
    if not isinstance(text, str):
        raise FlowError("invalid_request_schema", "record_user_prompt.text must be a string")
    with state_lock(roots.state_root):
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        input_id = new_input_id(request.get("request_id"))
        entry = {
            "input_id": input_id,
            "event": prompt.get("source", "UserPromptSubmit"),
            "received_at": utc_now(),
            "text": text,
            "status": "unclassified",
            "classification": None,
            "adoption": None,
            "applied_state_updates": [],
            "superseded_by": None,
        }
        state.setdefault("input_journal", []).append(entry)
        save_flow_state(roots, state)
    return (
        make_response(
            ok=True,
            operation="record_user_prompt",
            request_id=request.get("request_id"),
            updated_files=["flow_state.json"],
            state_summary={"mode": state.get("mode"), "input_id": input_id},
        ),
        EXIT_CODES["success"],
    )


def classify_input(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    roots = resolve_roots(request)
    payload = request.get("classify_input")
    if request.get("record_user_prompt") is not None or not isinstance(payload, dict):
        raise FlowError("invalid_request_schema", "classify_input must be specified alone")
    input_id = payload.get("input_id")
    classification = payload.get("classification")
    if not isinstance(input_id, str) or not isinstance(classification, dict):
        raise FlowError("invalid_request_schema", "classify_input.input_id and classification are required")
    confidence = classification.get("confidence", 0)
    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError) as exc:
        raise FlowError("invalid_request_schema", "classification.confidence must be numeric") from exc

    with state_lock(roots.state_root):
        state = load_flow_state(roots)
        validate_state_root_contract(roots, state)
        entry = next((item for item in state.get("input_journal", []) if item.get("input_id") == input_id), None)
        if entry is None:
            raise FlowError("validation_failed", "input_id is not recorded", {"input_id": input_id})

        adoption = payload.get("adoption")
        if not adoption:
            adoption = "auto" if confidence_value >= 0.8 else "provisional" if confidence_value >= 0.5 else "needs_confirmation"
        state_effect = payload.get("state_effect") or {}
        entry["classification"] = classification
        entry["adoption"] = adoption
        entry["applied_state_updates"] = state_effect

        needs_confirmation = adoption == "needs_confirmation" or confidence_value < 0.5 or classification.get("intent") == "ambiguous"
        if needs_confirmation:
            entry["status"] = "needs_confirmation"
            state["mode"] = "pending_user_intent"
            state["pending_user_intent"] = {
                "input_id": input_id,
                "text": entry.get("text"),
                "classification": classification,
                "required_agent_action": classification.get(
                    "question_to_user",
                    "ユーザー入力の意図を確認してください。",
                ),
            }
        else:
            entry["status"] = "applied"
            mode_after = state_effect.get("mode_after")
            if isinstance(mode_after, str):
                state["mode"] = mode_after
            pending = state.get("pending_user_intent") or {}
            if pending.get("input_id") == input_id:
                state["pending_user_intent"] = None
            if classification.get("intent") in {"additional_info", "flow_change"}:
                state.setdefault("context", []).append(
                    {
                        "source": "user",
                        "type": classification.get("intent"),
                        "summary": classification.get("summary"),
                        "reason": classification.get("reason"),
                        "input_id": input_id,
                    }
                )
        save_flow_state(roots, state)

    return (
        make_response(
            ok=not needs_confirmation,
            operation="classify_input",
            request_id=request.get("request_id"),
            updated_files=["flow_state.json"],
            errors=[{"code": "user_confirmation_required", "input_id": input_id}] if needs_confirmation else [],
            state_summary={"mode": state.get("mode"), "input_id": input_id, "status": entry.get("status")},
            required_agent_action=state.get("pending_user_intent", {}).get("required_agent_action")
            if needs_confirmation
            else None,
        ),
        EXIT_CODES["user_confirmation_required"] if needs_confirmation else EXIT_CODES["success"],
    )


def handle(request: dict[str, Any]) -> tuple[dict[str, Any], int]:
    operation = request.get("operation")
    if operation == "record_user_prompt":
        return record_user_prompt(request)
    if operation == "classify_input":
        return classify_input(request)
    raise FlowError("unsupported_operation", "unsupported operation", {"operation": operation})


if __name__ == "__main__":
    main_wrapper(handle)

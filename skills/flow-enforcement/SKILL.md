---
name: flow-enforcement
description: Maintain repository-local flow state with Codex hooks and JSON state update scripts.
---

# Flow Enforcement

Use this skill when a repository has a `.codex/state/flow_state.json`, `.codex/state/progress.json`, and `.codex/workflows/*.json` flow that should be enforced by Codex hooks.

## Purpose

- `hooks/user_prompt_flow_state.py` records active-flow user prompts and asks the main agent to classify them.
- `hooks/post_tool_flow.py` updates progress after tool use and syncs derived cursor fields.
- `hooks/stop_guard.py` blocks completion while required nodes, pending input, interrupts, or workflow mutations remain unresolved.
- `scripts/*.py` are the only normal write path for `flow_state.json`, `progress.json`, and workflow mutation updates.

## Usage

All state scripts read one JSON request from stdin and write one JSON response to stdout. Requests must include `operation`, `request_id`, `actor`, `state_root`, `workflow_root`, and `step_root`.

Supported initial operations:

- `update_input_journal.py`: `record_user_prompt`, `classify_input`
- `update_workflow.py`: `propose_workflow_mutation`, `apply_workflow_mutation`
- `update_progress.py`: `mark_completed_nodes`
- `sync_flow_state.py`: `sync_derived_state`
- `validate_state.py`: `validate`

Use `hooks/hooks.sample.json` as the hook wiring template and set the root environment variables to absolute paths.

## Constraints

- Natural-language classification is not done in hooks.
- The main agent must not edit `flow_state.json` or `progress.json` directly during normal operation.
- Writes are limited to `state_root` and `workflow_root`.
- Canonical step node paths are `task_path#step_set_id/step_id`.
- `step_set_ref` is normalized to `step_set_refs`; specifying both is invalid.

## Out Of Scope

- No nested `codex exec` classifier is implemented.
- Initial workflow mutation apply supports only `add_node` and `add_dependency`.
- Hook evidence matching is intentionally minimal and should be treated as early feedback, not complete semantic proof.

---
name: chat-implementation-worker
description: Coordinate implementation in one ChatGPT chat by invoking runtime-neutral Skills and adding ChatGPT-specific permissions, persistence, PR, and handoff behavior.
---

# Chat Implementation Wrapper

## Goal

Act as the ChatGPT runtime wrapper for implementation. The user is the parent. This Skill must not redefine implementation semantics.

## Required Skills

Invoke these Skills in order:

1. `work-context-manager`
2. `implementation-worker`
3. `report-writer`
4. `chat-handoff-manager`

All four must be installed. Do not replace them with repository-external shared files.

## Runtime responsibilities

- Use the current chat and available connectors.
- Resolve permissions before writes.
- Apply changes, commit, push, and create or update the PR only when authorized.
- Persist the detailed implementation report under target-repository rules, or return it in full when writing is unavailable.
- Post the concise PR comment when authorized, or return its complete body.
- Persist the handoff under target-repository rules, or return the complete packet for copy and paste.
- The user chooses the next chat and merge action.

## Execution location

Keep both normal-chat and connected-PC execution available. Follow the user's
explicit selection, then Project Instruction; otherwise use the connected-PC
route through Remote Desktop Commander. Normal chat is the fallback only when
it is explicitly selected or the governing instruction selects it.

For normal chat, use only the current chat's authorized filesystem and
executor, if actually available. For the connected-PC route, discover the
current Remote Desktop Commander tools, identify the specified device by a
read-only call, and pin subsequent calls to that device. Use that connector
for local source reads, edits, dependency checks, and validation.

Pass the observations to `work-context-manager` and use its
`execution_environment` contract before editing. Keep another task's worktree
unchanged; create a separate worktree from the connector-confirmed target
only when authorized. Use absolute paths and a task-specific diagnostic
output directory. Recheck identity on reconnect or unexpected changes.
Prepare dependencies only inside the authorized worktree or task scratch
area; administrator access, global installation, machine configuration, and
authentication changes require separate approval. Missing dependencies or a
failed requested connection remain blocked, not an automatic route switch.

Use the GitHub connector for GitHub repository reads and updates, published
commits and branch updates, Issues, PRs, and comments. PC access does not
authorize replacing it with terminal `gh`, authenticated Git network
operations, or direct REST calls. Local Git inspection, worktree isolation,
and preparing content do not grant publication permission.

Run authorized local validation before a CI-triggering publication, preserving
both successful and failed results, stdout, stderr, and required diagnostic
logs. Compare the publication tree with validated local content; bind dirty
source evidence to its fingerprint, not only its baseline HEAD. Follow the
verification-route rules below for separate publication and CI states.

When a document self-check is required, read the applicable Skill, references,
before/after text, context, and definitions from the verified source through
the selected route. The current chat reads and judges the text; command
success or Remote Desktop Commander is not semantic review evidence. Keep
self-check and mechanical-check outcomes separate, and do not use either as
proof that normal or independent review was performed.

## Verification-route execution

Use the capability resolved by `work-context-manager`, rather than assuming a
route from ChatGPT alone.

- `local_execution_available`: run relevant local validation before a
  review-target commit; keep normal review/fix loops local and do not wait for
  CI. Validate the pushed change before any CI-triggering push, run the
  repository-defined full local gate before final push, and after attestation
  wait once only for exact-head required `pull_request` CI.
- `remote_ci_only`: after an authorized push, wait for matching current-HEAD
  CI as formal verification evidence and record absent, pending, or failed
  evidence honestly.

Commit, push, and CI wait are separate states. Do not put CI-wait semantics in
`implementation-worker`.

## Modes

- `initial implementation`
- `review follow-up`

Pass the selected mode and resolved context to `implementation-worker`.

## Boundaries

- Do not start another worker or sub-agent, including agent CLIs through a PC terminal.
- Do not implement rules locally when the required Skill is unavailable; report the missing dependency.
- Do not issue an independent review verdict.
- Do not exceed current-chat permissions.
- Do not merge.

## Completion condition

Complete when the required Skills have produced context, implementation
evidence, report output, and a transportable handoff; the selected verification
route and separate commit, push, and CI states are recorded; authorized
repository and PR updates are complete; and no merge was performed.

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
for local source reads, edits, dependency checks, validation, and authorized
Git commit and push operations. Keep commit and push on the pinned PC and
worktree; do not transfer the source tree into the chat runtime for publication.

Pass the observations to `work-context-manager` and use its
`execution_environment` contract before editing. Keep another task's worktree
unchanged; create a separate worktree from the connector-confirmed target
only when authorized. Use absolute paths and a task-specific diagnostic
output directory. Recheck identity on reconnect or unexpected changes.
Prepare dependencies only inside the authorized worktree or task scratch
area; administrator access, global installation, machine configuration, and
authentication changes require separate approval. Missing dependencies or a
failed requested connection remain blocked, not an automatic route switch.

Use the GitHub connector for remote repository evidence, Issues, PRs,
comments, and exact-head CI evidence. On the connected-PC route, an authorized
Git push uses the pinned PC's existing Git remote and authentication through
Remote Desktop Commander. Do not use terminal `gh` or direct REST calls, and
do not change Git credentials or authentication settings without separate
approval. Local Git commit or push still requires explicit write permission.

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

### Node.js verification in normal chat

When local execution is authorized and actually available, check `node --version` and `npm --version`; do not infer that either is usable from the runtime name. Record three identities separately: the source baseline commit SHA, the actual verification candidate (including a manifest or content fingerprint for dirty or reconstructed files), and, when a PR exists, its current head SHA. Use the GitHub connector within its existing permissions to obtain source and relevant CI artifacts. Do not substitute unauthenticated `git clone`, direct REST calls, or other credentials for an inaccessible private repository.

Keep repository source, retrieved CI diagnostics or attachments, and newly generated validation output in three separate temporary areas. Record connector references separately from the local paths materialized for commands. Transfer and extract files only through existing authorized means; verify their recorded SHA, manifest, or hashes before use. Before extracting a ZIP, check its entry names and destination; do not extract unexpected paths or entries that leave the permitted area. Missing material or any identity mismatch leaves the affected validation unconfirmed; never mix files from different candidates.

Inspect `package.json`, the applicable lockfile, existing `node_modules`, available cache, and declared scripts. Verify existing dependencies against the lockfile. If installation is authorized, use the project's approved lockfile-preserving command, for example `npm ci`, in an isolated working area. Record the observed Node.js and npm versions, package manager and version constraints, and lockfile and dependency state. If Node.js, npm, required dependencies, network access, or permission is unavailable, record affected checks as not run or blocked. Do not install globally or change authentication.

Follow the project’s declared commands. A typical order is focused tests for the changed area, relevant build and lint scripts, then broader tests when required. Treat these as examples only; do not assume a script exists. Record each command, exit code, outcome, environment, candidate identity, and the available test results and saved stdout/stderr paths. Record why any check was not run.

Keep local results separate from formal CI. For CI, record the run ID and compare its head SHA with the PR’s current head; inspect the relevant job and step results and diagnostics. A matching SHA alone is insufficient: a required check that was skipped, cancelled, missing, or not run is not a success. Record the CI event and run head SHA. For a failure, inspect available stdout, stderr and test results and record what the diagnostics show. If there is no matching PR run or the diagnostics are missing or inaccessible, the affected evidence remains unconfirmed.

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

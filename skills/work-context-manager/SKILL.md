---
name: work-context-manager
description: Resolve authoritative task context, repository state, scope, target identity, validation policy, and write boundaries without depending on a Codex parent or ChatGPT chat runtime.
---

# Work Context Manager

## Goal

Produce a runtime-neutral work context that another Skill can use for implementation, review, or report generation.

## Runtime independence

This Skill does not assume:

- a Codex parent agent,
- a Codex sub-agent,
- a ChatGPT user acting as parent,
- cross-chat memory,
- a particular repository connector,
- permission to write, commit, push, comment, or merge.

The caller owns tool selection, permissions, persistence, and delegation.

## Authority order

Use applicable sources in this order:

1. the user's current explicit instruction,
2. the target repository's instructions and project configuration,
3. the accepted Issue, task entry, and design,
4. the target PR and repository evidence,
5. earlier reports and handoffs.

Do not silently resolve conflicts between authoritative sources. Return the conflict as blocked context.

## Required discovery

Resolve as much as the available evidence permits:

- repository and repository instructions,
- Issue, task, phase, accepted scope, and non-goals,
- branch, base ref, PR, current HEAD, and relevant commit range,
- requirements and design references,
- changed files, target files, and direct dependencies,
- applicable findings and reviewed HEAD,
- development method and testing order required by the target project,
- validation commands, workflow entry points, and required failure diagnostics,
- actual execution location, source identity, dependencies, and ownership,
- actual local-execution capability and the resulting verification route,
- matching current-HEAD CI runs, jobs, and artifacts,
- report and handoff naming rules,
- allowed and forbidden writes,
- unknown, blocked, unexplored, and not-applicable items.

An Issue or PR identifier is normally sufficient when repository evidence determines the remaining state unambiguously.

## Scope and safety

- Work on one accepted task or PR scope at a time.
- Do not broaden scope through unrelated cleanup or redesign.
- Do not modify work owned by another task or PR.
- Do not revert unrelated changes.
- Preserve intentionally untouched areas and the reason they remain untouched.
- Do not expose credentials, secrets, private tokens, or unrelated personal information.
- The target project owns whether work is TDD, test-after, validation-only, or another method.
- CodexSkill repository maintenance is non-TDD unless the user explicitly changes that policy.

## Target identity and evidence

Make these explicit when applicable:

- branch,
- base ref,
- full current HEAD SHA,
- reviewed HEAD,
- relevant commit range.

Use only CI evidence whose `head_sha` matches the target HEAD when current-HEAD evidence is required. A missing matching run is not success.

## Verification capability

Resolve `verification_capability` from tools actually available to the current
runtime, not from its name:

- `local_execution_available`: a usable local test or validation executor is
  available.
- `remote_ci_only`: no usable local executor is available.

Record the evidence for that decision. Keep commit, push, and CI wait as
separate states. This core Skill resolves the route and evidence requirements;
the runtime wrapper owns authorized push and any CI waiting behavior.

## Execution environment evidence

Keep execution location separate from `verification_capability`. The caller
selects an authorized tool and requested location; this core Skill resolves
the evidence, not a vendor-specific connection or permission policy.

- Record the actual machine, shell, absolute working directory, repository,
  branch, HEAD, source state, ownership, and allowed writes before execution.
- Compare the observed source with the target resolved from authoritative
  repository evidence. A different HEAD or another task's dirty worktree is
  not a usable substitute. Do not switch, reset, clean, or stash another
  task's work to manufacture a match. An authorized separate worktree or
  source snapshot must have its own identity and output directory.
- A successful connection alone does not prove that required commands or
  dependencies work. Record each required dependency as available, missing,
  or not checked; missing required tools cannot produce passing validation.
- For dirty or reconstructed sources, preserve a content manifest or diff
  fingerprint as well as the baseline HEAD. Record which files and untracked
  inputs the fingerprint covers; a baseline SHA alone is insufficient.
- Bind each validation result to its actual execution environment and source
  identity. Keep command, exit status, results, stdout, stderr, and diagnostic
  logs for both success and failure when execution is authorized. Report any
  missing evidence instead of treating an attempted command as success.
- Before publication, compare the intended repository tree with the locally
  validated content. Changed content invalidates the affected evidence.
- Recheck identity and authorization after reconnection, location changes,
  unexpected concurrent edits, and before writes or reuse of evidence.
  An unavailable requested location blocks dependent operations; capability
  classification does not authorize a silent fallback or skipped gate.
- Distinguish connected-machine paths, runtime-local paths, and connector
  file references. Do not expose credentials, complete environment dumps,
  or unrelated personal files in evidence.

## Output contract

Return a structured context containing:

```yaml
repository: owner/name | unknown
issue_or_pr: string | null
task_id: string | null
mode: implementation | review | report | unknown
branch: string | unknown
base_ref: string | null
current_head: full_sha | unknown
reviewed_head: full_sha | null
verification_capability: local_execution_available | remote_ci_only | unknown
verification_capability_evidence:
  - string
execution_environment:
  kind: runtime_local | connected_computer | none | unknown
  tool: string | null
  machine_id: string | null
  connection: available | unavailable | not_applicable | unknown
  os: string | null
  shell: string | null
  working_directory: absolute_path | null
  repository: owner/name | unknown
  branch: string | unknown
  head_sha: full_sha | unknown
  source_state: clean | dirty | snapshot | unknown
  source_fingerprint: string | null
  ownership: current_task | other_task | read_only | unknown
  writable_paths:
    - string
  dependencies:
    - name: string
      status: available | missing | not_checked
      evidence: string
  evidence:
    - string
execution_state:
  technical_head: full_sha | unknown
  administrative_parent: full_sha | null
  commit: commit_pending | committed | not_required | unknown
  push: push_pending | pushed | not_required | unauthorized | unknown
  ci_wait: ci_wait_pending | ci_wait_completed | not_required | unavailable | unknown
  full_local_equivalence_gate:
    state: not_started | passed | invalidated | not_required | unsupported | unknown
    candidate_head: full_sha | unknown
    invalidated_runs:
      - head: full_sha
        reason: string
scope:
  - string
non_goals:
  - string
authoritative_requirements:
  - source: string
    reference: string
    summary: string
write_boundary:
  allowed:
    - string
  forbidden:
    - string
development_policy:
  method: string | unknown
  testing_order: string | unknown
validation:
  commands:
    - string
  required_failure_diagnostics:
    - string
ci:
  matching_run: string | null
  conclusion: string | unknown
unknown:
  - string
blocked:
  - string
remaining_risks:
  - string
```

## Merge boundary

This Skill does not merge and does not grant merge permission to its caller.

## Completion condition

Complete when discoverable state has been resolved, conflicts and unknowns remain explicit, scope and target identity are usable by the next Skill, and no runtime-specific execution or persistence behavior has been assumed.

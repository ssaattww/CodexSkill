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

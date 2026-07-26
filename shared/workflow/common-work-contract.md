# Common Work Contract

## Purpose

This file is the runtime-neutral source of truth for work performed through Codex agents and ChatGPT worker chats.

Runtime adapters may add execution-specific rules, such as Codex sub-agent dispatch or ChatGPT user-coordinated chats. They must not duplicate, weaken, or contradict this contract.

## Authority and project policy

Use authoritative sources in this order when they apply:

1. the user's current explicit instruction,
2. the target repository's instructions and project configuration,
3. the accepted Issue, task entry, and design,
4. the target PR and repository evidence,
5. earlier reports and handoffs.

When authoritative sources conflict, stop and surface the conflict instead of selecting a convenient interpretation.

The target project's instructions own the development method and testing order. Do not impose TDD, non-TDD, a test framework, or a validation command that the target project does not require.

The CodexSkill repository itself does not use TDD unless the user explicitly changes that policy. Repository maintenance may use existing lint, schema validation, build checks, and packaging verification as normal validation.

## State discovery

Resolve discoverable state before asking the user. Depending on the task, this includes:

- repository and repository instructions,
- Issue, task, phase, and accepted scope,
- branch, base ref, PR, and current HEAD,
- requirements and design references,
- changed files and direct contract dependencies,
- reports, handoffs, comments, and review rounds,
- validation wiring, workflow runs, jobs, and artifacts,
- report naming and destination rules,
- available permissions and write boundaries.

An Issue or PR identifier is normally sufficient when those sources determine the remaining state unambiguously.

Ask the user only when authoritative sources conflict, multiple unresolved candidates remain, or a product decision cannot be inferred safely.

## Scope and write safety

- Work on one accepted task or PR scope at a time.
- Do not broaden scope through unrelated cleanup or redesign.
- Do not modify work owned by another task or PR.
- Do not revert unrelated changes.
- Preserve intentionally untouched areas and record why they remain untouched.
- Do not place credentials, secrets, private tokens, or unrelated personal information in repository artifacts.
- Respect the runtime adapter's write boundary.

## Commit and target identity

Make the applicable target identity explicit:

- branch,
- base ref when relevant,
- full current HEAD SHA,
- reviewed HEAD for a review round,
- commit range when a follow-up depends on earlier work.

Do not describe an earlier HEAD as the final result after the branch has moved.

## Validation and CI evidence

- Run focused validation first, then relevant broader validation required by the target project.
- Record the exact command or workflow, result, target HEAD, and evidence location.
- Preserve or inspect failure diagnostics required by the target project.
- Use only CI runs whose `head_sha` matches the target HEAD when the project requires current-HEAD evidence.
- Do not substitute a run from another SHA.
- A missing matching run is `not_run`, `unknown`, or `not_available`; it is not success.
- CI success does not replace implementation inspection or review.
- Unknown, blocked, unexplored, and not-applicable items must remain explicit.

## Reports, comments, and handoffs

A detailed report, a concise PR comment, and a handoff are different artifacts.

- The detailed report contains the durable scope, evidence, outcome, and remaining risk.
- The concise PR comment summarizes the detailed report and links or refers to it. It does not replace the report.
- The handoff transports enough state for another runtime context to continue. It does not replace the report.
- Do not invent missing evidence to complete any artifact.
- When repository writing or PR commenting is unavailable, return the complete body and state why it was not persisted.

## Merge boundary

Agents and worker chats do not merge. The user owns the merge decision and merge action.

## Completion condition

Work governed by this contract is complete only when the accepted scope is completed or explicitly blocked, the target identity is explicit, required validation and current-HEAD evidence are recorded accurately, reports and handoffs required by the runtime adapter are available, remaining risks and unknowns are stated, and no merge was performed.
---
name: review-enforcer
description: Require a dedicated review step for every task before the task is treated as complete. Use when implementation appears done, before final progress updates, before commit/PR closure, or whenever a review result must be captured and addressed task by task.
---

# Review Enforcer

Prevent completion without review.

## Goal

Make task completion impossible until review has run and its outcome is recorded.

## Execution owner

Run this skill as: `parent`

- Parent owns completion gating and finding disposition.
- The actual review work inside this skill remains mandatory sub-agent work.

## Inputs

Before running this skill, gather:

- task-scoped diff or changed-file set
- surrounding repository context the reviewer may need to inspect directly
- relevant validation context and reports
- current task identifier and review scope
- active session reviewer assignment, if one already exists
- the parent agent's current model and any user override of reviewer reasoning effort
- task-specific review criteria that were established earlier in the same session, such as audit decisions, design rules, naming rules, or comment standards
- when Markdown-related work is in scope, the `markdown-word-checker` result and any proposed exact whitelist, `prh`, or target-exclusion entries with the user's explicit review state

## Required flow

1. Prepare a task-scoped diff or changed-file set, but keep broader workspace context available for direct inspection by the reviewer.
2. When the review touches source layout, naming, partial types, XML documentation, or test comments, read [references/session-review-shape-policy.md](references/session-review-shape-policy.md) before drafting the review request.
3. When the task changes Markdown, Markdown lint configuration, reports, task tracking, design documents, or review-facing text, call `markdown-word-checker` before completion and include its result in the review report.
4. Treat a `markdown-word-checker` `failed gate` result as a blocking review gate unless the current task is explicitly to introduce a failing stricter gate and the failure is recorded as the intended current state in the implementation report and tracking.
5. Treat a `markdown-word-checker` `needs user review` result as a stopped gate. Exact entry review approval alone is not enough; the appropriate implementation owner must apply the approved repo-specific setting change, rerun the affected focused or full lint, and update the same report before the review gate can close.
6. Treat a `markdown-word-checker` `unsupported` result as requiring caller disposition, not as pass. If Markdown lint is mandatory for the task/review gate, or the target repository has the relevant check configured, unsupported alone cannot complete the review gate.
7. In a repository without Markdown lint setup, if neither focused lint nor full lint can run immediately after Markdown creation, record the unsupported reason and remaining risk in the review report. Only treat it as a held disposition when the documented normal path still satisfies the user's intent.
8. When the task creates, rebuilds, or changes Markdown whitelist, `prh`, or target-exclusion entries, verify that the user explicitly reviewed the exact entries before the task is treated as complete.
9. Reuse the same review `sub-agent` for the session when one is already assigned and still available; otherwise select one reviewer and record that assignment in the report or parent progress note.
10. Include task-specific review criteria from earlier audit/design decisions in the review request, and require the reviewer to evaluate the diff against those criteria.
11. Run review for that task only as a `sub-agent` task through `sub-agent-task-manager`.
12. Instruct the review `sub-agent` to use the built-in review behavior: findings first, severity-ordered, with file/line references when available.
13. Select the parent agent's current model for the reviewer and use `high` reasoning effort unless the user overrides it. Pass that profile through `sub-agent-task-manager` into the actual spawn arguments; for a fresh reviewer spawn, use `fork_turns: "none"`, or an explicit positive partial fork only when bounded context is required.
14. Materialize the built-in review result into the pre-created report file under `reports/` while preserving the existing template format and filling only the intended blank sections.
15. Prefer having the review `sub-agent` write the report file directly; treat parent-side report materialization as fallback only.
16. If the review `sub-agent` does not write the report file directly, have the parent write it immediately from the returned review findings.
17. Once review has been dispatched, keep waiting or re-polling until the review `sub-agent` finishes unless the user explicitly tells you to stop.
18. Treat report structure as parent-owned. The reviewer may fill only blank sections or placeholder values and must not repair, reorder, rename, or reformat the template.
19. Address findings that break the intended normal path.
20. If a finding means the user still cannot do what they intend even with careful use, stop and confirm with the user before deciding whether to expand scope.
21. If a finding is avoidable by careful use and the user can still achieve the intended goal, record it in the report and leave it on hold until a concrete problem appears or the user explicitly promotes it.
22. Re-run review if required, using the same session reviewer unless the reference policy allows a change.
23. Only then allow progress sync and Git submission.

If mandatory review `sub-agent` dispatch cannot be executed because the current run lacks explicit user permission for delegation, stop and ask the user before continuing. Do not silently replace mandatory `sub-agent` review with parent review.

When creating a new review report file, call `report-output-manager`.

## Rules

- Review one task at a time.
- Do not batch multiple unrelated tasks into one review.
- Do not mark a task complete without recorded review evidence.
- Distinguish between “no findings” and “review not run”.
- Review is mandatory sub-agent work.
- Reviewer assignment is never switchable to the parent.
- A single session should normally use one reviewer `sub-agent` for initial review and re-review so review standards remain consistent.
- If the reviewer must change because the original reviewer is unavailable, conflicted, or explicitly replaced by the user, record the reason in the review report.
- When a session has established concrete review criteria, such as naming, placement, XML comment, test-comment, or design-consistency rules, later reviews in that session must apply those criteria unless the user supersedes them.
- The reviewer model is the parent agent's current model. Default reviewer reasoning effort is `high`; the user may override that effort for the current run.
- Apply the selected reviewer model and reasoning effort through the central `sub-agent-task-manager` spawn contract, not as prompt text. Do not use a full-history fork with that override.
- If mandatory `sub-agent` review is blocked by permission or execution-mode constraints, ask the user explicitly instead of improvising a parent-side substitute.
- Review requests should explicitly ask for a code review, not a generic diff summary.
- Review requests should tell the `sub-agent` to read the pre-created report first and preserve its headings, order, spacing, and any prefilled text.
- Review requests should explicitly allow and require the reviewer to fill the pre-created report file directly.
- Report template ownership stays with the parent; the reviewer is not allowed to fix formatting, headings, spacing, or other report structure.
- Markdown text quality is part of the review gate. Do not treat Markdown-related changes as review-complete until `markdown-word-checker` reports per-scope results and an aggregate gate state that the caller can disposition, or an intentionally failing stricter gate is explicitly documented for the current task.
- If Markdown lint is mandatory for the current task/review gate, or the repository has the relevant Markdown check configured, `unsupported` alone cannot complete the gate.
- In a repository without Markdown lint setup, when focused lint and full lint are both unavailable, `unsupported` may be held only with a report entry that records the reason, remaining risk, and why the user's intended normal path is still satisfied.
- Repository-specific whitelist data must stay in the target repository. Do not put project terms into this skill; `markdown-word-checker` owns the detailed Markdown lint routing and reads repo-local `tools/lint/` configuration.
- Changes to `tools/lint/markdown-whitelist.yaml`, `tools/lint/prh.yml`, or target exclusions require explicit user review before the repo-specific setting edit can proceed. Do not treat exact entry review alone as completion; rerun the affected focused or full lint and update the report before closing the review gate.
- The review report must include the `markdown-word-checker` result, including command evidence, focused/full per-scope results, aggregate gate state, `skip` / `unsupported` / `failed gate` / `needs user review` classification, exact-entry review requirement, and any unresolved risk.
- Prefer shipping a working normal path over delaying for a speculative full hardening pass.
- If a review concern is real but avoidable by careful use, and the user can still achieve the intended goal, record it in the report and mark it as held rather than blocking release immediately.
- If a review concern means the user cannot achieve the intended goal, stop and confirm with the user unless the intended normal path is already broken and should simply be fixed.
- Do not cancel, replace, or abandon an in-flight review `sub-agent` only because it is slow or a wait timed out; keep waiting until it completes unless the user explicitly says to stop.
- Do not constrain the reviewer to a parent-authored diff summary when surrounding workspace context matters.
- Built-in review output alone is not sufficient; it must also exist in the report file.

## Required report contents

Include:

- task identifier
- scope reviewed
- reviewer or sub-agent used
- reviewer reuse decision or reviewer-change reason
- established review criteria used for this review, if any
- findings summary
- file/line references for findings when available
- explicit `no findings` statement when applicable
- disposition of findings
- explicit hold/disposition for non-blocking concerns when they are deferred
- final outcome

## Outputs

After this skill runs, there should be:

- a review report in `reports/`
- explicit findings or explicit `no findings`
- a clear disposition for whether follow-up work is required

## Completion condition

This skill is complete only when:

- review has run for the current task
- findings are materialized in the report file
- required follow-up has been addressed or explicitly left open

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager`.

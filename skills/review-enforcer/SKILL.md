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
- task-specific review criteria that were established earlier in the same session, such as audit decisions, design rules, naming rules, or comment standards

## Required flow

1. Prepare a task-scoped diff or changed-file set, but keep broader workspace context available for direct inspection by the reviewer.
2. Read [references/session-reviewer-policy.md](references/session-reviewer-policy.md) before selecting or reusing a reviewer.
3. Reuse the same review `sub-agent` for the session when one is already assigned and still available; otherwise select one reviewer and record that assignment in the report or parent progress note.
4. Include task-specific review criteria from earlier audit/design decisions in the review request, and require the reviewer to evaluate the diff against those criteria.
5. Run review for that task only as a `sub-agent` task through `sub-agent-task-manager`.
6. Instruct the review `sub-agent` to use the built-in review behavior: findings first, severity-ordered, with file/line references when available.
7. Use `gpt-5.4` with `high` reasoning effort as the default review `sub-agent` unless the user explicitly overrides the reviewer model for the current run.
8. Materialize the built-in review result into the pre-created report file under `reports/` while preserving the existing template format and filling only the intended blank sections.
9. Prefer having the review `sub-agent` write the report file directly; treat parent-side report materialization as fallback only.
10. If the review `sub-agent` does not write the report file directly, have the parent write it immediately from the returned review findings.
11. Once review has been dispatched, keep waiting or re-polling until the review `sub-agent` finishes unless the user explicitly tells you to stop.
12. Treat report structure as parent-owned. The reviewer may fill only blank sections or placeholder values and must not repair, reorder, rename, or reformat the template.
13. Address findings that break the intended normal path.
14. If a finding means the user still cannot do what they intend even with careful use, stop and confirm with the user before deciding whether to expand scope.
15. If a finding is avoidable by careful use and the user can still achieve the intended goal, record it in the report and leave it on hold until a concrete problem appears or the user explicitly promotes it.
16. Re-run review if required, using the same session reviewer unless the reference policy allows a change.
17. Only then allow progress sync and Git submission.

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
- Default reviewer model is `gpt-5.4` with `high` reasoning effort unless the user explicitly chooses another reviewer configuration.
- If mandatory `sub-agent` review is blocked by permission or execution-mode constraints, ask the user explicitly instead of improvising a parent-side substitute.
- Review requests should explicitly ask for a code review, not a generic diff summary.
- Review requests should tell the `sub-agent` to read the pre-created report first and preserve its headings, order, spacing, and any prefilled text.
- Review requests should explicitly allow and require the reviewer to fill the pre-created report file directly.
- Report template ownership stays with the parent; the reviewer is not allowed to fix formatting, headings, spacing, or other report structure.
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

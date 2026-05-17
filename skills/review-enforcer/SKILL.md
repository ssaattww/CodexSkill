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
- when Markdown whitelist work is in scope, the proposed whitelist entries and the user's explicit review state for each entry

## Required flow

1. Prepare a task-scoped diff or changed-file set, but keep broader workspace context available for direct inspection by the reviewer.
2. When the review touches source layout, naming, partial types, XML documentation, or test comments, read [references/session-review-shape-policy.md](references/session-review-shape-policy.md) before drafting the review request.
3. When the task changes Markdown, markdown lint configuration, reports, task tracking, design documents, or review-facing text, run the repository Markdown lint gate before completion. Prefer `npm run lint:md` when the target repository provides it. If the repository uses the standard review-enforcer scripts, the shared implementation lives under [scripts/](scripts/) and the repository owns only its `tools/lint/markdown-whitelist.yaml`, `tools/lint/markdown-targets.json`, package wiring, and local setup memo.
4. Treat Markdown lint failure as a blocking review gate unless the current task is explicitly to introduce a failing stricter gate and the failure is recorded as the intended current state in the implementation report and tracking.
5. When the task creates, rebuilds, or changes a Markdown whitelist, verify that the user explicitly reviewed the exact whitelist entries before the task is treated as complete.
6. Reuse the same review `sub-agent` for the session when one is already assigned and still available; otherwise select one reviewer and record that assignment in the report or parent progress note.
7. Include task-specific review criteria from earlier audit/design decisions in the review request, and require the reviewer to evaluate the diff against those criteria.
8. Run review for that task only as a `sub-agent` task through `sub-agent-task-manager`.
9. Instruct the review `sub-agent` to use the built-in review behavior: findings first, severity-ordered, with file/line references when available.
10. Use `gpt-5.5` with `high` reasoning effort as the first-choice review `sub-agent` unless the user explicitly overrides the reviewer model for the current run. If `gpt-5.5` is unavailable, use `gpt-5.4` with `high` reasoning effort as the next choice.
11. Materialize the built-in review result into the pre-created report file under `reports/` while preserving the existing template format and filling only the intended blank sections.
12. Prefer having the review `sub-agent` write the report file directly; treat parent-side report materialization as fallback only.
13. If the review `sub-agent` does not write the report file directly, have the parent write it immediately from the returned review findings.
14. Once review has been dispatched, keep waiting or re-polling until the review `sub-agent` finishes unless the user explicitly tells you to stop.
15. Treat report structure as parent-owned. The reviewer may fill only blank sections or placeholder values and must not repair, reorder, rename, or reformat the template.
16. Address findings that break the intended normal path.
17. If a finding means the user still cannot do what they intend even with careful use, stop and confirm with the user before deciding whether to expand scope.
18. If a finding is avoidable by careful use and the user can still achieve the intended goal, record it in the report and leave it on hold until a concrete problem appears or the user explicitly promotes it.
19. Re-run review if required, using the same session reviewer unless the reference policy allows a change.
20. Only then allow progress sync and Git submission.

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
- Default reviewer model priority is `gpt-5.5 high` first, then `gpt-5.4 high` if `gpt-5.5` is unavailable, unless the user explicitly chooses another reviewer configuration.
- If mandatory `sub-agent` review is blocked by permission or execution-mode constraints, ask the user explicitly instead of improvising a parent-side substitute.
- Review requests should explicitly ask for a code review, not a generic diff summary.
- Review requests should tell the `sub-agent` to read the pre-created report first and preserve its headings, order, spacing, and any prefilled text.
- Review requests should explicitly allow and require the reviewer to fill the pre-created report file directly.
- Report template ownership stays with the parent; the reviewer is not allowed to fix formatting, headings, spacing, or other report structure.
- Markdown text quality is part of the review gate. When a repository has Markdown lint wiring, do not treat Markdown changes as review-complete until that lint gate is either passing or explicitly documented as an intentionally failing stricter gate for the current task.
- Repository-specific whitelist data must stay in the target repository. Do not put project terms into this skill; the shared scripts should read `tools/lint/markdown-whitelist.yaml` from the current repository.
- Changes to `tools/lint/markdown-whitelist.yaml` require explicit user review before the task can be treated as complete. Do not add, remove, or rewrite whitelist entries and then close the task only through agent review; the user must explicitly review the whitelist content because it defines accepted terminology and meanings.
- When fixing whitelist failures, prefer registering the concrete compound term or phrase that carries the intended meaning. Registering a single generic word is a last resort because it broadens accepted vocabulary beyond the reviewed concept.
- Use whitelist `aliases` only for alternate forms that remain intentionally valid. Put spellings that should be corrected to a canonical term in `tools/lint/prh.yml` instead.
- Do not add generated batches of whitelist entries to make lint pass. Present small concept groups to the user and edit only entries the user explicitly approves.
- The standard Markdown lint scripts support explicit file review. `scripts/list-markdown-targets.js --files <path...>` lists only those Markdown files after repository ignore rules are applied. Pipe that output to `textlint` or `scripts/run-cspell-markdown.js` when focused validation is needed. `scripts/check-markdown-whitelist.js --files <path...>` checks only those Markdown files plus whitelist descriptions. Use explicit file mode for focused review evidence when full-scope lint is intentionally failing because the stricter gate is being introduced.
- For repositories that need Japanese vocabulary inspection, use `scripts/extract-markdown-vocabulary-sudachi.py` for SudachiPy-based `.md`/`.txt` extraction and `scripts/check-markdown-whitelist-sudachi.py` for the matching whitelist gate. These scripts still read repository-owned `tools/lint/markdown-targets.json` and `tools/lint/markdown-whitelist.yaml`.
- When `scripts/extract-markdown-vocabulary-sudachi.py` emits ChikkarPy synonym candidates, treat them only as candidate-grouping evidence. Do not automatically convert synonym candidates into whitelist `aliases` or `prh` rules without explicit user review.
- Markdown link addresses are not prose and should be excluded from spelling / whitelist checks. The shared scripts should ignore the address part of inline links and reference links while leaving visible link text subject to lint.
- When Markdown lint excludes inline code or quoted identifiers, the reviewer must also check for lint evasion. Do not accept prose changes that merely wrap ordinary English words, katakana words, or unexplained terms in backticks or quotation marks to avoid the whitelist gate; backticks should be used only for real code, identifiers, commands, file paths, UI labels, or explicitly itemized terms.
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

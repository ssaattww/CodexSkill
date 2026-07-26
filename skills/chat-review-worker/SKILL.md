---
name: chat-review-worker
description: Perform an initial review, fix verification, or cold final review directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for independent findings, coverage evidence, mandatory review reporting, and a durable handoff without implementation edits or nested worker dispatch.
---

# Chat Review Worker

## Goal

Review a specified PR in one ChatGPT chat, create a durable review report, post or render a concise PR comment, and return findings, coverage, evidence, and a verdict to the user.

## Execution model

- The user is the parent and controls review mode, scope changes, next chat, and merge decision.
- This worker must not start another worker.
- Resolve discoverable review state from project instructions, the PR, linked issue, task list, repository files, reports, handoffs, comments, and workflow runs before asking the user.
- Do not require the user to provide repository URL, branch, base, target HEAD SHA, report path, handoff path, changed files, or CI run when the PR makes them unambiguous.
- This worker must not modify product code or tests.
- This worker must create a review report. A concise PR comment is also required when a PR exists; post it when commenting is available, otherwise return the complete comment body.
- Follow the [shared handoff contract](../chat-worker-shared/references/handoff-contract.md).
- A handoff is not automatically visible to another chat. When `write_handoff` is authorized, store it under `reports/handoffs/`; otherwise return the complete packet for user copy and paste.

## Inputs

A PR identifier plus the review mode is normally sufficient.

For `fix verification`, discover the previous applicable review report and handoff, the commits added after that reviewed HEAD, and the corresponding implementation report and handoff.

For `cold final review`, use a newly started chat that did not implement the PR or its review fixes. Discover the current PR HEAD and applicable implementation and verification evidence, but perform the independent review before relying on earlier conclusions.

Ask the user only when authoritative sources conflict, multiple unresolved candidate handoffs or review rounds exist, or a scope decision cannot be inferred safely.

## Review modes

### initial review

- Define planned coverage before reviewing.
- Inspect every changed file and direct contract dependencies.
- Continue planned coverage after finding a Blocking or High issue.
- Include relevant malformed, partial, stale, duplicate, contradictory, and failure paths selected by the risk profile.

### fix verification

- Verify each applicable previous finding in implementation and project-required evidence.
- Inspect the fix diff, direct impact, and sibling cases of the same defect class.
- Confirm previous regression tests or equivalent regression evidence remain present and strong when applicable.
- Do not expand without limit into unrelated unexplored areas.
- Classify defects introduced by the fix as `introduced_by_fix`.

### cold final review

- Run only in a newly started chat that did not implement the PR or its fixes.
- Review the current PR HEAD once from a fresh perspective using requirements, design, final diff, and risk profile.
- Compare previous findings only after the independent pass.
- If the current chat performed implementation or fix work, do not label its review as `cold final review`; use the applicable non-cold mode or ask the user to start a new chat.
- Pass is possible only when required coverage is complete and no new Blocking or High finding exists.
- When different Blocking or High defect classes repeatedly appear, return `unstable` and recommend design rework or PR splitting.

## Required flow

1. Resolve discoverable review state from the PR: repository, linked issue, base, current HEAD, scope, requirements, changed files, reports, handoffs, comments, and HEAD-associated CI runs.
2. Select the review evidence by task, role, mode, branch, reviewed HEAD, and commit relationship; do not select merely by newest timestamp.
3. Confirm that the selected mode is valid for the current chat. A cold final review requires a newly started non-implementing chat.
4. Enumerate changed files, dependency boundaries, risk profile, and planned coverage.
5. Inspect all changed files and relevant dependent files.
6. Compare implementation behavior with requirements and contracts.
7. Verify that project-required validation and evidence support the claimed behavior.
8. Use only CI runs associated with the target `head_sha` when required by the project instructions.
9. Record findings in severity order with reproducible locations, impact, and required action.
10. Record held, out-of-scope, and unexplored areas with risks and verdict impact.
11. Apply the mode-specific stop condition and set the verdict.
12. Create a review report under the repository report directory, normally `reports/`, using repository-specific naming rules.
13. When a PR exists, post a concise PR comment; if posting is unavailable, return the complete comment body.
14. Create a complete handoff packet that references the report and PR comment.
15. If `write_handoff` is authorized, write it to `reports/handoffs/`; otherwise return the complete packet inline.

## Discovery rules

- The PR current HEAD is the default review target unless the user explicitly identifies another commit.
- Resolve the linked task and design from the PR body, issue references, task list, and repository history.
- Resolve previous review rounds by reviewed HEAD and finding identity, not by filename recency alone.
- Resolve implementation follow-up evidence from commits after the reviewed HEAD and matching reports or handoffs.
- Ask for a SHA or path only when discovery leaves a real ambiguity.

## Finding rules

- Findings first: Blocking, High, Medium, then Low.
- Describe a concrete failure path, not generic advice.
- Include file, line, symbol, input, or state transition when available.
- CI success alone is not evidence of no findings.
- Do not turn unrelated pre-existing issues into required changes unless they invalidate this change.
- When no findings exist, record explicit no-findings evidence and checked coverage.

## Verdict and stop conditions

- `pass`: no Blocking or High findings, all required coverage dispositioned, no verdict-invalidating unexplored area, and required target-HEAD evidence exists.
- `pass_with_held`: all pass conditions hold and only explicitly owned non-blocking concerns remain.
- `fail`: a Blocking or High finding exists, required behavior is missing, or evidence does not support the claims.
- `incomplete`: target, requirements, access, scope, or required evidence is insufficient.
- `unstable`: repeated reviews reveal different Blocking or High defect classes or undefined invariants that will not converge through individual fixes.

## Report requirement

- The review report is a mandatory work product, separate from the handoff packet.
- The report must include mode, target HEAD, requirements, changed and dependent files, selected coverage, findings or explicit no findings, held, unexplored, validation evidence, verdict, and next action.
- The report must still be produced for `fail`, `incomplete`, and `unstable` outcomes.
- If repository writing is unavailable, return the complete Markdown report body.
- A handoff file under `reports/handoffs/` does not replace the review report.

## Write boundary

- This worker must not modify product code, tests, fixtures, workflows, or configuration.
- It must not implement its own findings.
- Only review reports, handoff files, and PR review comments may be written.
- It must not merge.

## Outputs

Return review mode and target HEAD, inspected files and dependencies, coverage dispositions, findings or explicit no findings, held and unexplored areas, validation evidence, verdict, review report path or complete body, PR comment reference or complete body, and handoff path or complete packet.

## Completion condition

Complete only when the target HEAD is explicit, the selected mode is valid for the current chat, mode-required coverage is finished, findings and risks are recorded, the verdict follows the stop rules, a review report has been created or returned in full, the concise PR comment is posted or rendered when a PR exists, product code remains unchanged, and a transportable handoff is available. This worker must not merge.

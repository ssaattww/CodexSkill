---
name: review-core
description: Perform a code or design review from a structured ReviewRequest and return a format-independent ReviewResult. Use as the reviewer worker in Codex delegation or directly in a standalone chat. Do not create report files, post PR comments, modify product code, or dispatch another agent.
---

# Review Core

Review the requested target and return a structured result without presentation or repository side effects.

## Goal

Convert one valid `ReviewRequest` into one evidence-backed `ReviewResult`.

## Execution owner

Run this skill as: `reviewer worker`

- In the Codex workflow, a delegated reviewer sub-agent runs this skill.
- In direct or ChatGPT chat use, the current agent may run it directly.
- This skill never dispatches another agent.

## Inputs

Before review, require:

- a `ReviewRequest` conforming to [references/review-contract.md](references/review-contract.md)
- the criterion definitions selected by `review-policy`
- direct access to the target diff, files, design, requirements, and available evidence
- the review stage and reviewer context

If required input is unavailable, return `verdict=incomplete` with explicit `unexplored` entries instead of inventing evidence.

## Required flow

1. Read [references/review-contract.md](references/review-contract.md).
2. Validate the request version, stage, planned criteria, risk profile, and selected modules.
3. Read the criterion source supplied by `review-policy`.
4. Inspect the target directly. Do not rely only on a caller-authored summary when source context is available.
5. Apply only the planned universal criteria and selected risk-module criteria.
6. Follow the stage boundary:
   - `initial`: complete all planned criteria even after finding a Blocking or High issue.
   - `fix_verification`: inspect prior findings, the fix, direct impact, and sibling cases of the same mechanism only.
   - `cold_final`: review final HEAD from fresh context using the planned criteria once.
7. Record inspected targets and exact evidence.
8. Return findings first, severity ordered, with stable IDs and origin classification.
9. Fill every planned coverage criterion exactly once.
10. Set verdict, follow-up, stop reason, and merge-candidate only according to `review-policy`.
11. Return the `ReviewResult` to the caller.

## Rules

- Do not choose a report path or filename.
- Do not select or edit a Markdown template.
- Do not write a repository report file.
- Do not post a PR comment or review.
- Do not commit, push, merge, or modify product code.
- Do not infer workflow state from prose; use fixed contract values.
- Do not silently add unrelated criteria during fix verification.
- Do not stop the initial review at the first finding; finish the planned coverage.
- Do not claim `pass` when required evidence is missing.
- Do not convert presentation failure into review failure or alter a completed result.
- Do not broaden scope beyond the request. Record out-of-scope defects with `origin=out_of_scope` and an appropriate follow-up.

## Outputs

Return one `ReviewResult` containing:

- inspected targets
- coverage dispositions
- severity-ordered findings
- held concerns
- unexplored areas
- validation evidence
- verdict
- follow-up
- stop reason
- merge-candidate flag

## Completion condition

This skill is complete only when:

- request validation has completed
- every planned criterion has exactly one coverage disposition
- findings and evidence are traceable
- result invariants are satisfied
- the structured result has been returned without repository or presentation side effects

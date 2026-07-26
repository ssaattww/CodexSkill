---
name: report-output-manager
description: Persist already-rendered report content under a target repository's reports directory using stable placement and filename rules. Use after a renderer or task worker has produced the complete body. This skill is an artifact adapter; it does not inspect code, choose review criteria, decide verdicts, or render ReviewResult content.
---

# Report Output Manager

Write a supplied report body to a predictable repository artifact.

## Goal

Convert rendered text plus artifact metadata into a concrete report path and persisted file without changing the source result.

## Execution owner

Run this skill as: `parent`

- Parent owns repository path selection and write authorization.
- Content semantics remain owned by the caller or renderer.

## Inputs

Require:

- target repository root
- complete rendered body text
- report purpose or item name
- issue, task, PR, or topic prefix
- revision number when this is a follow-up report
- whether an existing artifact should be reused or replaced
- source result identifier, when available

Do not accept an incomplete `ReviewResult` and attempt to render it here. Review content must first pass through `review-result-renderer`.

## Required flow

1. Confirm that the caller supplied complete rendered text.
2. Determine the report path under `<repo-root>/reports/`.
3. Use the filename policy.
4. Preserve the supplied body exactly except for repository-required terminal newline normalization.
5. Create or update only the intended report artifact.
6. Return the concrete path and write result to the caller.

For deterministic naming, use:

- [references/report-filename-policy.md](references/report-filename-policy.md)
- [scripts/build_report_path.sh](scripts/build_report_path.sh)

The generic sub-agent execution template remains available only for callers that explicitly choose artifact-backed delegation:

- [references/sub-agent-report-template.md](references/sub-agent-report-template.md)

## Filename rules

- Base form:
  - `<issue-prefix>-<item-name>-<yyyymmddhhmmss>.md`
- Revision form:
  - `<issue-prefix>-<item-name>-r<revision>-<yyyymmddhhmmss>.md`
- Prefer canonical issue or PR prefixes over freeform labels.
- Do not rename legacy reports unless explicitly requested.

## Responsibility boundary

This skill owns:

- `reports/` placement
- filename selection
- repository file creation or update
- returning the artifact reference

This skill does not own:

- `ReviewRequest` or `ReviewResult`
- review criteria or risk modules
- finding severity, verdict, follow-up, or merge-candidate
- Markdown review layout
- chat or PR-comment wording
- reviewer dispatch
- commit, push, PR comment, or merge decisions

Repository commit and PR posting are handled by the surrounding Git/GitHub workflow after this adapter returns the artifact.

## Rules

- Do not invent or reinterpret technical content.
- Do not derive workflow state from report prose.
- Do not change structured IDs or fixed result values embedded in rendered text.
- Do not ask a reviewer worker to edit this file directly when structured-result delegation is used.
- Do not silently overwrite an unrelated report.
- Write report body text in Japanese unless the renderer or user explicitly selected another language.

## Outputs

Return:

- report path
- filename
- create or update result
- source result identifier
- any artifact-write failure

## Completion condition

This skill is complete only when:

- the intended path and filename are explicit
- the supplied rendered body has been persisted without semantic changes
- artifact failure is reported separately from the source review or implementation result

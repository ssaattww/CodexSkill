---
name: report-output-manager
description: Reserve or persist report artifacts under a target repository's reports directory using stable placement and filename rules. Use when a caller needs a report path/scaffold before artifact-backed work, or when a renderer has produced the complete body. This skill does not inspect code, choose review criteria, decide verdicts, or render ReviewResult content.
---

# Report Output Manager

Manage repository report artifacts without owning their technical meaning.

## Goal

Provide stable report paths and persist caller-supplied content without changing the source result.

## Execution owner

Run this skill as: `parent`

- Parent owns repository path selection and write authorization.
- Content semantics remain owned by the caller or renderer.

## Operations

Select one operation.

### `reserve_artifact`

Use before an artifact-backed sub-agent task.

Inputs:

- target repository root
- report purpose or item name
- issue, task, PR, or topic prefix
- revision number when applicable
- optional caller-supplied scaffold text
- whether an existing artifact should be reused

Behavior:

- choose a concrete path and filename
- optionally create the caller-supplied scaffold
- do not invent headings, review criteria, findings, or workflow state
- return the reserved path

### `persist_rendered`

Use after a renderer or task worker has produced complete report text.

Inputs:

- target repository root
- complete rendered body text
- report purpose or item name
- issue, task, PR, or topic prefix
- revision number when applicable
- source result identifier when available
- whether an existing artifact should be updated

Behavior:

- choose or reuse the intended path
- preserve supplied body content except repository-required terminal newline normalization
- create or update only that artifact
- return the path and write result

Existing callers that do not explicitly select an operation use `reserve_artifact` for backward compatibility. Review rendering must explicitly use `persist_rendered` after `review-result-renderer`.

## Required flow

1. Select the operation, applying the backward-compatible default when needed.
2. Determine the path under `<repo-root>/reports/`.
3. Apply the filename policy.
4. For `reserve_artifact`, persist only caller-supplied scaffold content when supplied.
5. For `persist_rendered`, validate that complete text was supplied and persist it without semantic changes.
6. Return the concrete path and operation result.

For deterministic naming, use:

- [references/report-filename-policy.md](references/report-filename-policy.md)
- [scripts/build_report_path.sh](scripts/build_report_path.sh)

The generic sub-agent execution scaffold remains available to artifact-backed callers:

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
- optional reservation/scaffold creation
- rendered-text persistence
- returning artifact references

This skill does not own:

- `ReviewRequest` or `ReviewResult`
- review criteria or risk modules
- finding severity, verdict, follow-up, or merge-candidate
- Markdown review layout
- chat or PR-comment wording
- reviewer dispatch
- commit, push, PR comment, or merge decisions

Repository commit and PR posting are handled by the surrounding Git/GitHub workflow after this adapter returns.

## Rules

- Do not invent or reinterpret technical content.
- Do not derive workflow state from report prose.
- Do not change structured IDs or fixed result values embedded in rendered text.
- Do not ask a structured-result reviewer to edit an artifact directly.
- Do not silently overwrite an unrelated report.
- Write report body text in Japanese unless the caller or renderer selected another language.

## Outputs

Return:

- operation
- report path
- filename
- create, reserve, or update result
- source result identifier when supplied
- any artifact-write failure

## Completion condition

This skill is complete only when:

- the intended operation, path, and filename are explicit
- caller-supplied content is preserved without semantic changes
- artifact failure is reported separately from the source review or implementation result

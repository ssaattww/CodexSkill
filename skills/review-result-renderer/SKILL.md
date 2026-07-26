---
name: review-result-renderer
description: Render a structured ReviewResult as a Markdown report, chat response, or concise PR comment without changing findings or workflow state. Use after review-core. Do not inspect code, choose review criteria, write repository files, or post to GitHub.
---

# Review Result Renderer

Render review evidence without becoming a reviewer or repository adapter.

## Goal

Convert one valid `ReviewResult` into a requested presentation while preserving every structured decision.

## Execution owner

Run this skill as: `parent or report worker`

- Codex may call it after `review-enforcer` obtains a result.
- A direct chat report worker may call it without sub-agent dispatch.
- This skill has no repository side effects.

## Inputs

Require:

- a `ReviewResult` conforming to `../review-core/references/review-contract.md`
- the desired presentation: `markdown_report | chat_response | concise_pr_comment`
- criterion labels from `../review-policy/references/code-review-criteria.md`
- optional audience and language preference

## Required flow

1. Validate the result contract version and required fields.
2. Read criterion labels from the canonical criterion source.
3. Do not materialize non-selected risk modules.
4. Preserve criterion ID, disposition, evidence, notes, and remaining risk.
5. Preserve finding ID, severity, origin, location, evidence, and required change.
6. Preserve verdict, follow-up, stop reason, and merge-candidate exactly.
7. Render the requested presentation.
8. Return rendered text to the caller.

For Markdown reports, use [references/markdown-report-template.md](references/markdown-report-template.md).

## Presentation rules

### Markdown report

- Include full metadata, selected modules, coverage, findings, held concerns, unexplored areas, evidence, and final result.
- Materialize coverage rows from the structured result and canonical criterion labels.
- Do not duplicate criterion descriptions in the template.

### Chat response

- Lead with verdict and Blocking/High findings.
- Summarize coverage and remaining risk.
- Keep structured IDs when another worker will consume the response.

### Concise PR comment

- State verdict, addressed or remaining Blocking/High findings, follow-up, HEAD SHA, and report reference when supplied by the caller.
- Do not reproduce the full report.
- Do not post the comment; return text only.

## Rules

- Do not inspect source code or re-review the target.
- Do not create, remove, merge, or reclassify findings.
- Do not infer `pass` or `fail` from prose.
- Do not recalculate `merge_candidate`.
- Do not choose criteria or risk modules.
- Do not choose a repository path or filename.
- Do not write a file, commit, push, or post a PR comment.
- If the result is invalid or incomplete, report the contract error without fabricating missing evidence.

## Outputs

Return:

- `presentation_type`
- `rendered_text`
- `source_review_id`
- `contract_version`

## Completion condition

This skill is complete only when:

- rendered text is traceable to one ReviewResult
- structured decision values are unchanged
- criterion detail remains single-sourced in review-policy
- no repository or review side effect occurred

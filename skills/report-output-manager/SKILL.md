---
name: report-output-manager
description: Standardize report file placement, filenames, and report-type templates under the target repository's reports directory. Use when creating a new report file or deciding how to name, place, or initialize evidence, review, intake, or analysis reports.
---

# Report Output Manager

Keep report files predictable across skills and repositories.

## Goal

Create report files in a consistent location with stable, reusable naming and the
correct report-type template.

## Execution owner

Run this skill as: `parent`

- Report path and template selection are part of parent-owned workflow control.
- Parent should decide filenames, select the report type, and create report paths
  before delegating work.

## Inputs

Before running this skill, identify:

- target repository root
- report purpose or item name
- report type, such as implementation, review, verification, intake, or analysis
- issue, task, or topic prefix information
- whether an existing report should be reused

## Run this skill

Run this skill when:

- creating a new file under `reports/`
- deciding a report filename
- selecting the report template for the caller's report type
- trying to keep issue-scoped report prefixes consistent

## Core rules

- Place reports in `<repo-root>/reports/`.
- For new filenames, use:
  - `<issue-prefix>-<item-name>-<yyyymmddhhmmss>.md`
- When the same logical report needs another revision, keep the same prefix and item
  name, then insert `-r<revision>` before the timestamp:
  - `<issue-prefix>-<item-name>-r<revision>-<yyyymmddhhmmss>.md`
- Prefer canonical issue-based prefixes over freeform labels.
- Write report body text in Japanese unless the user explicitly requests another
  language.
- Do not rename legacy reports unless explicitly requested.
- For code review and re-review reports, initialize the report from
  [references/review-report-template.md](references/review-report-template.md).
  Do not use the generic sub-agent template for code review when the dedicated
  review template is available.
- Keep all headings, confirmation rows, and prefilled text in the selected template.
  Reviewers fill the intended blank fields and must not remove confirmation items.

## Read only what you need

- For naming, prefix selection, and examples:
  - [references/report-filename-policy.md](references/report-filename-policy.md)
- For generic Japanese sub-agent execution report structure:
  - [references/sub-agent-report-template.md](references/sub-agent-report-template.md)
- For code review and re-review report structure, including the confirmation item
  list and coverage matrix:
  - [references/review-report-template.md](references/review-report-template.md)

Use the script when you want a deterministic path:

- [scripts/build_report_path.sh](scripts/build_report_path.sh)

Current limitation:

- `build_report_path.sh` generates the base
  `<issue-prefix>-<item-name>-<timestamp>.md` form.
- When you need a revisioned filename with `-r<revision>-`, choose the final path
  manually unless the script has been extended for that case.

## Outputs

When this skill runs, make the chosen report path, filename, and selected template
explicit in chat, command output, or the created file itself.

## Completion condition

This skill is complete only when:

- a concrete report path and filename have been determined and surfaced to the
  caller
- the correct report-type template has been selected
- for review reports, the dedicated template has been copied without removing its
  confirmation item list

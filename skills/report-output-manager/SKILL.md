---
name: report-output-manager
description: Standardize report file placement and filenames under the target repository's reports directory. Use when creating a new report file or deciding how to name and place evidence, review, intake, or analysis reports.
---

# Report Output Manager

Keep report files predictable across skills and repositories.

## Goal

Create report files in a consistent location with stable, reusable naming.

## Execution owner

Run this skill as: `parent`

- Report path selection is part of parent-owned workflow control.
- Parent should decide filenames and create report paths before delegating work.

## Inputs

Before running this skill, identify:

- target repository root
- report purpose or item name
- issue, task, or topic prefix information
- whether an existing report should be reused

## Run this skill

Run this skill when:

- creating a new file under `reports/`
- deciding a report filename
- trying to keep issue-scoped report prefixes consistent

## Core rules

- Place reports in `<repo-root>/reports/`.
- For new filenames, use:
  - `<issue-prefix>-<item-name>-<yyyymmddhhmmss>.md`
- Prefer canonical issue-based prefixes over freeform labels.
- Write report body text in Japanese unless the user explicitly requests another language.
- Do not rename legacy reports unless explicitly requested.

## Read only what you need

- For naming, prefix selection, and examples:
  - [references/report-filename-policy.md](references/report-filename-policy.md)
- For Japanese sub-agent execution report structure:
  - [references/sub-agent-report-template.md](references/sub-agent-report-template.md)

Use the script when you want a deterministic path:

- [scripts/build_report_path.sh](scripts/build_report_path.sh)

## Outputs

When this skill runs, make the chosen report path explicit in chat, command output, or the created file itself.

## Completion condition

This skill is complete only when a concrete report path and filename have been determined and surfaced to the caller.

---
name: report-output-manager
description: Apply the shared report contract and standardize report file placement and filenames under the target repository's reports directory. Use when reserving, rendering, creating, or updating implementation, review, verification, evidence, intake, or analysis reports.
---

# Report Output Manager

## Goal

Apply shared evidence-fidelity rules while keeping report paths, filenames, and persisted output predictable through the Codex runtime.

## Shared contracts

Follow:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Report Contract](../../shared/workflow/report-contract.md)

These files are the canonical report semantics shared with ChatGPT workers. This Skill owns only the Codex path, rendering, and persistence adapter.

## Execution owner

Run this Skill as: `parent`.

- Parent owns report mode, source selection, path reservation, template choice, and final persistence.
- Parent should determine report paths before delegating report section work.
- A delegated writer may populate only the intended sections and must not change source evidence or parent-owned structure.

## Inputs

Before running this Skill, identify:

- target repository root,
- report mode and purpose,
- authoritative source identities,
- Issue, task, PR, branch, and target HEAD,
- whether an existing report should be reused or revised,
- repository-specific language and template rules,
- allowed write path.

## Required flow

1. Select authoritative sources according to the shared Report Contract.
2. Choose or reserve the report path under `<repo-root>/reports/`.
3. Apply the repository-specific filename, language, and template rules.
4. Render evidence without changing meaning, verdict, severity, validation result, or uncertainty.
5. Persist the report or return the complete body when writing is unavailable.
6. Surface the final path and source identities to the caller.
7. Leave PR commenting and handoff transport to the calling runtime unless explicitly delegated.

## Path and filename rules

- Place reports in `<repo-root>/reports/`.
- For new filenames, use `<issue-prefix>-<item-name>-<yyyymmddhhmmss>.md`.
- For a revision, keep the prefix and item name, then insert `-r<revision>` before the timestamp: `<issue-prefix>-<item-name>-r<revision>-<yyyymmddhhmmss>.md`.
- Prefer canonical Issue-based prefixes over freeform labels.
- Write report body text in Japanese unless the user explicitly requests another language.
- Do not rename legacy reports unless explicitly requested.

## References and helper

- [Report filename policy](references/report-filename-policy.md)
- [Sub-agent report template](references/sub-agent-report-template.md)
- [Deterministic path helper](scripts/build_report_path.sh)

Current helper limitation:

- `build_report_path.sh` generates only the base filename form.
- Choose a revisioned path manually unless the helper has been extended.

## Codex adapter rules

- Do not invent evidence to fill a template.
- Do not convert missing current-HEAD CI into success.
- Do not let a concise PR comment replace the detailed report.
- Do not modify code, tests, workflows, or design merely to improve the report.
- Do not merge.

## Outputs

Return:

- report mode,
- authoritative source identities,
- concrete report path,
- created or updated outcome,
- preserved unknowns and remaining risks,
- any persistence limitation.

## Completion condition

This Skill is complete only when the shared Common Work and Report contracts are satisfied for the selected report, a concrete path and complete body are available, evidence meaning and uncertainty are preserved, the caller can identify the authoritative sources, and no merge was performed.

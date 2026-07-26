# Report Contract

## Purpose

This file defines evidence and report semantics shared by Codex report output and ChatGPT report workers.

Use it together with [Common Work Contract](common-work-contract.md). Runtime adapters own source discovery, path selection, persistence, PR commenting, and handoff transport.

## Report modes

### Implementation report

Represent accepted scope, non-goals, requirements, implementation changes, validation, diagnostics, commits, final HEAD, matching CI evidence, artifacts, blocked items, remaining risks, and next action.

Do not invent test-first evidence or a review verdict.

### Review report

Represent review mode, target HEAD, reviewer identity, requirements, changed and dependent files, risk profile, coverage dispositions, findings or explicit no findings, held and unexplored areas, target-HEAD evidence, verdict, and next action.

Do not change finding severity, location, impact, required action, or verdict supplied by the reviewer.

### Verification report

Represent verification target, commands, tests, environment, target HEAD, CI runs, jobs, artifacts, passed and failed states, blocked and unexplored areas, and remaining risks.

Do not report an unsuccessful or unavailable check as successful.

### Consolidated report

Combine compatible source reports without erasing source identity, disagreement, uncertainty, held items, or unexplored areas.

A consolidated report does not create a new technical finding or upgrade the certainty of a source.

### Concise PR comment

Summarize purpose, principal changes or findings, target HEAD, applicable validation and CI evidence, detailed report path, remaining risk, next action, and confirmation that no merge was performed.

A concise PR comment does not replace the detailed report.

## Source selection

Select sources by:

- task or Issue,
- PR,
- producer role,
- report or review mode,
- branch,
- target or reviewed HEAD,
- commit relationship,
- explicit source references.

Do not select a report or handoff merely because it has the newest timestamp.

When repository evidence and a source report disagree, preserve the disagreement and identify the authoritative source instead of silently reconciling it.

## Evidence fidelity

- Do not invent facts, requirements, findings, severity, causes, fixes, validation results, CI conclusions, artifact identities, or merge readiness.
- Do not convert uncertainty into certainty.
- Do not convert `in_progress`, `unknown`, `not_run`, or `not_available` into success.
- Keep artifact identity separate from confirmed or inferred cause.
- Keep target HEAD and CI `head_sha` explicit.
- Preserve held, out-of-scope, unexplored, unknown, and not-applicable items.
- Mark inference as inference and retain the evidence that supports it.
- A report-only runtime copies technical judgments from authoritative sources; it does not create new technical judgments.

## Required structure

Include the sections applicable to the selected mode:

- report metadata and source identities,
- repository, Issue or PR, branch, base ref, and target HEAD,
- accepted scope and non-goals,
- authoritative requirements and design,
- changed or inspected files and dependencies,
- commands, tests, validation, CI, and artifacts,
- implementation outcome or review verdict,
- findings or explicit no findings,
- held, out-of-scope, unexplored, unknown, and not-applicable items,
- remaining risks,
- next action,
- persistence or commenting limitations,
- confirmation that no merge was performed.

Follow repository-specific path, filename, language, and template rules without changing evidence meaning.

## Write boundary

A report-only runtime may write only report files, permitted handoff files, and PR comments.

It must not modify product code, tests, fixtures, workflows, configuration, or design merely to improve the report. It must not perform a new technical review or implement changes.

## Completion condition

A report is complete only when its mode and authoritative sources are explicit, target identity and evidence match those sources, uncertainty and gaps remain visible, the required structure is present, the report is persisted or returned in full, any required concise PR comment is posted or rendered, no new technical judgment was invented, and no merge was performed.

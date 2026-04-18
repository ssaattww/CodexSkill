---
name: feedback-issue-intake-fallback-manager
description: Acquire authoritative issue requirements with fallback paths when GitHub CLI or a primary retrieval path fails. Use before implementation whenever issue scope is unclear or tooling constraints block normal issue intake.
---

# Issue Intake Fallback Manager

Resolve issue requirements without relying on a single tool path.

## Goal

Establish reliable, auditable issue requirements before planning or implementation.

## Execution owner

Run this skill as: `parent`

- Parent owns source selection, confidence judgment, and escalation decisions.
- Requirement extraction and source reconciliation inside this skill remain mandatory sub-agent work.

## Inputs

Before running this skill, gather:

- target issue identifier or URL
- currently available access paths
- any partial requirement context already known

## Run this skill

Run this skill when:

- `gh issue view` is unavailable or failing
- repository auth/scope limits block normal issue reads
- issue text is partially visible and requirements remain ambiguous

## Intake order

Use this fallback order:

1. GitHub app/connector issue fetch
2. `gh issue view` (when available)
3. direct issue URL retrieval
4. existing project reports/discussion artifacts as temporary fallback

If moving to a lower-confidence source, mark confidence explicitly.

Run the actual intake pass as a `sub-agent` task through `sub-agent-task-manager`.

## Outputs

Produce an intake note in `reports/` containing:

- issue identifier and source URL
- which retrieval path succeeded
- extracted requirements (must/should/out-of-scope)
- confidence level and missing information
- blocking questions if unresolved

When creating a new intake report file, call `report-output-manager`.

## Completion condition

This skill is complete only when authoritative or explicitly lower-confidence requirements are captured in a report with confidence and gaps stated.

## Strong rules

- Do not start implementation from inferred requirements when authoritative issue text is missing.
- Distinguish confirmed requirements from assumptions.
- Escalate to user only for truly blocking ambiguity.
- Requirement extraction and source reconciliation are mandatory sub-agent work.

## Cross-cutting rule

If issue-intake failures recur, call `feedback-points-manager`.

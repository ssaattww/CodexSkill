---
name: feedback-coding-standards-enforcer
description: Enforce repository coding standards such as required documentation comments and API-surface hygiene before review and commit. Use when code changes may introduce public/protected APIs or style-contract violations.
---

# Coding Standards Enforcer

Make coding standards executable instead of optional.

## Goal

Prevent review/merge of changes that violate declared coding standards.

## Execution owner

Run this skill as: `parent`

- Parent owns the enforcement decision and any required fixes.
- Standards detection and validation inside this skill remain mandatory sub-agent work.

## Inputs

Before running this skill, gather:

- changed files
- API-surface changes when applicable
- repository-specific standards to enforce
- current validation or analyzer setup if any

## Run this skill

Run this skill:

- before review when API surface changed
- before commit for standards-sensitive repositories
- when repeated style/documentation regressions appear

## Required checks

Check standards relevant to the repository, including:

- public/protected member documentation requirements
- API naming and visibility consistency
- repository-specific style or analyzer requirements

For C# API changes, explicitly verify required XML documentation comments exist for new/changed public/protected members.

## Enforcement flow

1. identify changed files and API-surface diffs
2. detect standards violations as a `sub-agent` task through `sub-agent-task-manager`
3. fix or record each violation
4. run configured validation commands as `sub-agent` verification when they are used as evidence
5. record evidence in `reports/`

## Strong rules

- Do not treat standards checks as optional cleanup.
- Do not defer known violations without explicit rationale.
- If a standard is ambiguous, propose a concrete rule and record it.
- Standards detection and standards validation are mandatory sub-agent work.

## Outputs

After this skill runs, there should be:

- explicit standards-check evidence
- fixed violations or a recorded rationale for any remaining item
- report-backed verification when used as evidence

## Completion condition

This skill is complete only when standards-sensitive changes have been checked and any resulting violations are fixed or explicitly recorded.

## Cross-cutting rule

If repeated standards violations recur, call `feedback-points-manager`.

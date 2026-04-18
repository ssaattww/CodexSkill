---
name: feedback-coding-standards-enforcer
description: Enforce repository coding standards such as required documentation comments and API-surface hygiene before review and commit. Use when code changes may introduce public/protected APIs or style-contract violations.
---

# Coding Standards Enforcer

Make coding standards executable instead of optional.

## Goal

Prevent review/merge of changes that violate declared coding standards.

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
2. detect standards violations
3. fix or record each violation
4. run configured validation commands
5. record evidence in `reports/`

## Strong rules

- Do not treat standards checks as optional cleanup.
- Do not defer known violations without explicit rationale.
- If a standard is ambiguous, propose a concrete rule and record it.

## Cross-cutting rule

If repeated standards violations recur, call `feedback-points-manager`.

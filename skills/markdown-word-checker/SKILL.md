---
name: markdown-word-checker
description: Check Markdown wording and terminology with the target repository's lint configuration after Markdown files, Markdown lint settings, reports, task tracking, design documents, or review-facing text are created or edited.
---

# Markdown Word Checker

Check Markdown wording with the target repository's own lint configuration.

## Goal

Keep Markdown terminology checks in one reusable skill so Markdown-writing and review skills do not carry detailed vocabulary rules.

This skill reads repo-specific configuration under the target repository's `tools/lint/` directory when it exists. It does not define global project terminology in CodexSkill.

## Execution owner

Run this skill as: `parent`

- Parent decides the target repository root, target Markdown files, and whether the current caller needs focused lint, full lint, or both.
- Parent decides whether a lint failure blocks the caller's gate or is an intentionally recorded stricter gate state.
- Parent decides whether repo-specific lint configuration changes need user review before editing.
- Large lint evidence collection may be delegated through `sub-agent-task-manager`; this skill still owns the result classification returned to the caller.

## Inputs

Before running this skill, gather:

- target repository root
- Markdown files created or edited by the current task, if any
- caller and gate context, such as authoring, task completion, review, or handover
- available repo-local lint configuration under `tools/lint/`, especially `tools/lint/README.md`, `tools/lint/markdown-targets.json`, `tools/lint/markdown-whitelist.yaml`, and `tools/lint/prh.yml`
- available package wiring such as `package.json` and `lint:md`
- whether the caller already has a report where lint evidence must be summarized

## Required flow

1. Confirm the target repository root.
2. Read repo-local Markdown lint instructions and settings from `tools/lint/` when present.
3. Decide the target file set.
   - Use explicit Markdown files for focused lint when the caller created or edited Markdown.
   - Consider full lint for task completion and review gates.
4. Choose an available command path.
   - Prefer the repository's `lint:md` script for full lint when it exists.
   - For focused lint, use explicit-file support in the shared scripts when available.
   - In the initial implementation, do not move shared scripts; reference the existing scripts under `skills/review-enforcer/scripts/`.
5. Run or delegate the lint evidence collection.
6. Check whether backticks or quotes are being used to evade prose lint.
   - Code, identifiers, commands, file paths, and real UI labels may remain inline code.
   - Ordinary prose terms must not be wrapped only to avoid the lint gate.
7. Classify findings and execution state.
8. If repo-specific configuration changes are needed, prepare exact entry candidates and stop for user review before editing.
9. Return the command results, classification, user-review needs, and report paths to the caller.

## Outputs

Return these results to the caller:

- target repository root
- target Markdown files
- command path used and exit status
- skipped checks with `skip` reasons
- unsupported checks with `unsupported` reasons
- blocking lint failures with `failed gate` reasons
- lint findings classified as body fixes, lint-setting review, or intentional stricter gate state
- backtick or quote evasion findings
- whether repo-specific lint settings need user review
- exact entry review requirement for whitelist, `prh`, or target exclusions
- sub-agent report path when evidence collection was delegated

## Completion condition

This skill is complete only when:

- the target root and target Markdown file set have been classified
- available repo-local `tools/lint/` configuration has been considered
- focused or full lint has either run or has a recorded `skip`, `unsupported`, or `failed gate` reason
- caller-facing results include command evidence and remaining risks
- repo-specific whitelist, `prh`, or target-exclusion exact entry changes have not been applied without user review

## Rules

- Keep repo-specific terminology data in the target repository; do not add project terms to this skill.
- Do not create or edit repo-specific `tools/lint/` entries unless the user has reviewed the exact entry change.
- `markdown-whitelist.yaml` `term`, `aliases`, and `description` additions, deletions, or rewrites require user review.
- `prh.yml` rule additions, deletions, or rewrites require user review.
- Expanding target exclusions requires user review because it can hide documents from full lint.
- ChikkarPy and SudachiPy candidates are evidence only. Do not automatically convert them into whitelist aliases or `prh` rules.
- When lint evidence collection is delegated, use `sub-agent-task-manager` and `report-output-manager` contracts. The delegated worker must read the pre-created report first, preserve headings and spacing, and fill only command, checked-file, result, and risk placeholders.
- Do not make worker-facing instructions verbose. The normal author-facing rule is only to run Markdown lint, fix valid findings, and report unsuitable lint rules instead of bypassing them.

### Execution state classification

| State | Meaning |
| --- | --- |
| `skip` | No Markdown target exists, or an optional check is not configured. |
| `unsupported` | The repository or target file set cannot satisfy this skill's lint contract, so the result cannot be treated as pass or fail. |
| `failed gate` | A caller-required gate or repository-configured check ran and failed. |

Typical classification:

| Target | Missing or failing case |
| --- | --- |
| Markdown changed files | No targets means `skip`; unresolved root or files means `unsupported`. |
| `package.json` | npm lint path is `unsupported`; if no alternate script path can run a required gate, record `failed gate`. |
| `lint:md` | npm path is `skip`; consider focused shared-script validation. |
| `tools/lint/markdown-targets.json` | full lint is `unsupported`; explicit-file focused lint may continue. |
| `tools/lint/markdown-whitelist.yaml` | whitelist check is `unsupported`; other independent checks may continue. |
| `tools/lint/prh.yml` | `prh` check is `skip` unless repository wiring requires it and command failure makes it `failed gate`. |
| `tools/lint/README.md` | record missing local instructions as a risk, but do not fail a runnable lint gate only for this. |

### New-term routing

Use this table for lint findings and extracted candidates. It is internal to this skill and should not be expanded into worker-facing vocabulary rules.

| Candidate | Route |
| --- | --- |
| typo, redundant English, or context-poor wording | Fix the Markdown body. Prefer a context-bearing compound phrase or Japanese wording when a standalone word is too broad. |
| term that names a new concept and should remain allowed | Candidate `term` in `markdown-whitelist.yaml` with a meaning-bearing `description`. |
| alternate spelling that should remain valid for the same concept | Candidate `aliases` entry. Do not mix different concepts into aliases. |
| spelling that should be corrected to a canonical form | Candidate `prh.yml` rule. Treat it as a correction, not an allowed alias. |
| missing root, target file, package wiring, targets, whitelist, or `prh` settings | Classify as `skip`, `unsupported`, or `failed gate`, not as a vocabulary candidate. |
| uncertain candidate or any repo-specific setting addition, deletion, or rewrite | Send exact entry and rationale to user review before editing. |
| ChikkarPy or SudachiPy output | Use as grouping, frequency, and source evidence only. Do not auto-apply. |

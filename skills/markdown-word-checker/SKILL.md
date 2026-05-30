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
- for Codex hook use, the `PostToolUse` JSON payload from stdin, including `cwd`, `hook_event_name`, `tool_name`, `tool_input`, and `tool_response`

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
9. If exact entry review is required, stop the gate and return the candidates, rationale, target files, and caller report path.
10. Return per-scope command results, aggregate gate state, classification, user-review needs, and report paths to the caller.

### Codex PostToolUse hook helper

The optional hook helper is an early feedback path. It must not replace the authoring skill call to `markdown-word-checker`, the review-enforcer gate, or the caller's report disposition.

Initial hook scope:

- Use `PostToolUse` only.
- Match `apply_patch` and `Edit|Write` style tools.
- Do not introduce `PreToolUse`.
- Treat `Stop` hook coverage as a future hardening option, not as part of the initial contract.

Hook input contract:

- Read hook JSON from stdin.
- Use `cwd` to resolve the target repository root.
- Use `tool_name` to identify supported tools.
- For `apply_patch`, parse `*** Add File:`, `*** Update File:`, and `*** Move to:` as created, updated, or moved-to paths.
- For `apply_patch`, parse `*** Delete File:` as deleted paths and exclude them.
- For `Edit|Write`, extract file path fields from `tool_input`.
- Keep only existing `.md` files inside the target repository.
- Exclude deleted files, missing files, non-Markdown files, and repo-external paths.

Hook output contract:

- Return JSON.
- Put short model-facing feedback in `systemMessage`.
- Put structured check context under `hookSpecificOutput.additionalContext`.
- Return `decision: block` only as feedback to the model when the state is `unsupported`, `failed gate`, or `needs user review`.
- Do not describe `decision: block` as undoing the edit; `PostToolUse` runs after side effects and cannot revert them.

Hook classification:

| Condition | State |
| --- | --- |
| No repo-local Markdown target was edited | `skip` |
| Hook payload or path extraction cannot identify target files | `unsupported` |
| Target repo lacks required focused-lint wiring | `unsupported` |
| Focused lint command exits non-zero | `failed gate` |
| Exact repo-specific whitelist, `prh`, or target-exclusion entries need user approval | `needs user review` |
| Focused lint succeeds | `pass` |

Hook limitations:

- Codex hooks are not Git hooks or editor hooks.
- Some shell, unified exec, and MCP edit paths may not be intercepted.
- Hook success is not a task-completion gate by itself.
- Hook output is immediate model feedback; durable evidence belongs in the caller report or review report.
- The helper uses the target repository's lint configuration. Do not add `package.json`, `tools/lint/`, whitelist, or `prh` data to CodexSkill just to make this helper run locally.

## Outputs

Return these results to the caller:

- target repository root
- target Markdown files
- per-scope check results
  - `focused`: target files, command path used, exit status, state, reason, and remaining risk
  - `full`: target set, command path used, exit status, state, reason, and remaining risk
- aggregate gate state for the caller
- skipped checks with `skip` reasons
- unsupported checks with `unsupported` reasons
- blocking lint failures with `failed gate` reasons
- user-review waits with `needs user review` reasons
- lint findings classified as body fixes, lint-setting review, or intentional stricter gate state
- backtick or quote evasion findings
- whether repo-specific lint settings need user review
- exact entry review requirement for whitelist, `prh`, or target exclusions, including candidates, rationale, target files, and caller report path
- sub-agent report path when evidence collection was delegated
- hook feedback state, target files, command evidence, and remaining interception risk when the Codex PostToolUse helper was used

## Completion condition

This skill is complete only when:

- the target root and target Markdown file set have been classified
- available repo-local `tools/lint/` configuration has been considered
- each caller-requested focused or full lint scope has either run or has a recorded `skip`, `unsupported`, `failed gate`, or `needs user review` reason
- caller-facing results include command evidence and remaining risks
- repo-specific whitelist, `prh`, or target-exclusion exact entry changes have not been applied without user review
- any aggregate gate state is derived from the per-scope results without letting one scope's pass overwrite another scope's blocking state

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
| `needs user review` | Exact repo-specific entries must be reviewed by the user before configuration edits can proceed. |

`unsupported` is not pass. The caller must record a disposition that explains whether the unsupported check blocks the gate, remains on hold, or is acceptable as a documented risk for this caller.

Aggregate gate state is calculated from all caller-requested scopes. `failed gate` has the highest priority, followed by `needs user review`, `unsupported`, `skip`, and pass-equivalent states. When focused lint and full lint are both in scope, a passing result from one scope must not overwrite a `failed gate`, `needs user review`, or `unsupported` result from the other scope.

Typical classification:

| Target | Missing or failing case |
| --- | --- |
| Markdown changed files | No targets means `skip`; unresolved root or files means `unsupported`. |
| `package.json` | npm lint path is `unsupported`; if no alternate script path can run a required gate, record `failed gate`. |
| `lint:md` | npm path is `skip`; consider focused shared-script validation. |
| `tools/lint/markdown-targets.json` | full lint is `unsupported`; explicit-file focused lint may continue. |
| `tools/lint/markdown-whitelist.yaml` | whitelist check is `unsupported`; other independent checks may continue. |
| `tools/lint/prh.yml` | `prh` check is `skip` unless repository wiring requires it and command failure makes it `failed gate`. |
| `cspell.config.jsonc` | cspell check is `skip` when no config exists; when config exists but cspell cannot run, record `unsupported` unless an executed command failure makes it `failed gate`. |
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

When exact entry review is needed, stop the caller gate and return:

- candidate exact entries
- rationale for each candidate
- target files that triggered the candidate
- caller report path to update after approval

After user approval, the caller assigns repo-specific configuration edits to the appropriate implementation owner, reruns the affected focused lint, full lint, or both, and updates the same caller report with the new per-scope results and aggregate gate state. User approval of an exact entry by itself does not close the gate.

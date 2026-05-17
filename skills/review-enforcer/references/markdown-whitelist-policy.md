# Markdown Whitelist Policy

Use this policy when reviewing or changing repository Markdown lint wiring, vocabulary extraction, whitelist entries, or notation rules.

## Goal

Keep the whitelist as a reviewed terminology contract, not as a mechanical escape hatch for lint failures.

The repository owns:

- `tools/lint/markdown-whitelist.yaml`
- `tools/lint/markdown-targets.json`
- `tools/lint/prh.yml` when notation normalization is enabled
- package wiring and local setup notes

The shared skill owns reusable scripts only.

## User Workflow

When rebuilding or extending a whitelist, the user should:

1. Run the repository vocabulary extractor over the intended document scope.
2. Review the frequency-ranked output, including surface form, normalized form, reading, part of speech, group key, count, and source files.
3. Decide the canonical term for each concept.
4. Decide whether alternate spellings are truly allowed aliases or should be corrected by `prh`.
5. Review every proposed whitelist entry's `term`, optional `aliases`, and `description`.
6. Approve whitelist changes explicitly before the task is treated as complete.

The user is not expected to approve bulk-generated whitelist entries blindly. The useful review unit is a small concept group with its meaning.

## Agent Workflow

When the repository uses the standard scripts, the agent should:

1. Use `scripts/extract-markdown-vocabulary-sudachi.py` for `.md` / `.txt` vocabulary inventory when Japanese tokenization matters.
2. Use frequency and sources to prioritize review. High-frequency tokens should be considered first, but frequency alone is not approval.
3. Use `groupKey`, reading, and normalized form to propose candidate groups.
4. Clearly separate candidate extraction from whitelist editing.
5. Present the user with minimal, concept-level whitelist proposals before editing `tools/lint/markdown-whitelist.yaml`.
6. Record intentionally failing strict gates when the task introduces stricter checking before the whitelist has been rebuilt.

Do not add large generated whitelist batches to make lint pass.

## Classification Rules

Use `tools/lint/markdown-whitelist.yaml` for terms that are allowed vocabulary:

- canonical product names
- project-specific concepts
- domain terms that must remain in prose
- alternate forms that are intentionally accepted long term

Use `tools/lint/prh.yml` for notation normalization:

- misspellings
- obsolete names
- forms that should be rewritten to a canonical term
- katakana or English variants that are not intended to remain accepted prose

Do not use whitelist aliases for spellings that should be corrected. Put those in `prh`.

## Entry Shape

Each whitelist entry must have:

- `term`: the allowed term
- `description`: the meaning reviewed by the user

Use `aliases` only for alternate forms that remain intentionally valid.

Prefer concrete compound terms or phrases. Registering a single generic word is a last resort because it broadens accepted vocabulary beyond the reviewed concept.

Descriptions are lint targets. If description text introduces new English, katakana, or Japanese terms, those terms must also be acceptable under the current policy.

## Scope Rules

The extractor may scan existing docs broadly, but whitelist edits should remain small and reviewable.

`--files` narrows Markdown input files. Standard whitelist checking may still inspect whitelist descriptions unless the command is `--stdin` for a normal document body.

Markdown link addresses, URL-like destinations, code fences, inline code, and footnote definition lines are not prose. Visible link text remains prose and should be checked.

## User Approval Rule

Whitelist changes are not complete until the user explicitly reviews the actual entries being added, removed, or changed.

Agent review, successful lint output, or high token frequency cannot replace that user approval.

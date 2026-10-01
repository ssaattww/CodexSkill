# Markdown terminology check

This directory is repository-local tooling installed by the CodexSkill markdown-word-checker bootstrap.

## Setup

Create a local virtual environment and install the pinned dependencies.

Windows:

    py -m venv tools/lint/.venv
    tools\lint\.venv\Scripts\python -m pip install -r tools/lint/requirements.txt

Linux/macOS:

    python3 -m venv tools/lint/.venv
    tools/lint/.venv/bin/python -m pip install -r tools/lint/requirements.txt

## Audit before enforcement

Start with audit mode. Audit reports unknown terms but does not turn those terms alone into a failing process.

    tools/lint/.venv/Scripts/python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope full --output-dir tools/lint/artifacts/audit

Use the corresponding .venv/bin/python path on Linux/macOS.

The result.json state needs_user_review means the terminology baseline is not approved yet. It is not a passing terminology gate.

## Focused check

For explicit files:

    python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope files --files docs/example.md --output-dir tools/lint/artifacts/focused

For changed Markdown:

    python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope changed --output-dir tools/lint/artifacts/changed

## Enforcement

Switch to enforce only after the target set and initial whitelist have been reviewed.

    python tools/lint/scripts/run_markdown_word_check.py --mode enforce --scope full --output-dir tools/lint/artifacts/enforce

Do not bulk-add extracted terms just to make enforcement pass. Changes to whitelist terms, aliases, descriptions, spelling rules, or document exclusions require the repository's user-review process.

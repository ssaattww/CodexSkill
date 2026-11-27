# Markdown terminology check

This directory is repository-local tooling installed by the CodexSkill markdown-word-checker bootstrap. It does not require this repository's root package manager. The same seven installation paths and pass/fail rules apply on Windows and Linux.

## Read-only bootstrap plan

The current bootstrap entry is a read-only planner. It requires Node.js 18 or newer in the development environment; do not assume that consumer repositories have Node.js installed. It requires no root `package.json`, npm package, or network access. It checks the fixed seven-file manifest, optionally the CI file, target Git worktree root, current HEAD, source SHA-256 values, and existing destinations. It ignores sources outside the fixed manifest and refuses missing or non-regular required sources. A successful plan does not authorize a later write. It never writes to the target and never invokes a Python writer.

From a CodexSkill checkout:

    node skills/markdown-word-checker/scripts/plan_markdown_word_check_bootstrap.mjs --target C:\work\consumer-repo
    node skills/markdown-word-checker/scripts/plan_markdown_word_check_bootstrap.mjs --target /work/consumer-repo --with-ci --expected-head 0123456789abcdef0123456789abcdef01234567

The second command's SHA is an example; replace it with the expected full commit SHA. A destination collision or unsafe path returns exit 3 and leaves the consumer tree unchanged. A ready plan returns exit 0 with `writes_enabled: false`; it is not an installation or lint result.

## Installation manifest

The following is the proposed destination manifest only. The current planner creates none of these files.

| Invocation | Files created |
|---|---|
| Default | The seven files under `tools/lint/` listed by the bootstrap manifest |
| Explicit `--with-ci` | Those seven files plus `.github/workflows/markdown-word-check.yml` |

The optional installer candidate is for disposable Git repositories until Windows verification and review are complete. From the CodexSkill checkout, run `node skills/markdown-word-checker/scripts/bootstrap_markdown_word_check.mjs --target /path/to/disposable-worktree --expected-head <full-sha> --install`. Add `--with-ci` only to include the CI workflow. Leaving out `--install` makes the invocation read-only.

An existing `tools/lint/` is refused, never overwritten or migrated. Installation diagnostics are stored separately from the fixed assets under `tools/lint/artifacts/bootstrap/`. If an installation or its diagnostics fail, check the result and retained paths before using the destination; do not assume that retrying is safe.

## Setup

Create the local virtual environment and install the pinned dependencies.

Windows:

    py -m venv tools/lint/.venv
    tools\lint\.venv\Scripts\python -m pip install -r tools/lint/requirements.txt

Linux:

    python3 -m venv tools/lint/.venv
    tools/lint/.venv/bin/python -m pip install -r tools/lint/requirements.txt

## Run checks

Use the local environment on both operating systems. When the future runner supports diagnostics, `--output-dir` must use a new direct child of the existing `tools/lint/artifacts/` area. Do not create a second automatic diagnostics root. Choose a new run ID for every command; the examples use `audit-full-001`, `audit-files-001`, and `audit-changed-001`.

Windows:

    tools\lint\.venv\Scripts\python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope full --output-dir tools/lint/artifacts/audit-full-001
    tools\lint\.venv\Scripts\python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope files --files docs/example.md --output-dir tools/lint/artifacts/audit-files-001
    tools\lint\.venv\Scripts\python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope changed --output-dir tools/lint/artifacts/audit-changed-001

Linux:

    tools/lint/.venv/bin/python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope full --output-dir tools/lint/artifacts/audit-full-001
    tools/lint/.venv/bin/python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope files --files docs/example.md --output-dir tools/lint/artifacts/audit-files-001
    tools/lint/.venv/bin/python tools/lint/scripts/run_markdown_word_check.py --mode audit --scope changed --output-dir tools/lint/artifacts/audit-changed-001

The wrapper validates arguments before creating diagnostics. Once a check starts it stores `stdout.log`, `stderr.log`, and `result.json`. For `files`, the existing checker also evaluates whitelist terms, aliases, and descriptions; the command is focused on the requested files while retaining that configuration check.

## Result examples

| Example | Result | Exit |
|---|---|---:|
| Audit runs, no unknown terms | `pass` | 0 |
| Audit finds an unknown term | `needs_user_review`; candidate is recorded, not accepted | 0 |
| Enforce finds an unknown term | `needs_user_review` | nonzero |
| Missing dependency, invalid config, checker cannot start | `failed` with diagnostics | nonzero |
| `changed` cannot read any required Git change source | `failed`; do not treat it as no changes | nonzero |
| Explicit file is missing, outside the repository, excluded, or unsupported | `failed` with the reason | nonzero |
| Output path outside the dedicated run directory or an existing run ID | Reject without overwriting or creating diagnostics | nonzero |
| Invalid arguments | Reject before creating the diagnostics directory | nonzero |

An audit exit code of 0 with `needs_user_review` means the audit ran successfully; it does not mean the terminology is approved. Do not automatically add extracted candidates to the whitelist, aliases, `prh`, or exclusions. Review exact entries first.

## CI

The optional workflow starts in `audit`. It checks that the checked-out PR HEAD equals the event's expected HEAD before running the checker. Checkout and `setup-python` action logs remain in the GitHub job log; the artifact records those actions' outcomes and does not invent action stdout/stderr files. Available shell diagnostics (HEAD check, repository diagnostic preparation, venv, pip, and checker) are captured, with diagnostic preparation, venv, and pip statuses recorded separately (`success`, `failure`, or `not_run`). Each run writes diagnostics to a fresh `$RUNNER_TEMP` directory and checker output to a run/attempt-specific directory under `tools/lint/artifacts/ci/`. The workflow rejects an existing checker output path immediately before running. It collects only the current wrapper execution’s reported result, with the referenced `stdout.log` and `stderr.log` beside it. An executed shell step must retain its logs (empty files are valid). The job fails if required diagnostics or the artifact are missing. A HEAD mismatch or an execution/diagnostic failure fails the job; unknown terms alone remain a review candidate during initial audit.

Use `enforce` as a blocking gate only after the target set and initial approved whitelist have been reviewed. See the [bootstrap design](../../../../../../design/markdown-word-check-bootstrap-design.md) for the full R01–R06 contract and platform safety rules.

# Markdown terminology check

This directory is repository-local tooling installed by the CodexSkill markdown-word-checker bootstrap. It does not require this repository's root package manager. The same seven installation paths and pass/fail rules apply on Windows and Linux.

## Read-only bootstrap plan

The default bootstrap entry is a read-only planner. It requires Node.js 18 or newer in the development environment; do not assume that consumer repositories have Node.js installed. It requires no root `package.json`, npm package, or network access. It checks the fixed seven-file manifest, optionally the CI file, target Git worktree root, current HEAD, source SHA-256 values, and existing destinations. It ignores sources outside the fixed manifest and refuses missing or non-regular required sources. A successful plan does not authorize a later write. It never writes to the target and never invokes a Python writer.

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

The explicit installer creates a private checkout of the requested HEAD and installs the fixed manifest into that copy only. It does not write to the original consumer repository. Use `--install --confirm-exclusive --expected-head <full-sha>` only after confirming exclusive use of the source checkout and temporary area, and add `--with-ci` for the optional eighth asset. The tool cannot prevent concurrent changes by another process using the same account. If exclusive use is uncertain, omit the installation flags and run only the read-only plan. The temporary parent must resolve outside the source checkout. Linux requires a current-user-owned mode 0700 `XDG_RUNTIME_DIR` on a local tmpfs device distinct from the source; its ancestors must pass the owner and write-permission checks. Windows requires an ordinary user session and `--temp-parent <directory>` on a local fixed NTFS volume. The parent and created area must belong to the user and grant explicit creation rights. The installer also checks ancestor ownership, reparse points, and ACLs and refuses untrusted writers or unverifiable attributes. Windows execution of this version has not been verified. On success, use the checkout path printed as `isolated_workspace=...` for the checker commands below.

An existing `tools/lint/` is refused, never overwritten or migrated. Installation diagnostics are stored separately from the fixed assets under `tools/lint/artifacts/bootstrap/`. On installation failure, no further diagnostics are written and any created isolated area is retained. Inspect the error and retained path before retrying; the tool does not clean it up or apply the assets to the original checkout.

## Setup

Create the local virtual environment and install the pinned dependencies.

Windows:

    py -m venv tools/lint/.venv
    tools\lint\.venv\Scripts\python -m pip install -r tools/lint/requirements.txt

Linux:

    python3 -m venv tools/lint/.venv
    tools/lint/.venv/bin/python -m pip install -r tools/lint/requirements.txt

## Run checks

Use the local environment on both operating systems. The runner accepts a new `--output-dir` only inside `tools/lint/artifacts/`. Choose a new run ID for each command.

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
| Explicit file is missing, outside the repository, excluded, unsupported, or points to the same resolved file as another argument | `failed` with the reason | nonzero |
| Output path outside the dedicated run directory or an existing run ID | Reject without overwriting or creating diagnostics | nonzero |
| Invalid arguments | Reject before creating the diagnostics directory | nonzero |

An audit exit code of 0 with `needs_user_review` means the audit ran successfully; it does not mean the terminology is approved. Do not automatically add extracted candidates to the whitelist, aliases, `prh`, or exclusions. Review exact entries first.

The changed-file check keeps Japanese names and whitespace intact. Target configuration values, when present, must be arrays of strings. A Git read or directory traversal failure is not an empty successful check.

## CI

The optional workflow starts in `audit`. It checks that the checked-out PR HEAD equals the event's expected HEAD before running the checker. Checkout and `setup-python` action logs remain in the GitHub job log; the artifact records those actions' outcomes and does not invent action stdout/stderr files. Available shell diagnostics (HEAD check, repository diagnostic preparation, venv, pip, and checker) are captured, with diagnostic preparation, venv, and pip statuses recorded separately (`success`, `failure`, or `not_run`). Each run writes diagnostics to a fresh `$RUNNER_TEMP` directory and checker output to a run/attempt-specific directory under `tools/lint/artifacts/ci/`. The workflow rejects an existing checker output path immediately before running. It collects only the current wrapper execution’s reported result, with the referenced `stdout.log` and `stderr.log` beside it. An executed shell step must retain its logs (empty files are valid). The job fails if required diagnostics or the artifact are missing. A HEAD mismatch or an execution/diagnostic failure fails the job; unknown terms alone remain a review candidate during initial audit.

Use `enforce` as a blocking gate only after the target set and initial approved whitelist have been reviewed. The [CodexSkill bootstrap design](https://github.com/ssaattww/CodexSkill/blob/issue-87-md-bootstrap/design/markdown-word-check-bootstrap-design.md) contains the full contract and platform safety rules.

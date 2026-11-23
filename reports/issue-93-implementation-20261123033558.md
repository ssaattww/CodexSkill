# Issue #93 implementation report

## Target identity

- Repository: `ssaattww/CodexSkill`
- Issue / PR: [#93](https://github.com/ssaattww/CodexSkill/issues/93) / Draft [#94](https://github.com/ssaattww/CodexSkill/pull/94)
- Branch: `issue-93-cloud-tools-installer` (base `main`)
- Implementation HEAD validated: `34c34e5eaa37614f774348fc592d0e08305b48a1`
- Base HEAD: `8ee6e9f80a0362a4d066c4ea39fd3e87002fc829`
- The implementation SHA above identifies the tested installer source. This report does not self-reference its own later persistence commit.

## Scope and non-goals

Implement the smallest Codex Cloud entry point that accepts a consumer repository root and consumer-owned config, installs only a fixed Linux x64 .NET SDK after checksum verification, and safely reuses a matching existing SDK.

Duck, its cloud settings, product configuration, Node.js, yomiyasu, document dependency commands, dependency updates, Project registration, PR comments, and merge are outside this change. Document dependency setup remains consumer-owned and is not copied into the common installer. CodexSkill's repository policy makes TDD not applicable.

## Changes

- `design/cloud-tools-installer-design.md`: defines the two-argument CLI, minimal JSON schema, consumer/shared responsibility boundary, cache and failure behavior, and focused verification.
- `scripts/install-cloud-tools.sh`: parses `--repo-root` and `--config`; validates Linux x64, config containment, strict schema, exact SDK version, checksum, and external cache root; derives the fixed official URL; verifies SHA-512 before extraction; validates the staged SDK version before atomic placement; reuses only an existing SDK that reports the configured version; preserves invalid existing state and removes only its own staging directory.
- `tasks/tasks-status.md` and `tasks/phases-status.md`: track Issue #93 as T-008 / Phase 12.

The script does not evaluate config as shell, accept arbitrary URLs/commands, invoke npm or pip, or place SDK binaries in the repository. On success it prints the resolved `DOTNET_ROOT`; the caller exports it and prepends it to `PATH`.

## Validation

All focused installation checks ran after code commit `34c34e5eaa37614f774348fc592d0e08305b48a1`, using a disposable Git consumer, disposable cache, synthetic archive bytes, and temporary `curl` / `tar` shims. No published SDK or Duck environment was changed.

- `bash -n scripts/install-cloud-tools.sh`: pass.
- Synthetic archive with matching SHA-512: pass; staged SDK version checked and installed only after validation.
- Syntactically valid but incorrect SHA-512: pass; command failed before extraction and left no SDK root or staging directory.
- Existing exact-version SDK: pass; reused without invoking `curl` or `tar`.
- Unknown config field, unsupported configured platform, and config outside the consumer root: pass; all rejected before cache creation.
- Consumer Git status and tracked-file hashes before/after all installer cases: unchanged.
- Temporary staging cleanup after successful install, bad hash, and reuse: pass.
- `python3 scripts/verify_skill_repository.py`: pass.
- `git show --check --oneline HEAD`: pass.
- UTF-8 without BOM/replacement characters and LF checks for edited source/docs: pass.
- ShellCheck: unavailable in this environment.
- Markdown focused lint: `unsupported`, not pass. The explicit-file target selector failed because current CodexSkill has no `tools/lint/markdown-targets.json`; no `package.json` or local Markdown lint wiring is present. No lint configuration was added.
- Real SDK download/extraction and actual Codex Cloud environment propagation: not run. Verification used synthetic archive bytes only.
- CI: no current-HEAD run evidence collected or awaited.

## Environment handoff example

```bash
export CODEX_CLOUD_TOOLS_HOME=/workspace/.duck-env
/workspace/CodexSkill/scripts/install-cloud-tools.sh \
  --repo-root /workspace/Duck \
  --config tools/cloud/toolchain.json
export DOTNET_ROOT="$CODEX_CLOUD_TOOLS_HOME/dotnet"
export PATH="$DOTNET_ROOT:$PATH"
```

The Duck config path above is a future consumer-owned path example; this task did not create or modify it.

## Remaining risks and next action

- The real .NET archive was not downloaded in order to avoid touching the published/shared environment. The pinned consumer config and official checksum must be supplied by Duck when it adopts the entry point.
- Markdown lint is unsupported until CodexSkill's own lint wiring exists; this report records that state explicitly.
- Independent Sol 6.2 High review was not dispatched. The repository's `sub-agent-task-manager` requires a pre-dispatch role/default-role plan and says to stop when the profile effect cannot be inspected. `/workspace/.codex` and `/workspace/.agents` contained no role configuration, and the available `collaboration.spawn_agent` interface has no `agent_type` field. No reviewer ran, and no requested/applied profile is claimed. PR #94 remains Draft. The user/parent owns review comments and merge.

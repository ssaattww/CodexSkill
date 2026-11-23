# Codex Cloud shared tool installer design

## Goal and boundary

Codex Cloud's Install script should call one pinned CodexSkill installer directly, passing the selected consumer repository root and a consumer-owned configuration file. The shared installer owns only common SDK installation mechanics. Product repositories own tool versions, archive checksums, platform selection, build targets, inspection settings, and dependency lockfiles.

The first implementation supports the existing Duck Linux x64 .NET SDK pin. It does not install Node.js, yomiyasu, or document-tool dependencies. Duck's existing npm and Python lockfiles and repository commands remain their owner's concern; this installer must not duplicate or reinterpret them. The Codex Cloud Start skill is not installed by this path.

## Entry point and inputs

Use `scripts/install-cloud-tools.sh` with only `--repo-root` and `--config`. A relative config path is resolved beneath the supplied repository root. An absolute config path is accepted only when its canonical path remains beneath that root. Require `CODEX_CLOUD_TOOLS_HOME` as the external cache root so SDK files do not enter the repository.

The initial JSON schema is intentionally narrow:

```json
{
  "schema_version": 1,
  "platform": "linux-x64",
  "dotnet_sdk": {
    "version": "10.0.401",
    "sha512": "<128 hexadecimal characters>"
  }
}
```

Reject unknown keys, unsupported schema/platform values, malformed exact versions, malformed hashes, non-Linux/non-x64 execution, and config paths outside the repository before changing the cache. Do not read configuration as shell code or accept arbitrary URLs or commands. Derive the archive URL from the exact version using the fixed official `builds.dotnet.microsoft.com` endpoint.

## Install and reuse behavior

Canonicalize `CODEX_CLOUD_TOOLS_HOME` once while parsing the consumer config, reject control characters in that canonical path, validate that it is outside the repository, and use that same value for all later filesystem operations. Resolve the SDK root as `<canonical-cache-root>/dotnet`. If its `dotnet` executable and requested `sdk/<version>` directory exist, run `dotnet --version` with that root and reuse it only when the reported version matches. A mismatched or incomplete existing root is preserved and causes a clear failure.

For a missing SDK root, create a unique staging directory under the external cache, download the version-specific official archive there, verify SHA-512 before extraction, extract into staging, and verify the staged `dotnet --version`. Publish the staged root with a same-filesystem `mv --no-target-directory --no-clobber`; this prevents nesting under and replacing an existing destination. GNU `mv --no-clobber` may return success when it skips a move, so check that the staging source disappeared; if it remains, report a concurrent/existing destination and exit nonzero. In a race, one invocation publishes and the other fails while preserving the winner's SDK. A trap removes only this invocation's staging directory. Never overwrite or delete an existing cache root. Fail fast with a nonzero status and a phase-specific, secret-free diagnostic.

The caller owns environment propagation and must stop on installer failure. In the Cloud Install script, use `set -euo pipefail`, set `CODEX_CLOUD_TOOLS_HOME`, call the installer, then export `DOTNET_ROOT="$CODEX_CLOUD_TOOLS_HOME/dotnet"` and prepend it to `PATH`. Later shell sessions must source their product-owned environment setup or repeat those exports.

## Focused verification

Use disposable fixture repositories and cache directories. Verify shell syntax; reject unknown config fields, invalid platform, out-of-root config, and invalid canonical cache paths; prove a bad digest leaves no SDK root; prove a valid preinstalled exact-version SDK is reused without invoking download or extraction; run two synchronized installers against one absent SDK root and confirm exactly one succeeds while the winner's cache remains unchanged; confirm failure propagation in the caller example; and confirm `git status` and tracked-file hashes in the fixture are unchanged. Use synthetic archives and command shims only; do not replace or mutate a published SDK installation. Separately inspect the edited Markdown for LF, valid Japanese text, and the repository's configured document checks.

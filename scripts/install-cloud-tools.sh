#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: install-cloud-tools.sh --repo-root PATH --config PATH

Install the fixed .NET SDK described by a consumer-owned JSON config.
Set CODEX_CLOUD_TOOLS_HOME to an absolute directory outside the repository.
USAGE
}

fail() {
  printf 'install-cloud-tools: %s\n' "$1" >&2
  exit 1
}

repo_root_arg=''
config_arg=''
while (($#)); do
  case "$1" in
    --repo-root)
      (($# >= 2)) || { usage >&2; exit 2; }
      [[ -z "$repo_root_arg" ]] || { usage >&2; exit 2; }
      repo_root_arg="$2"
      shift 2
      ;;
    --config)
      (($# >= 2)) || { usage >&2; exit 2; }
      [[ -z "$config_arg" ]] || { usage >&2; exit 2; }
      config_arg="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n "$repo_root_arg" && -n "$config_arg" ]] || { usage >&2; exit 2; }
[[ -d "$repo_root_arg" ]] || fail 'repository root must be an existing directory'
repo_root="$(cd -- "$repo_root_arg" && pwd -P)"

[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail 'only Linux x64 is supported'
[[ -n "${CODEX_CLOUD_TOOLS_HOME:-}" ]] || fail 'CODEX_CLOUD_TOOLS_HOME must name an external cache directory'
[[ "$CODEX_CLOUD_TOOLS_HOME" == /* ]] || fail 'CODEX_CLOUD_TOOLS_HOME must be an absolute path'
[[ "$CODEX_CLOUD_TOOLS_HOME" != *$'\n'* ]] || fail 'cache path must not contain a newline'

config_path="$config_arg"
if [[ "$config_path" != /* ]]; then
  config_path="$repo_root/$config_path"
fi

config_values="$(python3 - "$repo_root" "$config_path" "$CODEX_CLOUD_TOOLS_HOME" <<'PY'
import json
import re
import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve(strict=True)
config_path = Path(sys.argv[2]).resolve(strict=True)
cache_root = Path(sys.argv[3]).resolve(strict=False)

try:
    config_path.relative_to(repo_root)
except ValueError:
    raise SystemExit("install-cloud-tools: config path must remain inside the repository root")

try:
    cache_root.relative_to(repo_root)
except ValueError:
    pass
else:
    raise SystemExit("install-cloud-tools: cache directory must remain outside the repository root")
if any(ord(character) < 32 or ord(character) == 127 for character in str(cache_root)):
    raise SystemExit("install-cloud-tools: normalized cache path contains a control character")

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result

try:
    with config_path.open("r", encoding="utf-8") as source:
        config = json.load(source, object_pairs_hook=unique_object)
except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
    raise SystemExit("install-cloud-tools: config must be valid UTF-8 JSON without duplicate keys")

if not isinstance(config, dict) or set(config) != {"schema_version", "platform", "dotnet_sdk"}:
    raise SystemExit("install-cloud-tools: config contains missing or unsupported fields")
if type(config["schema_version"]) is not int or config["schema_version"] != 1:
    raise SystemExit("install-cloud-tools: unsupported config schema version")
if config["platform"] != "linux-x64":
    raise SystemExit("install-cloud-tools: unsupported configured platform")

sdk = config["dotnet_sdk"]
if not isinstance(sdk, dict) or set(sdk) != {"version", "sha512"}:
    raise SystemExit("install-cloud-tools: dotnet_sdk contains missing or unsupported fields")
version = sdk["version"]
digest = sdk["sha512"]
if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
    raise SystemExit("install-cloud-tools: dotnet SDK version must be an exact stable version")
if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{128}", digest):
    raise SystemExit("install-cloud-tools: dotnet SDK SHA-512 must contain 128 hexadecimal characters")

print(version)
print(digest.lower())
print(cache_root)
PY
)" || exit $?
mapfile -t config_lines <<<"$config_values"
[[ "${#config_lines[@]}" == 3 ]] || fail 'config parser returned invalid data'
sdk_version="${config_lines[0]}"
sdk_sha512="${config_lines[1]}"
cache_root="${config_lines[2]}"
mkdir -p -- "$cache_root" || fail 'could not create cache directory'
sdk_root="$cache_root/dotnet"

stage_dir=''
cleanup() {
  if [[ -n "$stage_dir" && -d "$stage_dir" ]]; then
    rm -rf -- "$stage_dir"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

verify_sdk_version() {
  local candidate_root="$1" reported_version
  mkdir -p -- "$stage_dir/dotnet-cli-home"
  if ! reported_version="$(cd / && DOTNET_ROOT="$candidate_root" \
    DOTNET_CLI_HOME="$stage_dir/dotnet-cli-home" \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    "$candidate_root/dotnet" --version 2>/dev/null)"; then
    return 1
  fi
  [[ "$reported_version" == "$sdk_version" ]]
}

if [[ -e "$sdk_root" || -L "$sdk_root" ]]; then
  [[ ! -L "$sdk_root" && -x "$sdk_root/dotnet" && -d "$sdk_root/sdk/$sdk_version" ]] \
    || fail 'existing SDK root is incomplete; preserved it without changes'
  stage_dir="$(mktemp -d -- "$cache_root/.cloud-tools.XXXXXX")" \
    || fail 'could not create SDK verification staging directory'
  verify_sdk_version "$sdk_root" \
    || fail 'existing SDK did not report the configured version; preserved it without changes'
  printf 'install-cloud-tools: reused .NET SDK %s\n' "$sdk_version"
  printf 'DOTNET_ROOT=%s\n' "$sdk_root"
  exit 0
fi

stage_dir="$(mktemp -d -- "$cache_root/.cloud-tools.XXXXXX")" \
  || fail 'could not create SDK staging directory'
archive_path="$stage_dir/dotnet-sdk.tar.gz"
staged_sdk_root="$stage_dir/dotnet"
archive_url="https://builds.dotnet.microsoft.com/dotnet/Sdk/$sdk_version/dotnet-sdk-$sdk_version-linux-x64.tar.gz"

if ! curl --fail --silent --show-error --location --retry 2 "$archive_url" -o "$archive_path"; then
  fail 'official .NET SDK download failed'
fi
if ! printf '%s  %s\n' "$sdk_sha512" "$archive_path" | sha512sum --check --status -; then
  fail 'official .NET SDK archive SHA-512 did not match; nothing was installed'
fi

mkdir -- "$staged_sdk_root"
if ! tar -xzf "$archive_path" -C "$staged_sdk_root"; then
  fail 'verified .NET SDK archive could not be extracted; nothing was installed'
fi
[[ -x "$staged_sdk_root/dotnet" && -d "$staged_sdk_root/sdk/$sdk_version" ]] \
  || fail 'verified archive did not contain the configured SDK; nothing was installed'
verify_sdk_version "$staged_sdk_root" \
  || fail 'staged SDK did not report the configured version; nothing was installed'

if [[ -e "$sdk_root" || -L "$sdk_root" ]]; then
  fail 'SDK root appeared during installation; preserved it without changes'
fi
if ! mv --no-target-directory --no-clobber "$staged_sdk_root" "$sdk_root"; then
  fail 'verified SDK could not be moved into the cache; existing state was preserved'
fi
if [[ -e "$staged_sdk_root" || -L "$staged_sdk_root" ]]; then
  fail 'SDK root already exists; concurrent installation was not overwritten'
fi

printf 'install-cloud-tools: installed .NET SDK %s\n' "$sdk_version"
printf 'DOTNET_ROOT=%s\n' "$sdk_root"

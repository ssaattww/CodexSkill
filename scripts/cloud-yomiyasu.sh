#!/usr/bin/env bash
set -euo pipefail

revision=0df47749139dfd64ad3d55e7d53d3839e5874848
base_url="https://raw.githubusercontent.com/nanaism/yomiyasu/$revision"
files=(scripts/yomiyasu_lint.py scripts/markdown_visibility.py LICENSE UNICODE-LICENSE.txt)
digests=(
  998ceb5b7f46a78b8d11cb4ef229f639b3b095e830f16cec80ea3a89c4755ec4
  e0cc01d3263d65f4c1ccddb939972b4098fdd1453fc0de8fc7e8e25522ec5c8d
  79d802f15bc8caf67f1a83c1bdbe214ccb41a0a0275f9046b329b89c65ee1fca
  e7a93b009565cfce55919a381437ac4db883e9da2126fa28b91d12732bc53d96
)

usage() {
  printf '%s\n' 'Usage: cloud-yomiyasu.sh install --cache-root PATH' \
    '       cloud-yomiyasu.sh run --cache-root PATH DOCUMENT [--strict]' >&2
  exit 2
}

failure_code=2
fail() {
  printf 'cloud-yomiyasu: %s; no existing cache replaced\n' "$1" >&2
  exit "$failure_code"
}

(( $# >= 3 )) || usage
action="$1"
[[ "$2" == --cache-root ]] || usage
cache_arg="$3"
shift 3
case "$action" in
  install) failure_code=1; (( $# == 0 )) || usage ;;
  run)
    (( $# == 1 || $# == 2 )) || usage
    document="$1"
    strict=()
    if (( $# == 2 )); then
      [[ "$2" == --strict ]] || usage
      strict=(--strict)
    fi
    ;;
  *) usage ;;
esac

[[ "$cache_arg" == /* ]] || fail 'cache root must be absolute'
IFS= read -r -d '' cache_root < <(realpath -mz -- "$cache_arg") || fail 'could not resolve cache root'
[[ "$cache_root" != *[[:cntrl:]]* ]] || fail 'cache root must not contain control characters'
parent="$cache_root/yomiyasu"
version_root="$parent/$revision"
temporary=''
cleanup() {
  if [[ -n "$temporary" ]]; then
    rm -rf -- "$temporary"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

real_directory() {
  [[ -d "$1" && ! -L "$1" ]] || fail "expected a real directory: $1"
}

verify_layout() (
  local root="$1" name
  local -a entries
  real_directory "$root"
  real_directory "$root/scripts"
  shopt -s nullglob dotglob
  entries=("$root"/*)
  (( ${#entries[@]} == 3 )) || fail "unexpected or missing cache entries: $root"
  entries=("$root/scripts"/*)
  (( ${#entries[@]} == 2 )) || fail "unexpected or missing script entries: $root/scripts"
  for name in "${files[@]}"; do
    [[ -f "$root/$name" && ! -L "$root/$name" ]] || fail "not a regular file: $root/$name"
  done
)

verify_distribution() {
  local root="$1" index actual
  verify_layout "$root"
  for index in "${!files[@]}"; do
    actual="$(cd -- "$root" && sha256sum -- "${files[index]}")" \
      || fail "could not hash: $root/${files[index]}"
    [[ "${actual%% *}" == "${digests[index]}" ]] || fail "SHA-256 mismatch: $root/${files[index]}"
  done
}

if [[ "$action" == install ]]; then
  mkdir -p -- "$parent" || fail 'could not create Yomiyasu cache directory'
  real_directory "$parent"
  if [[ -e "$version_root" || -L "$version_root" ]]; then
    verify_distribution "$version_root"
    printf 'cloud-yomiyasu: reused %s\n' "$revision"
    exit 0
  fi

  temporary="$(mktemp -d -- "$parent/.yomiyasu.XXXXXX")" || fail 'could not create staging directory'
  stage="$temporary/$revision"
  mkdir -p -- "$stage/scripts" || fail 'could not create staged scripts directory'
  for name in "${files[@]}"; do
    curl --fail --silent --show-error --location --retry 2 --max-time 60 \
      "$base_url/$name" -o "$stage/$name" || fail "official download failed: $name"
  done
  verify_distribution "$stage"
  mv --no-target-directory --no-clobber -- "$stage" "$version_root" \
    || fail 'could not publish verified cache'
  [[ ! -e "$stage" && ! -L "$stage" ]] || fail 'cache appeared during installation'
  printf 'cloud-yomiyasu: installed %s\n' "$revision"
else
  real_directory "$parent"
  verify_layout "$version_root"
  temporary="$(mktemp -d -- "${TMPDIR:-/tmp}/cloud-yomiyasu-run.XXXXXX")" \
    || fail 'could not create execution staging directory'
  mkdir -- "$temporary/scripts" || fail 'could not create execution scripts directory'
  for name in "${files[@]}"; do
    cp -- "$version_root/$name" "$temporary/$name" || fail "could not copy cached file: $name"
  done
  # Check the exact bytes that will be executed; never execute mutable cache
  # files directly or reuse unverified Python bytecode. No download on run.
  verify_distribution "$temporary"
  status=0
  python3 -I -S -B "$temporary/scripts/yomiyasu_lint.py" "$document" --json "${strict[@]}" \
    || status=$?
  case "$status" in
    0|1|2) exit "$status" ;;
    *) fail "upstream execution failed (exit $status)" ;;
  esac
fi

#!/usr/bin/env bash
set -euo pipefail

repo_root="."
reports_dir=""
issue_number=""
task_id=""
topic=""
item_name=""
timestamp=""
create_file="0"

usage() {
  cat <<'EOF'
Usage:
  build_report_path.sh --item-name <name> [--repo-root <path>] [--create-file]
                       (--issue-number <n> | --task-id <id> | --topic <key>)

Examples:
  build_report_path.sh --repo-root /repo --issue-number 128 --item-name review-summary
  build_report_path.sh --task-id phase-2 --item-name intake-note
  build_report_path.sh --topic feedback-points --item-name analysis
EOF
}

normalize() {
  local value="$1"
  value="$(printf '%s' "$value" | tr '[:upper:]' '[:lower:]')"
  value="$(printf '%s' "$value" | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g')"
  printf '%s' "$value"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      repo_root="$2"
      shift 2
      ;;
    --reports-dir)
      reports_dir="$2"
      shift 2
      ;;
    --issue-number)
      issue_number="$2"
      shift 2
      ;;
    --task-id)
      task_id="$2"
      shift 2
      ;;
    --topic)
      topic="$2"
      shift 2
      ;;
    --item-name)
      item_name="$2"
      shift 2
      ;;
    --timestamp)
      timestamp="$2"
      shift 2
      ;;
    --create-file)
      create_file="1"
      shift 1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

source_count=0
[[ -n "$issue_number" ]] && source_count=$((source_count + 1))
[[ -n "$task_id" ]] && source_count=$((source_count + 1))
[[ -n "$topic" ]] && source_count=$((source_count + 1))

if [[ "$source_count" -ne 1 ]]; then
  printf 'Specify exactly one prefix source: --issue-number, --task-id, or --topic\n' >&2
  exit 1
fi

if [[ -z "$item_name" ]]; then
  printf '--item-name is required\n' >&2
  exit 1
fi

if [[ -z "$reports_dir" ]]; then
  reports_dir="${repo_root%/}/reports"
fi

if [[ -n "$issue_number" ]]; then
  prefix="issue-$(normalize "$issue_number")"
elif [[ -n "$task_id" ]]; then
  prefix="task-$(normalize "$task_id")"
else
  prefix="topic-$(normalize "$topic")"
fi

item_slug="$(normalize "$item_name")"

if [[ -z "$prefix" || -z "$item_slug" ]]; then
  printf 'Normalized prefix or item name is empty\n' >&2
  exit 1
fi

if [[ -z "$timestamp" ]]; then
  timestamp="$(date '+%Y%m%d%H%M%S')"
fi

if ! [[ "$timestamp" =~ ^[0-9]{14}$ ]]; then
  printf 'Timestamp must match yyyymmddhhmmss\n' >&2
  exit 1
fi

mkdir -p "$reports_dir"

path="${reports_dir%/}/${prefix}-${item_slug}-${timestamp}.md"

if [[ -e "$path" ]]; then
  printf 'Report path already exists: %s\n' "$path" >&2
  exit 1
fi

if [[ "$create_file" == "1" ]]; then
  : > "$path"
fi

printf '%s\n' "$path"

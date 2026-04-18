#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  build_skillization_issue.sh \
    --group <duplicate-group> \
    --fps <comma-separated-fp-ids> \
    --summary <problem-summary> \
    --proposal <new-skill-or-update> \
    [--title <issue-title>] \
    [--create] \
    [--repo <owner/repo>] \
    [--occurrences <n>] \
    [--cost <impact>] \
    [--mapping <skill-name-or-none>]

By default, prints Markdown issue body to stdout.
If --create is specified, creates a GitHub issue via gh CLI.
EOF
}

group=""
fps=""
summary=""
proposal=""
title=""
create_issue="false"
repo=""
occurrences=""
cost=""
mapping=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --group)
      group="${2:-}"
      shift 2
      ;;
    --fps)
      fps="${2:-}"
      shift 2
      ;;
    --summary)
      summary="${2:-}"
      shift 2
      ;;
    --proposal)
      proposal="${2:-}"
      shift 2
      ;;
    --title)
      title="${2:-}"
      shift 2
      ;;
    --create)
      create_issue="true"
      shift 1
      ;;
    --repo)
      repo="${2:-}"
      shift 2
      ;;
    --occurrences)
      occurrences="${2:-}"
      shift 2
      ;;
    --cost)
      cost="${2:-}"
      shift 2
      ;;
    --mapping)
      mapping="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$group" || -z "$fps" || -z "$summary" || -z "$proposal" ]]; then
  echo "Missing required arguments." >&2
  usage >&2
  exit 1
fi

repo_value="${repo:-<owner/repo>}"
occurrences_value="${occurrences:-<number>}"
cost_value="${cost:-<quality/risk/time impact>}"
mapping_value="${mapping:-<skill-name or none>}"

generate_body() {
cat <<EOF
## Summary

- Duplicate Group: \`$group\`
- Problem: $summary
- Proposed Action: $proposal

## Source Feedback Points

- Repository: $repo_value
- FP IDs: $fps

## Recurrence and Cost

- Occurrences: $occurrences_value
- Cost of not skillizing: $cost_value

## Proposed Acceptance Criteria

1. Define deterministic workflow steps for this reusable problem.
2. Add or update the mapped skill with explicit trigger and completion conditions.
3. Update feedback-point mapping so future recurrences route to the skill.

## Candidate Skill Mapping

- Existing skill to extend: $mapping_value

EOF
}

if [[ "$create_issue" == "true" ]]; then
  if [[ -z "$repo" || -z "$title" ]]; then
    echo "--create requires both --repo and --title." >&2
    exit 1
  fi
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI not found. Cannot create issue." >&2
    exit 1
  fi
  tmp_file="$(mktemp)"
  trap 'rm -f "$tmp_file"' EXIT
  generate_body > "$tmp_file"
  gh issue create --repo "$repo" --title "$title" --body-file "$tmp_file"
else
  generate_body
fi

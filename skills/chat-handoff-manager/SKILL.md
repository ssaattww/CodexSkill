---
name: chat-handoff-manager
description: Create and validate transportable handoff packets between independent ChatGPT worker chats without serving as implementation, review, or report logic.
---

# Chat Handoff Manager

## Goal

Create a complete handoff packet that lets another user-started ChatGPT chat continue without relying on conversation memory.

## Runtime boundary

This Skill is ChatGPT-specific transport logic. It does not implement, review, write the detailed report, start another chat, or merge.

## Required input

Accept the resolved work context and the output of `implementation-worker`, `review-worker`, or `report-writer`.

## Required packet

```yaml
schema_version: 2
producer:
  skill: string
  mode: string
  generated_at: ISO-8601
repository: owner/name
issue_or_pr: string | null
task_id: string | null
branch: string
base_ref: string | null
head_sha: full_sha | unknown
authorized_actions:
  - string
write_boundary:
  allowed:
    - string
  forbidden:
    - string
scope:
  - string
non_goals:
  - string
files:
  changed:
    - path: string
      purpose: string
  inspected:
    - path: string
      purpose: string
commands:
  - command: string
    result: passed | failed | blocked | not_run
    evidence: string | null
ci:
  run_id: integer | null
  head_sha: full_sha | unknown
  conclusion: success | failure | cancelled | skipped | in_progress | unknown | not_applicable
implementation:
  outcome: completed | partial | blocked | not_applicable
review:
  mode: initial_review | fix_verification | independent_final_review | not_applicable
  verdict: pass | pass_with_held | fail | incomplete | unstable | not_applicable
report:
  paths:
    - string
findings:
  - id: string
    severity: blocking | high | medium | low
    description: string
    required_action: string
unknown:
  - string
remaining_risks:
  - string
next_action:
  target_skill: string | none
  mode: string | null
  instructions:
    - string
  requested_authorized_actions:
    - string
transport:
  method: repository_file | copy_paste
  packet_path: string | null
  packet_url: string | null
```

## Rules

- Unknown facts remain unknown; do not guess.
- CI evidence must belong to the packet's HEAD.
- Current permissions do not automatically transfer to the next chat.
- Requested next-chat permissions are proposals requiring a new user grant.
- The handoff does not replace the detailed report.
- When repository persistence is unavailable, return the complete packet for copy and paste.
- Readers may normalize schema version 1 `cold_final_review` to `independent_final_review`; unsupported future schemas remain blocked.

## Completion condition

Complete when the packet is sufficient to continue independently, target identity and uncertainty are explicit, transport is specified, and no implementation, review verdict change, or merge was performed.

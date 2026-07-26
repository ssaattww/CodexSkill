# Chat Worker Handoff Contract

## Purpose

This contract defines the payload exchanged between independent ChatGPT chats when the user acts as the parent and starts each worker chat manually.

A handoff packet is data, not an automatic cross-chat memory mechanism. The packet is not automatically visible to another chat merely because the producing chat printed it. The user must transport it by one of the supported methods below.

## Transport model

### Repository-backed transport

The repository-backed transport is the canonical durable method when repository writes are authorized.

- Store the complete packet under `reports/handoffs/`.
- Use a stable name such as `<task-id>-<producer>-<mode>-<head-short>-<timestamp>.md`.
- Put the canonical YAML packet in a fenced block inside the Markdown file.
- Record the created path in `handoff_transport.packet_path`.
- The user passes the repository path or GitHub URL to the next chat.
- The next chat reads that exact file through the repository connector and must not guess from conversation history.

A handoff file is structured execution evidence, not a narrative implementation or review report. An implementation worker may therefore write a handoff file without taking ownership of report writing.

### Copy and paste transport

When `write_handoff` is not authorized, return the complete packet in the final response. The user must copy and paste the packet into the next chat. A summary alone is insufficient.

### Unsupported assumption

Workers must never assume that another chat can discover the previous chat, its final response, or its private conversation state automatically.

## Core rules

- The user is the parent and decides the next worker, scope, permissions, and merge action.
- Workers must not start another worker.
- A packet must be sufficient to continue without the previous conversation.
- Unknown facts must be listed under `unknown`; they must not be guessed.
- Non-applicable fields must be listed under `not_applicable` with reasons.
- CI evidence must belong to the packet's `head_sha`.
- A report writer must not alter implementation outcomes, findings, test results, or CI conclusions.
- Current permissions must not inherit into the next chat. Requested permissions are proposals only.
- Testing order and development method come from the target project's instructions. Workers must not impose TDD when the target project does not require it.
- Do not embed secrets, credentials, personal information, or unnecessary large logs.

## Canonical packet

```yaml
schema_version: 1
producer:
  skill: chat-implementation-worker | chat-review-worker | chat-report-writer
  mode: string
  generated_at: ISO-8601

task_id: string
issue_or_pr: string | null
repository: owner/name
branch: string
base_ref: string | null
head_sha: full commit SHA | unknown

authorized_actions:
  - read_repository | edit_code | edit_tests | write_handoff | write_report | commit | push | update_pr | comment_pr
write_boundary:
  allowed:
    - path_or_operation: string
      reason: string
  forbidden:
    - path_or_operation: string
      reason: string

handoff_transport:
  method: repository_file | copy_paste
  packet_path: string | null
  packet_url: string | null
  transport_note: string

scope:
  - string
non_goals:
  - string
authoritative_requirements:
  - source: issue | design | user_instruction | repository_instruction
    reference: string
    summary: string

files:
  changed:
    - path: string
      purpose: string
  inspected:
    - path: string
      purpose: string
  intentionally_untouched:
    - path_or_area: string
      reason: string

commands:
  - command: string
    purpose: string
    exit_code: integer | unknown
    result: passed | failed | blocked | not_run
    evidence: string | null

tests:
  - name: string
    phase: red | green | pre_implementation | post_implementation | regression | verification | not_applicable
    result: passed | failed | blocked | not_run
    head_sha: full commit SHA | unknown
    evidence: string | null

ci:
  required: true | false
  workflow: string | null
  run_id: integer | null
  head_sha: full commit SHA | unknown
  conclusion: success | failure | cancelled | skipped | in_progress | unknown | not_applicable
  jobs:
    - name: string
      conclusion: string
  artifacts:
    - id: integer
      name: string
      purpose: string

implementation:
  outcome: completed | partial | blocked | not_applicable
  commits:
    - sha: full commit SHA
      purpose: string
  summary:
    - string

review:
  review_mode: initial_review | fix_verification | cold_final_review | not_applicable
  verdict: pass | pass_with_held | fail | incomplete | unstable | not_applicable
  required_coverage:
    - criterion: string
      disposition: checked_no_finding | checked_finding | held | not_applicable | unexplored
      evidence: string
  summary:
    - string

report:
  report_type: implementation_report | review_report | verification_report | consolidated_report | concise_pr_comment | not_applicable
  outcome: created | updated | rendered | blocked | not_applicable
  source_packets:
    - producer_skill: string
      task_id: string
      head_sha: full commit SHA | unknown
  paths:
    - string
  pr_comments:
    - target: string
      url_or_id: string | unknown
  summary:
    - string

findings:
  - id: string
    severity: blocking | high | medium | low
    origin: introduced_by_change | introduced_by_fix | pre_existing | coverage_miss | out_of_scope | unknown
    location: string
    description: string
    impact: string
    required_action: string

held:
  - item: string
    reason: string
    owner: string | unknown
    remaining_risk: string

unexplored:
  - area: string
    blocker: string
    remaining_risk: string
    verdict_impact: string

remaining_risks:
  - string
unknown:
  - field_or_fact: string
    reason: string
not_applicable:
  - field_or_area: string
    reason: string

next_action:
  type: none | implementation | review | report | design_rework | split_pr | user_decision | external_owner
  summary: string

next_chat_input:
  target_skill: chat-implementation-worker | chat-review-worker | chat-report-writer | none
  mode: string | null
  instructions:
    - string
  required_attachments_or_references:
    - string
  requested_authorized_actions:
    - read_repository | edit_code | edit_tests | write_handoff | write_report | commit | push | update_pr | comment_pr
  requested_write_boundary:
    allowed:
      - path_or_operation: string
        reason: string
    forbidden:
      - path_or_operation: string
        reason: string
```

## Permission semantics

Top-level `authorized_actions` and `write_boundary` describe permissions granted for the current worker. The worker records them but must not broaden them.

`next_chat_input.requested_authorized_actions` and `requested_write_boundary` are proposals. The next chat must not inherit them automatically. The user reviews the proposal and explicitly grants a new top-level permission set.

Without a new grant, the next worker remains read-only.

## Required worker fields

### Implementation worker

Require repository identity, scope, requirements, permissions, changed files, commands, implementation outcome, risks, transport, and next action. Record the testing and validation evidence required by the target project's instructions. When no test or testing order applies, record that fact under `not_applicable` with a reason. Review and report outcomes remain `not_applicable`.

### Review worker

Require the reviewed HEAD, scope, requirements, permissions, inspected files, review mode, verdict, coverage, findings or explicit no-findings evidence, held items, unexplored areas, risks, transport, and next action. Implementation outcome remains `not_applicable`.

### Report writer

Require source packet identities, newly granted report permissions, report type and outcome, produced paths or rendered body, copied evidence, unknowns, transport, and next action. The writer must not modify source outcomes.

## User-mediated transfer

1. The user gives a worker the task packet and current permissions.
2. The worker performs the assigned role and creates a complete handoff packet.
3. If `write_handoff` is authorized, the worker stores it under `reports/handoffs/`; otherwise it returns the complete packet for copy and paste.
4. The user reviews `head_sha`, scope, findings, unknowns, and requested next permissions.
5. The user starts the next chat and supplies the packet path or pastes the packet.
6. The next chat reads only the supplied packet and authoritative repository sources; it does not infer the previous conversation.

## Incomplete packets

When required information is missing, do not guess. Mark implementation as `blocked`, review as `incomplete`, or report as `blocked`; list missing facts under `unknown`; set `next_action.type` to `user_decision`; and identify the exact information the user must provide.

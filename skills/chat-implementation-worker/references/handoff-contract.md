# Chat Worker Handoff Contract

## Purpose

This contract defines the payload exchanged between independent ChatGPT worker chats. The release bundle contains three installable Skills. Each Skill includes an identical copy of this contract under `references/handoff-contract.md`.

The repository copy at `shared/chat-worker/handoff-contract.md` is a maintenance source only. It is not an installable Skill and is not included as a fourth Skill in the ChatGPT bundle.

## Transport model

A handoff packet is data, not automatic cross-chat memory. Persist it under `reports/handoffs/` when repository writes are authorized, or return the complete packet for copy and paste.

When a repository-backed packet is uniquely discoverable from the target Issue or PR, the next worker resolves it through the repository connector without requiring the user to repeat its path.

## Core rules

- The user is the parent and decides the next worker, scope, permissions, and merge action.
- Workers must not start another worker.
- A packet must be sufficient to continue without the previous conversation.
- Unknown facts must be recorded and must not be guessed.
- CI evidence must belong to the packet's `head_sha`.
- Current permissions do not transfer automatically to the next chat.
- Testing order and development method come from the target project's instructions.
- A handoff does not replace the worker's detailed report.

## Required identity

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
```

## Authorization and write boundary

```yaml
authorized_actions:
  - read_repository | edit_code | edit_tests | edit_documentation | edit_configuration | edit_workflows | write_handoff | write_report | create_branch | commit | push | create_issue | update_issue | create_pr | update_pr | comment_pr
write_boundary:
  allowed:
    - path_or_operation: string
      reason: string
  forbidden:
    - path_or_operation: string
      reason: string
```

## Transport

```yaml
handoff_transport:
  method: repository_file | copy_paste
  packet_path: string | null
  packet_url: string | null
  transport_note: string
```

## Scope and requirements

```yaml
scope:
  - string
non_goals:
  - string
authoritative_requirements:
  - source: issue | design | user_instruction | repository_instruction
    reference: string
    summary: string
```

## Files and evidence

```yaml
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
  artifacts:
    - id: integer
      name: string
      purpose: string
```

## Outcomes

```yaml
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
  paths:
    - string
  pr_comments:
    - target: string
      url_or_id: string | unknown
  summary:
    - string
```

## Findings and uncertainty

```yaml
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
```

## Next action

```yaml
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
    - read_repository | edit_code | edit_tests | edit_documentation | edit_configuration | edit_workflows | write_handoff | write_report | create_branch | commit | push | create_issue | update_issue | create_pr | update_pr | comment_pr
```

## Permission semantics

Top-level permissions describe only the current worker. `next_chat_input.requested_authorized_actions` is a proposal. The next chat must receive a new explicit grant.

## Incomplete packets

When required information is missing, do not guess. Mark implementation as `blocked`, review as `incomplete`, or report as `blocked`; list missing facts under `unknown`; and identify the exact next decision or input required.
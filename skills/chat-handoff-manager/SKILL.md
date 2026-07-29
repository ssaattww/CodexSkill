---
name: chat-handoff-manager
description: Create and validate lossless, transportable handoff packets between independent ChatGPT worker chats without serving as implementation, review, or report logic.
---

# Chat Handoff Manager

## Goal

Create a complete handoff packet that lets another user-started ChatGPT chat continue without relying on conversation memory or silently losing implementation, review, validation, report, or permission evidence.

## Runtime boundary

This Skill is ChatGPT-specific transport logic. It does not implement, review, write the detailed report, start another chat, change a verdict, or merge.

## Required input

Accept:

- the structured context from `work-context-manager`,
- the complete output of `implementation-worker`, `review-worker`, or `report-writer`,
- runtime-specific authorization, persistence, PR-comment, and next-chat information supplied by the wrapper.

Do not summarize away fields required by the producing core Skill. A handoff is a lossless transport envelope for available evidence, not a shorter substitute for that evidence.

## Required packet

Writers emit `schema_version: 3`.

```yaml
schema_version: 3
producer:
  skill: string
  mode: string
  generated_at: ISO-8601

repository: owner/name | unknown
issue_or_pr: string | null
task_id: string | null
branch: string | unknown
base_ref: string | null
target:
  current_head: full_sha | unknown
  reviewed_head: full_sha | null
  commit_range: string | null

authoritative_requirements:
  - source: user_instruction | repository_instruction | issue | task | design | pr | report | handoff | other
    reference: string
    summary: string

authorized_actions:
  - read_repository | edit_code | edit_tests | edit_documentation | edit_configuration | edit_workflows | write_handoff | write_report | create_branch | commit | push | create_issue | update_issue | create_pr | update_pr | comment_pr
write_boundary:
  allowed:
    - path_or_operation: string
      reason: string
  forbidden:
    - path_or_operation: string
      reason: string

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
  intentionally_untouched:
    - path_or_area: string
      reason: string

commands:
  - command: string
    purpose: string
    exit_code: integer | unknown
    result: passed | failed | blocked | not_run
    head_sha: full_sha | unknown
    evidence: string | null

tests:
  - name: string
    phase: red | green | pre_implementation | post_implementation | regression | verification | not_applicable
    result: passed | failed | blocked | not_run
    head_sha: full_sha | unknown
    evidence: string | null

ci:
  required: true | false
  workflow: string | null
  run_id: integer | null
  head_sha: full_sha | unknown
  conclusion: success | failure | cancelled | skipped | in_progress | unknown | not_applicable
  artifacts:
    - id: integer | unknown
      name: string
      purpose: string

implementation:
  outcome: completed | partial | blocked | not_applicable
  final_head: full_sha | unknown
  commits:
    - sha: full_sha
      purpose: string
  addressed_findings:
    - id: string
      reviewed_head: full_sha | unknown
      disposition: addressed | partial | blocked | not_applicable
      evidence: string
  summary:
    - string

review:
  mode: initial_review | fix_verification | independent_final_review | not_applicable
  reviewed_head: full_sha | unknown
  verdict: pass | pass_with_held | fail | incomplete | unstable | not_applicable
  required_coverage:
    - criterion: string
      disposition: checked_no_finding | checked_finding | held | not_applicable | unexplored
      evidence: string
  validation_assessment:
    - item: string
      result: supported | unsupported | failed | unavailable | not_applicable
      evidence: string
  summary:
    - string

report:
  report_type: implementation_report | review_report | verification_report | independent_final_review_report | consolidated_report | concise_pr_comment | not_applicable
  outcome: created | updated | rendered | blocked | not_applicable
  persistence_mode: repository_file | report_attestation_commit | external_artifact | copy_paste | not_applicable
  paths:
    - string
  reviewed_head: full_sha | null
  attestation_head: full_sha | null
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
    evidence: string
    required_action: string

held:
  - item: string
    reason: string
    owner: string | unknown
    remaining_risk: string
    verdict_impact: string

unexplored:
  - area: string
    blocker: string
    remaining_risk: string
    verdict_impact: string

unknown:
  - field_or_fact: string
    reason: string
not_applicable:
  - field_or_area: string
    reason: string
remaining_risks:
  - string

next_action:
  type: none | implementation | review | report | design_rework | split_pr | user_decision | external_owner
  target_skill: string | none
  mode: string | null
  summary: string
  instructions:
    - string
  required_attachments_or_references:
    - string
  requested_authorized_actions:
    - read_repository | edit_code | edit_tests | edit_documentation | edit_configuration | edit_workflows | write_handoff | write_report | create_branch | commit | push | create_issue | update_issue | create_pr | update_pr | comment_pr

transport:
  method: repository_file | copy_paste
  packet_path: string | null
  packet_url: string | null
  transport_note: string
```

## Lossless transport rules

- Preserve every available field required by the producing core Skill's output contract.
- Preserve exact finding identity, origin, location, impact, evidence, required action, and reviewed HEAD.
- Preserve required coverage dispositions, held items, unexplored areas, validation assessment, intentionally untouched areas, commands, tests, CI artifacts, implementation commits, report paths, and PR comment references.
- Do not replace structured evidence with a prose summary when the structured evidence is available.
- Unknown facts remain unknown; do not guess.
- CI evidence must belong to the packet's target HEAD.
- Current permissions do not automatically transfer to the next chat.
- Requested next-chat permissions are proposals requiring a new user grant.
- The handoff does not replace the detailed report.
- When repository persistence is unavailable, return the complete packet for copy and paste.

## Compatibility

- Writers emit schema version 3.
- Readers must accept schema versions 1 and 2 when encountered.
- Normalize version 1 or 2 `cold_final_review` to `independent_final_review`.
- Preserve every field that exists in an older packet. Do not discard older free-form or structured evidence merely because version 3 uses a different location.
- Map absent version 3 fields to explicit `unknown` or `not_applicable` entries with the reason `not present in source schema`; do not invent values.
- When missing fields prevent safe continuation, mark the receiving operation `blocked` or review verdict `incomplete` and identify the exact missing evidence.
- Unsupported future schema versions remain blocked until a migration rule exists.

## Final-review terminal rule

After an independent final review passes and its detailed report is persisted as a report-attestation commit, return the final handoff inline or transport it outside the reviewed PR branch. Do not create another repository handoff commit after the attestation head, because that would create an unreviewed post-attestation HEAD.

The packet must record both:

- `review.reviewed_head`: the implementation HEAD reviewed by the independent reviewer,
- `report.attestation_head`: the validated report-only commit, when one exists.

## Completion condition

Complete when the packet losslessly represents the available core-Skill output, target and reviewed identities are explicit, findings and uncertainty retain their evidence, permissions and transport are explicit, compatibility handling did not discard data, the next chat can continue independently, and no implementation, review verdict change, additional post-attestation commit, or merge was performed.

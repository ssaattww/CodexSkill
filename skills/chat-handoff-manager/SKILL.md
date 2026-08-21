---
name: chat-handoff-manager
description: Create and validate lossless, transportable handoff packets between independent ChatGPT worker chats without serving as implementation, review, or report logic.
---

# Chat Handoff Manager

## Goal

Create a complete handoff packet that lets another user-started ChatGPT chat continue without relying on conversation memory or silently losing context, implementation, review, validation, report, permission, blocked-state, or terminal-gate evidence.

## Runtime boundary

This Skill is ChatGPT-specific transport logic. It does not implement, review, write the detailed report, start another chat, change a verdict, or merge.

## Required input

Accept:

- the structured context from `work-context-manager`,
- the complete output of `implementation-worker`, `review-worker`, or `report-writer`,
- runtime-specific authorization, persistence, PR-comment, attestation-gate, and next-chat information supplied by the wrapper.

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

verification:
  capability: local_execution_available | remote_ci_only | unknown
  capability_evidence:
    - string
  technical_head: full_sha | unknown
  administrative_parent: full_sha | null
  commit:
    state: commit_pending | committed | not_required | unknown
    review_target_sha: full_sha | null
  push:
    state: pending | pushed | not_required | unauthorized | unknown
    head_sha: full_sha | unknown
  ci_wait:
    state: pending | completed | not_required | unavailable | unknown
    required_for: route_verification | merge_gate | not_required | unknown
  final_publication:
    sequence: final_push_then_authorized_pr_create_or_update_then_exact_head_pull_request_ci_wait | not_applicable | unknown
    pr_action: create | update | not_required | unauthorized | unknown

authoritative_requirements:
  - source: user_instruction | repository_instruction | issue | task | design | pr | report | handoff | other
    reference: string
    summary: string

development_policy:
  method: string | unknown
  testing_order: string | unknown
  governing_source: string | unknown
validation_plan:
  commands:
    - string
  required_failure_diagnostics:
    - string
blocked:
  - item: string
    reason: string
    required_input_or_decision: string | null

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
  failure_diagnostics:
    - type: log | test_result | standard_output | standard_error | artifact | other
      location: string | null
      summary: string
  blocked_items:
    - item: string
      reason: string
      required_input_or_decision: string | null
  summary:
    - string

review:
  mode: initial_review | fix_verification | independent_final_review | independent_final_closure | not_applicable
  reviewed_head: full_sha | unknown
  reviewer:
    identity: string | unknown
    role: normal_reviewer | replacement_normal_reviewer | independent_final_reviewer | not_applicable
    continuity:
      previous_reviewer_identity: string | null
      changed: true | false
      reason: string | null
    independence:
      implemented_change: true | false | unknown
      implemented_review_fix: true | false | unknown
      served_as_normal_reviewer: true | false | unknown
      inherited_conversation: true | false | unknown
      evidence:
        - string
  verdict: pass | pass_with_held | fail | incomplete | unstable | not_applicable
  required_coverage:
    - criterion: string
      disposition: checked_no_finding | checked_finding | held | not_applicable | unexplored
      evidence: string
  validation_assessment:
    - item: string
      result: supported | unsupported | failed | unavailable | not_applicable
      evidence: string
  reserved_report_paths:
    - string
  report_attestation:
    allowed: true | false | not_applicable
    reviewed_implementation_head: full_sha | null
    allowed_paths:
      - string
    required_first_parent: full_sha | null
    maximum_commits_after_reviewed_head: integer | null
    forbidden_path_classes:
      - executable | skill | design | workflow | configuration | tracking | handoff | product | other
    no_later_commits_required: true | false | not_applicable
    validation_status: pending | passed | failed | not_applicable
    validation_evidence:
      - string
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

source_payloads:
  - source_skill: string
    output_contract_version: string | unknown
    content_type: application/yaml | application/json | text/markdown | text/plain | other
    payload: object | string
extensions:
  - namespace: string
    payload: object | string

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

- Populate the typed projection for every available field defined above.
- Also preserve each producing core Skill's complete, versioned output under `source_payloads`; typed projection does not replace the raw source payload.
- Preserve every available field required by the producing core Skill's output contract, including development policy, planned validation, required failure diagnostics, blocked state, `verification_capability`, separate commit/push/CI-wait state, failure diagnostics, reviewer identity, reviewer independence, reserved report paths, and exact report-attestation conditions.
- Preserve exact finding identity, origin, location, impact, evidence, required action, and reviewed HEAD.
- Preserve required coverage dispositions, held items, unexplored areas, validation assessment, intentionally untouched areas, commands, tests, CI artifacts, implementation commits, report paths, and PR comment references.
- Use `extensions` for runtime or future fields that are not yet represented in the typed projection.
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
- Preserve the complete original version 1 or 2 packet as a `source_payloads` entry before projecting fields into version 3.
- Preserve every field that exists in an older packet. Mapping failures or fields without a version 3 typed destination must remain in the original `source_payloads` entry or a namespaced `extensions` entry.
- Map genuinely absent version 3 fields to explicit `unknown` or `not_applicable` entries with the reason `not present in source schema`; do not invent values.
- Do not convert an existing source value into `unknown` merely because no typed mapping exists.
- When missing fields prevent safe continuation, mark the receiving operation `blocked` or review verdict `incomplete` and identify the exact missing evidence.
- Unsupported future schema versions remain blocked until a migration rule exists; preserve the untouched future packet as source evidence when safe parsing is possible.

## Final-review terminal rule

After an independent final review passes and its detailed report is persisted as a report-attestation commit, return the final handoff inline or transport it outside the reviewed PR branch. Do not create another repository handoff commit after the attestation head, because that would create an unreviewed post-attestation HEAD.

The packet must record:

- `review.reviewed_head`: the implementation HEAD reviewed by the independent reviewer,
- `review.reviewer`: identity and independence evidence,
- `review.mode` and reviewed-head chain for the one exhaustive independent pass and any same-reviewer bounded closure,
- `review.reserved_report_paths`: paths reserved before the review,
- `review.report_attestation`: the complete allowlist and validation gate,
- `report.attestation_head`: the validated report-only commit, when one exists.
- `verification`: capability evidence plus distinct technical head,
  administrative parent, commit, push, and CI-wait state. Do not require a
  packet or report to contain its own future commit SHA; use `commit_pending`
  until a commit exists.
- `verification.final_publication`: the terminal sequence of final push,
  authorized PR creation or update, then exact-head required `pull_request` CI
  wait when it is the merge gate.

## Completion condition

Complete when the packet's typed projection and preserved source payloads losslessly represent the available core-Skill output, target and reviewed identities are explicit, blocked state and failure-diagnostic requirements remain actionable, reviewer identity and independence are verifiable, report-attestation conditions are reproducible, findings and uncertainty retain their evidence, permissions and transport are explicit, compatibility handling did not discard data, the next chat can continue independently, and no implementation, review verdict change, additional post-attestation commit, or merge was performed.

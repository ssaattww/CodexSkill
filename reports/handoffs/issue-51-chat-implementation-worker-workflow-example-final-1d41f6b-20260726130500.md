# Chat Worker Handoff Packet

```yaml
schema_version: 1
producer:
  skill: chat-implementation-worker
  mode: documentation-follow-up
  generated_at: 2026-07-26T13:05:00+09:00

task_id: issue-51
issue_or_pr: PR #52
repository: ssaattww/CodexSkill
branch: agent/issue-51-chat-worker-skills
base_ref: main
head_sha: 1d41f6bcad683d24ba59cd911154ba898d210c5e

authorized_actions:
  - read_repository
  - write_report
  - write_handoff
  - commit
  - push
  - update_pr
  - comment_pr

scope:
  - add a concrete user workflow example
  - define when to create or continue chats
  - provide prompts for implementation, review, follow-up, verification, and cold final review
non_goals:
  - modify worker responsibilities
  - modify existing Codex-oriented skills
  - merge the pull request

files:
  changed:
    - path: tests/test_chat_worker_skills_contract.py
      purpose: require concrete workflow examples
    - path: design/chat-worker-skill-design.md
      purpose: Japanese user workflow and prompts
    - path: skills/design/chat-worker-skill-design.md
      purpose: byte-identical design mirror
    - path: reports/issue-51-chat-worker-skills-implementation-r4-20260726130000.md
      purpose: implementation report

ci:
  required: true
  workflow: Chat worker skill contract
  run_id: 30187113650
  head_sha: 1d41f6bcad683d24ba59cd911154ba898d210c5e
  conclusion: success
  jobs:
    - name: contract
      conclusion: success
  artifacts: []

implementation:
  outcome: completed
  commits:
    - sha: 840eb50c92c0d477ed4c406b3ac2d04d68538fe3
      purpose: add workflow example contract test
    - sha: 42594e4159a2493d11b6327a51274b3a7a74f531
      purpose: add primary design workflow examples
    - sha: 61d9ef59d94579a244374b501617da41f346efb9
      purpose: synchronize design mirror
    - sha: 1d41f6bcad683d24ba59cd911154ba898d210c5e
      purpose: finalize report and CI evidence
  summary:
    - Chat A is created for initial implementation and reused for review follow-up.
    - Chat B is newly created for initial review.
    - Chat C is normally newly created for fix verification.
    - Chat D is always newly created for cold final review.
    - Complete prompt examples are included for every stage.

review:
  review_mode: not_applicable
  verdict: not_applicable
  required_coverage: []
  summary: []

report:
  report_type: implementation_report
  outcome: created
  source_packets: []
  paths:
    - reports/issue-51-chat-worker-skills-implementation-r4-20260726130000.md
  pr_comments: []
  summary:
    - User workflow examples were added and validated.

findings: []
held:
  - item: operational trial across real separate ChatGPT chats
    reason: not executed in this implementation session
    owner: user
    remaining_risk: prompt wording may need refinement after practical use
unexplored: []
remaining_risks:
  - real multi-chat operational trial remains pending
unknown: []
not_applicable: []

handoff_transport:
  method: repository_file
  packet_path: reports/handoffs/issue-51-chat-implementation-worker-workflow-example-final-1d41f6b-20260726130500.md

next_action:
  type: review
  summary: review the updated PR if another independent review is required

next_chat_input:
  target_skill: chat-review-worker
  mode: cold_final_review
  instructions:
    - Review PR #52 at HEAD 1d41f6bcad683d24ba59cd911154ba898d210c5e.
    - Confirm that the user workflow examples are sufficient and consistent with the worker contracts.
  required_attachments_or_references:
    - reports/handoffs/issue-51-chat-implementation-worker-workflow-example-final-1d41f6b-20260726130500.md
    - design/chat-worker-skill-design.md
  requested_authorized_actions:
    - read_repository
    - write_report
    - write_handoff
    - comment_pr
  requested_write_boundary:
    allowed:
      - path_or_operation: reports/**
        reason: review evidence and handoff only
      - path_or_operation: PR #52 comment
        reason: concise review summary
    forbidden:
      - path_or_operation: product code and worker Skill files
        reason: review-only operation
```

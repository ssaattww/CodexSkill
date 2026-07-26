# Chat Worker Handoff Contract

## 目的

このcontractは、利用者が親として複数のChatGPT chatを順番に起動するときに、前のchatの結果を次のchatへ渡す共通形式を定義する。

各workerは別のworkerを自動起動しない。利用者がhandoff packetを確認し、必要な部分を次のchatへ渡す。

## 基本原則

- 会話履歴を前提にせず、packetだけで次のchatが作業を再開できるようにする。
- 確認できなかった値は推測せず、`unknown`へ記録する。
- 対象外の値は空欄にせず、理由付きで`not_applicable`へ記録する。
- branchのCI判定には、必ずpacketの`head_sha`に紐づくrunだけを使用する。
- 実装結果、review finding、test結果、CI結果をreport writerが変更または補完してはならない。
- secret、credential、個人情報、不要な大容量logをpacketへ埋め込まない。

## Canonical packet

次のYAML形状を標準とする。Markdown内のYAML block、JSON、または同じfieldを持つ表現へ変換してよいが、fieldの意味を変更しない。

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
    phase: red | green | regression | verification
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
```

## Worker別の必須field

### Implementation worker

次を必須とする。

- `task_id`
- `repository`、`branch`、`base_ref`、`head_sha`
- `scope`、`non_goals`、`authoritative_requirements`
- `files.changed`
- Red、Green、またはtest-firstが対象外である理由を含む`tests`
- `commands`
- `implementation.outcome`
- `remaining_risks`
- `next_action`
- `next_chat_input`

Review結果を作らないため、`review.review_mode`と`review.verdict`は`not_applicable`とする。

### Review worker

次を必須とする。

- review対象の`repository`、`branch`、`base_ref`、`head_sha`
- `scope`、`non_goals`、`authoritative_requirements`
- `files.inspected`
- `review.review_mode`
- `review.verdict`
- `review.required_coverage`
- `findings`または明示的なfindingなしのsummary
- `held`、`unexplored`、`remaining_risks`
- `next_action`
- `next_chat_input`

Product implementationを行わないため、`implementation.outcome`は`not_applicable`とする。

### Report writer

次を必須とする。

- 入力に使ったhandoff packetの識別情報
- 作成したreport pathまたは返却したreport本文
- reportへ転記したHEAD SHA、CI run、artifact、finding
- 入力不足を示す`unknown`
- report作成後の`next_action`

Report writerは、入力packetの`implementation`、`review`、`findings`、`tests`、`ci`を変更しない。

## 利用者によるchat間引き渡し

1. 利用者が対象workerのSkillとtask packetをchatへ渡す。
2. workerが作業し、このcontractに従うhandoff packetを返す。
3. 利用者がpacketの`head_sha`、scope、finding、unknownを確認する。
4. 利用者が`next_chat_input`と必要なrepository参照を次のchatへ渡す。
5. 次のchatは以前の会話を推測せず、受け取ったpacketとrepositoryを正として作業する。

## 不完全なpacket

必要fieldが不足していて安全に作業できない場合、workerは値を推測しない。

- `review.verdict`はreview時のみ`incomplete`とする。
- `implementation.outcome`は実装時のみ`blocked`とする。
- 不足fieldと理由を`unknown`へ記録する。
- `next_action.type`を`user_decision`とする。
- `next_chat_input.instructions`へ、利用者が補うべき情報を列挙する。

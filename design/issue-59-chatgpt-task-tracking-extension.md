# Issue #59 ChatGPT Task Tracking Extension

## 目的

Issue #59「task更新スキルがzipに同封されていないので、chatgpt側からtask更新できない」に必要な差分だけを定義する。

この文書は `design/chat-worker-skill-design.md` と `design/skill-hierarchy-design.md` の既存契約を削除・置換しない。Issue #59に関して、ChatGPT登録用Skill集合、implementation wrapperのtask tracking flow、canonical tracking path、handoff task tracking projectionだけを追加規定する。

review continuity、pre-freeze、independent final review、report attestation、Release publication、Codex review flow、merge境界など既存設計のその他の契約は変更しない。

## 追加するSkill

ChatGPT登録用 `chatgpt-worker-skills.zip` へ、既存の4 wrapper + 4 core Skillに加えて次の3 Skillを含める。

- `task-breakdown-planner`
- `task-consistency-manager`
- `progress-sync-manager`

したがって配布ZIPは次の11 root Skillを持つ。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
├─ chat-review-worker/
├─ chat-report-writer/
├─ chat-handoff-manager/
├─ work-context-manager/
├─ implementation-worker/
├─ review-worker/
├─ report-writer/
├─ task-breakdown-planner/
├─ task-consistency-manager/
└─ progress-sync-manager/
```

各rootは独立Skill directoryであり `SKILL.md` を持つ。既存のsymlink禁止、Skill外shared runtime file依存禁止、front matter name一致、archive root検証は維持する。

## 実行owner

3つのtask tracking SkillはCodex親専用ではなく、canonical tracking writeを所有するauthorized callerが実行するruntime-neutral Skillとする。

- Codex標準flowでは通常parentが実行する。
- ChatGPT implementation wrapperではcurrent chatが直接実行する。
- `chat-implementation-worker`はsub-agentを起動しないため、task tracking Skillの実行にsub-agent delegationを要求しない。
- delegation可能な別runtimeが補助auditを行う場合でも、canonical trackingの最終write ownerはauthorized callerのままとする。

## Canonical tracking path

tracking file名をSkill内で固定しない。

`work-context-manager`はProject Instruction、repository instruction、accepted task/designなどのauthorityから次を解決する。

```yaml
tracking:
  task_path: repository_relative_path | unknown
  phase_path: repository_relative_path | null | unknown
```

例としてProject Instructionが `tasks/tasks-status.md` を指定している場合、`task_path`はそのpathを完全一致で保持する。`tasks-status.md`というbasenameへ置換してはならない。

`phase_path`は別phase fileを使わないprojectでは`null`を許可する。必要なpathを解決できない場合は推測せずblocked／unknownとする。

3つのtask tracking Skillと`chat-implementation-worker`は、`work-context-manager`が解決したpathを変更せず受け渡す。

## ChatGPT implementation flow

`chat-implementation-worker`は次を実行する。

1. `work-context-manager`
2. `task-consistency-manager`
3. trackingが未登録、大きすぎる、曖昧、dependencies／exit criteria不足の場合だけ `task-breakdown-planner`
4. 3を実行した場合は `task-consistency-manager` を再実行
5. `implementation-worker`
6. `progress-sync-manager`
7. `report-writer`
8. `chat-handoff-manager`

`progress-sync-manager`は実装進捗、validation、review follow-up、commit／PR、blocked state、完了状態が変化した時点でcanonical trackingを同期する。

canonical task trackingの直接編集ロジックを`chat-implementation-worker`へ複製しない。

## Handoff task tracking projection

`chat-handoff-manager` schema version 3へ次のtyped projectionを追加する。

```yaml
task_tracking:
  task_path: repository_relative_path | unknown
  phase_path: repository_relative_path | null | unknown
  state: string | unknown
  phase: string | null | unknown
  dependencies:
    - string
  exit_criteria:
    - string
  blockers:
    - string
  pending_action: string | null | unknown
```

canonical pathは`work-context-manager`の出力を完全一致で保持する。task state、phase、dependencies、exit criteria、blockers、pending actionは最新のtask tracking Skill outputから保持する。

従来どおりtyped projectionだけでなく、producing Skillのcomplete outputを`source_payloads`へ保持する。schema version 1／2からversion 3へ読む場合、元schemaに存在しないtask tracking fieldを推測しない。

## Release workflowへの影響

Release publication方式、権限境界、current-HEAD checkout規則は変更しない。

既存build step `scripts/build_chatgpt_worker_skills.py` が4 wrapper、4 core Skillに加えて3 task tracking Skillを必須rootとして収録・検証することだけをIssue #59の変更対象とする。

## 完了条件

- 3 task tracking SkillがChatGPT登録用ZIPに含まれる。
- 3 SkillがChatGPT current chatからsub-agentなしで実行可能なcontractを持つ。
- canonical task／phase pathが`work-context-manager`から各task tracking Skillへlosslessに渡る。
- configured pathをbasenameへ置換または推測しない。
- `chat-handoff-manager`がtask tracking path/state/phase/dependencies/exit criteria/blocker/pending actionをtyped projectionとして保持する。
- 既存設計のIssue #59と無関係な契約を削除しない。
- CodexSkill repository policyに従い、この保守作業へTDDを適用しない。
- mergeは行わない。

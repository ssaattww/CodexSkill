# Issue #59 Review Follow-up Report

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #59
- PR: #60
- Mode: review follow-up
- Source review comment: PR conversation comment `5208976404`
- Source reviewed implementation HEAD: `a39942bdb11397099463135f0d8487aad8f0d7a6`

CodexSkill repository policyに従いTDDは適用していない。

## 指摘対応

### F-60-01 blocking

指摘: 配布対象へ追加したtask tracking Skillが`parent`専用かつsub-agent delegation前提で、ChatGPT wrapperのcurrent-chat execution契約と矛盾する。

対応:

- `task-breakdown-planner`
- `task-consistency-manager`
- `progress-sync-manager`

を「authorized canonical tracking writeを所有するcaller」が実行するruntime-neutral contractへ変更した。

Codex標準flowでは通常parent、ChatGPT implementation wrapperではcurrent chatが直接実行する。3 Skill自身はsub-agentを要求・起動しない。別runtimeが補助delegationを持つ場合でも、canonical write ownerはcallerに残る。

`chat-implementation-worker`には、dependency Skill内のoptional delegationを実行せずcurrent chatでtask tracking operationを行うboundaryを明記した。

### F-60-02 blocking

指摘: task tracking Skillが`tasks-status.md` / `phases-status.md`を固定名で扱い、Project Instructionの`tasks/tasks-status.md`等と一致しない可能性がある。

対応:

`work-context-manager` outputへ次を追加した。

```yaml
tracking:
  task_path: repository_relative_path | unknown
  phase_path: repository_relative_path | null | unknown
```

Project/repository authorityからcanonical pathを解決し、configured pathをbasenameへ置換しない。task pathが解決不能ならguessせずblocked／unknownとする。phase fileを利用しないprojectでは`null`を許可する。

3 task tracking Skillと`chat-implementation-worker`はこのresolved pathを完全一致で受け渡すcontractへ変更した。

### F-60-03 high

指摘: 設計がtask tracking stateをhandoffへ保持するとしている一方、`chat-handoff-manager` typed schemaに対応fieldがない。

対応:

schema version 3へ次を追加した。

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

canonical pathは`work-context-manager` outputをlosslessに保持し、state等は最新task tracking Skill outputから保持する。task tracking Skill outputも`source_payloads`へ完全保存するcontractへ変更した。

### F-60-04 high

指摘: Issue #59と無関係なRelease詳細、review continuity、pre-freeze、attestation等を既存設計書から大量削除した。

対応:

最初に次の3ファイルをPR base `aa3c1462ece21dce82f644788b9cbc36a38e76a7`の内容へ復元し、無関係な大量削除を除去した。

- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`

その後、正本設計と実装の矛盾を残さないため、Issue #59の影響箇所だけを最小差分で再更新した。Release publication、normal review continuity、pre-freeze、independent final review、report attestation、Codex review flow、標準作業手順、merge境界などIssue #59と無関係な既存契約は維持した。

正本設計では次だけを更新した。

- 4 wrapper + 4 core Skillへ3 task tracking Skillを加えた11 Skill配布構成
- task tracking Skillをauthorized callerが実行するruntime-neutral contract
- `work-context-manager`によるcanonical tracking path解決
- `chat-implementation-worker`のtask consistency／breakdown／progress sync flow
- handoffのtask tracking typed projectionとtask tracking raw output保持
- Release validator／builderが必須task tracking Skillを扱うこと
- Skill一覧上のtask tracking Skill実行方式

Issue #59固有の詳細は`design/issue-59-chatgpt-task-tracking-extension.md`にも保持し、正本の該当箇所と整合させた。

`design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`は同一blob `bd3f9f784b2d723fea828c0fe215d109cbd82182`へ同期した。

## Canonical tracking同期

Project Instructionのcanonical task tracking path `tasks/tasks-status.md`と既存phase path `tasks/phases-status.md`を使用した。

- `tasks/tasks-status.md`へIssue #59をT-003として登録した
- T-003はPhase 8、statusはreview follow-up実装済み／normal fix verification待ち
- T-002の現在の配布構成表記だけを4 wrapper + 4 core + 3 task tracking Skillへ同期し、Issue #53のreview履歴は変更していない
- `tasks/phases-status.md`へPhase 8を追加し、F-60-01からF-60-04の対応状態とcurrent-HEAD validation待ちを記録した

## Base比較

PR base `aa3c1462ece21dce82f644788b9cbc36a38e76a7` とtracking同期HEAD `ed5785a0b1d80d69e2fe3d1d388d128a0763c3b9` のcompareでは、設計差分は次の規模に収まっている。

- `design/chat-worker-skill-design.md`: +77 / -24
- `design/skill-hierarchy-design.md`: +52 / -22
- `skills/design/skill-hierarchy-design.md`: +52 / -22

初回対応時に発生していた約1000行規模の無関係な削除は残っていない。

## 主要変更file

- `scripts/build_chatgpt_worker_skills.py`
- `skills/work-context-manager/SKILL.md`
- `skills/task-breakdown-planner/SKILL.md`
- `skills/task-consistency-manager/SKILL.md`
- `skills/progress-sync-manager/SKILL.md`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-handoff-manager/SKILL.md`
- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
- `design/issue-59-chatgpt-task-tracking-extension.md`
- `tasks/tasks-status.md`
- `tasks/phases-status.md`

## 検証方針

CodexSkill repository policyによりRed/Green TDDは`not applicable`。

本report commit後のcurrent PR HEADに一致する `Validate and release ChatGPT worker skills` workflow runだけをCI evidenceとして使用する。別SHAのrunは代用しない。

matching runが存在しない場合はCI未実施として扱う。

## 残作業

- current HEAD固有のrepository validator／11 Skill ZIP build／artifact確認
- source finding `F-60-01`から`F-60-04`について、同じnormal review continuityでfix verificationを実施する

本implementation worker自身はreview verdictを出さない。

## Merge

mergeは実施しない。

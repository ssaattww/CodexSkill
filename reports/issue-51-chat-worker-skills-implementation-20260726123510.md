# Issue #51 ChatGPT Chat Worker Skill 実装レポート

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- Pull Request: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Base: `main`
- 実装確認HEAD: `b626eab469bd46e5350991b69c5790c41e9b4edc`

## 背景

ChatGPTの通常chatでは、1つのchatが別のsub-agentを起動する構成を前提にできない。一方で、利用者は複数chatを明示的に起動でき、各chatはrepositoryへMarkdown reportを配置できる。

このため、利用者自身が親としてchatの順序とhandoffを管理し、各chatが単一workerとして直接作業する構成を追加した。

## Scope

- ChatGPT chat向けstandalone worker Skillを3つ追加する
- chat間で共有するhandoff contractを追加する
- ChatGPT向け構成を既存Codex hierarchyと分離して設計する
- contract testをtest-firstで追加する
- failure時に原因調査用artifactを保存するGitHub Actions workflowを追加する
- workflowが対象branch HEAD SHAそのものを検証するようにする

## Non-goals

- ChatGPT chatから別agentを起動する仕組み
- 自動chat orchestration
- 既存Codex向けSkillの置換または実行契約変更
- 自動merge
- 独立verification worker、task planner、design worker、Git workflow managerの追加

## 切り出したSkill

### `chat-implementation-worker`

決定済みtaskをtest-firstで実装するworkerである。

- `initial implementation`と`review follow-up`を扱う
- code、test、validation evidenceを所有する
- `authorized_actions`と`write_boundary`内だけを変更する
- narrative reportを作成しない
- 独立review判定を行わない
- mergeしない

### `chat-review-worker`

指定HEADを直接reviewするworkerである。

- `initial review`
- `fix verification`
- `cold final review`
- riskに応じたcoverage選択
- `pass`、`pass_with_held`、`fail`、`incomplete`、`unstable`の判定
- product codeとtestを変更しない
- 許可されたreview reportまたはPR commentだけを配置する
- mergeしない

### `chat-report-writer`

確定済みhandoffをMarkdown reportまたは簡易PR commentへ変換するworkerである。

- implementation、review、verification reportを扱う
- 入力にないfinding、severity、test結果、CI結論を作らない
- codeまたはtestを変更しない
- `authorized_actions`に従ってreportとPR commentだけを配置する
- mergeしない

## 切り出さなかったSkill

### Chat orchestrator

利用者が親としてchatを起動し、順序、停止、scope変更、mergeを管理するため追加しなかった。

### Delegation manager

workerは別workerへ委譲せず、受け取った作業を直接実行するため追加しなかった。

### Verification worker

初期構成では、implementation validationを`chat-implementation-worker`、review evidence確認を`chat-review-worker`が担当する。独立verificationが反復して必要になった場合だけ後続Issueで検討する。

### Task planner、design worker、Git workflow manager

利用者がscopeとauthoritative requirementsを決定し、全体Git flowを管理する前提であるため、今回の必須workerには含めなかった。

## Shared handoff contract

`skills/chat-worker-shared/references/handoff-contract.md`を3 Skill共通の唯一のcontractとして追加した。

主なfieldは次のとおり。

- task、Issue、PR identifier
- repository、branch、base ref、HEAD SHA
- `authorized_actions`
- `write_boundary`
- scope、non-goals、authoritative requirements
- changedまたはinspected files
- commands、tests、CI、artifacts
- implementation outcome
- review mode、coverage、verdict
- report type、source packets、path、PR comment、outcome
- findings、held、unexplored、remaining risks
- unknown、not applicable
- next action、next chat input

値を確認できない場合は推測せず`unknown`、非該当の場合は理由付き`not_applicable`を使用する。

## 設計書

ChatGPT向け構成は既存Codex向けhierarchyへ混在させず、次の2ファイルを正本としてbyte-identicalに管理する。

- `design/chat-worker-skill-design.md`
- `skills/design/chat-worker-skill-design.md`

既存の次のファイルは変更していない。

- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
- `skills/development-orchestrator/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/codex-delegation-executor/SKILL.md`
- `skills/implementation-executor/SKILL.md`
- `skills/review-enforcer/SKILL.md`
- `skills/report-output-manager/SKILL.md`

## TDD証跡

### 初回Red

- Test commit: `f344d2a77ca72ed5936093510547a4c81a2d0b98`
- Workflow追加後HEAD: `f5b2107dfdce2e9c66944f1bf5d313c0ea9e341d`
- Workflow Run: `30185865727`
- Result: failure
- Failure reason: 3つのworker Skill、shared handoff contract、設計書が未作成
- Diagnostic artifact:
  - ID: `8626998950`
  - Name: `chat-worker-skill-contract-diagnostics-30185865727-1`

### 初回Green

- HEAD: `1a189b243fe215eaa0ddc3259a4c6ec599464ba1`
- Workflow Run: `30186081623`
- Result: success

初回Green後のreviewで、次の契約不足を確認した。

- PR eventでmerge refをcheckoutしており、branch HEADそのものを検証していなかった
- workflowのpath filterとfailure artifactが旧design fileを参照していた
- implementation workerがnarrative reportを兼務できる表現で、実装専任という分離が不十分だった
- handoffにworkerの許可操作とwrite boundaryがなかった
- report writerの出力を表す構造化fieldがなかった

### Review強化Red

上記責務境界をcontract testへ先行追加した。

- Test commit: `32e55938644acf7530cdfd4365ed7e2a9d6695e0`
- Workflow Run: `30186176348`
- Result: failure
- Failure reason:
  - implementation workerに`narrative reportを作成しない`契約が未反映
  - shared handoffに`authorized_actions`、`write_boundary`、`report`等が未反映
- Diagnostic artifact:
  - ID: `8627103321`
  - Name: `chat-worker-skill-contract-diagnostics-30186176348-1`

### Review強化Green

次を修正した。

- implementation workerを実装、test、validation evidence、handoffだけへ限定
- review workerのreportとPR commentを明示許可制に変更
- report writerへsource packet、path、comment、outcomeを持つ`report` fieldを追加
- 3 workerへ`authorized_actions`と`write_boundary`を追加
- workflowでPRのbranch HEAD SHAをcheckoutし、actual SHAとの一致を検査
- failure artifactへ対象Skill、ChatGPT向け設計、HEAD情報を保存
- Issue #51 report commitもworkflow対象に追加

実装確認HEAD:

- HEAD: `b626eab469bd46e5350991b69c5790c41e9b4edc`
- Workflow Run: `30186397394`
- Result: success
- Job: `contract` success

このreport追加後の最終HEADに紐づくRunは、PR本文またはPR commentへ別途記録する。

## 変更ファイル

- `.github/workflows/chat-worker-skill-contract.yml`
- `design/chat-worker-skill-design.md`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`
- `skills/design/chat-worker-skill-design.md`
- `tests/test_chat_worker_skills_contract.py`

## CI failure diagnostics

workflow failure時は次をartifactへ保存する。

- test stdout
- test stderr
- runner、Python、Git、event、ref、target HEAD、actual HEAD
- contract test source
- 3 worker Skillとshared contract
- 2つのChatGPT向け設計書
- Issue #51 report
- `git diff --check`
- `git status`
- HEAD commit summary

## Scope保護

- 既存Codex向けSkillを変更していない
- PR #50のbranchまたは変更内容を取り込んでいない
- Issue #51専用のworker、shared contract、design、test、workflowだけを変更した
- mergeは実施していない

## Remaining risks

- 実際に別々のChatGPT chatへSkill bundleを配置し、handoffだけで一連の実装、review、reportを完走するoperational trialは未実施である
- handoffはMarkdown上のcontractであり、JSON Schemaによる型検証は今回のscope外である
- 独立verification worker、task planner、design workerの必要性は実運用で反復が確認された場合に後続Issueで判断する

## 結果

Issue #51で定義した3つのstandalone worker、shared handoff contract、専用設計、contract test、failure diagnostics workflowを実装した。

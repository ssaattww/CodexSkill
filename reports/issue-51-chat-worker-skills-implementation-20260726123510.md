# Issue #51 ChatGPT Chat Worker Skill 実装レポート

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- Pull Request: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Base: `main`
- Report対象HEAD: `8fd4f58456720d8a75fef02c39b67fdf4e315629`
- Merge: 実施しない

## 概要

利用者が親として複数のChatGPT chatを起動する運用向けに、別workerを自動起動しないstandalone worker Skillを追加した。

追加したworkerは次の3つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`

Issue番号またはPR番号から取得できるrepository状態はworker自身がGitHub connectorで解決し、利用者へrepository URL、branch、HEAD SHA、report path、handoff pathを原則として再入力させない構成とした。

## 実装内容

### `chat-implementation-worker`

- 初回実装とreview follow-upを扱う
- 対象projectのProject Instructionに定義されたtesting policyへ従う
- 対象projectがTDDを要求しない場合、TDDを持ち込まない
- implementation reportとhandoffを別成果物として作成する
- PRを作成または更新し、簡易PR commentを投稿する
- review verdictを出さず、mergeしない

### `chat-review-worker`

- initial review、fix verification、cold final reviewを区別する
- current PR HEAD、linked Issue、changed files、過去report、handoff、review comment、HEAD固有CIを自己解決する
- product codeとtestを変更しない
- review reportとhandoffを別成果物として作成する
- 簡易PR commentを投稿し、mergeしない

### `chat-report-writer`

- PRまたはIssueからsource reportとhandoffを自己解決する
- implementation、review、verification、統合reportを扱う
- technical finding、test結果、CI結論を発明しない
- code/testを変更しない
- 指定report、handoff、簡易PR commentを出力し、mergeしない

### Shared handoff contract

`skills/chat-worker-shared/references/handoff-contract.md`を3 worker共通のsource of truthとした。

主な規則は次のとおりである。

- handoffはchat間の状態移送用であり、詳細reportの代替ではない
- repositoryへ保存できる場合は`reports/handoffs/`へ保存する
- PRまたはIssueから一意に特定できるpacketは、次workerがconnectorで自己解決する
- 利用者へpathまたはpacket本文を求めるのは、複数候補、repository外、またはrepository discovery不可の場合だけとする
- 前workerの権限を次chatへ自動継承しない
- testing orderとdevelopment methodは対象projectのProject Instructionから取得し、worker側からTDDを強制しない
- implementation workerとreview workerも、それぞれ必須reportを作成して`report` fieldへ記録する

## Project Instruction例

`design/chat-worker-skill-design.md`へ、RevMemでそのまま設定できるProject Instruction例を追加した。

含めた固定情報と運用規則は次のとおりである。

- 対象repository: `https://github.com/ssaattww/RevMem`
- task list: `tasks/tasks-status.md`
- Codex用Skill参照先: `https://github.com/ssaattww/CodexSkill`
- repository、Issue、PR、PR commentの操作にGitHub connectorを使用する
- RevMemのtest failure時に、テスト結果、標準出力、標準エラー、原因調査ログをartifactへ保存するworkflowを確認し、存在しなければ追加する
- RevMem実装ではTDDを基本とする
- 変更をレビュー可能な小さな論理単位でcommit/pushする
- 詳細reportとは別に簡易reportをPR commentへ投稿する
- PR作成または更新まで行い、mergeは利用者が行う
- current PR HEAD SHAと一致するworkflow runだけをCI確認へ使用する
- 一致するrunがない場合はCI未実施として扱い、別SHAのrunを代用しない

RevMem向けTDDと診断artifact workflowの方針はRevMemの実装にのみ適用し、参照先のCodexSkill repositoryには適用しないことを明記した。

## CodexSkill repositoryの非TDD方針

利用者指示に従い、CodexSkill repository自身にはTDDを適用していない。

- Red/Greenを作る目的のtestを先行追加していない
- この変更専用のcontract testを最終差分へ含めていない
- TDD用の専用workflowを最終差分へ含めていない
- 旧TDD方針を前提としたhandoff 2件、改訂実装report 5件、改訂review report 1件を最終差分から削除した
- Issue #51の実装方針と完了条件も、CodexSkill非TDD方針へ更新した
- 有効な自動検証がないため、設計書、3 Skill、handoff contract、Issue、PR説明の整合性reviewを検証方法とする

## 設計書

日本語設計書の正本は次の1ファイルへ集約した。

- `design/chat-worker-skill-design.md`

削除済みの重複設計書を同期対象とする旧記述も除去した。

## 最終差分の構成

Report対象HEAD時点のPR changed filesは7件である。

- `design/chat-worker-skill-design.md`
- `reports/issue-51-chat-worker-skills-implementation-20260726123510.md`
- `reports/issue-51-chat-worker-skills-review-20260726124000.md`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

既存Codex向けorchestrator、delegation、sub-agent Skillは変更していない。

## 検証

GitHub connectorでIssue、PR metadata、changed files、設計書、3 Skill、handoff contractを取得し、次を確認した。

- 3 workerが別workerを起動しない
- 3 workerが各自の必須reportとhandoffを分離して出力する
- implementation workerが対象projectのtesting policyへ従い、TDDを強制しない
- PRまたはIssueから一意に特定できるhandoffはworker自身が取得する
- RevMem向けTDD方針とCodexSkill非TDD方針が分離されている
- 設計書が1ファイルを正本としている
- merge禁止が全workerと設計書で一致している

Report対象HEAD `8fd4f58456720d8a75fef02c39b67fdf4e315629`について、GitHub connectorが返したworkflow runは0件、commit statusも0件であった。したがってCI successとは判定せず、CIは`not available`として扱う。

CodexSkill用のtestまたはworkflowは追加・実行していない。

## 未実施

- 本report更新後のcurrent PR HEADを対象とする独立review
- 実際の複数ChatGPT chatを用いたend-to-end operational trial

## マージ

マージは実施しない。

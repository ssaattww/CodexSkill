# Issue #51 ChatGPT Chat Worker Skill 実装レポート

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- Pull Request: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Base: `main`
- Report対象HEAD: `79c0997174b8b6a4ed65f68461c41a8e71bb3e09`
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
- code/testだけでなく、configuration、documentation、repository変更も対象にできる
- 対象projectのProject Instructionに定義されたimplementation/testing policyへ従う
- 対象projectがTDDを要求しない場合、TDDを持ち込まない
- implementation reportとhandoffを別成果物として作成する
- PRが存在する場合は簡易PR commentを必須成果物とし、投稿不能時は完成本文を返す
- review verdictを出さず、mergeしない

### `chat-review-worker`

- initial review、fix verification、cold final reviewを区別する
- current PR HEAD、linked Issue、changed files、過去report、handoff、review comment、HEAD固有CIを自己解決する
- cold final reviewは、実装・修正を行っていない新規chatだけで実行する
- 同じchatが実装または修正を行った場合はcold final reviewを名乗らない
- product codeとtestを変更しない
- review report、handoff、簡易PR commentを出力し、mergeしない

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
- code/testだけでなく、documentation、configuration、workflow、Issue、PR、branch操作を権限として表現できる

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

## Reviewで確認して修正した事項

### 1. Repository-backed handoffの取得経路

旧contractでは利用者が毎回pathを渡す運用が残っていた。PRまたはIssueから一意に特定できる場合は、次workerがconnectorで取得するよう修正した。

### 2. Worker reportとhandoffの責務

旧contractではimplementation workerとreview workerの`report` outcomeを`not_applicable`とする記述が残っていた。各workerが必須reportとhandoffを別成果物として作成する現行方針へ統一した。

### 3. Implementation workerの対象範囲とPR comment

code/test変更だけに見えるdescriptionを、documentation、configuration、repository変更も扱える表現へ修正した。PRが存在する場合の簡易PR commentも必須成果物へ統一した。

### 4. Cold final reviewの独立性

設計書だけでなく`chat-review-worker`本体にも、新規かつ非実装chatでのみcold final reviewを実施できる規則を追加した。

### 5. Handoffの権限表現

`edit_code`と`edit_tests`だけでは今回の設計書、configuration、workflow、Issue/PR操作を表現できなかったため、必要なactionを追加した。

## 最終差分の構成

Report対象HEAD時点のPR changed filesは7件である。

- `design/chat-worker-skill-design.md`
- `reports/issue-51-chat-worker-skills-implementation-20260726123510.md`
- `reports/issue-51-chat-worker-skills-review-20260726124000.md`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

既存Codex向けorchestrator、delegation、sub-agent Skillは変更していない。`main`に対してbehindは0、aheadは78 commitsである。

## 検証

GitHub connectorでIssue、PR metadata、changed files、設計書、3 Skill、handoff contract、既存hierarchy design、既存implementation/review/report Skillを取得し、次を確認した。

- 3 workerが別workerを起動しない
- 3 workerが各自の必須reportとhandoffを分離して出力する
- implementation workerが対象projectのtesting policyへ従い、TDDを強制しない
- PRまたはIssueから一意に特定できるhandoffはworker自身が取得する
- RevMem向けTDD方針とCodexSkill非TDD方針が分離されている
- cold final reviewの新規chat要件が設計書とSkillで一致している
- 設計書が1ファイルを正本としている
- merge禁止が全workerと設計書で一致している

Report対象HEAD `79c0997174b8b6a4ed65f68461c41a8e71bb3e09`について、GitHub connectorが返したworkflow runは0件、commit statusも0件であった。したがってCI successとは判定せず、CIは`not available`として扱う。

CodexSkill用のtestまたはworkflowは追加・実行していない。Markdown lintとSkill schema validationは実行環境がなく未実施である。

## Remaining risks

- 実際の複数ChatGPT chatを用いたend-to-end operational trialは未実施である
- machine-readable schema validationは未実施である
- PR branchには最終差分から削除した旧TDD試行を含む78 commitsの履歴が残る。通常mergeではその履歴がmainの祖先となり、squash mergeでは最終差分を1 commitとして取り込める

## マージ

マージは実施しない。

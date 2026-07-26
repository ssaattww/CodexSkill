# Issue #51 ChatGPT Chat Worker Skill 実装レポート

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- Pull Request: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Base: `main`
- Report対象HEAD: `e4f62751f5bf5783bfbd62bd6441152bb08b8c80`
- Base SHA: `f1ba3dbefe94dd7cc22eeed34149804c400b13cd`
- Ahead / Behind: ahead 88 / behind 0
- Merge: 実施しない

## 概要

利用者が親として複数のChatGPT chatを起動する運用向けに、別workerを自動起動しないstandalone worker Skillを追加した。

追加したSkillは次の3つである。

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
- PRが存在する場合は簡易PR commentを必須成果物とする
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

## ChatGPTへの登録構成

ChatGPTへ登録するSkill数は3つである。`chat-worker-shared`は4つ目のSkillとして登録しない。

各Skill packageを自己完結させるため、次の構成へ変更した。

```text
<skill-name>/
├─ SKILL.md
└─ references/
   └─ handoff-contract.md
```

追加したsupporting resourceは次の3ファイルである。

- `skills/chat-implementation-worker/references/handoff-contract.md`
- `skills/chat-review-worker/references/handoff-contract.md`
- `skills/chat-report-writer/references/handoff-contract.md`

各`SKILL.md`の参照先をpackage内の`references/handoff-contract.md`へ変更した。

`skills/chat-worker-shared/references/handoff-contract.md`をcanonical sourceとし、3つのpackage内copyはcanonical sourceとbyte-identicalにした。

Project InstructionはSkill packageとは別に対象Projectへ設定する。設計書とreportはruntime登録対象ではない。

## Codex reviewとの境界

ChatGPTのcold final reviewとCodexの標準reviewは別契約である。

- ChatGPTのcold final reviewは、新規かつ非実装chatで実施する
- Codexの`review-enforcer`は専用reviewer sub-agentを使用する
- Codexでは同一セッション内で原則として同じreviewer sub-agentをinitial reviewと再reviewで継続利用する
- Codex標準flowは新規ChatGPT chatのcold final reviewを要求しない
- Codexでfreshな独立最終reviewを必要とする場合は、Codex側のProject Instructionまたはreview要件へ別途明示する

## 設計書

次を更新した。

- `design/chat-worker-skill-design.md`
  - Codex reviewとChatGPT cold final reviewの差
  - ChatGPTへ登録する3 Skill packageの構成
  - package-local supporting resource
  - 完了条件
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
  - Codex flowとChatGPT chat worker flowの実行方式を分離
  - ChatGPT chat worker flowの呼び出し関係を追加
  - 3 Skillの役割と契約を追加
  - Codex reviewとの境界と登録構成を追加

2つのskill hierarchy designはbyte-identicalである。

## Project Instruction例

`design/chat-worker-skill-design.md`へ、RevMemでそのまま設定できるProject Instruction例を記載した。

含めた固定情報と運用規則は次のとおりである。

- 対象repository: `https://github.com/ssaattww/RevMem`
- task list: `tasks/tasks-status.md`
- Codex用Skill参照先: `https://github.com/ssaattww/CodexSkill`
- repository、Issue、PR、PR commentの操作にGitHub connectorを使用する
- RevMemのtest failure時に診断artifactを保存するworkflowを確認し、存在しなければ追加する
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
- 有効な自動検証がないため、設計書、Skill、handoff contract、Issue、PR説明の整合性reviewを検証方法とする

## Report対象HEADの差分

Report対象HEAD時点のPR changed filesは12件である。

- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `reports/issue-51-chat-worker-skills-implementation-20260726123510.md`
- `reports/issue-51-chat-worker-skills-review-20260726124000.md`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-implementation-worker/references/handoff-contract.md`
- `skills/chat-report-writer/SKILL.md`
- `skills/chat-report-writer/references/handoff-contract.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-review-worker/references/handoff-contract.md`
- `skills/chat-worker-shared/references/handoff-contract.md`
- `skills/design/skill-hierarchy-design.md`

既存Codex向けorchestrator、delegation、sub-agent Skillは変更していない。

## 検証

GitHub connectorでIssue、PR metadata、changed files、設計書、3 Skill、handoff contract、既存Codex review contractを取得し、次を確認した。

- 3 workerが別workerを起動しない
- 3 workerが各自の必須reportとhandoffを分離して出力する
- 3 Skill packageがpackage-localなhandoff contractを参照する
- canonical handoff contractと3つのpackage copyのblob SHAはすべて`fb0515ef32a72064f468a51c87348616afb944a2`で一致する
- 2つのskill hierarchy designのblob SHAはともに`a5485b384cfbc932edf1a4b610e0a03b84ee2a00`で一致する
- implementation workerが対象projectのtesting policyへ従い、TDDを強制しない
- RevMem向けTDD方針とCodexSkill非TDD方針が分離されている
- ChatGPT cold final reviewとCodex reviewの契約が分離されている
- merge禁止が全workerと設計書で一致している

Report対象HEAD `e4f62751f5bf5783bfbd62bd6441152bb08b8c80`に紐づくworkflow runは0件、commit statusも0件であった。CI successとは判定せず、CIは`not available`として扱う。

CodexSkill用のtestまたはworkflowは追加・実行していない。Markdown lintとSkill schema validationは利用可能な自動実行経路が確認できず未実施である。

## Remaining risks

- 実際の複数ChatGPT chatを用いたend-to-end operational trialは未実施である
- machine-readable schema validationは未実施である
- PR branchには最終差分から削除した旧TDD試行を含む履歴が残る。通常mergeでは中間commitがmainの祖先となり、squash mergeでは最終差分を1 commitとして取り込める

## マージ

マージは実施しない。

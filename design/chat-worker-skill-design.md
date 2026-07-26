# ChatGPT Chat Worker Skill Design

## 目的

この設計書は、利用者が親として複数のChatGPT chatを起動し、各chatへ独立したworker Skillを割り当てる構成を定義する。

ChatGPT chat同士は自動的にsub-agentとして連携しないため、利用者がchatの起動順序だけを管理する。一方、repository、Issue、PR、HEAD、report、handoff、CIなど、connectorで取得できる情報はworker自身が解決し、利用者へ入力を要求しない。

## 言語方針

- `SKILL.md`と実行contractは英語で記述する。
- 日本人利用者向け設計書は日本語で記述する。
- 実行規則はSkill、構成理由と利用例は設計書へ置く。

## 設計上の前提

### 利用者が親となるChatGPT chat worker flow

- 利用者はtask選択、chatの新規作成・継続、scope変更、merge判断を行う。
- workerは別workerを起動しない。
- workerはconnectorとrepositoryから取得できる情報を自分で探す。
- 各workerは成果物としてreportとhandoffを出力する。
- handoffは別chatへ自動共有されないが、PRやIssueから一意に辿れる場合は利用者がpathを指定する必要はない。

### 既存Codex向けskill hierarchyとは分離

既存Codex向けhierarchyは親agentがsub-agentを起動する。ChatGPT chat worker flowでは利用者が親であるため、Codex向けorchestratorやdelegation managerを流用しない。

本設計書と`skills/design/chat-worker-skill-design.md`はbyte-identicalに管理する。

## 切り出すSkill

| Skill | 責務 | 必須成果物 | 禁止事項 |
| --- | --- | --- | --- |
| `chat-implementation-worker` | 初回実装、review follow-up、validation | implementation report、handoff packet、PR簡易コメント | 独立review判定、scope拡張、merge |
| `chat-review-worker` | initial review、fix verification、cold final review | review report、handoff packet、PR簡易コメント | product code/test修正、finding対応実装、merge |
| `chat-report-writer` | report統合、再整形、最終report作成 | report、handoff packet、PR簡易コメント | technical findingの発明、code/test修正、merge |

## 全workerの成果物要件

全workerは成果物としてレポートを出力する。

- implementation workerはimplementation reportを出力する。
- review workerはreview reportを出力する。
- report writerは指定されたreportを出力する。
- handoff packetはchat間の状態移送用であり、reportの代替ではない。
- repositoryへwriteできる場合はreportを`reports/`、handoffを`reports/handoffs/`へ保存する。
- writeできない場合は完成したMarkdown本文を返す。
- failure、blocked、incompleteの場合もreportを省略しない。

## Project Instructionへ置く固定情報

全taskで共通する情報はProject Instructionへ置き、各chat promptでは再掲しない。

RevMemでは、利用者が提示した次の情報を固定前提とする。

- repository: `https://github.com/ssaattww/RevMem`
- task list: `tasks/tasks-status.md`
- reference Skill repository: `https://github.com/ssaattww/CodexSkill`
- repository accessはconnectorを使用する
- IssueとPRの作成・更新もconnectorで行う
- test failure時の診断artifact workflowを作業開始時に確認する
- Project InstructionでTDDが指定されているため、RevMem実装ではtestを先に作る
- 小さくcommit/pushする
- reportとは別にPRへ簡易コメントを残す
- PR作成・更新まで行い、mergeしない
- CIは自分のbranch HEAD SHAに紐づくworkflow runだけを見る

これらを毎回のpromptへ書かない。

CodexSkill repository自身のSkill Markdown変更には、TDD用contract testや専用workflowを導入しない。Markdown lintや有効な検証基盤がない状態で形式的なtestを追加しない。Skill変更は設計、差分確認、reviewで検証する。

## Workerが自分で解決する情報

workerはIssue番号またはPR番号から、次を自分で取得する。

- repositoryとProject Instruction
- task list上の対象task
- linked Issue、PR、branch、base
- current PR HEAD SHA
- changed filesと依存先
- applicable design
- applicable implementation/review reports
- applicable handoff packets
- review commentsと未解決finding
- current HEAD SHAに紐づくCI runとartifact
- report/handoffの保存先と命名規則

選択は単なる更新日時ではなく、task、PR、branch、mode、producer、対象HEAD、commit関係で行う。

PR番号だけで開始できることを標準とする。Issue番号だけで開始できることを標準とする。

利用者へHEAD SHAやhandoff pathを聞くのは、複数候補がありrepository情報だけでは一意に決められない場合だけとする。

## Chat promptに書く情報

通常、利用者が書くのは次の2点だけでよい。

- 対象IssueまたはPR
- 実施する作業またはreview mode

task固有の追加scope、通常方針と異なる制約、重点確認点がある場合だけ追記する。

プロジェクトInstructionを再掲しない。repository URL、branch、HEAD、handoff path、report path、connector、TDD、artifact、CI方針、merge禁止はworkerが自分で解決する。

## 標準flow

```text
利用者 [親]
├─ Chat A: implementation worker [新規]
├─ Chat B: initial review [新規]
├─ Chat A: review follow-up [継続]
├─ Chat C: fix verification [新規、またはChat B継続]
├─ Chat D: cold final review [必ず新規]
└─ Report chat [統合reportが必要な場合のみ]
```

## 利用者向け実行例

### Chat A: 初回実装

新規chatへ送るprompt:

```text
Issue #<issue-number>を開始してください。
```

task一覧から開始する場合:

```text
T<task-number>を開始してください。
```

workerはIssue、task list、branch、open PR、design、現在状態を自分で確認する。利用者はbranch名、HEAD、report path、handoff pathを入力しない。

完了時、workerはimplementation report、handoff、PR、HEAD SHA、CI結果を返す。

### Chat B: 初回レビュー

新規chatへ送るprompt:

```text
PR #<pr-number>を初回レビューしてください。
```

workerはcurrent PR HEAD、linked Issue、design、implementation report、handoff、changed files、CIを自分で取得する。

### Chat Aを継続: レビュー対応

初回実装chatへ戻り、次だけ送る。

```text
レビュー結果に対応してください。
```

workerは現在のPR、最新の適用可能なreview report、handoff、未解決findingを自分で特定する。

別のreview roundを明示する必要がある場合だけ次のように指定する。

```text
PR #<pr-number>の<review roundまたはcomment>に対応してください。
```

### Chat C: 修正確認

原則として新規chatへ送るprompt:

```text
PR #<pr-number>の修正確認をしてください。
```

workerはprevious reviewed HEAD、fix commits、review report、implementation follow-up report、handoffを自分で解決する。

Chat Bを継続する場合は次だけでよい。

```text
修正確認をしてください。
```

### Chat D: 独立最終レビュー

必ず新規chatへ送るprompt:

```text
PR #<pr-number>を独立レビューしてください。
```

workerはcurrent PR HEADを対象とし、過去reviewの結論を前提にせず確認する。必要な過去findingとregression evidenceは独立確認後に自分で取得する。

### Report chat

各workerがreportを出力するため通常は不要である。統合reportが必要な場合だけ新規chatを作成する。

```text
PR #<pr-number>の最終レポートを作成してください。
```

report writerはPRからsource reportsとhandoffsを自分で解決する。

## Handoff transport

handoff packetは自動共有memoryではない。

ただし、PR番号から一意に該当handoffを特定できる場合、利用者がpathを転記する必要はない。次chatのworkerがconnectorで探す。

利用者がhandoff pathまたはpacket本文を渡す必要があるのは次の場合だけである。

- repositoryへ保存できなかった
- 同一PRに同mode・同HEAD候補が複数あり一意に決められない
- repository外のhandoffを使用する
- 利用者が特定roundを明示的に選ぶ

## Worker境界

### Implementation worker

- Project Instructionに従って実装・test・validationを行う。
- implementation report、handoff、PR簡易コメントを出力する。
- review verdictは出さない。

### Review worker

- product code/testを変更しない。
- modeに応じたcoverageを実施する。
- review report、handoff、PR簡易コメントを出力する。

### Report writer

- source reportsとhandoffsを忠実に統合する。
-新しいtechnical findingを作らない。
- report、handoff、PR簡易コメントを出力する。

## Review lifecycle

1. `initial review`: planned coverageを最後まで確認する。
2. `fix verification`: previous findingsとfix impactを確認する。
3. `cold final review`: fresh chatでcurrent PR HEADを独立確認する。

別系統のBlocking/Highが繰り返し見つかる場合は`unstable`とし、設計見直しまたはPR分割へ戻す。

## 検証方針

CodexSkill内のMarkdown Skill変更に形式的なTDDを持ち込まない。

- 専用contract testを追加しない。
- 専用workflowを追加しない。
- Markdown lintが有効化されていない場合、lint成功を検証根拠にしない。
- 設計書、Skill、handoff contract、利用例の整合性をreviewで確認する。
- 将来、repository全体でMarkdown lintやSkill schema検証が正式導入された場合は、その既存基盤へ統合する。

## 完了条件

- 3 worker Skillが独立して利用できる
- 全workerがreportを必須成果物とする
- Issue番号またはPR番号だけで通常flowを開始できる
- workerがHEAD、handoff、report、CIを自分で解決する
- 利用者promptがtask固有情報だけに限定される
- CodexSkillへ形式的なTDD workflowを追加しない
- mergeは利用者が行う

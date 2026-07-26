# ChatGPT Chat Worker Skill Design

## 目的

この設計書は、利用者が親として複数のChatGPT chatを起動し、各chatへ独立したworker Skillを割り当てる構成を定義する。

ChatGPT chat同士は自動的にsub-agentとして連携しない。利用者はchatの起動順序とmerge判断を管理する。一方、repository、Issue、PR、HEAD、report、handoff、CIなど、connectorとrepositoryから取得できる情報はworker自身が解決し、利用者へ不要な再入力を求めない。

## 言語方針

- `SKILL.md`と実行contractは英語で記述する。
- 日本人利用者向け設計書は日本語で記述する。
- 実行規則はSkill、構成理由と利用例は本設計書へ置く。
- 本設計書の正本は`design/chat-worker-skill-design.md`の1ファイルとし、重複した設計書を作らない。

## 設計上の前提

### 利用者が親となるChatGPT chat worker flow

- 利用者はtask選択、chatの新規作成・継続、scope変更、merge判断を行う。
- workerは別workerを起動しない。
- workerはconnectorとrepositoryから取得できる情報を自分で探す。
- 各workerは成果物としてreportとhandoffを出力する。
- handoffは別chatへ自動共有されない。ただし、PRやIssueから一意に辿れる場合は、利用者がpathを転記する必要はない。

### 既存Codex向けskill hierarchyとの分離

既存Codex向けhierarchyは親agentがsub-agentを起動する。ChatGPT chat worker flowでは利用者が親であるため、Codex向けorchestratorやdelegation managerを流用しない。

## Codex実行とのreview契約の違い

ChatGPT chat worker flowの`cold final review`と、既存Codex flowのreviewは同じ契約ではない。

- ChatGPTの`cold final review`は、PRまたはreview fixを実装していない新規chatで実施する。
- Codexの標準flowは`review-enforcer`が専用reviewer sub-agentを起動し、同一セッションでは原則として同じreviewer sub-agentをinitial reviewと再reviewで継続利用する。
- Codexの標準flowは、新規ChatGPT chatを立ち上げることも、毎回別reviewerへ切り替えることも要求しない。
- Codex実行でfreshな独立最終reviewを追加する場合は、Codex側のProject Instructionまたはreview要件へ明示する。ChatGPT向け`cold final review`契約はCodexへ自動適用しない。
- Codexでfresh reviewを要求する場合も、実行単位は新規ChatGPT chatではなく、履歴継承を制限した新しいreviewer sub-agentなど、Codex側の実行方式で定義する。

## 切り出すSkill

| Skill | 責務 | 必須成果物 | 禁止事項 |
| --- | --- | --- | --- |
| `chat-implementation-worker` | 初回実装、review follow-up、validation | implementation report、handoff packet、PR簡易コメント | 独立review判定、scope拡張、merge |
| `chat-review-worker` | initial review、fix verification、cold final review | review report、handoff packet、PR簡易コメント | product code/test修正、finding対応実装、merge |
| `chat-report-writer` | report統合、再整形、最終report作成 | 指定report、handoff packet、PR簡易コメント | technical findingの発明、code/test修正、merge |

## ChatGPTへのSkill登録構成

ChatGPTへ登録するSkillは次の3つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`

`chat-worker-shared`は4つ目のSkillとして登録しない。`skills/chat-worker-shared/references/handoff-contract.md`をcanonical sourceとし、各Skill packageへ`references/handoff-contract.md`として同梱するsupporting resourceである。

各Skill packageは、少なくとも次を含む。

```text
<skill-name>/
├─ SKILL.md
└─ references/
   └─ handoff-contract.md
```

- ChatGPTへ登録する数は3 Skillでよい。
- 3つの`SKILL.md`だけを取り出して登録する構成では、相対参照先のhandoff contractが欠けるため不十分である。
- 各package内の`references/handoff-contract.md`はcanonical sourceとbyte-identicalに保つ。
- Project InstructionはSkillとは別に対象Projectへ設定する。
- `design/chat-worker-skill-design.md`と`reports/`配下のreportはruntime登録対象ではない。
- ChatGPTとCodexのSkill登録状態は別管理とし、使用する実行面へそれぞれ登録する。

## 全workerの成果物要件

- implementation workerはimplementation reportを出力する。
- review workerはreview reportを出力する。
- report writerは指定されたreportを出力する。
- handoff packetはchat間の状態移送用であり、reportの代替ではない。
- repositoryへwriteできる場合はreportを`reports/`、handoffを`reports/handoffs/`へ保存する。
- writeできない場合は、完成したMarkdown本文を返す。
- failure、blocked、incompleteの場合もreportを省略しない。

## Project Instructionへ置く固定情報

全taskで共通する情報はProject Instructionへ置き、各chat promptでは再掲しない。

### RevMem向けProject Instruction例

以下は、RevMemで使用する固定情報と運用規則を、Project Instructionへそのまま設定できる形に整理した例である。

```text
対象リポジトリ:
https://github.com/ssaattww/RevMem

タスク一覧:
tasks/tasks-status.md

Codex用Skillの参照リポジトリ:
https://github.com/ssaattww/CodexSkill

必要な作業手順やSkillの構成は、この参照リポジトリを確認してください。

リポジトリの参照・更新、IssueとPRの作成・更新、PRコメントの投稿にはGitHub connectorを使用してください。

作業開始時に、テスト失敗時の原因調査に必要な情報をartifactとして保存するworkflowが存在するか確認してください。存在しない場合は、対象workflowへ追加してください。artifactには、少なくともテスト結果、標準出力、標準エラー、および失敗原因の調査に必要なログを含めてください。

実装はTDDを基本とし、先にテストを追加して失敗を確認してから実装してください。このTDD方針と診断artifact workflowの追加方針は、対象リポジトリであるRevMemの実装作業に適用します。参照先であるCodexSkillリポジトリの変更には適用しません。

変更は、レビュー可能な小さな論理単位でcommit/pushしてください。

作業完了時は、詳細reportをrepositoryへ保存してください。それとは別に、変更内容と検証結果を要約した簡易reportをPRコメントへ投稿してください。

PRの作成または既存PRの更新まで行ってください。mergeは利用者が行うため、workerはmergeしないでください。

並行開発中の別branchのrunを誤認しないでください。「最新のworkflow run」ではなく、対象PRのhead branchのcurrent HEAD SHAを取得し、runのhead SHAが一致するworkflow runだけをCI確認の対象としてください。HEADが更新された場合は、更新後のHEAD SHAに紐づくrunを改めて確認してください。一致するrunが存在しない場合は、CI未実施として報告し、別SHAのrunを代用しないでください。
```

この例に含まれるrepository URL、task list、参照Skill、connector、RevMem向けTDD、artifact、commit/push、report、PR、CI、mergeの各方針はtask共通の固定情報である。これらを毎回のchat promptへ書かない。

### CodexSkill repository自身の開発方針

CodexSkill repository自身にはTDDを適用しない。

- Red/Greenを作る目的のtestを先行追加しない。
- CodexSkillの変更専用のcontract testやTDD用workflowを追加しない。
- 既存のlint、schema validation、Skill validationなどが存在する場合は通常の検証として実行できるが、TDDの証跡として扱わない。
- 有効な自動検証が存在しない場合は、設計書、Skill、handoff contract、利用例、変更差分の整合性をreviewで確認する。
- 利用先プロジェクトのProject InstructionにTDDが書かれていても、その方針を参照先のCodexSkillへ持ち込まない。

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

PR番号だけ、またはIssue番号だけで通常flowを開始できることを標準とする。利用者へHEAD SHAやhandoff pathを聞くのは、複数候補がありrepository情報だけでは一意に決められない場合だけとする。

## Chat promptに書く情報

通常、利用者が書くのは次の2点だけでよい。

- 対象IssueまたはPR
- 実施する作業またはreview mode

task固有の追加scope、通常方針と異なる制約、重点確認点がある場合だけ追記する。

Project Instructionにあるrepository URL、branch、HEAD、handoff path、report path、connector、testing policy、artifact、CI方針、merge禁止はworkerが自分で解決する。

## 標準flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [新規、initial implementation]
├─ Chat B: chat-review-worker [新規、initial review]
├─ Chat A: chat-implementation-worker [継続、review follow-up]
├─ Chat C: chat-review-worker [原則新規、fix verification]
├─ Chat D: chat-review-worker [必ず新規かつ非実装chat、cold final review]
└─ Report chat: chat-report-writer [統合reportが必要な場合のみ]
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

workerは現在のPR、適用可能なreview report、handoff、未解決findingを自分で特定する。

別のreview roundを明示する必要がある場合だけ、次のように指定する。

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

workerはcurrent PR HEADを対象とし、過去reviewの結論を前提にせず確認する。必要な過去findingとregression evidenceは、独立確認後に自分で取得する。

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
- Project InstructionがTDDを要求しないrepositoryへ、TDDを持ち込まない。
- implementation report、handoff、PR簡易コメントを出力する。
- review verdictは出さない。

### Review worker

- product code/testを変更しない。
- modeに応じたcoverageを実施する。
- review report、handoff、PR簡易コメントを出力する。

### Report writer

- source reportsとhandoffsを忠実に統合する。
- 新しいtechnical findingを作らない。
- report、handoff、PR簡易コメントを出力する。

## Review lifecycle

1. `initial review`: planned coverageを最後まで確認する。
2. `fix verification`: previous findingsとfix impactを確認する。
3. `cold final review`: ChatGPT chat worker flowでのみ、新規かつ非実装chatからcurrent PR HEADを独立確認する。

別系統のBlocking/Highが繰り返し見つかる場合は`unstable`とし、設計見直しまたはPR分割へ戻す。

## 検証方針

- 対象repositoryのProject Instructionと既存検証基盤に従う。
- CodexSkill repository自身にはTDDを適用しない。
- CodexSkillの変更専用にtestやworkflowを新設しない。
- 既存の自動検証がある場合は実行し、存在しない場合は`unsupported`または`not available`として明記する。
- CIを確認する場合は、current PR HEAD SHAに紐づくrunだけを使用する。
- CI runが存在しないことをsuccessとして扱わない。
- 設計書、Skill、handoff contract、利用例、PR説明の整合性をreviewで確認する。

## 完了条件

- 3 worker Skill packageが独立して利用できる
- 各Skill packageに`SKILL.md`と`references/handoff-contract.md`が同梱されている
- `chat-worker-shared`を4つ目のSkillとして登録しない
- Codex標準reviewとChatGPTのcold final reviewの違いが明記されている
- 全workerがreportを必須成果物とする
- Issue番号またはPR番号だけで通常flowを開始できる
- workerがHEAD、handoff、report、CIを自分で解決する
- 利用者promptがtask固有情報だけに限定される
- RevMem向けTDD方針とCodexSkillの非TDD方針が明確に分離されている
- CodexSkillへTDD用testまたは専用workflowを追加しない
- mergeは利用者が行う

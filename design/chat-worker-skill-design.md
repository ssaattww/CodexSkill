# ChatGPT Chat Worker Skill Design

## 目的

この設計書は、利用者が親として複数のChatGPT chatを起動し、各chatへ独立したworker Skillを割り当てる構成を定義する。

ChatGPTの通常chatでは、あるchatが別chatをsub-agentとして自動起動することを前提にできない。一方、各chatはrepositoryを読み書きし、Markdown report、handoff packet、PR commentを配置できる。したがって、自動orchestrationではなく、利用者がchat間の順序と情報伝達を管理する。

## 言語方針

- `SKILL.md`は原則として英語で記述する。
- Skillが直接参照する実行contractも、可搬性を優先して英語で記述する。
- 日本人利用者向けの設計書は日本語で記述する。
- Skill内には実行に必要な規則だけを置き、構成理由や設計判断は本設計書へ置く。

## 設計上の前提

### 利用者が親となるChatGPT chat worker flow

- 利用者がrepository、branch、task順序、権限、次に起動するchatを決める。
- 各chatは1つのworker roleだけを担当する。
- workerは別workerを起動しない。
- 利用者だけがscope変更、次chat起動、finding採用、mergeを決定する。
- 各workerは前chatの会話履歴を参照できるとは仮定しない。

### 既存Codex向けskill hierarchyとは分離

既存のCodex向けhierarchyは親agentがsub-agentを起動する実行契約を持つ。ChatGPT chat worker flowは利用者が親であるため、同じorchestratorやdelegation managerを流用しない。

本設計書と`skills/design/chat-worker-skill-design.md`をChatGPT向け構成の正本としてbyte-identicalに管理する。既存Codex向けSkillの実行契約は変更しない。

## 切り出すSkill

| Skill | 責務 | 主なwrite対象 | 禁止事項 |
| --- | --- | --- | --- |
| `chat-implementation-worker` | 決定済みtaskのtest-first実装とreview follow-up | code、test、commit、handoff packet | narrative report、独立review判定、scope拡張、merge |
| `chat-review-worker` | initial review、fix verification、cold final review | review report、PR comment、handoff packet | product code/test修正、finding対応実装、merge |
| `chat-report-writer` | handoff evidenceからreportと簡易PR commentを生成 | report、PR comment、handoff packet | finding・severity・test結果の発明、code/test修正、merge |

3 Skillは`skills/chat-worker-shared/references/handoff-contract.md`を共通contractとして使用する。

## 切り出さないSkill

### Chat orchestrator

利用者が親としてchat生成、順序、停止、handoff採用を担当するため切り出さない。

### Delegation manager

workerは別workerへ委譲せず、自分に割り当てられた作業を直接実行するため切り出さない。

### Verification worker

初期構成では切り出さない。implementation時のvalidationはimplementation worker、review evidenceの検証はreview worker、verification reportはreport writerが担当する。独立したenvironment verificationが反復的に必要になった場合だけ後続Issueで検討する。

### Git workflow manager

branch作成、PR作成、mergeを一括管理するChatGPT用Skillは設けない。各workerは利用者から明示的に許可された操作だけを行い、mergeは利用者が行う。

## Handoff packetの意味

handoff packetは、chat間で渡す**payload**であり、ChatGPTが自動的に共有するmemoryではない。

前chatが完了時にpacketを出力しただけでは、別chatから自動的には参照できない。次chatへ渡すには、利用者が次のいずれかを行う必要がある。

1. repositoryへpacketを保存し、そのpathまたはGitHub URLを次chatへ渡す
2. packet全文をcopy and pasteして次chatへ渡す

「前chatが出力したので次chatも読める」という想定は禁止する。

## Handoff transport

### Repository-backed transport

repositoryへのwriteが許可されている場合の標準経路とする。

- packetは`reports/handoffs/`へ保存する。
- filenameは原則として`<task-id>-<producer>-<mode>-<head-short>-<timestamp>.md`とする。
- Markdown内にcanonical YAML packetをfenced blockとして保持する。
- workerは作成したpathを`handoff_transport.packet_path`へ記録する。
- 利用者は次chatへpathまたはGitHub URLを渡す。
- 次chatはconnectorでそのfileを読み、前会話を推測しない。

handoff fileは作業結果を運ぶ構造化evidenceであり、narrative reportではない。したがってimplementation workerがhandoff fileを作成しても、report writerの責務を侵害しない。

### Copy and paste transport

`write_handoff`が許可されていない場合、workerは最終応答へpacket全文を出力する。利用者はその全文を次chatへ貼り付ける。要約だけでは再開に必要な情報が欠けるため、transportとして扱わない。

## 権限contract

- top-levelの`authorized_actions`と`write_boundary`は現在workerへ利用者が付与した権限である。
- `write_handoff`は`reports/handoffs/`へのpacket保存権限を表す。
- `next_chat_input.requested_authorized_actions`は次chatに必要と考える権限の提案であり、付与ではない。
- 次chatは前workerの権限を自動継承しない。
- 利用者が次chat用のtop-level権限を改めて付与する。

## Portability bundle

### Implementation bundle

- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

### Review bundle

- `skills/chat-review-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

### Report bundle

- `skills/chat-report-writer/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

`report-output-manager`は利用可能なら使用できるが、各bundleの必須依存にはしない。

## 標準flow

```text
利用者 [親]
├─ implementation chat
│  └─ chat-implementation-worker
│     └─ reports/handoffs/... または packet全文
├─ report chat [必要な場合]
│  └─ chat-report-writer
├─ review chat
│  └─ chat-review-worker [initial review]
├─ implementation chat
│  └─ chat-implementation-worker [review follow-up]
├─ review chat
│  └─ chat-review-worker [fix verification]
├─ review chat [medium/high riskの場合]
│  └─ chat-review-worker [cold final review]
└─ report chat [必要な場合]
   └─ chat-report-writer
```

各矢印の間で、利用者がhandoff path、URL、またはpacket全文を次chatへ渡す。

## 利用者向け実行例

ここでは、Issue対応を実装し、初回レビュー、レビュー対応、修正確認、独立最終レビューまで行う標準例を示す。

### Chatの使い分け

| Chat | 用途 | 新規・継続 | 理由 |
| --- | --- | --- | --- |
| Chat A | 初回実装とレビュー対応 | 初回実装時に新規作成し、レビュー対応でも同じchatを継続 | 実装時の設計判断、Red/Green、変更履歴を保持したまま修正できるため |
| Chat B | 初回レビュー | 新規作成 | 実装chatの意図や自己評価に引きずられないため |
| Chat C | 修正確認 | 原則として新規作成 | 実装chatと分離し、修正diffと前回findingに限定して確認するため |
| Chat D | 独立最終レビュー | 必ず新規作成 | 過去reviewの結論にanchoringされず、最終HEADをfreshに確認するため |
| Report chat | report整形のみ | 必要な場合だけ新規作成 | technical判断とpresentation責務を分離するため |

Chat Bを修正確認にも再利用することは許容する。ただし、独立最終レビューはChat BまたはChat Cを継続せず、必ずChat Dとして新規作成する。

### 1. Chat A: 初回実装

新規chatを作成し、`chat-implementation-worker`を割り当てる。

#### 新規chatへ送るprompt

```text
chat-implementation-workerとして作業してください。

Repository: <owner/repository>
Issue: #<issue-number>
Branch: <working-branch>
Base: <base-branch>

Issue、repository指示、設計書を確認し、scope内だけをTDDで実装してください。
作業開始時に、テスト失敗時の原因調査に必要なstdout、stderr、environment、test result、対象sourceをartifactへ保存するworkflowが存在するか確認し、なければ先に追加してください。

許可する操作:
- repository read
- code/test/workflow edit
- commit/push
- PR create/update
- reports/handoffs/へのhandoff保存

禁止:
- scope外変更
- 他PRの変更を上書きすること
- merge

完了時はcanonical handoff packetをreports/handoffs/へ保存し、そのhandoff path、最終HEAD SHA、CI run IDを返してください。
```

Chat Aが完了したら、利用者は次を確認する。

- PRが作成または更新されている
- handoff pathが返されている
- handoff内のbranch、HEAD SHA、scope、remaining riskが妥当である
- 対象HEAD SHAに紐づくCI結果が記録されている

### 2. Chat B: 初回レビュー

Chat Aとは別の新規chatを作成し、`chat-review-worker`の`initial review`を割り当てる。

#### 新規chatへ送るprompt

```text
chat-review-workerとしてinitial reviewを実施してください。

Repository: <owner/repository>
PR: #<pr-number>
Review target HEAD: <implementation-head-sha>
Implementation handoff path: <reports/handoffs/...>

GitHub connectorでPR、Issue、設計書、handoff packet、全変更file、変更contractの直接依存先を確認してください。
BlockingまたはHighを見つけてもそこで中断せず、planned coverageを最後まで完了してからfindingsを一括報告してください。

許可する操作:
- repository/PR read
- review report作成
- PR review comment投稿
- reports/handoffs/へのreview handoff保存

禁止:
- product code/testの変更
- finding対応実装
- merge

詳細review reportをrepositoryへ配置し、PRへ簡易コメントを投稿してください。
完了時はreview handoff path、対象HEAD SHA、verdict、findings、unexplored、next actionを返してください。
```

Chat Bが`fail`を返した場合、利用者はreview handoff pathをChat Aへ戻す。

### 3. Chat Aを継続: レビュー対応

初回実装を行った既存のChat Aへ戻る。新規chatは作らない。

#### 既存chatへ送るprompt

```text
レビュー結果へ対応してください。

Review handoff path: <reports/handoffs/...>
Review report path: <reports/...review...md>
Current target branch: <working-branch>
Reviewed HEAD: <review-target-head-sha>

chat-implementation-workerのreview follow-upとして、前回findingを再現するtestを先に追加または強化し、finding、修正diff、直接影響、同種欠陥だけをscopeとして対応してください。
前回と無関係な改善は混ぜないでください。

修正後は対象branch HEADに紐づくCIだけを確認し、implementation handoffを新しくreports/handoffs/へ保存してください。
PRは更新してください。mergeはしないでください。
```

レビュー対応が複数回必要な場合も、原則としてChat Aを継続する。Chat Aのcontextが破損した、対象branchやtaskが変わった、またはhandoffだけで安全に再開できることを確認した場合だけ、新しいimplementation chatへ切り替える。

### 4. Chat C: 修正確認

レビュー対応後はreview用chatを使用する。独立性を高める標準例では、新規のChat Cを作成する。

#### 新規chatへ送るprompt

```text
chat-review-workerとしてfix verificationを実施してください。

Repository: <owner/repository>
PR: #<pr-number>
Previous review handoff path: <reports/handoffs/...initial-review...>
Fix implementation handoff path: <reports/handoffs/...review-follow-up...>
Previous reviewed HEAD: <old-head-sha>
Current fix HEAD: <new-head-sha>

前回findingsがcodeとtestの両方で解消されたか確認してください。
確認範囲は、前回finding、修正diff、直接影響範囲、同種欠陥のsibling case、過去regression testの保持に限定してください。
前回と無関係な未探索領域へ無制限に範囲を広げないでください。

許可する操作:
- repository/PR read
- fix verification report作成
- PR comment投稿
- reports/handoffs/へのreview handoff保存

禁止:
- product code/testの変更
- finding対応実装
- merge

対象fix HEADに紐づくCIを確認し、verdictとhandoff pathを返してください。
```

fix verificationで、修正由来の新規Blocking/Highが出た場合はChat Aへ戻す。前回と別系統のBlocking/Highが繰り返し出る場合は、追加reviewを続けず`unstable`として設計見直しまたはPR分割へ戻す。

### 5. Chat D: 独立最終レビュー

medium/high riskの変更、state・identity・persistence・parser・atomicity・外部processなどを扱う変更では、fix verification通過後に新規のChat Dを作成する。

Chat Dには、最初から過去findingの詳細を強調しすぎない。まずIssue、設計書、最終diff、最終HEAD、risk profileを使って独立確認させる。過去handoffは、独立確認後のregression照合に使用させる。

#### 新規chatへ送るprompt

```text
chat-review-workerとしてcold final reviewを実施してください。

Repository: <owner/repository>
PR: #<pr-number>
Final target HEAD: <final-head-sha>
Issue: #<issue-number>
Authoritative design: <design-path>
Final implementation handoff path: <reports/handoffs/...>
Fix verification handoff path: <reports/handoffs/...>

このchatは独立最終レビュー専用です。過去review chatの結論を前提にせず、Issue、設計書、final diff、変更contractの依存先、risk profileから最終HEADをfreshに確認してください。
独立確認が完了した後で、過去findingのregression testが保持されているか照合してください。

許可する操作:
- repository/PR read
- final review report作成
- PR comment投稿
- reports/handoffs/へのfinal review handoff保存

禁止:
- product code/testの変更
- finding対応実装
- merge

Blocking/Highがなく、required coverageがdisposition済みで、final HEADに紐づくCIが成功している場合だけpass候補としてください。
別系統のBlocking/Highが再び見つかった場合はunstableとして、設計見直しまたはPR分割を返してください。
```

### 6. Pass後の利用者判断

Chat Dが`pass`または`pass_with_held`を返した場合、利用者は次を確認してから自分でmergeする。

- final reviewの対象HEAD SHAと現在のPR HEADが一致する
- final HEADに紐づくCIが成功している
- Blocking/Highが0件である
- held、unexplored、remaining riskを受容できる
- review後に新しいcommitが追加されていない

final review後にcode、test、workflow、設計書へcommitが追加された場合、そのcommitを対象とするfix verificationまたはcold final reviewをやり直す。単なるPR commentやreport追加だけでproduct behaviorとvalidation evidenceが変わらない場合は、変更内容を確認したうえで再review要否を判断する。

### Report chatを使う場合

worker自身が詳細reportを配置済みなら、通常は別report chatを作る必要はない。複数handoffを統合したい、repository固有templateへ再整形したい、または最終reportと簡易PR commentを一括生成したい場合だけ新規chatを作る。

#### 新規chatへ送るprompt

```text
chat-report-writerとしてreport-only作業をしてください。

Repository: <owner/repository>
PR: #<pr-number>
Source handoff paths:
- <implementation handoff path>
- <initial review handoff path>
- <fix verification handoff path>
- <cold final review handoff path>

入力handoffの事実だけを使用し、finding、severity、test結果、CI結論を追加または変更しないでください。
詳細Markdown reportを指定pathへ配置し、PRへ簡易コメントを投稿してください。
code/testは変更せず、mergeもしないでください。
```

## Worker境界

### Implementation worker

- test-firstでcode/testを変更する。
- Red、Green、commit、HEAD、riskをhandoffへ記録する。
- narrative reportとreview verdictを作成しない。
- `write_handoff`があればpacketを保存する。

### Review worker

- product code/testを変更しない。
- initial review、fix verification、cold final reviewを区別する。
- initial reviewはfinding発見後もplanned coverageを完了する。
- fix verificationはfinding、修正diff、直接影響、同種欠陥へ限定する。
- 別系統のBlocking/Highが反復する場合は`unstable`とし、追加reviewではなく設計見直しまたはPR分割へ戻す。

### Report writer

- source packetを忠実にMarkdownへ変換する。
- finding、severity、test結果、CI結論を新しく作らない。
- code/testを変更しない。

## Review lifecycle

1. `initial review`: required coverageを最後まで実施し、findingsを一括報告する。
2. `fix verification`: previous findings、修正影響、同種欠陥だけを確認する。
3. `cold final review`: medium/high riskの場合にfresh chatで1回実施する。

新しいBlocking/Highが別系統で反復する場合は`unstable`とする。review回数を無制限に増やさない。

## Report配置

Markdown report配置はChatGPT chatでも可能である。

- implementation workerはnarrative reportを作らない。
- review workerは許可された場合にreview reportを配置できる。
- report writerはimplementation、review、verification reportを配置できる。
- handoff packetはreportとは別に`reports/handoffs/`へ配置できる。

## Failure handling

- 必須input不足は推測しない。
- implementationは`blocked`、reviewは`incomplete`、reportは`blocked`とする。
- failure時は原因調査に必要なstdout、stderr、environment、source、test、configuration、generated output、test result artifactを保存または参照する。
- CIは対象branchのpacket `head_sha`に紐づくrunだけを使用する。

## Validation contract

CIで次を検証する。

- 3つのworker `SKILL.md`が英語で記述されている
- 2つの設計書が日本語でbyte-identicalである
- 各workerが利用者を親とし、別workerを起動しない
- agent orchestration依存を持たない
- 全workerが共通handoff contractを参照する
- `write_handoff`と`reports/handoffs/`によるdurable transportが定義される
- packet出力だけでは別chatから自動参照できないことが明記される
- copy and paste fallbackが定義される
- initial implementation、initial review、review follow-up、fix verification、cold final reviewの利用者向けprompt例がある
- 新規chatと既存chatを使い分ける時点が明記される
- review停止条件とrole boundaryが定義される

## 完了条件

- 3 worker Skillとshared contractが存在する
- Skillは英語、設計書は日本語である
- repository-backed transportとcopy/paste transportが実装契約に含まれる
- 利用者が親として次chatへpacketを明示的に渡す
- 利用者が新規chatと既存chatの使い分け、および各promptを設計書だけで判断できる
- contract testがGreenである
- failure diagnostics workflowが存在する
- implementation report、review report、PR commentが残る
- mergeは利用者が行う

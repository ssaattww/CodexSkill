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
- review停止条件とrole boundaryが定義される

## 完了条件

- 3 worker Skillとshared contractが存在する
- Skillは英語、設計書は日本語である
- repository-backed transportとcopy/paste transportが実装契約に含まれる
- 利用者が親として次chatへpacketを明示的に渡す
- contract testがGreenである
- failure diagnostics workflowが存在する
- implementation report、review report、PR commentが残る
- mergeは利用者が行う

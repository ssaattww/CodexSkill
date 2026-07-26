# ChatGPT Chat Worker Skill Design

## 目的

この設計書は、利用者が親として複数のChatGPT chatを起動し、各chatへ独立したworker Skillを割り当てる構成を定義する。

ChatGPTの通常chatでは、あるchatが別chatをsub-agentとして自動起動することを前提にできない。そのため、利用者がchatの起動順序、handoff、scope、権限、merge判断を管理する。

## 言語方針

- `SKILL.md`は原則として英語で記述する。
- Skillが直接参照する実行contractも英語で記述する。
- 日本人利用者向けの設計書は日本語で記述する。
- 実行規則はSkill、構成理由と運用例は設計書へ置く。

## 設計上の前提

### 利用者が親となるChatGPT chat worker flow

- 利用者がrepository、branch、task順序、次chat、scope変更、mergeを決める。
- 各chatは1つのworker roleだけを担当する。
- workerは別workerを起動しない。
- 各workerは前chatの会話履歴を参照できるとは仮定しない。
- handoff packetは利用者が次chatへ明示的に渡す。

### 既存Codex向けskill hierarchyとは分離

既存のCodex向けhierarchyは親agentがsub-agentを起動する。ChatGPT chat worker flowでは利用者が親であるため、Codex向けorchestratorやdelegation managerを流用しない。

本設計書と`skills/design/chat-worker-skill-design.md`はbyte-identicalに管理する。

## 切り出すSkill

| Skill | 責務 | 必須成果物 | 禁止事項 |
| --- | --- | --- | --- |
| `chat-implementation-worker` | test-first実装、review follow-up、validation | implementation report、handoff packet | 独立review判定、scope拡張、merge |
| `chat-review-worker` | initial review、fix verification、cold final review | review report、handoff packet、簡易PR comment | product code/test修正、finding対応実装、merge |
| `chat-report-writer` | 複数handoffの統合、再整形、最終report作成 | report、handoff packet、簡易PR comment | technical findingの発明、code/test修正、merge |

3 Skillは`skills/chat-worker-shared/references/handoff-contract.md`を共通contractとして使用する。

## 全workerの成果物要件

全workerは成果物としてレポートを出力する。

- implementation workerはimplementation reportを出力する。
- review workerはreview reportを出力する。
- report writerは指定されたreportを出力する。
- handoff packetはchat間移送用であり、レポートの代替ではない。
- repositoryへwriteできる場合は`reports/`へ保存する。
- writeできない場合は完成したMarkdown本文を返す。
- 失敗またはblockedの場合も、原因、未確認事項、次actionを含むreportを出力する。

## Handoff packetの意味

handoff packetはchat間で渡すpayloadであり、自動共有memoryではない。

前chatがpacketを出力しただけでは、別chatから自動的には参照できない。利用者は次のいずれかで渡す。

1. `reports/handoffs/`へ保存し、pathまたはGitHub URLを次chatへ渡す
2. packet全文をcopy and pasteする

要約だけはhandoffとして扱わない。

## Project Instructionへ置く固定情報

次のような全task共通の方針はプロジェクトInstructionへ置く。

- repository URL
- task一覧や設計書の配置場所
- GitHub connectorを使うこと
- TDDを基本とすること
- test failure時に診断artifactを保存すること
- 小さくcommit/pushすること
- reportを`reports/`へ保存すること
- handoffを`reports/handoffs/`へ保存すること
- PRへ簡易コメントを残すこと
- CIは自branchのHEAD SHAに紐づくrunだけを見ること
- mergeしないこと
- `SKILL.md`は英語、設計書は日本語とすること
- scope外変更を行わないこと

各chat promptでは、プロジェクトInstructionを再掲しない。

## Chat promptに書く情報

chat promptには、そのchatだけで変化する情報だけを書く。

- worker Skill名またはmode
- IssueまたはPR番号
- 対象branchまたはHEAD SHA
- handoff path
- 今回だけ追加するscope、制約、重点確認点

repository URL、TDD、artifact、report、connector、merge禁止など、Project Instructionにある情報は原則として繰り返さない。

例外は次の場合だけである。

- 今回だけ通常方針と異なる権限またはscopeを与える
- Project Instructionとtask固有条件が衝突する
- 対象HEAD SHAやhandoff pathなど、今回固有の識別子が必要

## 標準flow

```text
利用者 [親]
├─ Chat A: implementation worker [新規]
├─ Chat B: initial review [新規]
├─ Chat A: review follow-up [継続]
├─ Chat C: fix verification [新規、またはChat B継続]
├─ Chat D: cold final review [必ず新規]
└─ Report chat [必要時のみ新規]
```

## 利用者向け実行例

### Chatの使い分け

| Chat | 用途 | 新規・継続 |
| --- | --- | --- |
| Chat A | 初回実装とレビュー対応 | 初回実装時に新規作成し、レビュー対応でも継続 |
| Chat B | 初回レビュー | 新規作成 |
| Chat C | 修正確認 | 原則新規作成。Chat B継続も許容 |
| Chat D | 独立最終レビュー | 必ず新規作成 |
| Report chat | 複数handoff統合または再整形 | 必要な場合だけ新規作成 |

### 1. Chat A: 初回実装

新規chatへ送るprompt:

```text
chat-implementation-workerとしてIssue #<issue-number>を実装してください。
Branch: <working-branch>
Mode: initial implementation
```

必要な場合だけ追記する。

```text
今回の追加scope: <task固有scope>
今回だけの制約: <task固有constraint>
```

完了時に確認するもの:

- implementation report path
- implementation handoff path
- PR番号
- final HEAD SHA
- HEAD SHAに紐づくCI run

### 2. Chat B: 初回レビュー

新規chatへ送るprompt:

```text
chat-review-workerとしてPR #<pr-number>のinitial reviewを実施してください。
Review target HEAD: <implementation-head-sha>
Implementation handoff: <reports/handoffs/...>
```

必要な場合だけ重点項目を追加する。

```text
重点確認: <state / parser / identity / atomicity / performance など>
```

完了時に確認するもの:

- review report path
- review handoff path
- verdict
- findings
- unexplored

### 3. Chat Aを継続: レビュー対応

既存chatへ送るprompt:

```text
レビュー結果へ対応してください。
Mode: review follow-up
Review handoff: <reports/handoffs/...>
Review report: <reports/...review...md>
```

Chat Aは既にProject Instruction、Issue、branch、実装contextを持つため、それらを再掲しない。

完了時に確認するもの:

- review follow-up implementation report path
- new implementation handoff path
- new HEAD SHA
- new HEAD SHAに紐づくCI run

### 4. Chat C: 修正確認

原則として新規chatへ送るprompt:

```text
chat-review-workerとしてPR #<pr-number>のfix verificationを実施してください。
Previous review handoff: <reports/handoffs/...initial-review...>
Fix implementation handoff: <reports/handoffs/...review-follow-up...>
Current fix HEAD: <new-head-sha>
```

確認範囲はSkill側で、previous findings、修正diff、直接影響、同種欠陥、regression保持へ限定される。promptで毎回説明しない。

### 5. Chat D: 独立最終レビュー

必ず新規chatへ送るprompt:

```text
chat-review-workerとしてPR #<pr-number>のcold final reviewを実施してください。
Final target HEAD: <final-head-sha>
Final implementation handoff: <reports/handoffs/...>
Fix verification handoff: <reports/handoffs/...>
```

独立性を守るため、過去review chatは継続しない。

### 6. Report chatを使う場合

各workerが自分のreportを出力するため、通常は不要である。複数reportの統合、最終report作成、repository固有templateへの再整形が必要な場合だけ使う。

新規chatへ送るprompt:

```text
chat-report-writerとしてPR #<pr-number>の最終reportを作成してください。
Source handoffs:
- <implementation handoff>
- <initial review handoff>
- <fix verification handoff>
- <cold final review handoff>
```

## Worker境界

### Implementation worker

- code/testをtest-firstで変更する。
- validationを実施する。
- implementation reportを必ず作成する。
- handoff packetを作成する。
- review verdictは出さない。

### Review worker

- product code/testを変更しない。
- review modeに応じたcoverageを実施する。
- review reportを必ず作成する。
- PRへ簡易コメントを投稿する。
- handoff packetを作成する。

### Report writer

- source packetとsource reportを忠実に統合する。
- 新しいtechnical findingを作らない。
- code/testを変更しない。
- 指定reportと簡易PR commentを作成する。

## Review lifecycle

1. `initial review`: planned coverageを最後まで確認する。
2. `fix verification`: previous findingsと修正影響だけを確認する。
3. `cold final review`: fresh chatで最終HEADを独立確認する。

別系統のBlocking/Highが繰り返し見つかる場合は`unstable`とし、設計見直しまたはPR分割へ戻す。

## Failure handling

- implementation failureでもimplementation reportを出力する。
- review incompleteでもreview reportを出力する。
- report生成blockedでもblocked reportを返す。
- test failure時は原因調査に必要なartifactを保存する。
- CIは対象HEAD SHAに紐づくrunだけを使用する。

## Validation contract

CIで次を検証する。

- 3つのworker `SKILL.md`が英語である
- 2つの設計書が日本語でbyte-identicalである
- 全workerがreportを必須成果物とする
- implementation workerがimplementation reportを作成する
- handoff packetがreportの代替ではない
- Project Instructionへ固定情報を置く
- chat promptがtask固有情報だけを含む
- 新規chatと既存chatの使い分けが明記される
- review停止条件が定義される

## 完了条件

- 3 worker Skillとshared contractが存在する
- 全workerが成果物reportを出力する
- repository-backed transportとcopy/paste transportが定義される
- 利用者が新規chatと継続chatの使い分けを判断できる
- prompt例がProject Instructionを重複して再掲しない
- contract testがGreenである
- failure diagnostics workflowが存在する
- mergeは利用者が行う

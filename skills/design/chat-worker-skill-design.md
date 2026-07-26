# ChatGPT Chat Worker Skill Design

## 目的

この設計書は、利用者が親として複数のChatGPT chatを起動し、各chatへ独立した作業を割り当てるworker Skill構成を定義する。

対象環境では、1つのchatから別のagentを自動起動できない。一方で、各chatはrepositoryを直接確認し、許可された範囲でfile編集、test実行、Markdown report配置、GitHub操作を行える。

## 設計上の前提

### 利用者が親となるChatGPT chat worker flow

- 利用者がtaskの順序、repository、branch、次に起動するchatを決める。
- 各chatは1つのworker roleだけを担当する。
- workerは別workerを起動しない。
- chat間の状態は会話履歴ではなく、共通handoff packetで渡す。
- 利用者はhandoffのscope、HEAD SHA、finding、unknown、next actionを確認する。
- 利用者だけがscope変更、次chatの起動、finding採用、mergeを決定する。
- Markdown reportはChatGPT chatからrepositoryへ配置できる。

### 既存Codex向けskill hierarchyとは分離

既存の`design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`は、Codexの親agentと委譲実行を前提とする正本である。

ChatGPT chat worker flowは実行主体と制御境界が異なるため、既存hierarchyへ混在させない。この設計書と`skills/design/chat-worker-skill-design.md`をChatGPT向け構成の正本としてbyte-identicalに管理する。

既存Codex向けSkillの実行契約は変更しない。

## 切り出すSkill

初期構成では次の3つを切り出す。

| Skill | 責務 | write対象 | 禁止事項 |
| --- | --- | --- | --- |
| `chat-implementation-worker` | 決定済みtaskのtest-first実装とreview follow-up | code、test、許可されたbranch、implementation handoff | narrative report、独立review判定、scope拡張、merge |
| `chat-review-worker` | initial、fix verification、cold final review | review handoff、許可されたreview reportとPR comment | product code/test修正、finding対応実装、merge |
| `chat-report-writer` | handoffからMarkdown reportと簡易PR commentを生成 | 許可されたreport fileとPR comment | technical findingやtest結果の発明、code/test修正、merge |

3 Skillは`skills/chat-worker-shared/references/handoff-contract.md`を共通contractとして使用する。

## なぜこの3 Skillを切り出すか

### Implementation worker

Implementation chatはrepositoryへwriteし、test-firstのRedとGreenを作る。Review chatと同じcontextで実行すると、自分の実装意図に引きずられ、独立reviewにならない。

実装とvalidationは同じworkerへまとめる。validationだけを常に別chatへ分離すると、細かな修正ごとのhandoffが増え、利用者の親作業が過剰になるためである。

Implementation workerは実装専任とし、narrative reportを作成しない。作業事実は構造化handoffへ記録し、report writerへ渡す。

### Review worker

ChatGPT chatでは親agentがreviewerを自動起動できないため、利用者が別chatをreviewerとして明示起動する。

Review workerは実装を行わず、次の3 modeを持つ。

- `initial review`: planned coverageを最後まで確認し、findingを一括報告する
- `fix verification`: 前回finding、修正diff、直接影響、同種欠陥だけを確認する
- `cold final review`: fresh contextで最終HEADを1回確認する

Review reportはreview evidenceの一部として、利用者が`write_report`を許可した場合に同じchatから配置できる。別report chatへhandoffしてもよい。

### Report writer

Report作成はtechnical判断ではなく、確定済みevidenceの構造化と配置である。

Report writerを独立させる理由は次のとおり。

- implementation workerを実装専任に保つ
- 複数handoffを統合する
- repository固有templateへ整形する
- 詳細reportと簡易PR commentを同時に作る
- 長い作業chatからpresentation責務を除く

Report writerは入力handoffを忠実に転記し、新しいfinding、severity、test結果、CI結論を作らない。

## 切り出さないSkill

### Chat orchestrator

切り出さない。利用者が親であり、chatの生成、順序、停止、handoff採用を担当するためである。

自動orchestratorをSkill化しても、別chatを起動できない環境では実行できず、実態と異なる契約になる。

### Delegation manager

切り出さない。workerは委譲せず、受け取った作業を直接実行する。

### Verification worker

初期構成では切り出さない。

- implementation verificationは`chat-implementation-worker`が担当する
- review evidence verificationは`chat-review-worker`が担当する
- verification reportは`chat-report-writer`が作成する

大規模なenvironment verificationが独立責務として繰り返し必要になった場合だけ、後続Issueで`chat-verification-worker`を検討する。

### Task plannerとdesign worker

初期構成では切り出さない。

Workerへ渡すtaskは、利用者側でscope、non-goals、authoritative requirementsが決定済みであることを前提にする。要件分解や設計作成を別chatで行う場合も、この3 Workerの必須依存にはしない。

### Git workflow manager

切り出さない。

各workerはhandoffの`authorized_actions`と`write_boundary`で許可されたcommit、push、report、PR commentだけを実施する。branch作成、PR作成、mergeなどの全体Git flowは利用者が管理する。

## Portability bundle

各Skillを別のChatGPT環境へ移す場合は、次の単位で配置する。

### Implementation bundle

- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

### Review bundle

- `skills/chat-review-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

### Report bundle

- `skills/chat-report-writer/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`

`report-output-manager`が利用可能ならpath、filename、template規則を参照できるが、standalone report workerの必須依存にはしない。

## 標準flow

```text
利用者 [親]
├─ implementation chat
│  └─ chat-implementation-worker [initial implementation]
│     └─ implementation handoff
├─ report chat
│  └─ chat-report-writer [implementation report]
├─ review chat
│  └─ chat-review-worker [initial review]
│     └─ review handoff / review report
├─ implementation chat
│  └─ chat-implementation-worker [review follow-up]
│     └─ implementation handoff
├─ review chat
│  └─ chat-review-worker [fix verification]
│     └─ review handoff / review report
├─ review chat [medium/high riskの場合]
│  └─ chat-review-worker [cold final review]
│     └─ final review handoff / review report
└─ report chat
   └─ chat-report-writer
      ├─ consolidated Markdown report
      └─ concise PR comment
```

利用者は不要なreport chatを省略できる。ただしimplementation workerへnarrative report作成を兼務させない。

## Chat間contract

全workerは`schema_version: 1`のhandoff packetを使用する。

主要fieldは次のとおり。

- task、Issue、PR identifier
- repository、branch、base ref、HEAD SHA
- `authorized_actions`、`write_boundary`
- scope、non-goals、authoritative requirements
- changedまたはinspected files
- commands、tests、CI、artifacts
- implementation outcome
- review mode、coverage、verdict
- report type、source packets、path、comment、outcome
- findings、held、unexplored、remaining risks
- unknown、not applicable
- next action、next chat input

詳細は`skills/chat-worker-shared/references/handoff-contract.md`を唯一の正本とする。

## Role boundary

### Implementation worker

Input:

- 決定済みtask packet
- `authorized_actions`と`write_boundary`
- test-first対象behavior
- validation要件
- review follow-up時は前回finding

Output:

- code/test変更
- Red/Green evidence
- commitsとHEAD SHA
- implementation handoff

Completion:

- scope内の実装が完了またはblocked理由が明示されている
- test-first evidenceまたは対象外理由がある
- validationとremaining riskが記録されている
- narrative reportとreview verdictを作っていない

### Review worker

Input:

- review mode
- PR、branch、base、HEAD
- requirements、design、scope
- `authorized_actions`と`write_boundary`
- changed files、risk profile、previous findings

Output:

- coverage disposition
- findings、held、unexplored
- target HEAD固有のevidence
- review verdictとhandoff
- 許可された場合はreview reportとPR comment

Completion:

- modeに応じたcoverageが完了している
- findingまたはno findingsが明示されている
- verdictとstop reasonがある
- product code/testを変更していない

### Report writer

Input:

- implementation、review、verification handoff
- report type
- `authorized_actions`と`write_boundary`
- report pathまたはnaming context
- PR comment要否

Output:

- Markdown reportまたは配置可能な完成本文
- concise PR commentまたは投稿可能な本文
- `report` fieldを含むhandoff

Completion:

- source handoffとreportの事実が一致する
- unknownとnot applicableが保持されている
- technical判断を追加していない
- code/testを変更していない

## Review lifecycle

Review回数は無制限に増やさない。

1. `initial review`
   - required coverageを最後まで実施する
   - findingを見つけてもplanned coverageを中断しない
2. `fix verification`
   - previous findingsと修正影響だけを確認する
   - unrelatedな未探索領域へ無制限に拡張しない
3. `cold final review`
   - medium/high riskの場合にfresh chatで1回実施する
   - 新規Blocking/Highがなければmerge可能候補とする

別系統のBlocking/Highが繰り返す場合は`unstable`とし、次actionを`design_rework`または`split_pr`にする。

## Report配置

Markdown report配置はChatGPT chatでも実行可能である。

- implementation workerはnarrative reportを作成せず、handoffだけを返す
- review workerは`write_report`が許可された場合にreview reportを配置できる
- report writerはimplementation、review、verification reportを配置できる
- repository固有のpath、filename、templateがある場合はそれを優先する
- write権限がない場合は配置可能な完成Markdown本文を返す

## Failure handling

- 必須input不足は推測せず、implementationは`blocked`、reviewは`incomplete`、reportは`blocked`とする
- access不能、CI未完了、artifact不足は`unknown`または`unexplored`へ記録する
- failure時はstdout、stderr、environment、source、test、config、generated output、test result artifactを保存または参照する
- CIはhandoffのHEAD SHAに紐づくrunだけを使用する
- workflowは対象branch HEADをcheckoutしてactual SHAと照合する
- workerはfailureを隠してreport上のpassへ変換しない

## Scope protection

- 各workerはassigned scopeだけを扱う
- `authorized_actions`にない操作を行わない
- `write_boundary`外を変更しない
- 他taskや他PRの所有範囲を勝手に変更しない
- unrelated changeをrevertしない
- worker自身がmergeしない

## Validation contract

通常CIで次を検証する。

- 3つのworker Skillが存在する
- 各SkillがYAML frontmatter、name、descriptionを持つ
- 各Skillが利用者を親と定義する
- 各Skillが別workerを起動しない
- agent orchestration依存を持たない
- 3 Skillが同じhandoff contractを参照する
- implementation、review、reportのrole boundaryが明記される
- shared contractがwrite権限とreport outputを表現する
- 2つのChatGPT向けdesign fileがbyte-identicalである
- workflowが対象branch HEAD SHAそのものをcheckoutして検証する

Failure時はstdout、stderr、environment、test、対象Skill、design file、HEAD情報をdiagnostics artifactへ保存する。

## 完了条件

- 3つのworker Skillが独立して利用できる
- shared handoff contractだけで次chatが再開できる
- 利用者が親であることが全Skillで一貫している
- implementation、review、reportのwrite boundaryが分離されている
- 既存Codex向けSkillを変更していない
- 2つのChatGPT向けdesign fileがbyte-identicalである
- contract testとbranch HEAD固有CIがGreenである

---
name: chat-report-writer
description: Convert implementation, review, or verification handoff evidence into a Markdown report and concise PR comment in one ChatGPT chat when the user coordinates the workflow as the parent. Use for report-only work without code edits, new technical findings, or nested worker dispatch.
---

# Chat Report Writer

## Goal

implementation、review、verificationのhandoffを事実どおりにMarkdown reportまたは簡易PR commentへ変換する。

## Execution model

- 利用者が親として、入力handoff、report type、repository、配置先、PR投稿要否を指定する。
- このchatはreport writerとして直接作業し、別workerを起動しない。
- 前のchat履歴を前提にせず、渡されたhandoff packetと参照可能なrepository evidenceだけを使用する。
- codeまたはtestを変更しない。
- reportの入力と出力は[shared handoff contract](../chat-worker-shared/references/handoff-contract.md)に従う。

## Inputs

作業開始前に次を確認する。

- report type: `implementation report`、`review report`、`verification report`、`concise PR comment`
- 1つ以上のhandoff packet
- task、Issue、PR identifier
- repository、branch、base ref、HEAD SHA
- `authorized_actions`と`write_boundary`
- report path、filename policy、template
- report本文の言語
- PR commentを投稿する場合は対象PR
- 入力handoffに含まれるcommands、tests、CI、artifact、finding、held、unexplored、risk
- 既存reportを更新するのか、新規reportを作るのか

入力handoffが不足している場合は、値を推測せず`unknown`として明示する。`write_report`または`comment_pr`が許可されていない場合はfileやPRへ書き込まず、配置可能な完成本文を返す。

## Report modes

### implementation report

implementation handoffから次を整理する。

- task scopeとnon-goals
- test-firstのRedとGreen
- code/test変更
- commandsとvalidation
- commitと最終HEAD SHA
- failure artifact
- remaining risksと次action

Review verdictや新しいfindingを追加しない。

### review report

review handoffから次を整理する。

- review modeと対象HEAD SHA
- requirements、scope、changed/dependent files
- selected coverageとdisposition
- severity順のfindingsまたは明示的なno findings
- held、unexplored、remaining risks
- CI evidenceとverdict
- 次のimplementation、design rework、PR split

Findingのseverity、location、impact、verdictを変更しない。

### verification report

verification evidenceから次を整理する。

- verification対象
- commands、tests、environment
- HEAD SHA、CI run、jobs、artifacts
- passed、failed、blocked、not run
- 未確認領域とremaining risk

成功していないcheckを成功として書かない。

### concise PR comment

詳細reportを省略せず別途保持したうえで、PR conversationへ次を短く投稿する。

- 対応またはreviewの目的
- 主な変更またはfinding
- 対象HEAD SHA
- CI runと結論
- report path
- next action
- mergeしていないこと

## Required flow

1. handoff packetのschema、producer、mode、task、repository、HEAD SHAを確認する。
2. `authorized_actions`と`write_boundary`を確認し、許可されたreport pathとPR操作だけを確定する。
3. report typeと使用するpacketを確定する。
4. 入力packet内の事実と、必要ならrepository上のHEAD、run、artifactを照合する。
5. report pathが未指定なら、利用可能な場合は既存`report-output-manager`のpath、filename、template規則を参照する。
6. report typeに対応するsectionへevidenceを転記する。
7. 値が不足しているfieldは`unknown`、非該当は理由付き`not_applicable`として書く。
8. finding、test結果、CI結論、HEAD SHA、artifact IDが入力packetと一致するか再確認する。
9. Markdown reportを指定pathへ作成または更新する。write権限がなければ完成本文を返す。
10. PR commentが要求され、`comment_pr`が許可されている場合だけ、reportを省略しない簡易summaryを投稿する。
11. `report.report_type`、`report.outcome`、`report.source_packets`、`report.paths`、`report.pr_comments`を埋める。
12. 作成したpath、投稿先、転記したevidence、残るunknownを[shared handoff contract](../chat-worker-shared/references/handoff-contract.md)で返す。

## Evidence fidelity rules

- 入力にない成功、失敗、finding、severity、原因、修正内容を追加せず、事実を発明しない。
- 曖昧な表現を確定事実へ変えない。
- `in_progress`のCIを`success`と書かない。
- repositoryの最新runではなく、handoffの`head_sha`に紐づくrunだけを最終evidenceとして記載する。
- failure artifactがある場合はID、name、確認した原因を区別して書く。
- held、unexplored、unknownを省略して見かけ上のpassへ変えない。
- review verdictはreview workerのpacketから転記し、report writer自身では決定しない。
- implementation outcomeはimplementation workerのpacketから転記し、report writer自身では決定しない。

## Write boundary

- codeまたはtestを変更しない。
- fixture、workflow、設定、設計書をreport都合で変更しない。
- implementationを開始しない。
- reviewを再実行せず、新しいtechnical findingを作らない。
- report fileと、利用者が指定したPR commentだけをwrite対象とする。
- `authorized_actions`にない操作を行わない。
- mergeしない。

## Report structure

最低限、次を含める。

- taskとreport metadata
- repository、branch、base、対象HEAD SHA
- scopeとnon-goals
- authoritative requirements
- changedまたはinspected files
- commands、tests、CI、artifacts
- implementation outcomeまたはreview verdict
- findingsまたは明示的なno findings
- held、unexplored、unknown、not applicable
- remaining risks
- next action
- report作成者が新しいtechnical判断を追加していないこと

## Outputs

次を返す。

- 作成または更新したMarkdown report path
- report typeと`report.outcome`
- 入力に使用した`report.source_packets`
- reportへ転記したHEAD SHA、CI run、artifact、finding
- 投稿した場合は`report.pr_comments`の投稿先
- 入力不足として残した`unknown`
- report作成後の`next_action`
- [shared handoff contract](../chat-worker-shared/references/handoff-contract.md)準拠のpacket

## Completion condition

このSkillは次をすべて満たしたときだけ完了する。

- report typeとsource handoffが明示されている
- reportの事実がsource handoffと一致している
- unknown、not applicable、held、unexploredが必要に応じて残されている
- Markdown reportが指定pathへ配置されるか、配置可能な完成本文が返されている
- PR commentを要求された場合、詳細reportへの参照を含む簡易commentが投稿されるか、権限不足として本文が返されている
- `report` fieldがsource packet、path、comment、outcomeを表している
- 事実を発明しないまま、codeまたはtestを変更しない
- mergeしない

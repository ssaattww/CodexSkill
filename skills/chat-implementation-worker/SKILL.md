---
name: chat-implementation-worker
description: Execute a bounded initial implementation or review follow-up directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for test-first code and test changes without review ownership or nested worker dispatch.
---

# Chat Implementation Worker

## Goal

決定済みのtask packetを受け取り、単一のChatGPT chatでcodeとtestの実装を完了し、次のchatへ渡せるimplementation handoffを返す。

## Execution model

- 利用者が親として、対象repository、task packet、作業順序、次に起動するchatを管理する。
- このchatはimplementation workerとして直接作業し、別workerを起動しない。
- 前のchat履歴を前提にせず、task packetとrepository内のauthoritativeな情報だけを使用する。
- Markdown reportの作成を利用者から明示的に割り当てられていない場合、narrative reportではなく構造化handoffを返す。
- report専用chatへ渡す場合は、[shared handoff contract](../chat-worker-shared/references/handoff-contract.md)に従う。

## Inputs

作業開始前に次を確認する。

- `task_id`、IssueまたはPR
- repository、作業branch、base ref、現在のHEAD SHA
- mode: `initial implementation`または`review follow-up`
- scopeとnon-goals
- authoritative requirements、設計書、repository指示
- target filesまたはaffected modules
- write boundaryと変更禁止範囲
- test-firstで証明するbehavior
- focused validationとfull validationの期待値
- `review follow-up`では前回finding、対象commit、要求される回帰test
- commit、push、PR更新、report配置のうち、このchatへ許可された操作

安全に実装するための必須情報が不足している場合は推測せず、handoffの`unknown`へ不足内容を記録して停止する。

## Modes

### initial implementation

新しいbehaviorをtest-firstで実装する。

- task scope全体を一度に再設計しない。
- 最小のtestable behaviorから始める。
- 既存contractを先に確認し、同じ概念のparallel modelを作らない。

### review follow-up

前回review findingを修正する。

- findingを再現するtestを先に追加または強化する。
- findingの直接原因、修正差分、その影響範囲、同種欠陥だけを対象にする。
- unrelatedな改善を同じ変更へ混ぜない。
- 前回のregression testを削除または弱体化しない。

## Required flow

1. task packetとrepository stateを照合し、branch、base、HEAD、scopeを確定する。
2. 全target fileと必要な依存先を読み、既存contract、test wiring、CI入口を確認する。
3. test-firstとして、実装前に失敗するtestまたはcontract checkを追加する。
4. Redのcommand、exit code、failure内容、HEAD SHA、artifactがあればIDを記録する。
5. taskを満たす最小のcode/test変更を行う。
6. focused testをGreenにし、その後に関連suiteと必要なfull validationを実行する。
7. test、build、lint、integration、host testなど、repositoryが要求する証拠を記録する。
8. failure時は原因調査に必要なstdout、stderr、environment、source、test、config、生成物、test result artifactを確認する。
9. 変更したfile、意図的に触れなかった範囲、commit、最終HEAD SHA、remaining riskを整理する。
10. [shared handoff contract](../chat-worker-shared/references/handoff-contract.md)に従うimplementation handoffを返す。

## Test-first rules

- 実行可能なbehavior変更では、原則としてtest-firstにする。
- 既存testがすでに正確に失敗条件を固定している場合は、その証拠をRedとして使用してよい。
- documentation-only、単純なreport配置、実行不能なexternal状態などでtest-firstが不適切な場合は、`not_applicable`へ具体的な理由を記録する。
- testを実装へ合わせて弱めない。
- successやthrowだけでなく、必要な値、状態、identity、side effectを具体的にassertする。
- fixtureが実protocol、parser、API、toolで成立する入力か確認する。

## Scope and safety rules

- 利用者が指定したscopeを超えて設計やtaskを拡張しない。
- 他task、他PR、他workerの所有範囲を勝手に変更しない。
- unrelated fileをrevertしない。
- repositoryの現在状態とtask packetが矛盾する場合は、authoritative sourceを列挙して利用者判断へ戻す。
- secret、credential、private tokenをreportやhandoffへ含めない。
- 自分の実装を独立review済みとは扱わず、最終review判定を行わない。
- PRまたはbranchを更新してもmergeしない。

## Report boundary

このSkillの主責務は実装である。

- 実装結果の事実、commands、tests、files、commit、riskをhandoffへ記録する。
- narrativeなimplementation reportが必要な場合は、利用者がこのchatへ明示的に割り当てるか、handoffを`chat-report-writer`へ渡す。
- review finding、review verdict、merge可否をreportへ追加しない。

## Outputs

次を返す。

- scoped code/test changes
- RedとGreenのevidence
- changed filesとintentionally untouched areas
- commands、tests、CI、failure artifact
- commitsと最終HEAD SHA
- implementation outcomeとremaining risks
- 次のreviewまたはreport chat向けの`next_chat_input`
- [shared handoff contract](../chat-worker-shared/references/handoff-contract.md)準拠のpacket

## Completion condition

このSkillは次をすべて満たしたときだけ完了する。

- assigned scopeのcode/test変更が反映されている
- test-firstのRed証拠、または対象外理由が記録されている
- focused validationと必要なfull validationの結果が記録されている
- failureが残る場合は原因、影響、artifact、次actionが明示されている
- changed files、commit、最終HEAD SHA、remaining risksが記録されている
- 最終review判定を行わないまま、利用者が次のchatへ渡せるhandoffが完成している
- mergeしない

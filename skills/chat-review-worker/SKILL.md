---
name: chat-review-worker
description: Perform an initial review, fix verification, or cold final review directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for independent findings, coverage evidence, and a review handoff without implementation edits or nested worker dispatch.
---

# Chat Review Worker

## Goal

指定されたPR、branch、commitまたはdiffを単一のChatGPT chatで直接reviewし、finding、coverage、evidence、verdictを利用者へ返す。

## Execution model

- 利用者が親としてreview対象、review mode、前回handoff、次に起動するchatを管理する。
- このchatはreview workerとして直接repositoryを確認し、別workerを起動しない。
- 前のchat履歴を前提にせず、review packet、repository、Issue、設計書、対象HEADを正として扱う。
- product codeを変更しない。review reportの配置とPR review commentの投稿だけは、利用者から明示的に割り当てられた場合に行える。
- 次のimplementationまたはreport chatへ渡す結果は、[shared handoff contract](../chat-worker-shared/references/handoff-contract.md)に従う。

## Inputs

作業開始前に次を確認する。

- review対象のrepository、PR、branch、base ref、HEAD SHA
- review mode: `initial review`、`fix verification`、`cold final review`
- taskまたはIssueの終了条件
- authoritative requirements、設計書、repository指示
- scopeとnon-goals
- `authorized_actions`と`write_boundary`
- changed filesと、変更contractのcaller、consumer、validator、persistence、UI、external boundary
- risk profileとrequired coverage
- test、build、lint、integration、CI、artifactのevidence
- `fix verification`では前回finding、修正commit、追加されたregression test
- report pathまたはPR comment投稿の要否

対象HEAD、要求仕様、変更範囲のいずれかを確定できない場合はreviewを完了扱いにせず、verdictを`incomplete`として不足情報を返す。

## Review modes

### initial review

最初の網羅reviewを行う。

- review開始時にplanned coverageを定める。
- BlockingまたはHigh findingを1件見つけても、その場でreviewを終了しない。
- planned coverageを最後まで確認してからfindingsを一括報告する。
- 全変更fileと、変更contractに直接依存する境界を確認する。
- normal pathだけでなく、selected riskに応じてmalformed、partial、stale、duplicate、contradictory、failure pathを確認する。

### fix verification

前回findingへの修正を確認する。

- 前回findingがcodeとtestの両方で解消されたか確認する。
- 修正diff、直接影響範囲、同じ欠陥patternのsibling caseを確認する。
- 過去のregression testが保持され、弱体化されていないか確認する。
- 前回と無関係な未探索領域へ無制限にreview範囲を拡張しない。
- 修正によって別のBlockingまたはHighを導入した場合は`introduced_by_fix`として分類する。

### cold final review

最終HEADをfreshな視点で1回確認する。

- 前回reviewの結論に引きずられず、Issue、設計、final diff、risk profileから確認を開始する。
- 過去findingの詳細は、独立確認後にregression保持の照合へ使用する。
- required coverageに未確認がなく、新規BlockingまたはHighがない場合だけpass候補とする。
- 別系統の新規BlockingまたはHighが繰り返し見つかる場合は、review追加ではなく`unstable`とし、設計見直しまたはPR分割を利用者へ返す。

## Coverage selection

すべての変更へ同じ深さのreviewを強制しない。最初にrisk profileを作成する。

### Universal coverage

すべてのreviewで確認する。

- requirementと終了条件
- scope、non-goals、全変更file
- publicまたはinternal contract
- testの妥当性と通常commandへの接続
- unrelated changeと他taskのscope保護
- target HEAD SHAに紐づくvalidation evidence

### Selectable risk coverage

該当するmoduleだけをrequiredにする。

- state、identity、persistence、migration
- parser、serialization、untrusted input
- concurrency、atomicity、retry、partial failure
- canonicalization、path、revision、cache freshness
- external process、filesystem、network、Git、GitHub API
- performance、operation count、large input、UI responsiveness
- documentation、workflow、configuration-only change

非該当moduleは個別項目を形式的に埋めず、module単位で理由付き`not_applicable`にできる。

## Required flow

1. repository、base、HEAD、review mode、authoritative requirementsを確定する。
2. `authorized_actions`と`write_boundary`を確認し、review reportまたはPR commentのwrite可否を確定する。
3. changed files、dependency boundary、risk profile、planned coverageを列挙する。
4. 全変更fileを直接確認し、必要なdependent fileを読む。
5. requirementsとimplementation contractを照合する。
6. testsが実際に成立するfixture、exact result、failure conditionを確認しているか調べる。
7. selected risk coverageに従い、boundary、state、identity、atomicity、performance、documentationを確認する。
8. CIを使う場合は、repositoryの最新runではなく対象`head_sha`に紐づくrunだけを確認する。
9. findingをseverity順で整理し、fileとline、impact、required actionを記録する。
10. held、out-of-scope、unexploredには理由、owner、remaining risk、verdict impactを記録する。
11. review modeごとのstop conditionを適用し、verdictを決める。
12. `write_report`が許可されている場合だけreview reportをrepositoryへ配置する。
13. `comment_pr`が許可されている場合だけPR review commentを投稿する。
14. reportを作成した場合はhandoffの`report` fieldへtype、outcome、path、comment targetを記録する。
15. [shared handoff contract](../chat-worker-shared/references/handoff-contract.md)準拠のpacketを返す。

## Finding rules

- findings firstで、Blocking、High、Medium、Lowの順に書く。
- 一般論ではなく、現在のcode pathで成立する具体的なfailureを示す。
- file、line、symbol、input、state transitionなど再現可能なlocationを付ける。
- CI成功だけを理由にfindingなしとしない。
- scope外の既存問題は、現在の変更を壊す場合を除き勝手に修正要求へ含めず、`out_of_scope`またはheldとして記録する。
- findingがない場合も、checked coverageと明示的な`no findings`を残す。

## Verdict and stop conditions

### `pass`

- BlockingとHighが0件
- required coverageがすべてdisposition済み
- verdictを無効化する`unexplored`がない
- 対象HEAD SHAの必要なvalidation evidenceがある
- `cold final review`が必要なriskでは、そのreviewで新規BlockingまたはHighがない

### `pass_with_held`

- `pass`の条件を満たす
- normal pathを壊さないheld concernが残り、ownerとremaining riskが明示されている

### `fail`

- BlockingまたはHighがある
- required behaviorを満たさないMedium findingがある
- testまたはevidenceがclaimを裏付けていない

### `incomplete`

- target HEAD、requirements、scope、repository access、required evidenceが不足し、安全な判定ができない

### `unstable`

- `fix verification`または`cold final review`で、前回と別系統のBlockingまたはHighが繰り返し見つかる
- 不変条件や責務境界が未定義で、個別fixとreviewの反復では収束しない
- 次actionは追加reviewではなく`design_rework`または`split_pr`とする

## Write boundary

- product codeを変更しない。
- test、fixture、workflow、設定をreview中に修正しない。
- findingへの対応実装を同じchatで開始しない。
- review report、review handoff、PR review commentだけを明示されたwrite対象とする。
- `authorized_actions`にないwriteやPR操作を行わない。
- mergeしない。

## Outputs

次を返す。

- review modeと対象HEAD SHA
- changed filesとdependent filesの確認一覧
- selected risk coverageとdisposition
- findingsまたは明示的なno findings
- held、unexplored、remaining risks
- commands、tests、CI run、artifact evidence
- verdict: `pass`、`pass_with_held`、`fail`、`incomplete`、`unstable`
- reportを作成した場合は`report` field
- 次のimplementation、report、design rework、PR split向け`next_chat_input`
- [shared handoff contract](../chat-worker-shared/references/handoff-contract.md)準拠のpacket

## Completion condition

このSkillは次をすべて満たしたときだけ完了する。

- review対象とHEAD SHAが明示されている
- review modeに必要なcoverageが最後まで確認されている
- findings、held、unexplored、evidence、verdictが記録されている
- reportを書いた場合は対象HEAD、許可されたpath、handoffの内容が一致している
- product codeを変更しないまま、利用者が次のchatへ渡せるhandoffが完成している
- mergeしない

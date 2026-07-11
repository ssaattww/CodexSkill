# Issue #47 task routine hook 最終レビュー

## 対象

- repository: `ssaattww/CodexSkill`
- branch: `agent/issue-47-task-routine-hooks`
- base: `main`
- review基準: Issue #47 の acceptance criteria
- GitHub操作経路: GitHub connectorのみ
- 未使用: clone、`gh`

## 実装概要

`development-orchestrator` の内部toolとして、repositoryごとの永続task routineとCodex lifecycle hookを追加した。

- `SessionStart` / `UserPromptSubmit`: active taskと次工程を再注入
- `PreToolUse`: 前提工程未完了の編集・提出を拒否
- `Stop`: 未完了taskに継続promptを返す
- skill reflection / tool reflection / feedback trackingを必須化
- Issue/FPを履歴・重複・follow-upの正本とし、runtimeの次工程はlocal stateを正本化
- plugin導入とproject/user hooks installerを追加

## レビュー結果

### 修正済み finding 1: Stop hookの再入loop

初回の`decision: block`後、Codexは`stop_hook_active: true`でStop hookを再実行する。再入時にも同じblockを返すと無限継続になり得るため、再入時は再blockしないよう修正した。

### 修正済み finding 2: GitHub Contents APIの提出gate迂回

`create_file`、`update_file`、`delete_file`はfile editと同時にcommitを作成する。そのため通常editではなくsubmissionとして扱い、verification、review、両reflection、feedback、progress syncの証拠が揃うまで拒否するよう修正した。

Issue作成・更新・コメント・PR review投稿はrepository contentのcommitではないため、routine未開始でもdurable trackingを残せるようgate対象外とした。

### 修正済み finding 3: PR本文の証跡が未強制

Issue #47はPR本文にroutine、skill action、tool actionの証跡を要求している。従来実装はPR作成時の前提stepだけを確認し、本文内容を検証していなかった。

`create_pull_request` / `open_pull_request`に対して、次の見出しと非placeholder内容を必須化した。

```markdown
## Task routine evidence

## Skill action

## Tool action
```

`TODO`、`TBD`、`N/A`、理由のない`none`、`未記入`等は証跡として認めない。

## 検証

- connectorから取得した`.codex-plugin/plugin.json`と`hooks/hooks.json`をJSON parse: 成功
- 最終hook変更のPython AST parse: 成功
- 最新hook/stateを使ったtargeted unittest 6件: pass
  - Contents API提出gate
  - tracking tool除外
  - Stop再入防止
  - PR本文section不足
  - PR本文placeholder
  - PR本文の証跡あり
- 初期版のtask routine unittest 11件: pass
- checked-in test総数: 17件
- head commit `243cf276f16d85700715d21f9ae48eb5d062ec84`に紐づくGitHub Actions run: なし

最新差分を含む17件を単一commandでまとめて実行する確認は、clone可能なrunnerがこの作業環境にないため未実行である。初期11件と最新差分に直接関係する6件はそれぞれ成功している。PRはDraftとして作成し、CIまたはlocal runnerでの全17件一括実行をmerge前の確認事項とする。

## 残存リスク

- shellや任意script内部の副作用を完全には分類できない。hookはsecurity sandboxではなくworkflow omission gateである。
- Stop hookは無限再入防止のため1回のcontinuation後は再blockしない。継続できない場合は`pause`または`abort`を明示記録する必要がある。
- repositoryにPR向けGitHub Actions runが確認できないため、自動CIの有無はPR作成後に再確認する。

## task routine evidence

- intake: Issue #47と利用者の追加指示を確認
- skill scan: development-orchestrator、feedback-points-manager、git-pr-submitter、関連設計を確認
- task definition: 1 task routineとhook gateの実装、検証、PR提出
- plan: state、CLI、hook、test、skill/design、review、PRの順で実施
- implementation: branch上に実装・policy・設計・testを追加
- verification: JSON parse、AST parse、targeted helper検証、既存11 unittest成功記録
- review: 本reportでfindingを裁定
- feedback tracking: Issue #47をdurable recordとして継続
- progress sync: 本report、Draft PR、Issue commentへ同期

## skill action

`update-existing`

- `development-orchestrator`: task routine ownerとskill/tool reflectionを追加
- `feedback-points-manager`: Issue/FPとruntime triggerの責務を分離
- `git-pr-submitter`: PR本文のroutine/skill/tool証跡を必須化

新規skillは作成しない。既存skillの責務内で閉じる。

## tool action

`create-internal`

- `task_routine.py`
- `task_routine_state.py`
- `task_routine_hooks.py`
- plugin hook設定
- installer
- unit tests

反復確認と出力判定を、`development-orchestrator`所有の決定的な内部toolへ移した。

## disposition

Draft PRを作成し、Issue #47へPRと本reportを紐付ける。merge前に最新branchでunittest全件を実行する。

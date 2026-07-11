# Issue #47 task routine hook 最終レビュー r2

## 対象

- repository: `ssaattww/CodexSkill`
- branch: `agent/issue-47-task-routine-hooks`
- base: `main`
- Draft PR: #48
- review基準: Issue #47 の acceptance criteria
- GitHub操作経路: GitHub connectorのみ
- 未使用: clone、`gh`

## r1以降の追加finding

### 修正済み finding 4: MCP canonical tool名を分類できない

Codexの公式実装では、MCP toolの`PreToolUse`入力に`mcp__<server>__<tool>`形式のcanonical名が渡される。公式testでも`tool_name`が`mcp__rmcp__echo`になることが検証されている。

従来の`tool_token`は`.`区切りだけを除去していたため、次のようなGitHub connector操作を既知toolとして分類できなかった。

```text
mcp__github__create_pull_request
mcp__github__update_file
```

この状態では、PR本文証跡gateやContents APIのsubmission gateを迂回できる可能性があった。

判定前に`.`、`/`、`:`のnamespaceを除去し、`__`区切りがある場合は最後の要素を実tool名として扱うよう修正した。

```text
mcp__github__create_pull_request -> create_pull_request
mcp__github__update_file -> update_file
```

確認元:

- `openai/codex/codex-rs/hooks/src/events/common.rs`
- `openai/codex/codex-rs/core/tests/suite/hooks_mcp.rs`

## 全findingの状態

1. Stop hookの再入loop: 修正済み
2. GitHub Contents APIの提出gate迂回: 修正済み
3. PR本文のroutine/skill/tool証跡が未強制: 修正済み
4. MCP canonical tool名によるgate迂回: 修正済み

## 検証

- connectorから取得した`.codex-plugin/plugin.json`と`hooks/hooks.json`をJSON parse: 成功
- 最終hook変更と追加testのPython AST parse: 成功
- 初期版のtask routine unittest 11件: pass
- 最新hook/stateを使ったtargeted unittest 8件: pass
  - Contents API提出gate
  - tracking tool除外
  - Stop再入防止
  - PR本文section不足
  - PR本文placeholder
  - PR本文の証跡あり
  - MCP形式PR tool名の正規化と本文gate
  - MCP形式Contents API tool名のsubmission gate
- checked-in test総数: 19件
- Draft PR作成前head commit `6f3b531aefceea414a559bb537222068726c0ed1`に紐づくGitHub Actions run: なし

最新差分を含む19件を単一commandでまとめて実行する確認は、clone可能なrunnerがこの作業環境にないため未実行である。初期11件と最新差分に直接関係する8件はそれぞれ成功している。Draft PR #48は、CIまたはlocal runnerでの全19件一括実行をmerge前の確認事項とする。

## 残存リスク

- shellや任意script内部の副作用を完全には分類できない。hookはsecurity sandboxではなくworkflow omission gateである。
- 未知のnamespace表現が将来追加された場合は`tool_token`の正規化規則を更新する必要がある。
- Stop hookは無限再入防止のため1回のcontinuation後は再blockしない。継続できない場合は`pause`または`abort`を明示記録する必要がある。
- repositoryにPR向けGitHub Actions runが確認できないため、自動CIの有無は引き続きmerge前確認事項である。

## Task routine evidence

- intake: Issue #47と利用者の追加指示を確認
- skill scan: development-orchestrator、feedback-points-manager、git-pr-submitter、Codex公式hook実装を確認
- task definition: 1 task routine、hook gate、connector tool名正規化、検証、PR提出
- plan: state、CLI、hook、test、skill/design、review、PRの順で実施
- implementation: branch上に実装・policy・設計・testを追加
- verification: JSON parse、AST parse、初期11 unittest、最新差分targeted 8 unittest
- review: r1と本r2でfindingを裁定
- feedback tracking: Issue #47をdurable recordとして継続
- progress sync: review report、Draft PR #48、Issue commentへ同期

## Skill action

`update-existing`

- `development-orchestrator`: task routine ownerとskill/tool reflectionを追加
- `feedback-points-manager`: Issue/FPとruntime triggerの責務を分離
- `git-pr-submitter`: PR本文のroutine/skill/tool証跡を必須化

新規skillは作成しない。既存skillの責務内で閉じる。

## Tool action

`create-internal`

- `task_routine.py`
- `task_routine_state.py`
- `task_routine_hooks.py`
- plugin hook設定
- installer
- unit tests
- MCP canonical tool名の正規化

反復確認と出力判定を、`development-orchestrator`所有の決定的な内部toolへ移した。

## disposition

Draft PR #48へ本修正とr2 reportを追加し、Issue #47のコメントを最新状態へ更新する。merge前に最新branchでunittest全19件を一括実行する。

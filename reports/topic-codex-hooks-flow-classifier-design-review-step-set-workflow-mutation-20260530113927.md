# Sub-agent実行レポート

## タスク

- 目的: 複数種類の step set と workflow mutation を明文化した設計修正のレビュー
- タスク種別: design review

## sub-agentを使う理由

- 理由: task / step set / workflow mutation の contract 追加が通常経路を壊していないか、親エージェントから独立して確認するため。

## 対象範囲

- 対象: `design/codex-hooks-flow-classifier-design.md` の未コミット差分と現在内容。特に `task_type`、`step_set_refs`、複数 step set の node path、`update_workflow.py`、`workflow_mutations`、レビュー中の設計修正 task 追加。

## 対象外

- 対象外: 実装、PR本文更新、commit、push、既存未追跡ファイルの整理、`codex exec classifier` 方針の再採用。

## 実行コマンド

- 実行コマンド:
  - `sed -n '1,220p' skills/review-enforcer/SKILL.md`
  - `sed -n '1,220p' skills/sub-agent-task-manager/SKILL.md`
  - `sed -n '1,220p' skills/markdown-word-checker/SKILL.md`
  - `git status --short`
  - `git diff -- design/codex-hooks-flow-classifier-design.md`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '260,580p'`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '620,1130p'`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '1180,1335p'`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '1440,1535p'`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '1530,1715p'`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '1710,1795p'`
  - `nl -ba design/codex-hooks-flow-classifier-design.md | sed -n '1960,2025p'`
  - `rg -n "step_set_ref|step_set_refs|current_step|workflow_mutations|pending_workflow_mutation|update_workflow|直接編集|Codex 本体は|flow_state\\.json|progress\\.json" design/codex-hooks-flow-classifier-design.md`
  - `printf '%s\n' '{"hook_event_name":"PostToolUse","cwd":"/home/ibis/AI/CodexSkill","tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Update File: design/codex-hooks-flow-classifier-design.md\n*** End Patch"}}' | python3 skills/markdown-word-checker/hooks/post_tool_use_markdown_lint.py --codexskill-root /home/ibis/AI/CodexSkill`
  - `sed -n '1,260p' reports/topic-codex-hooks-flow-classifier-design-review-step-set-workflow-mutation-20260530113927.md`
  - `printf '%s\n' '{"hook_event_name":"PostToolUse","cwd":"/home/ibis/AI/CodexSkill","tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Update File: reports/topic-codex-hooks-flow-classifier-design-review-step-set-workflow-mutation-20260530113927.md\n*** End Patch"}}' | python3 skills/markdown-word-checker/hooks/post_tool_use_markdown_lint.py --codexskill-root /home/ibis/AI/CodexSkill`

## 対象ファイル

- 変更または確認したファイル:
  - 確認: `design/codex-hooks-flow-classifier-design.md`
  - 確認: `skills/review-enforcer/SKILL.md`
  - 確認: `skills/sub-agent-task-manager/SKILL.md`
  - 確認: `skills/markdown-word-checker/SKILL.md`
  - 確認: `skills/markdown-word-checker/hooks/post_tool_use_markdown_lint.py`
  - 変更: `reports/topic-codex-hooks-flow-classifier-design-review-step-set-workflow-mutation-20260530113927.md`

## 指摘事項

- 指摘要約または「指摘なし」:
  - blocking: `update_progress.py` の workflow mutation required 応答が、mutation 適用前に未作成 node を `next_node_path` に入れている。`design/codex-hooks-flow-classifier-design.md:1090` から `design/codex-hooks-flow-classifier-design.md:1111` では review step を完了しない応答の `state_summary.next_node_path` が `implementation_phase/design_revision_task#design-task/gather_requirements` になるが、この時点では `design_revision_task` はまだユーザー確認前で workflow_root に存在しない。`design/codex-hooks-flow-classifier-design.md:1775` から `design/codex-hooks-flow-classifier-design.md:1778` の順序では、ユーザー確認後に `update_workflow.py` が task を追加し、その後 `sync_flow_state.py` が next node を移すため、mutation 適用前の state が存在しない runtime node を指す。通常経路では `validate_state.py` / Stop hook の整合性検査に失敗するか、未適用 proposal を実行対象として提示する。
  - blocking: `workflow_mutations` の proposed 状態を application 済みに更新する所有者が明文化されていない。`design/codex-hooks-flow-classifier-design.md:1007` から `design/codex-hooks-flow-classifier-design.md:1040` の `update_workflow.py` request は workflow operations と `confirmation` を受け取るが、`workflow_mutations[].status` を `active` にし `applied_at` を埋める契約がない。一方で `design/codex-hooks-flow-classifier-design.md:1707` から `design/codex-hooks-flow-classifier-design.md:1753` は mutation state を持ち、`design/codex-hooks-flow-classifier-design.md:1555` から `design/codex-hooks-flow-classifier-design.md:1558` は proposed / failed mutation が残ると終了不可にしている。このままだと、実装が workflow JSON だけを更新しても state 側の proposed が残り、`pending_workflow_mutation` が閉じない通常経路になる。
  - blocking: Stop hook の擬似コードが `pending_workflow_mutation` と未解決 `workflow_mutations` を検査していない。`design/codex-hooks-flow-classifier-design.md:1289` から `design/codex-hooks-flow-classifier-design.md:1299` と `design/codex-hooks-flow-classifier-design.md:1555` から `design/codex-hooks-flow-classifier-design.md:1558` は Stop hook が proposed / failed mutation と `pending_workflow_mutation` を block すると定義しているが、実装擬似コード `design/codex-hooks-flow-classifier-design.md:1974` から `design/codex-hooks-flow-classifier-design.md:2001` には該当分岐がない。実装者がこの擬似コードを基準にすると、workflow mutation 待ちの mode と未解決 mutation を Stop 判定に反映しない。
  - user-confirmation-required: なし。
  - non-blocking: `step_set_ref` shorthand と `step_set_refs` canonical の両方が同一 task に存在する場合の優先順位または schema error が未定義。`design/codex-hooks-flow-classifier-design.md:335` から `design/codex-hooks-flow-classifier-design.md:342` では shorthand を読み込み時に canonical 配列へ正規化するとあるが、重複指定時の扱いは明文化されていない。通常例は `step_set_refs` なので現時点では記録のみ。
  - non-blocking: 複数 step set の canonical path は `task_path#step_set_id/step_id` として整備されているが、derived cache の `current_step` / `next_step` は step id 単独のまま残っている。`design/codex-hooks-flow-classifier-design.md:628` から `design/codex-hooks-flow-classifier-design.md:637` と `design/codex-hooks-flow-classifier-design.md:667` から `design/codex-hooks-flow-classifier-design.md:670` では canonical source が `progress.json` / `current_node_path` であるため直ちに破綻しないが、複数 step set で同名 step がある場合、表示・復帰用 cache として曖昧になる可能性がある。

## 結果

- 結果:
  - 指摘あり。blocking 3 件、user-confirmation-required 0 件、non-blocking 2 件。
  - repository-local task が `task_type` と `step_set_refs` で CodexSkill 側 step set を明示参照する方向性、および design / implementation / investigation / review-fix の複数 step set を定義できる方向性は確認した。
  - canonical node path は主要な state / progress / Flow State 例では `task_path#step_set_id/step_id` に更新されていることを確認した。
  - Codex 本体が `.codex/workflows/*.json`、`progress.json`、`flow_state.json` を直接編集する通常経路は、本文上は専用 script 経由に寄せられていることを確認した。ただし workflow mutation 待ちの state 遷移と Stop hook 擬似コードに上記 blocking の矛盾がある。

## リスク

- 未解決のリスクまたは後続対応:
  - Markdown lint は `design/codex-hooks-flow-classifier-design.md` と本報告書の確認で `unsupported`。理由は `package.json`, `tools/lint/markdown-targets.json`, `tools/lint/markdown-whitelist.yaml` が不足しているため。これは pass ではなく、設計内容の指摘有無とは分けた remaining risk として扱う。
  - この sub-agent review 内では、`codex exec`、ネストした Codex、追加の別エージェント起動は実施していない。built-in review behavior に沿ってレビューした。

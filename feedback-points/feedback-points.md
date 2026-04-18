# Feedback Points

Canonical active feedback-point ledger.

Location rule:

- real repository root: `feedback-points/feedback-points.md`
- do not keep the active ledger inside `skills/`

Update rule:

- このファイルは `feedback-points-manager` または `feedback-points-sanitizer` を通してのみ更新する
- それ以外の経路で直接追記・修正しない

| FP | 記録起点 | 内容 | カテゴリ | 重複グループ | skill化状態 | 関連skill | 状態 | 記録日 | 最終更新日 | 根拠リンク |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FP-001 | `親判断` | 大きめの一括差分は崩れやすいため、手動編集は数本ずつの小さな差分に分けて確実に適用する。ユーザーが明示的に `FP` と言わなくても、こうした reusable な実行上の気づきは記録する。 | `cost-control` | `split_large_manual_patches_and_record_execution_lessons` | `skill化済み` | `feedback-points-manager`, `development-orchestrator` | `対応済み` | `2026-04-18` | `2026-04-18` | `skills/feedback-points-manager/SKILL.md`, `skills/development-orchestrator/SKILL.md` |

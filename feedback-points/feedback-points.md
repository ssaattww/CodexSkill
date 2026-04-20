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
| FP-003 | `ユーザー指示` | 運用用語や出力項目名は、英語をそのまま残す前に自然な日本語表現を先に検討する。特に workflow や feedback の説明では、`next owner` のような曖昧な英語より `次アクション対応` のように役割が分かる日本語を優先する。 | `communication` | `prefer_clear_japanese_operational_terms` | `skill化済み` | `feedback-points-manager` | `対応済み` | `2026-04-18` | `2026-04-18` | `skills/feedback-points-manager/SKILL.md`, `skills/design/skill-hierarchy-design.md` |

# Feedback Format And Cleanup

Open this only when you need table format, status vocabulary, or legacy cleanup rules.

## Canonical feedback format

When bootstrapping a new active or backlog file, include an update-rule note near the top stating that the file may be updated only through `feedback-points-manager` or `feedback-points-sanitizer`.

Use this active table schema for `<repo-root>/feedback-points/feedback-points.md`:

- `FP`
- `記録起点`
- `内容`
- `カテゴリ`
- `重複グループ`
- `skill化状態`
- `関連skill`
- `状態`
- `記録日`
- `最終更新日`
- `根拠リンク`

## Origin values

`記録起点`:

- `ユーザー指示`: ユーザーが明示的に記録や反映を求めた
- `親判断`: 親が reusable な process lesson と判断して記録した
- `sub-agent提案`: sub-agent の分類や提案を受けて親が記録した
- `混合`: 複数の起点が明確に混ざっており、単一値に落とせない

`<repo-root>/feedback-points/feedback-points-backlog.md` keeps completed or archived points.
It may contain a one-time `Legacy Archive` section in an older schema.

## Status values

`状態`:

- `記録`
- `対応中`
- `対応済み`
- `不要`

`skill化状態`:

- `未整理`
- `検討中`
- `skill化済み`
- `不要`

## Bootstrap cleanup

If current feedback data is noisy or stale:

1. move active legacy rows into backlog as `Legacy Archive` without conversion
2. rebuild the active feedback file with the canonical header
3. re-register only high-signal active process points
4. continue FP numbering without reuse

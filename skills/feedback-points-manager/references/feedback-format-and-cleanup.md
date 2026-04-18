# Feedback Format And Cleanup

Open this only when you need table format, status vocabulary, or legacy cleanup rules.

## Canonical feedback format

Use this active table schema for `<repo-root>/feedback-points/feedback-points.md`:

- `FP`
- `内容`
- `カテゴリ`
- `重複グループ`
- `skill化状態`
- `関連skill`
- `状態`
- `記録日`
- `最終更新日`
- `根拠リンク`

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

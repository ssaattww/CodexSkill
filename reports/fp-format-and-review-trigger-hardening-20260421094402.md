# feedback-points フォーマット拡張と review trigger hardening

## 背景

- ユーザー指摘により、feedback / issue のフォーマットが薄く、`指摘回数` のような再発情報が追えないことが明確になった
- あわせて、ユーザーの `〜べきです` 発言は 100% 指摘として扱うべきという運用ルールを明文化する必要が生じた

## 実施内容

1. `feedback-points-manager` に `〜べきです` を即時 `指摘` として扱うルールを追加
2. `feedback-format-and-cleanup.md` に以下を canonical schema として追加
   - `指摘回数`
   - `直近指摘日`
   - `次アクション対応`
3. `skillization-issue-template.md` に以下を追加
   - `Next Action`
   - `Trigger Type`
   - `First Reported`
   - `Last Reported`
   - `Latest Trigger`
4. `build_skillization_issue.sh` を新しい template 項目に対応
5. `feedback-points.md` / `feedback-points-backlog.md` の実ファイルを新 schema に同期
6. `git-pr-submitter` / `git-workflow-manager` に、PR 本文で issue を必ず紐付けるルールを追加

## 変更ファイル

- `skills/feedback-points-manager/SKILL.md`
- `skills/feedback-points-manager/references/feedback-format-and-cleanup.md`
- `skills/feedback-points-manager/references/skillization-issue-template.md`
- `skills/feedback-points-manager/scripts/build_skillization_issue.sh`
- `feedback-points/feedback-points.md`
- `feedback-points/feedback-points-backlog.md`
- `skills/git-pr-submitter/SKILL.md`
- `skills/git-workflow-manager/SKILL.md`

## 補足

- `FP-004` は `指摘回数=2` として backlog 上に明示した
- issue `#11` は follow-up として新フォーマットに寄せて更新する

## 検証

- `git diff --check`
- 変更ファイルの差分確認
- script の help / 生成本文確認

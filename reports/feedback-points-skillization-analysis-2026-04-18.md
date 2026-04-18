# feedback-points の skill 化分析 (2026-04-18)

## 対象範囲

`ExcelReport` 側の `tasks/feedback-points.md` を確認し、`CodexSkill` に取り込むべき再利用可能な process ルールを抽出した。

確認対象:

- `codex-delegation-executor` と関連する基本 workflow skill 一式
- issue / PR / CI に関係する GitHub plugin skill

## 主な結論

1. アクティブな FP には、skill 化できる process ルールが多く含まれている。
2. 一部の FP は issue 固有の機能仕様であり、再利用可能な process ルールとしては扱うべきではない。
3. release 系 FP には明確な運用境界が必要である。
   - NuGet pre-release は `master` push をトリガーに完全自動
   - stable release はユーザー手動
   - workflow / publish 設定は、ユーザーが明示指示しない限りエージェントは編集しない

## 今回追加した skill

このリポジトリに以下を追加した。

- `skills/feedback-issue-intake-fallback-manager/SKILL.md`
- `skills/feedback-autonomy-boundary-manager/SKILL.md`
- `skills/feedback-coding-standards-enforcer/SKILL.md`
- `skills/feedback-points-sanitizer/SKILL.md`

更新したもの:

- `skills/feedback-points-manager/SKILL.md`
  - noisy な feedback を扱うための正規化方針
  - skill 化 issue フロー
  - 重複グループごとのルーティング方針
  - release 系は監査/レポート専用とする方針

## skill に落とし込んだルール

- FP111 系: `gh` が使えないときの issue 取得 fallback
- FP21 / FP141 / FP144 系: 自走継続と停止条件の境界
- FP19 系: public/protected API を含むコーディング規約チェック
- noisy な feedback の整理: 重複統合、仕分け、再利用可能な process ルールの抽出

## 今回 skill 化しなかったもの

- release 自動化そのものを変更する専用 skill
  - ユーザー方針により除外
  - 自動化の所有者は既存システムであり、明示指示があるまで変更しない
- issue / task 固有の DSL / 設計仕様
  - これらは再利用可能な process skill ではなく、issue / task / design で管理する

## 次の推奨作業

`feedback-points-sanitizer` を使って現在の active FP を整理し、再利用価値の高い process ルールだけを再登録して、関連 skill を対応付ける。

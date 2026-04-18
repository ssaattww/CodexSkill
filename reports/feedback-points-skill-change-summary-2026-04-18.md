# feedback-points skill 変更サマリ (2026-04-18)

## 変更範囲

今回の変更は `CodexSkill` における feedback-point の skill 化に限定している。

変更対象:

- `skills/feedback-points-manager/`
- `feedback-` プレフィックス付きの新規子 skill
- skill 化用の補助 reference / script
- skill 側レポート

release workflow や publish 自動化ファイルは、この変更では触っていない。

## 更新した skill

### `feedback-points-manager`

役割:

- `feedback-points/feedback-points.md` の運用責任を持つ親 skill
- 重複グループ化、skill 化判断、issue 化判断を行う
- active ledger 更新前に `feedback-points-sanitizer` の事前判定を要求する
- `feedback-` プレフィックス付き子 skill へルーティングする

補助追加:

- taxonomy reference
- skill 化 issue template
- issue 本文生成 script

## 新規子 skill

### `feedback-issue-intake-fallback-manager`

目的:

- issue 要件取得の fallback 専用 skill
- `gh` 失敗時でも信頼度付きで要件を確定する

### `feedback-autonomy-boundary-manager`

目的:

- 自走継続と停止確認の境界を決める skill
- 高リスク曖昧性、承認境界、外部契約変更で止まる

### `feedback-coding-standards-enforcer`

目的:

- 繰り返し指摘される規約違反をレビュー前に潰す skill
- 特に public/protected API と XML doc を強制する

### `feedback-points-sanitizer`

目的:

- feedback 一覧の分類とノイズ除去を担当する skill
- active ledger へ書く前の事前判定 reviewer も兼ねる
- `keep active / merge / move to backlog / skip` を返す

## 命名と役割の整合性

現時点では、skill 名と実際の役割に大きな乖離はない。

- `feedback-points-manager`
  - active ledger の管理責任と子 skill ルーティングを持つため、`manager` は妥当
- `feedback-points-sanitizer`
  - cleanup 専用ではなく事前分類 reviewer も担うが、役割の中心は sanitization なので現名称で問題ない
- `feedback-issue-intake-fallback-manager`
  - fallback 経路の管理が主目的なので名称どおり
- `feedback-autonomy-boundary-manager`
  - 自走/停止境界の管理が主目的なので名称どおり
- `feedback-coding-standards-enforcer`
  - 規約違反の検出と是正を強制するため、`enforcer` は妥当

## 命名規則

feedback-point 分析から派生した子 skill には `feedback-` プレフィックスを付け、`feedback-points-manager` との関係が skill 一覧から分かるようにした。

## 運用境界

release 関連の自動化はユーザー管理のままとする。

- pre-release 自動化は既存システムの責務
- stable release は引き続き手動
- この領域での agent 作業は、ユーザー明示指示がない限り監査/レポートのみ

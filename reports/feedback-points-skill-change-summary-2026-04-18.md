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

- 再利用可能な process feedback の管理
- 重複グループ化
- skill 化判断
- skill リポジトリ issue 化フロー
- `feedback-` プレフィックス付き子 skill へのルーティング

補助追加:

- taxonomy reference
- skill 化 issue template
- issue 本文生成 script

## 新規子 skill

### `feedback-issue-intake-fallback-manager`

目的:

- 通常の `gh issue view` 経路が使えないときに issue 要件を回収する
- 実装前に fallback 順序と信頼度扱いを明確にする

### `feedback-autonomy-boundary-manager`

目的:

- どこまで自走継続してよいかを定義する
- 曖昧さ、リスク、承認境界で止まる条件を定義する

### `feedback-coding-standards-enforcer`

目的:

- レビュー/コミット前に繰り返し指摘されるコーディング規約を強制する
- 特に public/protected API と XML doc コメントの確認を対象にする

### `feedback-points-sanitizer`

目的:

- noisy な feedback 一覧を整理する
- 再利用可能な process ルールと issue 固有の仕様/設計判断を分離する
- 履歴を残しながら active なノイズを減らす

## 命名規則

feedback-point 分析から派生した子 skill には `feedback-` プレフィックスを付け、`feedback-points-manager` との関係が skill 一覧から分かるようにした。

## 運用境界

release 関連の自動化はユーザー管理のままとする。

- pre-release 自動化は既存システムの責務
- stable release は引き続き手動
- この領域での agent 作業は、ユーザー明示指示がない限り監査/レポートのみ

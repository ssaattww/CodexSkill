# Markdown用語検査

CodexSkill自身のMarkdownについて、Git管理下のファイルを対象に英字語・カタカナ語の許可一覧検査を行う。

## 実行

- 全体検査: `npm run lint:md`
- 全体の未登録語一覧: `npm run lint:md:unknown`
- 変更Markdownだけ: `npm run lint:md:changed`
- 変更Markdownの未登録語一覧: `npm run lint:md:changed:unknown`

## 設定

- `markdown-targets.json`: 対象除外。現在は除外なし。
- `markdown-whitelist.yaml`: 許可語句。`term`、`aliases`、`description` の具体的変更は利用者確認後に反映する。

## 初期導入状態

許可一覧が `entries: []` の間は、未登録語一覧を利用者確認用の候補として収集する。`scripts/run_validation.py` はこの状態を `needs_user_review` と記録し、初期導入中だけ全体検証を失敗にしない。利用者確認済みの許可一覧が入った後も未登録語が残る場合は、全体検証を失敗として扱う。

GitHub Actionsでは依存関係の導入結果、用語検査の標準出力・標準エラー、結果、既存のrepository検証結果を同じ診断artifactへ保存する。

検査成功は文章の意味や読みやすさを保証しない。文章品質は `document-wording-review` と分けて確認する。

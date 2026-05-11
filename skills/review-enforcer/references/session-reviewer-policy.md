# Session Reviewer Policy

レビュー担当とレビュー基準をセッション内で安定させるための補助方針。

## レビュワー固定

- 1 つの作業セッションでは、基本的に 1 人の reviewer sub-agent を継続して使う。
- 初回 review、review finding の修正後再レビュー、同じ task 群の追加確認は、同じ reviewer に戻す。
- reviewer を固定する目的は、初回の観点、重大度判断、blocking / non-blocking の線引きを同じ基準で維持すること。
- reviewer は実装 worker とは分ける。監査担当が先に明確な基準を作った場合は、その監査担当を固定 reviewer にしてよい。

## レビュワー変更を許す条件

- 元の reviewer が利用できない、または再開できない。
- 元の reviewer が対象変更の実装 worker になっており、独立性が弱い。
- ユーザーが別 reviewer を明示した。
- task scope が大きく変わり、元の reviewer の基準では不十分になった。

reviewer を変更した場合は、review report に変更理由と新 reviewer を明記する。

## セッション内で決めた指針の継続利用

- audit report、design doc、review finding、ユーザー指示で決まったレビュー指針は、同じセッション内の後続 review に引き継ぐ。
- 後続 review request には、参照すべき report / design doc / user decision を明示する。
- 指針が命名、配置、XML コメント、test 説明、設計整合性、設定外出し、UI 表示差分などに関わる場合、reviewer はその指針に対する逸脱を blocking / non-blocking に分類して報告する。
- 新しい指針が既存指針を置き換える場合は、親がどちらを正とするかを明示してから review を依頼する。

## Review Request に含める項目

- 固定 reviewer として扱うか、今回だけの reviewer か。
- 前回 review / audit / design report の path。
- 今回適用する具体的な基準。
- reviewer 変更がある場合はその理由。
- 再レビューの場合は、前回 finding と修正 commit / report。

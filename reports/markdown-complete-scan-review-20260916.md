# Markdown全文検査の通常レビュー

作成日時: 2026-09-15T20:45:14.122094+00:00

対象: ssaattww/CodexSkill PR #81

レビュー方式: 初回の通常レビュー。実装・修正はこのチャットでは行っていない。

判定: **fail（要修正）**。中優先度（P2）4件。うち3件は今回の退行、1件は今回の境界厳密化に残る既存欠陥。

## 対象の固定

- ブランチ: `fix/markdown-lint-complete-scan`
- 比較元: `106ea5dcf12c4805756351fb9381df220b94f044`
- レビューした実装HEAD: `279b8da9ffe954f78fd8461555be429f1bdcc100`
- 比較範囲: `106ea5dcf12c4805756351fb9381df220b94f044...279b8da9ffe954f78fd8461555be429f1bdcc100`
- レビュー担当: `chatgpt-pr81-normal-review-20260916`

技術的な判定は上記HEADに対するもの。この記録・証拠・引き継ぎの保存コミットは通常レビューの記録用であり、独立最終レビューの承認コミットではない。保存コミット自身のSHAはコミット後のPRコメントで記録する。

## 確認した変更

長文分割、漢字名詞の検査対象除外、脚注IDだけの除外、複合許可語の境界判定、通常の対象拡張子を確認した。実装変更はPythonとJavaScriptの2ファイル。AGENTS.mdの非TDD方針に従い、実行用の恒久テストやワークフローは追加していない。

## 指摘

### R81-01 / P2 / 分割境界をまたぐ未登録の片仮名語が見逃される。

- 重大度: `medium`
- 発生区分: `introduced_by_change`
- 場所: `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py:517-525`

**影響:** 文書中の位置だけで許可一覧違反の検出結果が変わり、検査が誤って成功する。

**再現と根拠:** 「あ」15999文字 + 「ギア」 + 「あ」10文字（48033 bytes）を --stdin probe.md に渡すと、base は exit 1 でギアを検出し、HEAD は exit 0。同じ本文の先頭に「あ」を1文字加えると HEAD も exit 1。11種類の再結合確認は通るが、語の判定は保持されていない。

**必要な対応:** 分割境界周辺の語を元の文脈で検査できる方式にし、語を保持できない場合を成功扱いにしない。2文字語・長い片仮名語・境界前後の位置と行番号を確認する。

### R81-02 / P2 / 登録済みの英語複合語に漢字が隣接すると cspell が誤検出する。

- 重大度: `medium`
- 発生区分: `introduced_by_change`
- 場所: `skills/review-enforcer/scripts/run-cspell-markdown.js:89-90`

**影響:** 許可された識別子を日本語文中で使えなくなり、Python の許可判定と cspell の判定が食い違う。

**再現と根拠:** Tracker.DebugHost を許可した状態で、Tracker.DebugHost構成 と 構成Tracker.DebugHost は base cspell が exit 0、HEAD cspell が exit 1（Tracker / Debug / Host を拒否）。HEAD Python は同じ入力を exit 0 にする。ひらがな隣接の Tracker.DebugHostと は成功する。

**必要な対応:** 英語識別子の継続文字と日本語本文の境界を区別し、登録語の漢字隣接を許可しつつ Tracker.DebugHostx は拒否する。前後両側と Python/cspell の組合せを確認する。

### R81-03 / P2 / --files で明示指定した .txt が無警告で検査対象から捨てられる。

- 重大度: `medium`
- 発生区分: `introduced_by_change`
- 場所: `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py:21`

**影響:** 使用者が指定したファイルを検査していないのに成功を返す。help は引き続き .md/.txt 対応と案内している。

**再現と根拠:** 未登録語 qzxvunknownword を含む note.txt に --files note.txt を実行すると base は exit 1、HEAD は stderr 空の exit 0。同じ内容の note.md は HEAD でも exit 1。

**必要な対応:** 暗黙探索から .txt を除外する方針は維持できるが、明示指定時は検査するか非対応をエラーとして返す。--files / --changed の help と実際の契約を同期する。

### R81-04 / P2 / 複合語の境界修正後も、ドット・ハイフンによる未登録の連結語が通る。

- 重大度: `medium`
- 発生区分: `pre_existing`
- 場所: `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py:393-394; skills/review-enforcer/scripts/run-cspell-markdown.js:89-90`

**影響:** 登録した複合語だけを許可する契約に対して、登録語を連結した未登録の識別子まで許可される。

**再現と根拠:** Tracker.DebugHost を許可すると、未登録の Tracker.DebugHost.Tracker.DebugHost と Tracker.DebugHost-Tracker.DebugHost が HEAD の Python/cspell とも exit 0。英語検出の ENGLISH_RE はこれらを1語として扱うが、その前に部分語がマスクされる。base cspell でも成功するため、新規退行ではなく今回の境界厳密化に残る既存欠陥。

**必要な対応:** 英語語彙の継続子として使う . / - と文末の句読点を区別し、未登録の全体語を部分マスクしない。単独登録語、文末ピリオド、ドット・ハイフン・アンダースコアでの連結を両検査器で確認する。

## 実行確認

Ubuntu上で、実際のSudachiPyとcspellを使用した。比較元とレビュー対象で同じ依存版・入力・許可一覧を使った。再現用許可一覧の説明は「せつめい」とし、比較元の漢字検査が終了コードに混入しないようにした。

| 項目 | 結果 |
|---|---|
| 既存リポジトリ検証・配布物生成 | repository、bundle、zip-integrity、zip-contentsの4項目成功 |
| 構文・差分形式 | Python AST解析、node --check、git diff --check成功 |
| 分割性質 | 11種類で上限・再結合・オフセット保持を確認 |
| 実CLI・比較など | 46件の記録。検査による意図した拒否と不具合の再現を含み、全件成功という意味ではない |
| 脚注 | 参照IDは除外、定義本文と複数行本文の未登録英語は検出 |
| 通常漢字・未登録語 | 通常漢字を許容し、未登録英語・片仮名を検出 |
| 長文末尾 | 114,010 bytesの本文末尾を6002行目として検出。96,010 bytesの長い行を含む本文も末尾を2行目として検出 |

依存版: Python 3.12.3、Node.js 22.13.1、SudachiPy 0.6.11、SudachiDict core 20260428、PyYAML 6.0.3、cspell 9.8.0。

詳細コマンド、実際の標準出力・標準エラー・終了コード、再現用入力を構築するプログラム本文は `reports/markdown-complete-scan-review-evidence-20260916.json` に保存した。プログラムは証拠JSON内の文字列として保持し、恒久テストとしては追加していない。

## CIの確認

レビューした実装HEADと一致する実行を確認した。`34969144592` のbuildジョブはリポジトリ構造・リンク検証、配布物生成、アップロードが成功。配布物IDは `10396730778`（メタデータを確認、ダウンロードは未実施）。リリース用3ジョブはスキップ。`34969144491` もワークフロー全体はsuccessだが、実行ステップの検証証拠としては使用しない。

既存CIの成功は、今回検出した用語検査の意味的正しさを保証しない。記録保存後の新しいHEADのCI結果を、上記実装HEADの結果と混同しない。マージ時の必須チェック設定は未確認。

## 観点別の確認結果

| 観点 | 状態 | 根拠 |
|---|---|---|
| requirement and design conformance | checked_finding | R81-01..04。PRの5つの変更目的と比較。既存設計の脚注説明差は H-DOC。 |
| correctness and edge cases | checked_finding | 分割境界、漢字隣接、連結子、脚注、長文の実行結果。 |
| scope discipline | checked_finding | R81-03。差分は2ファイルに限定。 |
| changed files and dependencies | checked_finding | Python/cspell全差分、CLI本体、対象列挙、実利用側の設定と依存版を確認。 |
| API and compatibility | checked_finding | R81-02/03。baseとHEADを同じ依存版で比較。 |
| error handling and diagnostics | checked_finding | R81-03はファイル未検査を成功にする。実行ログを保持。 |
| security and secret handling | checked_no_finding | 今回差分に認証・外部送信・権限変更なし。検証は分離した作業領域で実行。 |
| validation adequacy | checked_finding | 既存4項目は通るが、実CLIの追加確認で退行を再現。検査用コードやworkflowの恒久追加は行わない。 |
| current-HEAD CI | checked_no_finding | 279b8da の pull_request CI 2件 success。build job成功とartifact作成を確認。 |
| report and documentation accuracy | held | H-DOC: 既存の許可一覧再構築設計は脚注定義行を除外と記載するが、PRは本文を検査へ変更。 |
| regression and maintainability | checked_finding | R81-01..03はbaseからの退行。R81-04は既存の残件として区別。 |

## 保留・未確認

**H-DOC（実装担当への文書同期確認）:** 既存の `design/review-enforcer-markdown-whitelist-rebuild-design.md` には脚注定義行を除外するとある一方、PRは脚注本文の検査を明示している。この差は保留として残す。今回のfail判定はR81-01からR81-04に基づく。

Windows側でもレビュー対象SHAとソースを確認したが、実CLIの検証はUbuntu側で行った。Windows固有の起動経路は未確認であり、Windows動作成功とは判定していない。

## 読んだ資料

- `AGENTS.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/work-context-manager/SKILL.md`
- `skills/review-worker/SKILL.md`
- `skills/report-writer/SKILL.md`
- `skills/chat-handoff-manager/SKILL.md`
- `skills/review-enforcer/SKILL.md`
- `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py`
- `skills/review-enforcer/scripts/run-cspell-markdown.js`
- `skills/review-enforcer/scripts/list-markdown-targets.js`
- `scripts/run_validation.py`
- `design/review-enforcer-markdown-whitelist-rebuild-design.md`
- `.github/workflows/pr-commit-artifacts.yml`

加えて、語彙抽出スクリプトの先頭220行、実利用側IbisDuckのpackage.json・cspell設定・対象一覧設定・Python依存一覧、GitHubのPR情報とCIジョブ・配布物メタデータを確認した。語彙抽出スクリプト全体を精査したとは主張しない。

## 次の対応

実装担当がR81-01からR81-04を修正し、指摘ごとに必要な対応・本番の処理経路・実際に組み合わせて動作を確認する入力・検証結果を対応付ける。境界の前後、両検査器、明示指定と暗黙探索を含めて確認したコミットを、同じ通常レビューチャットへ再レビューに出す。

引き継ぎ: `reports/handoffs/markdown-complete-scan-review-20260916.yaml`。今回、実装・許可一覧・設計・ワークフローは修正せず、マージも行っていない。

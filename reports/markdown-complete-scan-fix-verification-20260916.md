# Markdown全文検査 PR #81 fix verification

作成日時: 2026-09-15T22:50:25.139800+00:00

## 判定

**fail（要修正）**。先行のR81-01〜R81-05はすべてresolved。兄弟ケース確認でpre-existingのR81-06 / mediumを1件検出した。

## 対象

- reviewed implementation HEAD: `f7b4ac1213c20a6d1bb74e4ce445485755733d13`
- fix commit: `59dff18e4164d88de85fc44006e144bc5d26472c`
- previous review publication HEAD: `6a6f33df2498b7cac50c51e8110a3f9c8483cac9`
- review mode: fix verification
- reviewer continuity: `chatgpt-pr81-normal-review-20260916`（同じ通常レビュー会話）

実装commit後の`f7b4ac`との差分はreport/handoffのみで、`skills/`配下の差分がないことを確認した。

## 先行5件のfix verification

| Finding | Required action | Production path | Actual fixture | Focused evidence | Disposition |
|---|---|---|---|---|---|
| R81-01 | 語境界と元位置を保持して全文検査する。 | split_oversized_sudachi_segment / preserve_katakana_boundary | 48,033 bytes境界の「ギア」と2行目「ギアボックス」 | /tmp/pr81-fixverify-r1/python-results.json: boundary, boundary-line2 | **resolved** |
| R81-02 | 漢字隣接を許可しつつASCII継続子は拒否する。 | build_whitelist_value_pattern / whitelistValuePattern | Tracker.DebugHostの漢字前後、ASCII prefix/suffix | python-results.json + node-current/results.json | **resolved** |
| R81-03 | 明示.txtを検査しhelpを実契約に同期する。 | EXPLICIT_TARGET_SUFFIXES / select_target_files / parse_args | note.txt explicitとimplicit | python-results.json: explicit-txt, implicit-txt | **resolved** |
| R81-04 | 識別子継続子と文末句読点を区別する。 | Python/Node whitelist boundary patterns | dot/hyphen/underscore連結、prefix/suffix、terminal period | python-results.json + node-current/results.json | **resolved** |
| R81-05 | 正規化後の入力上限を保証し、語境界と元位置を保持する。 | sudachi_input_bytes / iter_sudachi_chunks / split_oversized_sudachi_segment | ㍿×6000 + 改行 + ジッタ | python-results.json: normalization + chunk_results | **resolved** |

実装handoffの`review.independent_closure.completeness_matrix`自体は空だったが、必要な4要素は実装レポート、保存済みprobe、現HEADの再実行から解決できたため、上表をclosure readiness matrixとして確定してからfix verificationを実施した。

## 新規指摘

### R81-06 / medium / pre-existing

場所: `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py:558`

NFKCで片仮名になる半角カタカナが許可一覧検査を無条件にすり抜ける。

**影響:** 未承認の半角カタカナ語を文書に書いてもMarkdown用語検査が成功し、cspellも日本語語彙を拒否しないためlint経路全体で見逃す。

**証拠:** current HEADで全角「コンピューター」はexit 1で未登録違反になる一方、半角「ｺﾝﾋﾟｭｰﾀｰ」はexit 0・診断なし。SudachiPyは半角surfaceをnormalized_form「コンピューター」の名詞として返す。base 106ea5でもexit 0のためpre-existing。

**必要な対応:** 片仮名判定をraw surfaceだけで早期終了せずNFKC/normalized formを考慮し、半角片仮名も未登録なら拒否する。長文分割の片仮名境界判定も同じ正規化契約に揃え、全角/半角と分割境界の組合せを確認する。

設計は英字語と片仮名語を語彙対象としている。current HEADでは全角`コンピューター`は未登録違反になる一方、半角`ｺﾝﾋﾟｭｰﾀｰ`は無診断でexit 0。SudachiPy自体は後者をnormalized form `コンピューター`の名詞として返すため、tokenizerではなく`should_check_japanese`のraw-surface早期終了が検査漏れの原因である。cspellは全角/半角ともexit 0なので別gateも補完しない。

## Validation

- 現HEAD Python checker: 元5件に対応する15ケースを再実行。元5件は期待通り。半角カタカナだけ期待違反としてexit 0。
- chunk invariants: NFKC膨張、分割境界、多行、長い半角文字列の4ケースで再結合・offset・48,000 byte上限を確認。
- 現HEAD cspell wrapper: 11ケースを直接実行し全件期待通り。
- repository validation: repository / bundle / zip-integrity / zip-contents 全てpass。
- Python構文、Node構文、`git diff --check`成功。
- exact-head CI: `35028597741` / head `f7b4ac...` / build success。artifact `10420910703`。

## Coverage dispositions

| Criterion | Disposition | Evidence |
|---|---|---|
| requirement and design conformance | checked_finding | R81-01〜05は修正済み。設計の「片仮名語」を半角表記がすり抜けるR81-06を検出。 |
| correctness and edge cases | checked_finding | 元5件と兄弟ケースを現HEADで直接実行。R81-06のみ未解消。 |
| scope discipline | checked_no_finding | 実装修正は2スクリプト、後続commitはreport/handoffのみ。 |
| changed files and dependencies | checked_finding | SudachiPy 0.6.11 / SudachiDict 20260428 / cspell 9.8.0で確認。R81-06はPython checkerのraw surface判定。 |
| API and compatibility | checked_no_finding | 明示.txtと既存Markdown探索、英語許可語境界の期待動作を確認。 |
| tests and validation adequacy | checked_finding | 実装側focused probesは元5件を覆うが、半角片仮名の兄弟ケースを含まずR81-06を見逃した。 |
| current-HEAD CI evidence | checked_no_finding | f7b4acと一致するrun 35028597741 build success、artifact 10420910703。 |
| report and documentation accuracy | held | H-DOC脚注設計差は継続。implementation handoffのcompleteness_matrixは空だったため本レビューで実証拠から再構築。 |
| regression and maintainability risks | checked_finding | R81-06はbase 106ea5にも存在するpre-existingの検査漏れ。 |

## Held / remaining risks

- H-DOC: 脚注定義本文を検査する現仕様と既存設計の除外記載の差は継続。今回のfail根拠とは別。
- Windowsの既存`cspell.cmd` spawn挙動はscope外。cspellの意味的確認はUbuntuで現HEADを直接実行した。
- R81-06が未解消のため独立最終レビューには進めない。

## Next action

R81-06を実装し、全角/半角の未登録・許可済み両方と、48,000 byte分割境界をまたぐ半角片仮名をfocused fixtureに追加する。修正後は同じ通常レビュー会話でR81-06とCI deltaのfix verificationを行う。mergeはしない。

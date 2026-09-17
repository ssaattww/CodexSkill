# Markdown日本語許可判定 互換表記指摘対応レポート

作成日: 2026-09-17

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81 fix: make Markdown lint scan complete documents`
- Branch: `fix/markdown-lint-complete-scan`
- Finding: `R81-07 / medium / coverage_miss`
- Finding review target: `c67370f985f5c0c1ee330f10ff5bbd500c72fe2a`
- Review record HEAD: `7417ac0da68202ff81f5cdf0c91417f6d8bb290b`
- Technical fix commit: `bb3ad34bbba6a873c73d2d737ddd4368631eee04`
- Development policy: CodexSkill保守のため非TDD
- Verification capability: `local_execution_available`

## 目的と範囲

Duckで判明した追加要件のfix verificationで検出されたR81-07だけを修正する。
日本語の許可判定では、半角片仮名の幅差は同一視する一方、`㌔` / `キロ` のようなUnicode互換表記を暗黙の別表記として許可しない。

引用例外Issue #85、Duck側の許可一覧、既存H-DOC、Windowsの既存`cspell.cmd` spawn挙動は変更しない。
## 原因

従来は英語用・診断用と同じ `normalize_term` を日本語の許可判定にも使用していた。
`normalize_term` は `NFKC + casefold` のため、半角片仮名だけでなくUnicode互換文字も展開する。

その結果、明示的な `term` / `aliases` に登録していないにもかかわらず、次の表記が同一視された。

- `㌔` ↔ `キロ`
- `㌢` ↔ `センチ`
- `㍑` ↔ `リットル`
- `㍍` ↔ `メートル`

また `㌢` / `センチ` はSudachiPyの品詞が経路によって `形状詞` となるため、単純に許可判定の正規化だけを差し替えると片方向が既存の名詞filterで検査対象外になることも確認した。

## 修正

`check-markdown-whitelist-sudachi.py` に日本語許可判定専用の正規化を追加した。

- `normalize_japanese_whitelist_term`: 半角片仮名run `U+FF61..U+FF9F` だけをNFKCで幅統一し、その他の互換文字は展開しない。
- `Whitelist.japanese_terms`: `term` と明示 `aliases` を上記規則で保持する。
- 日本語のallow判定は `surface_normalized in whitelist.japanese_terms` のみにする。
`compatibility_permission_mismatch` は、従来のNFKCなら許可語へ一致する一方、幅差専用正規化では一致しない片仮名表記だけを検出する。
この場合は既存の品詞filterで無言skipせず、未承認の互換表記として違反にする。

この方式により、R81-07のために `形状詞` 全体を新たな検査対象へ広げる変更は避けた。
既存の通常判定は引き続き名詞filterを維持する。

Sudachi `normalized_form` は未知語集計・診断用の正規化値として残し、許可判定には使わない。

## Focused validation

実SudachiPyで17ケースを実行し、全件期待値と一致した。

| ケース | 期待 | 結果 |
| --- | --- | --- |
| `term: キロ`, input `㌔` | reject | exit 1 |
| `term: ㌔`, input `キロ` | reject | exit 1 |
| `term: センチ`, input `㌢` | reject | exit 1 |
| `term: ㌢`, input `センチ` | reject | exit 1 |
| `term: リットル`, input `㍑` | reject | exit 1 |
| `term: ㍑`, input `リットル` | reject | exit 1 |
| `term: メートル`, input `㍍` | reject | exit 1 |
| `term: ㍍`, input `メートル` | reject | exit 1 |
追加で以下も確認した。

- `キロ` に `㌔` を明示alias登録した場合だけ `㌔` をallow。
- `㌔` に `キロ` を明示alias登録した逆向きもallow。
- `ギア` / `ｷﾞｱ` は両方向allowを維持。
- `キャプチャー` はallow、未承認の `キャプチャ` はrejectを維持。
- `ｷﾞｱｽ`、`ﾃｽﾄｷﾞｱ`、`ｷﾞｱス` はrejectを維持。

保存証拠:

- `reports/markdown-japanese-compatibility-whitelist-followup-evidence-20260917.json`
- RDC task scratch `C:\Users\donabe\Project\CodexSkill-pr81-validation\r81-07-logs`

依存版:

- SudachiPy `0.6.11`
- SudachiDict-core `20260428`
- PyYAML `6.0.3`

## Regression validation

Technical fix commit `bb3ad34bbba6a873c73d2d737ddd4368631eee04` で既存probeも再実行した。

- Duck正規形/読み追加対応: 10/10 success
- R81-06 全角/半角・長文境界: 8/8 success
- R81-01〜05 Python regression: 13/13 success
- IR81-01 / IR81-02 regression: 15/15 success
## Repository validation

Technical fix commit上で以下を実行し、全てpassした。

- Python構文確認
- `git diff --check`
- `scripts/run_validation.py`
  - repository: pass
  - bundle: pass
  - zip-integrity: pass
  - zip-contents: pass

診断出力:
`C:\Users\donabe\Project\CodexSkill-pr81-validation\full-validation-r81-07-technical`

## Intentionally untouched

- Duck側の `markdown-whitelist.yaml`: 変更していない。
- `aliases`: 自動追加していない。
- Issue #85 attributed quotation lint exception: 別scopeのため未変更。
- cspell実装: R81-07はPython whitelist checkerの許可判定問題であり変更していない。
- H-DOC脚注設計差: held継続。
- Windowsの既存 `cspell.cmd` spawn挙動: held継続。
- reserved independent-final report: 実装担当ではmaterializeしない。

## Publication / CI

本report生成時点のtechnical fix commitは `bb3ad34bbba6a873c73d2d737ddd4368631eee04`。
report/handoff/evidenceを管理commitとして追加し、最終publication treeのfull local gateを再実行してからpushする。
push後はPR current HEADとrunの `head_sha` が完全一致するCIだけを確認し、別SHAは代用しない。
## Remaining risks / held

- R81-07の技術修正は実装担当として完了したが、同じ通常レビュアーによるfix verificationは未実施。
- 新しいtechnical commitが入ったため、既存の独立最終closureはそのまま完了扱いにできない。
- cspellは日本語のこの承認差を担保するgateではなく、whitelist checker側で表記承認を保証する。

## Next action

1. 同じ通常レビュアーで `R81-07` と直接回帰だけをfix verificationする。
2. 通常review収束後、既存の独立最終レビュー同一ライフサイクルで新しいtechnical / CI deltaをbounded closureする。
3. 独立最終closureがpassするまでreserved reportをmaterializeしない。
4. mergeは利用者が行うため実施しない。

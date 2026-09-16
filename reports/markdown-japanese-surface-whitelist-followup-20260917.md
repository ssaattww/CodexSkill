# Markdown日本語許可判定 Duck追加対応レポート

作成日: 2026-09-17

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81 fix: make Markdown lint scan complete documents`
- Branch: `fix/markdown-lint-complete-scan`
- 追加要件: PR #81 comment `5704475283`
- 発生元: `ibis-ssl/Duck` PR #20 の用語検査
- 修正前確認HEAD: `28823db2a0f3f0354c43ae892f25307b1679159c`
- 実装commit: `daeddaa5a5d5a626d1ad891a831f6476a9c530a4`
- 実装commitの親: `df7c6c6be53e4f3d6e81b4e3c15aef188454b5dc`
- Development policy: CodexSkill保守のため非TDD
- Verification capability: `local_execution_available`

## 要件

Duckでは承認済み表記が「キャプチャー」のみであるのに、未承認の「キャプチャ」もwhitelist検査を通過した。
日本語の許可判定は、実際に記載された表記と承認済み `term` / 明示 `aliases` の一致に限定する。
Sudachiの `normalized_form` または `reading_form` が一致するだけでは許可しない。
全角・半角の幅差はNFKCで同一表記として扱う既存契約を維持する。Duck側の許可一覧へ「キャプチャ」を追加したり、aliasを自動追加したりして回避しない。

引用原文の検査例外はIssue #85の別scopeであり、この変更には含めない。

## 原因

修正前は `check_japanese_tokens` が次の3値のいずれかをwhitelistと照合していた。

- Sudachi `normalized_form`
- Sudachi `reading_form`
- 実表記を `normalize_term` した値

実SudachiPy 0.6.11 / SudachiDict-core 20260428では「キャプチャ」の `normalized_form` が「キャプチャー」となる。
そのため `term: キャプチャー` だけでも、修正前HEADでは「キャプチャ」が許可された。

修正前HEAD `28823db...` を固定して再実行した結果:

- whitelist: `term: キャプチャー`、aliasなし
- input: `キャプチャを確認する。`
- whitelist checker exit: `0`
- stdout/stderr: 空
- evidence: `C:\Users\donabe\Project\CodexSkill-pr81-validation\duck-normalization-before.json`
## 実装

変更ファイルは `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py` のみ。

- 許可判定を `surface_normalized in whitelist.terms` に限定した。
- `surface_normalized` は既存 `normalize_term`、つまりNFKC + casefoldを使用するため、`ギア` / `ｷﾞｱ` の幅差は同一として扱う。
- `whitelist.terms` は `term` と明示 `aliases` だけから作られるため、alias追加時だけ別表記を許可する。
- Sudachi `normalized_form` は `diagnostic_normalized` として未知語集計・違反診断の正規化値に残した。
- `reading_form` は許可判定から外した。読みの一致だけで許可範囲は拡張しない。

許可一覧、target設定、cspellスクリプト、設計、workflowは変更していない。

## Focused validation

実装commit `daeddaa5a5d5a626d1ad891a831f6476a9c530a4` で実SudachiPyを使用して10ケースを実行し、全件期待値と一致した。

| Case | Expected | Result |
|---|---:|---:|
| `term: キャプチャー` + `キャプチャー` | allow / 0 | 0 |
| `term: キャプチャー` + `キャプチャ` | reject / 1 | 1 |
| `alias: キャプチャ` 明示 + `キャプチャ` | allow / 0 | 0 |
| `term: アオリンゴ` + `青リンゴ`（readingのみ一致） | reject / 1 | 1 |
| `term: ユーザー` + `ユーザ`（normalized_formのみ一致） | reject / 1 | 1 |
| `term: ギア` + `ｷﾞｱ` | allow / 0 | 0 |
| `term: ｷﾞｱ` + `ギア` | allow / 0 | 0 |
| `term: ギア` + `ｷﾞｱｽ` | reject / 1 | 1 |
| `term: ギア` + `ﾃｽﾄｷﾞｱ` | reject / 1 | 1 |
| `term: ギア` + `ｷﾞｱス` | reject / 1 | 1 |

Evidence:

- `C:\Users\donabe\Project\CodexSkill-pr81-validation\duck-normalization-results.json`
- `C:\Users\donabe\Project\CodexSkill-pr81-validation\duck-normalization-logs\*.stdout.log`
- `C:\Users\donabe\Project\CodexSkill-pr81-validation\duck-normalization-logs\*.stderr.log`
- dependencies: SudachiPy `0.6.11`, SudachiDict-core `20260428`, PyYAML `6.0.3`

## cspellの個別確認

Ubuntu RDC上のcspell `9.8.0`をwhitelist checkerとは別に実行した。

- `キャプチャーを確認する。`: exit 0、Issues 0
- `キャプチャを確認する。`: exit 0、Issues 0

したがって、cspellは今回の日本語表記承認差を判定しない。cspell成功をwhitelist検査の成功証拠には使わず、両検査器の責務差として記録する。
Evidence: `/tmp/pr81-validation/logs/cspell-capture-*.{stdout,stderr,exit}.log|txt`
## Regression validation

同じrebased implementation HEAD `daeddaa5a5d5a626d1ad891a831f6476a9c530a4` で既存回帰を再実行した。

- R81-01〜R81-05向けPython probe: 13ケース success
- R81-06向け全角/半角・48,000 byte境界 probe: 8ケース success
- IR81-01 / IR81-02向けfocused probe: 15ケース success
- `git diff --check`: success

R81-06で維持した全角/半角相互許可、IR81-01で維持したprefix/suffix拒否、IR81-02の明示file validationはいずれも維持された。

## Repository validation

`daeddaa5...` のtreeで `scripts/run_validation.py` を実行した。

| Step | Result |
|---|---|
| repository | pass / exit 0 |
| bundle | pass / exit 0 |
| zip-integrity | pass / exit 0 |
| zip-contents | pass / exit 0 |

Diagnostics: `C:\Users\donabe\Project\CodexSkill-pr81-validation\full-validation-duck-normalization-rebased`

## Publication state

実装commit `daeddaa5...` はpush済み。詳細report/handoffの管理commitは本レポート生成後に作成する。
最終publication HEADでrepository-defined full local gateを再実行し、そのHEADと完全一致するworkflow runだけをCI証拠として使用する。
別SHAのCIは代用しない。
## Intentionally untouched / held

- Issue #85の引用例外: 別scope。実装していない。
- H-DOC: 脚注本文の現仕様と既存設計記載の差。継続held。
- Windowsの既存 `cspell.cmd` spawn挙動。継続held。
- Duck側の許可一覧: 変更していない。「キャプチャ」のterm/alias追加も行っていない。
- 独立最終レビュー予約先: この追加実装により技術HEADが更新されたため、既存の独立closure前提をそのまま完了扱いにしない。

## Next action

1. 同じ通常レビュアーで、PR #81 comment `5704475283` の追加findingと直接回帰をfix verificationする。
2. current HEAD更新に伴う既存review/independent closureのCI deltaを、review-enforcer契約に従って再確認する。
3. 独立最終reviewが再び収束するまでmergeしない。

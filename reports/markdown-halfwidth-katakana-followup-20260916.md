# Markdown半角片仮名 指摘対応レポート

作成日: 2026-09-16

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81 fix: make Markdown lint scan complete documents`
- Branch: `fix/markdown-lint-complete-scan`
- 指摘元HEAD: `422207a52e574281147a721113421281cc5a686f`
- 実装コミット: `606b7e7d3d7fe000dc97d6541bac7d22c07c0247`
- Finding: `R81-06 / medium / pre-existing`
- Development policy: CodexSkill保守のため非TDD
- Verification capability: `local_execution_available`

## 目的と範囲

R81-06のみを修正した。半角片仮名をNFKC後の片仮名として用語検査対象にし、長文分割境界の片仮名判定も同じ正規化契約に揃える。

対象外はH-DOC保留事項、Windowsの既存`cspell.cmd`起動挙動、許可一覧の語彙変更、mergeである。

## 原因

`should_check_japanese` がraw surfaceに対する `KATAKANA_RE` 判定で早期returnしていたため、SudachiPyがnormalized formを全角片仮名として返しても半角片仮名を検査しなかった。

同様に `preserve_katakana_boundary` もraw 1文字だけを判定していたため、半角片仮名の長文分割境界を同じ契約で保護していなかった。

## 実装

`skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py` に `contains_katakana` を追加し、NFKC正規化後の文字列に対して片仮名を判定するようにした。

- `should_check_japanese`
  - raw surfaceのNFKC結果とSudachiPy `normalized_form` の双方を確認する。
  - 半角表記でも片仮名名詞なら既存の許可一覧照合へ進む。
- `preserve_katakana_boundary`
  - 分割境界の左右を `contains_katakana` で判定する。
  - 全角と半角で分割保護の契約を共通化する。

変更はこの1ファイルだけで、既存の英語識別子境界、明示`.txt`、NFKC入力長、脚注処理には変更を加えていない。

## Focused validation

実SudachiPy `0.6.11`、SudachiDict-core `20260428`、PyYAML `6.0.3` を使用した。

| Case | Expected | Result |
|---|---:|---:|
| 未登録 全角 `コンピューター` | reject | exit 1 |
| 未登録 半角 `ｺﾝﾋﾟｭｰﾀｰ` | reject | exit 1 |
| 全角許可語 + 全角入力 | allow | exit 0 |
| 全角許可語 + 半角入力 | allow | exit 0 |
| 半角許可語 + 全角入力 | allow | exit 0 |
| 半角許可語 + 半角入力 | allow | exit 0 |
| 48,000 byte境界をまたぐ半角語・未登録 | reject | exit 1 |
| 48,000 byte境界をまたぐ半角語・許可済み | allow | exit 0 |

境界fixtureは `"あ" * 15999 + "ｺﾝﾋﾟｭｰﾀｰ" + "あ" * 10`。NFKC後48,048 bytesで2チャンクに分割され、再結合一致、全チャンク48,000 bytes以下、半角語が1チャンク内に保持されることを確認した。

証拠:

- `C:\Users\donabe\Project\CodexSkill-pr81-validation\r81-06-results.json`
- `C:\Users\donabe\Project\CodexSkill-pr81-validation\r81-06-logs`

加えてR81-01〜R81-05向け既存Python回帰13ケースを現実装で再実行し、全件成功した。

## Repository validation

`606b7e7d3d7fe000dc97d6541bac7d22c07c0247` の実装内容で `scripts/run_validation.py` を実行した。

| Step | Result |
|---|---|
| repository | pass / exit 0 |
| bundle | pass / exit 0 |
| zip-integrity | pass / exit 0 |
| zip-contents | pass / exit 0 |

診断出力: `C:\Users\donabe\Project\CodexSkill-pr81-validation\full-validation-r81-06`

## Failure diagnostics / CI artifact workflow

`.github/workflows/pr-commit-artifacts.yml` は現在も存在し、exact PR HEADをcheckoutした上でvalidationの標準出力・標準エラー・結果・source archiveを成功/失敗に関係なくartifactへ保存する契約を確認した。今回workflow変更は不要。

R81-06の修正前証拠は `reports/markdown-complete-scan-fix-verification-20260916.md` と `reports/markdown-complete-scan-fix-verification-evidence-20260916.json` に保存済みである。

## Intentionally untouched

- R81-01〜R81-05の実装: fix verificationでresolved済みのため変更しない。
- H-DOC: 脚注本文の現仕様と既存設計記載差は継続held。
- `run-cspell-markdown.js`: R81-06はPython checkerの片仮名判定が原因であり変更不要。
- Markdown許可一覧: 語彙変更なし。
- workflow: 既存artifact workflowが要件を満たすため変更なし。

## Publication / CI

本レポート作成時点では実装コミット `606b7e7d...` はローカルで、push前である。report/handoffを含む最終publication treeでfull local gateを再実行し、push後はPR current HEADとrun head SHAが一致するCIだけを確認する。

## Remaining risks / next action

R81-06の技術修正はfocused validationで期待動作を確認済み。最終判断は同じ通常レビュアーによるR81-06とCI deltaのfix verificationに委ねる。

mergeは実施しない。

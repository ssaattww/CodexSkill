# Markdown全文検査 PR #81 指摘対応レポート

作成日: 2026-09-16

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81 fix: make Markdown lint scan complete documents`
- Branch: `fix/markdown-lint-complete-scan`
- 指摘対応開始時HEAD: `6a6f33df2498b7cac50c51e8110a3f9c8483cac9`
- 実装コミット: `59dff18e4164d88de85fc44006e144bc5d26472c`
- Development policy: CodexSkill保守のため非TDD
- Verification capability: `local_execution_available`

## 目的と範囲

通常レビューで残った `R81-01` から `R81-05` の5件だけを修正した。
設計、許可一覧、CI workflow、既存レビュー記録の内容は変更していない。
マージは実施しない。

## 変更ファイル

- `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py`
  - 明示指定 `.txt` の検査契約を復元
  - 許可語の識別子境界を修正
  - Sudachi入力長をNFKC正規化後のUTF-8バイト数で制限
  - 長文分割時に片仮名語の途中を可能な限り切らない
- `skills/review-enforcer/scripts/run-cspell-markdown.js`
  - 英語識別子と日本語本文の境界を分離
  - `.`, `-`, `_` で連結された未登録語の部分マスクを防止

## 指摘対応

| Finding | 対応 | 検証 |
|---|---|---|
| R81-01 | Sudachi分割位置が片仮名語の内部に入る場合、語の手前まで分割位置を戻す。 | 48,033 bytesの境界入力で `ギア` を1行目として検出。2行目に長い片仮名語を置いた入力でも2行目の違反として検出。 |
| R81-02 | ASCII識別子の境界から漢字を除外し、日本語本文との隣接を許可。 | Python/cspellで `Tracker.DebugHost構成` と `構成Tracker.DebugHost` が成功。`Tracker.DebugHostx` は失敗。 |
| R81-03 | 通常探索は `.md` のまま、`--files` 明示指定だけ `.md/.txt` を許可。`--changed` helpも `.md` に同期。 | `--files note.txt` が未登録語を検出しexit 1。通常探索では `.txt` を対象にせずexit 0。 |
| R81-04 | ASCII許可語の前後で `._-` と識別子文字が連続する場合はマスクしない。 | Python/cspellで dot、hyphen、underscore連結をexit 1。単独語と文末ピリオドはexit 0。 |
| R81-05 | 分割判定を生テキストのバイト数ではなく、NFKC正規化後のUTF-8バイト数で実施。 | `㍿`×6000 + 改行 + `ジッタ` で `Input is too long` を出さず、2行目の `ジッタ` を検出。 |

## focused validation

Windows/FA780の専用scratchで SudachiPy の実CLIを検証した。
依存は `SudachiPy 0.6.11`、`SudachiDict-core 20260428`、`PyYAML 6.0.3`。
13ケースすべて期待した終了コードと診断になった。
証拠は `C:\Users\donabe\Project\CodexSkill-pr81-validation\python-probe-results.json` と同ディレクトリの `logs` に保持した。

Ubuntu/ibis-ThinkBook-14-G7-IML の `/tmp/pr81-validation` では `cspell 9.8.0` を使用した。
8ケースすべて期待した終了コードになった。
証拠は `/tmp/pr81-validation/node-probe-results.json` と `/tmp/pr81-validation/logs` に保持した。

Windowsでは既存のNodeラッパーが `spawnSync` から `cspell.cmd` を直接起動できず、無出力exit 1になるため、cspell実行確認は元レビューと同じUbuntu経路で実施した。このWindows固有の既存挙動は今回の5指摘の修正対象には含めていない。

## repository validation

実装コミット `59dff18e4164d88de85fc44006e144bc5d26472c` で `scripts/run_validation.py` を実行した。

| Step | Result |
|---|---|
| repository | pass / exit 0 |
| bundle | pass / exit 0 |
| zip-integrity | pass / exit 0 |
| zip-contents | pass / exit 0 |

診断出力は `C:\Users\donabe\Project\CodexSkill-pr81-validation\full-validation-impl` に保持した。
`git diff --check`、Python構文確認、Node構文確認も成功した。

## intentionally untouched

- 既存レビュー2レポートと証拠JSON/YAML: 履歴証拠のため変更しない。
- `design/review-enforcer-markdown-whitelist-rebuild-design.md`: 通常レビューのH-DOC保留事項であり、今回の5指摘対応には含めない。
- Markdown許可一覧: 語彙の追加・削除は行わない。
- workflow: CodexSkill保守の既存方針を変更しない。

## publication / CI

本レポート生成時点では実装コミットはローカルにあり、push前である。
最終publication treeに対するローカルゲートを再確認してからpushする。
CIはpush後、PRのcurrent HEAD SHAとrunのhead SHAが一致するrunだけを確認する。別SHAのrunは代用しない。

## remaining risks / unknowns

- Windowsでの `run-cspell-markdown.js` 実CLI起動は、既存の `.cmd` spawn挙動により成功確認できていない。Ubuntu実cspellでは今回変更した境界契約を確認済み。
- 先行レビューのH-DOC保留事項は未解消のまま。
- push後のexact-head CI結果は本レポート作成時点では未成立。

## next action

同じ通常レビュアーによる `R81-01` から `R81-05` のfix verificationが次のレビュー工程となる。
独立最終レビューの判定はこの実装作業では行わない。
mergeは利用者が行うため実施しない。

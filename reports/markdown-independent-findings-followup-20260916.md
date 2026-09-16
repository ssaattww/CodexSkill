# Markdown全文検査 独立最終レビュー指摘対応レポート

作成日: 2026-09-16

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81 fix: make Markdown lint scan complete documents`
- Branch: `fix/markdown-lint-complete-scan`
- 独立レビュー対象HEAD: `c2a21ecdf7e9e3d6bd74414eed087ea2af6aa346`
- 実装commit: `3a004c2a762a67d35cbdcbc14092a1a138c0820d`
- Independent review: `pullrequestreview-5221411529`
- Development policy: CodexSkill保守のため非TDD
- Verification capability: `local_execution_available`

## 目的と範囲

独立最終レビューで検出された required finding `IR81-01` と `IR81-02` の2件だけを修正した。
既存の `R81-01` から `R81-06` の解消済み契約を維持し、設計、許可一覧、workflow、独立最終レビュー予約先は変更していない。

## 指摘対応

| Finding | 対応 |
|---|---|
| IR81-01 / medium / coverage_miss | 非ASCII許可語の境界文字へ半角片仮名 `U+FF65..U+FF9F` を追加し、半角許可語の一部だけをprefix/suffix付き語からマスクしないようにした。 |
| IR81-02 / medium / coverage_miss | `--files` の各指定pathを選択前に検証し、不存在、repo外、対象外suffix、非file、ignore対象を明示エラー `exit 2` にした。 |

## focused validation

実装commit `3a004c2a762a67d35cbdcbc14092a1a138c0820d` のclean worktreeで、実SudachiPyを使って15ケースを確認した。

### IR81-01

- 半角許可語 `ｷﾞｱ` 自体: allow
- 半角許可語を全角 `ギア` で使用: allow
- 全角許可語 `ギア` を半角 `ｷﾞｱ` で使用: allow
- 半角suffix `ｷﾞｱｽ`: reject
- 半角prefix `ﾃｽﾄｷﾞｱ`: reject
- 全角suffix `ｷﾞｱス`: reject

### IR81-02

- 実在する違反 `.md`: exit 1
- 明示 `.txt` の違反: exit 1
- `missing.md`: exit 2 + 明示診断
- ignore directory配下: exit 2 + 明示診断
- ignored prefix配下: exit 2 + 明示診断
- 正常file + missing混在: exit 2
- 対象外suffix: exit 2
- repo外path: exit 2

証拠: `C:\Users\donabe\Project\CodexSkill-pr81-validation\ir81-independent-results.json` と `ir81-independent-logs`。

## regression validation

同じ実装commitで既存回帰も再実行した。

- R81-01〜R81-05向けPython probe: 13ケース success
- R81-06向け全角/半角・48,000 byte境界 probe: 8ケース success
- Python構文確認: success
- `git diff --check`: success

R81-06 probeは、未登録全角/半角をrejectし、許可済み全角/半角の相互表記をallowし、長文境界でも未登録reject / 許可済みallowを維持した。

## repository validation

実装commit `3a004c2a762a67d35cbdcbc14092a1a138c0820d` で `scripts/run_validation.py` を実行した。

| Step | Result |
|---|---|
| repository | pass / exit 0 |
| bundle | pass / exit 0 |
| zip-integrity | pass / exit 0 |
| zip-contents | pass / exit 0 |

診断出力: `C:\Users\donabe\Project\CodexSkill-pr81-validation\full-validation-ir81-independent-impl`

## intentionally untouched

- `reports/markdown-complete-scan-independent-final-review-20260916.md`: 独立最終レビュー予約先。metadata-only状態を維持し、作成していない。
- `design/review-enforcer-markdown-whitelist-rebuild-design.md`: H-DOC heldは今回のrequired 2件とは別のため変更していない。
- Windowsの既存 `cspell.cmd` spawn挙動: 今回のPython checker指摘とは別のheldとして変更していない。
- Markdown許可一覧、lint target設定、workflow: 変更していない。

## publication / CI

本レポート作成時点では実装commitはローカルで、push前である。
report/handoffを含む最終publication treeにrepository-defined full local gateを再実行してからpushする。
push後はPR current HEADとhead SHAが一致するworkflow runだけをCI証拠として使用し、別SHAのrunは代用しない。

## remaining risks / held

- H-DOC: 脚注本文を検査する現仕様と既存設計の脚注定義行除外記載の差は継続held。
- Windowsの既存 `cspell.cmd` spawn挙動は継続held。
- 独立最終レビューはfailのままであり、この実装担当はclosure verdictを出さない。

## next action

1. 同じ通常レビュアーで `IR81-01` / `IR81-02` のfix verificationを行う。
2. 通常fix verification収束後、独立最終レビューの同一レビュアー・同一ライフサイクルで `IR81-01` / `IR81-02` とCI deltaだけをclosure確認する。
3. 独立レビューがpassした場合だけ、予約済み独立最終レポートを既存reservation identityでattestationとして永続化する。
4. mergeは利用者が行うため実施しない。

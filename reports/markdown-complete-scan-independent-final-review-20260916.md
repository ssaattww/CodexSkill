# Markdown全文検査 独立最終レビュー

作成日時: 2026-09-17T09:08:55+09:00

## 判定

**pass_with_held**。変更点分の独立レビューで新規required findingはない。

- reviewed implementation HEAD: `d29dd07be76c55a78821002a56bed563d055214e`
- initial independent reviewed HEAD: `c2a21ecdf7e9e3d6bd74414eed087ea2af6aa346`
- initial independent review: `pullrequestreview-5221411529`
- reviewer continuity: 同じ独立レビュー会話を継続
- review mode: bounded independent final closure / change-delta review
- merge: 未実施

初回独立レビュー後に追加された実装変更を対象に、既存findingのclosure、追加要件、R81-07、およびexact-head CI deltaだけを確認した。独立レビュー中に実装変更は行っていない。

## 対象差分

初回独立HEADからcurrent HEADまでの実装変更は `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py` に集約される。report/handoff/evidenceの追加はレビュー履歴として確認した。
主要な変更は次の3系統。

1. `IR81-01`: 半角片仮名を許可語境界へ含め、prefix/suffix付き未登録語の部分マスクを防止。
2. `IR81-02`: `--files` の未解決・除外・対象外pathを明示診断付きexit 2にする。
3. 日本語許可判定: Sudachi `normalized_form` / `reading_form` を許可根拠にせず、term/aliasesの表面形と必要な幅差だけを許可する。さらにR81-07で一般NFKC互換展開と幅差を分離。

## Finding completeness matrix

| Finding | Required action | Production path | Actual composition fixture | Focused evidence | Disposition |
| --- | --- | --- | --- | --- | --- |
| IR81-01 | 幅違いを同一境界契約にし、未登録片仮名のprefix/suffix連結を拒否する | `build_whitelist_value_pattern` → mask → Japanese check | `ギア/ｷﾞｱ` exact相互表記、`ｷﾞｱｽ`、`ﾃｽﾄｷﾞｱ`、`ｷﾞｱス` | `latest-results.json` | **resolved** |
| IR81-02 | explicit targetの未解決・除外・対象外を無検査successにしない | `select_target_files` → `validate_explicit_targets` | valid `.md/.txt`、missing、ignored、mixed、unsupported、directory、outside | `latest-results.json` | **resolved** |
| R81-07 | 幅差だけを許可正規化し、一般NFKC互換表記は明示term/aliasなしで拒否する | `read_whitelist` → `japanese_terms` / `normalize_japanese_whitelist_term` → `check_japanese_tokens` | `㌔/キロ`、`㌢/センチ`、`㍑/リットル`、`㍍/メートル`両方向、explicit alias、Unicode互換139組 | `latest-results.json` | **resolved** |

通常レビュアー側でもIR81-01/02とR81-07のfix verificationがそれぞれ`pass_with_held`で収束済みであることを確認した。
## 独立focused validation

current HEADをFA780上の専用detached worktreeで固定し、SudachiPy実CLIをUTF-8固定で実行した。

### 日本語surface / reading / width契約

- `term: キャプチャー` + `キャプチャー`: allow
- `term: キャプチャー` + `キャプチャ`: reject
- `aliases: キャプチャ` を明示した場合: allow
- `term: ユーザー` + `ユーザ`: reject
- `term: アオリンゴ` + `青リンゴ`: reject
- `ギア` / `ｷﾞｱ`: 両方向allow
- `ｷﾞｱｽ`、`ﾃｽﾄｷﾞｱ`、`ｷﾞｱス`: reject

Sudachiのnormalized formまたはreadingだけが一致する表記を許可根拠にしないことと、既存の全角・半角片仮名幅差契約が維持されることを確認した。

### R81-07 compatibility契約
- `キロ` ↔ `㌔`: aliasなしでは両方向reject
- `センチ` ↔ `㌢`: aliasなしでは両方向reject
- `リットル` ↔ `㍑`: aliasなしでは両方向reject
- `メートル` ↔ `㍍`: aliasなしでは両方向reject
- `キロ` に `㌔` を明示alias登録したcontrol: 両表記allow

追加でUnicode全域を走査し、「1 code pointがNFKCで純片仮名列へ変換されるが半角片仮名runではない」互換表記を139組抽出した。`normalize_japanese_whitelist_term` がその互換元とNFKC展開先を同一値へ潰した組は **0/139** だった。

これにより、width-only正規化が一般のUnicode互換展開へ広がっていないことを独立に確認した。

### IR81-02 explicit target契約

- 実在する違反 `.md`: exit 1
- 実在する違反 `.txt`: exit 1
- missing: exit 2
- ignore directory: exit 2
- ignored prefix: exit 2
- valid + missing混在: exit 2
- unsupported suffix: exit 2
- directory指定: exit 2
- repository外path: exit 2

無検査のexit 0へ戻る回帰は確認していない。
## Local validation

reviewed implementation HEAD `d29dd07be76c55a78821002a56bed563d055214e` で実施した。

- independent focused fixture: 全ケース期待値一致
- Unicode compatibility invariant: 139組確認、width-only normalizerによる誤collapse 0件
- Python構文確認: pass
- `git diff --check c2a21ec...d29dd07`: pass
- `scripts/run_validation.py`: pass
  - repository: pass
  - bundle: pass
  - zip-integrity: pass
  - zip-contents: pass
- local diagnostics: `C:\Users\donabe\Project\CodexSkill-pr81-independent-delta-validation\latest-full-validation`
- focused evidence: `C:\Users\donabe\Project\CodexSkill-pr81-independent-delta-validation\latest-results.json`

## Exact-head CI

別SHAのrunは使用していない。

- `Validate and release ChatGPT worker skills` run `35163293417`: success
  - head SHA: `d29dd07be76c55a78821002a56bed563d055214e`
  - build job `105018674520`: success
  - exact HEAD checkout、repository architecture/link validation、ZIP build/verify、artifact uploadがsuccess
  - artifact `chatgpt-worker-skills-35163293417` (`10473109330`)
- `PR commit artifacts` push run `35163289057`: success
  - head SHA: `d29dd07be76c55a78821002a56bed563d055214e`
  - collect job `105018659909`: success
  - exact HEAD checkout、source archive、repository validation、stdout/stderr/test result記録、artifact uploadがsuccess
  - diagnostic artifact `pr-81-d29dd07be76c55a78821002a56bed563d055214e-35163289057-1` (`10473364035`)

同SHAのpull_request側 `PR commit artifacts` runは、same-repository synchronize経路では収集処理がskipされ得るため診断証拠には使用していない。push runのcollect結果を診断artifact根拠とした。

## Coverage dispositions

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| requirement / contract conformance | checked_no_finding | surface-only許可、width-only正規化、explicit target失敗契約を実CLIで確認 |
| correctness / edge cases | checked_no_finding | normalized/reading差、濁点を含む幅差、互換文字、prefix/suffix、missing/ignored/mixed targetを確認 |
| scope discipline | checked_no_finding | 実装差分はMarkdown whitelist checkerに限定。reviewerは実装修正していない |
| changed files / dependencies | checked_no_finding | SudachiPy実環境とcurrent HEADのproduction scriptを直接使用 |
| API / compatibility | checked_no_finding | `.md/.txt` explicit契約、幅差相互許可、明示aliasを維持 |
| error handling / diagnostics | checked_no_finding | unresolved explicit targetはexit 2 + stderr診断 |
| security / secrets | not_applicable | 認証・secret処理変更なし |
| validation adequacy | checked_no_finding | independent fixture + Unicode全域derived invariant + repository full validation |
| current-HEAD CI | checked_no_finding | `d29dd07...`一致runのみ採用 |
| report / documentation accuracy | held | H-DOC脚注設計差は既存held |
| regression / maintainability | checked_no_finding | IR81-01/02およびR81-07の直接回帰を同一current HEADで確認 |
## Held / remaining risks

- H-DOC: 脚注本文を検査する現仕様と、既存設計の「脚注定義行を検査対象外」とする記載の差は継続held。今回の変更差分とは別で非blocking。
- Windowsの既存 `cspell.cmd` spawn挙動は継続held。今回のcurrent implementation deltaはPython checkerのみで、cspell実装差分はない。
- Issue #85の引用原文例外は別scopeであり、本closureでは判定していない。

上記heldを除き、今回の変更点分について未解決required findingはない。

## Report attestation

この技術判定は `d29dd07be76c55a78821002a56bed563d055214e` に対するもの。

本ファイルは独立最終レビュー前からmetadata-onlyで予約されていた `reports/markdown-complete-scan-independent-final-review-20260916.md` を使用する。report-only attestation commitは次を満たすこと。

- first parentが reviewed implementation HEAD `d29dd07be76c55a78821002a56bed563d055214e`
- 変更pathは本report 1ファイルだけ
- executable / Skill / design / workflow / configuration / tracking / handoff / product pathを変更しない
- attestation後に別のGit commitを追加しない
- 技術判定はreviewed implementation HEADに紐付き、attestation commit自身はレビュー対象を拡張しない

## Next action

attestation allowlistを検証して公開し、その後はGit HEADを変更しない。mergeは利用者が行う。

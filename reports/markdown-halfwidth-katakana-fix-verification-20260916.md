# Markdown半角片仮名 R81-06 fix verification

作成日時: 2026-09-16T03:59:06.952706+00:00

## 判定

**pass_with_held**。R81-06はresolved。新規required findingはない。H-DOCとWindowsの既存cspell起動挙動はheldとして継続する。

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81`
- review mode: `fix_verification`
- reviewer: `chatgpt-pr81-normal-review-20260916`（同じ通常レビュー会話）
- previous review HEAD: `422207a52e574281147a721113421281cc5a686f`
- R81-06 implementation commit: `606b7e7d3d7fe000dc97d6541bac7d22c07c0247`
- reviewed implementation HEAD: `2c486628816b5f0c784ee454e56601ce86d9af00`
- base: `106ea5dcf12c4805756351fb9381df220b94f044`

`606b7e7d3d7fe000dc97d6541bac7d22c07c0247` 以後 `2c486628816b5f0c784ee454e56601ce86d9af00` までの実装・Skill・設計・workflow差分はなく、後続変更はR81-06対応report/handoffのみであることを確認した。

## Finding completeness matrix

| Finding | Required action | Production path | Actual fixture | Focused evidence | Disposition |
|---|---|---|---|---|---|
| R81-06 | 半角片仮名をNFKC/normalized formで検査し、分割境界も同じ契約にする | `contains_katakana` / `should_check_japanese` / `preserve_katakana_boundary` | 未登録/許可済みの全角・半角・濁点/半濁点・混在幅、48,000 byte境界12位置、2行目境界 | `/tmp/pr81-r81-06-rereview/focused-results.json` | **resolved** |

## Fix verification

R81-06の実装差分は `check-markdown-whitelist-sudachi.py` の11行追加・3行変更だけである。`contains_katakana` がNFKC後の片仮名を判定し、`should_check_japanese` はraw surfaceとSudachi `normalized_form`の双方を同じ判定へ通す。`preserve_katakana_boundary` も同じ判定を使用する。

独立した現HEAD実行で40 CLIケースを確認した。未登録の全角/半角、半角濁点 `ｷﾞｱ`、半角半濁点 `ﾊﾟﾗﾒｰﾀｰ`、混在幅を拒否し、全角/半角の許可語相互表記を許可した。`ｷﾞｱ` を48,000 byte境界付近12位置へずらした未登録/許可済み24ケースも期待通りだった。

分割性質は同12位置で、再結合一致、全chunkのSudachi入力長48,000 bytes以下、半角濁点語の内部にchunk境界が入らないことを確認した。2行目の半角片仮名は元行番号2を保持した。

R81-06が変更する分割・正規化経路の回帰として、R81-01の全角境界語とR81-05のNFKC膨張入力も再実行して成功した。R81-03の明示`.txt`/通常探索契約も再確認した。

## Validation / CI

- focused CLI: 40 cases pass
- chunk invariants: 12 cases pass
- repository validation: repository / bundle / zip-integrity / zip-contents 全てpass
- `git diff --check`: pass
- reviewed HEAD `2c486628816b5f0c784ee454e56601ce86d9af00` と一致する `Validate and release ChatGPT worker skills` run `35034918139`: success
- 同run build job `104601738394`: checkout / repository validation / ZIP build / artifact upload 全てsuccess
- artifact `10422364795` (`chatgpt-worker-skills-35034918139`)
- reviewed HEADと一致するpush run `35034914386`: success。collect job `104601727243` でexact HEAD checkout、source archive、validation、stdout/stderr記録、artifact uploadが全てsuccess
- diagnostic artifact `10422492764`

別SHAのCIは使用していない。

## Coverage dispositions
- **requirement and design conformance**: `checked_no_finding` — 設計上の片仮名語検査契約に半角表記もNFKC後の片仮名として合流することを確認。
- **correctness and edge cases**: `checked_no_finding` — 全角/半角、濁点/半濁点、混在幅、許可済み/未登録、境界位置12通りを現HEADで実行。
- **scope discipline**: `checked_no_finding` — R81-06実装差分はcheck-markdown-whitelist-sudachi.pyのみ。後続はreport/handoffのみ。
- **changed files and dependencies**: `checked_no_finding` — SudachiPy 0.6.11 / SudachiDict-core 20260428 / PyYAML 6.0.3を使用。
- **API and compatibility**: `checked_no_finding` — R81-01/R81-03/R81-05経路の回帰を再実行。cspell実装は前回から未変更。
- **tests and validation adequacy**: `checked_no_finding` — 独立focused 40 cases、chunk invariants 12 cases、repository validation 4/4 pass。
- **current-HEAD CI evidence**: `checked_no_finding` — 2c486628と一致するrun 35034918139 build success、push run 35034914386 diagnostics success。
- **report and documentation accuracy**: `held` — H-DOC: 脚注本文を検査する現仕様と既存設計の脚注定義行除外記載の差は継続。
- **regression and maintainability risks**: `checked_no_finding` — R81-06修正で触る分割・正規化経路のR81-01/R81-05回帰を確認し、新規required findingなし。

## Held / remaining risks

- H-DOC: 脚注本文を検査する現仕様と既存設計の脚注定義行除外記載の差は継続。今回の技術修正とは別で非blocking。
- Windowsの既存`cspell.cmd` spawn挙動は未解消。R81-06はPython checkerのみの変更で、cspell実装に差分はない。

## Next action

通常レビューcycleは `pass_with_held` として収束可能。report/handoff公開後のPR current HEADに対するexact-head CIを確認し、その後は独立最終レビューへ進める。mergeは行わない。

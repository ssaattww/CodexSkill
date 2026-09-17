# Markdown日本語許可判定 追加対応fix verification

作成日: 2026-09-17

## 判定

**fail（要修正）**。PR #81 comment `5704475283` の主要ケースは修正済みだが、同コメントが要求する「全角・半角の統一と、語の表記自体の置き換えを分ける」を満たさない `R81-07 / medium / coverage_miss` を1件確認した。

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#81 fix: make Markdown lint scan complete documents`
- review mode: `fix_verification`
- reviewer continuity: `chatgpt-pr81-normal-review-20260916`（同じ通常レビュー会話）
- previous normal-review HEAD: `df7c6c6be53e4f3d6e81b4e3c15aef188454b5dc`
- technical fix commit: `daeddaa5a5d5a626d1ad891a831f6476a9c530a4`
- reviewed HEAD: `c67370f985f5c0c1ee330f10ff5bbd500c72fe2a`
- authoritative requirement: PR comment `5704475283`

`daeddaa5...` 以後のcommitはreport/handoffのみで、実装・Skill・設計・workflow・設定に追加変更がないことを確認した。

## 追加要件の確認

- `term: キャプチャー` + `キャプチャー`: allow
- 同じ許可一覧 + `キャプチャ`: reject
- `alias: キャプチャ` を明示した隔離fixture: allow
- normalized-formだけ一致する `ユーザー` / `ユーザ`: reject
- readingだけ一致する `アオリンゴ` / `青リンゴ`: reject
- `ギア` / `ｷﾞｱ`: NFKCにより相互allow

上記はcurrent HEADを専用fixtureで直接実行し、期待値と一致した。
## R81-07 / medium / coverage_miss

場所: `skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py:491,621`

**内容:** 許可判定に使う `surface_normalized` と whitelist term/alias の正規化が `NFKC + casefold` のままであるため、全角・半角の幅差だけでなくUnicode互換文字の置換まで同一表記として扱う。

**影響:** 明示的に承認していない表記でも、NFKCで承認termへ展開されればwhitelist検査を通過する。これはcomment `5704475283` の「実際に記載された表記とterm/aliasに限定」「幅差と表記置換を分ける」という契約に反する。

**current HEADでの再現:**

| Approved term | Input | Expected | Actual |
|---|---|---:|---:|
| `キロ` | `㌔` | reject / 1 | allow / 0 |
| `センチ` | `㌢` | reject / 1 | allow / 0 |
| `リットル` | `㍑` | reject / 1 | allow / 0 |
| `メートル` | `㍍` | reject / 1 | allow / 0 |
| `㌔` | `キロ` | reject / 1 | allow / 0 |

比較元 `df7c6c6...` でも `term: キロ` + `㌔` はexit 0であり、新規退行ではない。今回の追加要件に対するfixture不足として `coverage_miss` に分類する。

**必要な対応:** 日本語の「許可判定用」の表記正規化を、幅差の同一視と一般的なNFKC互換置換から分離する。`ギア` / `ｷﾞｱ` の既存契約を維持しつつ、`㌔` / `キロ` のような互換表記は明示term/aliasがない限り拒否する。少なくとも上表の両方向fixtureを追加して確認する。

Sudachi `normalized_form` を診断用に残す変更自体には問題を確認していない。
## Validation

- Reviewer focused probe: 10ケース。commentの主要6系統は期待値一致、互換文字4ケースはR81-07として失敗を再現。
- 比較確認: `df7c6c6...` でも `キロ` / `㌔` はallowでありpre-existing behaviorを確認。
- repository validation: repository / bundle / zip-integrity / zip-contents 全てpass。
- Python構文 / `git diff --check`: pass。
- reviewed HEAD `c67370f...` と一致するCIのみを採用。
  - `Validate and release ChatGPT worker skills` run `35153871592`: success、build `104988533853` success、artifact `10470411579`。
  - `PR commit artifacts` push run `35153868102`: success、collect `104988520422` success、artifact `10470640735`。

Reviewer probeの入力、stdout/stderr、終了値は `reports/markdown-japanese-surface-whitelist-fix-verification-evidence-20260917.json` に保存する。

## Held

- H-DOC: 脚注本文の現仕様と既存設計記載の差。
- Windowsの既存 `cspell.cmd` spawn挙動。
- Issue #85の引用原文例外は別scope。

いずれもR81-07の判定とは別である。

## Next action

R81-07を修正し、width-only approval normalizationと互換文字の両方向fixtureを確認する。その後、同じ通常レビュアーでR81-07とCI deltaのみfix verificationする。通常レビューが再収束した後に、既存の独立最終レビューライフサイクルへ戻す。mergeはしない。

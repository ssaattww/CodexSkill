# Issue #79 Markdown用語検査導入 実装報告

## メタデータ

- Repository: `ssaattww/CodexSkill`
- Issue: `#79 CodexSkill自身へMarkdown用語検査を導入する`
- Branch: `issue-79-md-terms-v2`
- Base: `main` / `70cd31fbfdaed3f1b54151a8717e01ad86e329fd`
- Technical implementation HEAD: `1daa622d8fb325a1d715686144b2f68731c65a0a`
- Verification capability: `local_execution_available`
- Development policy: CodexSkill保守のためTDDは`not applicable`
- PR: report生成時点では未作成
- Merge: 実施しない

## 目的と範囲

CodexSkill自身のGit管理下Markdownに対し、既存の`markdown-word-checker`契約と`skills/review-enforcer/scripts/check-markdown-whitelist.js`を利用するrepo-local用語検査を導入した。

full/focusedの実行入口、対象設定、未登録語列挙、ローカル診断保存、CI診断保存を実装対象とした。文章の意味・読みやすさ判定は`document-wording-review`の責務として分離した。

`markdown-whitelist.yaml`の具体的な`term`、`aliases`、`description`、`prh.yml`、対象除外は利用者確認前に追加・変更していない。単独語の一般許可も追加していない。

## 作業環境

- Device: `FA780`
- OS: Windows
- Worktree: `C:\Users\donabe\Project\CodexSkill-issue-79-md-terms-v2`
- Git remote: `origin https://github.com/ssaattww/CodexSkill.git`
- Git commit/pushはRDC経由で実行する方針
- Git global設定、認証設定は変更していない

## 既存作業の保全

既存の`C:\Users\donabe\Project\CodexSkill-issue-79-md-terms`は、旧mainを基点にした未コミット変更を含んでいた。これをreset/stashせず保全し、最新`origin/main`から専用worktreeを作成した。

既存remote branchの#79 commitを最新mainへ再適用し、旧worktreeにだけ存在した設計・Skill・workflow path trigger差分も内容を確認して取り込んだ。元worktreeの差分は`C:\Users\donabe\Project\issue79-scratch\local-extra.patch`へ退避し、SHA-256は`639E37C63C41781694A3C4126CEF528F0FCA2F9BC5307CED56FBBC46A9617D9E`である。

## 実装内容

- `package.json` / `package-lock.json`を追加し、`yaml`依存とMarkdown用語検査のnpm scriptsを定義した。
- `tools/lint/markdown-targets.json`を追加し、導入時点の対象除外を空として明示した。
- `tools/lint/markdown-whitelist.yaml`を`entries: []`で追加し、具体的許可語を自動追加しない初期状態とした。
- `tools/lint/run-markdown-word-check.js`でGit管理下のMarkdownのみをfull検査へ渡す経路を追加した。
- `npm run lint:md` / `lint:md:unknown`をfull、`lint:md:changed` / `lint:md:changed:unknown`をfocusedの入口とした。
- `markdown-word-checker` Skillと設計へ、CodexSkill自身を明示的lint対象にできる契約と利用者レビュー境界を追加した。
- workflowのpath triggerへ`package.json`、`package-lock.json`、`tools/lint/**`を追加した。
- CIで`npm ci --ignore-scripts`を実行し、そのstdout/stderrと成否を既存診断artifactへ保存するようにした。
- `scripts/run_validation.py`へfull未登録語列挙を組み込み、stdout/stderr、exit code、未登録語件数を既存`results.json` / `results.xml`へ保持するようにした。

## 初期導入gate

許可一覧が正確に`entries: []`の間だけ、full未登録語検査のexit 1を`needs_user_review`として記録し、全体validationを失敗にしない。この例外は初期候補抽出期間だけに限定した。

利用者確認済みの許可一覧が1件以上入った後に未登録語が残れば、同じexit 1は通常のfailureとして全体validationを失敗させる。用語検査の失敗を恒久的に非blockingにする実装ではない。

## 診断artifact workflow

作業開始時点の`.github/workflows/release-chatgpt-worker-skills.yml`には、`scripts/run_validation.py`が生成する結果、標準出力、標準エラー等を`always()`でartifactへ保存する経路が存在した。新規workflowは追加せず、この既存経路を維持した。

## ローカル検証

初期候補抽出では、`npm run lint:md:unknown`がexit 1となり、未登録英字・カタカナ語を列挙できることを確認した。専用worktreeの`run_validation.py`実行では3446種類の未登録語を検出し、`markdown-terminology`を`needs_user_review`として記録した。

`python scripts/run_validation.py --output-dir validation-artifacts/issue79-runner-precommit`の結果は次のとおりだった。

- repository: pass / exit 0
- markdown-terminology: needs_user_review / underlying exit 1 / 3446 unregistered terms
- bundle: pass / exit 0
- zip-integrity: pass / exit 0
- zip-contents: pass / exit 0
- aggregate: pass / runner exit 0

`source.json`へ`package.json`と`tools/`配下がfingerprint対象として記録されることも確認した。

focused経路は、Markdown変更がない状態では`npm run lint:md:changed:unknown`がexit 0となった。`tools/lint/README.md`を変更した状態ではexit 1となり、`Actions`、`artifact`、`CodexSkill`、`Git`、`GitHub`、`Markdown`、`repository`等の未登録語を列挙した。これにより変更Markdownだけを対象にする経路も実行できることを確認した。

`npm ci`はRDC上で`cmd.exe`経由でexit 0。PowerShellの`npm.ps1`はExecution Policyで直接実行できないため、ローカルnpm検証は`cmd.exe`経由とした。CIはUbuntu上の`npm`を使用する。

## Findings / held items

- 未登録語3446種類は、許可語として承認済みではない。機械抽出結果であり、具体的な許可一覧変更はheldとする。
- `prh.yml`は今回追加していない。必要な表記補正規則が決まった場合は、具体的ruleを利用者確認してから追加する。
- `markdown-targets.json`の除外は空。除外追加は検査範囲を狭めるため、具体的変更を利用者確認してから行う。
- document-wording-reviewによる意味・読みやすさの独立判定は、本実装chatのreview verdictとしては実施していない。

## CI / publication state

report生成時点ではbranchは未push、PRは未作成であり、current HEAD一致CIは未実施である。report/handoff保存後の最終commitをRDC経由でpushし、GitHub connectorでPRを作成した後、そのPR current HEADとrunのhead SHAが一致する`pull_request` workflow runだけを最終CI証拠として扱う。

## 変更対象と非対象

主要変更対象は`.github/workflows/release-chatgpt-worker-skills.yml`、`.gitignore`、`package.json`、`package-lock.json`、`tools/lint/**`、`scripts/run_validation.py`、`design/markdown-word-check-skill-design.md`、`skills/markdown-word-checker/SKILL.md`である。

`tasks/tasks-status.md`にはIssue #79の既存task entryがなく、今回新規task IDは作成していない。既存の他Issue用worktree、他branchの内容、具体的whitelist entriesは変更していない。

## 残リスク

初期許可一覧が空のため、用語gateは候補抽出状態である。利用者が許可語・表記補正・対象除外の具体案を確認するまでは、未登録語0件の状態にはならない。

CI上でnpm依存導入と用語検査が実際に動作することは、PR作成後のcurrent HEAD一致runで確認する必要がある。別SHAのworkflow runは代用しない。

## 次の操作

1. 本reportとhandoffをcommitする。
2. 最終commit HEADでローカル同等検証を再実行する。
3. RDC経由でbranchをpushする。
4. GitHub connectorでPRを作成する。
5. PR current HEADと一致する`pull_request` workflow runだけを確認する。
6. 変更内容、ローカル検証、exact-head CI、held項目を簡易PRコメントへ記録する。
7. mergeは利用者が行う。

## Persistence

- Report path: `reports/issue-79-markdown-terminology-implementation-20260915.md`
- Handoff path: `reports/handoffs/issue-79-markdown-terminology-20260915.yaml`
- Report生成時のrepository commit state: `commit_pending`
- Technical HEAD: `1daa622d8fb325a1d715686144b2f68731c65a0a`
- Administrative parent: `1daa622d8fb325a1d715686144b2f68731c65a0a`

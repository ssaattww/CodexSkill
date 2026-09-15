# Issue #73 RDC Git操作対応 実装報告

## メタデータ

- Repository: `ssaattww/CodexSkill`
- Issue: `#73 git操作のrdc化`
- PR: `#78`
- Branch: `issue-73-rdc-git`
- Base: `main` / `106ea5dcf12c4805756351fb9381df220b94f044`
- Technical implementation HEAD: `ce445faa71eedf60b73ee9497bd1d6c1d484ec7c`
- Verification capability: `local_execution_available`
- Development policy: CodexSkill保守のためTDDは`not applicable`
- Merge: 実施しない

## 目的

Remote Desktop Commanderを利用できるPC接続経路では、ファイル操作と検証だけでなく、認可された`git commit`と`git push`も接続PC上でRDC経由で実行する。RDC上のソースをChat環境へ転送して公開内容を再構成する経路は使用しない。

GitHub connectorはremote repository evidence、Issue、PR、PR comment、current HEADに一致するCI evidenceの取得に使用する。端末`gh`、直接REST呼び出し、無断のGit認証設定変更は許可しない。

## #70復元

current main `106ea5d`では、PR #72でmainへ取り込まれていた#70のRDC実行経路の主要内容が#68取り込み時に欠落していた。#70のsquash merge `62a7ddf3dce5c40df0a7c36a5aff27b4702cb47c`の差分をcurrent mainへ3-wayで復元し、#68/#69の後続内容は保持した。

復元commitは`9832e116cb4939401e4cbf14d58a5b1a854edf6d`。専用execution-environment設計、ChatGPT wrapper、execution environment evidence契約、#70の実装報告・通常レビュー報告・handoffを復元した。

PR #72はmerged済みで、当時の通常レビューは`pass_with_held`、required finding 0件だった。これは#70の履歴証拠であり、#73の現行HEADに対するレビューまたはCI証拠としては使用しない。

## #73実装内容

- `chat-implementation-worker`で、接続PC経路のlocal source read/edit/dependency check/validationに加えて、認可されたGit commit/pushをRDCへ固定した。
- `chat-review-worker`で、許可されたreview reportのcommit/pushをRDC経由とし、review対象treeをChat環境へ転送して公開しない契約を追加した。
- `chat-report-writer`で、許可されたreport/handoffのcommit/pushをRDC経由とし、GitHub connectorの責務をremote evidence、PR、comment、CIへ限定した。
- `design/chat-execution-environment-design.md`へ#73のsuperseding ruleを追加し、RDC push失敗時はblockedとして別publication経路へ切り替えないことを定義した。
- `design/chat-worker-skill-design.md`、Project Instruction例、hierarchy設計2ファイルを同じ操作境界へ同期した。
- `tasks/tasks-status.md`へT-007、`tasks/phases-status.md`へPhase 11を追加した。

## 実行環境

- Device: `FA780`
- OS: Windows
- Worktree: `C:\Users\donabe\Project\CodexSkill-issue-73-rdc-git`
- Ownership: Issue #73専用worktree
- Git remote: `origin https://github.com/ssaattww/CodexSkill.git`
- RDC経由でbranch作成、編集、ローカル検証、commit、pushを実施した。
- Git認証設定、global Git設定、管理者設定は変更していない。

## 診断artifact workflow確認

`.github/workflows/pr-commit-artifacts.yml`に、`scripts/run_validation.py`の結果、標準出力、標準エラー、source archive、job statusを成功・失敗の双方で`always()` uploadする処理が存在することを確認した。新しいworkflow追加は不要と判断した。

## ローカル検証

#70復元差分に対し、`git diff --cached --check`と`scripts/run_validation.py`を実施し、repository / bundle / ZIP integrity / ZIP contentsが全てpassした。診断保存先は`C:\Users\donabe\Project\CodexSkill-issue-73-artifacts\restore70-validation`。

#73実装差分に対し、`git diff --check`、`scripts/run_validation.py`、hierarchy設計2ファイルのbyte一致確認を実施し、全てpassした。診断保存先は`C:\Users\donabe\Project\CodexSkill-issue-73-artifacts\implementation-validation`。

handoff YAMLはタスク専用scratchに導入した`yaml`パーサーで構文解析し、schema version 3とnext actionを確認した。repository依存は変更していない。

report／handoff／trackingを含むpublication candidateでは、同じ--output-dirを再利用した再実行がrunnerの出力先新規性チェックによりexit 2となり、validation step自体は開始されなかった。この失敗stdout/stderrも保持した。その後は毎回新規保存先で再実行し、git diff --check、repository、bundle、ZIP integrity、ZIP contents、hierarchy byte一致、handoff YAML parseが全てpassした。losslessなsource payload補強後の最終検証結果と診断保存先は、永続化後のPR commentへ記録する。

検証済みtechnical HEADは`ce445faa71eedf60b73ee9497bd1d6c1d484ec7c`。このreportとhandoffの保存でGit HEADは更新されるため、最終CIはreport/handoff commit後のPR current HEADに一致する`pull_request` runだけを確認する。`ce445fa`以前のrunは最終CIの代用にしない。

## 未実施・残リスク

- #73変更に対するnormal reviewおよびindependent final reviewはこの実装chatでは実施していない。実装者自身の確認をreview verdictとして扱わない。
- report/handoff保存後のfinal HEADに対するmatching CIはreport生成時点では未確定。
- 実機で確認したRDC pushは今回のIssue #73 branchへのpushで成功した。認証失敗時のfallbackを実行していないため、失敗時動作は契約上のblocked規則として保持する。
- #69の欠落内容は今回の#70復元・#73 scopeには含めない。

## 次の操作

1. 本reportとhandoffをrepositoryへ保存してcommitする。
2. commit/pushをRDC経由で実行する。
3. GitHub connectorでPR #78を更新し、PR current HEADと一致するworkflow runだけを確認する。
4. 簡易reportをPR commentへ投稿する。
5. mergeは利用者が行う。

## Persistence

- Report path: `reports/issue-73-rdc-git-implementation-20260915.md`
- Handoff path: `reports/handoffs/issue-73-rdc-git-20260915.yaml`
- Report生成時のrepository commit state: `commit_pending`
- Technical HEAD: `ce445faa71eedf60b73ee9497bd1d6c1d484ec7c`
- Administrative parent: `ce445faa71eedf60b73ee9497bd1d6c1d484ec7c`

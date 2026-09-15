# PR #78 通常レビュー指摘対応報告

## メタデータ

- Repository: `ssaattww/CodexSkill`
- Issue: `#73 git操作のrdc化`
- PR: `#78`
- Mode: `review follow-up`
- Initial reviewed HEAD: `85c47515cbe086824746534ffb6cf6398894a63a`
- Initial review artifact HEAD: `ae63a10abd1797d7fc81f234ad7b2bfb947054dd`
- Fix candidate technical HEAD: `ac1bff201f8d6f0e8974f3ab5a42b177109a5a15`
- Execution environment: RDC / `FA780` / Issue #73 dedicated worktree
- Development policy: CodexSkill maintenance, TDD `not applicable`
- Review verdict: この実装chatでは発行しない
- Merge: 実施しない

## 対象

通常レビューでrequired finding 4件が報告された。finding identity、severity、reviewed HEADを維持し、各required actionの直接原因と同一欠陥クラスだけを修正した。

参照:
- `reports/issue-73-pr78-normal-review-20260915.md`
- `reports/handoffs/issue-73-pr78-normal-review-20260915.json`

## Finding対応

### PR78-NR-001 / medium / required

- Required action: 埋め込みRevMem向けProject Instruction例を#73の操作境界へ同期する。
- Fix: `design/chat-worker-skill-design.md` の旧connector publication指示を、GitHub connector=remote evidence/Issue/PR/comment/current-HEAD CI、RDC=PC上の認可済みgit commit/pushへ変更した。
- Commit: `2c471faa9ae8c165f4ae5a0fc3fb4cc295cc3403`
- Focused evidence: 旧文言が消え、`認可されたgit commit／pushは接続PC上でRDC経由` が存在することを確認。

### PR78-NR-002 / medium / required

- Required action: `commands[].execution_environment`をschemaどおり`object | null`にする。
- Fix: `reports/handoffs/issue-73-rdc-git-20260915.yaml` の3 commandをtop-level execution environment objectのYAML alias `*a2`へ変更した。
- Commit: `6e0135355a085d40ce47454f436e6d37a35c6c87`
- Focused evidence: YAML parse後 `commands=3`, `bad_count=0`。各objectの`machine_id=FA780`、`repository=ssaattww/CodexSkill`を確認。

### PR78-NR-003 / medium / required

- Required action: #70当時の履歴とcurrent package契約を分離し、実際の配布構成へ同期する。
- Fix: #69統合時の9スキルは履歴、#68後のcurrent main/#73では`document-wording-review`が存在せず、#73では#69を復元しないためcurrent packageは4 wrapper + 4 coreの8スキル、と設計を統一した。
- Commit: `d55e955283fed3ae26a4ce47e98ccb4f51f041a6`
- Focused evidence: hierarchy 2ファイルbyte-identical。builderで生成したZIP rootは8件で、`document-wording-review`は含まれない。
- 同一欠陥クラスとして、execution designの古い「#69未マージ」表現と診断workflowの歴史記述も現在事実と履歴を分離した。

### PR78-NR-004 / low / required

- Required action: Phase 11とUpdated日付を現在状態へ同期する。
- Fix: `tasks/phases-status.md`を`Updated: 2026-09-15`、Phase 11をnormal review findings follow-up / same reviewer fix verification pendingへ更新した。T-007もinitial review failと4 finding follow-upへ同期した。
- Commit: `ac1bff201f8d6f0e8974f3ab5a42b177109a5a15`
- Focused evidence: phases/tasks双方でinitial review fail、`PR78-NR-001`〜`004`、same reviewer fix verification待ちを確認。

## ローカル検証

Fix candidate `ac1bff201f8d6f0e8974f3ab5a42b177109a5a15` のclean worktreeで実施した。

- `git diff --check 85c47515...ac1bff2`: success
- `python scripts/run_validation.py`: success
  - repository: pass
  - bundle: pass
  - ZIP integrity: pass
  - ZIP contents: pass
- PR78-NR-001 focused check: pass
- PR78-NR-002 schema type check: pass (`commands=3`, `bad_count=0`)
- PR78-NR-003 package check: pass（8 root、hierarchy byte一致）
- PR78-NR-004 tracking check: pass
- 診断保存先: `C:\Users\donabe\Project\CodexSkill-issue-73-review-fix-artifacts\full-validation-ac1bff2`
- validationのstdout/stderr、focused check出力、commit/file一覧を保存した。
- report/handoff/trackingを含む永続化候補でも `git diff --cached --check`、repository / bundle / ZIP、handoff JSON検証を実施し、全項目passを確認した。
- 永続化候補の診断はIssue #73 review-fix専用artifact directoryへ保存し、最終保存先はPR commentへ記録する。

## CIと公開状態

4 fix commitはすべてRDC経由でcommit/push済み。local routeのnormal review/fix loopではCI完了をfix条件にしない。

本report/handoff/tracking同期をcommit/pushした後、PR current HEADと一致するworkflow runだけを確認し、結果はPR metadata/commentへ記録する。別SHAのrunは代用しない。

## 残リスクと次操作

- 4 findingのresolved判定は実装者では行わない。
- 同じnormal reviewerによる`fix_verification`が必要。
- normal review cycle収束後にのみ独立最終レビューへ進む。
- mergeは利用者が行う。

## Persistence

- Report path: `reports/issue-73-pr78-review-followup-20260915.md`
- Handoff path: `reports/handoffs/issue-73-pr78-review-followup-20260915.json`
- Report生成時のcommit state: `commit_pending`
- Technical HEAD: `ac1bff201f8d6f0e8974f3ab5a42b177109a5a15`
- Administrative parent: `ac1bff201f8d6f0e8974f3ab5a42b177109a5a15`

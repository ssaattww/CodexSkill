# Issue #51 ChatGPT Chat Worker Skill 実装レポート R5

## 概要

利用者負担を下げるため、ChatGPT chat workerの入力contractを見直した。

- 全workerに成果物reportを必須化した
- Issue番号またはPR番号から取得できる情報はworker自身がconnectorで解決する
- HEAD SHA、handoff path、report path、branchは原則として利用者へ要求しない
- Project Instructionにある固定方針は各promptで再掲しない
- CodexSkill repository自身へ導入していたMarkdown contract testと専用workflowを撤去した

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- PR: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Report作成前HEAD: `736305f8c3604576205eac81cb3dbaf542d50911`
- 現在確認済みHEAD: `0269bc6f9e0262b06e6fcd8dc3869a1e59ac4c78`

## 変更したSkill

### `chat-implementation-worker`

- implementation reportを必須成果物とした
- IssueまたはPRからbranch、HEAD、設計、report、handoff、CIを自己解決する
- 利用先Project Instructionの実装・test方針に従う
- CodexSkill固有のTDDを強制しない

### `chat-review-worker`

- review reportとPR簡易コメントを必須成果物とした
- PR番号からcurrent HEAD、linked Issue、過去review、fix commits、handoff、CIを自己解決する
- SHAまたはpathを利用者へ聞くのは候補が一意でない場合だけとした

### `chat-report-writer`

- PRまたはIssueからsource reportsとhandoffsを自己解決する
- 利用者によるsource path列挙を通常不要とした

## 設計書

正本を次の1ファイルへ集約した。

- `design/chat-worker-skill-design.md`

重複していた`skills/design/chat-worker-skill-design.md`は削除した。

設計書には、現在のRevMem Project Instructionを固定前提の具体例として記載した。

## 利用者prompt

通常flowは次のpromptだけで開始できる。

```text
Issue #<number>を開始してください。
```

```text
PR #<number>を初回レビューしてください。
```

```text
レビュー結果に対応してください。
```

```text
PR #<number>の修正確認をしてください。
```

```text
PR #<number>を独立レビューしてください。
```

HEAD SHA、handoff path、branch、report pathは、repositoryから一意に解決できない場合だけ利用者へ確認する。

## CodexSkillでの検証方針

CodexSkillはSkill Markdown repositoryであり、Markdown lintや正式なSkill schema検証が有効化されていない。この変更のためだけに形式的なTDDを持ち込まない。

次を撤去した。

- `tests/test_chat_worker_skills_contract.py`
- `.github/workflows/chat-worker-skill-contract.yml`

過去のTDD・workflow記録は旧方針の履歴であり、本R5で置き換える。

現在は設計書、Skill、handoff contract、利用例の差分reviewで確認する。将来repository全体へ正式なlintまたはschema検証が導入された場合のみ、その既存基盤へ統合する。

## 成果物方針

- implementation worker: implementation report + handoff + PR簡易コメント
- review worker: review report + handoff + PR簡易コメント
- report writer: requested report + handoff + PR簡易コメント

handoffはreportの代替ではない。

## 未実施

- 独立review
- 実際の複数ChatGPT chatを用いたoperational trial

## マージ

マージは実施していない。

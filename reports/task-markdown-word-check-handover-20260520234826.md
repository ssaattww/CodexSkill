# Markdown 単語チェック skill 設計 引き継ぎ資料

## 目的

CodexSkill リポジトリで、複数リポジトリに適用できる Markdown 単語チェック / 用語検査の仕組みを作る。

利用者の最終意図は、IbisDuck 専用の用語整理ではなく、各リポジトリ固有の `tools/lint/` 設定を読み込み、review skill と Markdown 資料作成 skill から共通利用できる `markdown-word-checker` skill を CodexSkill 側に追加することである。

今回のチャットでは、そのための設計を作成し、利用者が設計を承認した。

## 対象リポジトリ

- リポジトリ: `/home/ibis/AI/CodexSkill`
- 現在の branch: `docs/markdown-word-checker-design`
- upstream: `origin/docs/markdown-word-checker-design`
- base: `main`
- 関連 issue: `#40` `Markdown単語チェックskillの設計を追加する`
- 関連 PR: `#41` `docs: Markdown単語チェックskill設計を追加する`
- PR URL: `https://github.com/ssaattww/CodexSkill/pull/41`
- 現在 commit: `02adf4c docs(markdown-word-check): 単語チェックskill設計を追加`

## 現在の Git / PR 状態

確認時点の状態:

- `git status --short --branch`: `docs/markdown-word-checker-design...origin/docs/markdown-word-checker-design`
- 作業ツリー: handover 作成前は clean
- PR #41: open
- PR #41 draft 状態: false
- PR #41 merge state: `CLEAN`
- PR #41 status checks: なし
- PR #41 review decision: 空

この handover report 自体は、作成直後は未 commit の新規ファイルになる。

## 作成済み成果物

### 設計文書

- `design/markdown-word-check-skill-design.md`

主な設計内容:

- 新規 skill 名は `markdown-word-checker`。
- 作業者へ出すルールは Markdown lint の実行、指摘対応、不適切な指摘の lint 設定見直し報告だけに限定する。
- repo 固有用語は CodexSkill に持たず、対象 repo の `tools/lint/markdown-whitelist.yaml`、`tools/lint/prh.yml`、`tools/lint/markdown-targets.json` などから読む。
- `review-enforcer` は Markdown lint 詳細を直接持たず、`markdown-word-checker` を呼ぶ。
- Markdown 資料作成 skill は、資料作成後に `markdown-word-checker` を呼ぶ。
- 初期実装では既存 shared script を `skills/review-enforcer/scripts/` から移動しない。
- 複数 repo 対応のため、設定不足時の `skip` / `unsupported` / `failed gate` を定義する。
- lint 証跡収集を sub-agent に委譲する場合の report 契約を定義する。
- backtick / quote による lint 回避チェックを required flow / output contract / 完了条件へ残す。
- whitelist / prh の exact entry 変更は利用者レビュー必須とする。

### レビュー / 修正レポート

- `reports/task-markdown-word-check-design-review-20260520230107.md`
- `reports/task-markdown-word-check-design-fix-20260520230537.md`
- `reports/task-markdown-word-check-design-review-r2-20260520230107.md`

初回 review 指摘:

1. 複数 repo 対応の最低構成と fallback が曖昧。
2. sub-agent に lint 証跡収集を委譲する場合の report 契約が不足。
3. backtick 回避チェックが required flow / output contract に明示されていない。

修正結果:

- 上記 3 件を `design/markdown-word-check-skill-design.md` に反映した。
- r2 review は `no findings`。

## 利用者が承認した事項

利用者は次を明示した。

- 「設計を承認します。」

承認対象は、PR #41 に含まれる `design/markdown-word-check-skill-design.md` の設計である。

## 合意済みの作業方針

### 親 agent の役割

今後の実装・修正作業は sub-agent に委譲する。

親 agent は次を担当する。

- 設計、範囲決定、委譲内容の作成。
- sub-agent report の事前作成。
- sub-agent 結果の確認と判断。
- review gate の管理。
- commit / push / PR 管理。

親 agent は、実装・修正作業を直接進めない。

### sub-agent の役割

sub-agent は、親が指定した範囲で次を実施する。

- 設計修正。
- skill 実体の作成。
- 既存 skill の更新。
- 検証や review。
- report の空欄記入。

sub-agent には、必ず対象 skill、対象ファイル、対象外、report path、検証コマンドを明示する。

### Markdown / lint 方針

作業者に細かい語彙規則を知らせない。

作業者向けに出すルールは次だけ。

```text
Markdown 資料を作成または編集したら、このリポジトリの Markdown lint を実行してください。
lint の指摘に従って本文を直してください。
指摘が不適切に見える場合は、回避せず lint 設定見直しとして報告してください。
```

細かい用語判断は `markdown-word-checker` と repo 固有 lint 設定に閉じ込める。

## 実行済みコマンド / 検証

主な実行:

- `git diff --check`
- sub-agent design review
- sub-agent design fix
- sub-agent r2 design review
- `gh issue create ...`
- `git push -u origin docs/markdown-word-checker-design`
- `gh pr create ...`
- `gh pr edit 41 --body-file -`
- `gh pr view 41 --json ...`

検証結果:

- `git diff --check`: 成功
- 初回 design review: 指摘あり
- design fix: 実施済み
- r2 design review: no findings
- PR #41: 作成済み
- PR #41 body: 作成時に shell 展開で崩れたため、`gh pr edit --body-file -` で修正済み

## 注意点

- CodexSkill リポジトリ直下には確認時点で `package.json` が見つからなかったため、Markdown lint は実行していない。
- PR #41 は設計追加のみであり、`skills/markdown-word-checker/SKILL.md` の作成、既存 skill の変更、shared script の移動はまだ行っていない。
- `design/skill-hierarchy-design.md` と `skills/design/skill-hierarchy-design.md` の更新は、実際に `markdown-word-checker` skill を追加する後続作業で必要になる。
- PR #41 の commit にはこの handover report は含まれていない。

## 未解決項目

1. PR #41 を merge する。
2. merge 後、`markdown-word-checker` skill 実装用の新しい作業 branch を切る。
3. `skills/markdown-word-checker/SKILL.md` を追加する。
4. `review-enforcer/SKILL.md` から Markdown lint 詳細を `markdown-word-checker` 参照へ寄せる。
5. `design-executor` と `handover-memo-writer` に、Markdown 作成後の `markdown-word-checker` 呼び出し契約を追加する。
6. `design/skill-hierarchy-design.md` と `skills/design/skill-hierarchy-design.md` を同期更新する。
7. 必要なら、shared script の移動は別 task として後続に切り出す。

## 次チャットで最初に確認すること

1. `/home/ibis/AI/CodexSkill` で `git status --short --branch` を確認する。
2. PR #41 の状態を `gh pr view 41 --json state,mergeStateStatus,reviewDecision,statusCheckRollup` で確認する。
3. PR #41 が未 merge なら、利用者に merge するか確認する。
4. PR #41 が merge 済みなら、`main` を最新化して、`markdown-word-checker` skill 実装用の branch を作る。
5. 実装は sub-agent に委譲する。親 agent が直接実装しない。

## 次チャット用プロンプト

```text
/home/ibis/AI/CodexSkill で Markdown 単語チェック skill の作業を続けてください。

まず AGENTS.md と development-orchestrator / git-workflow-manager / skill-authoring-wrapper / review-enforcer / sub-agent-task-manager を確認してください。

現在の前提:
- 設計 PR #41 `docs: Markdown単語チェックskill設計を追加する` は作成済みです。
- 設計文書は `design/markdown-word-check-skill-design.md` です。
- 利用者は設計を承認済みです。
- 初回 review は指摘あり、修正後 r2 review は no findings です。
- 関連 report:
  - `reports/task-markdown-word-check-design-review-20260520230107.md`
  - `reports/task-markdown-word-check-design-fix-20260520230537.md`
  - `reports/task-markdown-word-check-design-review-r2-20260520230107.md`
  - `reports/task-markdown-word-check-handover-20260520234826.md`

重要な方針:
- 今後の実装・修正作業は sub-agent に委譲してください。
- 親 agent は、設計、範囲決定、委譲、report 確認、Git/PR 管理を担当してください。
- 作業者には細かい用語規則を知らせず、Markdown lint を実行し指摘に従う運用だけを示す方針です。
- repo 固有用語は CodexSkill 側へ持ち込まず、対象リポジトリの `tools/lint/` から読み込む設計です。

最初にやること:
1. PR #41 の状態を確認してください。
2. 未 merge なら merge 方針を確認してください。
3. merge 済みなら main を最新化し、`markdown-word-checker` skill 実装の branch を切ってください。
4. 実装作業は sub-agent に委譲してください。
```

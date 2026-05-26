# Markdown 単語チェック skill 実装 引き継ぎ資料

## 目的

この handover は、CodexSkill リポジトリで進めている `markdown-word-checker` skill の設計・初期実装 PR を、次のチャットで同じ前提のまま再開できるようにするための資料である。

最終目的は、複数リポジトリに適用できる Markdown 単語チェック / 用語検査の共通 skill を CodexSkill 側へ追加し、Markdown 資料作成 skill と review skill が細かい語彙規則を直接持たずに使える状態にすることである。

## 対象リポジトリ

- リポジトリ: `/home/ibis/AI/CodexSkill`
- branch: `docs/markdown-word-checker-design`
- upstream: `origin/docs/markdown-word-checker-design`
- base: `main`
- 関連 issue: `#40` `Markdown単語チェックskillの設計を追加する`
- 関連 PR: `#41` `docs: Markdown単語チェックskill設計を追加する`
- PR URL: `https://github.com/ssaattww/CodexSkill/pull/41`
- 現在 commit: `cb6e00e fix(markdown-word-check): clarify gate flow`

## 現在の Git / PR 状態

確認時点の状態:

- `git status --short --branch`: `docs/markdown-word-checker-design...origin/docs/markdown-word-checker-design`
- 作業ツリー: この handover report 作成前は clean
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
- whitelist / prh / target 除外の exact entry 変更は利用者レビュー必須とする。
- focused lint と full lint は check scope ごとの個別 result と aggregate gate state で扱い、片方の pass が片方の `failed gate` / `needs user review` / `unsupported` を上書きしない。
- exact entry review 後は、設定編集 owner、再 lint、同一 caller report 更新まで完了しないと gate を閉じない。
- `unsupported` は pass ではなく caller disposition が必要な状態として扱う。

### 実装済み skill / 変更済み skill

- `skills/markdown-word-checker/SKILL.md`
- `skills/markdown-word-checker/agents/openai.yaml`
- `skills/review-enforcer/SKILL.md`
- `skills/design-executor/SKILL.md`
- `skills/handover-memo-writer/SKILL.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`

実装内容:

- `markdown-word-checker` を repo-local standard sections で追加した。
- `markdown-word-checker` は target repo root、Markdown file list、caller gate context、repo-local `tools/lint/` 設定、package lint wiring を入力にする。
- 出力には per-scope check result、aggregate gate state、`skip` / `unsupported` / `failed gate` / `needs user review`、backtick / quote evasion、exact entry review 要否、sub-agent report path を含める。
- `review-enforcer` は Markdown 関連変更で `markdown-word-checker` を呼び、結果を review report に含める。
- `design-executor` と `handover-memo-writer` は、作成または編集した Markdown file list を `markdown-word-checker` へ渡し、focused lint 結果を caller report に残す契約を持つ。
- hierarchy design 2 ファイルは同期更新済み。

### 追加 commit

- `02adf4c docs(markdown-word-check): 単語チェックskill設計を追加`
- `98c1b1f docs(markdown-word-check): clarify term routing flow`
- `b95d63d feat(markdown-word-check): add checker skill`
- `cb6e00e fix(markdown-word-check): clarify gate flow`

## レビュー / 検証レポート

### 設計 review

- `reports/task-markdown-word-check-design-review-20260520230107.md`
- `reports/task-markdown-word-check-design-fix-20260520230537.md`
- `reports/task-markdown-word-check-design-review-r2-20260520230107.md`

結果:

- 初回 review は指摘あり。
- 修正後 r2 review は no findings。

### 新語ルーティング review

- `reports/task-markdown-word-check-term-routing-design-audit-20260521204755.md`
- `reports/task-markdown-word-check-term-routing-design-fix-20260521205114.md`
- `reports/task-markdown-word-check-term-routing-design-review-20260521205510.md`

結果:

- 当初は新語を本文修正、whitelist `term`、`aliases`、`prh.yml`、設定状態、利用者 exact entry review へ分類する決定表が不足していた。
- 決定表を追加し、review は no findings。

### ユーザーフロー思考実験

- `reports/task-markdown-word-check-user-flow-author-audit-20260521211429.md`
- `reports/task-markdown-word-check-user-flow-review-audit-20260521211429.md`
- `reports/task-markdown-word-check-user-flow-design-fix-20260521211944.md`
- `reports/task-markdown-word-check-user-flow-design-review-20260521212259.md`

結果:

- author flow 側で、`reports/` 配下など full lint 対象外になり得る Markdown の focused lint 契約が弱いという Major が出た。
- 設計へ明示ファイル、focused lint、full lint 検討、caller report 記録を追加した。
- 修正後 review は no findings。

### 実装 review

- `reports/task-markdown-word-check-implementation-20260522102043.md`
- `reports/task-markdown-word-check-implementation-review-20260522102902.md`
- `reports/task-markdown-word-check-implementation-fix-20260522103311.md`
- `reports/task-markdown-word-check-implementation-review-r2-20260522103812.md`

結果:

- 初回実装 review で `design-executor` / `handover-memo-writer` の Completion condition と `agents/openai.yaml` の `default_prompt` に指摘あり。
- 修正後 r2 review は no findings。

### 実 skill 使用想定の設計フロー review

- `reports/task-markdown-word-check-design-flow-review-20260522163846.md`
- `reports/task-markdown-word-check-flow-fix-20260522164303.md`
- `reports/task-markdown-word-check-design-flow-review-r2-20260522164807.md`

結果:

- 初回 review で次のフロー穴が見つかった。
  - focused lint と full lint の aggregate gate state が未定義。
  - exact entry user review 後の再開フロー不足。
  - `unsupported` を caller gate で許容する条件が曖昧。
- 修正後 r2 review は no findings。

## 実行済み検証

実行済みまたは sub-agent report に記録済みの主な検証:

- `python3 /home/ibis/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/ibis/AI/CodexSkill/skills/markdown-word-checker`
- `git diff --check`
- `git diff --cached --check`
- `cmp -s design/skill-hierarchy-design.md skills/design/skill-hierarchy-design.md`
- sub-agent design review / r2 review
- sub-agent 新語ルーティング監査 / 修正 / review
- 2 agent 並列のユーザーフロー思考実験 / 反映後 review
- sub-agent implementation / review / fix / r2 review
- sub-agent による実 skill 使用想定の設計フローレビュー / 修正 / r2 review

注意:

- CodexSkill repo 自体には `tools/lint/` と repo root `package.json` がないため、`markdown-word-checker` をこの repo の Markdown に対して実 lint すると現時点では `unsupported` になる。
- これは現在の設計上、pass ではなく caller disposition として扱う状態である。

## 合意済みの作業方針

### 親 agent の役割

親 agent はマネージャーとして振る舞う。

親 agent が担当する:

- development-orchestrator を入口にする。
- 作業範囲の選定。
- sub-agent report の事前作成。
- sub-agent への実装 / review 委譲。
- sub-agent report の確認と判断。
- Git / PR 管理。
- 最終的な進行判断。

親 agent は、実装・修正・レビュー作業を直接進めない。

### sub-agent の役割

実装、修正、レビューは `gpt-5.5 high` の sub-agent に委譲する。

sub-agent に渡す時は必ず次を明示する:

- 対象 skill。
- 対象ファイル。
- 対象外。
- report path。
- 検証コマンド。
- report の heading / spacing / filled text を保持すること。

### Markdown / lint 方針

作業者に細かい語彙規則を知らせない。

作業者向けに出すルールは次だけ。

```text
Markdown 資料を作成または編集したら、このリポジトリの Markdown lint を実行してください。
lint の指摘に従って本文を直してください。
指摘が不適切に見える場合は、回避せず lint 設定見直しとして報告してください。
```

細かい用語判断は `markdown-word-checker` と repo 固有 lint 設定に閉じ込める。

## まだ open の項目

### PR #41 の扱い

PR #41 は open / mergeable clean のまま。

次のチャットで最初に確認すること:

1. `/home/ibis/AI/CodexSkill` で `git status --short --branch` を確認する。
2. `gh pr view 41 --json state,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,url` を確認する。
3. PR #41 がまだ open なら、必要に応じて review 依頼または merge 方針を利用者に確認する。

### 後続 task

今回の PR では次を対象外としている。

- shared script の `skills/markdown-word-checker/scripts/` への移動。
- repo 固有 whitelist / `prh` 実データ変更。
- CodexSkill repo 自体への Markdown lint 設定導入。

これらは必要なら別 task として扱う。

## markdown-word-checker 結果

この handover report 作成に対する `markdown-word-checker` 相当の確認結果:

- 対象 repository root: `/home/ibis/AI/CodexSkill`
- 対象 Markdown file: `reports/task-markdown-word-check-handover-r2-20260527055108.md`
- check scope: focused
- command path: focused lint の実行候補を確認する
- 結果: `unsupported`
- 理由: CodexSkill repo root には現時点で `package.json` と `tools/lint/` がなく、repo-local Markdown lint 設定が導入されていない。
- aggregate gate state: `unsupported`
- disposition: この handover は次チャットへの再開資料であり、repo-local lint 未導入のため focused lint は実行不能として残リスクを記録する。これは handover 作成自体の normal path を妨げない。
- 残リスク: 将来 CodexSkill repo に Markdown lint 設定を導入する場合、この handover report も focused lint 対象として再確認できる。

## 次チャット用プロンプト

```text
/home/ibis/AI/CodexSkill で Markdown 単語チェック skill の作業を続けてください。

まず AGENTS.md と development-orchestrator / restart-handover-manager / git-workflow-manager / review-enforcer / sub-agent-task-manager を確認してください。

現在の前提:
- branch は `docs/markdown-word-checker-design` です。
- PR #41 `docs: Markdown単語チェックskill設計を追加する` は open / mergeable clean です。
- 最新 commit は `cb6e00e fix(markdown-word-check): clarify gate flow` です。
- `markdown-word-checker` の設計と初期実装は PR #41 に含まれています。
- 実装、レビュー、設計修正は `gpt-5.5 high` の sub-agent に委譲してください。
- 親 agent はマネージャーとして、範囲決定、委譲、report 確認、Git/PR 管理だけを担当してください。

重要な成果物:
- `design/markdown-word-check-skill-design.md`
- `skills/markdown-word-checker/SKILL.md`
- `skills/markdown-word-checker/agents/openai.yaml`
- `skills/review-enforcer/SKILL.md`
- `skills/design-executor/SKILL.md`
- `skills/handover-memo-writer/SKILL.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`

重要な report:
- `reports/task-markdown-word-check-design-review-r2-20260520230107.md`
- `reports/task-markdown-word-check-term-routing-design-review-20260521205510.md`
- `reports/task-markdown-word-check-user-flow-design-review-20260521212259.md`
- `reports/task-markdown-word-check-implementation-review-r2-20260522103812.md`
- `reports/task-markdown-word-check-design-flow-review-r2-20260522164807.md`
- `reports/task-markdown-word-check-handover-r2-20260527055108.md`

最初にやること:
1. `git status --short --branch` を確認してください。
2. PR #41 の現在状態を `gh pr view 41 --json state,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,url` で確認してください。
3. PR #41 がまだ open なら、利用者に merge / review 依頼 / 追加修正のどれへ進めるか確認してください。
4. 追加修正が必要な場合、実装とレビューは sub-agent `gpt-5.5 high` に委譲してください。
```

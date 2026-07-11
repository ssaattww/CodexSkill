# task routine hook 設計

## 目的

開発 agent が、skill の確認、検証、レビュー、skill 改善判断、tool 化判断、feedback/issue の重複確認、進捗同期、Git 提出を忘れないようにする。

手順を自然言語の注意書きだけに置かず、1 task ごとの永続状態と Codex hook によって実行順を維持する。

## 問題

既存の `AGENTS.md`、`development-orchestrator`、`feedback-points-manager` には必要な手順が書かれている。しかし、これらは agent が作業中に読み直し、必要なタイミングで思い出すことを前提としている。

GitHub Issue は次の用途には適している。

- 再発内容の保存
- 重複の統合
- skill 改善作業の追跡
- PR との紐付け

一方、Issue は agent が参照しなければ実行されないため、task runtime の記憶装置にはしない。

## 所有者

`development-orchestrator` が task routine の所有者になる。

新しい独立 skill は作成しない。task 選定から Git 提出までの lifecycle は既に `development-orchestrator` の責務であり、routine state、hook gate、skill/tool reflection を同 skill の内部 tool として持つ。

実装は次に置く。

```text
skills/development-orchestrator/scripts/task_routine.py
skills/development-orchestrator/scripts/task_routine_state.py
skills/development-orchestrator/scripts/task_routine_hooks.py
skills/development-orchestrator/tests/test_task_routine.py
skills/development-orchestrator/tests/test_task_routine_pr_body.py
hooks/hooks.json
.codex-plugin/plugin.json
```

## 状態の正本

状態は対象リポジトリの Git directory 内に保存する。

```text
<git-dir>/codex-task-routine/state.json
<git-dir>/codex-task-routine/history/*.json
```

この配置には次の性質がある。

- session restart、context compaction、chat 移動後も残る。
- project の tracked file を汚さない。
- repository ごとに分離される。
- worktree では `git rev-parse --git-path` の結果に従う。

Issue と FP は履歴・重複・follow-up の正本であり、実行中の次工程は local routine state が正本である。

## 1 task の routine

routine は次の順序を持つ。

1. `intake`
2. `skill_scan`
3. `task_definition`
4. `plan`
5. `implementation`
6. `verification`
7. `review`
8. `skill_reflection`
9. `tool_reflection`
10. `feedback_tracking`
11. `progress_sync`
12. `git_submission`

通常 step は `complete <step> --evidence ...` で完了する。該当しない工程は `skip <step> --reason ...` で `not_applicable` にできる。

`skill_reflection`、`tool_reflection`、`feedback_tracking` は generic な完了を禁止し、structured command を必須にする。

### skill reflection

許可する判断は次のとおり。

- `none`
- `update-existing`
- `propose-new`

既存 skill の責務内に収まる低リスクで可逆な改善は、発見した task 内で更新してよい。`update-existing` は、変更候補を記録しただけでは完了せず、更新済み file、commit、report 等の証拠を残す。

新規 skill は責務分割と trigger 増加を伴うため、従来どおり利用者への提案を境界とする。

### tool reflection

許可する判断は次のとおり。

- `none`
- `update-existing`
- `create-internal`
- `propose-external`

agent が毎回直接生成、変換、検証、整形している出力に、決定的で再利用可能な部分がある場合は helper script または tool 化を検討する。

既存 skill の内部 helper として閉じる低リスクな tool は `create-internal` で自動作成できる。外部公開 interface、破壊的処理、credential、組織承認を伴う standalone tool は `propose-external` とする。

### feedback tracking

許可する判断は次のとおり。

- `none`
- `merged`
- `issue`
- `commit-backed`

GitHub Issue を runtime trigger にはしないが、task 完了前に重複確認と追跡先の証拠は必須にする。

## hook

Codex が提供する次の lifecycle event を使う。

### `SessionStart`

session の startup、resume、clear、compact 後に local state を読み、active task と次 step を model context へ再注入する。

### `UserPromptSubmit`

各 user turn の開始時に同じ state を再注入する。長い作業中に instruction が context の後方へ流れても、現在位置を再提示できる。

### `PreToolUse`

次を拒否できる gate とする。

- active task がない状態での file/repository mutation
- `intake`、`skill_scan`、`task_definition`、`plan` より前の実編集
- `verification`、`review`、両 reflection、feedback tracking、progress sync より前の commit、push、PR 作成
- task routine、skill action、tool action の証拠が本文にない PR 作成
- 壊れた routine state のままの mutation

read-only command と task routine CLI 自身は許可する。

shell command の mutation 判定は、Git/GitHub submission command、既知の file mutation command、output redirection を対象にする。任意 script の内部副作用を完全には判定できないため、これは最終 security sandbox ではなく workflow omission gate とする。

PR 作成時は本文に次の見出しと非placeholderの証拠を要求する。

```markdown
## Task routine evidence

## Skill action

## Tool action
```

`none` を選ぶ場合も、単語だけで済ませず、その判断理由を記録する。

### `Stop`

active task に未完了 step がある場合、`decision: block` と具体的な continuation prompt を返す。

Codex が continuation 後に `stop_hook_active: true` で同じ Stop hook を再実行した場合は、無限再入を避けるため再度 block しない。最初の continuation で次工程を実行できない場合は、`pause` または `abort` を明示的に記録する。

外部依存や利用者判断待ちで終了する必要がある場合は、silent bypass ではなく次のいずれかを状態へ残す。

- `pause --reason ...`
- `abort --reason ...`

## Codex plugin と直接導入

repository root に `.codex-plugin/plugin.json` と `hooks/hooks.json` を置き、plugin として導入した場合は `$PLUGIN_ROOT` を使って hook helper を起動する。

plugin を使わない構成では、次の command で既存 `.codex/hooks.json` を保持したまま task routine handler を追加できる。

```bash
python3 skills/development-orchestrator/scripts/task_routine.py install-hooks --scope project
python3 skills/development-orchestrator/scripts/task_routine.py install-hooks --scope user
```

installer は同じ handler を重複追加しない。削除は `uninstall-hooks` を使う。

## 主な CLI

```bash
# 1 task を開始する
python3 skills/development-orchestrator/scripts/task_routine.py \
  start --id issue-47 --summary "task routine hookを実装する"

# 状態を確認する
python3 skills/development-orchestrator/scripts/task_routine.py status

# 通常 step を完了する
python3 skills/development-orchestrator/scripts/task_routine.py \
  complete verification --evidence "python3 -m unittest: 15 tests passed"

# skill 改善判断を記録する
python3 skills/development-orchestrator/scripts/task_routine.py \
  reflect skill --decision update-existing \
  --target development-orchestrator \
  --evidence "SKILL.mdとtask_routine.pyを更新"

# tool 化判断を記録する
python3 skills/development-orchestrator/scripts/task_routine.py \
  reflect tool --decision create-internal \
  --target task_routine.py \
  --evidence "反復確認をCLIとhookへ移した"

# reviewで差し戻された工程以降を再度未完了にする
python3 skills/development-orchestrator/scripts/task_routine.py \
  reopen implementation --reason "review findingを修正する"
```

## 安全境界

自動実施してよい範囲は、内部、可逆、低リスクで、既存責務の中に閉じる変更である。

次は利用者確認を維持する。

- 外部公開契約の変更
- 破壊的または不可逆な操作
- credential、法務、組織承認が必要な操作
- acceptance criteria を変える曖昧な判断
- 新規 skill による責務分割
- standalone external tool の導入

## 完了条件

次をすべて満たしたときに実装完了とする。

- task state が repository ごとに永続化される。
- step の順序違反が拒否される。
- active task なしの mutation が拒否される。
- review と reflection 未完了の Git submission が拒否される。
- 必須のroutine/skill/tool証跡がないPR作成が拒否される。
- incomplete task の `Stop` が continuation を返し、再入時は無限loopを起こさない。
- restart/compact 後に next step が再注入される。
- 既存 hooks 設定を保持して install/uninstall できる。
- unit test が状態遷移、gate、hook output、installer の主要経路を検証する。

# Codex Hooks による Skill 実行フロー強制設計書

## 1. 目的

本設計書は、Codex の Skill に定義した作業フローを、hooks を用いてできるだけ強制・矯正するための設計をまとめる。

主目的は以下である。

- Skill に書かれた作業手順を Codex に守らせる
- ツール実行後に「今行っていたはずの作業」「今回実行した作業」「次に行う作業」を Codex に提示する
- 完了前に未完了ステップがあれば Stop hook で終了を止める
- ユーザーの追加情報・割り込み依頼・方針変更・中止・復帰を扱う
- 自然文分類は原則として本体エージェントに行わせる
- hook は分類結果の明示、state 更新、未完了 node の検査を担当する
- 設計段階で排除した分類方式は排除理由として一箇所にだけ記録する

## 2. 前提

### 2.1 対象

- Codex CLI
- Codex hooks
- Codex Skills
- リポジトリローカルの `.codex/` ディレクトリ
- Python 製 hook スクリプト
- Markdown / JSON による Skill flow 定義

### 2.2 非対象

以下は本設計の対象外とする。

- Codex 本体の改造
- hooks の仕様拡張
- 完全なセキュリティサンドボックスの実装
- LLM の分類結果を絶対的に信頼する設計
- ユーザーに `/info` や `/interrupt` などのカスタムコマンドを強制する運用

## 3. 基本方針

### 3.1 役割分担

```text
Skill / SKILL.md
  人間・Codex 向けの作業説明を書く

Repository / workflow.json
  repository 固有の phase / task 階層を書く

Skill / steps.json
  hooks が読む機械可読な reusable step 定義を書く

UserPromptSubmit hook
  active flow がある場合だけ現在のユーザー入力を durable state に保存する
  保存した入力 ID、Flow State、分類要求を Codex 本体に提示する

Codex 本体
  ユーザー入力を additional_info / interrupt / flow_change / cancel / resume / ambiguous に分類する
  UserPromptSubmit が保存した入力 ID に分類結果を紐づける
  state update script の分類更新 interface に payload を渡す

PostToolUse hook
  ツール実行後に進捗を更新し、次の作業を Codex に提示する

Stop hook
  未完了フロー、未解決の割り込み、曖昧なユーザー意図があれば終了を止める

PreToolUse hook
  必要に応じて、明らかな順序違反や禁止操作を止める
```

### 3.2 LLM と hook の責務分離

LLM に任せること。

```text
- ユーザー入力の自然文分類
- 分類理由の説明
- 追加情報の要約
- 割り込み作業の要約
- 曖昧な場合の確認質問案
```

ここでの LLM は、会話コンテキストを持つ Codex 本体を指す。

hook が担当すること。

```text
- state の保存
- state の更新
- ユーザー入力受付記録の durable state 化
- flow の進捗管理
- 未完了 node の検出
- Stop 時の block
- 次作業の提示
- 再帰防止
- 分類失敗時の ambiguous 扱い
```

Codex 本体に任せないこと。

```text
- 自分自身の作業がフロー違反かどうかの最終判定
- hook block を回避する弁明
- 未完了 node の勝手な完了扱い
```

### 3.3 排除した設計案

初期案では、`UserPromptSubmit` hook から分類専用 `codex exec` を起動し、ユーザー入力を hook 側で分類する方針としていた。

その後の検討で、この案は設計段階で排除する。
排除理由は以下である。

```text
- 本体エージェントは会話コンテキスト、現在作業、直前の割り込みを保持している
- hook から毎回 codex exec を起動すると遅延、再帰防止、失敗点が増える
- skill 化して hook が常時起動する場合、active flow がない入力まで分類器を動かすべきではない
- hook は分類者ではなく、分類の明示と state machine による検査役に寄せる方が単純である
```

排除した案の詳細手順は本文の実装設計には残さない。
本設計では、自然文分類は Codex 本体が行い、hook は Flow State 提示と後追い検査に限定する。

## 4. ディレクトリ構成

推奨構成は以下である。

state は Codex を起動したときのプロジェクトディレクトリ内に保持する。
途中で tool の `cwd` が変わっても、state の保存先は起動時プロジェクトディレクトリから動かさない。

task / phase 定義は起動したプロジェクト側に保持する。
task / phase は repository ごとの開発単位、粒度、リリース運用に依存するためである。

step 定義は CodexSkill 側に保持する。
step は「設計する」「実装する」「検証する」「レビューする」「commit する」のように、多くの task で再利用されるためである。

```text
started-project/
  .codex/
    config.toml
    hooks/
      user_prompt_flow_state.py
      post_tool_flow.py
      stop_guard.py
      pre_tool_guard.py
    state/
      flow_state.json
      progress.json
      hook_logs/
    workflows/
      release-governance-workflow.json

CodexSkill/
  skills/
    release-governance-manager/
      SKILL.md
      steps.json
```

責務境界。

```text
started-project/.codex/state/
  起動したプロジェクト固有の実行 state を保持する

CodexSkill/skills/*/steps.json
  Skill ごとの再利用可能な step 定義を保持する

started-project/.codex/workflows/*.json
  repository ごとの phase / task 階層と、各 task が使う step 参照を保持する

started-project/.codex/config.toml
  hook の有効化、state root、workflow root、CodexSkill root、step root を保持する
```

### 4.1 root 解決契約

hook は tool payload の `cwd` を state root の決定に使わない。
`cwd` は実行された tool の作業ディレクトリであり、途中で別ディレクトリに変わる可能性があるためである。

初期実装では、root 解決は以下の順で行う。

```text
1. 環境変数を優先する
   - CODEX_STARTED_PROJECT_ROOT
   - CODEX_FLOW_STATE_ROOT
   - CODEX_SKILL_ROOT
   - CODEX_REPO_WORKFLOW_ROOT
   - CODEX_SKILL_STEP_ROOT

2. 環境変数がなければ started-project/.codex/config.toml を読む
   - [flow_enforcement].started_project_root
   - [flow_enforcement].state_root
   - [flow_enforcement].codex_skill_root
   - [flow_enforcement].workflow_root
   - [flow_enforcement].step_root

3. flow_state.json の roots は検証用として読む
   - hook が解決した root と一致しない場合は state 破損扱いにする
   - flow_state.json だけを root discovery の起点にはしない
```

必須契約。

```text
started_project_root
  Codex を起動したプロジェクト root の絶対 path

state_root
  started_project_root/.codex/state の絶対 path

codex_skill_root
  CodexSkill repository root の絶対 path

workflow_root
  started_project_root/.codex/workflows の絶対 path

step_root
  codex_skill_root/skills の絶対 path
```

`workflow_root` は repository-local な phase / task 定義を指す。
`step_root` は CodexSkill 側の reusable step 定義を指す。
hook は `flow_state.json` の `current_workflow.workflow_path` から repo-local workflow を読み、各 task の `step_set_ref` から `{step_root}/{skill}/steps.json` を読む。

hook command は相対 `cwd` に依存しない形で起動する。
相対 command を使う場合でも、wrapper は上記環境変数を必ず渡す。
後続実装では、root が未設定、相対 path、repo 外、または相互不一致の場合は no-op ではなく block 可能な `unsupported_state_root` として扱う。

避ける構成。

```text
started-project/.codex/skills/
  release-governance-manager/
    steps.json
```

上記のように reusable step 定義をプロジェクト側へ複製すると、Skill 本体と step 定義が分岐するため採用しない。

## 5. Skill flow 定義

### 5.1 `SKILL.md`

`SKILL.md` には、Codex と人間が読むための説明を書く。
このファイルは CodexSkill 側の Skill ディレクトリに置く。

例。

```markdown
# Release Governance Manager

## Goal

Release governance を確認し、以下の整合性を取る。

- Design/BreakingChanges.md
- GitHub Actions workflow
- NuGet package version policy
- release tag policy

## Required flow

1. Design/BreakingChanges.md を読む
2. .github/workflows を確認する
3. package version source を確認する
4. 判断結果をまとめる
```

### 5.2 repository workflow 定義

hooks は自然文の `SKILL.md` を直接解釈しない。
repository ごとの phase / task 階層は、起動したプロジェクト側の `.codex/workflows/*.json` に機械可読な workflow 定義として置く。

phase と task は repository ごとに異なる。
そのため、CodexSkill 側へ置かず、対象 repository が所有する。

例。

```json
{
  "workflow_id": "release-governance",
  "version": 1,
  "nodes": [
    {
      "id": "implementation_phase",
      "kind": "phase",
      "description": "実装 phase",
      "required": true,
      "children": [
        {
          "id": "hook_state_task",
          "kind": "task",
          "description": "hook state 管理を実装する",
          "required": true,
          "step_set_ref": {
            "skill": "development-lifecycle",
            "version": 1,
            "set": "design-implementation-review-commit"
          }
        }
      ]
    }
  ]
}
```

repository workflow node contract。

```text
id
  同じ parent 配下で一意な repository-local ID。

kind
  phase / task など、repository workflow 上の分類。
  初期実装では phase と task を想定するが、hook は未知 kind でも node tree として扱う。

node_path
  root から node までの id を `/` で連結した canonical path。
  例: implementation_phase/hook_state_task

children
  任意深さの子 node。

required
  parent 完了条件に含めるかどうか。

step_set_ref
  task node が使う CodexSkill 側 step set への参照。

depends_on
  同じ repository workflow 内の他 node_path への依存。
```

### 5.3 CodexSkill step 定義

step は task / phase とは別概念である。
step は多くの task で共通に使う標準手順であり、基本的には CodexSkill 側に保持する。

例。

```json
{
  "skill": "development-lifecycle",
  "version": 1,
  "step_sets": [
    {
      "id": "design-implementation-review-commit",
      "steps": [
        {
          "id": "design",
          "description": "設計を更新する",
          "required": true,
          "evidence": [{"type": "markdown_changed"}]
        },
        {
          "id": "implement",
          "description": "実装する",
          "required": true,
          "evidence": [{"tool": "apply_patch"}]
        },
        {
          "id": "review",
          "description": "レビューを受ける",
          "required": true,
          "evidence": [{"type": "review_report"}]
        },
        {
          "id": "commit",
          "description": "変更を commit する",
          "required": true,
          "evidence": [{"tool": "Bash", "command_contains": "git commit"}]
        }
      ]
    }
  ]
}
```

CodexSkill step contract。

```text
step_set
  複数 task から参照される標準 lifecycle。

step
  task 内で実行される再利用可能な作業単位。
  phase / task の所有者ではなく、CodexSkill 側の標準手順である。

step_id
  step_set 内で一意な安定 ID。

evidence
  step 完了候補を検出する条件。
```

### 5.4 workflow と step の合成 model

hook は repository workflow と CodexSkill step set を合成して、実行時の node tree を作る。
task node に `step_set_ref` がある場合、その task の子として参照先 step set の steps を展開する。

実行時 node path は repository-local task path と CodexSkill step id を合成する。

```text
implementation_phase/hook_state_task#design
implementation_phase/hook_state_task#implement
implementation_phase/hook_state_task#review
implementation_phase/hook_state_task#commit
```

区切り規則。

```text
/
  repository-local phase / task 階層を表す。

#
  task node と CodexSkill step を接続する。
```

この形式により、phase / task の階層が将来さらに深くなっても repository-local path はそのまま伸びる。
step は task の深さに関係なく CodexSkill 側の同じ step 定義を参照する。

完了判定。

```text
step node
  CodexSkill 側 step の evidence または manual_required の確認で完了する。

task node
  参照した step_set の required steps がすべて完了したら完了する。

phase node
  required children がすべて完了したら完了する。

optional task / phase
  parent 完了条件には含めないが、完了履歴は記録できる。

required task / phase / step の skip / optional 化
  flow_overrides の明示確認済み override がある場合だけ Stop 判定に反映する。
```

hook 内部では、repository workflow と step set を読み込んだ後に tree を走査し、`node_path -> node` の index を作る。
進捗、現在位置、override、interrupt の戻り先は `node_path` を基準に記録する。

## 6. state 設計

### 6.1 state の配置

state は起動時プロジェクトディレクトリの `.codex/state/` に保持する。

```text
started-project/.codex/state/
  flow_state.json
  progress.json
  hook_logs/
```

この state は対象プロジェクトごとの実行状態であり、CodexSkill 側には置かない。
同じ Skill flow を複数プロジェクトで使う場合も、各プロジェクトがそれぞれ自分の state を持つ。

### 6.2 `flow_state.json`

現在の作業状態を保持する。

```json
{
  "schema_version": 1,
  "mode": "normal",
  "roots": {
    "started_project_root": "/path/to/started-project",
    "state_root": "/path/to/started-project/.codex/state",
    "codex_skill_root": "/path/to/CodexSkill",
    "workflow_root": "/path/to/started-project/.codex/workflows",
    "step_root": "/path/to/CodexSkill/skills"
  },
  "current_workflow": {
    "workflow_id": "release-governance",
    "version": 1,
    "workflow_path": "/path/to/started-project/.codex/workflows/release-governance-workflow.json"
  },
  "current_task": {
    "workflow_id": "release-governance",
    "task_id": "hook_state_task",
    "task_node_path": "implementation_phase/hook_state_task",
    "status": "active",
    "current_step": "review",
    "next_step": "commit",
    "current_node_path": "implementation_phase/hook_state_task#review",
    "next_node_path": "implementation_phase/hook_state_task#commit",
    "step_set_ref": {
      "skill": "development-lifecycle",
      "version": 1,
      "set": "design-implementation-review-commit"
    },
    "steps_path": "/path/to/CodexSkill/skills/development-lifecycle/steps.json"
  },
  "workflow_cursor": {
    "current_node_path": "implementation_phase/hook_state_task#review",
    "next_node_path": "implementation_phase/hook_state_task#commit",
    "active_path_stack": [
      "implementation_phase",
      "implementation_phase/hook_state_task",
      "implementation_phase/hook_state_task#review"
    ]
  },
  "context": [],
  "interrupt_stack": [],
  "input_journal": [],
  "flow_overrides": [],
  "pending_user_intent": null
}
```

`current_task.current_step`、`current_task.next_step`、`current_task.current_node_path`、`current_task.next_node_path`、`current_task.status` は表示と復帰のための derived cache である。
完了 node の canonical source は `progress.json` とする。
hook は repository workflow、CodexSkill step 定義、`progress.json`、確認済み `flow_overrides` から derived cache を再計算できなければならない。
`workflow_cursor.active_path_stack` は現在 node の祖先を含む表示用 cursor であり、Stop 判定の canonical source ではない。

### 6.3 mode

`mode` は以下を取る。

| mode | 意味 |
|---|---|
| `normal` | 通常の Skill フロー進行中 |
| `interrupted` | ユーザー割り込み作業中 |
| `pending_user_intent` | ユーザー入力の分類が曖昧で確認待ち |
| `resuming` | 割り込みから元作業へ復帰中 |
| `cancelled` | 現在作業が中止された |
| `completed` | 現在作業が完了した |

### 6.4 context

追加情報や方針変更を蓄積する。

```json
[
  {
    "source": "user",
    "type": "additional_info",
    "text": "対象は v2 系だけです",
    "summary": "対象を v2 系に限定する",
    "constraints": ["対象は v2 系のみ"],
    "notes": []
  }
]
```

### 6.5 interrupt_stack

割り込み作業を stack として保持する。

```json
[
  {
    "request": "先に README を直して",
    "summary": "README の文言を修正する",
    "status": "active",
    "return_to": {
      "workflow_id": "release-governance",
      "task_node_path": "implementation_phase/hook_state_task",
      "status": "active",
      "current_step": "review",
      "next_step": "commit",
      "current_node_path": "implementation_phase/hook_state_task#review",
      "next_node_path": "implementation_phase/hook_state_task#commit"
    }
  }
]
```

### 6.6 pending_user_intent

分類不能な入力を保持する。

```json
{
  "input_id": "2026-05-30T10:31:58.123456Z-userprompt-0001",
  "text": "それ先にやって",
  "classification": {
    "intent": "ambiguous",
    "confidence": 0.42,
    "candidates": ["interrupt", "flow_change"]
  },
  "required_agent_action": "これは割り込み作業か、現在フローの変更かをユーザーに確認する"
}
```

### 6.7 input_journal

`UserPromptSubmit` が受け取ったユーザー入力を durable state として保持する。
active flow がある場合、hook は Codex 本体へ分類要求を返す前に必ず `input_journal` へ追記する。

```json
[
  {
    "input_id": "2026-05-30T10:31:58.123456Z-userprompt-0001",
    "event": "UserPromptSubmit",
    "received_at": "2026-05-30T10:31:58.123456Z",
    "text": "対象は v2 系だけです",
    "status": "unclassified",
    "classification": null,
    "adoption": null,
    "applied_state_updates": [],
    "superseded_by": null
  }
]
```

`status` は以下を取る。

| status | 意味 |
|---|---|
| `unclassified` | UserPromptSubmit が保存しただけで、Codex 本体の分類が未記録 |
| `classified` | Codex 本体が分類結果を記録したが、state 反映が未完了 |
| `applied` | 分類結果に基づく state 反映が完了 |
| `needs_confirmation` | ユーザー確認待ち |
| `superseded` | 後続入力で置き換えられた |

Codex 本体は、UserPromptSubmit が返した `input_id` に対して分類結果を記録する。
`input_id` が一致しない分類結果、または未保存入力への分類結果は採用しない。

### 6.8 Codex 本体の分類更新 interface

Codex 本体は自然文分類を行った後、通常作業へ進む前に state update script へ以下の payload を渡す。
Codex 本体が `flow_state.json` を直接編集することは原則禁止する。
hook は分類者ではなく、script が更新した state の検査者である。

```json
{
  "input_id": "2026-05-30T10:31:58.123456Z-userprompt-0001",
  "classification": {
    "intent": "additional_info",
    "confidence": 0.86,
    "reason": "現在作業への制約追加であり、別作業を要求していない",
    "summary": "対象を v2 系に限定する"
  },
  "adoption": "auto",
  "state_effect": {
    "context_added": true,
    "interrupt_pushed": false,
    "flow_override_ids": [],
    "mode_after": "normal"
  }
}
```

更新規則。

```text
- confidence >= 0.8 は adoption = auto として採用できる
- 0.5 <= confidence < 0.8 は adoption = provisional として記録する
- confidence < 0.5 は pending_user_intent を作り、adoption = needs_confirmation にする
- flow_change で required node を skip / optional 化する場合は confidence に関係なく明示確認が必要
- state_effect は実際に変更した state field を要約する
- input_journal の status は state 反映後に applied または needs_confirmation にする
```

分類更新 script は、payload schema、`input_id` の存在、現在 mode、required node を緩める override の確認状態を検証してから atomic write する。
script が失敗した場合、Codex 本体は通常作業へ進まず、失敗理由を Flow State として扱う。

Stop hook は `input_journal` に `unclassified` または `classified` の最新入力が残っていれば block する。
`needs_confirmation` が残っている場合は、確認質問または確認結果の反映が終わるまで block する。

### 6.9 `progress.json`

node 完了履歴の canonical source として `progress.json` を保持する。
単一階層の `steps` は leaf node に正規化されるため、同じ `completed_nodes` で扱う。

```json
{
  "schema_version": 1,
  "workflow": {
    "workflow_id": "release-governance",
    "version": 1
  },
  "completed_nodes": [
    {
      "node_path": "implementation_phase/hook_state_task#review",
      "node_kind": "step",
      "completed_at": "2026-05-30T10:35:00Z",
      "source": "PostToolUse",
      "evidence": {
        "tool_name": "apply_patch",
        "tool_input_excerpt": "reports/codex-hooks-flow-classifier-design-review-20260530102421.md"
      }
    }
  ]
}
```

所有者。

```text
progress.json
  PostToolUse が専用 script 経由で更新する canonical source。
  Codex 本体は直接 completed_nodes を追加しない。
  手動完了や再計算が必要な場合も、Codex 本体は script を呼ぶだけで JSON を直接編集しない。

flow_state.json current_task.current_step / next_step / current_node_path / next_node_path
  PostToolUse が progress 更新 script の結果を使って同期する derived field。
  UserPromptSubmit は読み取りと input_journal 追記だけを行い、node を進めない。

flow_state.json current_task.status
  PostToolUse が required nodes 完了時に completed へ更新する。
  Codex 本体は cancel / resume / interrupt の分類 payload を update_input_journal.py に渡すだけで、mode と status は script が更新する。
  Stop hook は completed と書かれていても required nodes が未完了なら block する。
```

### 6.10 state update scripts

state の破損を避けるため、`progress.json` と derived state の更新は専用 script を通す。
Codex 本体、hook、手動復旧作業のいずれも、可能な限り同じ script を使う。

推奨配置。

```text
CodexSkill/
  skills/
    flow-enforcement/
      scripts/
        update_input_journal.py
        update_progress.py
        sync_flow_state.py
        validate_state.py
```

script contract。

```text
update_input_journal.py
  UserPromptSubmit の入力受付記録と、Codex 本体の分類結果反映を担当する。

update_progress.py
  completed_nodes の追加、重複排除、evidence 検証、parent roll-up 再計算を担当する。

sync_flow_state.py
  progress と confirmed override から current node / next node / status を再計算する。

validate_state.py
  flow_state.json、progress.json、repository workflow、CodexSkill step 定義の整合性を検査する。
```

必須性質。

```text
- JSON schema を検証してから書く
- state_root 外への書き込みを拒否する
- workflow_root / step_root との不一致を拒否する
- atomic write を使う
- 可能なら file lock を使う
- 更新前後の validation を行う
- 更新結果と変更理由を hook_logs に残す
```

共通 CLI contract。

```text
- 全 script は stdin から JSON request を読み、stdout に JSON response を返す
- stderr は human-readable な診断だけに使い、machine-readable な結果は stdout に集約する
- request には必ず operation、state_root、workflow_root、step_root、request_id、actor を含める
- response には必ず ok、operation、request_id、updated_files、warnings、errors、state_summary を含める
- state_root / workflow_root / step_root は絶対 path に解決してから検証する
- state 更新系 script は state_root/.flow-state.lock を同じ exclusive lock として使う
- lock timeout は初期値 10 秒とし、timeout 時は state を変更しない
- validate_state.py は書き込みを行わず、lock が取得できる環境では shared lock を使う
- 書き込み前に対象 JSON を schema validation する
- 書き込みは一時ファイルへ出力し、fsync 後に atomic rename する
- 書き込み後に validate_state.py 相当の整合性検査を行う
- 書き込み後検証に失敗した場合は .bak から atomic に復元し、failure を hook_logs に残す
- hook 側の retry は lock timeout と一時的 I/O 失敗だけを対象に 1 回まで許可する
- schema 不一致、root 不一致、未確認 flow_change、evidence 不一致は retry せず block 可能な failure とする
```

exit code contract。

```text
0  success
2  invalid_request_schema
3  root_contract_mismatch
4  validation_failed
5  lock_timeout
6  write_or_rollback_failed
7  user_confirmation_required
8  evidence_rejected
9  unsupported_operation
```

`update_input_journal.py` request。

```json
{
  "operation": "record_user_prompt | classify_input",
  "request_id": "2026-05-30T10:31:58.123456Z-userprompt-0001",
  "actor": "UserPromptSubmit | codex-main-agent",
  "state_root": "/started-project/.codex/state",
  "workflow_root": "/started-project/.codex/workflows",
  "step_root": "/home/ibis/AI/CodexSkill/skills",
  "record_user_prompt": {
    "text": "対象は v2 系だけです",
    "source": "UserPromptSubmit"
  },
  "classify_input": {
    "input_id": "2026-05-30T10:31:58.123456Z-userprompt-0001",
    "classification": {
      "intent": "additional_info",
      "confidence": 0.86,
      "reason": "現在作業への制約追加であり、別作業を要求していない",
      "summary": "対象を v2 系に限定する"
    },
    "adoption": "auto",
    "state_effect": {
      "context_added": true,
      "interrupt_pushed": false,
      "flow_override_ids": [],
      "mode_after": "normal"
    }
  }
}
```

`record_user_prompt` と `classify_input` は同時に指定しない。
UserPromptSubmit は `record_user_prompt` だけを使い、Codex 本体は分類後に `classify_input` だけを使う。

`update_progress.py` request。

```json
{
  "operation": "mark_completed_nodes",
  "request_id": "2026-05-30T10:35:00.000000Z-posttool-0001",
  "actor": "PostToolUse",
  "state_root": "/started-project/.codex/state",
  "workflow_root": "/started-project/.codex/workflows",
  "step_root": "/home/ibis/AI/CodexSkill/skills",
  "completed_nodes": [
    {
      "node_id": "review",
      "node_path": "implementation_phase/hook_state_task#review",
      "evidence": {
        "tool_name": "Bash",
        "summary": "review report created"
      }
    }
  ]
}
```

`sync_flow_state.py` request。

```json
{
  "operation": "sync_derived_state",
  "request_id": "2026-05-30T10:35:00.000000Z-posttool-0001-sync",
  "actor": "PostToolUse",
  "state_root": "/started-project/.codex/state",
  "workflow_root": "/started-project/.codex/workflows",
  "step_root": "/home/ibis/AI/CodexSkill/skills",
  "confirmed_overrides": []
}
```

`validate_state.py` request。

```json
{
  "operation": "validate",
  "request_id": "2026-05-30T10:36:00.000000Z-validate-0001",
  "actor": "Stop | manual-recovery | PostToolUse",
  "state_root": "/started-project/.codex/state",
  "workflow_root": "/started-project/.codex/workflows",
  "step_root": "/home/ibis/AI/CodexSkill/skills"
}
```

共通 response。

```json
{
  "ok": true,
  "operation": "sync_derived_state",
  "request_id": "2026-05-30T10:35:00.000000Z-posttool-0001-sync",
  "updated_files": [
    ".codex/state/flow_state.json"
  ],
  "warnings": [],
  "errors": [],
  "state_summary": {
    "mode": "normal",
    "current_node_path": "implementation_phase/hook_state_task#commit",
    "next_node_path": "implementation_phase/hook_state_task#push"
  }
}
```

`progress.json` の直接編集は、通常運用では禁止する。
直接編集が許されるのは state 破損時の明示的な復旧作業だけであり、その場合も `validate_state.py` の結果を report に残す。

## 7. ユーザー入力分類

この分類は、Codex 本体エージェントが行う。

hook は分類結果を state に反映できているか、曖昧な入力を確認待ちにしているか、未完了の flow を勝手に完了扱いしていないかを検査する。

### 7.1 分類値

エージェントはユーザー入力を以下のいずれかとして扱う。

| intent | 意味 |
|---|---|
| `additional_info` | 現在作業への補足情報・制約追加 |
| `interrupt` | 現在作業とは別の割り込み依頼 |
| `flow_change` | 現在作業の手順・条件・完了条件の変更 |
| `cancel` | 現在作業の中止・破棄 |
| `resume` | 中断していた元作業への復帰 |
| `ambiguous` | 判断不能 |

### 7.2 分類 JSON

state に保存する分類結果は、以下の JSON 形状を基本とする。

```json
{
  "intent": "additional_info",
  "confidence": 0.86,
  "reason": "現在作業への制約追加であり、別作業を要求していない",
  "summary": "対象を v2 系に限定する",
  "context_patch": {
    "constraints": ["対象は v2 系のみ"],
    "notes": []
  },
  "interrupt_task": {
    "summary": ""
  },
  "question_to_user": ""
}
```

この JSON は単独で信頼しない。
必ず `input_journal[].input_id` と紐づけ、`adoption` と `state_effect` を同じ入力記録に残す。

### 7.3 confidence の扱い

```text
confidence >= 0.8
  自動採用

0.5 <= confidence < 0.8
  仮採用し、Flow State に分類結果を明示する

confidence < 0.5
  pending_user_intent にして確認を強制する
```

ただし、`flow_change` が required node の skip、optional 化、完了条件の緩和を含む場合は例外とする。
この場合は LLM 分類の confidence が 0.8 以上でも、確認済み override になるまでは Stop hook の required node 判定を緩めない。

## 8. UserPromptSubmit hook

### 8.1 目的

`UserPromptSubmit` hook は、ユーザー入力を受け取った直後に動く。
ここでは以下を行う。

- active flow がない場合は no-op にする
- active flow がある場合は現在のユーザー入力を `input_journal` に保存する
- active flow がある場合は現在の Flow State を Codex 本体に提示する
- Codex 本体に `input_id` 付きでユーザー入力の分類と state 更新を明示的に要求する
- 直前に曖昧な入力が残っている場合は確認を優先させる

### 8.2 処理フロー

```text
UserPromptSubmit
  ↓
stdin JSON を読む
  ↓
ユーザー入力を抽出
  ↓
flow_state.json を読む
  ↓
active flow の有無を確認する
  ↓
active flow がなければ no-op
  ↓
現在のユーザー入力を input_journal に unclassified として保存する
  ↓
active flow があれば分類要求を含む Flow State を生成する
  ↓
Codex 本体に input_id と Flow State を返す
```

`UserPromptSubmit` が返す model-facing message には以下を必ず含める。

```text
- input_id
- 現在の current_task
- 未完了 required nodes
- 既存の pending_user_intent
- Codex 本体が `update_input_journal.py` の `classify_input` operation に分類結果 payload を渡す必要があること
- required node を緩める flow_change はユーザー明示確認が必要であること
```

## 9. PostToolUse hook

### 9.1 目的

`PostToolUse` hook は、ツール実行後に以下を行う。

- 実行した tool / input / output をもとに leaf node 完了を判定する
- update script 経由で `progress.json` を更新する
- update script 経由で `flow_state.json` の derived field を同期する
- 現在の作業状態を Codex に提示する
- 次に行う作業を Codex に提示する

### 9.2 出力テンプレート

Codex には毎回、以下のような Flow State を返す。

```text
[Flow State]
本来行っていた作業:
- release-governance / implementation_phase/hook_state_task#review

今回実行した作業:
- Bash: ls .github/workflows

現在の追加情報:
- 対象は v2 系のみ

次に行う作業:
- implementation_phase/hook_state_task#commit: 変更を commit する

注意:
- 元の作業は完了していません。
```

### 9.3 割り込み中の出力

```text
[Flow State]
本来行っていた作業:
- release-governance / implementation_phase/hook_state_task#review

今回の割り込み作業:
- README の文言修正

今回実行した作業:
- Edit: README.md

割り込み完了後に戻る作業:
- release-governance / implementation_phase/hook_state_task#commit
```

## 10. Stop hook

### 10.1 目的

`Stop` hook は、Codex が応答を終了しようとしたときに動く。
未完了フロー、曖昧なユーザー入力、割り込みからの未復帰があれば終了を block する。

### 10.2 判定

```text
mode = normal
  required node が未完了なら block
  unclassified / classified の user input が残っていれば block

mode = pending_user_intent
  ユーザー意図確認をしていなければ block

mode = interrupted
  割り込み作業完了後に戻り先へ復帰していなければ block

mode = resuming
  元作業の next node に戻っていなければ block

mode = cancelled
  元作業への復帰は要求しない

mode = completed
  progress.json 上の required nodes が完了していれば allow
  flow_state.json の derived status だけで completed なら block
```

### 10.3 block 例

```json
{
  "decision": "block",
  "reason": "未完了 node があります。次に implementation_phase/hook_state_task#review を実行してください。"
}
```

割り込み中。

```json
{
  "decision": "block",
  "reason": "割り込み作業中です。完了した場合は、中断前の作業に戻ってください。戻り先: release-governance / implementation_phase/hook_state_task#commit"
}
```

曖昧な入力。

```json
{
  "decision": "block",
  "reason": "ユーザー入力の意図が曖昧です。追加情報・割り込み・方針変更・中止・復帰のどれか確認してください。"
}
```

## 11. PreToolUse hook

### 11.1 目的

`PreToolUse` hook は必須ではない。
ただし、以下を強制したい場合に使用する。

- 危険コマンドを止める
- 明らかな順序違反を止める
- 現在 node で許可されない編集を止める
- ユーザー承認が必要な操作を止める

### 11.2 注意点

`PreToolUse` を強くしすぎると、ユーザー割り込みを阻害する。
そのため、`mode = interrupted` の場合は判定を緩める。

```text
mode = normal
  flow に沿わない操作を block しやすくする

mode = interrupted
  割り込み作業に必要な操作は許可する

mode = pending_user_intent
  原則として作業系 tool は block する
```

## 12. hook 設定例

### 12.1 TOML 例

```toml
[features]
hooks = true

[flow_enforcement]
started_project_root = "/path/to/started-project"
state_root = "/path/to/started-project/.codex/state"
codex_skill_root = "/path/to/CodexSkill"
workflow_root = "/path/to/started-project/.codex/workflows"
step_root = "/path/to/CodexSkill/skills"

[[hooks.UserPromptSubmit]]
command = "CODEX_STARTED_PROJECT_ROOT=/path/to/started-project CODEX_FLOW_STATE_ROOT=/path/to/started-project/.codex/state CODEX_SKILL_ROOT=/path/to/CodexSkill CODEX_REPO_WORKFLOW_ROOT=/path/to/started-project/.codex/workflows CODEX_SKILL_STEP_ROOT=/path/to/CodexSkill/skills python3 /path/to/started-project/.codex/hooks/user_prompt_flow_state.py"
timeout = 20

[[hooks.PostToolUse]]
command = "CODEX_STARTED_PROJECT_ROOT=/path/to/started-project CODEX_FLOW_STATE_ROOT=/path/to/started-project/.codex/state CODEX_SKILL_ROOT=/path/to/CodexSkill CODEX_REPO_WORKFLOW_ROOT=/path/to/started-project/.codex/workflows CODEX_SKILL_STEP_ROOT=/path/to/CodexSkill/skills python3 /path/to/started-project/.codex/hooks/post_tool_flow.py"
timeout = 20

[[hooks.Stop]]
command = "CODEX_STARTED_PROJECT_ROOT=/path/to/started-project CODEX_FLOW_STATE_ROOT=/path/to/started-project/.codex/state CODEX_SKILL_ROOT=/path/to/CodexSkill CODEX_REPO_WORKFLOW_ROOT=/path/to/started-project/.codex/workflows CODEX_SKILL_STEP_ROOT=/path/to/CodexSkill/skills python3 /path/to/started-project/.codex/hooks/stop_guard.py"
timeout = 20
```

feature flag 名は Codex のバージョンにより異なる可能性がある。
`features.hooks` と `features.codex_hooks` のどちらが有効かは手元で確認する。

### 12.2 hooks.json 例

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "CODEX_STARTED_PROJECT_ROOT=/path/to/started-project CODEX_FLOW_STATE_ROOT=/path/to/started-project/.codex/state CODEX_SKILL_ROOT=/path/to/CodexSkill CODEX_REPO_WORKFLOW_ROOT=/path/to/started-project/.codex/workflows CODEX_SKILL_STEP_ROOT=/path/to/CodexSkill/skills python3 /path/to/started-project/.codex/hooks/user_prompt_flow_state.py",
            "timeout": 20,
            "statusMessage": "Updating flow state"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash|Edit|Write|apply_patch",
        "hooks": [
          {
            "type": "command",
            "command": "CODEX_STARTED_PROJECT_ROOT=/path/to/started-project CODEX_FLOW_STATE_ROOT=/path/to/started-project/.codex/state CODEX_SKILL_ROOT=/path/to/CodexSkill CODEX_REPO_WORKFLOW_ROOT=/path/to/started-project/.codex/workflows CODEX_SKILL_STEP_ROOT=/path/to/CodexSkill/skills python3 /path/to/started-project/.codex/hooks/post_tool_flow.py",
            "timeout": 20,
            "statusMessage": "Updating flow progress"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "CODEX_STARTED_PROJECT_ROOT=/path/to/started-project CODEX_FLOW_STATE_ROOT=/path/to/started-project/.codex/state CODEX_SKILL_ROOT=/path/to/CodexSkill CODEX_REPO_WORKFLOW_ROOT=/path/to/started-project/.codex/workflows CODEX_SKILL_STEP_ROOT=/path/to/CodexSkill/skills python3 /path/to/started-project/.codex/hooks/stop_guard.py",
            "timeout": 20,
            "statusMessage": "Checking completion gate"
          }
        ]
      }
    ]
  }
}
```

## 13. user_prompt_flow_state.py 設計

### 13.1 処理

```text
1. env / config から started_project_root, state_root, workflow_root, step_root を解決する
2. stdin JSON を読む
3. ユーザー入力を抽出する
4. flow_state.json を読む
5. root contract と state 内 roots の一致を検査する
6. active flow がなければ no-op を返す
7. active flow があれば input_journal に unclassified の入力記録を追記する
8. 現在の Flow State を作る
9. Codex 本体に input_id、分類値、state update script の呼び出し contract を提示する
10. pending_user_intent があれば確認優先の指示を返す
```

### 13.2 失敗時

この hook 自体はユーザー入力を分類しない。
そのため分類不能は Codex 本体に確認質問を要求する Flow State として扱う。

state root、workflow root、CodexSkill root、step root が解決できない場合は `unsupported_state_root` として返す。
active flow があるのに `input_journal` へ保存できない場合は、分類要求だけを返してはいけない。
この場合は Stop hook が検出できるよう、block 可能な failure を model-facing message に含める。

## 14. post_tool_flow.py 設計

### 14.1 処理

```text
1. env / config から started_project_root, state_root, workflow_root, step_root を解決する
2. stdin JSON を読む
3. tool_name / tool_input / tool_result を抽出する
4. flow_state.json と progress.json を読む
5. current workflow を workflow_root から読む
6. task が参照する step set を step_root から読む
7. repository workflow と CodexSkill step set を合成し、node_path index に正規化する
8. step node の evidence と照合する
9. update_progress.py に完了候補 node と evidence を渡す
10. update_progress.py が progress.json 更新と parent roll-up 完了を再計算する
11. sync_flow_state.py が確認済み flow_overrides を適用して next node を算出する
12. sync_flow_state.py が flow_state.json の current node / next node / status を同期する
13. Flow State を Codex に返す
```

### 14.2 evidence 判定

初期実装では厳密にしすぎない。

例。

```text
tool_name == Bash
かつ command に "dotnet test" を含む
  → run_tests 完了候補

tool_name == Bash
かつ command に ".github/workflows" を含む
  → check_workflows 完了候補

tool_name == Edit / Write / apply_patch
かつ対象 path が Design/*.md
  → update_design_doc 完了候補
```

誤判定を避けたい node は `manual_required` とする。

### 14.3 同期責務

`PostToolUse` は `update_progress.py` を呼んだ直後に、同じ hook 実行内で `sync_flow_state.py` を呼ぶ。
parent roll-up と `flow_state.json` の derived field は script が更新する。
同期対象は以下である。

```text
- current_task.current_step
- current_task.next_step
- current_task.current_node_path
- current_task.next_node_path
- workflow_cursor.active_path_stack
- current_task.status
```

全 required nodes が完了した場合、`current_task.status = completed` と `mode = completed` へ更新する所有者は `PostToolUse` である。
`flow_change` による required node の除外は、`flow_overrides.status = active` かつ `confirmation = explicit_user_confirmed` のものだけを適用する。
LLM の仮採用分類だけで required node を完了扱いまたは任意扱いにしてはいけない。

## 15. stop_guard.py 設計

### 15.1 処理

```text
1. env / config から started_project_root, state_root, workflow_root, step_root を解決する
2. flow_state.json を読む
3. progress.json を読む
4. current workflow と参照 step set を読み、node_path index を作る
5. mode を確認する
6. input_journal の未処理入力を確認する
7. confirmed override だけを適用して未完了 required node を探す
8. pending_user_intent を確認する
9. interrupt_stack を確認する
10. flow_state.json の derived field が progress と矛盾していないか確認する
11. 必要に応じて block を返す
```

### 15.2 終了許可条件

```text
- pending_user_intent がない
- input_journal に unclassified / classified / needs_confirmation の未処理入力がない
- active な interrupt がない、または明示的に cancel / complete 済み
- progress.json 上で current_task の required nodes が完了している
- current_task.status が completed または cancelled で、progress.json と矛盾しない
```

## 16. ユーザー割り込みの扱い

### 16.1 原則

ユーザー入力は最上位命令である。
そのため、割り込みを即フロー違反として潰してはいけない。

### 16.2 割り込み時の動作

```text
1. 現在の current_task を return_to として保存
2. interrupt_stack に新規 interrupt を積む
3. mode = interrupted にする
4. Codex には割り込み作業を進めさせる
5. Stop hook で、完了後に戻り先へ復帰させる
```

### 16.3 割り込み完了

割り込み完了判定は初期実装では自動化しすぎない。
以下のいずれかで完了扱いにする。

- Codex が明示的に割り込み作業完了を出力する
- ユーザーが「それでOK」「戻って」と言う
- Stop hook が復帰を要求し、Codex が戻り先 node を実行する

## 17. 追加情報の扱い

追加情報は割り込みではない。

```text
例:
- 対象は v2 系だけです
- 今回は Linux だけでいいです
- テストは integration test だけ見てください
```

動作。

```text
1. context に追加する
2. current_task は維持する
3. current node も維持する
4. next node は必要なら条件付きで更新する
5. Codex に追加情報を反映して続行させる
```

## 18. 方針変更の扱い

方針変更は current flow に影響する。

```text
例:
- テストは不要でいい
- 設計書更新だけでいい
- stable release ではなく prerelease として扱って
```

動作。

```text
1. input_journal に flow_change 分類を記録する
2. context に flow_change として記録する
3. required node の一部を skip / optional にする提案を flow_overrides に proposed として記録する
4. required node を緩める場合は、対象 node、変更理由、適用範囲をユーザーに確認する
5. ユーザーの明示確認後に flow_overrides を active / explicit_user_confirmed に更新する
6. Stop hook は確認済み override を適用した後の flow を基準に判定する
```

### 18.1 override contract

`flow_change` による required node の skip、optional 化、完了条件緩和は durable state に残す。

```json
[
  {
    "override_id": "override-20260530-0001",
    "input_id": "2026-05-30T10:31:58.123456Z-userprompt-0001",
    "status": "proposed",
    "confirmation": "missing",
    "kind": "skip_required_node",
    "target_nodes": ["implementation_phase/hook_state_task#review"],
    "scope": "current_task",
    "reason": "ユーザーが今回は package version 確認不要と依頼したため",
    "requested_by": "user",
    "classified_by": "codex_body",
    "confidence": 0.82,
    "applied_at": null
  }
]
```

`status` は以下を取る。

| status | 意味 |
|---|---|
| `proposed` | Codex 本体が仮採用したが、Stop 判定には未適用 |
| `active` | ユーザー明示確認済みで Stop 判定へ適用する |
| `rejected` | ユーザーが否定した |
| `expired` | task 変更などで適用範囲外になった |

確認済み override は以下の形に更新する。

```json
{
  "override_id": "override-20260530-0001",
  "status": "active",
  "confirmation": "explicit_user_confirmed",
  "confirmed_by_input_id": "2026-05-30T10:33:00.000000Z-userprompt-0002",
  "applied_at": "2026-05-30T10:33:05Z"
}
```

`scope` は `current_task`、`current_workflow`、`current_session` のいずれかとする。
初期実装では `current_task` 以外の scope は確認済みでも Stop hook が `unsupported_override_scope` として block してよい。

## 19. 中止・復帰の扱い

### 19.1 中止

```text
例:
- 今の作業はやめて
- もういい
- この件は中止
```

動作。

```text
1. current_task.status = cancelled
2. mode = cancelled
3. Stop hook は元 task の未完了 node を block 理由にしない
```

### 19.2 復帰

```text
例:
- 元の作業に戻って
- 続けて
- さっきの作業に戻って
```

動作。

```text
1. interrupt_stack の active task を閉じる
2. return_to を current_task に戻す
3. mode = resuming
4. next node から再開させる
```

## 20. セキュリティ・信頼境界

### 20.1 agent 自己申告を信用しない

以下は信用しない。

```text
- Codex が「これは割り込みです」と言うだけ
- Codex が「この step は完了しました」と言うだけ
- Codex が「Stop を通してよい」と言うだけ
```

採用する根拠。

```text
- UserPromptSubmit で保存したユーザー入力
- Codex 本体が `update_input_journal.py` 経由で state に記録した分類結果
- repository workflow と CodexSkill step 定義の evidence
- 実際の tool input / output
- state に記録された変更履歴
```

## 21. 失敗時の動作

### 21.1 分類失敗

Codex 本体が分類に迷う場合、または分類結果を state に反映できない場合は `ambiguous` にする。

```json
{
  "mode": "pending_user_intent",
  "pending_user_intent": {
    "required_agent_action": "ユーザー入力の意図を確認してください。"
  }
}
```

### 21.2 state 破損

state JSON が壊れていた場合。

```text
1. validate_state.py で破損対象と root contract を確認する
2. state_root/.flow-state.lock を取得する
3. 壊れたファイルを .bak に退避し、hook_logs に復旧開始を記録する
4. progress.json が読める場合は canonical 履歴として保持する
5. progress.json が読めない場合は .bak から復元できる範囲を明示し、復元不能ならユーザー確認を要求する
6. script contract に従って最小 state を再生成する
7. validate_state.py を再実行し、結果を report に残す
8. Codex に state 復旧結果と未確認事項を出す
```

## 22. 実装順

### Phase 1: state と Stop hook

```text
1. flow_state.json の形式を決める
2. progress.json の形式を決める
3. Stop hook で未完了 node を block する
4. validate_state.py で初期 state を検証する
5. update_input_journal.py の record_user_prompt / classify_input を使って state 更新を確認する
```

### Phase 2: PostToolUse

```text
1. PostToolUse payload をログ出力する
2. tool_name / tool_input の shape を確認する
3. evidence と照合して update_progress.py に完了候補を渡す
4. sync_flow_state.py で derived field を同期する
5. Flow State を出力する
```

### Phase 3: UserPromptSubmit

```text
1. UserPromptSubmit payload をログ出力する
2. ユーザー入力抽出を実装する
3. active flow がなければ no-op を返す
4. active flow があれば Flow State と分類要求を返す
5. Codex 本体が分類結果を state に反映できることを確認する
```

### Phase 4: PreToolUse

```text
1. 危険コマンドだけ block する
2. mode = pending_user_intent のときは作業系 tool を block する
3. 順序違反 block は必要最小限から始める
```

## 23. 最小実装の擬似コード

### 23.1 UserPromptSubmit

```python
payload = read_json_stdin()
user_prompt = extract_user_prompt(payload)
roots = resolve_roots_from_env_or_config()
state = load_flow_state(roots.state_root)
validate_roots(roots, state.roots)

if not state.current_task or state.current_task.status != "active":
    allow_noop()

input_result = run_update_input_journal_script(
    state_root=roots.state_root,
    user_prompt=user_prompt,
    operation="record_user_prompt",
)

message = build_flow_state_message(
    state=state,
    input_id=input_result.state_summary.input_id,
    user_prompt=user_prompt,
    required_agent_action="input_id に分類結果を紐づけて update_input_journal.py classify_input を呼び出してください",
)

print(json_response_for_codex(message))
```

### 23.2 PostToolUse

```python
payload = read_json_stdin()
roots = resolve_roots_from_env_or_config()
state = load_flow_state(roots.state_root)
progress = load_progress(roots.state_root)
workflow = load_current_workflow(roots.workflow_root, state)
step_sets = load_referenced_step_sets(roots.step_root, workflow)
flow = compose_runtime_flow(workflow, step_sets)

completed_nodes = detect_completed_nodes(payload, flow)
progress_result = run_update_progress_script(
    state_root=roots.state_root,
    completed_nodes=completed_nodes,
    evidence_source="PostToolUse",
)

confirmed_overrides = confirmed_flow_overrides(state)
sync_result = run_sync_flow_state_script(
    state_root=roots.state_root,
    workflow=workflow,
    step_sets=step_sets,
    confirmed_overrides=confirmed_overrides,
)

print(flow_state_message(sync_result.state, progress_result.completed_nodes, sync_result.next_node))
```

### 23.3 Stop

```python
roots = resolve_roots_from_env_or_config()
state = load_flow_state(roots.state_root)
progress = load_progress(roots.state_root)
workflow = load_current_workflow(roots.workflow_root, state)
step_sets = load_referenced_step_sets(roots.step_root, workflow)
flow = compose_runtime_flow(workflow, step_sets)

if state.mode == "pending_user_intent":
    block("ユーザー入力の意図を確認してください")

if has_unprocessed_input(state.input_journal):
    block("未処理のユーザー入力分類があります")

if state.mode == "interrupted":
    block("割り込み作業中です。完了後に戻り先へ復帰してください")

confirmed_overrides = confirmed_flow_overrides(state)

if has_uncompleted_required_nodes(flow, progress, confirmed_overrides):
    block("未完了 node があります。次の node を実行してください")

if derived_state_conflicts_with_progress(state, progress, flow, confirmed_overrides):
    block("flow_state.json と progress.json が矛盾しています")

allow()
```

## 24. 制約

この設計には以下の制約がある。

```text
- LLM 分類は非決定的である
- hooks の event payload shape は実環境で確認が必要
- PostToolUse の evidence 判定は完全ではない
- agent が行った意味的な作業完了を完全には機械判定できない
- ユーザーの曖昧な自然文は最終的に確認が必要になる
```

## 25. 採用判断

採用してよいケース。

```text
- Skill フローを守らせたい
- 作業の戻り先を失いたくない
- ユーザー割り込みを許容したい
- ユーザーにカスタムコマンドを強制したくない
- hook は常時起動するが、active flow がないときは no-op にしたい
```

採用しない方がよいケース。

```text
- hook は完全に deterministic である必要がある
- LLM の分類揺れを許容できない
- 短時間の単純作業が中心
```

## 26. 結論

本設計では、自然文理解を hook スクリプトだけで行わない。

```text
自然文理解:
  Codex 本体エージェント

状態管理:
  flow_state.json / progress.json

強制:
  PostToolUse / Stop / 必要なら PreToolUse

作業説明:
  SKILL.md

機械判定:
  repository workflow JSON + CodexSkill steps.json
```

これにより、ユーザーに `/info` や `/interrupt` のようなカスタムコマンドを強制せずに、Codex の Skill 実行フローをある程度矯正できる。

ただし、Codex 本体の自己申告だけで完了判定を通してはいけない。
Stop / PostToolUse hook は、state、progress、repository workflow、CodexSkill step 定義、実際の tool input / output を使って後追い検査する。

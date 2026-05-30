# Codex Hooks による Skill 実行フロー強制設計書

## 1. 目的

本設計書は、Codex の Skill に定義した作業フローを、hooks を用いてできるだけ強制・矯正するための設計をまとめる。

主目的は以下である。

- Skill に書かれた作業手順を Codex に守らせる
- ツール実行後に「今行っていたはずの作業」「今回実行した作業」「次に行う作業」を Codex に提示する
- 完了前に未完了ステップがあれば Stop hook で終了を止める
- ユーザーの追加情報・割り込み依頼・方針変更・中止・復帰を扱う
- 自然文分類は原則として本体エージェントに行わせる
- hook は分類結果の明示、state 更新、未完了 step の検査を担当する
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

Skill / flow.json
  hooks が読む機械可読な必須フローを書く

UserPromptSubmit hook
  active flow がある場合だけ Flow State と分類要求を Codex 本体に提示する

Codex 本体
  ユーザー入力を additional_info / interrupt / flow_change / cancel / resume / ambiguous に分類する
  分類結果に基づいて state 更新に必要な作業を行う

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
- flow の進捗管理
- 未完了 step の検出
- Stop 時の block
- 次作業の提示
- 再帰防止
- 分類失敗時の ambiguous 扱い
```

Codex 本体に任せないこと。

```text
- 自分自身の作業がフロー違反かどうかの最終判定
- hook block を回避する弁明
- 未完了 step の勝手な完了扱い
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

```text
repo/
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
    skills/
      release-governance-manager/
        SKILL.md
        flow.json
```

## 5. Skill flow 定義

### 5.1 `SKILL.md`

`SKILL.md` には、Codex と人間が読むための説明を書く。

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

### 5.2 `flow.json`

hooks は自然文の `SKILL.md` を直接解釈しない。  
同じフローを機械可読な `flow.json` として定義する。

例。

```json
{
  "skill": "release-governance-manager",
  "version": 1,
  "steps": [
    {
      "id": "read_breaking_changes",
      "description": "Design/BreakingChanges.md を読む",
      "required": true,
      "evidence": [
        {
          "tool": "Bash",
          "command_contains": "Design/BreakingChanges.md"
        }
      ]
    },
    {
      "id": "check_workflows",
      "description": ".github/workflows を確認する",
      "required": true,
      "evidence": [
        {
          "tool": "Bash",
          "command_contains": ".github/workflows"
        }
      ]
    },
    {
      "id": "check_package_version",
      "description": "package version source を確認する",
      "required": true,
      "evidence": [
        {
          "tool": "Bash",
          "command_contains": "VersionPrefix"
        },
        {
          "tool": "Bash",
          "command_contains": "Directory.Build.props"
        }
      ]
    },
    {
      "id": "summarize_decision",
      "description": "判断結果をまとめる",
      "required": true,
      "evidence": [
        {
          "type": "agent_output"
        }
      ]
    }
  ]
}
```

## 6. state 設計

### 6.1 `flow_state.json`

現在の作業状態を保持する。

```json
{
  "mode": "normal",
  "current_task": {
    "skill": "release-governance-manager",
    "status": "active",
    "current_step": "check_workflows",
    "next_step": "check_package_version"
  },
  "context": [],
  "interrupt_stack": [],
  "pending_user_intent": null
}
```

### 6.2 mode

`mode` は以下を取る。

| mode | 意味 |
|---|---|
| `normal` | 通常の Skill フロー進行中 |
| `interrupted` | ユーザー割り込み作業中 |
| `pending_user_intent` | ユーザー入力の分類が曖昧で確認待ち |
| `resuming` | 割り込みから元作業へ復帰中 |
| `cancelled` | 現在作業が中止された |
| `completed` | 現在作業が完了した |

### 6.3 context

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

### 6.4 interrupt_stack

割り込み作業を stack として保持する。

```json
[
  {
    "request": "先に README を直して",
    "summary": "README の文言を修正する",
    "status": "active",
    "return_to": {
      "skill": "release-governance-manager",
      "status": "active",
      "current_step": "check_workflows",
      "next_step": "check_package_version"
    }
  }
]
```

### 6.5 pending_user_intent

分類不能な入力を保持する。

```json
{
  "text": "それ先にやって",
  "classification": {
    "intent": "ambiguous",
    "confidence": 0.42,
    "candidates": ["interrupt", "flow_change"]
  },
  "required_agent_action": "これは割り込み作業か、現在フローの変更かをユーザーに確認する"
}
```

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

### 7.3 confidence の扱い

```text
confidence >= 0.8
  自動採用

0.5 <= confidence < 0.8
  仮採用し、Flow State に分類結果を明示する

confidence < 0.5
  pending_user_intent にして確認を強制する
```

## 8. UserPromptSubmit hook

### 8.1 目的

`UserPromptSubmit` hook は、ユーザー入力を受け取った直後に動く。
ここでは以下を行う。

- active flow がない場合は no-op にする
- active flow がある場合は現在の Flow State を Codex 本体に提示する
- Codex 本体にユーザー入力の分類と state 更新を明示的に要求する
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
active flow があれば分類要求を含む Flow State を生成する
  ↓
Codex 本体に Flow State を返す
```

## 9. PostToolUse hook

### 9.1 目的

`PostToolUse` hook は、ツール実行後に以下を行う。

- 実行した tool / input / output をもとに step 完了を判定する
- `progress.json` を更新する
- 現在の作業状態を Codex に提示する
- 次に行う作業を Codex に提示する

### 9.2 出力テンプレート

Codex には毎回、以下のような Flow State を返す。

```text
[Flow State]
本来行っていた作業:
- release-governance-manager / check_workflows

今回実行した作業:
- Bash: ls .github/workflows

現在の追加情報:
- 対象は v2 系のみ

次に行う作業:
- check_package_version: package version source を確認する

注意:
- 元の作業は完了していません。
```

### 9.3 割り込み中の出力

```text
[Flow State]
本来行っていた作業:
- release-governance-manager / check_workflows

今回の割り込み作業:
- README の文言修正

今回実行した作業:
- Edit: README.md

割り込み完了後に戻る作業:
- release-governance-manager / check_package_version
```

## 10. Stop hook

### 10.1 目的

`Stop` hook は、Codex が応答を終了しようとしたときに動く。  
未完了フロー、曖昧なユーザー入力、割り込みからの未復帰があれば終了を block する。

### 10.2 判定

```text
mode = normal
  required step が未完了なら block

mode = pending_user_intent
  ユーザー意図確認をしていなければ block

mode = interrupted
  割り込み作業完了後に戻り先へ復帰していなければ block

mode = resuming
  元作業の next_step に戻っていなければ block

mode = cancelled
  元作業への復帰は要求しない

mode = completed
  allow
```

### 10.3 block 例

```json
{
  "decision": "block",
  "reason": "未完了 step があります。次に check_package_version を実行してください。"
}
```

割り込み中。

```json
{
  "decision": "block",
  "reason": "割り込み作業中です。完了した場合は、中断前の作業に戻ってください。戻り先: release-governance-manager / check_package_version"
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
- 現在 step で許可されない編集を止める
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

[[hooks.UserPromptSubmit]]
command = "python3 .codex/hooks/user_prompt_flow_state.py"
timeout = 20

[[hooks.PostToolUse]]
command = "python3 .codex/hooks/post_tool_flow.py"
timeout = 20

[[hooks.Stop]]
command = "python3 .codex/hooks/stop_guard.py"
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
            "command": "python3 .codex/hooks/user_prompt_flow_state.py",
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
            "command": "python3 .codex/hooks/post_tool_flow.py",
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
            "command": "python3 .codex/hooks/stop_guard.py",
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
1. stdin JSON を読む
2. ユーザー入力を抽出する
3. flow_state.json を読む
4. active flow がなければ no-op を返す
5. active flow があれば現在の Flow State を作る
6. Codex 本体に分類値と state 更新の要求を提示する
7. pending_user_intent があれば確認優先の指示を返す
```

### 13.2 失敗時

この hook 自体はユーザー入力を分類しない。
そのため分類不能は Codex 本体に確認質問を要求する Flow State として扱う。

## 14. post_tool_flow.py 設計

### 14.1 処理

```text
1. stdin JSON を読む
2. tool_name / tool_input / tool_result を抽出する
3. current flow を読む
4. flow.json の evidence と照合する
5. 完了 step を progress.json に記録する
6. next_step を算出する
7. Flow State を Codex に返す
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

誤判定を避けたい step は `manual_required` とする。

## 15. stop_guard.py 設計

### 15.1 処理

```text
1. flow_state.json を読む
2. progress.json を読む
3. mode を確認する
4. 未完了 required step を探す
5. pending_user_intent を確認する
6. interrupt_stack を確認する
7. 必要に応じて block を返す
```

### 15.2 終了許可条件

```text
- pending_user_intent がない
- active な interrupt がない、または明示的に cancel / complete 済み
- current_task の required steps が完了している
- current_task.status が completed または cancelled
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
- Stop hook が復帰を要求し、Codex が戻り先 step を実行する

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
3. current_step も維持する
4. next_step は必要なら条件付きで更新する
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
1. context に flow_change として記録
2. required step の一部を skip / optional に変更する
3. 変更理由を state に残す
4. Stop hook は変更後の flow を基準に判定する
```

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
3. Stop hook は元 task の未完了 step を block 理由にしない
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
4. next_step から再開させる
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
- Codex 本体が state に記録した分類結果
- flow.json の evidence
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
1. 壊れたファイルを .bak に退避
2. 初期 state を作る
3. Codex に state 復旧が必要であることを出す
4. 必要ならユーザー確認を要求する
```

## 22. 実装順

### Phase 1: state と Stop hook

```text
1. flow_state.json の形式を決める
2. progress.json の形式を決める
3. Stop hook で未完了 step を block する
4. 手動で state を編集して動作確認する
```

### Phase 2: PostToolUse

```text
1. PostToolUse payload をログ出力する
2. tool_name / tool_input の shape を確認する
3. evidence と照合して progress を更新する
4. Flow State を出力する
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
state = load_flow_state()

if not state.current_task or state.current_task.status != "active":
    allow_noop()

message = build_flow_state_message(
    state=state,
    user_prompt=user_prompt,
    required_agent_action="ユーザー入力を分類し、必要なら state を更新してください",
)

print(json_response_for_codex(message))
```

### 23.2 PostToolUse

```python
payload = read_json_stdin()
state = load_flow_state()
flow = load_current_flow(state)

completed_steps = detect_completed_steps(payload, flow)
update_progress(completed_steps)

next_step = calculate_next_step(flow, progress)

print(flow_state_message(state, completed_steps, next_step))
```

### 23.3 Stop

```python
state = load_flow_state()
progress = load_progress()

if state.mode == "pending_user_intent":
    block("ユーザー入力の意図を確認してください")

if state.mode == "interrupted":
    block("割り込み作業中です。完了後に戻り先へ復帰してください")

if has_uncompleted_required_steps(state, progress):
    block("未完了 step があります。次の step を実行してください")

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
  flow.json
```

これにより、ユーザーに `/info` や `/interrupt` のようなカスタムコマンドを強制せずに、Codex の Skill 実行フローをある程度矯正できる。

ただし、Codex 本体の自己申告だけで完了判定を通してはいけない。
Stop / PostToolUse hook は、state、progress、flow.json、実際の tool input / output を使って後追い検査する。

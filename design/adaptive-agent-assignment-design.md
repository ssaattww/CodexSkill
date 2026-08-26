# 適応型agent割当設計

## 目的

delegated taskの性質に応じて、sub-agentへ適切なモデル、推論強度、fork方式を割り当てる。

単純なfile数や一律のreviewer設定ではなく、工程、判断負荷、不確実性、変更半径、重要度、反復性、分割可能性を評価する。選定結果と実際にruntimeへ適用されたprofileを分離し、割当理由とfallbackをreportへ残す。

本設計はIssue #13の「sub-agentの使用モデルがSkillへ定義されていない」という問題を解消する。

## 背景

既存flowには次の要素があった。

- `codex-delegation-executor`によるmain agentとsub-agentのexecutor選択
- `sub-agent-task-manager`によるbounded taskとreport契約
- `spawn-agent-model-overrides.md`によるhidden model overrideの適用方法
- `development-orchestrator`によるimplementation modelの事前ユーザー確認

一方、taskの性質からmodelとreasoning effortを選ぶ中央規則がなかった。そのため、callerごとにprofileが固定または手動選択され、次を区別できなかった。

- 既に手順が決まった反復作業
- 通常のbounded implementation
- 要件、設計、難しいdebug、reviewのような判断中心作業
- 一つの難問へ深く取り組む場合
- 複数の独立workstreamへ分割する場合

## 設計原則

### モデルと推論強度を別軸にする

モデルtierはtaskが要求する判断能力を表す。

- Luna: 決定済みの機械的・反復的・高volume作業
- Terra: 通常のbounded technical work
- Sol: 不確実、判断中心、高重要度、cross-system、design、難しいdebug、review

推論強度は同じ問題へどれだけ慎重に取り組むかを表す。

- `low`: exactな低risk変換
- `medium`: 通常実装またはdeterministic evidence
- `high`: 複数条件、debug、design、review
- `xhigh`: boundedかつ網羅性または重要度が高いaudit
- `max`: 一つの非常に難しく分割不能な問題

モデルtierを上げる条件とreasoning effortを上げる条件を混同しない。

### Ultraをreasoning effortにしない

参考記事のUltra相当は、単一agentの推論強度ではなく、独立workstreamへ分割し親が統合するmulti-agent戦略として扱う。

- `codex-delegation-executor`が分割可否を判断する
- 各bounded taskへ`sub-agent-task-manager`が個別profileを選ぶ
- `reasoning_effort: ultra`は生成しない

### 行数より変更半径を重視する

小さなdiffでもsecurity、authorization、migration、concurrency、compatibility、public API、releaseへ影響する場合は高重要度とする。

大きなdiffでも、手順と期待結果が完全に決まりdeterministic validatorがある反復処理ならLuna候補になりうる。

### requestedとappliedを分離する

runtime制約により、選択したprofileがそのまま適用されない場合がある。

- full-history forkはparent profileを継承する
- hidden overrideがbackendでrejectされる可能性がある
- runtimeでmodelが利用不能な場合がある

reportでは`requested`と`applied`、`application_status`を別に記録し、未適用profileを適用済みとしない。

## 責務配置

### `development-orchestrator`

- workflow開始時にroutineなimplementation model確認を要求しない
- userまたはrepositoryが明示したoverrideやbudget制約だけを取得する
- executor、assessment、requested/applied profileをlifecycle evidenceとして保持する

### `codex-delegation-executor`

- main agent、single sub-agent、multi-agent decompositionを選ぶ
- taskを次の軸で評価する
  - `task_kind`
  - `work_class`
  - `uncertainty`
  - `change_radius`
  - `criticality`
  - `repetition`
  - `decomposability`
  - `context_need`
- multi-agent分割のwrite ownership、blocking dependency、synthesisを確認する
- modelとreasoning effortの中央tableは持たない

### `sub-agent-task-manager`

- 各bounded taskのmodel tier、reasoning effort、fork policyを選ぶ
- explicit overrideの優先順位を適用する
- requested profileをruntimeへ適用する
- applied profileとfallbackをreportへ記録する
- taskが独立分割可能になった場合はdispatch前に`codex-delegation-executor`へ戻す

### `execution-cost-stabilizer`

- `max`またはmulti-agentを使う前に、再実行、過剰parallelism、evidence再利用を確認する
- costだけを理由に必要なmodel floorを下げない

## 処理flow

```text
development-orchestrator
  |
  | explicit override / repository policy / task context
  v
codex-delegation-executor
  |-- executor decision
  |-- delegation assessment
  |-- single vs multi-agent decision
  |
  +--> main agent
  |
  +--> bounded sub-agent task(s)
          |
          v
      sub-agent-task-manager
          |-- model tier selection
          |-- reasoning effort selection
          |-- fork policy selection
          |-- requested -> applied resolution
          |-- report pre-creation
          v
      collaboration.spawn_agent
```

## 選定入力

```yaml
task_kind: implementation | design | investigation | review | verification | environment_verification | intake_verification | standards | other
work_class: mechanical | bounded_technical | judgment_heavy
uncertainty: low | medium | high
change_radius: local | cross_module | cross_system
criticality: ordinary | high
repetition: single | high_volume
decomposability: single | sequential_dependencies | independent_workstreams
context_need: fresh | bounded_history | full_history
constraints:
  user_override: null
  repository_policy: null
  runtime_availability: known | unknown
```

非自明な分類にはsource evidenceを付ける。不明な場合は低く見積もらず、uncertaintyを上げる。

## profile選定

### model floor

| 条件 | 最低tier |
| --- | --- |
| low uncertainty、local、ordinary、deterministic、mechanical | Luna |
| 通常のbounded implementationまたはfocused verification | Terra |
| requirement/design、open-ended investigation、cross-system、高重要度、review | Sol |

複数条件が該当する場合は最も高いfloorを採用する。

### task default

| task | default |
| --- | --- |
| exact repetitive transformation | Luna `low` |
| deterministic build/test execution | Luna `medium` |
| ordinary bounded implementation | Terra `medium` |
| cross-module implementation | Terra `high` |
| localized debug with concrete hypothesis | Terra `high` |
| design / requirement interpretation | Sol `high` |
| open-ended or cross-layer investigation | Sol `high` |
| initial normal review | Sol `high` |
| focused fix verification | Terra `high` |
| independent final review / release audit | Sol `xhigh` |

失敗したdeterministic verificationは同じLuna taskとして再実行せず、investigationへ再分類する。

### `max` gate

`max`は次を全て満たす場合だけ使用する。

- 一つの問題が主要blockerである
- workstreamへ安全に分割できない
- `high`または`xhigh`で不足する具体的理由がある
- `execution-cost-stabilizer`でscopeとevidence再利用を確認した

### multi-agent gate

複数agentへ分割するには次を全て満たす。

- 独立workstreamが2件以上ある
- scope、non-goals、evidence、report ownerを各taskへ定義できる
- write ownershipが重複しない、またはread-onlyである
- blocking investigation dependencyがない
- parent synthesisが定義されている
- parallelismの実益がある

各taskは別々にprofile選定する。

## override優先順位

1. 明示的なuser instruction
2. authoritative repository policy
3. runtime capabilityとmodel availability
4. automatic selection

explicit overrideがautomatic floorを下回る場合も、silentに置換しない。mismatchを記録し、governing authorityに従う。

model tierだけが指定された場合はreasoning effortを自動選定できる。reasoning effortだけが指定された場合はmodel tierを自動選定できる。

## dispatch profile schema

```yaml
dispatch_profile:
  schema_version: 1
  selection_source: automatic | user_override | repository_policy
  task_kind: review
  signals:
    work_class: judgment_heavy
    uncertainty: high
    change_radius: cross_module
    criticality: high
    repetition: single
    decomposability: single
    context_need: fresh
  requested:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: xhigh
    fork_turns: none
    parallelism_mode: single_agent
  applied:
    model: gpt-5.6-sol
    reasoning_effort: xhigh
    fork_turns: none
  application_status: applied | inherited_parent_profile | fallback_applied | capability_gap
  reasons: []
  constraints: []
  escalation_triggers: []
```

## fork制約

- fresh specialistとoverrideを組み合わせる場合は`fork_turns: "none"`
- bounded historyだけ必要なら明示的なpositive partial fork
- full-history forkはparent profileを継承し、`inherited_parent_profile`として記録
- model specializationを優先する場合は、必要contextをtask-local promptへ明示してfresh spawnする

## 再分類とescalation

新しいevidenceがtask kind、不確実性、変更半径、重要度を変えた場合、profileを再計算する。

- 問題自体は同じだが慎重さが不足する場合: reasoning effortを上げる
- 問題の性質または必要判断能力が変わる場合: model tierを上げる
- 独立workstreamが判明した場合: multi-agent分割判断へ戻る
- runtime rejectionの場合: spawn適用contractに従いrequested/appliedを分離する

理由のないretry escalationは禁止する。

## 代表例

### formatting対象が多数ある

- mechanical
- low uncertainty
- local
- ordinary
- high volume

選定: Luna `low`。validator解釈が必要ならLuna `medium`。

### accepted designに基づく通常実装

- bounded technical
- lowからmedium uncertainty
- localまたはcross-module
- ordinary

選定: Terra `medium`。module間regression reasoningが必要ならTerra `high`。

### intermittent concurrency failureの原因調査

- judgment heavy
- high uncertainty
- cross-moduleまたはcross-system
- high criticality

選定: Sol `high`。一つの非分割root causeへ深い証明が必要な場合だけSol `max`。

### independent final review

- judgment heavy
- high uncertainty
- scopeに応じたchange radius
- release criticality

選定: Sol `xhigh`。過去review conclusionを引き継がないfresh spawnを使う。

### frontend、backend、migrationが独立している

単一のSol `max`へまとめない。write ownershipとdependencyを確認し、3 bounded taskへ分割する。各taskは個別にTerraまたはSolを選定し、parentが統合する。

## 既存設計との関係

Skill hierarchyのtopologyは変更しない。

- `codex-delegation-executor`から`sub-agent-task-manager`へ委譲する既存関係を維持する
- model overrideの実applicationは既存referenceを拡張する
- 新規runtime wrapperまたはcore Skillは追加しない

このため`design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`の同期対象内容は変更しない。

## 検証方針

CodexSkill repositoryの方針に従いTDDは適用しない。

- `python3 scripts/verify_skill_repository.py`
- `python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip`
- active relative Markdown link検証
- current PR HEAD SHAと一致するGitHub Actions runの確認
- selected/applied profile、Ultraとreasoning effort、full-history forkのcontract review

## 非対象

- Codex runtime本体へのmodel router実装
- runtime model availability APIの新設
- model価格に基づく自動optimization
- userのexplicit overrideをsilentに変更すること
- full-history forkへ異なるmodelを強制すること
- `reasoning_effort: ultra`の追加
- automatic merge

## 関連file

- [Codex Delegation Executor](../skills/codex-delegation-executor/SKILL.md)
- [Sub-Agent Task Manager](../skills/sub-agent-task-manager/SKILL.md)
- [Agent profile selection](../skills/sub-agent-task-manager/references/agent-profile-selection.md)
- [Spawn-agent model overrides](../skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md)
- [Development Orchestrator](../skills/development-orchestrator/SKILL.md)
- [Execution Cost Stabilizer](../skills/execution-cost-stabilizer/SKILL.md)

## 参考資料

- [役割分担で回すGPT-5.6 Luna / Terra / Sol](https://qiita.com/azarashin/items/0a37ec8cce7c75d7f5eb)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [OpenAI latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model)

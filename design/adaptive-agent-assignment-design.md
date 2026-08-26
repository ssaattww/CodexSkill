# 適応型agent割当設計

## 目的

delegated taskの性質に応じて、sub-agentへ適切なモデル、推論強度、fork方式を割り当てる。

単純なfile数や一律のreviewer設定ではなく、工程、判断負荷、不確実性、変更半径、重要度、反復性、分割可能性を評価する。選定結果と実際にruntimeへ適用されたprofileを分離し、割当理由、承認状態、fallbackをreportへ残す。

本設計はIssue #13の「sub-agentの使用モデルがSkillへ定義されていない」という問題を解消する。

## 背景

既存flowには次の要素があった。

- `codex-delegation-executor`によるmain agentとsub-agentのexecutor選択
- `sub-agent-task-manager`によるbounded taskとreport契約
- `spawn-agent-model-overrides.md`によるhidden model overrideの適用方法
- `development-orchestrator`によるworkflow lifecycle管理

一方、taskの性質からmodelとreasoning effortを選ぶ中央規則がなかった。そのため、callerごとにprofileが固定または手動選択され、機械的作業、通常実装、判断中心作業、難しい単一問題、独立workstream分割を区別できなかった。

また、`Sol xhigh`と`Sol max`は実行コストが高いため、品質要件だけで自動選定すると意図せず高コストなdispatchが発生する。そこで、この2 profileは自動選定の最終結果ではなく、ユーザー承認が必要なproposalとして扱う。

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

### `Sol xhigh` / `Sol max`はapproval-gated

`Sol xhigh`と`Sol max`は自動dispatchしない。

selectorがどちらかを必要と判断した場合は、次の状態遷移にする。

```text
automatic classification
  -> proposed_profile = Sol xhigh | Sol max
  -> userへ理由とcost noticeを提示
  -> STOP
      |-- approve -> requestedへ昇格 -> runtime application
      `-- reject  -> xhigh/maxを除外して再計算
```

approval前は`requested`と`applied`を空にする。repository policy、過去の別taskでの承認、沈黙、推測したユーザー嗜好はapprovalとして扱わない。

現在taskでユーザーが明示的に`Sol xhigh`または`Sol max`を指定している場合のみ、その指示自体をapproval evidenceとして扱える。

このgateはreviewやrelease auditを含む全task kindへ適用し、repository policyとautomatic selectionより優先する。

### Ultraをreasoning effortにしない

参考記事のUltra相当は、単一agentの推論強度ではなく、独立workstreamへ分割し親が統合するmulti-agent戦略として扱う。

- `codex-delegation-executor`が分割可否を判断する
- 各bounded taskへ`sub-agent-task-manager`が個別profileを選ぶ
- `reasoning_effort: ultra`は生成しない

### 行数より変更半径を重視する

小さなdiffでもsecurity、authorization、migration、concurrency、compatibility、public API、releaseへ影響する場合は高重要度とする。

大きなdiffでも、手順と期待結果が完全に決まりdeterministic validatorがある反復処理ならLuna候補になりうる。

### proposed / requested / appliedを分離する

profile stateは次の3段階を区別する。

- `proposed_profile`: cost gateなどによりまだ選択確定していない候補
- `requested`: 承認済みまたは通常自動選定され、runtimeへ要求するprofile
- `applied`: runtimeへ実際に適用されたprofile

full-history fork、hidden override rejection、runtime model unavailableなどにより`requested`と`applied`が異なる場合がある。未承認proposalを`requested`または`applied`として記録してはならない。

## 責務配置

### `development-orchestrator`

- workflow開始時にroutineなimplementation model確認を要求しない
- userまたはrepositoryが明示したoverrideやbudget制約だけを取得する
- `Sol xhigh` / `Sol max` proposalが出た場合はuser confirmation boundaryとしてworkflowを停止する
- executor、assessment、proposal/approval、requested/applied profileをlifecycle evidenceとして保持する

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
- `Sol xhigh` / `Sol max`ではproposalを生成し、approvalがない限りdispatchしない
- explicit overrideの優先順位を適用する
- approved requested profileをruntimeへ適用する
- applied profileとfallbackをreportへ記録する
- taskが独立分割可能になった場合はdispatch前に`codex-delegation-executor`へ戻す

### `execution-cost-stabilizer`

- `max` proposalまたはmulti-agentを使う前に、再実行、過剰parallelism、evidence再利用を確認する
- `Sol xhigh` / `Sol max` proposalのcost rationaleを支援する
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
          |
          |-- Sol xhigh/max ?
          |       |-- yes -> proposal + cost notice -> USER APPROVAL STOP
          |       `-- no  -> requested
          |
          |-- approved proposal -> requested
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
approval:
  required: false
  status: not_required | pending | approved | rejected
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
| independent final review / release audit | propose Sol `xhigh`, then stop for approval |

失敗したdeterministic verificationは同じLuna taskとして再実行せず、investigationへ再分類する。

### `xhigh` gate

Sol `xhigh`が適切と判断された場合、selectorは次を実行する。

- `proposed_profile`へSol `xhigh`を設定
- Sol `high`では不足する理由を記録
- higher effortによるexecution cost増加をユーザーへ伝える
- explicit approvalがなければdispatchを停止

承認後のみ`requested`へ昇格する。

### `max` gate

Sol `max`は次を全て満たす場合だけproposal可能とする。

- 一つの問題が主要blockerである
- workstreamへ安全に分割できない
- Sol `high`では不足する具体的理由がある
- `execution-cost-stabilizer`でscopeとevidence再利用を確認した
- ユーザーへcost notice付きで提案する
- explicit approvalを得るまでdispatchしない

`xhigh`を先に実行する必要はない。task evidenceから直接`max`候補になりうるが、いずれの場合もapproval gateは必須である。

### multi-agent gate

複数agentへ分割するには次を全て満たす。

- 独立workstreamが2件以上ある
- scope、non-goals、evidence、report ownerを各taskへ定義できる
- write ownershipが重複しない、またはread-onlyである
- blocking investigation dependencyがない
- parent synthesisが定義されている
- parallelismの実益がある

各taskは別々にprofile選定する。分割後の個別taskがSol `xhigh`またはSol `max`候補なら、そのtaskごとにapproval gateを通す。

## override優先順位

1. 明示的なcurrent-task user instruction
2. 未承認Sol `xhigh` / `Sol max`に対するmandatory user-approval gate
3. authoritative repository policy
4. runtime capabilityとmodel availability
5. automatic selection

explicit overrideがautomatic floorを下回る場合も、silentに置換しない。mismatchを記録し、governing authorityに従う。

repository policyがSol `xhigh`またはSol `max`を要求していても、それはproposalの根拠にはなるがuser approvalの代替にはならない。

## dispatch profile schema

通常profile:

```yaml
dispatch_profile:
  schema_version: 2
  selection_source: automatic | user_override | repository_policy
  task_kind: review
  requested:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: high
    fork_turns: none
  applied:
    model: gpt-5.6-sol
    reasoning_effort: high
    fork_turns: none
  application_status: applied | inherited_parent_profile | fallback_applied | capability_gap
  approval:
    required: false
    status: not_required
```

approval待ちprofile:

```yaml
dispatch_profile:
  schema_version: 2
  selection_source: automatic | repository_policy
  proposed_profile:
    model_tier: sol
    model: gpt-5.6-sol
    reasoning_effort: xhigh | max
    fork_turns: none
  requested: null
  applied: null
  application_status: awaiting_user_approval
  approval:
    required: true
    status: pending
    approved_by: null
    approval_evidence: null
  reasons:
    - why Sol high is insufficient
  cost_notice:
    - higher reasoning effort increases execution cost
```

承認後はapproval evidenceを保存し、approved proposalを`requested`へ昇格してからruntime applicationへ進む。

## fork制約

- fresh specialistとoverrideを組み合わせる場合は`fork_turns: "none"`
- bounded historyだけ必要なら明示的なpositive partial fork
- full-history forkはparent profileを継承し、`inherited_parent_profile`として記録
- model specializationを優先する場合は、必要contextをtask-local promptへ明示してfresh spawnする
- approvalはfork制約を上書きしない

## 再分類とescalation

新しいevidenceがtask kind、不確実性、変更半径、重要度を変えた場合、profileを再計算する。

- 問題自体は同じだが慎重さが不足する場合: reasoning effortを上げる
- 問題の性質または必要判断能力が変わる場合: model tierを上げる
- 独立workstreamが判明した場合: multi-agent分割判断へ戻る
- escalation結果がSol `xhigh`またはSol `max`ならproposalへ変換し、user approval stopへ入る
- runtime rejectionの場合: spawn適用contractに従いrequested/appliedを分離する

理由のないretry escalationは禁止する。

## 代表例

### formatting対象が多数ある

選定: Luna `low`。validator解釈が必要ならLuna `medium`。

### accepted designに基づく通常実装

選定: Terra `medium`。module間regression reasoningが必要ならTerra `high`。

### intermittent concurrency failureの原因調査

通常はSol `high`。一つの非分割root causeへ深い証明が必要でSol `high`では不足すると判断した場合はSol `max`を提案し、ユーザー承認まで停止する。

### independent final review

release-criticalな独立final reviewではSol `xhigh`を候補として提案する。Sol `high`との差とcost noticeを提示し、ユーザー承認前にはreviewerをdispatchしない。

### frontend、backend、migrationが独立している

単一のSol `max`へまとめない。write ownershipとdependencyを確認し、3 bounded taskへ分割する。各taskは個別にLuna、Terra、Solを選定し、parentが統合する。

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
- proposed/requested/applied profile、approval gate、Ultraとreasoning effort、full-history forkのcontract review

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

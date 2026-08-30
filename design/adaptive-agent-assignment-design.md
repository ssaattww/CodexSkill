# 適応型agent割当設計

## 目的

delegated taskの性質に応じて、sub-agentへ適切なmodel tier、reasoning effort、fork方式を割り当てる。

単純なfile数ではなく、task kind、判断負荷、不確実性、変更半径、重要度、反復性、分割可能性、context needを評価する。profileは`proposed`、`requested`、role/default-roleを考慮した`planned_runtime_profile`、runtimeで観測できた場合だけ確定する`applied`を分離し、割当理由、承認状態、runtime observability、fallback、reviewer continuityを証跡として残す。

本設計はIssue #13の「sub-agentの使用modelがSkillへ定義されていない」という問題を解消する。

## 設計原則

### model tierとreasoning effortを別軸にする

model tierはtaskが要求する判断能力を表す。

- Luna: 決定済みの機械的・反復的・高volume作業
- Terra: 通常のbounded technical work
- Sol: 不確実、判断中心、高重要度、cross-system、design、難しいdebug、review

reasoning effortは同じ問題へどれだけ慎重に取り組むかを表す。

- `low`: exactな低risk変換
- `medium`: 通常実装またはdeterministic evidence
- `high`: 複数条件、debug、design、review
- `xhigh`: boundedかつ網羅性または重要度が高いaudit
- `max`: 一つの非常に難しく、本質的に分割不能な問題

### `Sol xhigh` / `Sol max`はapproval-gated

`Sol xhigh`と`Sol max`は自動dispatchしない。

```text
automatic classification
  -> proposed_profile = Sol xhigh | Sol max
  -> userへ理由とcost noticeを提示
  -> STOP
      |-- approve -> requestedへ昇格
      `-- reject  -> xhigh/maxを除外して再計算
```

- approval前は`requested`へ昇格しない
- repository policy、過去taskの承認、沈黙、推測した嗜好はapprovalにしない
- current taskでユーザーが明示的にそのprofileを指定した場合はapproval evidenceとして扱える
- implementation、investigation、review、release auditを含む全taskへ適用する
- role/default roleがrequestedより高いprofileへ上書きする場合も同じgateを再評価する

### Ultraはreasoning effortではない

参考記事のUltra相当は、独立workstreamへ分割し親が統合するmulti-agent strategyとして扱う。

- `codex-delegation-executor`が分割可否を判断する
- 各bounded taskへ`sub-agent-task-manager`が個別profileを選ぶ
- `reasoning_effort: ultra`は生成しない

ただしcallerがidentity-sensitive lifecycleとして`decomposition_policy: forbidden`を指定したtaskは実行分割しない。

### decomposabilityとdecomposition policyを分離する

`decomposability`はtaskの構造に関する観測事実、`decomposition_policy`は実行制約である。

```yaml
decomposability: independent_workstreams
decomposition_policy: forbidden
decomposition_disposition: prohibited_by_review_lifecycle
parallelism_mode: single_agent
```

上記は矛盾しない。large reviewに独立review areaが複数存在しても、reviewer identity / continuity / one exhaustive passを守るためsingle reviewer executionを要求できる。

禁止事項:

- policyが`forbidden`だから観測signalを`decomposability: single`へ書き換える
- caller policyで分割禁止になったことを、`max`の「本質的にnon-decomposable」条件の根拠にする

### `proposed` / `requested` / `planned_runtime_profile` / `applied`を分離する

profile stateは次の段階を持つ。

- `proposed_profile`: user approvalなどが未確定の候補
- `requested`: spawn前に親がruntimeへ要求するprofile
- `role_plan`: explicit/default agent roleと、そのroleがmodel/reasoningへ与える影響
- `planned_runtime_profile`: role/default-role constraintsを加味したspawn前の予測
- `applied`: parentから最終runtime profileを観測できた場合だけ記録する事実

```text
classification
  -> proposed? -> approval
  -> requested
  -> agent role/default-role planning
  -> planned_runtime_profile
  -> floor / expensive-profile approval recheck
  -> spawn / inheritance / fallback attempt
  -> parent-visible runtime evidence
      |-- exact final snapshot -> applied
      `-- hidden/unobservable   -> applied=null + unverified state
```

禁止事項:

- `requested`または`planned_runtime_profile`を無条件に`applied`へcopyする
- spawn成功だけを根拠にexact model/reasoningが適用されたと断定する
- runtime rejectionを成功したapplicationとして扱う

## Codex MultiAgent V2のrole適用制約

現行Codex MultiAgent V2では、requested model/reasoning overrideを適用した後にexplicit/default agent roleが適用される。role configはmodel/reasoningを再変更できる。

そのためspawn前に次を記録する。

```yaml
role_plan:
  explicit_agent_type: <role or null>
  effective_role: <role name>
  role_config_evidence: <source or null>
  profile_effect: unchanged | changed | locked | unknown
planned_runtime_profile:
  model: <known planned model or null>
  reasoning_effort: <known planned effort or null>
```

規則:

- roleがprofileを変更/lockする場合、変更後profileでmodel floorとapproval gateを再評価する
- roleがSol `xhigh/max`を生む場合、requestedが安価でもuser approvalまでspawnしない
- roleがrequired floorより低いprofileを強制する場合はcapability/policy mismatch
- applicable role/default-role configの影響を確認できない場合、高コストgateを保証できないためpre-spawn capability gapとして停止する
- `planned_runtime_profile`は予測であり`applied`ではない

通常spawn outputでfinal model/reasoning snapshotが親に公開されない場合、spawn成功後も:

```yaml
applied: null
application_status: spawn_succeeded_profile_unverified
profile_observability: final_profile_hidden
```

とする。

## 責務配置

### `development-orchestrator`

- routineなimplementation model確認を要求しない
- user/repositoryが明示したoverrideやbudget制約だけを取得する
- Sol `xhigh/max` proposalではuser confirmation boundaryとしてworkflowを停止する
- executor、assessment、proposal、approval、requested、runtime observabilityをlifecycle evidenceとして保持する

### `codex-delegation-executor`

- main agent / single sub-agent / multi-agent decompositionを選ぶ
- taskを次の軸で評価する
  - `task_kind`
  - `work_class`
  - `uncertainty`
  - `change_radius`
  - `criticality`
  - `repetition`
  - `decomposability`
  - `context_need`
- write ownership、blocking dependency、parent synthesisを確認する
- model/reasoningの中央defaultは持たない

### `sub-agent-task-manager`

新規sub-agentについて次を所有する。

- model tier / reasoning effort / fork policy選定
- truthful decomposability evidenceとdecomposition policy disposition
- expensive Sol approval gate
- explicit/default role planning
- role-adjusted approval re-evaluation
- requested profileのspawn call plan
- runtime profile observability
- exact evidenceがある場合だけapplied profile
- runtime rejection / inheritance / parent-owned fallback evidence
- report persistence mode

### `review-enforcer`

review lifecycleについて次を所有する。

- reviewer identity
- normal reviewer continuity
- independent reviewer independence
- `decomposition_policy: forbidden`
- `parallelism_mode: single_agent`
- truthful decomposability signal / suppressed-decomposition disposition
- review mode
- report persistence mode
- frozen reviewed implementation HEAD
- retained independent-review evidence
- report-attestation lifecycle

new normal / replacement / independent reviewerは`sub-agent-task-manager`経由でdispatchする。

### `report-output-manager`

phaseごとに責務を分ける。

#### normal persistence

- `work-context-manager` + `report-writer`
- normal reportのpath予約・作成・永続化

#### independent-final reservation

- `work-context-manager`のみ
- exact pathをmetadata-onlyで予約
- `report-writer`を呼ばない
- report body/fileを作らない

#### independent-final attestation persistence

- passing verdict後のみ`work-context-manager` + `report-writer`
- retained evidenceからreport生成
- reserved pathへ初回persist
- report-only attestation commitとallowlist diff検証

## profile選定入力

```yaml
task_kind: implementation | design | investigation | review | verification | environment_verification | intake_verification | standards | other
work_class: mechanical | bounded_technical | judgment_heavy
uncertainty: low | medium | high
change_radius: local | cross_module | cross_system
criticality: ordinary | high
repetition: single | high_volume
decomposability: single | sequential_dependencies | independent_workstreams
decomposition_policy: allowed | forbidden
context_need: fresh | bounded_history | full_history
constraints:
  user_override: null
  repository_policy: null
  runtime_availability: known | unknown
  agent_type: null
  effective_default_role: null
approval:
  required: false
  status: not_required | pending | approved | rejected
```

非自明な分類にはsource evidenceを付ける。不明な場合は低く見積もらずuncertaintyを上げる。

## model floor

| 条件 | 最低tier |
| --- | --- |
| low uncertainty、local、ordinary、deterministic、mechanical | Luna |
| 通常のbounded implementationまたはfocused verification | Terra |
| requirement/design、open-ended investigation、cross-system、高重要度、review | Sol |

複数条件が該当する場合は最も高いfloorを採用する。

## task default

新規agentを作る場合だけ適用する。

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
| focused fix verification, replacement reviewerのみ | Terra `high` |
| independent final review / release audit | propose Sol `xhigh`; approval待ちで停止 |

失敗したdeterministic verificationは同じLuna taskとして再実行せず、investigationへ再分類する。

## reasoning effort gate

### `xhigh`

Sol `xhigh`が適切な場合:

- `proposed_profile`へ設定
- Sol `high`で不足する理由を記録
- cost増加をユーザーへ通知
- explicit approvalまでdispatchしない

### `max`

Sol `max`は次を満たす場合だけproposal可能とする。

- 一つの問題が主要blocker
- `decomposability`が本質的に`single`または分割不能なsequential dependencyである
- Sol `high` / `xhigh`では不足する具体的理由がある
- `execution-cost-stabilizer`でscopeとevidence reuseを確認済み
- userへcost noticeを提示
- explicit approvalまでdispatchしない

`decomposition_policy: forbidden`はnon-decomposable条件の代替にならない。

## multi-agent gate

`decomposition_policy: allowed`のtaskだけ分割候補にできる。

必要条件:

- 独立workstreamが2件以上
- 各taskへscope / non-goals / evidence / report ownerを定義できる
- write ownershipが重複しない、またはread-only
- blocking investigation dependencyがない
- parent synthesisが定義されている
- parallelismの実益がある

reviewer taskの例:

```yaml
decomposability: independent_workstreams  # observed fact when true
decomposition_policy: forbidden
decomposition_disposition: prohibited_by_review_lifecycle
parallelism_mode: single_agent
```

review scopeが大きいことだけを理由に複数reviewerへ分割しないが、scopeの構造自体は正しく記録する。

## spawn application

### spawn前

```yaml
dispatch_profile:
  schema_version: 4
  requested:
    model: gpt-5.6-sol
    reasoning_effort: high
    fork_turns: none
  role_plan:
    explicit_agent_type: null
    effective_role: default
    role_config_evidence: <source>
    profile_effect: unchanged
  planned_runtime_profile:
    model: gpt-5.6-sol
    reasoning_effort: high
  applied: null
  application_status: pending_runtime_result
  profile_observability: pending
```

`requested`をactual spawn argumentsへ使う。explicit roleがある場合は`agent_type`もcall planへ含める。default roleを使う場合もrole effectを事前評価する。

### spawn後: exact snapshotが見える場合

```yaml
applied:
  model: <observed final model>
  reasoning_effort: <observed final effort>
  fork_turns: <established fork policy>
application_status: applied_verified
profile_observability: verified_final_snapshot
```

### spawn後: final profileが見えない場合

```yaml
applied: null
application_status: spawn_succeeded_profile_unverified
profile_observability: final_profile_hidden
```

spawn成功だけを根拠にrequested/plannedをappliedへcopyしない。

full-history、runtime rejection、fallbackも同じ原則で扱い、exact final evidenceがない場合はunknown/unverifiedを保持する。

## reviewer continuity

既存normal reviewerまたはindependent reviewerをfix verification / finding closureで再利用するときは新規spawnしない。

- original profile evidence / observability stateを維持
- task defaultを再適用しない
- `application_status: reused_existing_agent_profile`
- reviewer identity、original exact/unverified evidence、continued modeを記録

同じreview lifecycle内で既に承認されたSol `xhigh/max` reviewerを再利用する場合、再承認は不要。replacement reviewerまたは新task lifecycleは新規selectionとしてapproval gateを通す。

## report persistence

### normal sub-agent / normal review

`report_persistence_mode: normal_persistence`を使う。

- `work-context-manager` + `report-writer`
- report pathを予約し、dispatch前にstandard templateを作成可能
- `Dispatch profile` sectionはparent-owned
- parentがpre-dispatch requested / role plan / planned runtime profileを記録
- spawn後にparentがexact appliedまたはunverified stateを記録
- childはhidden runtime stateを推測せずchild-owned sectionだけを埋める

### independent final review: reservation

freeze前:

- `report-output-manager` reservation-only phaseを使う
- `work-context-manager`のみ呼ぶ
- exact report pathをmetadataとして予約
- `report-writer`を呼ばない
- repository file/report bodyを作成しない
- 他の全repository変更をcommitしてHEADをfreeze

review中:

- independent reviewerはreserved report fileを作らない
- structured findings / coverage / commands / verdict / risks / unexploredをparentへ返す
- parentはreviewer outputとdispatch-profile evidenceをrepository外lifecycle evidenceとして保持

reviewがfailした場合:

- reserved report pathをpersistしない
- implementation -> normal fix verificationへ戻る
- 同じindependent reviewerでbounded finding/CI-delta closureを行う

### independent final review: attestation persistence

passing verdict後:

- `work-context-manager`でauthoritative contextを再確認
- 初めて`report-writer`を呼ぶ
- retained evidenceからreportを生成
- `report-output-manager`がreserved pathへ初回persist
- reviewed implementation HEADの直後にreport-only attestation commitを1件だけ作成
- allowlist diffを検証

## override優先順位

1. current-task user instruction / explicit expensive-profile approval
2. unapproved initial/role-adjusted Sol `xhigh/max` mandatory approval gate
3. existing reviewer continuity
4. caller-owned decomposition policy
5. authoritative repository policy
6. runtime role/default-role constraints / model availability
7. automatic selection

## fork制約

- fresh specialist + overrideは原則`fork_turns: "none"`
- bounded historyならexplicit positive partial fork
- full-historyはruntime inheritance/role pathに従う
- specialization優先ならtask-local contextを明示してfresh spawn
- reviewer continuity reuseは新規forkではない

## 再分類とescalation

新しいagentをdispatchする場合、新しいevidenceでtask kind / uncertainty / change radius / criticality / role-adjusted planが変化したらprofileを再計算する。

- failed deterministic verification -> investigation
- local implementationでarchitecture ambiguity判明 -> Sol floor
- independently separable -> decomposition allowed時だけ`codex-delegation-executor`へ戻る
- decomposition forbidden時はobserved decomposabilityを保持しsuppressed dispositionを記録
- 同一problemで慎重さ不足 -> effortを上げる
- problem nature変化 -> model tierを上げる
- role/default roleでprofile変化 -> floor/approval再評価
- Sol `xhigh/max`到達 -> proposal化しuser approval stop

existing reviewerがinitial reviewからfix verificationやbounded closureへ移るだけではprofileを再計算しない。

## 代表例

### formatting対象が多数ある

Luna `low`。validator解釈が必要ならLuna `medium`。

### accepted designに基づく通常実装

Terra `medium`。module間regression reasoningが必要ならTerra `high`。

### intermittent concurrency failureの原因調査

通常はSol `high`。本質的に一つの非分割root causeへ深い証明が必要な場合だけSol `max`をproposalし、承認まで停止する。

### roleがreasoningを上書きする

selectorがSol `high`をrequestedしても、default roleがSol `xhigh`をlockすることが事前に分かった場合、role-adjusted planをSol `xhigh` proposalへ変換しuser approvalまでspawnしない。role configを確認できずxhigh化の可能性を排除できない場合もspawnしない。

### normal reviewとfix verification

initial reviewerはnew Sol `high`がdefault。同じreviewerをfix verificationへreuseする場合はoriginal profile/observability evidenceを継続し、Terra `high`へ切り替えない。

### independent final review

single-agent execution policy。review scopeが独立workstreamを含むならその事実は保持するがdecompositionはsuppressed。Sol `xhigh`をproposalし、approvalとrole-plan safetyを確認後にfresh reviewerをdispatchする。report pathはmetadata予約だけでpassing verdictまでfileを作らない。

### frontend / backend / migrationが独立している

通常implementationなら3 bounded taskへ分割可能。各taskへ個別profileを選びparentが統合する。review-enforcerのone-reviewer lifecycleには実行分割を適用しないが、review scopeのdecomposability signalは保持する。

## 検証方針

CodexSkill repositoryの方針に従いTDDは適用しない。

- `python3 scripts/verify_skill_repository.py`
- `python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip`
- active relative Markdown link検証
- current PR HEAD SHAと一致するGitHub Actions runの確認
- requested -> role plan -> spawn -> applied/unverifiedの時系列contract review
- role/default-roleによるexpensive Sol approval再評価
- hidden final-profile metadata時にexact appliedを断定しないことのreview
- decomposability signalとdecomposition policy分離のreview
- reviewer single-agent execution / continuity contract review
- independent-final reservation phaseでreport-writerを呼ばないことのreview
- passing-verdict後だけattestation persistenceするcontract review
- fixed `Dispatch profile` templateのparent/child ownership review

## 非対象

- Codex runtime本体へのmodel router実装
- runtime model availability APIの新設
- parent-visible final agent config snapshot APIの新設
- model価格だけに基づくoptimization
- user explicit overrideのsilent変更
- full-history forkへ異なるmodelを強制
- `reasoning_effort: ultra`
- multi-agent review lifecycleの新設
- automatic merge

## 関連file

- [Codex Delegation Executor](../skills/codex-delegation-executor/SKILL.md)
- [Sub-Agent Task Manager](../skills/sub-agent-task-manager/SKILL.md)
- [Agent profile selection](../skills/sub-agent-task-manager/references/agent-profile-selection.md)
- [Spawn-agent model overrides](../skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md)
- [Development Orchestrator](../skills/development-orchestrator/SKILL.md)
- [Review Enforcer](../skills/review-enforcer/SKILL.md)
- [Report Output Manager](../skills/report-output-manager/SKILL.md)
- [Sub-agent report template](../skills/report-output-manager/references/sub-agent-report-template.md)
- [Execution Cost Stabilizer](../skills/execution-cost-stabilizer/SKILL.md)

## 参考資料

- [役割分担で回すGPT-5.6 Luna / Terra / Sol](https://qiita.com/azarashin/items/0a37ec8cce7c75d7f5eb)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [OpenAI latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [Codex MultiAgent V2 spawn implementation](https://github.com/openai/codex/blob/6478a751fde8884b2fdc76486fe23175a8e795d4/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs)

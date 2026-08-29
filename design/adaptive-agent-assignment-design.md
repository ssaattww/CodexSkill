# 適応型agent割当設計

## 目的

delegated taskの性質に応じて、sub-agentへ適切なmodel tier、reasoning effort、fork方式を割り当てる。

単純なfile数ではなく、task kind、判断負荷、不確実性、変更半径、重要度、反復性、分割可能性、context needを評価する。選定した`requested` profileとruntimeで実際に成立した`applied` profileを分離し、割当理由、承認状態、fallback、reviewer continuityを証跡として残す。

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
- `max`: 一つの非常に難しく分割不能な問題

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

### Ultraはreasoning effortではない

参考記事のUltra相当は、独立workstreamへ分割し親が統合するmulti-agent strategyとして扱う。

- `codex-delegation-executor`が分割可否を判断する
- 各bounded taskへ`sub-agent-task-manager`が個別profileを選ぶ
- `reasoning_effort: ultra`は生成しない

ただし、callerがidentity-sensitive lifecycleとして`decomposition_policy: forbidden`を指定したtaskは分割しない。

### `proposed` / `requested` / `applied`を時系列で分離する

profile stateは次の3段階を持つ。

- `proposed_profile`: user approvalなどが未確定の候補
- `requested`: spawn前に親がruntimeへ要求するprofile
- `applied`: spawn後にruntime evidenceから確定したprofile

`applied`はspawn前には確定できない。

```text
classification
  -> proposed? -> approval
  -> requested
  -> spawn / inheritance / fallback attempt
  -> runtime evidence
  -> applied + application_status
```

禁止事項:

- `requested`を無条件に`applied`へcopyする
- spawn入力として、まだ存在しない`applied`を使う
- runtime rejectionを成功したapplicationとして扱う

## 責務配置

### `development-orchestrator`

- routineなimplementation model確認を要求しない
- userまたはrepositoryが明示したoverrideやbudget制約だけを取得する
- `Sol xhigh` / `Sol max` proposalではuser confirmation boundaryとしてworkflowを停止する
- executor、assessment、proposal、approval、requested、appliedをlifecycle evidenceとして保持する

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

- model tier選定
- reasoning effort選定
- fork policy選定
- expensive Sol approval gate
- requested profileのspawn call plan
- post-runtime applied profileとapplication status
- runtime rejection / inheritance / parent-owned fallback evidence
- report persistence mode

callerが`decomposition_policy: forbidden`を指定した場合、taskをmulti-agent decompositionへ戻さない。

### `review-enforcer`

review lifecycleについて次を所有する。

- reviewer identity
- normal reviewer continuity
- independent reviewer independence
- single-reviewer enforcement
- review mode
- report persistence mode
- frozen reviewed implementation HEAD
- retained independent-review evidence
- report-attestation lifecycle

new normal / replacement / independent reviewerは`sub-agent-task-manager`経由でdispatchする。

### `report-output-manager`

- normal reportのpath予約・作成・永続化
- independent-final-review report pathのmetadata-only予約
- passing verdict後のreport-attestation persistence
- attestation diff allowlist検証

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
approval:
  required: false
  status: not_required | pending | approved | rejected
```

非自明な分類にはsource evidenceを付ける。不明な場合は低く見積もらず、uncertaintyを上げる。

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
- 安全にworkstream分割できない
- Sol `high`では不足する具体的理由がある
- `execution-cost-stabilizer`でscopeとevidence reuseを確認済み
- userへcost noticeを提示
- explicit approvalまでdispatchしない

## multi-agent gate

`decomposition_policy: allowed`のtaskだけ分割候補にできる。

必要条件:

- 独立workstreamが2件以上
- 各taskへscope / non-goals / evidence / report ownerを定義できる
- write ownershipが重複しない、またはread-only
- blocking investigation dependencyがない
- parent synthesisが定義されている
- parallelismの実益がある

`review-enforcer`が作るreviewer taskは常に:

```yaml
decomposability: single
decomposition_policy: forbidden
parallelism_mode: single_agent
```

review scopeが大きいことだけを理由に複数reviewerへ分割しない。normal reviewer continuityとindependent final reviewのone exhaustive passは、一つのreviewer identityへ結び付く。

## spawn application

### spawn前

```yaml
dispatch_profile:
  schema_version: 3
  requested:
    model: gpt-5.6-sol
    reasoning_effort: high
    fork_turns: none
  applied: null
  application_status: pending_runtime_result
```

`requested`をactual spawn argumentsへ使う。

### spawn後

runtime evidenceを確認してから次を記録する。

```yaml
applied:
  model: <actual model or inherited parent model>
  reasoning_effort: <actual effort or inherited parent effort>
  fork_turns: <actual fork policy>
application_status: applied | inherited_parent_profile | fallback_applied | capability_gap
```

full-history forkの場合はoverrideを付けずparent profileを継承し、runtime path確定後に`inherited_parent_profile`を記録する。

runtimeがhidden overrideをrejectした場合、rejectされたrequested profileを`applied`にしない。fallbackが許可される場合は親がfallbackを実行し、そのactual profileだけを`applied`へ記録する。

## reviewer continuity

既存normal reviewerまたはindependent reviewerをfix verification / finding closureで再利用するときは新規spawnしない。

- original applied model / effort / contextを維持
- task defaultを再適用しない
- `application_status: reused_existing_agent_profile`
- reviewer identity、original applied profile evidence、continued modeを記録

同じreview lifecycle内で既に承認されたSol `xhigh/max` reviewerを再利用する場合、再承認は不要。replacement reviewerまたは新task lifecycleは新規selectionとしてapproval gateを通す。

## report persistence

### normal sub-agent / normal review

`report_persistence_mode: normal_persistence`を使う。

- report pathを予約し、dispatch前にstandard templateを作成可能
- `Dispatch profile` sectionはparent-owned
- parentがpre-dispatch `requested`等を記録
- spawn後にparentが`applied` / `application_status`をruntime evidenceから記録
- childはhidden runtime stateを推測せず、child-owned task/result sectionだけを埋める

### independent final review

`report_persistence_mode: deferred_attestation`を使う。

freeze前:

- exact report pathをmetadataとして予約
- repository fileを作成・pre-populate・編集しない
- 他の全repository変更をcommitしてHEADをfreeze

review中:

- independent reviewerはreserved report fileを作らない
- structured findings / coverage / commands / verdict / risks / unexploredをparentへ返す
- parentはreviewer outputとdispatch-profile evidenceをrepository外のlifecycle evidenceとして保持

reviewがfailした場合:

- reserved report pathをpersistしない
- implementation -> normal fix verificationへ戻る
- 同じindependent reviewerでbounded finding/CI-delta closureを行う

passing verdict後:

- `report-writer`がretained evidenceからreportを生成
- `report-output-manager`がreserved pathへ初めてpersist
- reviewed implementation HEADの直後にreport-only attestation commitを1件だけ作成
- allowlist diffを検証

## override優先順位

1. current-task user instruction / explicit expensive-profile approval
2. unapproved Sol `xhigh/max` mandatory approval gate
3. existing reviewer continuity
4. caller-owned decomposition prohibition
5. authoritative repository policy
6. runtime capability / model availability
7. automatic selection

## fork制約

- fresh specialist + overrideは原則`fork_turns: "none"`
- bounded historyならexplicit positive partial fork
- full-historyはparent execution profile継承
- specialization優先ならtask-local contextを明示してfresh spawn
- reviewer continuity reuseは新規forkではない

## 再分類とescalation

新しいagentをdispatchする場合、新しいevidenceでtask kind / uncertainty / change radius / criticalityが変化したらprofileを再計算する。

- failed deterministic verification -> investigation
- local implementationでarchitecture ambiguity判明 -> Sol floorへ
- independently separable -> decomposition allowed時だけ`codex-delegation-executor`へ戻る
- 同一problemで慎重さ不足 -> effortを上げる
- problem nature変化 -> model tierを上げる
- Sol `xhigh/max`到達 -> proposal化しuser approval stop

existing reviewerがinitial reviewからfix verificationやbounded closureへ移るだけではprofileを再計算しない。

## 代表例

### formatting対象が多数ある

Luna `low`。validator解釈が必要ならLuna `medium`。

### accepted designに基づく通常実装

Terra `medium`。module間regression reasoningが必要ならTerra `high`。

### intermittent concurrency failureの原因調査

通常はSol `high`。一つの非分割root causeへ深い証明が必要ならSol `max`をproposalし、承認まで停止する。

### normal reviewとfix verification

initial reviewerはnew Sol `high`がdefault。同じreviewerをfix verificationへreuseする場合はSol `high`のoriginal applied profileを継続し、Terra `high`へ切り替えない。

### independent final review

single reviewer固定。Sol `xhigh`をproposalし、承認後にfresh reviewerをdispatchする。report pathは予約だけで、passing verdictまでrepository fileを作らない。

### frontend / backend / migrationが独立している

通常implementationなら3 bounded taskへ分割可能。各taskへ個別profileを選びparentが統合する。review-enforcerのone-reviewer lifecycleにはこの分割規則を適用しない。

## 検証方針

CodexSkill repositoryの方針に従いTDDは適用しない。

- `python3 scripts/verify_skill_repository.py`
- `python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip`
- active relative Markdown link検証
- current PR HEAD SHAと一致するGitHub Actions runの確認
- requested -> spawn -> appliedの時系列contract review
- expensive Sol approval gate review
- reviewer single-agent / continuity contract review
- independent-final deferred-attestation contract review
- fixed `Dispatch profile` templateのparent/child ownership review

## 非対象

- Codex runtime本体へのmodel router実装
- runtime model availability APIの新設
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

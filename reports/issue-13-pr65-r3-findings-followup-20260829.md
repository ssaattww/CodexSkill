# PR #65 R3 指摘対応レポート

## 対象

- repository: `ssaattww/CodexSkill`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- 対応対象review: R3
- 実装修正HEAD: `2cf3451747c03a045c9cd275c58238db04a4f151`
- target repository policy: CodexSkill maintenanceはnon-TDD

## 指摘

### F65-R3-001 / HIGH

`spawn_agent`成功後も、requested overrideが最終model/reasoningとして適用されたとは断定できない問題。

確認した現行Codex MultiAgent V2 implementationでは、requested model/reasoning override適用後に`apply_spawn_agent_role`が実行される。explicit/default agent roleはmodel/reasoningを再変更できる。また内部ではagent config snapshotが取得されるが、通常のparent-visible spawn outputは設定によりmetadataを隠し、`task_name`のみを返す。

このため、spawn成功だけを根拠に`applied=requested`とする証跡は不正確であり、roleがSol `xhigh` / `max`へ変更した場合にはuser approval gateを迂回する可能性がある。

### F65-R3-002 / HIGH

`report-output-manager`のRequired Skillsで`report-writer`を無条件invokeすると、independent-final-review前のmetadata-only report path reservationと矛盾する問題。

reservation時点ではcoverage/findings/verdictがまだ存在せず、report生成はできない。

### F65-R3-003 / MEDIUM

`decomposition_policy: forbidden`を理由に観測された`decomposability`を`single`へ書き換えていた問題。

実際にはreview scopeに独立workstreamが複数存在しても、reviewer identity / continuityを守るためexecution decompositionだけ禁止するケースがある。観測signalの改変はprofile理由を歪め、特にSol `max`のintrinsic non-decomposability条件を人工的に満たす可能性がある。

## 対応内容

### agent role / default roleを含むprofile planning

`skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`とselector contractを更新した。

spawn前に次を分離して記録する。

- `requested`: selector/user policyが要求するprofile
- `role_plan`: explicit `agent_type`またはeffective default roleと、そのconfig evidence
- `planned_runtime_profile`: known role constraints適用後の予測profile
- `applied`: parent-visibleなexact final runtime evidenceが存在する場合だけ記録

role/default roleがmodel tierまたはreasoning effortを変更・lockする場合、role-adjusted planでmodel floorとSol `xhigh` / `max` approval gateを再評価する。

role/default-role configの影響をspawn前に十分確認できず、高コストprofileへ変更されないことを保証できない場合は、silent dispatchせずpre-spawn capability gapとして停止する。

### runtime observability

spawn成功だけではexact `applied`を確定しない。

parent-visible final snapshotがある場合のみ:

```yaml
application_status: applied_verified
profile_observability: verified_final_snapshot
```

final model/reasoning metadataがparentから見えない場合:

```yaml
applied: null
application_status: spawn_succeeded_profile_unverified
profile_observability: final_profile_hidden
```

とし、requested/planned profileをappliedへcopyしない。

standard sub-agent report templateにもrole plan、planned runtime profile、runtime observabilityをparent-owned欄として追加した。

### report-output-managerのphase分離

`report-output-manager`をphase-specific contractへ変更した。

- normal persistence: `work-context-manager` + `report-writer`
- independent-final reservation: `work-context-manager`のみ。`report-writer`はinvokeしない
- independent-final attestation persistence: passing verdict後に`work-context-manager` + `report-writer`

reservation phaseではreport body/fileを作らず、exact path metadataだけを確定する。

### decomposabilityとdecomposition policyの分離

selectorとreview lifecycleを次のように変更した。

```yaml
decomposability: independent_workstreams
decomposition_policy: forbidden
decomposition_disposition: prohibited_by_review_lifecycle
parallelism_mode: single_agent
```

- `decomposability`: work structureの観測事実
- `decomposition_policy`: execution constraint
- `decomposition_disposition`: observed decompositionを実行しなかった理由

reviewerはsingle-agent executionを維持するが、review scopeの構造は偽装しない。

Sol `max`のnon-decomposable条件はintrinsicなtask propertyとして判定し、`decomposition_policy: forbidden`を根拠にしない。

## 主な変更ファイル

- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/report-output-manager/SKILL.md`
- `skills/report-output-manager/references/sub-agent-report-template.md`
- `skills/review-enforcer/SKILL.md`
- `skills/development-orchestrator/SKILL.md`
- `design/adaptive-agent-assignment-design.md`

## 現行Codex挙動の確認

確認対象:

- repository: `openai/codex`
- commit: `6478a751fde8884b2fdc76486fe23175a8e795d4`
- `codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs`
- `codex-rs/core/src/tools/handlers/multi_agents_common.rs`

確認事項:

- requested model/reasoning overrideの後に`apply_spawn_agent_role`が呼ばれる
- role applicationは`config.model` / `config.model_reasoning_effort`を変更できる
- runtime-only overrideはapproval/cwd/permission等であり、今回確認した範囲ではmodel/reasoningを変更していない
- child spawn後、runtime内部ではconfig snapshotを取得してtelemetryへ利用している
- parent-visible spawn resultはmetadata非表示時`task_name`のみとなり、final model/reasoningをparentが観測できないケースがある

したがって「runtime内部にsnapshotが存在すること」と「parentがexact final profileを証跡として取得できること」は区別した。

## 検証

CodexSkill repository policyに従いTDDは適用していない。

実装修正HEAD `2cf3451747c03a045c9cd275c58238db04a4f151` に対して、同一SHAのpull-request workflow runだけを検証対象とした。

- workflow: `Validate and release ChatGPT worker skills`
- run ID: `33248500555`
- run number: `191`
- run head SHA: `2cf3451747c03a045c9cd275c58238db04a4f151`
- build job: `99089994435`
- conclusion: `success`

成功step:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

artifact:

- name: `chatgpt-worker-skills-33248500555`
- ID: `9713604462`
- workflow run head SHA: `2cf3451747c03a045c9cd275c58238db04a4f151`
- digest: `sha256:16a39097e7851ce11aae09f8981f517ad9c224f5741a201cd209cc1cbbef91ed`

このreport commit後はPR HEADが変わるため、上記runをfinal PR HEAD CIとしては代用しない。final exact-head CIはreport commit後の新しいHEADに対して別途確認する。

## 残存制約

- 本repositoryはCodex runtime本体を変更しないため、parent-visible final agent config snapshot APIは追加していない。
- runtimeがfinal model/reasoningをparentへ公開しない場合、exact `applied`は不明のまま保持する。
- role/default-role configをspawn前に確認できないruntimeでは、高コストapproval gateを保証するためdispatchをcapability gapとして停止する。
- multi-agent review lifecycle自体は今回のscope外であり、review executionはsingle reviewer policyを維持する。

## Merge

mergeは行わない。

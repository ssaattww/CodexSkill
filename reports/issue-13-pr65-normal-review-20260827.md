# PR #65 通常レビュー報告

## メタデータ

- repository: `ssaattww/CodexSkill`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- Issue: `#13 sub-agentの使用モデル`
- review mode: `initial_review`
- reviewed implementation HEAD: `46776a85f09b101018338309ccd3221cc10592ad`
- base: `main`
- base HEAD: `2ea9522d494b2b37c1d8aabb340a3113cfd18240`
- commit range: `2ea9522d494b2b37c1d8aabb340a3113cfd18240...46776a85f09b101018338309ccd3221cc10592ad`
- reviewer role: normal reviewer
- reviewer independence: このreview chatではPR #65の実装・修正を行っていない
- development policy: CodexSkill repository maintenanceはnon-TDD
- verdict: `fail`

## 要求と設計の確認

対象要求は次のとおり。

- Issue #13: sub-agentの使用modelをtask種別に応じて定義する。
- PR #65: bounded taskごとにLuna / Terra / Sol、reasoning effort、fork policyを選定する。
- 追加要求: `Sol xhigh` / `Sol max`は自動dispatchせず、current-taskの明示的なユーザー承認後のみdispatchする。
- review / independent final review / release auditにも同じapproval gateを適用する。
- `codex-delegation-executor`はexecutorとmulti-agent decomposition、`sub-agent-task-manager`はper-task profileを所有する。

GPT-5.6のSol / Terra / Lunaと、`max`・`ultra`の公開上の位置づけはOpenAIの現行資料とも照合した。`ultra`を単一agentの深いreasoningではなくmulti-agent戦略として扱う設計方針自体には指摘なし。

参考:

- https://openai.com/index/gpt-5-6/
- https://openai.com/index/builders-guide-to-gpt-5-6/

## 変更範囲

変更9ファイルを全件確認した。

- `design/adaptive-agent-assignment-design.md`
- `reports/issue-13-adaptive-agent-assignment-handoff-20260826.yaml`
- `reports/issue-13-adaptive-agent-assignment-implementation-20260826.md`
- `reports/issue-13-sol-expensive-profile-approval-followup-20260827.md`
- `skills/codex-delegation-executor/SKILL.md`
- `skills/development-orchestrator/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`

直接依存として少なくとも次を横断確認した。

- `skills/review-enforcer/SKILL.md`
- `skills/report-output-manager/SKILL.md`
- `skills/report-output-manager/references/sub-agent-report-template.md`
- `skills/execution-cost-stabilizer/SKILL.md`
- `design/skill-hierarchy-design.md`
- root `AGENTS.md`
- `tasks/tasks-status.md`

## Findings

### F65-001 — HIGH — review dispatchがprofile selectorを通らず、review向けapproval gateを迂回できる

- origin: `coverage_miss`
- location:
  - `skills/development-orchestrator/SKILL.md:68,74`
  - `skills/review-enforcer/SKILL.md` のnormal reviewer / independent final reviewer dispatch
  - `design/skill-hierarchy-design.md` のreview-enforcer配下

#### 説明

PRでは`development-orchestrator`がnormal reviewとindependent final reviewを`review-enforcer`へ委譲し、review profileが`Sol xhigh` / `Sol max`になった場合はdispatch前にapproval stopすると定義している。

しかしcurrent HEADの`review-enforcer`はRequired Skillsに`sub-agent-task-manager`を含まず、required flowでもnormal reviewerとindependent final reviewerを直接dispatchしている。したがって、標準review lifecycle上で`agent-profile-selection.md`のclassification、requested/applied profile、`Sol xhigh` approval gateが実行される保証がない。

一方、既存の`design/skill-hierarchy-design.md`は`review-enforcer -> sub-agent-task-manager -> review-worker`を正規経路として記載しているため、Skill実装とhierarchy設計も一致していない。

#### 影響

- initial normal reviewをSol `high`へ割り当てる新規規則が実行されない可能性がある。
- independent final reviewでSol `xhigh` proposalを生成せず、ユーザー承認を取らないままreviewerをdispatchできる。
- PRが追加した高コストprofileのapproval safeguardをreview経路だけ迂回できる。
- PR本文の「review / independent final reviewにもgateを適用」という要求を満たさない。

#### required action

`review-enforcer`の新規reviewer dispatchを必ず`sub-agent-task-manager`経由へ変更する。normal review / independent final reviewのmode・criticalityをselectorへ渡し、`proposed_profile`が返った場合はspawn前にparentへapproval stopを返すこと。既存`design/skill-hierarchy-design.md`の経路とSkill実装を一致させること。

### F65-002 — MEDIUM — fix verificationのTerra defaultと同一reviewer継続契約が両立しない

- origin: `introduced_by_change`
- location:
  - `skills/sub-agent-task-manager/references/agent-profile-selection.md:118-120`
  - `skills/sub-agent-task-manager/SKILL.md` のreview default
  - `skills/review-enforcer/SKILL.md` のnormal reviewer continuity / step 6

#### 説明

新しいprofile tableはinitial normal reviewをSol `high`、focused fix verificationをTerra `high`としている。一方、`review-enforcer`はinitial reviewとfix verificationで同一のnormal reviewer sub-agentを可能な限り再利用することを必須にしている。

model / reasoning overrideはspawn時のprofileであり、既に起動済みのreviewerをfix verification時にSolからTerraへ変更するruntime application pathは定義されていない。

そのためfix verification時には次のどちらかになる。

- 同一reviewerを再利用する: 実際はinitial reviewのSol `high`のままで、Terra `high` defaultを適用できない。
- Terra `high`で新規spawnする: reviewer continuity契約を破る。

また、`dispatch_profile.application_status`にも「既存reviewer継続のため元profileを継承した」状態がない。

#### 影響

- fix verificationのrequested/applied profile証跡が実態と一致しなくなる。
- cost最適化としてTerraを選んだという記録だけが残り、実際にはSolを継続利用する可能性がある。
- selector規則を守ろうとするとreviewer continuityを壊すため、callerごとに挙動が分岐する。

#### required action

reviewer continuityとprofile selectionの優先関係を明示する。推奨は、既存normal reviewerを再利用できるfix verificationではinitial spawn時のapplied profileを継続し、その事実を専用のapplication statusまたはconstraintとして記録すること。Terra `high` defaultはreplacement reviewerなど新規spawnが必要な場合に限定するなど、selector table・`sub-agent-task-manager`・`review-enforcer`の契約を一貫させること。

### F65-003 — MEDIUM — 必須dispatch-profile証跡を標準sub-agent report templateへ保存できない

- origin: `coverage_miss`
- location:
  - `skills/sub-agent-task-manager/SKILL.md` required flow 9-13 / Report rules / Standard report sections
  - `skills/report-output-manager/references/sub-agent-report-template.md`

#### 説明

`sub-agent-task-manager`は、全dispatchについてselection inputs、proposal / approval evidence、requested / applied profile、selection source、reasons、constraints、fork policy、application status、escalation / fallbackをreportへ保存することをcompletion条件に追加した。

同時に、sub-agentにはpre-created standard reportのheading順・format・既存textを維持し、「blank section / placeholderだけを埋める」よう要求している。

しかし参照される`sub-agent-report-template.md`は従来の10 sectionのままで、dispatch profile、approval evidence、requested/applied、application status等のplaceholderが存在しない。`sub-agent-task-manager`自身の`Standard report sections`一覧も同じ旧構造のままである。

#### 影響

- 新しい必須profile evidenceをどこへ記録するかcallerごとに異なる。
- fixed templateを守ると必要証跡を構造化して残せず、証跡を追加すると「report formatを変更しない」というprompt契約と衝突する。
- `Sol xhigh` / `Sol max`のapproval evidenceを含むcost-control監査情報が欠落・散在し得る。
- completion gateをreport内容から一貫して確認できない。

#### required action

`sub-agent-report-template.md`と`sub-agent-task-manager`のStandard report sectionsを更新し、dispatch-profile専用sectionまたは固定YAML blockを追加する。少なくともselection inputs、proposal/approval、requested、applied、fork policy、application status、fallback/escalationを明示的なplaceholderとして持たせ、parent/childのどちらがどのfieldを埋めるかも定義すること。

## Required coverage

| criterion | disposition | evidence |
| --- | --- | --- |
| requirement and design conformance | `checked_finding` | F65-001, F65-002, F65-003 |
| correctness and edge cases | `checked_finding` | review dispatch bypassとreviewer reuse/profile変更不能を確認 |
| scope discipline and unrelated changes | `checked_no_finding` | 変更9ファイルはIssue #13、approval follow-up、report/handoffに限定 |
| changed files and direct dependency impact | `checked_finding` | `review-enforcer`、report templateまで横断しF65-001/F65-003を検出 |
| API / data / configuration / workflow / compatibility | `checked_finding` | spawn override、fork、review lifecycleを確認。F65-001/F65-002あり |
| error handling and failure diagnostics | `checked_no_finding` | runtime rejectionをfallback/capability_gapとして区別するcontractは存在 |
| security and secret handling | `not_applicable` | secret/auth処理の変更なし |
| tests and validation adequacy | `checked_finding` | static validator/buildは成功するが、review call pathとreport schemaのsemantic整合は検証対象外 |
| current-HEAD CI evidence | `checked_no_finding` | run `33019645686`の`head_sha`がreviewed HEADと完全一致しbuild成功 |
| report / tracking / documentation accuracy | `checked_finding` | implementation reportが`review-enforcer`をintentionally untouchedとしているがF65-001のintegration gapが残る |
| regression and maintainability risk | `checked_finding` | profile evidenceとreviewer continuityの契約不整合あり |

## CI / validation assessment

reviewed implementation HEAD `46776a85f09b101018338309ccd3221cc10592ad`と一致するrunだけを確認した。

- workflow: `Validate and release ChatGPT worker skills`
- run ID: `33019645686`
- run number: `165`
- event: `pull_request`
- run head SHA: `46776a85f09b101018338309ccd3221cc10592ad`
- conclusion: `success`
- build job ID: `98346565507`
- build job conclusion: `success`
- validation step: `Validate repository Skill architecture and active links` -> success
- ZIP build step: `Build and verify ChatGPT wrapper and core Skill ZIP` -> success
- artifact upload step: success
- artifact ID: `9625970350`
- artifact name: `chatgpt-worker-skills-33019645686`
- artifact digest: `sha256:45e2e8d58f4941260788e33d48a98b51ef48c9235600dcd109df732e5e73a091`

CI成功はstatic architecture/link/build validationの成功を示すが、F65-001からF65-003のsemantic contractまでは検査していないため、findingsを解消しない。

## Held / unexplored

### runtime model availability

- disposition: `held`
- reason: account/runtimeごとのsub-agent model availabilityをrepositoryから決定できない。
- current contract: unavailable時はsame/higher tier resolution、fallback、または`capability_gap`を記録する。
- verdict impact: 今回のfail理由ではない。

### live `collaboration.spawn_agent` integration

- disposition: `held`
- reason: repository CIにlive spawn fixtureがない。
- current Codex実装ではmodel override exposure/availabilityがruntime設定・catalogに依存するため、requested/applied分離とcapability stateを残す方針は妥当。
- verdict impact: 今回のfail理由ではない。

## Verdict

`fail`

required finding 3件があるため、このHEADをacceptしない。

## Next action

1. F65-001からF65-003を実装側でまとめて修正する。
2. 関連Skill、設計、report templateを同期する。
3. CodexSkill方針に従いrepository validator / ZIP buildを実行する。
4. push後、新しいPR current HEADと`head_sha`が一致するworkflow runだけをCI evidenceにする。
5. 同じnormal review chatでfinding-by-finding fix verificationを行う。
6. mergeは利用者が行う。
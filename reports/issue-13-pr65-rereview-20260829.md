# PR #65 再reviewレポート

## メタデータ

- repository: `ssaattww/CodexSkill`
- Issue: `#13 sub-agentの使用モデル`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- review mode: fix verification + current HEAD full re-review
- base: `main`
- base SHA: `2ea9522d494b2b37c1d8aabb340a3113cfd18240`
- reviewed implementation HEAD: `3ae8a067b648ffbbc956fdc651f3bdfa7b1316d2`
- previous review target: `46776a85f09b101018338309ccd3221cc10592ad`
- previous review report persistence HEAD: `5beb9511cf0ec508456628e6fe556edc19d5cd14`
- date: 2026-08-29
- verdict: `fail`

## 目的

前回reviewの `F65-001`〜`F65-003` が解消されたかをfinding identity単位で確認し、そのfix deltaだけでなくcurrent PR HEADの全変更と直接依存を再走査して、新規欠陥が残っていないか確認する。

## authoritative requirements

- Issue #13: sub-agentのtask特性に応じてmodel / reasoning effortを適切に割り当てる。
- user requirement: 一度で指摘点を網羅する。
- current PR policy: `Sol xhigh` / `Sol max` は自動dispatchせず、current-task user approvalを得てから使用する。
- repository policy: CodexSkill repository maintenanceはnon-TDD。
- CI policy: PR current HEAD SHAとworkflow run `head_sha`が一致するrunのみCI evidenceとして採用する。
- review lifecycle: normal reviewer continuityと、one fresh exhaustive independent final reviewerを維持する。
- report-attestation lifecycle: independent-final-review report pathはreview前に予約し、passing verdict後にreportを生成・persistして最大1 attestation commitにする。

## review scope

### 前回review後のfix delta

`5beb9511cf0ec508456628e6fe556edc19d5cd14...3ae8a067b648ffbbc956fdc651f3bdfa7b1316d2`

7 commits、7 files:

- `design/adaptive-agent-assignment-design.md`
- `reports/issue-13-pr65-review-findings-followup-20260829.md`
- `scripts/verify_skill_repository.py`
- `skills/report-output-manager/references/sub-agent-report-template.md`
- `skills/review-enforcer/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`

### current PR changed files

14 filesを確認した。

- `design/adaptive-agent-assignment-design.md`
- `reports/issue-13-adaptive-agent-assignment-handoff-20260826.yaml`
- `reports/issue-13-adaptive-agent-assignment-implementation-20260826.md`
- `reports/issue-13-pr65-normal-review-20260827.md`
- `reports/issue-13-pr65-review-findings-followup-20260829.md`
- `reports/issue-13-sol-expensive-profile-approval-followup-20260827.md`
- `scripts/verify_skill_repository.py`
- `skills/codex-delegation-executor/SKILL.md`
- `skills/development-orchestrator/SKILL.md`
- `skills/report-output-manager/references/sub-agent-report-template.md`
- `skills/review-enforcer/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`

Direct dependencyとして `skills/report-output-manager/SKILL.md`、`review-worker` contract、current Codex multi-agent / spawn-agent behavior、OpenAI GPT-5.6 model catalogも照合した。

## 前回finding fix verification

### F65-001 / HIGH — resolved

前回: review経路が`sub-agent-task-manager`のprofile selection / expensive-profile approval gateを通る保証がなかった。

確認結果:

- `review-enforcer` Required Skillsへ`sub-agent-task-manager`が追加された。
- new normal / replacement / independent reviewerは同Skill経由でdispatchする契約になった。
- `Sol xhigh` / `Sol max` proposal時はreviewer spawn前にstopする。
- repository validatorにも`review-enforcer -> sub-agent-task-manager` dependencyが追加された。

Disposition: `resolved`

### F65-002 / MEDIUM — resolved

前回: focused fix verificationのTerra `high` defaultとsame normal reviewer continuityが両立しなかった。

確認結果:

- new reviewerのdefaultとexisting reviewer continuityが分離された。
- reuseではoriginal applied profileを維持する。
- `application_status: reused_existing_agent_profile`、reviewer identity、original profile evidence、continued modeを記録する契約が追加された。

Disposition: `resolved`

### F65-003 / MEDIUM — resolved

前回: dispatch-profile evidence必須契約に対しfixed report templateへ記入欄がなかった。

確認結果:

- `sub-agent-report-template.md`へ固定`## Dispatch profile` sectionが追加された。
- selection inputs / source / proposal / approval / requested / applied / application status / continuity / fork / reasons のplaceholderが追加された。
- `sub-agent-task-manager`のStandard report sectionsと同期している。

Disposition: `resolved`

## 新規findings

### F65-R2-001 / HIGH — requested/appliedの時系列契約が自己矛盾

Origin: current HEAD full review

Location:

- `skills/sub-agent-task-manager/SKILL.md` Required flow step 7 / 14
- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md` Call shape / After the call

Description:

`sub-agent-task-manager`はspawn前のstep 7で`requested` profileを`applied runtime profile`へresolveし、step 14で`applied model and reasoning effort`をactual tool-call argumentsとしてdispatchするよう要求している。

一方`spawn-agent-model-overrides.md`は、spawn callの引数には`dispatch_profile.requested.model` / `requested.reasoning_effort`を使用し、call後にruntime evidenceから`applied`を記録し、requested値をruntime evidenceなしで`applied`へcopyしてはならないと定義している。

Impact:

`applied`はruntime applicationの結果であり、spawn前には確定できない。現契約のままでは、runtime evidence取得前に`applied`を捏造するか、spawn inputとruntime outcomeを同じ概念として扱うことになり、今回の主要要件であるrequested/applied分離が破綻する。hidden override rejection、full-history inheritance、fallback時に特に誤ったevidenceを生成しうる。

Required action:

flowを少なくとも次の順序に分離する。

1. selectorが`requested`とfork policyを確定する
2. runtime availability / full-history制約からcall可能なrequested argumentsを解決する
3. `requested`値をactual spawn argumentsとしてdispatchする
4. call outcome / runtime evidenceを取得する
5. その後だけ`applied`と`application_status`を記録する
6. rejection時はfallback / capability gapを記録する

Severity: `high`

### F65-R2-002 / HIGH — independent-final-review report-attestation lifecycleとpre-created child reportが衝突

Origin: F65-001 fixによって顕在化したcross-contract defect

Location:

- `skills/sub-agent-task-manager/SKILL.md` Required flow step 9-13
- `skills/review-enforcer/SKILL.md` Independent final review / Required flow step 11-15
- `skills/report-output-manager/SKILL.md` Independent-final-review report-attestation mode

Description:

`review-enforcer`のfresh independent reviewerは今回のfixにより必ず`sub-agent-task-manager`を通る。しかし`sub-agent-task-manager`は全new sub-agentについてdispatch前にrepository内report fileを作成し、reviewer自身がそのfileを埋めることを要求する。

一方independent-final-review lifecycleは、review前にはreport pathだけをreserveしてimplementation HEADをfreezeし、passing verdict後に`report-writer`を呼び、reserved pathへ初めてreportをpersistして最大1 report-attestation commitにする契約である。

Impact:

fresh independent reviewerをtask manager経由にすると、freeze後・verdict前にreserved report fileをcreate/editするrepository writeが発生し、pre-freeze repository-stable条件とpost-verdict report generation順序が崩れる。またreviewer-written child reportとpost-verdict `report-writer`のauthoritative report ownerが二重化する。

Required action:

independent final reviewを`sub-agent-task-manager`のreport pre-creationから明示的にspecial-caseする。例えば:

- review前はreserved repository pathだけ保持し、repository fileをcreate/editしない
- reviewer outputはparent-held evidenceまたはrepository外scratch artifactへ返す
- passing verdict後にのみ`report-writer`がreserved pathへcomplete reportを生成する
- そのreportだけをreport-attestation commitに含める

normal review / fix verificationのpre-created report contractとは分離する。

Severity: `high`

### F65-R2-003 / HIGH — reviewer taskがmulti-agent decompositionへ戻れるためsingle reviewer保証がない

Origin: F65-001 fixによって顕在化したreview lifecycle defect

Location:

- `skills/review-enforcer/SKILL.md` Reviewer dispatch contract / Required flow step 3, 12
- `skills/sub-agent-task-manager/SKILL.md` Required flow step 4
- `skills/sub-agent-task-manager/references/agent-profile-selection.md` Multi-agent decision
- `skills/codex-delegation-executor/SKILL.md` Multi-agent decomposition

Description:

`review-enforcer`はnormal reviewでone dedicated reviewer、independent final reviewでone fresh exhaustive reviewerを要求し、reviewer identity / continuity / independenceをcompletion gateとしている。

しかし委譲先`sub-agent-task-manager`はbounded taskがindependent workstreamsへ分割可能と判断すると`codex-delegation-executor`へ戻し、multi-agent decompositionを選べる。review-enforcerから渡すreview taskについて`decomposability: single`固定またはdecomposition禁止のcontractがない。

Impact:

large reviewが複数reviewerへ分割されると、誰がauthoritative normal reviewer / independent reviewerなのか、finding continuityをどのagentへ保持するのか、one exhaustive independent passを誰が満たしたのかが不定になる。parent synthesisだけでは既存`review-worker` / `review-enforcer`のsingle-reviewer identity contractを満たさない。

Required action:

現行review lifecycleを維持するなら、`review-enforcer`が作るreviewer taskは`decomposability: single`または`multi_agent_decomposition: forbidden_for_reviewer_identity`として固定し、`sub-agent-task-manager`からdelegation executorへ戻さないことを明記する。

review自体をmulti-agent化したい場合は別途、reviewer identity、finding authority、synthesis、continuity、independent-final-review completion semanticsをreview lifecycle側に設計する必要がある。

Severity: `high`

## validation assessment

### exact-head CI

Reviewed implementation HEAD:

`3ae8a067b648ffbbc956fdc651f3bdfa7b1316d2`

Matching pull_request workflow:

- workflow: `Validate and release ChatGPT worker skills`
- run ID: `33245090292`
- run number: `173`
- event: `pull_request`
- run `head_sha`: `3ae8a067b648ffbbc956fdc651f3bdfa7b1316d2`
- status: `completed`
- conclusion: `success`

PR bodyに記載されたrun identityとGitHub Actions API上のhead SHA / conclusionが一致している。

### external/runtime verification

OpenAI current model catalogでは `gpt-5.6-sol` / `gpt-5.6-terra` / `gpt-5.6-luna` が存在し、GPT-5.6 familyは`none`, `low`, `medium`, `high`, `xhigh`, `max` reasoning effortをsupportしていることを確認した。

Codex current sourceではspawn-agent model/reasoning override exposureとfull-history fork inheritance contractが存在することも確認した。

## coverage

- requirement/design conformance: `checked_finding`
- correctness / state transitions: `checked_finding`
- previous finding closure: `checked_no_finding`
- scope discipline: `checked_no_finding`
- changed files / direct dependencies: `checked_finding`
- API/runtime model identifiers: `checked_no_finding`
- fork / runtime application semantics: `checked_finding`
- review lifecycle / reviewer identity: `checked_finding`
- report lifecycle / attestation: `checked_finding`
- validation / exact-head CI: `checked_no_finding`
- documentation/report accuracy: `checked_no_finding`
- security / secret handling: `not_applicable`

## held / unexplored / unknown

### held

なし。

### unexplored

- live `collaboration.spawn_agent` integration fixtureはrepository CIに存在しないため、hidden overrideのactual backend behaviorはcontract/source reviewまで。

### unknown

- account/sessionごとの実際のCodex model availabilityはrepositoryから取得できない。

これらは今回の3 required findingを緩和しない。

## verdict

`fail`

前回3 findingはresolvedしたが、current HEADにはrequired high findingが3件残る。

## next action

1. `F65-R2-001` requested -> spawn -> applied の時系列を修正する。
2. `F65-R2-002` independent final reviewだけreport pre-creationを禁止するspecial-caseを追加する。
3. `F65-R2-003` review-enforcer配下reviewerのmulti-agent decomposition禁止または正式なmulti-agent review lifecycleを定義する。
4. fix後、current HEAD固有のrepository validator / ZIP build / exact-head CIを確認する。
5. 同じnormal reviewer contextで3 findingをidentity単位にfix verificationし、新規変更領域も再確認する。

mergeは行わない。

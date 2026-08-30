# PR #65 R3 再reviewレポート

## メタデータ

- repository: `ssaattww/CodexSkill`
- Issue: `#13 sub-agentの使用モデル`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- review mode: `fix verification + full changed-area regression review`
- branch: `feat/adaptive-agent-assignment`
- base: `main`
- reviewed implementation HEAD: `bfac39347647e66dfce7c8af925f2deab2300d92`
- previous review report: `reports/issue-13-pr65-rereview-20260829.md`
- previous findings: `F65-R2-001`〜`F65-R2-003`
- date: `2026-08-29`
- reviewer: current ChatGPT review chat
- verdict: `fail`
- merge: not performed

## authoritative requirements

- user instruction: PR #65を再reviewし、指摘点を一度で網羅する。
- uploaded review Skills:
  - `chat-review-worker`
  - `review-worker`
  - `work-context-manager`
  - `report-writer`
- repository instruction: root `AGENTS.md`に従いCodexSkill repository maintenanceへTDDを適用しない。
- project instruction: repository/PR操作にはGitHub connectorを使用し、current PR HEADとworkflow run `head_sha`が一致するrunだけをCI evidenceとして扱い、詳細reportをrepositoryへ保存し、mergeしない。

## scope

- 前回R2 findingのclosure確認
- R2後の8 commitの差分確認
- PR全変更fileとprofile selection / spawn application / review lifecycle / report lifecycleの直接依存確認
- 現行OpenAI GPT-5.6 model guidanceとの整合確認
- 現行`openai/codex`のspawn-agent runtime実装との整合確認
- exact-head CI確認

## non-goals

- findingの実装修正
- PR merge
- Codex runtime本体の変更
- multi-agent review lifecycleの新設

## target identity

- reviewed implementation HEAD: `bfac39347647e66dfce7c8af925f2deab2300d92`
- base HEAD: `2ea9522d494b2b37c1d8aabb340a3113cfd18240`
- R2 review-report HEAD: `5302de3d4bc4c7c29e53943bba30a7307df16cee`
- R2後のcommit数: 8

R2後に変更されたfile:

- `design/adaptive-agent-assignment-design.md`
- `reports/issue-13-pr65-r2-findings-followup-20260829.md`
- `skills/report-output-manager/SKILL.md`
- `skills/report-output-manager/references/sub-agent-report-template.md`
- `skills/review-enforcer/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`

PR全体のchanged fileは17件。

## R2 finding closure

### F65-R2-001 / HIGH

Status: `resolved`

確認内容:

- `requested`はpre-spawn instructionとして記録される。
- spawn前は`applied: null` / `application_status: pending_runtime_result`。
- actual spawn argsには`requested`を使用する。
- spawn / inheritance / rejection / fallback後にのみ`applied`を記録する。
- rejected requestを`applied`へcopyしない。

時系列の逆転は解消されている。

### F65-R2-002 / HIGH

Status: `resolved for the original finding`

確認内容:

- independent final reviewは`report_persistence_mode: deferred_attestation`。
- freeze前はreport pathをmetadata予約するだけでrepository fileを作成しない。
- independent reviewerはreserved report fileを編集せず、structured evidenceをparentへ返す。
- passing verdict後だけreserved pathへ初回persistして1 report-attestation commitを作る。

元findingの「freeze後にchild report fileを作る」問題は解消された。

ただし、この修正によって`report-output-manager`のRequired Skills contractとの新しい矛盾が顕在化した。詳細は`F65-R3-002`。

### F65-R2-003 / HIGH

Status: `resolved for the original finding`

確認内容:

- `review-enforcer`のnew normal / replacement / independent reviewerはsingle reviewer固定。
- `decomposition_policy: forbidden`。
- `parallelism_mode: single_agent`。
- task managerはreviewer taskをmulti-agent decompositionへ戻さない。

one-reviewer identity lifecycleは維持される。

ただし、policyとtask propertyを同じ値へ潰しているためselection evidence上の新規問題がある。詳細は`F65-R3-003`。

## 新規 findings

### F65-R3-001 / HIGH

#### location

- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`
- 関連: `skills/sub-agent-task-manager/SKILL.md`
- 関連: `skills/sub-agent-task-manager/references/agent-profile-selection.md`

#### description

PRはspawn後のruntime evidenceからexact `applied.model` / `applied.reasoning_effort`を記録する契約にしているが、現行Codex V2ではsuccessful `spawn_agent` resultだけでは最終profileを観測できない。

現行`openai/codex`実装では、`multi_agents_v2/spawn.rs`で次の順に処理される。

1. `apply_requested_spawn_agent_model_overrides`
2. `apply_spawn_agent_role`
3. spawn

`apply_spawn_agent_role`は`agent_type`省略時にも`default` roleを適用する。さらに`agent/role.rs`ではuser-defined roleがbuilt-inより優先され、role configは`model`と`model_reasoning_effort`を上書き可能。

一方、`spawn_agent` outputは`hide_agent_metadata`時に`task_name`しか返さず、model / reasoning effortをparentへ返さない。内部の`ThreadConfigSnapshot`はanalyticsには使われるがtool outputへ含まれない。

#### impact

- successful callを根拠に`applied=requested`とすると誤証跡になりうる。
- explicit user profile overrideがroleで上書きされても検出できない。
- user-defined `default` roleがSol `xhigh` / `max`へ上げる場合、PRのmandatory approval gateを通らず高コストprofileが実際に適用されうる。
- requested/applied分離の主要目的であるruntime fidelityが成立しない。

#### evidence

現行OpenAI Codex source:

- `https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs`
- `https://github.com/openai/codex/blob/main/codex-rs/core/src/agent/role.rs`
- `https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs`

確認事項:

- requested override後にroleを適用する。
- role configはmodel / reasoning effortをoverride可能。
- hidden-metadata outputはtask nameのみ。

#### required action

- spawn call planningへeffective agent role / default roleを含める。
- roleでmodel / reasoningが固定または変更される場合、そのeffective profileをapproval gateにも反映する。
- Sol `xhigh` / `max`へroleが上げる場合もdispatch前approvalを必須にする。
- actual snapshotをcallerが観測できないruntimeではexact `applied`を断定せず、`unknown` / `unverified_applied_profile`等のcapability stateを定義する。
- exact applied profileを記録するのはruntime metadataまたは決定的なrole/profile evidenceが得られる場合だけにする。

### F65-R3-002 / HIGH

#### location

- `skills/report-output-manager/SKILL.md`
- 関連: `skills/sub-agent-task-manager/SKILL.md`
- 関連: `skills/review-enforcer/SKILL.md`

#### description

`report-output-manager`冒頭のRequired Skillsは`work-context-manager`と`report-writer`を無条件に`Invoke`すると定義している。

一方、R2修正で追加されたindependent-final-reviewのbefore-review phaseは「reservation only」であり、review開始前にreportを生成せずexact path metadataだけを予約する契約になった。

uploaded `report-writer` contractではindependent-final-review report生成に次が必要:

- immutable reviewed implementation HEAD
- reviewer identity / independence
- complete coverage / findings / held / unexplored
- validation assessment
- verdict
- pre-reserved path

review前のreservation phaseにはこれらreview resultが存在しない。

#### impact

- `sub-agent-task-manager`がindependent reviewer dispatch前に`report-output-manager`を呼ぶと、同SkillのRequired Skillsを満たすためには`report-writer`を早過ぎる段階で呼ぶ必要がある。
- `report-writer`を呼べばdeferred-attestationの「review前はreportを生成しない」contractを破る。
- 呼ばなければ`report-output-manager`自身のRequired Skills contractを破る。
- independent final reviewのreservation phaseが自己矛盾している。

#### required action

`report-output-manager`をphase別contractへ分離する。

例:

- `reservation_only`: `work-context-manager`のみ必須。report path metadataを返し、`report-writer`を呼ばない。
- `normal_persistence`: `report-writer`を使用。
- `report_attestation_commit`: passing independent evidenceが揃った後に`report-writer`を必須化。

`Required Skills`もunconditional listではなくmode別に定義する。

### F65-R3-003 / MEDIUM

#### location

- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- 関連: `skills/review-enforcer/SKILL.md`
- 関連: `design/adaptive-agent-assignment-design.md`

#### description

`decomposability`はtask自身の性質、`decomposition_policy`はcallerが実行分割を許可するかというpolicyであり、別軸である。

現行contractは`decomposition_policy: forbidden`の場合、scopeに複数の独立review areaが存在しても`decomposability: single`へ上書きすると明記している。

これはobserved task signalをpolicyで書き換えている。

#### impact

- reportされるselection inputが実際のtask propertyと異なる。
- 将来のclassification / audit / tuningで「分割可能だったがidentity policyで禁止した」ケースと「本当に非分割だった」ケースを区別できない。
- `max` effortは「exceptionally difficult, non-decomposable problem」が条件なので、policyにより人工的に`single`化したsignalがmax判定を歪めうる。
- R2-003で必要だったsingle-reviewer保証自体には`decomposition_policy: forbidden`だけで足りる。

#### required action

- `decomposability`には観測されたtask propertyを保持する。
- review scopeが独立workstreamを含むなら`independent_workstreams`等をそのまま記録する。
- `decomposition_policy: forbidden`で実行上の分割だけ禁止する。
- profile selection / max判定では「inherent decomposability」と「policy-forbidden execution」を区別する。

## coverage

### requirement and design conformance

Disposition: `checked_finding`

- adaptive Luna / Terra / Sol selection: 概ね整合。
- Sol xhigh/max approval gate: Skill上は整合するがruntime role overrideで迂回可能 (`F65-R3-001`)。
- Ultraをmulti-agent strategyとして扱う方針: OpenAI current model guidanceと整合。

### correctness and edge cases

Disposition: `checked_finding`

- requested -> spawn -> applied時系列: R2問題はresolved。
- role post-override / hidden metadata edge: findingあり (`F65-R3-001`)。
- full-history inheritance: contract上整理済み。

### scope discipline

Disposition: `checked_no_finding`

R2対応は前回finding closureと関連contract同期に限定されている。

### changed files and direct dependency impact

Disposition: `checked_finding`

- task manager / profile selector / spawn reference / review enforcer / report manager / designを横断確認。
- report managerのmode dependency contradictionあり (`F65-R3-002`)。

### API / runtime compatibility

Disposition: `checked_finding`

OpenAI current sourceと比較し、role application orderとmetadata visibilityにcompatibility findingあり (`F65-R3-001`)。

### error handling and fallback

Disposition: `checked_no_finding` with finding overlap

- runtime rejectionをcapability gap / parent-owned fallbackとして扱う設計は存在する。
- exact applied observability不足は`F65-R3-001`で扱う。

### security / secret handling

Disposition: `not_applicable`

新規secret handlingなし。

### tests and validation adequacy

Disposition: `checked_no_finding`

CodexSkill repository policyによりTDDはnot applicable。repository validator / ZIP build / exact-head GitHub Actionsを使用。

### current-HEAD CI evidence

Disposition: `checked_no_finding`

reviewed HEAD `bfac39347647e66dfce7c8af925f2deab2300d92`:

- workflow: `Validate and release ChatGPT worker skills`
- run ID: `33246248774`
- run number: `182`
- run head SHA: `bfac39347647e66dfce7c8af925f2deab2300d92`
- conclusion: `success`
- artifact: `chatgpt-worker-skills-33246248774`
- artifact ID: `9712923664`
- digest: `sha256:72362ef0717170a990ca6067d6027e07f16610b1a8eb6c62e363feebda2d4927`

別SHAのrunは使用していない。

### report / documentation accuracy

Disposition: `checked_finding`

R2 follow-up reportはR2 findingへの対応内容を正しく記録している。
ただし新しいruntime compatibility issueとreport dependency issueは未記録であり、本reportでfinding化した。

### regression / maintainability

Disposition: `checked_finding`

- decomposability signalをpolicyで潰す設計は将来のclassification evidenceを損なう (`F65-R3-003`)。

## external/current verification

OpenAI current documentationを確認した。

- GPT-5.6 current IDs:
  - `gpt-5.6-sol`
  - `gpt-5.6-terra`
  - `gpt-5.6-luna`
- GPT-5.6 reasoning effort:
  - `none`
  - `low`
  - `medium`
  - `high`
  - `xhigh`
  - `max`
- model guidanceはMulti-agentをCodex ultra modeと類似するstrategyとして説明している。

Sources:

- `https://developers.openai.com/api/docs/models`
- `https://developers.openai.com/api/docs/guides/latest-model`

この部分にはfindingなし。

## held

なし。

## unexplored

- live account上の実`collaboration.spawn_agent` override integration test。repositoryにfixtureなし。
- 実user環境のcustom agent role設定。runtime source上、custom/default roleがmodel/reasoningを上書き可能であることまでは確認済み。

`F65-R3-001`はこのlive fixture不在を理由にheldへ落とさない。runtime sourceだけでcontract gapを確認できる。

## remaining risks

- model catalogやCodex role/spawn contractが将来変更された場合はcentral mappingとapplication contract更新が必要。
- current validatorはSkill dependency/link構造を検証するが、mode別semantic contradictionやruntime application observabilityまでは検証しない。

## verdict

`fail`

Required findings:

- `F65-R3-001 / HIGH`
- `F65-R3-002 / HIGH`
- `F65-R3-003 / MEDIUM`

R2 findingsはresolvedだが、上記3件が未解決のためacceptance不可。

## next action

- 3 findingを修正する。
- R3 fix後はsame normal review chatでfinding-by-finding fix verificationを行う。
- 修正HEADと一致するworkflow runだけをCI evidenceとして使用する。
- mergeは利用者が行う。
# Tasks Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-07-29

## In Progress

- T-002: Codex／ChatGPT Skillを親非依存core Skillとruntime wrapperへ共通化し、ChatGPT依存Skillを単一ZIPへ収録する
  - Status: independent final review r2のrequired finding 3件へreview follow-up中
  - Phase: Phase 7
  - Estimate: L
  - Depends on: なし
  - Supersedes:
    - `shared/workflow/`contractを複数Skillから参照する旧方針
    - Release時にshared dependencyを各Skillへ複製する旧方針
    - 3 ChatGPT Skillとshared handoff fileだけを配布する旧構成
  - Exit Criteria:
    - runtime非依存のcontext、implementation、review、report意味論が独立core Skillとして定義されている
    - Codex wrapperがcore SkillをSkill名で呼び出し、runtime固有責務だけを持つ
    - ChatGPT wrapperがcore SkillをSkill名で呼び出し、runtime固有責務だけを持つ
    - 各Skillが自directory内で完結し、Skill外shared runtime fileへ依存しない
    - `chat-handoff-manager`がtyped projectionとversioned raw source payloadの両方を保持する
    - handoffがdevelopment policy、planned validation、required failure diagnostics、blocked state、implementation failure diagnosticsを保持する
    - handoffがreviewer identity／continuity／independence、reserved report path、attestation allowlist／validation条件を保持する
    - handoffがfull finding、reviewed HEAD、coverage、held、unexplored、requirements、test、artifact、commit、report／comment参照をlosslessにtransportする
    - schema version 1／2のoriginal packetとmapping不能fieldをnormalizationで捨てない
    - 4 ChatGPT wrapperと4 core Skillが独立root directoryとして単一ZIPへ含まれる
    - repository-wide validatorがfront matter、Skill dependency、active Markdown link、symlink、削除済みshared runtime path、hierarchy design同期を検証する
    - PRとmain pushのworkflow triggerが`shared/**`だけの変更でもrepository validatorを実行する
    - PR buildがread-onlyかつ実PR HEAD SHAをcheckoutし、main反映後のrelease jobだけがwrite権限を持つ
    - finding identityとsource severityを維持し、reclassificationにはsource／new severity、理由、承認主体を記録する
    - independent final review前にSkill decision、feedback ledger、normal handoff、report、trackingを含む全非final repository変更をcommit／pushする
    - pre-freeze処理でrepositoryが変わった場合はnormal review／fix verificationへ戻る
    - passing final reportは予約済みpathだけを変更する1回のreport-attestation commitで保存できる
    - attestation後にrepository-writing Skillまたは追加Git commitを実行しない
    - current implementation HEAD固有のrepository validation、bundle workflow、artifact確認が成功する
    - normal reviewerがsource findingと`PR54-IFR2-001`から`PR54-IFR2-003`をfix verificationしてpassする
    - 別fresh reviewerがcurrent implementation HEADを独立最終reviewしてpassする
    - mergeを行わない
  - Output:
    - `skills/work-context-manager/SKILL.md`
    - `skills/implementation-worker/SKILL.md`
    - `skills/review-worker/SKILL.md`
    - `skills/report-writer/SKILL.md`
    - `skills/chat-implementation-worker/SKILL.md`
    - `skills/chat-review-worker/SKILL.md`
    - `skills/chat-report-writer/SKILL.md`
    - `skills/chat-handoff-manager/SKILL.md`
    - `skills/implementation-executor/SKILL.md`
    - `skills/review-enforcer/SKILL.md`
    - `skills/report-output-manager/SKILL.md`
    - `skills/development-orchestrator/SKILL.md`
    - `skills/tdd-executor/SKILL.md`
    - `skills/skill-authoring-wrapper/SKILL.md`
    - `scripts/build_chatgpt_worker_skills.py`
    - `scripts/verify_skill_repository.py`
    - `.github/workflows/release-chatgpt-worker-skills.yml`
    - `design/chat-worker-skill-design.md`
    - `design/chatgpt-project-instruction-example.md`
    - `design/skill-hierarchy-design.md`
    - `skills/design/skill-hierarchy-design.md`
    - `reports/issue-53-independent-final-review-20260729083728.md`
    - `reports/issue-53-core-skill-wrapper-review-followup-20260729174338.md`
    - `reports/issue-53-fix-verification-20260729182457.md`
    - `reports/issue-53-fix-verification-followup-20260729182800.md`
    - `reports/issue-53-fix-verification-r2-20260729185000.md`
    - `reports/issue-53-independent-final-review-r2-20260729185400.md`
    - `reports/issue-53-finding-severity-erratum-20260729193100.md`
  - Review History:
    - initial independent final review: source finding 5件、verdict `fail`
    - first fix verification: `PR54-IFR-001`／`005` resolved、`002`／`003`／`004` partial、verdict `fail`
    - r2 fix verification: source finding 5件 resolved、verdict `pass_with_held`、report commit `162e19ff44410d3fdfd8230615af8370cb8e2add`
    - independent final review r2: `PR54-IFR2-001` high、`PR54-IFR2-002` medium、`PR54-IFR2-003` medium、verdict `fail`、report commit `9922865b2bd49cb7a76d462258e075c6959ee05e`
  - Finding Fidelity:
    - `PR54-IFR-004`のauthoritative source severityは`high`
    - first／r2 fix-verification reportの`medium`表記はreclassificationではなくtranscription error
    - correctionは`reports/issue-53-finding-severity-erratum-20260729193100.md`を正とし、historical reportは改変しない
  - Pre-freeze State:
    - state: invalidated by independent final review r2 required findings; normal lifecycleへ復帰
    - Skill-gap decision: `update existing skill`を選択し、`review-worker`と`report-writer`へseverity continuity guardを反映。新規Skillは不要
    - feedback classification: task-specific implementation／report fidelity defect。新しい反復ユーザー指示ではないためactive feedback ledger追記は不要
    - normal handoff: Issue #53、PR #54、本tracking、phase tracking、review report群から一意に復元可能。standalone handoff fileは不要
    - freeze: 未実施。`PR54-IFR2-*`のfix verification passとcurrent-HEAD CI確認後に再判定する
  - Current Review Follow-up:
    - `PR54-IFR2-001`: r2結果、current stage、pre-freeze stateをtask／phase／Issue／PRへ同期する
    - `PR54-IFR2-002`: source severity `high`をerratumで維持し、Skillへexplicit reclassification metadata規則を追加する
    - `PR54-IFR2-003`: workflowのPR／main path filterへ`shared/**`を追加する
  - Verification:
    - TDDは利用者指示とCodexSkill repository policyにより`not applicable`
    - Reviewed implementation HEAD `162e19ff44410d3fdfd8230615af8370cb8e2add`のworkflow run `30441434956`と8 Skill artifact `8719602133`はsuccess
    - current review-follow-up HEADのrepository validation、8 Skill ZIP build、artifactは変更完了後に確認する
    - normal fix verificationは未実施
    - fresh independent final reviewは未実施

## Backlog

なし

## Done

- T-001: `spawn_agent` model override 呼び出し契約を Skill 化する
  - Status: 完了
  - Phase: Phase 2
  - Estimate: S
  - Depends on: なし
  - Exit Criteria:
    - `model` と `reasoning_effort` を prompt ではなく `spawn_agent` の実引数で渡す契約が明記されている
    - override 時は `fork_turns: "none"` または部分 fork を使い、full-history forkを避ける規則が明記されている
    - hidden schemaでもruntimeが受理する現在のmulti-agent v2挙動と、失敗時の `codex exec` fallbackが明記されている
    - reviewerは原則parentと同じmodelを使用し、review reasoningの既定をhighとする
    - implementation modelはdevelopment-orchestratorが作業開始時にユーザーへ確認する
    - orchestration/delegation/review Skillと2つのhierarchy designが同期している
    - Markdown lintを実行し、配線が無い場合は`unsupported`として理由と残リスクを記録する
    - Skill validationと独立reviewが成功する
    - commit、push、PR作成が完了する
  - Output:
    - `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`
    - `skills/sub-agent-task-manager/SKILL.md`
    - `skills/codex-delegation-executor/SKILL.md`
    - `skills/development-orchestrator/SKILL.md`
    - `skills/review-enforcer/SKILL.md`
    - `skills/design/skill-hierarchy-design.md`
    - `design/skill-hierarchy-design.md`
    - `reports/topic-spawn-agent-model-overrides-implementation-20260711194140.md`
    - `reports/topic-spawn-agent-model-overrides-verification-20260711194628.md`
    - `reports/topic-spawn-agent-model-overrides-review-20260711194140.md`
  - Verification:
    - built-in `skill-creator` の `quick_validate.py` が4 Skillで成功
    - 2つのhierarchy designがbyte-identical
    - `git diff --check` 成功
    - Markdown lintはrepo配線不在のため`unsupported`として記録
    - parentと同じ`gpt-5.6-sol / high` reviewerの再レビューで指摘なし

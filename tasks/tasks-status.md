# Tasks Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-07-29

## In Progress

- T-002: Codex／ChatGPT Skillを親非依存core Skillとruntime wrapperへ共通化し、ChatGPT依存Skillを単一ZIPへ収録する
  - Status: 独立最終レビュー指摘5件へのreview follow-up完了、current-HEAD検証とnormal fix verification待ち
  - Phase: Phase 6
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
    - `chat-handoff-manager`がfull finding、reviewed HEAD、coverage、held、unexplored、requirements、validation、test、artifact、commit、report／comment参照をlosslessにtransportする
    - schema version 1／2のsourceに存在する情報をnormalizationで捨てない
    - 4 ChatGPT wrapperと4 core Skillが独立root directoryとして単一ZIPへ含まれる
    - repository-wide validatorがfront matter、Skill dependency、active Markdown link、symlink、削除済みshared runtime path、hierarchy design同期を検証する
    - PR buildがread-onlyかつ実PR HEAD SHAをcheckoutし、main反映後のrelease jobだけがwrite権限を持つ
    - independent final review前に全非final repository変更をcommit／pushする
    - passing final reportは予約済みpathだけを変更する1回のreport-attestation commitで保存できる
    - current implementation HEAD固有のrepository validation、bundle workflow、artifact確認が成功する
    - normal reviewerがfinding `PR54-IFR-001`から`PR54-IFR-005`をfix verificationしてpassする
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
  - Review Follow-up:
    - `PR54-IFR-001`: deleted `shared/workflow/`参照をcore Skill呼び出しへ置換し、repository-wide validatorを追加
    - `PR54-IFR-002`: `chat-handoff-manager`をlossless schema version 3へ拡張
    - `PR54-IFR-003`: reviewed implementation HEADと1回のreport-attestation commitで有限に終端する規則をcore／wrapper／designへ反映
    - `PR54-IFR-004`: Issue #53をsuperseding decisionで更新し、本trackingとcurrent reportをcore／wrapper構成へ更新
    - `PR54-IFR-005`: obsolete shared-copy validatorを削除し、current architecture向けvalidatorへ置換してCIへ接続
  - Verification:
    - TDDは利用者指示とCodexSkill repository policyにより`not applicable`
    - 独立最終review reportはReviewed HEAD `7fe8660d0fb4133bd732dd8456ff4390cf7b91e7`へ5 findingを記録し、verdict `fail`
    - finding対応後のcurrent-HEAD repository validation、bundle workflow、artifact確認は実施中
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

# Tasks Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-07-26

## In Progress

- T-002: Codex／ChatGPT Skillを共通契約化し、ChatGPT runtime依存物を単一ZIPへ自動収集する
  - Status: 実装・通常検証完了、独立最終レビュー待ち
  - Phase: Phase 6
  - Estimate: L
  - Depends on: なし
  - Exit Criteria:
    - runtime非依存の作業・実装・レビュー・レポート契約が`shared/workflow/`で一元管理されている
    - Codex側とChatGPT側が共通契約を参照するruntime adapterになっている
    - ChatGPT Skill内に共通契約の手動copyが残っていない
    - 全`skills/chat-*/SKILL.md`と各Skill内fileが自動的に単一ZIPへ含まれる
    - 参照されるshared dependencyと全`shared/chat-worker/` runtime fileがZIPへ含まれ、漏れがあればbuildが失敗する
    - PR buildがread-onlyかつPRの実HEAD SHAをcheckoutし、main反映後のrelease jobだけがwrite権限を持つ
    - CodexSkill repository自身へTDDを適用しない方針がroot instructionと実行入口に反映されている
    - hierarchy design 2件とChatGPT worker designが実装と同期している
    - 最終current HEAD固有のbundle workflowとartifact検証が成功する
    - 独立したfresh reviewerによる最終レビューが成功する
    - commit、push、Draft PR更新が完了し、mergeを行わない
  - Output:
    - `shared/workflow/common-work-contract.md`
    - `shared/workflow/implementation-contract.md`
    - `shared/workflow/review-contract.md`
    - `shared/workflow/report-contract.md`
    - `shared/chat-worker/handoff-contract.md`
    - `shared/chat-worker/project-instruction-example.md`
    - `scripts/build_chatgpt_worker_skills.py`
    - `.github/workflows/release-chatgpt-worker-skills.yml`
    - `skills/chat-implementation-worker/SKILL.md`
    - `skills/chat-review-worker/SKILL.md`
    - `skills/chat-report-writer/SKILL.md`
    - `skills/implementation-executor/SKILL.md`
    - `skills/review-enforcer/SKILL.md`
    - `skills/report-output-manager/SKILL.md`
    - `skills/development-orchestrator/SKILL.md`
    - `skills/tdd-executor/SKILL.md`
    - `skills/skill-authoring-wrapper/SKILL.md`
    - `design/chat-worker-skill-design.md`
    - `design/skill-hierarchy-design.md`
    - `skills/design/skill-hierarchy-design.md`
    - `reports/issue-53-shared-workflow-contracts-20260726154744.md`
  - Verification:
    - TDDは利用者指示とCodexSkill repository policyにより`not applicable`
    - PR HEAD `cbe0004d133ec71570c76bdcb47122fab963d86a`のworkflow run `30191605925`が成功
    - artifact `chatgpt-worker-skills-cbe0004d133ec71570c76bdcb47122fab963d86a`を展開し、3 Skill、必要なshared contract、Project Instruction例、handoff contract、ZIP integrity、repository相対link解消を確認
    - tracking・report・設計整合commit後の最終current HEAD workflowは再確認する
    - 独立最終レビューは未実施

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

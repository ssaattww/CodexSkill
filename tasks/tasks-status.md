# Tasks Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-07-11

## In Progress

なし

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

# Phases Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-07-26

## Phase 1: 契約・設計

- Status: Done
- Notes:
  - Issue #32031 と実環境で、hidden `model` / `reasoning_effort` override、`fork_turns` 制約、`codex exec` fallbackを確認した
  - dispatch詳細は `sub-agent-task-manager` が所有し、caller Skillはその契約へ従う方針とした
  - reviewer modelは原則parentと同じmodel、implementation modelは作業開始時にユーザー確認する契約とした

## Phase 2: Skill実装

- Status: Done
- Notes:
  - orchestration/delegation/review Skill、reference、2つのhierarchy designを同期した

## Phase 3: 検証・提出

- Status: Done
- Notes:
  - Markdown lintを`unsupported`分類し、4 Skill validation、独立reviewを完了した
  - commit、push、PR作成を実行する

## Phase 4: 共通workflow契約と設計

- Status: Done
- Notes:
  - 実装、レビュー、レポート、共通作業規則を`shared/workflow/`のruntime非依存contractへ集約した
  - CodexとChatGPTのruntime責務、normal review cycle、independent final review、ChatGPT handoff、Release構造を設計へ反映した
  - CodexSkill repository自身へTDDを適用しない方針をroot `AGENTS.md`と共通contractへ反映した

## Phase 5: Runtime adapterとRelease実装

- Status: Done
- Notes:
  - Codex側とChatGPT側を共通contract参照型adapterへ変更した
  - ChatGPT Skill内のhandoff contract手動copy 3件を削除した
  - 全`skills/chat-*` Skill、Skill内file、参照shared dependency、全`shared/chat-worker/` runtime fileを単一ZIPへ収集するbuilderを追加した
  - PR buildをread-only、main反映後のrelease jobだけをwrite可能とした
  - PR eventではsynthetic merge refではなく実PR HEAD SHAをcheckoutしてartifact名にも使用するよう修正した

## Phase 6: 検証・PR提出

- Status: In Progress
- Notes:
  - PR #54をDraftで作成した
  - PR HEAD `cbe0004d133ec71570c76bdcb47122fab963d86a`のworkflow run `30191605925`とartifact内部検証が成功した
  - tracking、report、最終設計整合commit後のcurrent HEAD専用workflowを再確認する
  - 独立したfresh reviewerによる最終レビューは未実施であり、PRはDraftのまま維持する
  - mergeは利用者が行う

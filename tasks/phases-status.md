# Phases Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-07-29

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
  - commit、push、PR作成を実行した

## Phase 4: 親非依存core Skillとruntime wrapper設計

- Status: Done
- Notes:
  - 当初の`shared/workflow/`contract方式をsupersededとした
  - `work-context-manager`、`implementation-worker`、`review-worker`、`report-writer`を親runtime非依存core Skillとして定義した
  - CodexとChatGPTのruntime責務をwrapperへ限定した
  - normal review continuityとfresh independent final reviewを共通lifecycleとして設計した
  - ChatGPT handoffを独立`chat-handoff-manager` Skillへ移した
  - CodexSkill repository自身へTDDを適用しない方針をroot `AGENTS.md`と各入口Skillへ反映した

## Phase 5: Runtime wrapper、handoff、Release実装

- Status: Done
- Notes:
  - Codex wrapperとChatGPT wrapperをcore Skill呼び出し型へ変更した
  - Skill外shared runtime fileと手動copyを削除した
  - 4 ChatGPT wrapperと4 core Skillを独立root directoryとして単一ZIPへ収録するbuilderを実装した
  - PR buildをread-only、main反映後のrelease jobだけをwrite可能とした
  - PR eventではsynthetic merge refではなく実PR HEAD SHAをcheckoutしてartifact名にも使用するよう修正した

## Phase 6: 独立最終レビュー指摘への対応

- Status: In Progress
- Notes:
  - independent final reviewはReviewed HEAD `7fe8660d0fb4133bd732dd8456ff4390cf7b91e7`に対してverdict `fail`、required finding 5件を記録した
  - `PR54-IFR-001`: deleted shared contract参照をcore Skill呼び出しへ置換した
  - `PR54-IFR-002`: handoff schema version 3へfull evidence fieldを追加した
  - `PR54-IFR-003`: reviewed implementation HEADと1回のreport-attestation commitで有限に終端する規則を追加した
  - `PR54-IFR-004`: Issue #53、task／phase tracking、current architecture reportをcore／wrapper構成へ同期する
  - `PR54-IFR-005`: obsolete validatorをrepository-wide Skill validatorへ置換し、workflowへ接続した
  - hierarchy design 2件とChatGPT worker designへreview follow-upを反映した
  - CodexSkill repositoryにはTDDを適用していない
  - current-HEAD repository validation、bundle workflow、artifact確認は実施中
  - normal reviewerによるfix verificationは未実施
  - fresh reviewerによる独立最終reviewは未実施
  - PR #54はDraftのまま維持する
  - mergeは利用者が行う

## Phase 7: Fix verificationと独立最終レビュー

- Status: Pending
- Notes:
  - Phase 6の全非final変更とcurrent implementation／verification reportをcommit／pushする
  - current-HEAD repository validationとbundle artifactを確認する
  - normal reviewerが5 findingをidentity単位でfix verificationする
  - required findingがなければindependent-final-review report pathを予約し、implementation HEADをfreezeする
  - 別fresh reviewerがfrozen implementation HEADを独立最終reviewする
  - passing reportを保存する場合は予約済みpathだけを変更する1回のreport-attestation commitを作成する
  - PR body／commentへreviewed implementation HEAD、attestation HEAD、current-HEAD evidenceを記録する
  - attestation後にrepository commitを追加しない

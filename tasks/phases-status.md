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

## Phase 6: 独立最終レビュー指摘への初回対応

- Status: Done
- Notes:
  - independent final reviewはReviewed HEAD `7fe8660d0fb4133bd732dd8456ff4390cf7b91e7`に対してverdict `fail`、required finding 5件を記録した
  - `PR54-IFR-001`: deleted shared contract参照をcore Skill呼び出しへ置換した
  - `PR54-IFR-002`: handoff schema version 3へfull evidence fieldを追加した
  - `PR54-IFR-003`: reviewed implementation HEADと1回のreport-attestation commitで有限に終端する規則を追加した
  - `PR54-IFR-004`: Issue #53、task／phase tracking、historical report、current reportをcore／wrapper構成へ同期した
  - `PR54-IFR-005`: obsolete validatorをrepository-wide Skill validatorへ置換し、workflowへ接続した
  - hierarchy design 2件とChatGPT worker designへreview follow-upを反映した
  - review follow-up HEAD `39e2902beb47e85d412d1b1bc8044d8653b7cd34`のworkflow run `30437095001`が成功した
  - repository-wide Skill／active-link validationと8 Skill ZIP buildが成功した
  - first fix verificationは`PR54-IFR-001`／`005` resolved、`002`／`003`／`004` partial、verdict `fail`となった
  - CodexSkill repositoryにはTDDを適用していない
  - PR #54はDraftのまま維持する
  - mergeは利用者が行う

## Phase 7: 残存finding対応、再fix verification、独立最終レビュー

- Status: In Progress
- Notes:
  - `PR54-IFR-002`: typed schemaへdevelopment policy、validation plan、failure diagnostics、blocked state、reviewer identity／independence、attestation gateを追加した
  - `PR54-IFR-002`: complete core Skill outputとlegacy packetをversioned `source_payloads`へ保持し、mapping不能fieldを失わない規則へ変更した
  - `PR54-IFR-003`: end-of-Issue Skill decision、current-scope Skill update、feedback classification／ledger、normal handoffをpre-freeze gateへ移した
  - `PR54-IFR-003`: pre-freeze処理でrepositoryが変わった場合はvalidationとnormal review／fix verificationへ戻す規則を追加した
  - `PR54-IFR-003`: attestation後はPR／Issue等のnon-Git operationとbranch外transportだけを許可し、repository-writing Skillを禁止した
  - `PR54-IFR-004`: T-002をPhase 7へ更新し、本PhaseをIn Progressへ同期した
  - `chat-handoff-manager`、`development-orchestrator`、`review-enforcer`、hierarchy design 2件、ChatGPT worker designを同期した
  - second review-follow-up後のrepository-wide validationと8 Skill ZIP buildを実行する
  - 同じfinding identityによる再fix verificationを実施する
  - required findingがなければ、全pre-freeze変更が確定していることを確認する
  - independent-final-review report pathを予約し、implementation HEADをfreezeする
  - 別fresh reviewerがfrozen implementation HEADを独立最終reviewする
  - passing reportを保存する場合は予約済みpathだけを変更する1回のreport-attestation commitを作成する
  - report-attestation diffをallowlist検証する
  - PR body／commentへreviewed implementation HEAD、attestation HEAD、current-HEAD evidenceを記録する
  - attestation後にrepository commitまたはrepository-writing Skillを実行しない

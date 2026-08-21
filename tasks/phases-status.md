# Phases Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-08-21

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
  - first fix verificationは`PR54-IFR-001`／`005` resolved、`002`／`003`／`004` partial、verdict `fail`となった
  - CodexSkill repositoryにはTDDを適用していない
  - mergeは利用者が行う

## Phase 7: Review収束と独立最終レビュー

- Status: In Progress
- Notes:
  - first fix-verification残存3件へtyped／raw handoff、pre-freeze gate、task／phase同期を追加した
  - r2 fix verificationはReviewed implementation HEAD `5742ff0efd4885b5fe0b504ceb33ff7c927fcd10`に対しsource finding 5件をresolvedとし、verdict `pass_with_held`を記録した
  - independent final review r2は`PR54-IFR2-001` high、`PR54-IFR2-002` medium、`PR54-IFR2-003` mediumを記録し、verdict `fail`となった
  - `PR54-IFR2-002`はseverity erratumとcontinuity guardでresolvedを維持している
  - `PR54-IFR2-003`はPR／main path filterへ`shared/**`を追加しresolvedを維持している
  - `PR54-IFR2-001`のnormal handoff packetを`reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md`へ保存した
  - fix verification r2はpacketの`source_payloads`がcomplete outputではなく要約へ縮退していることと、task／phaseのfuture stateを指摘し、verdict `fail`となった
  - `reports/issue-53-complete-source-payload-followup-20260730070000.md`へcomplete report bodyを保存した
  - packetの4 `source_payloads`を各core SkillのOutput contractと同じfield名・構造へ更新した
  - `work-context-manager.authoritative_requirements`をstructured objectsとして保持した
  - `implementation-worker.changed_files`へ各pathのpurposeを保持した
  - `review-worker`のreviewer identity、coverage、full finding、severity record、held、unexplored、validation、verdictを保持した
  - `report-writer.complete_body`へ詳細report全文を埋め込み、`severity_records`を保持した
  - packet／report commitは`ab7d58dccc96b6e22a36723b885e8f44666d7007`
  - commit `ab7d58dccc96b6e22a36723b885e8f44666d7007`のworkflow run `30495649913`はsuccess
  - repository validatorと8 Skill ZIP buildはsuccess
  - artifact ID `8741451881`、digest `sha256:da3589d11beae31eab5265b2b982e491c8b8560e6f274c9a0bdd1b398244ff9c`
  - task／phaseをpacket保存済み、current-HEAD検証済み、normal fix verification待ちの現在形へ同期した
  - Project Instruction例は対象固有リポジトリ名を対象URL1か所だけで指定し、後続instructionを一般表現へ統一済み
  - Skill-gap decisionは`update existing skill`。既存Skill更新済みで新規Skillは作成しない
  - feedback classificationはtask-specific defectであり、active feedback ledgerへ追加しない
  - fix verification r3はReviewed implementation HEAD `6976a94391dd3d7afa3c8284c19986edd6f18726`に対し`PR54-IFR2-001`をresolved、`002`／`003`をresolved維持とし、verdict `pass_with_held`を記録した
  - fix verification r3のremaining required findingsは0件で、normal review cycleは収束した
  - fix-verification r3 report commit `6fb76ce5f4cf3e358c5d70c5139a024d9495186f`のworkflow run `30496514600`はsuccess
  - artifact ID `8741787240`、digest `sha256:03286426413470e9a9ad64ed13e003cfb562a8e87b978f3ab4d8a7e4c2e09eb9`
  - `reports/issue-53-normal-review-pass-prefreeze-followup-20260730091000.md`へnormal review passとpre-freeze準備を記録した
  - 本tracking更新を含むcurrent HEADのrepository validator、8 Skill ZIP build、matching artifactを確認する
  - matching validation成功後にindependent-final-review report pathを予約し、current HEADをfrozen implementation HEADとする
  - 別fresh reviewerがfrozen implementation HEADを独立最終reviewする
  - passing reportを保存する場合だけ予約済みpathを変更する1回のreport-attestation commitを作成する
  - report-attestation diffをallowlist検証する
  - attestation後にrepository commitまたはrepository-writing Skillを実行しない

## Phase 8: Runtime別verification経路の分離

- Status: In Progress
- Notes:
  - Issue #62を対象とする
  - local execution可能時はlocal test、review対象commit、reviewの順で進め、review中にCI完了を待たない
  - remote-CI-only時はmatching current-HEAD CIをverification routeとして使用する
  - commit、push、CI waitを独立した状態遷移として設計する
  - 設計更新、関連Skill contract更新、local validation、通常review、独立review、PR作成を行う
  - CodexSkill repository policyによりTDDは適用しない
  - 設計3文書と関連14 Skillのcontract更新を完了した
  - `git diff --check`と2つのSkill hierarchy設計一致は成功した
  - repository validator／bundle buildはlocal Python runtime不在、Markdown lintはrepo-local配線不在のため`unsupported`として記録した
  - 次はreview対象commitを作成し、通常reviewを一度の全範囲検査として実施する

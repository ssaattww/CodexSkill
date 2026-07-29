# Issue #53 / PR #54 Normal Handoff Packet

```yaml
schema_version: 3
producer:
  skill: chat-implementation-worker
  mode: review_follow_up
  generated_at: 2026-07-30T06:03:00+09:00

repository: ssaattww/CodexSkill
issue_or_pr: "Issue #53 / PR #54"
task_id: T-002
branch: agent/issue-53-shared-workflow-contracts
base_ref: main
target:
  current_head: 79caa8a218c8d3fe032f6888092c05a5e668d898
  reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
  commit_range: 17339b357226125b1b6bd6850645bfec8c92fcab..79caa8a218c8d3fe032f6888092c05a5e668d898

authoritative_requirements:
  - source: user_instruction
    reference: current conversation
    summary: 最新のレビュー結果へ対応し、GitHub connector経由でrepository、tracking、report、PRを更新する
  - source: user_instruction
    reference: 2026-07-30 Project Instruction追加指示
    summary: design/chatgpt-project-instruction-example.mdでは対象固有リポジトリ名を最初の1か所だけに置き、複数箇所の設定変更を不要にする
  - source: repository_instruction
    reference: AGENTS.md
    summary: CodexSkill repository自身にはTDDを適用せず、通常validationを使用し、mergeしない
  - source: issue
    reference: Issue #53
    summary: 親非依存core Skillとruntime wrapper、self-contained Skill、8 Skill ZIP、finite review lifecycleをcurrent architectureとする
  - source: report
    reference: reports/issue-53-independent-final-review-r2-fix-verification-20260729212800.md
    summary: PR54-IFR2-001だけがpartialであり、complete schema version 3 normal handoff packetをreports/handoffsへ保存する必要がある
  - source: design
    reference: skills/chat-handoff-manager/SKILL.md
    summary: typed projectionとversioned raw source_payloadsを持つlossless schema version 3 packetを生成する
  - source: design
    reference: skills/chat-implementation-worker/SKILL.md
    summary: chat-handoff-managerを必須Skillとして呼び、repository write可能時はhandoff packetを永続化する

development_policy:
  method: documentation_and_workflow_maintenance
  testing_order: validation_only_non_tdd
  governing_source: AGENTS.md and explicit user instruction
validation_plan:
  commands:
    - python3 scripts/verify_skill_repository.py
    - python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip
    - python3 -m zipfile -l chatgpt-worker-skills.zip
    - GitHub Actions workflow Validate and release ChatGPT worker skills
  required_failure_diagnostics:
    - GitHub Actions job and step status
    - workflow job logs when a step fails
    - generated ZIP listing or builder error output
    - repository validator error output
    - workflow artifact metadata and digest
blocked:
  - item: independent_final_review_target_freeze
    reason: PR54-IFR2-001はpacket保存後のnormal fix verificationが未実施
    required_input_or_decision: normal reviewerのpassまたはpass_with_held verdict

authorized_actions:
  - read_repository
  - edit_documentation
  - edit_workflows
  - write_handoff
  - write_report
  - commit
  - push
  - update_issue
  - update_pr
  - comment_pr
write_boundary:
  allowed:
    - path_or_operation: design/chatgpt-project-instruction-example.md
      reason: 利用者が対象固有設定を1か所へ集約するよう指示した
    - path_or_operation: tasks/tasks-status.md
      reason: review stateとhandoff pathを同期する
    - path_or_operation: tasks/phases-status.md
      reason: Phase 7のcurrent lifecycleを同期する
    - path_or_operation: reports/issue-53-normal-handoff-followup-20260730060300.md
      reason: 今回のreview-follow-up evidenceを保存する
    - path_or_operation: reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
      reason: schema version 3 normal handoffを永続化する
    - path_or_operation: Issue #53 metadata
      reason: packet path、current HEAD、CI evidenceを同期する
    - path_or_operation: PR #54 body and concise comment
      reason: current review stateとpacket evidenceを同期する
  forbidden:
    - path_or_operation: merge PR #54
      reason: mergeは利用者が所有する
    - path_or_operation: main branch or GitHub Release update
      reason: PR scope外でありmain push限定release jobの責務
    - path_or_operation: unrelated Skill or product changes
      reason: accepted review-follow-up scope外

scope:
  - PR54-IFR2-001の残存required actionとしてcomplete schema version 3 normal handoff packetを生成・保存する
  - repository discoveryをhandoff packetの代替とする記録を廃止し、Issue、PR、task、phaseからpacket pathを参照する
  - Project Instruction例の対象固有リポジトリ名を対象URL1か所へ集約する
  - packet保存後のcurrent HEADでrepository validation、8 Skill ZIP build、artifactを確認する
non_goals:
  - independent final reviewの実施またはpass判定
  - report-attestation commitの作成
  - main push release jobの実行
  - ChatGPT UIでの8 Skill実upload
  - PRのmerge

files:
  changed:
    - path: design/chatgpt-project-instruction-example.md
      purpose: 対象固有リポジトリ名を対象URL1か所だけに残し、後続instructionを一般表現へ変更
    - path: tasks/tasks-status.md
      purpose: 最新fix-verification結果、packet path、current lifecycleを同期
    - path: tasks/phases-status.md
      purpose: Phase 7へnormal handoff packet対応を記録
    - path: reports/issue-53-normal-handoff-followup-20260730060300.md
      purpose: review-follow-upの詳細evidenceを保存
    - path: reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
      purpose: 本schema version 3 packetをrepositoryへ永続化
  inspected:
    - path: skills/chat-handoff-manager/SKILL.md
      purpose: schema version 3 typed projection、source_payloads、transport contractを確認
    - path: skills/chat-implementation-worker/SKILL.md
      purpose: handoff manager必須呼出しとrepository persistence責務を確認
    - path: design/chat-worker-skill-design.md
      purpose: repository-backed normal handoffとProject Instruction参照方針を確認
    - path: reports/issue-53-independent-final-review-r2-fix-verification-20260729212800.md
      purpose: residual finding、impact、required actionを確認
    - path: .github/workflows/release-chatgpt-worker-skills.yml
      purpose: current-HEAD repository validatorと8 Skill ZIP build経路を確認
    - path: scripts/verify_skill_repository.py
      purpose: repository architecture validation範囲を確認
    - path: Issue #53
      purpose: current authority、completion criteria、pre-freeze stateを確認
    - path: PR #54
      purpose: branch、HEAD、review history、current stageを確認
  intentionally_untouched:
    - path_or_area: design/chat-worker-skill-design.mdのProject Instruction埋込み例
      reason: 今回の利用者指示はcanonical example file内の設定値集約を直接対象とし、既存設計節の全面編集はscope外
    - path_or_area: feedback-points/feedback-points.md
      reason: task-specific defectであり新しい反復ユーザー指示としてledger追加しない
    - path_or_area: main branch and release assets
      reason: merge後のmain workflowが所有するheld item

commands:
  - command: python3 scripts/verify_skill_repository.py
    purpose: Skill architecture、dependency、active link、forbidden shared runtime path、design同期を検証
    exit_code: 0
    result: passed
    head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
    evidence: GitHub Actions run 30491431364 build step 3
  - command: python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip
    purpose: 4 ChatGPT wrapperと4 core Skillの配布ZIPを生成・検証
    exit_code: 0
    result: passed
    head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
    evidence: GitHub Actions run 30491431364 build step 4
  - command: python3 -m zipfile -l chatgpt-worker-skills.zip
    purpose: ZIP entry listingを確認
    exit_code: 0
    result: passed
    head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
    evidence: GitHub Actions run 30491431364 build step 4

tests:
  - name: TDD applicability
    phase: not_applicable
    result: not_run
    head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
    evidence: CodexSkill repository policyによりTDDはnot applicable
  - name: repository Skill and active-link validation
    phase: verification
    result: passed
    head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
    evidence: workflow run 30491431364
  - name: 8 Skill ZIP build
    phase: verification
    result: passed
    head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
    evidence: workflow run 30491431364 and artifact 8739825968

ci:
  required: true
  workflow: Validate and release ChatGPT worker skills
  run_id: 30491431364
  head_sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
  conclusion: success
  artifacts:
    - id: 8739825968
      name: chatgpt-worker-skills-79caa8a218c8d3fe032f6888092c05a5e668d898
      purpose: 4 ChatGPT wrapperと4 core Skillを含むvalidation bundle

implementation:
  outcome: completed
  final_head: 79caa8a218c8d3fe032f6888092c05a5e668d898
  commits:
    - sha: 47d9c7a23105e8c68463f79f3ee0cfc2de65112b
      purpose: Project Instructionの対象固有設定を対象URL1か所へ集約
    - sha: 9edd0a1cb3351e65f8963fc61133832c9b4a44c3
      purpose: task trackingへnormal handoff packet requirementを同期
    - sha: 5ff5afff5ecca161027af790ed82fc29edfb41e4
      purpose: Phase 7へnormal handoff対応を同期
    - sha: 79caa8a218c8d3fe032f6888092c05a5e668d898
      purpose: normal handoff review-follow-up reportを保存
  addressed_findings:
    - id: PR54-IFR2-001
      reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
      disposition: addressed
      evidence: complete schema version 3 packetをreports/handoffs/issue-53-pr54-normal-handoff-20260730060300.mdへ保存
    - id: PR54-IFR2-002
      reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
      disposition: addressed
      evidence: source severity highをerratumで維持しcontinuity guardを追加済み
    - id: PR54-IFR2-003
      reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
      disposition: addressed
      evidence: PRとmainのpath filterへshared/**を追加済み
  failure_diagnostics: []
  blocked_items:
    - item: independent_final_review
      reason: normal reviewerによるPR54-IFR2-001のfix verification未実施
      required_input_or_decision: passまたはpass_with_held verdict
  summary:
    - repository discoveryをpacketの代替とする扱いを廃止した
    - complete schema version 3 normal handoff packetをrepositoryへ保存した
    - Project Instruction例の対象固有リポジトリ名を対象URL1か所へ集約した

review:
  mode: fix_verification
  reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
  reviewer:
    identity: normal reviewer chat recorded by report commit 17339b357226125b1b6bd6850645bfec8c92fcab
    role: normal_reviewer
    continuity:
      previous_reviewer_identity: independent-final-review-r2 reviewer chat
      changed: false
      reason: null
    independence:
      implemented_change: false
      implemented_review_fix: false
      served_as_normal_reviewer: true
      inherited_conversation: true
      evidence:
        - reports/issue-53-independent-final-review-r2-fix-verification-20260729212800.md metadata
  verdict: fail
  required_coverage:
    - criterion: requirement and design conformance
      disposition: checked_finding
      evidence: source review found missing schema v3 normal handoff packet
    - criterion: correctness and edge cases
      disposition: checked_finding
      evidence: repository discovery did not guarantee typed/raw lossless transport
    - criterion: scope discipline and unrelated changes
      disposition: checked_no_finding
      evidence: review-follow-up remained limited to handoff, tracking, report, and Project Instruction setting consolidation
    - criterion: changed files and direct dependency impact
      disposition: checked_finding
      evidence: handoff and wrapper direct dependencies were inspected
    - criterion: API, data, configuration, workflow, and compatibility effects
      disposition: checked_finding
      evidence: required handoff transport API was not previously exercised
    - criterion: error handling and failure diagnostics
      disposition: checked_finding
      evidence: repository discovery did not preserve typed blocked and failure-diagnostic fields
    - criterion: security and secret handling
      disposition: checked_no_finding
      evidence: no secret or permission expansion identified
    - criterion: tests and validation adequacy
      disposition: checked_no_finding
      evidence: current target HEAD validator and ZIP build passed
    - criterion: current-HEAD CI evidence
      disposition: checked_no_finding
      evidence: run 30491431364 matches target HEAD 79caa8a218c8d3fe032f6888092c05a5e668d898
    - criterion: report, tracking, and documentation accuracy
      disposition: checked_finding
      evidence: prior repository-discovery completion claim conflicted with Skill contract
    - criterion: regression and maintainability risks
      disposition: checked_finding
      evidence: bypassing packet generation would establish an invalid fallback precedent
  validation_assessment:
    - item: repository Skill architecture and active links
      result: supported
      evidence: workflow run 30491431364 step 3 passed
    - item: 8 Skill ZIP build
      result: supported
      evidence: workflow run 30491431364 step 4 and artifact 8739825968
    - item: schema version 3 normal handoff persistence
      result: supported
      evidence: reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
    - item: final review readiness
      result: unsupported
      evidence: packet persistence requires normal fix verification before freeze
  reserved_report_paths: []
  report_attestation:
    allowed: false
    reviewed_implementation_head: null
    allowed_paths: []
    required_first_parent: null
    maximum_commits_after_reviewed_head: null
    forbidden_path_classes: []
    no_later_commits_required: not_applicable
    validation_status: not_applicable
    validation_evidence: []
  summary:
    - source normal review verdict remains fail until this packet is fix-verified
    - PR54-IFR2-002 and PR54-IFR2-003 remain resolved
    - PR54-IFR2-001 is implemented but not yet review-verified

report:
  report_type: implementation_report
  outcome: created
  persistence_mode: repository_file
  paths:
    - reports/issue-53-normal-handoff-followup-20260730060300.md
    - reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
  reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
  attestation_head: null
  pr_comments:
    - target: PR #54
      url_or_id: pending_after_packet_persistence
  summary:
    - normal handoff packet対応とProject Instruction単一設定化を記録した

findings:
  - id: PR54-IFR2-001
    severity: high
    origin: introduced_by_fix
    location: reports/issue-53-independent-final-review-r2-followup-20260729193100.md; tasks/tasks-status.md; tasks/phases-status.md; Issue #53; PR #54; skills/chat-handoff-manager/SKILL.md; skills/chat-implementation-worker/SKILL.md
    description: pre-freeze必須のnormal handoffをschema version 3 packetとして生成・保存せず、repository discoveryで代替していた
    impact: 次chatがtyped projection、raw source payload、permissions、blocked evidence、failure diagnosticsをpacket単独で復元できず、core／wrapper separationを迂回する
    evidence: source fix-verification reportはreports/handoffs配下にpacketが存在しないこととrepository_discovery代替を確認した
    required_action: complete schema version 3 normal handoff packetをreports/handoffsへ保存し、Issue、PR、task、phaseからpacket pathを参照し、new HEADでCI確認後に同じnormal reviewerがfix verificationする

held:
  - item: main push release job and GitHub Release update
    reason: PR eventではrelease jobが設計どおりskipped
    owner: merge後のmain workflow
    remaining_risk: rolling tag、release asset upload、clobber動作は未確認
    verdict_impact: non-blocking held item
  - item: ChatGPT UI upload and wrapper-to-core runtime resolution
    reason: repositoryとartifact検査だけではChatGPT runtimeを実行できない
    owner: release candidate実機検証
    remaining_risk: 8 Skill一括upload後のSkill resolutionは未確認
    verdict_impact: non-blocking held item

unexplored:
  - area: packet persistence commit後のcurrent-HEAD CI
    blocker: packet file commit後にworkflowが起動する必要がある
    remaining_risk: packet commitに一致するvalidation evidenceがまだない
    verdict_impact: normal fix verification前に確認必須
  - area: fresh independent final review
    blocker: normal fix verification未完了
    remaining_risk: final architectureに追加findingが存在する可能性
    verdict_impact: completionを阻害
  - area: report-attestation allowlist validation
    blocker: passing independent final reviewへ未到達
    remaining_risk: terminal persistence pathの実運用未確認
    verdict_impact: final stageで確認必須

unknown:
  - field_or_fact: packet persistence commit SHA
    reason: packet本文生成時点ではpacket fileを保存するcommitがまだ存在しないため、PR metadataへ保存後に記録する
  - field_or_fact: packet persistence commitに一致するworkflow run and artifact
    reason: packet保存後にGitHub Actionsが実行されるため、Issue／PR metadataへ後から記録する
not_applicable:
  - field_or_area: TDD Red/Green evidence
    reason: CodexSkill repository policyでTDDはnot applicable
  - field_or_area: report attestation
    reason: normal review cycleでありpassing independent final reviewではない
remaining_risks:
  - packet persistence commit後のcurrent-HEAD validationを確認する必要がある
  - normal reviewerがPR54-IFR2-001を同じidentityでfix verificationする必要がある
  - fresh independent final reviewは未実施
  - main release jobとChatGPT UI実機確認はheld

source_payloads:
  - source_skill: work-context-manager
    output_contract_version: "2026-07-29"
    content_type: application/yaml
    payload:
      repository: ssaattww/CodexSkill
      issue_or_pr: "Issue #53 / PR #54"
      task_id: T-002
      mode: implementation
      branch: agent/issue-53-shared-workflow-contracts
      base_ref: main
      current_head: 79caa8a218c8d3fe032f6888092c05a5e668d898
      reviewed_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
      scope:
        - schema version 3 normal handoff packet persistence
        - Project Instruction target-specific setting consolidation
        - tracking, report, Issue, PR synchronization
      non_goals:
        - merge
        - independent final review
        - main release
      authoritative_requirements:
        - user current instruction
        - AGENTS.md non-TDD policy
        - Issue #53 current architecture
        - source fix-verification report
        - chat-handoff-manager and chat-implementation-worker contracts
      write_boundary:
        allowed:
          - Project Instruction example
          - task and phase tracking
          - review-follow-up report
          - normal handoff packet
          - Issue and PR metadata
        forbidden:
          - merge
          - main and release update
          - unrelated Skill changes
      development_policy:
        method: documentation_and_workflow_maintenance
        testing_order: validation_only_non_tdd
      validation:
        commands:
          - python3 scripts/verify_skill_repository.py
          - python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip
          - GitHub Actions workflow
        required_failure_diagnostics:
          - workflow logs
          - validator output
          - builder output
          - artifact metadata
      ci:
        matching_run: "30491431364"
        conclusion: success
      unknown:
        - packet persistence commit SHA
        - post-persistence matching CI
      blocked:
        - independent final review until normal fix verification passes
      remaining_risks:
        - main release held
        - ChatGPT UI validation held
  - source_skill: implementation-worker
    output_contract_version: "2026-07-29"
    content_type: application/yaml
    payload:
      mode: review_follow_up
      accepted_scope:
        - address PR54-IFR2-001 by generating a complete schema version 3 handoff packet
        - centralize target-specific Project Instruction setting
      non_goals:
        - independent final review
        - merge
      requirements_and_design_references:
        - reports/issue-53-independent-final-review-r2-fix-verification-20260729212800.md
        - skills/chat-handoff-manager/SKILL.md
        - skills/chat-implementation-worker/SKILL.md
        - design/chatgpt-project-instruction-example.md
      changed_files:
        - design/chatgpt-project-instruction-example.md
        - tasks/tasks-status.md
        - tasks/phases-status.md
        - reports/issue-53-normal-handoff-followup-20260730060300.md
        - reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
      intentionally_untouched:
        - main branch
        - release assets
        - unrelated Skills
        - feedback ledger
      validation_commands:
        - python3 scripts/verify_skill_repository.py
        - python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip
        - GitHub Actions run 30491431364
      validation_results:
        - repository validator passed
        - 8 Skill ZIP build passed
        - artifact 8739825968 created
      failure_diagnostics: []
      commits:
        - 47d9c7a23105e8c68463f79f3ee0cfc2de65112b
        - 9edd0a1cb3351e65f8963fc61133832c9b4a44c3
        - 5ff5afff5ecca161027af790ed82fc29edfb41e4
        - 79caa8a218c8d3fe032f6888092c05a5e668d898
      final_head: 79caa8a218c8d3fe032f6888092c05a5e668d898
      matching_ci:
        run_id: 30491431364
        artifact_id: 8739825968
      blocked_items:
        - normal fix verification required
      unknowns:
        - packet persistence commit and matching CI
      remaining_risks:
        - fresh independent final review not performed
      next_required_action: persist packet, validate new HEAD, request normal fix verification
  - source_skill: review-worker
    output_contract_version: "2026-07-29"
    content_type: application/yaml
    payload:
      review_mode: fix_verification
      reviewed_implementation_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
      base: main
      commit_range: 9922865b2bd49cb7a76d462258e075c6959ee05e..ab20b8875dd71722ada7fe4794e05d4a85671bde
      reviewer_identity: normal reviewer chat recorded in report commit 17339b357226125b1b6bd6850645bfec8c92fcab
      independence_evidence:
        - reviewer did not implement review follow-up
        - reviewer maintained source finding identity
      required_coverage:
        requirement_and_design_conformance: checked_finding
        correctness_and_edge_cases: checked_finding
        scope_discipline: checked_no_finding
        changed_files_and_dependencies: checked_finding
        api_data_configuration_workflow_compatibility: checked_finding
        error_handling_and_failure_diagnostics: checked_finding
        security_and_secret_handling: checked_no_finding
        tests_and_validation: checked_no_finding
        current_head_ci: checked_no_finding
        report_tracking_documentation_accuracy: checked_finding
        regression_and_maintainability: checked_finding
      findings:
        - id: PR54-IFR2-001
          severity: high
          origin: introduced_by_fix
          location: follow-up report, task, phase, Issue, PR, handoff manager, implementation wrapper
          description: schema version 3 normal handoff packet was not generated and persisted
          impact: lossless transport and core-wrapper separation were bypassed
          evidence: no reports/handoffs packet existed and repository_discovery was declared sufficient
          required_action: persist complete packet, sync references, validate new HEAD, repeat fix verification
      held_items:
        - main release job
        - ChatGPT UI runtime validation
      unexplored_areas:
        - new HEAD after packet persistence
        - fresh independent final review
        - passing attestation validation
      validation_assessment:
        repository_validation: supported
        bundle_build: supported
        handoff_packet_persistence: unsupported_at_review_time
      verdict: fail
      remaining_risks:
        - packet persistence and validation required
      next_action: implementation review follow-up
      reserved_report_paths: []
      report_attestation_allowed: false
      attestation_conditions: not_applicable
  - source_skill: report-writer
    output_contract_version: "2026-07-29"
    content_type: application/yaml
    payload:
      report_type: implementation_report
      complete_body_path: reports/issue-53-normal-handoff-followup-20260730060300.md
      evidence_sources:
        - source fix-verification report
        - current Skill contracts
        - task and phase tracking
        - GitHub Actions run 30491431364
        - artifact 8739825968
      target_identity:
        branch: agent/issue-53-shared-workflow-contracts
        base_ref: main
        current_head: 79caa8a218c8d3fe032f6888092c05a5e668d898
        reviewed_implementation_head: ab20b8875dd71722ada7fe4794e05d4a85671bde
      persistence:
        mode: repository_file
        reserved_paths:
          - reports/issue-53-normal-handoff-followup-20260730060300.md
          - reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
        report_attestation_head: null
      concise_pr_comment_body: packet persistence and current-HEAD evidence to be recorded after commit
      unresolved_discrepancies:
        - packet persistence commit SHA is not available until this file is committed
        - normal reviewer must verify PR54-IFR2-001 after persistence

extensions:
  - namespace: repository_persistence
    payload:
      packet_parent_head: 79caa8a218c8d3fe032f6888092c05a5e668d898
      packet_commit: record externally in Issue and PR after persistence
      packet_commit_is_normal_pre_freeze_write: true
      current_head_validation_required_after_persistence: true
  - namespace: project_instruction_configuration
    payload:
      canonical_file: design/chatgpt-project-instruction-example.md
      target_specific_repository_occurrences: 1
      editable_target_value_location: first target repository URL
      later_references_use_generic_terms: true

next_action:
  type: review
  target_skill: chat-review-worker
  mode: fix_verification
  summary: packet persistence commit後のHEADでPR54-IFR2-001を同じidentityで再確認する
  instructions:
    - reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.mdがschema version 3 required packetを満たすことを確認する
    - packetのtyped projectionとsource_payloadsがlosslessであることを確認する
    - Issue、PR、task、phaseがpacket pathを参照しrepository discoveryを代替扱いしていないことを確認する
    - packet persistence commitに一致するworkflow runとartifactを確認する
    - Project Instruction例で対象固有リポジトリ名が対象URL1か所だけに存在することを確認する
    - PR54-IFR2-002とPR54-IFR2-003がresolvedを維持することを確認する
  required_attachments_or_references:
    - reports/issue-53-independent-final-review-r2-fix-verification-20260729212800.md
    - reports/issue-53-normal-handoff-followup-20260730060300.md
    - reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
    - design/chatgpt-project-instruction-example.md
    - tasks/tasks-status.md
    - tasks/phases-status.md
    - Issue #53
    - PR #54
  requested_authorized_actions:
    - read_repository
    - write_report
    - commit
    - push
    - update_pr
    - comment_pr

transport:
  method: repository_file
  packet_path: reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
  packet_url: null
  transport_note: packet persistence commit SHA、new current HEAD、matching workflow run、artifactは保存後にIssue #53とPR #54へ記録する。現在のchat権限は次chatへ自動継承しない。
```

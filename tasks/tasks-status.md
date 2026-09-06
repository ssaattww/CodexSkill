# Tasks Status

このファイルは `task-breakdown-planner`、`task-consistency-manager`、`progress-sync-manager` のみが更新する。

- Updated: 2026-09-06

## In Progress

- T-004: Windowsネイティブ向けOpenSCAD Skillを設計・追加する
  - Status: 設計reviewのrequired finding対応済み、同一normal reviewerのfix verification待ち。Skill本体は未実装
  - Phase: Phase 9
  - Estimate: L。下表の小さな単位で実施する
  - PR: [#66](https://github.com/ssaattww/CodexSkill/pull/66)
  - Branch: `codex/openscad-windows-skill`
  - Depends on: 設計review収束後の実装開始、コピーする上流fileの取り込み条件確認
  - Scope: SKILLの段階的読込、WindowsのPython実行基盤、既存OpenSCAD機能の移植
  - Non-goals: 今回の設計段階でのコード実装、MCP server新設、汎用自動再構築、新規自動release、merge
  - Exit Criteria:
    - SKILLは入口・共通契約・routingを持ち、必要なmode referenceだけを読む構成が実Codexで確認される
    - WSL／Git BashなしでPythonとOpenSCADを起動し、空白・日本語・apostropheを含むpathと`-D`引数を扱える
    - PNG／STL／3MFの要求成果物と新runの証拠を保存し、部分失敗・未検証を成功にしない
    - 10 mm cube同士、Xへ5 mm移動、完全非重複でvolume IoUがそれぞれ1、1/3、0となる
    - 差分出力不在を0体積として100%一致と報告せず、失敗時はmetric=nullと診断を返す
    - PNG生成とCodexの実画像確認が分離され、未校正profileや未測定壁厚を検証済みにしない
    - crash／強制終了後のrun leaseについてlive／stale-and-provable／liveness-unknownを区別し、PID再利用や判定不能時にrunを誤削除しない
    - `design/openscad-acceptance-plan.md`の必須ACについて実装HEADに紐づく証拠がある
    - 実装後に二つのhierarchy designを同期し、既存repository validatorとZIP buildを確認する
    - 詳細reportとPR要約を保存し、利用者が実装後にmergeする。同じPRを継続使用する
  - Output:
    - [Skill構成設計](../design/openscad-skill-design.md)
    - [実行基盤設計](../design/openscad-runtime-design.md)
    - [受け入れ・実装計画](../design/openscad-acceptance-plan.md)
    - `skills/openscad/`は後続実装で追加する予定。現在は存在しない
  - Verification:
    - TDDはCodexSkill repository policyにより`not applicable`
    - 今回は設計文書とtrackingのみ。Windows実行・画像閲覧・機能受け入れは未実施
    - 設計段階の最終HEADとmatching CIの結果は詳細reportおよびPRコメントへ記録する
    - 既存の他task・phase・ChatGPT worker ZIP構成は変更しない

| T-004内の単位 | Size | Status | Depends on | 終了条件 |
| --- | --- | --- | --- | --- |
| P66-D: 設計と説明 | M | normal design reviewの全required findingへ対応済み、fix verification待ち | 本依頼 | 構成・Windows・受け入れ設計、report、PRコメント、normal review finding収束 |
| P66-I1: Skill分割・出典 | S | 未着手 | P66-D、実装指示、取り込み条件確認 | AC-01〜03、18、20の構造・文書部分。実行を伴う確認は後続単位へ残す |
| P66-I2: CLIと実行基盤 | M | 未着手 | P66-I1 | AC-04〜06、13〜14、19の基盤部分。schema／lease／retentionを含み、render等との結合は後続単位で確認 |
| P66-I3: 基本CAD操作 | M | 未着手 | P66-I2 | AC-06〜10、15、19と基盤の結合。render／validate／export、基本4viewとfeature coverage |
| P66-I4: mesh解析・再構築補助 | M | 未着手 | P66-I3 | AC-11〜12、16〜17、19。比較の失敗分離、schema／frame／複合品質gate、対応model限定 |
| P66-I5: Windows受け入れ・提出 | M | 未着手 | P66-I4 | 全必須ACの実機証拠、設計同期、report。workerはmergeしない |

各単位のAC番号は担当範囲を示す。後続実装が必要な実行項目は未実施のまま引き継ぎ、部分確認をAC全体の合格にしない。全必須ACの最終完了はP66-I5で判定する。

- T-003: Issue #62としてlocal executionとremote-CI-onlyの検証経路を分離する
  - Status: 通常review cycle収束、独立最終review待ち
  - Phase: Phase 8
  - Estimate: M
  - Depends on: Issue #58、Issue #61
  - Exit Criteria:
    - work contextが実際のtool capabilityから`local_execution_available`または`remote_ci_only`を解決する
    - local routeがlocal test、review対象commit、reviewの順で進み、review中にCI完了を待たない
    - local routeのCI-triggering push前に変更範囲のlocal validationがGreenである
    - remote-CI-only routeがmatching current-HEAD CIを正式なverification evidenceとして扱う
    - commit、push、CI waitを別の状態遷移として扱う
    - canonical state vocabularyとして`commit_pending|committed`、`push_pending|pushed`、`ci_wait_pending|ci_wait_completed`をcontext、report、handoff、trackingで保持する
    - final publication candidate HEADのfull local equivalence gateはnormal convergence後に一度だけ実行し、content delta時だけinvalidated evidenceを保持して再実行する
    - finding closure前にrequired action、production path、fixture、evidenceの完全性を確認する
    - terminal attestation後のexact-head pull-request CIだけをlocal routeのmerge gateとして待つ
    - local routeはvalidated local committed HEADをpre-review pushせずfreeze／one-time independent full review／attestation後にfinal push、authorized PR作成または更新、exact-head CI waitの順で進む
    - remote-CI-onlyだけがauthorized pre-review pushとmatching current-HEAD CIをformal verificationに使う
    - independent full reviewは一度だけとし、以後は同一reviewerのfinding／CI-delta closureに限定する
    - review-target、final task、normal report、report-attestation commitのpurpose gateが循環なく区別される
    - runtime-neutral core SkillとCodex／ChatGPT wrapperの責務が重複しない
    - workflow設計、Skill hierarchy、関連Skill contractが同期している
    - repository validation、Markdown check、通常review、独立reviewが成功する
    - commit、push、PR作成が完了する
  - Output:
    - `design/chat-worker-skill-design.md`
    - `design/skill-hierarchy-design.md`
    - `skills/design/skill-hierarchy-design.md`
    - `skills/work-context-manager/SKILL.md`
    - `skills/implementation-worker/SKILL.md`
    - `skills/development-orchestrator/SKILL.md`
    - `skills/execution-cost-stabilizer/SKILL.md`
    - `skills/implementation-executor/SKILL.md`
    - `skills/chat-implementation-worker/SKILL.md`
    - `skills/chat-review-worker/SKILL.md`
    - `skills/chat-handoff-manager/SKILL.md`
    - `skills/review-enforcer/SKILL.md`
    - `skills/review-worker/SKILL.md`
    - `skills/git-workflow-manager/SKILL.md`
    - `skills/git-commit-manager/SKILL.md`
    - `skills/progress-sync-manager/SKILL.md`
    - `skills/report-output-manager/SKILL.md`

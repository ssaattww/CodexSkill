# T-004 / PR #66 設計修正確認レビュー r4

## Metadata

- Date: 2026-09-06 23:18 Asia/Tokyo
- Repository: `ssaattww/CodexSkill`
- PR: #66
- Branch: `codex/openscad-windows-skill`
- Review mode: fix verification
- Reviewer identity: `pr66-design-review-current-chat`
- Reviewer continuity: initial design reviewから同じnormal reviewer。設計修正・実装は行っていない
- Previous review: `PRR_kwDOSFr3-88AAAABMXrJ8g`
- Reviewed design HEAD: `ecb0dc11c7f0ee48225f0b6c6c9c72b4c8791942`
- Fix range: `7e3909f1d789cb21c05eded633dd1e1dc640ebf4..ecb0dc11c7f0ee48225f0b6c6c9c72b4c8791942`
- Verdict: **pass**
- Open source finding identities: **0件**
- Source finding total: **12件 closed / 0件 open**
- Merge: 実施しない

本reviewは前回唯一openだった`PR66-DR-006` / mediumのfix verificationである。同じfinding identityとseverityを維持してclosure条件を確認し、同一欠陥classと今回fix rangeの回帰だけを確認した。独立最終reviewではない。

## Fix差分

前回review report/handoff保存後HEAD `7e3909f1...` からreviewed HEADまで3 commit。net変更は次の3fileのみ。

- `design/openscad-runtime-design.md`: abandoned retention anchor契約
- `design/openscad-acceptance-plan.md`: AC-13 retention回帰fixture
- `reports/task-t-004-pr66-design-review-followup-r4-20260906205500.md`: implementation-side follow-up report

主な技術commit:

- `9347c0d7201833ddb3bfb44c1d28cb176024f64e`: abandoned retention anchor契約
- `eef055bc2038db23d96097bcb0e1788822868d8f`: AC-13回帰fixture
- `ecb0dc11c7f0ee48225f0b6c6c9c72b4c8791942`: follow-up report

今回のfix rangeでは、以前closedしたwarning、preview/verify identity、profile topology、coordinate frame、shape identity、write collision、quality gate、intermediate schema、multi-view PNGの設計本文は変更されていない。

## Finding disposition

### `PR66-DR-006` / medium — **closed**

前回openだった問題は、abandoned runのretention anchorに古い`heartbeat_at`を採用でき、長時間live後にcrashしたrunのdiagnostics保持期間を実質0日に短絡できることだった。

現行runtime §4.4は次の契約へ修正された。

1. abandoned runの既定retention anchorを`abandoned_at`、すなわちreconciliationがterminal化をcommitした時刻に固定した。
2. OSまたはWindows Job Object等からowner termination時刻を信頼できる証拠として取得・記録できる場合だけ`owner_termination_at`をanchorとして許可する。
3. `heartbeat_at`はliveness補助情報でありowner死亡時刻の証拠ではないため、古いheartbeatだけでanchorを過去へ戻さない。
4. resultへ`retention_anchor_source: abandoned_at|owner_termination_at`を保存する。
5. abandonedへreconcileした同じhousekeeping / `project clean --expired-runs` passでも、新しい`retention_until`が未来なら削除候補へ戻さない。

これは前回Required actionの「初回実装では`abandoned_at`/reconciliation時刻をanchorとし、信頼できるtermination timestampがある場合だけ過去時刻を採用し、古いheartbeatをanchorへ使わない」を満たす。

AC-13も次の回帰fixtureを追加している。

- heartbeatを30日超古い時刻に固定したままowner processをliveとして維持する。
- PID / process creation time一致中は`live`で削除禁止であることを先に確認する。
- 後からownerを終了し、PID不在またはcreation time不一致でstaleを証明してabandonedへreconcileする。
- termination時刻を信頼できる証拠として取得できないfixtureでは`retention_anchor=abandoned_at`、`retention_anchor_source=abandoned_at`とする。
- `retention_until`がreconcile時点から新たに`retain_days`分確保される。
- 同じhousekeeping passおよび直後の`project clean --expired-runs`でdiagnostics / run directoryを削除しない。
- 古いheartbeatをanchorへ採用しない。

これにより前回Closure / acceptance条件を満たす。新しい矛盾や同一欠陥classの残存は確認しなかった。

## Source finding convergence

本normal reviewで追跡したsource findingは全件closedとなった。

- `P66-DR-001` / `PR66-DR-001`: warning gate — closed
- `P66-DR-002`: explore/verify PNGとexport評価条件 — closed
- `P66-DR-003`: profile topology — closed
- `P66-DR-004`: source / analysis frame — closed
- `P66-DR-005` / `PR66-DR-004`: Reconstruct複合品質gate — closed
- `PR66-DR-002`: dependency / override / artifact shape identity — closed
- `PR66-DR-003`: intermediate artifact schema / consumer compatibility — closed
- `PR66-DR-005`: write target / same-file / no-clobber / concurrent run — closed
- `PR66-DR-006`: diagnostics ownership / retention / stale lease / retention anchor — closed
- `P66-DR-006`: multi-view PNG / visual feature coverage — closed

歴史的なfinding ID系列を統合・再採番していない。既存severityも変更していない。

## Coverage

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| requirement / design conformance | `checked_no_finding` | 前回`PR66-DR-006` Required actionとClosureをruntime §4.4 / AC-13が満たす |
| correctness / edge cases | `checked_no_finding` | old heartbeat + long-lived owner + later crashでretentionを新規確保 |
| scope / unrelated changes | `checked_no_finding` | fix rangeのnet変更はruntime、acceptance、follow-up reportのみ |
| API / data / compatibility | `checked_no_finding` | anchor sourceをresultへ保存し、既存lease lifecycleと整合 |
| error / diagnostics | `checked_no_finding` | crash後diagnosticsをreconcile直後にexpired扱いしない |
| security / secret handling | `checked_no_finding` | host token / PID reuse / unknown安全側契約を変更せず維持 |
| validation adequacy | `checked_no_finding` | AC-13に30日超old-heartbeat→later-crash fixture追加 |
| current-HEAD CI | `checked_no_finding` | exact reviewed HEAD run `34031837729` success |
| reports / tracking / docs | `checked_no_finding` | follow-up r4はfinding identityを維持。PRはDraft、Skill未実装を明示 |
| regression / maintainability | `checked_no_finding` | 前回closed領域にnet変更なし。retention anchor ruleを一意化 |

## CI / validation

Reviewed HEAD `ecb0dc11c7f0ee48225f0b6c6c9c72b4c8791942` と完全一致するpull_request workflow runだけをCI evidenceに使用した。

- Run: `34031837729`
- Event: `pull_request`
- Run `head_sha`: `ecb0dc11c7f0ee48225f0b6c6c9c72b4c8791942`
- Attempt: 1
- Conclusion: `success`
- Build job: `101482672267` / success
- repository Skill architecture / active-link validation: success
- existing ChatGPT worker ZIP build / verify: success
- artifact upload: success
- Artifact: `9988862970` / `chatgpt-worker-skills-34031837729` / 18678 bytes / expired=false
- Digest: `sha256:6140a7642442dab16e8da3715607b332109305139e9b648f386f3e44404e3dfd`

別SHAのrunは代用していない。

このCIはrepository文書・既存worker ZIPのvalidationであり、Windows process liveness / termination timestamp API、OpenSCAD runtime、Codexによるverify PNG実閲覧、profile / slice / optimizeの実機受け入れ証拠ではない。これらはSkill未実装のためnot_runであり、設計review passを実装成功へ変換しない。CodexSkill policyによりTDDはnot applicable。

## Held / unexplored

- Windows native OpenSCAD実行: 未実装のためnot_run。
- Windows process liveness / termination timestamp API: 未実装のためnot_run。
- multi-view PNGの実生成・Codex実閲覧: 未実装のためnot_run。
- profile / slice / reconstruct quality fixtureの実行: 未実装のためnot_run。
- independent final review: **未実施**。本reviewerはnormal reviewerであり、同じreviewerが独立最終reviewを代行しない。
- upstream assetの正式な取り込み条件 / notice確認: 実装前gateとして継続。

これらは未実装・次段階の項目であり、現在のnormal design reviewのrequired findingとして再openしない。

## Verdict / next action

**pass**。normal design reviewのsource finding 12件はすべてclosedし、このfix verification cycleは収束した。

次のreview lifecycle actionは、必要な独立性を持つ別reviewerによるindependent final reviewである。独立最終reviewを通過するまで、本normal review passを最終承認または実装済み証拠として扱わない。PRはDraftのまま維持し、workerはmergeしない。

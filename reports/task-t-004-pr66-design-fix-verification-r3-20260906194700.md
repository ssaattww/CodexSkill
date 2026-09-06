# T-004 / PR #66 設計修正確認レビュー r3

## Metadata

- Date: 2026-09-06 19:47 Asia/Tokyo
- Repository: `ssaattww/CodexSkill`
- PR: #66
- Branch: `codex/openscad-windows-skill`
- Review mode: fix verification
- Reviewer identity: `pr66-design-review-current-chat`
- Reviewer continuity: 前回までのnormal reviewerと同一。設計修正・実装は行っていない
- Previous review: `PRR_kwDOSFr3-88AAAABMXkROg`
- Reviewed design HEAD: `55ea86530ee342689d5a8ef3ac5ae60b488cdf3f`
- Fix range: `b45e4e16bcb32aa5e1e5948b11762df920b35a8f..55ea86530ee342689d5a8ef3ac5ae60b488cdf3f`
- Verdict: **fail**
- Open source finding identities: **1件 (`PR66-DR-006` / medium)**
- Merge: 実施しない

本reviewは前回唯一openだった`PR66-DR-006`のfix verificationである。source finding identityとseverityを維持し、同一欠陥classだけを確認する。独立最終reviewではない。

## Fix差分

前回publication HEAD `b45e4e16...` からreviewed HEADまで6 commit、net変更は次の3file。

- `design/openscad-runtime-design.md`: +27 / -10
- `design/openscad-acceptance-plan.md`: +16 / -7
- `reports/task-t-004-pr66-design-review-followup-r3-20260906190000.md`: +125

実装側reportによれば主な技術commitは`e1eebc4e1e008084e887c4017a20c5da243c6340`（run lease lifecycle）と`74a4fbf42537137f95b1d1f16166a3fef3434640`（AC-13）。途中で誤更新されたtrackingは`55ea86530ee342689d5a8ef3ac5ae60b488cdf3f`でreview前blobへ復元され、上記compareのnet差分にtracking fileは残っていない。

## Finding disposition

### `PR66-DR-006` / medium — **open / partial**

前回指摘したstale active marker recoveryの主要部分は修正された。

- active markerを`openscad.run-lease` v1へversion化。
- host token、PID、process creation time、nonce、heartbeatを記録。
- heartbeatの古さだけではstaleにしない。
- WindowsではPIDとprocess creation timeでowner identityを検査し、PID reuseを区別。
- `live` / `stale-and-provable` / `liveness-unknown`を分離。
- stale証明後もreconciliation claimと再検査を行ってから`abandoned` terminal lifecycleへ遷移。
- unknownはauto/manual cleanで削除禁止。
- AC-13にlive owner、crash、PID reuse、liveness unknownのfixtureを追加。

これにより「stale active markerが永久にclean不能になる」主要経路と、PIDだけでlive/staleを誤認する経路は設計上解消された。

ただし、**abandoned runのretention anchorが古いheartbeatを採用できるため、診断保持期間を短絡できる**。

runtime §4.4は、`stale-and-provable`を`abandoned`へreconcileしたとき、妥当な`heartbeat_at`がreconcile時刻以前ならそのheartbeatをretention anchorにし、abandoned runのretentionをそのanchorから30日とする。一方、同じ節は`live`判定では「heartbeatが古くてもPIDとcreation timeが一致すればlive」と明記している。AC-13もlive owner fixtureでheartbeatを意図的に古くしてもliveであることを要求している。

したがって次の合法状態が成立する。

1. 1月1日にrun開始。最終heartbeatも1月1日。
2. heartbeat更新だけ停止するがowner processはPID/creation time一致でliveのまま2月15日まで動く。
3. 2月15日にprocessがcrashし、次回操作でPID不在を証明してabandonedへreconcileする。
4. 現行契約ではretention anchorが1月1日のheartbeatになり、30日retentionは1月31日に既に満了している。
5. reconcile直後の同じhousekeepingまたは次のcleanで、failure diagnosticsを実質0日保持のまま削除できる。

古いheartbeatは「最後にheartbeat更新できた時刻」ではあっても「ownerが死亡した時刻」ではない。現設計自身がheartbeat expiry単独のstale判定を禁止しているため、古いheartbeatをabandoned retentionの死亡時刻相当として扱うのは整合しない。

### Impact

元findingは、失敗時のhelper SCAD、stdout/stderr、中間成果物を調査可能な形で保持し、保持期間とclean lifecycleを定義することを要求している。現在のanchor規則では、長時間liveだったrunがcrashした場合に、reconciliationで初めて失敗を認識した直後にdiagnosticsが期限切れ扱いとなり得る。retentionを30日と表示していても、利用者がfailure evidenceへアクセスできる期間を保証できない。

### Required action

abandoned runのretention anchorを、単なる最終heartbeatより前へ戻さない契約に修正する。crash時刻を信頼できる別証拠で確定できない初回実装では、**`abandoned_at` / reconciliation時刻をretention anchorとする**のが安全で明確である。heartbeatはliveness補助情報として保持してよいが、heartbeatが古いという理由でreconciliation後の保持期間を消費済みにしない。

もし将来、OS等から信頼できるowner termination時刻を取得する場合は、その時刻を採用する条件と信頼性を別途定義する。推測したdeath timeは使わない。

### Closure / acceptance

AC-13へ少なくとも次を追加する。

- `--retain-days 30`のrunでheartbeatを30日超古くする。
- その状態でもowner PID/creation time一致中は`live`で削除しない。
- その後ownerを終了させて`stale-and-provable`→`abandoned`へreconcileする。
- `retention_until`が古いheartbeat基準で過去にならず、reconciliation/`abandoned_at`から30日後（または設計で定義した信頼できるtermination時刻＋30日）になること。
- reconcileを行ったhousekeepingと直後の`project clean --expired-runs`で当該diagnosticsを削除しないこと。
- 30日経過後に初めてexpiry条件を満たすこと。

## Regression / coverage

今回のlease追加が前回closedしたquality gate、artifact schema、multi-view PNG、warning、shape identity、topology/frame、write collisionを変更していないことをfix rangeとnet changed filesで確認した。新規の別findingは追加しない。

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| requirement / design conformance | `checked_finding` | `PR66-DR-006` retention anchorのみ残存 |
| correctness / edge cases | `checked_finding` | old-heartbeat + long-lived owner + later crash |
| scope / unrelated changes | `checked_no_finding` | net変更はruntime、acceptance、follow-up reportのみ。tracking差分は復元済み |
| API / data / compatibility | `checked_no_finding` | lease schema v1、PID+creation time、unknown分類は明確 |
| error / diagnostics | `checked_finding` | abandoned diagnosticsの実効保持期間が短絡可能 |
| security / secret handling | `checked_no_finding` | raw hostname/account/hardware IDを保存せずhost token化、unknownは安全側 |
| validation adequacy | `checked_finding` | AC-13にlong-live/old-heartbeat→later-crashのretention fixture不足 |
| regression / maintainability | `checked_no_finding` | reconciliation claimと再検査、PID reuse対策は整合 |

## CI / validation

Reviewed HEAD `55ea86530ee342689d5a8ef3ac5ae60b488cdf3f`と完全一致するpull_request workflow runだけをCI evidenceに使用した。

- Run: `34028233551`
- Event: `pull_request`
- Run `head_sha`: `55ea86530ee342689d5a8ef3ac5ae60b488cdf3f`
- Attempt: 1
- Conclusion: `success`
- Build job: `101472943720` / success
- repository Skill architecture / active-link validation: success
- existing ChatGPT worker ZIP build / verify: success
- artifact upload: success
- Artifact: `9987744571` / `chatgpt-worker-skills-34028233551` / 18678 bytes
- Digest: `sha256:9301a48628a7243999242cc0b5850253eb9f7ecca981c23329281c50eb71c91e`

このCIはrepository文書・既存worker ZIPのvalidationであり、Windows process liveness API、OpenSCAD runtime、PNG実閲覧等の実機受け入れ証拠ではない。CodexSkill policyによりTDDはnot applicable。

## Verdict / next action

**fail**。12 source finding中11件closed、`PR66-DR-006` 1件のみopen。

同じfinding identityを維持してretention anchorとAC-13を修正し、同じnormal reviewerでfix verificationを継続する。独立最終reviewへはまだ進めない。workerはmergeしない。

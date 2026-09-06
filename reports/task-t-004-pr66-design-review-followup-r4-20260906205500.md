# PR #66 OpenSCAD設計review指摘対応 report r4

## 1. 対象

- Repository: `ssaattww/CodexSkill`
- PR: #66 `feat(openscad): Windows対応Codex Skillの設計・実装`
- Branch: `codex/openscad-windows-skill`
- 対象review: `PRR_kwDOSFr3-88AAAABMXrJ8g`
- 対象finding: `PR66-DR-006` / medium
- Review時のtechnical HEAD: `55ea86530ee342689d5a8ef3ac5ae60b488cdf3f`
- Review report/handoff追加後の作業開始HEAD: `7e3909f1d789cb21c05eded633dd1e1dc640ebf4`

本対応では別の`review/*`branchを作らず、既存PR head branchだけを更新した。Skill本体・Python runtimeは未実装であり、本reportは設計契約と受け入れ条件の修正記録である。

## 2. 指摘内容

前回対応でrun ownership lease、`live | stale-and-provable | liveness-unknown`、PID reuse対策、abandoned reconciliationを定義したが、abandoned runのretention anchorに古い`heartbeat_at`を採用できる契約が残っていた。

同じ設計ではheartbeatが古くてもPIDとprocess creation timeが一致すればownerはliveである。このためheartbeatはowner死亡時刻の証拠ではない。30日超古いheartbeatをanchorにすると、ownerが後からcrashしてabandonedへreconcileされた直後にretentionが既に期限切れとなり、diagnosticsを即時削除できる矛盾があった。

## 3. 修正

### 3.1 Runtime contract

`design/openscad-runtime-design.md`を更新した。

- abandoned runの既定retention anchorを`abandoned_at`へ固定した。
- OS、Windows Job Object等からowner termination時刻を信頼できる証拠として取得・記録できた場合だけ`owner_termination_at`をanchorとして許可した。
- `heartbeat_at`をretention anchorに使用しないことを明示した。
- resultへanchor sourceを`abandoned_at | owner_termination_at`として保存する契約を追加した。
- abandonedへreconcileした同じhousekeeping / `project clean --expired-runs` passでも、新しい`retention_until`が未来なら削除候補へ戻さないことを明示した。
- `result.retention`にanchor sourceを含めることを明示した。

Commit: `9347c0d7201833ddb3bfb44c1d28cb176024f64e`

### 3.2 Acceptance contract

`design/openscad-acceptance-plan.md`のAC-13を更新した。

既存4 fixtureに加え、5番目として次を要求する。

1. heartbeatを30日超古い値に固定する。
2. PID + process creation timeが一致するownerをliveのまま維持する。
3. heartbeatの古さだけでは削除されないことを確認する。
4. 後からownerを終了し、PID不在またはcreation time不一致でstaleを証明する。
5. abandonedへreconcileする。
6. termination時刻を信頼できる証拠として取得できない場合、`retention_anchor=abandoned_at`かつ`retention_anchor_source=abandoned_at`になることを確認する。
7. `retention_until`がreconcile時点から新たに`retain_days`分確保されることを確認する。
8. 同じhousekeeping passおよび直後の`project clean --expired-runs`でdiagnostics / run directoryが削除されないことを確認する。

crash後stale marker fixtureについても、古いheartbeatをowner死亡時刻として利用しない契約へ修正した。

Commit: `eef055bc2038db23d96097bcb0e1788822868d8f`

## 4. 設計上の結果

今回の修正により、次の状態を区別する。

- live owner: heartbeatが古くてもowner identityがliveなら削除不可。
- stale-and-provable: owner不在またはPID reuse等を証明した場合だけabandonedへreconcile可能。
- liveness-unknown: 削除不可。
- abandoned: retentionは原則reconciliation時点から新しく開始する。
- owner termination時刻を過去へ遡ってanchorにするのは、OS等からその時刻を信頼できる証拠として取得できた場合だけ。

これにより「heartbeatは死亡証拠ではない」というliveness contractとretention contractが整合する。

## 5. 検証境界

CodexSkill repository policyに従いTDDは適用していない。今回追加したACは後続実装のacceptance fixtureであり、現時点では未実行である。

未実施:

- Windows process creation time / liveness APIの実装と実機検証
- crash / PID reuse / 30日超heartbeat fixtureの実行
- OpenSCAD runtime実装
- Codexによるverify PNG実閲覧

既存GitHub Actionsはrepository Skill architecture / active linksと既存ChatGPT worker ZIPを検証するもので、上記Windows runtime機能の証拠ではない。

## 6. CI方針

本report保存後にPR current HEADを再取得し、そのHEAD SHAとrun `head_sha`が完全一致するpull_request workflow runだけをCI証拠として使用する。一致runがなければCI未実施として扱い、過去SHAのsuccess runを代用しない。

## 7. 次の状態

- `PR66-DR-006`のfinding identityを維持して同じnormal reviewerによるfix verificationを待つ。
- reviewerがclosedと判定するまでは独立最終reviewやSkill実装へ進んだとは扱わない。
- PRはDraftのまま維持する。
- workerはmergeしない。
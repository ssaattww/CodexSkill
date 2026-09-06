# PR #66 設計review指摘対応 follow-up r3

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: #66 `feat(openscad): Windows対応Codex Skillの設計・実装`
- Branch: `codex/openscad-windows-skill`
- 対象review: `PRR_kwDOSFr3-88AAAABMXkROg`
- Review対象HEAD: `90eace372722d9abdf3be541eba8e9f12433fae3`
- Reviewer report/handoff保存後HEAD: `b45e4e16bcb32aa5e1e5948b11762df920b35a8f`
- 残存finding: `PR66-DR-006` / medium

本対応では別の`review/*`branchを作成せず、既存PR branchだけを更新した。mergeは行わない。

## finding

前回fix verification r2では、12 source finding中11件がclosedし、`PR66-DR-006`だけがopenとなった。

残存論点は、run diagnosticsのretention／ownership自体は定義された一方、crash、CLI強制終了、OS再起動などで`active` markerだけが残った場合のowner livenessとstale判定が未定義であったこと。PIDだけで判定するとWindowsのPID再利用により、live runの誤削除またはstale runの永久保持が起こり得る。

## 対応内容

### 1. active markerをversioned leaseへ変更

`design/openscad-runtime-design.md`でrun開始時に`.openscad/runs/<run-id>/lease.json`をatomic作成する契約を追加した。

- `schema_id: openscad.run-lease`
- `schema_version: 1`
- `project_id`
- `run_id`
- `owner_host_token`
- `owner_pid`
- `owner_process_start_time_utc`
- random `lease_nonce`
- `started_at`
- `heartbeat_at`
- `state`

`owner_host_token`は同一hostのCLI invocation間で安定するuser-local random UUIDとし、hostname、Windows account名、hardware serial等の生識別子を保存しない。

### 2. livenessを3状態へ分類

heartbeatの古さだけでstale判定せず、WindowsではPID存在とOS process creation timeを組み合わせる。

- `live`
  - host token一致
  - PID存在
  - process creation time一致
  - heartbeatが古くても削除しない
- `stale-and-provable`
  - host token一致
  - PID不在、またはPID存在でもcreation time不一致
  - PID再利用をcreation time不一致として判別する
- `liveness-unknown`
  - host token不一致／取得不能
  - process query access denied
  - creation time取得不能
  - lease identity欠落・破損
  - 自動・明示cleanとも削除禁止

### 3. stale runのabandoned reconciliation

`stale-and-provable`は即削除せず、run単位reconciliation claim取得後にlease/process identityを再検査する。再確認でもstaleの場合だけ、runを次のterminal lifecycleへatomicにreconcileする。

- `status: failed`
- `run_lifecycle: abandoned`
- `exit_code: null`
- `abandoned_reason`
- `abandoned_at`
- lease `state: abandoned`

実processが返していないexit codeを捏造しない。既存diagnosticsはreconcile時に保持する。

abandoned runのretention anchorは、妥当な最終`heartbeat_at`がreconcile時刻以前ならその時刻、欠落・未来値等で信用できなければreconcile時刻とする。

### 4. clean／housekeeping境界

自動housekeepingはcurrent project所有、terminalまたはabandoned、retention超過、live/unknownでない、path実体検査済みのrunだけをpruneできる。

`project clean --run-id`もreleased terminalまたはstale証明後にabandonedへreconcile済みのrunだけを対象にする。`liveness-unknown`を強制削除するescape hatchは初回実装では提供しない。

共有projectを別hostから開いた場合はhost token不一致のためunknownとし、remote process死亡を推測しない。

### 5. AC-13 fixture追加

`design/openscad-acceptance-plan.md`のAC-13へ次の4ケースを追加した。

1. live owner
   - process生存、host token/PID/creation time一致
   - heartbeatを意図的に古くしても`live`
   - housekeeping／expired clean／run-id cleanで削除しない
2. crash後stale marker
   - active leaseだけ残してowner process終了
   - PID不在を証明して`stale-and-provable`
   - 再検査後`abandoned`へreconcileし、diagnosticsを保持
3. PID reuse
   - 同じPIDのlive processがあるがcreation timeを意図的に不一致にする
   - PIDだけでlive判定せず`stale-and-provable`
4. liveness unknown
   - host token不一致、access denied、creation time取得不能
   - unknownとしてauto/manual clean双方で保持し、理由を返す

### 6. schema／実装計画同期

中間artifact schema一覧へ`openscad.run-lease` v1を追加し、P66-I2の担当範囲にlease lifecycleを含めた。

## 変更commit

- `e1eebc4e1e008084e887c4017a20c5da243c6340` — `docs(openscad): define recoverable run lease lifecycle`
- `74a4fbf42537137f95b1d1f16166a3fef3434640` — `docs(openscad): add stale lease recovery acceptance`

## 検証

CodexSkill repository policyによりTDDは`not applicable`。今回は設計文書のみの修正で、workflow、Skill実装、Python実装は変更していない。

このreportは技術修正後に保存するadministrative recordであり、本file自身を含む将来のcommit SHAやCI成功を先取りして記載しない。report保存後のcurrent PR HEADに対するmatching `pull_request` workflow runだけをPR body／PR commentで確認する。

Windows OpenSCAD実行、process liveness API、verify PNG実閲覧、profile／slice／optimizeの機能受け入れはSkill未実装のため未実施。今回の設計追加は実装契約と受け入れfixtureの定義であり、実機成功を意味しない。

## 状態

- `PR66-DR-006`: 実装修正側では設計対応済み
- review verdict: 同一normal reviewerによるfix verification待ち
- independent final review: 未実施
- merge: 未実施

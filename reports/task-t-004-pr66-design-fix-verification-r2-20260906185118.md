# T-004 / PR #66 設計修正確認レビュー r2

## Metadata

- Date: 2026-09-06 18:51:18 Asia/Tokyo
- Repository: `ssaattww/CodexSkill`
- PR: #66
- Branch: `codex/openscad-windows-skill`
- Base: `6507727986329e34e69da3680a00824eb1fbfe13`
- Review mode: fix verification
- Reviewer identity: `pr66-design-review-current-chat`
- Reviewer continuity: 前回のnormal review / fix verificationと同じchat・reviewer。設計修正・実装は行っていない
- Reviewed design HEAD: `90eace372722d9abdf3be541eba8e9f12433fae3`
- Fix range: `d04e76346b24239f002eb4a512fedfaf4623120e..90eace372722d9abdf3be541eba8e9f12433fae3`
- Verdict: **fail**
- Source findings: 元12件のうち **11件closed、1件open**
- Severity reclassification: なし
- Merge: 実施しない

本レビューは前回openだった5 source findingを固定して再検証し、修正差分による新規regressionも確認した。未実装のWindows OpenSCAD機能・PNG閲覧・profile/slice/optimize実行を実施済みとは扱わない。

## Fix差分

前回handoff HEAD `d04e763...` から reviewed HEAD まで4 commit、4 file。

- `03257ea1ae149eaeceaa59b0edce0b0f9b7e6708`: multi-view / visual feature coverage契約
- `9c15856463f6329ecf6d72008394e54095ced5b5`: quality gate / schema / diagnostics lifecycle契約
- `b2e016febabc743aeed6a81e2e858eb0de82f214`: acceptance fixture更新
- `90eace372722d9abdf3be541eba8e9f12433fae3`: implementation-side follow-up report

変更file:

- `design/openscad-skill-design.md`
- `design/openscad-runtime-design.md`
- `design/openscad-acceptance-plan.md`
- `reports/task-t-004-pr66-design-review-followup-r2-20260906184500.md`

Skill本体、script、workflow、README、hierarchy、trackingはこのfix rangeでは変更されていない。

## Finding continuity / disposition

| Finding | Source severity | Disposition | Evidence |
| --- | --- | --- | --- |
| `P66-DR-001` | P1 | closed（前回維持） | warning gate / AC-08 |
| `PR66-DR-001` | high | closed（前回維持） | 同一warning欠陥class |
| `P66-DR-002` | P1 | closed（前回維持） | explore/verify分離、final evaluation identity |
| `P66-DR-003` | P2 | closed（前回維持） | profile topology保持 |
| `P66-DR-004` | P2 | closed（前回維持） | source/analysis frameと逆変換 |
| `PR66-DR-002` | medium | closed（前回維持） | dependency/override/artifact identity |
| `PR66-DR-005` | medium | closed（前回維持） | path identity / no-clobber / concurrent claim |
| `P66-DR-005` | P2 | **closed** | IoU + bbox寸法 + required critical feature + unverified featureの複合gate。CLI target optionと値域、AC反例あり |
| `PR66-DR-004` | medium | **closed** | 品質targetの公開CLI、feature/dimension tolerance、quality spec、低品質反例を具体化 |
| `PR66-DR-003` | medium | **closed** | `openscad.profile` / `openscad.feature-map` / quality/view schema v1とconsumer compatibility gate、AC fixtureあり |
| `PR66-DR-006` | medium | **open / partial** | ownership / 30日retention / clean対象は追加されたが、stale active marker recoveryが未定義 |
| `P66-DR-006` | P2 / medium | **closed** | Quick含む形状変更modeの基本4 view、hidden feature追加view、feature-to-view coverage、一部失敗時のaggregate ruleをSkill/runtime/ACへ反映 |

## Closed finding verification

### `P66-DR-005` / `PR66-DR-004` — Reconstruct品質gate

runtime §8.4は `volume_iou_target_met`、`major_dimensions_target_met`、`critical_features_target_met`を別checkにし、既定gateを次のAND条件へ変更した。

1. export mesh `volume_iou >= 0.95`
2. source/candidate bbox X/Y/Z誤差 `<= 0.20 mm`
3. required feature全件が個別tolerance内
4. 検出した重要featureを分類・計測・照合できない場合は`unverified_feature`として成功にしない

公開CLIも `--min-volume-iou`、`--dimension-tolerance-mm`、`--quality-spec` を具体化し値域を定義している。`openscad.reconstruct-quality` v1はstable feature ID、kind、source-frame期待値、単位、tolerance、measurement methodを持ち、自動抽出required featureを黙って削除できない。

AC-16は「小体積の穴/slotを塞いでもIoU >= 0.95」の反例を要求し、feature gateでcandidate全体を不合格にする。元findingが求めた「高いIoUだけで重要feature欠落を隠さない」「主要寸法・feature・許容誤差」「利用者target入力場所」を満たすためclosed。

### `PR66-DR-003` — 中間artifact schema / consumer compatibility

runtime §7.1に次のschema ID/versionが定義された。

- `openscad.profile` v1
- `openscad.feature-map` v1
- `openscad.reconstruct-quality` v1
- `openscad.view-manifest` v1

各artifactはtop-level schema ID/version、producer version、source identity、必要frame参照を持つ。consumerはpayload読取前に完全一致するsupported versionを検査し、unknown/unsupportedはblocked/exit 3、必須field欠落・型不正はexit 2。migrationは明示変換としてversionを記録する。

AC-16/19にはv1、unsupported v2、schema ID違い、必須field欠落を含むため、元closure条件を満たしclosed。

### `P66-DR-006` — 複数面PNG

Skill §4.2/§6でQuick/Design/Refine/Modify/Replicate/Reconstructを形状変更modeとして基本 `iso/front/right/top` の4方向verifyへ接続した。4方向でrequired/changed featureが見えない場合は `back/left/bottom/custom/section diagnostic`を追加し、`visual_feature_coverage`でfeature ID、期待状態、view、実閲覧、所見を関連づける。

required viewの生成失敗・破損・未閲覧、またはrequired feature未確認をvisual passにしない。Export-onlyの限定依頼へ無条件で4 viewを追加しない。AC-07にhidden back/bottom feature、一部失敗、実閲覧まで具体化したためclosed。

## Open finding

### `PR66-DR-006` / medium — stale active markerのrecovery規則がない

**Origin:** 既存source findingのdiagnostics ownership / retention / explicit clean lifecycleのfix verification。同一欠陥classであり、新規finding IDへ分割しない。

**Location:** `design/openscad-runtime-design.md` §4.4、`design/openscad-acceptance-plan.md` AC-13。

**Description:** 今回、stable `project_id`、run ownership、`retention_until`、既定30日、`--retain-days 1..3650`、自動housekeeping、`project clean --expired-runs`、`project clean --run-id`が追加された。一方、削除可能条件は「非active」であり、`active marker`を実行中runの根拠として扱うが、process crash、Codex/CLI強制終了、OS再起動等でmarkerだけ残った場合のstale判定・recoveryが定義されていない。

**Impact:** 実processが存在しないのにactive markerだけ残ると、期限超過後のhousekeepingでも明示`--run-id`でも削除できない。特にfailure diagnosticsを保持する仕組み自身が、abandoned runを無期限に蓄積する経路を持つ。逆に単純なmarker削除を実装者判断で加えると、実行中runを誤ってcleanする危険がある。

**Evidence:** runtime §4.4は「active markerが残る実行中runを自動削除しない」「`--run-id`も非active検査を必須」とするが、marker ownerのliveness、marker lease/heartbeat、process start identity、staleへの状態遷移を定義していない。AC-13もactive runを残すfixtureはあるが、owner process消失後にmarkerだけ残るfixtureがない。

**Required action:** active状態を単なる永続markerではなく、owner livenessを再検証可能なleaseとして定義する。少なくともrun/project IDに加え、owner processをPIDだけで誤認しない識別情報（process creation identity、session/boot識別または同等手段）を保持し、CLI起動時またはclean時に次を区別する。

- ownerが実在し同じ実行identity: activeのまま削除禁止
- owner不在/identity不一致でstaleと証明可能: runを`abandoned`等のterminal stateへ遷移し、診断を保持したうえでretention/明示clean対象にできる
- staleか安全に判定不能: 削除せずblocked/warning

WindowsでPID再利用だけを根拠にactive扱いしない。Job Object等を利用する場合も、次回processから過去job livenessをどう認定するかを契約化する。

**Closure / acceptance:** AC-13へ次を追加する。

1. owner processが生きているactive runはhousekeeping/explicit clean双方で削除されない
2. owner processを異常終了させactive markerだけ残したrunは、次回起動でstale/abandonedとして安全にreconcileできる
3. reconcile後はretention期限超過または明示`--run-id`で削除できる
4. PID再利用または別processを元ownerと誤認しない
5. livenessを安全に判定できない場合は削除せず診断する

## Regression / broader coverage

fix rangeの3設計文書とfollow-up reportに加え、PR body、canonical task state、既存source finding reportを照合した。

- requirement/design conformance: `checked_finding` — PR66-DR-006のみ残存
- correctness / edge cases: `checked_finding` — crash/reboot後のstale marker
- scope / unrelated changes: `checked_no_finding` — fix rangeは3設計文書+follow-up reportのみ
- changed files / direct dependencies: `checked_no_finding` — Skill/runtime/acceptanceはmulti-viewで同期、quality/schemaもruntime/AC同期
- API/data/config/workflow/compatibility: `checked_no_finding` — quality CLI値域、schema compatibility、view IDsを具体化
- error handling / diagnostics: `checked_finding` — stale active recoveryのみ未定義
- security / secret handling: `checked_no_finding` — project ownership、path identity、junction、no-clobber既存契約を維持
- tests / validation adequacy: `checked_finding` — AC-13にstale marker fixture不足
- current-HEAD CI: `checked_no_finding` — reviewed HEAD exact-match run success
- reports / tracking / docs: `checked_no_finding` — PR bodyは今回open 5 source findingへの対応待ち状態を明記。task trackingは広義の設計・利用者確認待ちを維持
- regression / maintainability: `checked_finding` — crash recoveryのstate machineだけ残存

新規の別findingは追加しない。

## Validation

Reviewed HEAD `90eace372722d9abdf3be541eba8e9f12433fae3` と完全一致するpull_request runのみを確認した。

- Workflow run: `34025392743`
- Event: `pull_request`
- `head_sha`: `90eace372722d9abdf3be541eba8e9f12433fae3`
- Attempt: 1
- Conclusion: `success`
- Build job: `101465331215` / success
- repository Skill architecture / active-link validation: success
- existing ChatGPT worker ZIP build / verify: success
- artifact upload: success
- Artifact: `9986879054` / `chatgpt-worker-skills-34025392743` / 18678 bytes / expired=false
- Digest: `sha256:d4ead276eb81cdca9a6778b97aff820613de57742e268e5b79cf955e7356f3b7`

このCIはrepository設計・既存worker ZIPの検証であり、Windows OpenSCAD runtime、Codexのverify PNG実閲覧、profile/slice/optimize受け入れの成功証拠ではない。Markdown lintはrepository配線不在によりunsupported。CodexSkill repository policyによりTDDはnot applicable。

## Verdict / next action

**fail**。元source finding 12件中11件closed、`PR66-DR-006` 1件だけopen。

同じfinding identityを維持してstale active marker recoveryとAC-13を修正し、同じnormal reviewerでfix verificationを継続する。独立最終reviewへはまだ進めない。reviewerは設計・実装を修正せず、mergeしない。

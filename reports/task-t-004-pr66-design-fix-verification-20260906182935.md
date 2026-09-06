# T-004 / PR #66 設計修正確認レビュー

## Metadata

- Date: 2026-09-06 18:29:35 Asia/Tokyo
- Repository: `ssaattww/CodexSkill`
- PR: #66
- Branch: `codex/openscad-windows-skill`
- Base: `6507727986329e34e69da3680a00824eb1fbfe13`
- Review mode: fix verification
- Reviewer identity: `pr66-design-review-current-chat`
- Reviewer continuity: 前回の通常reviewと同じchat／reviewer。設計修正・実装は行っていない
- Reviewed design HEAD: `38824e11621b9dc09ead47cda73ff27c5fd5cdb0`
- Fix range: `ec39c07d43d61c05a297af573e28672a056bcf94..38824e11621b9dc09ead47cda73ff27c5fd5cdb0`
- Verdict: **fail**
- Open source finding identities: 5件。論理上は4論点
- Merge: 実施しない

本レビューは、前回までに記録したfinding identityとseverityを維持し、設計修正差分、影響契約、同一欠陥class、current-HEAD CIを確認する。未実装のWindows OpenSCAD機能を実行済みと扱わない。

## Fix差分

`ec39c07...`からreviewed HEADまでの3 commitは以下。

- `4b5beb1c8d2f2489dc38699a71a3fb76b858d87a`: runtime契約更新
- `92a10a5c35a67790b50991627a8ff4f9b461b6f2`: acceptance fixture更新
- `38824e11621b9dc09ead47cda73ff27c5fd5cdb0`: follow-up report保存

変更fileは `design/openscad-runtime-design.md`、`design/openscad-acceptance-plan.md`、`reports/task-t-004-pr66-design-review-followup-20260906182238.md` の3file。`design/openscad-skill-design.md`は変更されていない。

## Finding continuity / disposition

| Finding | Source severity | Disposition | Evidence |
| --- | --- | --- | --- |
| `P66-DR-001` | P1 | **closed** | warning gate、blocking diagnostic、unknown warning、exit/check対応をruntime §8.1とAC-08へ追加 |
| `PR66-DR-001` | high | **closed** | 上記と同一欠陥class。exit 0・非空成果物だけで成功にしないfixtureを定義 |
| `P66-DR-002` | P1 | **closed** | explore/verifyを分離し、verify PNGとexportを`$preview=false`、同一source identityへ固定。AC-07/10追加 |
| `P66-DR-003` | P2 | **closed** | outer/hole/component topology保持、hole union禁止、曖昧topology非成功。AC-16追加 |
| `P66-DR-004` | P2 | **closed** | source/analysis frame、4x4変換・逆変換、source frame比較、round-tripを定義。AC-16/17追加 |
| `PR66-DR-002` | medium | **closed** | dependency hash、effective override、artifact parent hash、identity completenessを定義。AC-06/19追加 |
| `PR66-DR-005` | medium | **closed** | junction/symlink再確認、file identity、no-clobber、atomic replace、target claimを定義。AC-14追加 |
| `P66-DR-005` | P2 | **open / partial** | solver/compile/qualityは分離されたが、品質合否が`volume_iou >= 0.95`単独で、元findingが要求した重要feature・寸法・許容誤差のgateがない |
| `PR66-DR-004` | medium | **open / partial** | 同じ品質欠陥class。既知modelの必要feature/寸法条件と、利用者targetを受け取る具体的CLI契約が未定義 |
| `PR66-DR-003` | medium | **open / partial** | topology/frameは修正されたが、元findingが要求したprofile/slice等の中間JSON schema versionとconsumer側version検査がない |
| `PR66-DR-006` | medium | **open / partial** | cleanup前のdiagnostics退避は追加されたが、元findingが要求した保持期間・明示clean対象・diagnostic ownershipの生命周期が未定義 |
| `P66-DR-006` | P2 / medium | **open** | 利用者追加要件の複数面PNGは未対応。Skill側はQuick=`iso一枚`のまま、AC-07もmultiを明示指定した場合の4枚生成に留まる |

## Open finding details

### `P66-DR-005` / P2 と `PR66-DR-004` / medium — 品質gateがvolume IoU単独

前回 `P66-DR-005` は、処理終了と要求品質合格を分離したうえで「対象・用途ごとの一致指標、重要寸法やfeature、許容誤差」を要求し、単一の高いIoUで小穴等を無視しないことをclosure条件とした。`PR66-DR-004`も初回対応modelの必要featureと許容誤差、利用者toleranceの入力場所を要求している。

現行runtime §8.4とAC-16/17は `volume_iou >= 0.95` を既定gateにし、solver／compile／metric／qualityを分離した点は修正済み。しかし、小体積の止まり穴・slot・counterbore等の重要featureが欠落しても全体volume IoUが0.95以上なら合格できる。既知stadium-slot fixtureのslot寸法・穴有無等の必須feature checkも定義されていない。また公開CLI表は`品質target`とだけ記載し、利用者が別targetを指定する具体的option名・値域・単位を定義していない。

**Required action:** 初回対応modelごとに、volume IoUに加えて保持必須featureと主要寸法、そのtoleranceを定義し、いずれか未達なら`quality_target_met=false`とする。stadium-slot等の既知fixtureで、IoUが閾値以上でも重要feature欠落なら失敗する反例をACへ追加する。利用者targetを許可するなら公開CLI optionとvalidationを具体化する。

### `PR66-DR-003` / medium — 中間artifactのschema version / consumer validationが未定義

元findingはframe・topologyに加えて「中間JSONのschema versionとconsumer側の検査」を要求した。現行runtimeは`result.json`に`schema_version: 1`を持つが、`profile`のtopology JSON、`slice`のfeature-map JSON等の中間artifact自体のschema名/versionと、consumerが対応versionを検査する契約は定義していない。

**Impact:** producer側のfieldやframe表現が変更された場合、古いconsumerが同じJSONを誤解釈して再構築へ進む経路を設計で排除できない。

**Required action:** profile/slice等のmachine-readable artifactにschema identifier/versionを持たせ、consumerは対応versionを検査し、未知versionを成功扱いしない。互換／非互換version fixtureをAC-16/17またはAC-19へ追加する。

### `PR66-DR-006` / medium — diagnosticsの保持・clean生命周期が未完

現行runtime §4.3は失敗・timeout時にhelper SCAD、stdout/stderr、manifest、途中成果物状態を`.openscad/runs/<run-id>/diagnostics/`へcleanup前に退避するため、前回の主要な調査不能経路は解消した。

ただし元findingは、保存できたものだけをmanifestへ列挙し「保持期限・明示cleanの対象」を決めることまで要求した。現行runtime／AC-13にはdiagnosticsをいつまで保持するか、`project clean`で削除可能か、run manifest上のownershipをどう扱うかがない。

**Required action:** diagnosticsをrun-owned artifactとしてmanifestへ関連付け、既定保持方針と明示clean時の対象／除外を定義する。成功run／失敗runのlog・diagnosticsが無期限に累積する設計にも、通常cleanで調査証拠を無条件削除する設計にもならないようACを追加する。

### `P66-DR-006` / P2 / medium — 複数面PNG要件が未対応

利用者追加要件に対して前回補遺で、形状確認用PNGの基本4方向、隠れるfeatureへの追加view、各featureと実閲覧画像の対応、一部未生成／未閲覧時の全体判定を要求した。

現行 `design/openscad-skill-design.md` はQuickの完了条件が依然として「iso一枚の確認」。runtimeの`--views multi`は生成可能だが、通常の形状確認でmultiを標準選択するroutingがなく、AC-07も`multi`を指定した場合の4枚生成のみ。背面・下面等で隠れるfeatureへの追加view規則もない。PR bodyも「必須8論点へ対応済み」としており、この後発findingをcurrent review stateへ反映していない。

**Required action:** 前回MV-01〜05をSkill §4.2/§6、runtime、ACへ反映する。形状確認を要求する通常Quick等では基本4方向を標準にし、必要featureが隠れる場合は背面・下面・追加斜視を選ぶ。利用者が単一viewやSTL-onlyを明示した場合はその限定を尊重する。

## Coverage

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| requirement / design conformance | `checked_finding` | P66-DR-005、PR66-DR-003/004/006、P66-DR-006 |
| correctness / edge cases | `checked_finding` | IoUで小feature欠落、artifact version mismatch、diagnostic lifecycle、hidden view |
| scope / unrelated changes | `checked_no_finding` | fix rangeはruntime、acceptance、follow-up reportのみ |
| changed files / direct dependencies | `checked_finding` | runtime↔acceptance↔unchanged Skill routingを照合 |
| API / data / compatibility | `checked_finding` | quality target CLI、intermediate schema version |
| error / diagnostics | `checked_finding` | warningはclosed、diagnostic retentionはpartial |
| security / secret handling | `checked_no_finding` | write target、same-file、junction、env dump契約は改善済み |
| validation adequacy | `checked_finding` | quality feature fixture、schema version fixture、diagnostic clean、multiview fixture不足 |
| current-HEAD CI | `checked_no_finding` | run `34024526920` head_sha=`38824e...`、success |
| report / tracking / documentation | `checked_finding` | follow-up reportは8論点のみ、PR bodyも後発P66-DR-006を未反映。canonical taskは広義には設計待ち状態を維持 |
| regression / maintainability | `checked_finding` | versioned intermediate artifactとdiagnostic lifecycleが未確定 |

## Validation

Reviewed HEAD `38824e11621b9dc09ead47cda73ff27c5fd5cdb0` と完全一致するpull_request run `34024526920`を確認した。

- conclusion: `success`
- build job: `101463021294` success
- repository Skill architecture / active-link validation: success
- existing ChatGPT worker ZIP build / verify: success
- artifact upload: success
- artifact: `9986611935` / `chatgpt-worker-skills-34024526920` / 18678 bytes
- digest: `sha256:91b08a30a88484c9fafb06f8061c1a43462207a333221fc5aa75d2e50d0e5992`

このCIはrepository文書・既存worker ZIPの検証であり、Windows OpenSCAD runtime、PNG閲覧、profile/SDF fixtureの実機受け入れ証拠ではない。Markdown lintはrepository配線不在によりunsupported。CodexSkill policyによりTDDはnot applicable。

## Verdict / next action

**fail**。source finding 12件中7件closed、5件open。open 5件は論理上4論点で、設計修正が必要。

次は同じfinding identityを保持してimplementation側へ戻す。修正後は同じnormal reviewerでfix verificationを継続する。独立最終reviewへ進めない。workerはmergeしない。

# PR #66 OpenSCAD設計review指摘対応 r2

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: #66
- Branch: `codex/openscad-windows-skill`
- Source fix-verification review: `PRR_kwDOSFr3-88AAAABMXhx-A`
- Reviewed design HEAD: `38824e11621b9dc09ead47cda73ff27c5fd5cdb0`
- Fix開始時current HEAD: `d04e76346b24239f002eb4a512fedfaf4623120e`
- Skill本体は未実装。今回も設計文書のみを修正した。
- `review/*`等の別branchは作成していない。

## Fix verificationでopenだったsource finding

前回fix verificationは12 source findingのうち7件closed、5件openと判定した。open 5件は論理上4論点であり、source finding identityを維持して対応した。

| Source finding | 状態 | 今回の対応 |
| --- | --- | --- |
| `P66-DR-005` / `PR66-DR-004` | 対応済み、再検証待ち | Reconstruct品質gateをvolume IoU単独から、volume IoU・主要bbox寸法・critical featureの複合gateへ変更。CLIに`--min-volume-iou`、`--dimension-tolerance-mm`、`--quality-spec`を定義し、値域を固定した |
| `PR66-DR-003` | 対応済み、再検証待ち | profile／feature-map／quality spec／view manifestへ`schema_id`と`schema_version`を定義し、consumerが未対応versionをbest-effortで読まずblockedにする契約を追加した |
| `PR66-DR-006` | 対応済み、再検証待ち | stable `project_id`、run ownership、既定30日のretention、`--retain-days 1..3650`、期限切れrunの所有者確認付きhousekeeping、明示cleanを定義した |
| `P66-DR-006` | 対応済み、再検証待ち | Quickを含む形状変更modeにiso/front/right/topの基本4方向verifyを要求。required／changed featureごとのview coverage、隠れfeatureの追加view、一枚失敗・未閲覧時にvisual passにしない集約規則を追加した |

## 変更内容

### `design/openscad-skill-design.md`

- 状態をfix verification対応中へ更新。
- `SKILL.md`共通契約へ基本4方向verifyとfeature coverageを追加。
- Quickの`iso一枚`を廃止し、Quick／Design／Refine／Modify／Replicate／Reconstructの完了条件へ基本4方向verifyを接続。
- required／changed featureと実閲覧viewの対応を`visual_feature_coverage`として保持する契約を追加。
- back／left／bottom／custom／section診断viewを、基本4方向で隠れるfeatureの追加確認手段として定義。
- required viewの生成失敗・破損・未閲覧、またはfeature未確認時は`visual_review=passed`にしない。

Commit: `03257ea1ae149eaeceaa59b0edce0b0f9b7e6708`

### `design/openscad-runtime-design.md`

- `optimize`公開CLIに次を定義。
  - `--min-volume-iou FLOAT`: `0 < value <= 1`、既定0.95。
  - `--dimension-tolerance-mm FLOAT`: 有限の`0 < value <= 1000`、既定0.20 mm。
  - `--quality-spec FILE`: `openscad.reconstruct-quality` schema v1。
- Reconstruct品質gateを次のAND条件へ変更。
  1. volume IoU target。
  2. bbox X/Y/Zの主要寸法target。
  3. required critical featureの全件target。
  4. unverified important featureが残らないこと。
- 小体積の穴／slotをIoUだけで落とさないため、利用者指定featureと解析・parameter化に用いた穴／slot／through opening等をrequired featureへ昇格する契約を追加。
- 中間artifact schemaを定義。
  - `openscad.profile` v1
  - `openscad.feature-map` v1
  - `openscad.reconstruct-quality` v1
  - `openscad.view-manifest` v1
- consumerはschema ID/versionをpayload読取前に検査し、unsupported versionはblocked／exit 3、必須field不正はexit 2とする。
- `project init`でstable project UUIDを作り、各runへproject ownershipを保存。
- run retention既定30日、`--retain-days 1..3650`を定義。
- housekeeping／`project clean --expired-runs`／`--run-id`はcurrent project所有、非active、path実体検査済みrunだけを削除対象にする。
- `render --views multi`をiso/front/right/topの基本viewとし、`--extra-view`を追加。

Commit: `9c15856463f6329ecf6d72008394e54095ced5b5`

### `design/openscad-acceptance-plan.md`

- AC-07へ基本4方向、隠れfeature追加view、feature-to-view coverage、一枚失敗／未閲覧時の集約条件を追加。
- AC-13へproject ID、30日retention、retain-days境界値、期限切れ／別project／active／不正runのclean fixtureを追加。
- AC-16へprofile／feature-map schema consumer fixtureと、IoUだけでは見逃せる小穴／slotをcritical feature gateで落とすfixtureを追加。
- AC-17へquality spec schema、CLI target値域、複合品質gateを追加。
- AC-19へ中間artifact schema互換性scenarioを追加。

Commit: `b2e016febabc743aeed6a81e2e858eb0de82f214`

## Validation

CodexSkill repository自身の保守なのでTDDは`not applicable`。今回もSkill実装、Windows OpenSCAD実行、PNG実閲覧、mesh／SDF実機受け入れは未実施であり、設計上の受け入れ条件を成功証拠として扱わない。

Technical fix HEAD `b2e016febabc743aeed6a81e2e858eb0de82f214`には、完全一致するpull_request workflow run `34025338159`があり、conclusionは`success`。

- build job: `101465187157`
- repository Skill architecture／active-link validation: success
- existing ChatGPT worker ZIP build／verify: success
- artifact upload: success
- artifact: `chatgpt-worker-skills-34025338159`
- artifact ID: `9986861924`
- size: 18678 bytes
- digest: `sha256:8dfa91290243502a5b93d9a3f233f65d8b977d724dbf5dd614ad65a53a339b45`

このreport追加によりPR HEADはtechnical fix HEADから進むため、最終publication判定ではreport commit後のcurrent HEADと`head_sha`が完全一致するrunだけを使用する。別SHAの上記runを最終current-HEAD CIとして代用しない。

## Remaining

- 同一normal reviewerによるsource finding 5件のfix verification。
- 上流assetをコピーする前の取り込み条件／notice確認。
- 利用者指示後のP66-I1〜I5実装。
- Windowsネイティブ上でのOpenSCAD、Codexによるverify PNG実閲覧、profile／slice／optimizeの実機受け入れ。
- workerはmergeしない。

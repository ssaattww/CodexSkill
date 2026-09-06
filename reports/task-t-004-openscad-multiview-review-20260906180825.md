# T-004 / PR #66 複数面PNGの追加レビュー

## 対象・範囲

- 作成日時: 2026-09-06 18:08:25 Asia/Tokyo
- Report type: review_report。通常設計レビューの利用者追加要件に対する補遺。
- Repository: `ssaattww/CodexSkill`
- PR: #66。Branch: `codex/openscad-windows-skill`。Base: `main`。
- Reviewed design HEAD: `4219753285b8813d68adade1353109ca26674c13`
- PR base SHA: `6507727986329e34e69da3680a00824eb1fbfe13`
- Reviewer identity: `pr66-design-review-current-chat`。同じ通常review chatを継続。設計・実装・指摘修正は行っておらず、独立最終レビューではない。
- 利用者追加要件: 「できればpngは複数面から見た、3dが理解できる画像にしたいですね。それもできていなければ指摘に追加してください。」
- 許可する書込: 本追加review report、PR #66コメントのみ。設計、Skill、script、workflow、task/phase、既存review reportは変更しない。mergeしない。
- 本追加範囲のverdict: `fail`（設計修正が必要）。追加指摘1件、`P66-DR-006` / P2 / medium / open。

元の[P66-DR-001〜005の報告](task-t-004-openscad-design-review-20260906174737.md)を置き換えず、ID・重要度・判定を変更しない。別に存在する`PR66-DR-001〜006`系列の[報告](task-t-004-pr66-design-review-20260906180147.md)ともIDを混同せず、本補遺では統合・再採番しない。今回の追加は利用者が明示した複数面PNG要件によるものであり、以前の全範囲レビューを再実施したものではない。

`cc9787604b2b3d6bfacaf714cf9485ec72ad0079`からreviewed HEADまでの変更は上記review report二つだけ。PNGに関係する3設計文書のblobは変わっていないことを確認した。本report自体を保存した後のHEADとCIはPRコメントへ別途記録し、保存前のCIを代用しない。

## 確認できた既存設計

| 対象 | 既存の内容 | 今回の判断 |
| --- | --- | --- |
| [runtime §3](../design/openscad-runtime-design.md) | `render --views iso`は1枚、`--views multi`はiso/front/right/topの4枚 | 複数方向の生成機能は設計済み。欠落とは指摘しない |
| [Skill §4.2](../design/openscad-skill-design.md) | Quickはiso一枚の確認。Designは複数view。その他は変更前後等の確認 | 形状確認を伴う全modeでmultiを選ぶ共通の完了条件にはなっていない |
| [Skill §6](../design/openscad-skill-design.md) | 複数方向のPNG、SCAD、meshを組み合わせる。画像未確認を分離 | 方針はあるが、必要な面の選択・遮蔽時の追加観察を具体化していない |
| [AC-07](../design/openscad-acceptance-plan.md) | 指定時の4枚生成、有効性・サイズ・向き、各PNGの実閲覧を確認 | CLIでmultiを指定しない通常依頼と、基本4方向から見えないfeatureの受け入れ条件がない |

参照blob: runtime `a842e92098ebc89392fb1c22759ac63499888869`、Skill `2fe5ecdd1264f4a92326f252d884a2c1345980d5`、acceptance `d17ba3f54abdd0a2d6b57128bdc7a171833614e3`。

Skill本体とCLIは未実装。実際に複数面PNGを生成・閲覧できたという証拠ではなく、設計の静的確認である。

## P66-DR-006 / P2 / 複数面による立体形状確認を完了条件へ反映する

**Origin:** 利用者の追加要件と現行設計の照合。既存の4方向生成案そのものを未設計とする指摘ではない。

**Location:** `design/openscad-skill-design.md` §4.2・§6、`design/openscad-runtime-design.md` §3・§7、`design/openscad-acceptance-plan.md` AC-02・03・07。実装時のmode referenceとCLI案内にも反映が必要。

**Description:** `--views multi`は設計済みだが、それを形状理解用PNGの標準として選ぶ規則がない。Quickは明示的にiso一枚で完了できる。さらに固定4方向に要求featureが写らない場合の追加view選択と、観察範囲不足時の完了判定が定義されていない。「複数画像を生成できる」と「依頼に必要な面を実際に見て立体形状を確認する」が分離したままである。

**Impact:** 通常の作成・修正・プレビュー依頼で一枚だけが返される、あるいは背面・下面等の未観察featureを確認済みとする経路が残る。画像枚数だけを増やしても、対象面を写して閲覧した証拠にはならない。これは設計上の不足であり、未実装CLIで発生済みの不具合とは主張しない。

### 必要な修正

1. 立体形状の確認用PNGを生成する場合は、既存の基本セット（isoの斜視、frontの正面、rightの右側面、topの上面）を標準とし、Quickを含む該当modeのrouting・完了条件へ接続する。利用者が一方向だけを明示した場合はその指定を尊重し、全体の複数面確認とは区別する。STLだけのExport依頼など、PNGを要求しない処理に画像生成を無条件追加しない。
2. 要求された穴・段差・突起・変更箇所が基本セットで隠れる場合は、背面・左側面・下面・追加斜視など、必要な面が見える視点を選ぶ。対象featureと観察画像の対応、追加理由を残す。外観画像で分からない内部形状は未確認とし、根拠なく不存在・適合を断定しない。断面等の追加手法を必要とする場合は、その可否と許可範囲を設計側で明示する。
3. 各PNGのview名、camera、projection、対象runとhashを追跡できるようにし、左右・前後の取り違え、同じ視点の重複、必要箇所の見切れを検出できる受け入れ例を定める。別PNGとして提供すればよく、一枚への画像合成や新しいviewerの実装は必須にしない。
4. 指定した画像を実際に開き、どの画像でどのfeatureを確認したかを報告する。要求された複数面の一部が生成失敗・未閲覧なら、複数面確認全体をpassedにしない。CLIの生成状態とSkillの視覚確認状態を分離し、生成済みだが未閲覧、未生成、確認不合格を区別する。
5. 最終成果物の確認に使う各viewは、既存`P66-DR-002`の要求どおりexportと同じ形状の評価条件に結び付ける。複数面化は同一形状の保証の代替ではない。

### 修正確認条件

| ID | 入力・状況 | 期待結果・証拠 |
| --- | --- | --- |
| MV-01 | Quick相当の単純部品について「作成してプレビュー」。CLIのmultiは利用者が明示しない | Skillが基本4方向を選択。異なるview名・camera、4枚の新規PNG、実閲覧と所見を記録。従来のiso一枚だけで複数面確認完了にしない |
| MV-02 | 幅・奥行・高さが異なり、上面に穴、正面に段差、右側面に突起を持つ既知の非対称fixture | 各featureがどのviewに写るかを期待値として定義し、向き、見切れ、重複viewを確認。四枚という枚数だけで合格にしない |
| MV-03 | 選定した基本4方向では隠れる背面の止まり穴・下面の凹部を確認する依頼 | 背面・下面等を追加し、要求featureの観察根拠を保存。観察不能なら未確認理由と完了できない範囲を記録。未観察を「穴なし」や確認済みにしない |
| MV-04 | 4枚のうち1枚の生成失敗、または画像tool不在・一部未閲覧 | 成功画像は保存するが、要求した複数面の視覚確認全体をpassedにしない。生成失敗と閲覧不能を別々に報告 |
| MV-05 | 「正面だけをPNGで」と「STLだけへ出力」の二つの明示限定依頼 | 前者は正面だけを生成し、複数面確認済みとはしない。後者には未依頼PNGを追加しない |

上表は新たに求める受け入れ条件であり、実行済みの検証結果ではない。構成・runtime・受け入れ文書と実装時referenceを同期させることがclosure条件である。

## 検証と未実施

- GitHub connectorでPR、対象文書、既存報告、changed files、snapshot間差分を確認した。
- 作業開始時に`.github/workflows/release-chatgpt-worker-skills.yml`を確認した。artifactは既存worker ZIPで、失敗時のstdout/stderr一式保存ではない。CodexSkillはRevMem向け診断artifact追加方針の対象外のため変更しない。
- Reviewed HEADとrunの`head_sha`が完全一致する[run 34023679173](https://github.com/ssaattww/CodexSkill/actions/runs/34023679173)、attempt 1、pull_request、conclusion successを確認。
- Build job `101460759835`: repository validator、既存worker ZIP build/verify、artifact uploadがsuccess。release系jobはskipped。
- Artifact `9986340979` / `chatgpt-worker-skills-34023679173` / 18678 bytes / expired=false。Digest: `sha256:56ea813231488b7a9c870e718b307eb957dbc4a6e9cff54ce2c2b1f6d1a09978`。metadataのみ確認し、bytes再展開は行っていない。
- Windows OpenSCAD、PNG生成、Codexによる実画像確認、MV-01〜05はnot_run。既存CI成功をこれらの成功証拠にしない。
- Markdown lintはこの補遺で実行していない。TDDはAGENTS.mdによりnot_applicable。
- 本report保存後のpublication HEADとmatching CIは保存前には未確定。PRコメントで確認結果を記録する。

## Coverage・継続情報

| 観点 | Disposition | 根拠 |
| --- | --- | --- |
| 追加要求・設計整合、視点と遮蔽、API・結果・AC | checked_finding | P66-DR-006、MV-01〜05 |
| 対象差分・scope・既存finding継続 | checked_no_finding | 既存P66系列のIDと重要度を維持。設計・実装は無変更。既存報告を上書きしない |
| current-HEAD CI | checked_no_finding | 4219753とrun 34023679173のhead_sha一致 |
| Windows・画像の実機検証 | unexplored | 未実装・設計レビュー範囲。形状認識の動作保証は出さない |
| 他機能の再レビュー・旧指摘のclosure・独立最終review | not_applicable | 今回の依頼は複数面PNGの条件付き指摘追加のみ |

残リスク: 基本4方向だけでは要求featureが見えない形状がある。画像所見だけで内部形状や製造品質を保証しない。対応する実機ACは後続実装で必要。

次の作業: 実装担当へP66-DR-006を渡し、設計とACを同期する。今回のreport保存は設計修正の実施・承認や実装開始の許可を意味しない。既存P66-DR-001〜005の修正確認は別途必要。workerはmergeしない。

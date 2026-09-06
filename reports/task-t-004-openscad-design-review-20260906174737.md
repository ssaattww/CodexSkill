# T-004 / PR #66 設計レビュー

## 対象と判定

- Repository: `ssaattww/CodexSkill`
- PR: #66
- Review mode: normal initial design review。独立最終レビューではない。
- Reviewer identity: `pr66-design-review-current-chat`
- Reviewed design HEAD: `cc9787604b2b3d6bfacaf714cf9485ec72ad0079`
- Base: `6507727986329e34e69da3680a00824eb1fbfe13`
- Reviewed changes: 11 files。
- この報告のファイル名の日時は、確認済みPR snapshotの更新日時 `2026-09-06T08:47:37Z`（日本時間17:47:37）を識別子として使用している。報告commitの作成日時や実機試験日時を表さない。
- Verdict: **changes_requested**。必須指摘5件。P1が2件、P2が3件。
- 本レビューは設計契約を対象とする。未実装であること、Windows受け入れが未実施であること自体を不具合として数えていない。
- 設計・実装の修正、依存packageの導入、workflow変更、mergeは行わない。今回のrepository変更はこのレビュー報告のみ。

レビュー開始時のHEADは `8bf9d0e2d94464285044a866f447e5540e7f533c`。途中で追加されたREADME、二つのhierarchy設計、overview reportを含め、上記 `cc978760` snapshotへレビュー対象を更新した。3つのOpenSCAD設計文書はこの間変更されていない。後続HEADへこの判定やCI成功を自動的に転用しない。

本レビューは設計作成・修正を行っていない通常レビューである。実装者の独立最終レビューや、別のfresh reviewerによる承認を代行するものではない。

## 重要度

- P1: 正常扱いされた成果物や検証証拠が、依頼した形状を表さない経路を防ぐための必須設計修正。
- P2: 移植・再構築の結果を一意に実装・受け入れできるようにするための必須設計修正。
- 今回の指摘はすべて未解決。実装を変更していないため、修正確認の合格を表明しない。

## 指摘一覧

| ID | 重要度 | 論点 | 主な対象 |
| --- | --- | --- | --- |
| P66-DR-001 | P1 | warning policyの合否規則が未定義 | runtime §8.1、acceptance AC-08 |
| P66-DR-002 | P1 | 検証PNGとexport形状の評価条件を一致させる契約がない | runtime §3・§7・§8.2、acceptance AC-07・10 |
| P66-DR-003 | P2 | profile抽出の穴・複数成分保持が移植契約とACにない | runtime §3、skill §7、acceptance AC-16 |
| P66-DR-004 | P2 | 解析座標から原座標へ戻す契約がない | runtime §3・§8.2・§8.3、acceptance AC-16・17 |
| P66-DR-005 | P2 | 再構築・最適化の形状品質に合否基準がない | acceptance AC-16・17、runtime §8.3 |

## P66-DR-001: warning policyの合否規則を定義する

### 根拠

`design/openscad-runtime-design.md` §8.1はvalidate成功を「compile、warning policy、今回の非空出力確認」と定義する。しかし、warning policyで何を不合格にするか、既知の警告・未知の警告をどう扱うかが定義されていない。§7は安定したcategoryと終了コードを要求するが、警告からcheck／status／exit codeへの対応を補っていない。

AC-08は未定義module・存在しないincludeを異常系に挙げる一方、「必須validationが失敗した場合は非0」としており、それらを必ずvalidation失敗にする判定基準がない。

### 問題になる入力

```scad
cube([10, 10, 10]);
missing_feature();
```

全体が空になる例だけでは、別の正常な形状が残ったままfeatureが欠落する経路を検出できない。終了値と非空STLだけでは、必要なmoduleやincludeが評価され、要求形状が完成したことの証拠にはならない。

本指摘は「warning policy」という未定義の判定契約に対するもの。Windows版で上記fixtureを実行済みとは主張しない。

### 影響

実装者ごとに警告を無視する、全警告で停止する、特定文字列だけを検出する等の判断が分かれる。欠落したfeatureを持つSTLを成功成果物として扱うことを、現在のACでは確実に排除できない。

### 必要な修正

少なくとも、未解決include／use、未定義module等の形状欠落につながる診断について、fatal／非fatalの既定分類を定義する。未知診断の扱い、例外を許可する場合の明示手段、`checks`・`status`・終了コードの対応も一つの正本に定める。render／validate／exportで判定が分岐しないようにする。

### 修正確認条件

正常形状だけのfixtureに加え、正常cubeに未定義moduleまたは欠落includeを併置したfixtureを用意する。子processの終了値、標準出力、標準エラー、生成物の有無を保存し、欠落featureを伴う実行がCLI全体のsuccess／exit 0にならないことを確認する。意図的に許可する非fatal診断がある場合は、別fixtureで許可条件を検証する。対応する設計とAC-08を同時更新する。

## P66-DR-002: 検証PNGとexport形状の評価条件を一致させる

### 根拠

runtime §3は`render`でPNG、`export`でSTL／3MF／PNGを生成する。§7はPNGを実際に見た証拠をrun ID・画像hash・所見で残すが、PNGがexportと同じOpenSCAD評価条件で生成されたことを要求していない。§8.2は比較overlayのpreview利用を定めるだけで、通常の形状検証用PNGとpreview画像の区別がない。

AC-07はPNGの有効性、サイズ、方向、実際の閲覧を確認する。これだけでは、閲覧した形状と出力した形状が同じであることを判定できない。

### 問題になる入力

```scad
if ($preview)
    cube([10, 10, 10]);
else
    cube([20, 10, 10]);
```

previewと最終出力で評価条件を変えるモデルについて、画像を確実に開いたという証拠と、最終出力形状を確認したという証拠は異なる。同じSCAD pathや同じrun IDだけではこの違いを除けない。分割数等をpreview時だけ下げるモデルでも同じ区別が必要になる。

### 影響

画像確認そのものは成功していても、検証対象のSTL／3MFとは違う形状を見て合格とする経路が残る。PNG生成と画像閲覧を分離しただけでは解決しない。

### 必要な修正

最終成果物の確認に使うPNGについて、入力source・依存file・parameter override・評価mode・必要な品質設定をexport側と一致させる契約を定める。探索用previewやoverlayは別の画像種別として保持し、それだけで最終成果物の視覚確認を合格にしない。manifestには実際に適用した評価modeを記録し、画像所見がどの成果物条件を確認したものか追えるようにする。

### 修正確認条件

上記のようにpreview時と最終評価時で外形が変わるfixtureをACへ追加する。探索用PNGと最終形状検証用PNGを区別できること、STL／3MFと異なる評価条件のPNGだけでは最終形状の視覚確認を合格にしないことを確認する。overlayの背景modifierのためにpreviewを用いる既存設計は維持し、通常の最終形状検証とは分離する。

## P66-DR-003: profile抽出の穴・複数成分を保持する契約を追加する

### 根拠

固定上流commit `c47ef2359a3329da45c3c2e6caa3c286133c2844` の `scripts/openscad-profile-extract.py` は、`segments_to_polygons()`でpolygonizeの生成polygonを返し、`detect_extrusion_axis()`や`extract_dominant_profile()`でそれらを`unary_union()`する。内周と外周から生成される領域を材料／空洞として分類せずに全てunionする構造である。

また、`polygon_to_scad()`とその呼出元は`.exterior`／`.interiors`を持つ単一Polygonを前提にしている。複数の独立した断面を扱う方針は明示されていない。

PRの移行一覧U-01〜U-09にはこの論点がなく、runtimeのprofile契約とAC-16にも、穴・独立成分を保持すること、または未対応として拒否することの明記がない。有限sliceによる見落としの注意はあるが、観測できた断面の空洞を出力過程で埋める問題とは別である。

### 影響

上流処理を入出力・Windows対応だけ変更して移植すると、抽出された輪郭が存在しているにもかかわらず穴のない断面を生成する、または複数成分で想定外の例外となる可能性がある。これはslice密度を増やしても直らない欠陥classである。

### 必要な修正

断面の外周・内周・入れ子・独立成分の表現とSCADへの変換規則を定める。対応範囲外のtopologyを扱えない場合は、明示した非成功結果を返し、黙って穴を埋めたり最大成分だけを残したりしない。上流移行の処置とprofile成果物schema、AC-16へ反映する。

### 修正確認条件

外側10×10 mm、内側4×4 mmの角穴を持つ一定断面を高さ10 mm押し出したfixtureを用いる。断面の材料面積は84 mm²、体積は840 mm³であり、SCAD再出力後も穴1個が保持されることを、事前に定めた許容誤差で確認する。

独立した2×2 mm正方形を二つ持つ断面も追加する。両成分を保持するか、設計で宣言したunsupportedとして非成功終了することを確認し、片方だけを成功成果物にしない。これらは新規の検証用fixture案であり、実行済みの数値ではない。

## P66-DR-004: 解析座標と原座標の往復契約を定義する

### 根拠

runtimeのprofileはaxis選択理由を、sliceは軸・位置・contourを、optimizeはparameter・sampled IoU等を返す。しかし、これらが入力STLの座標、OBB等による正規化座標、断面の二次元座標のどれに属するかを定めていない。

上流profile処理はOBB変換`T`を求め、変換後のmeshを解析する。`mesh_multiplane()`が返す平面変換を捨て、`generate_scad()`では入力axisをコメントに使いながら常にZ方向へ`linear_extrude()`する。元の位置・向きへ戻す変換は出力されない。

上流stadium-slot SDFもXY中心・Z基準を固定したモデルで、parameter一覧に入力meshの姿勢・平行移動はない。PRは同modelを初回end-to-end候補とするが、受け付ける姿勢の制限や変換の扱いを定めていない。

一方、compareは同じ座標・単位で比較し、無断center合わせやscale変更を禁止している。このため、解析側で失われた位置・向きを比較側で黙って補正することもできない。

### 影響

原点以外にある形状、Z以外の軸の押出形状、回転された形状について、形が近くても配置が違うSCADを出力する、あるいはSDFが対象と重ならない状態で最適化する経路が残る。

### 必要な修正

入力座標から解析座標、解析座標から断面座標への変換と逆変換、軸方向の基準位置、単位をschemaへ定義する。内部解析のために正規化する場合は、生成SCADを原座標へ戻して比較する。元mesh自体を位置合わせ・scale変更する操作は、既存設計どおり承認と別runを必要とする。

初回実装で任意姿勢を扱わない判断も可能だが、その場合は対応する入力姿勢と検出・拒否条件を明記し、未対応入力を成功にしない。

### 修正確認条件

10×20×30 mmの非立方体の直方体に回転と平行移動を与えたfixtureを使う。対応する場合は、生成SCADを再exportして原STLと無変換で比較し、元の位置・向き・寸法が保存されることを確認する。姿勢を制限する場合は、非対応姿勢を診断付きで拒否する。SDF経路についても、原点配置だけでなく平行移動した対応形状を入力し、宣言した方針が成立することを確認する。

## P66-DR-005: 再構築・最適化の品質に合否基準を設ける

### 根拠

AC-16はprofile、三軸slice、feature map、parameter化SCAD、export mesh比較の証拠を要求する。AC-17はseed、sample数、bounds、solver status、SCAD生成と別mesh比較を要求する。しかし、どの品質なら再構築として合格するのか、低い一致率を得た場合に全体statusをどうするかがない。

runtime §8.3もmesh再検証までは要求するが、比較を実行したことと形状一致を満たしたことを区別する判定契約がない。単純boxやcompare自身にはAC-06・11で許容誤差があるため、再構築の受け入れだけが証拠の存在確認で終わっている。

### 影響

solverが収束した、SCADがcompileした、volume IoUの数値を保存した、という条件は、得られた形状が依頼を満たすことを保証しない。低いIoUや重要な穴の欠落が残った候補でも、現在のACの記載事項を全て保存できてしまう。

### 必要な修正

処理が終了したことと要求品質に合格したことを分ける。対象・用途ごとに必要な一致指標、重要寸法やfeature、許容誤差を決め、満たさない場合の`checks`／overall statusを定義する。単一の高いIoUだけで重要な小穴を無視しない。任意モデルに一律の製造品質保証を付ける必要はない。

### 修正確認条件

profile経路と初回対応stadium-slot経路に、既知の正解SCADから作ったSTLの正常fixtureを少なくとも一件ずつ定義する。期待するfeature・寸法・mesh比較値と許容誤差を明記する。さらに意図的に一致しない候補を与え、compile成功・solver終了・metric保存だけでtask全体が成功しないことを確認する。品質不足の候補は診断用に保存しても完成品と表示しない。

## Coverage

| 対象 | 確認範囲 | 結果 |
| --- | --- | --- |
| OpenSCAD Skill構成設計 | 1 Skillへの分割、8 mode、reference routing、所有責務、上流移行、配布 | 読込分離・開発lifecycle非複製は定義済み。移行欠落をDR-003・004に記録 |
| runtime設計 | CLI、path、process、依存、project、schema、validation、比較、再構築 | DR-001〜005 |
| acceptance plan | D-01〜06、AC-01〜20、段階別の部分確認／最終合格の区別 | 機能未実施と設計完了は区別済み。DRに対応するAC補強が必要 |
| tasks/tasks-status.md | T-004、P66-D／I1〜I5、既存taskへの差分 | 追加範囲を確認。実装待ちの状態を維持 |
| tasks/phases-status.md | Phase 9、既存phaseへの差分 | 追加範囲を確認 |
| README.md | 入口、workflow/domain区分、Refine説明、未実装表示、リンク | 未実装Skillを利用可能とは表示していない |
| 2つのhierarchy設計 | domain層、責務、配布境界、README同期、既存review lifecycle | 両方のblobは `36a14ff9b2f47049a6127b6d5f0f7029562b339e` で同一 |
| 初回設計report | 要求、scope、検証範囲、snapshot／publication区別 | 過去snapshotのCIとして記載。Windows成功証拠にはしていない |
| overview report | 追加要求、hierarchy同期、README、snapshot CI | 過去snapshotとして区別 |
| handoff YAML | authority、非目標、書込境界、snapshot、raw report、次の操作 | 実装承認を自動移譲しない。記録は保存前snapshotと明記 |
| 既存workflow | HEAD checkout、validator、ZIP、artifact | ZIP artifactのみ。RevMem向け診断追加を本repositoryへ適用しない |
| 上流固定commit | tree、profile抽出、SDF最適化、既知の移行問題との照合 | 静的読解。上流欠陥をそのままPR実装の再現済み不具合とは扱わない |

## 検証証拠と限界

### 確認済みdesign HEADのCI

- HEAD: `cc9787604b2b3d6bfacaf714cf9485ec72ad0079`
- Workflow run: `34022791270`
- Event: `pull_request`
- Run head_sha: `cc9787604b2b3d6bfacaf714cf9485ec72ad0079`
- Attempt: 1
- Conclusion: success
- Build job: `101458336910`、success
- repository validator、既存ChatGPT worker ZIP build／verify、artifact uploadがsuccess。
- release関連jobはskipped。
- Artifact: `9986053406` / `chatgpt-worker-skills-34022791270` / 18678 bytes。
- Digest: `sha256:e940e5d0c11895603b66d8dc017fa06443d7878318dd4bd08a8b039c7530e4b0`
- 確認はrun／job／artifact metadata。ZIP bytesの再展開は実施証拠に含めない。

このCIはrepository構造と既存Skill ZIPの検証であり、OpenSCAD runtimeや今回の反例fixtureの成功・失敗を示すものではない。本report保存後のHEADにこのCIを転用しない。

### 未実施・未確認

- WindowsネイティブでのOpenSCAD／Python／Codex実機検証は未実施。
- 本報告のfixtureと期待値は修正確認の具体案。PRの新CLIは未実装であり、新CLIに対する実行結果ではない。
- 以前の作業中説明には手元OpenSCADの再現に言及したものがあるが、本報告には対応ログを照合した実行証拠を収録していない。そのため、当該説明をWindowsの実証、またはPRの実装テスト成功として使わない。
- Markdown lintは既存のrepository配線がないためunsupported。lint／test／workflowを追加していない。
- 上流の正式なlicense条件・notice確認、Windowsの具体的version組、empty booleanのversion別動作は既存計画の未確定事項として維持。今回新たな実装不具合として重複計上しない。
- review中に到着していない、または取得結果を照合できていない後続HEADの変更・CIは判定対象外。

## 後続の修正確認

P66-DR-001〜005を固定IDとして、対応する設計変更、AC変更、修正commit、検証結果を対応付ける。未実装段階では設計記載を修正したことと実機でACを満たしたことを分ける。同一指摘への修正確認では元の原因・影響範囲・同一欠陥classを確認し、本報告の指摘を隠したり別番号へ置き換えたりしない。

## 参照

- [レビュー対象PR](https://github.com/ssaattww/CodexSkill/pull/66)
- [Skill構成設計](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/openscad-skill-design.md)
- [runtime設計](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/openscad-runtime-design.md)
- [受け入れ計画](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/openscad-acceptance-plan.md)
- [上流profile抽出](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-profile-extract.py)
- [上流SDF最適化](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-sdf-optimize.py)
- [reviewed HEADのCI](https://github.com/ssaattww/CodexSkill/actions/runs/34022791270)

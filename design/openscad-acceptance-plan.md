# OpenSCAD Skill受け入れ・実装計画

## 1. 状態と正本

2026-09-06作成。PR #66は設計から実装まで一つのDraft PRとして継続する。今回は設計だけを行い、以下の実装受け入れ条件はすべて未実施である。設計文書が存在することを実装の成功と扱わない。

- 構成・読込・mode責務: [OpenSCAD Skill設計](openscad-skill-design.md)
- CLI・Windows・結果schema: [実行基盤設計](openscad-runtime-design.md)
- canonical tracking: `tasks/tasks-status.md`と`tasks/phases-status.md`

仕様の重複を避けるため、本書は上記契約に対する入力例・期待結果・証拠を定義する。契約変更時は対応ACを同じ論理commitで更新する。

## 2. 設計段階の完了条件

| ID | 条件 |
| --- | --- |
| D-01 | 詳細設計に先立ってPRを作成し、実装後まで同じPRを使うことが明示されている |
| D-02 | `SKILL.md`、mode別reference、共通知識、script、template、evalの責務と読込条件が定義されている |
| D-03 | Windowsネイティブ、Python必須化、依存能力別判定、非破壊性、エラーと画像未確認の区別が定義されている |
| D-04 | 上流の実在fileと説明の不整合を区別し、流用・修正・除外と根拠が追跡できる |
| D-05 | 実装受け入れ例、作業順序、未検証・未確定事項が具体化されている |
| D-06 | 文書・tracking・詳細reportを保存し、current HEADに対するCI結果または不在をPRコメントへ記録する |

設計ドラフト提出後は利用者へ説明する。設計reviewのrequired findingが収束する前にSkill本体やhelperの実装を開始しない。設計完了と実装完了・merge readinessは別状態とする。

## 3. Skill分割の受け入れ条件

### AC-01: 一つのinstallable Skillと可搬性

`skills/openscad/`だけを、空白・日本語を含むWindowsユーザーの`.agents/skills/openscad/`またはprojectの`.agents/skills/openscad/`へcopyする。repository本体や他の開発workflow Skillを配置しない状態で、Codexが`openscad`を認識し、`help`と対応commandを起動できること。

Skill内部にsymlink、repository外shared file参照、実行に必須な`.claude`固定pathがないこと。利用者が同名Skillを二重installした場合は一方を自動削除せず、選択したSkillの実体pathを確認できること。`agents/openai.yaml`がない構成でも基本動作を成立させる。

### AC-02: 必要な手順だけを読む

`SKILL.md`は設計上の上限200物理行以内とし、Goal、Execution owner、Inputs、Outputs、Completion condition、mode routing、共通禁止事項を省かない。長文を1行へ押し込めて上限を回避しない。

次の入力で、モデルが実際に読んだ文書pathと選択modeをセッションの検証記録へ残す。

| 入力例 | 必須読込 | 原則として読まないもの |
| --- | --- | --- |
| 「外径20、内径6、高さ5 mmのスペーサーを作ってプレビュー」 | SKILL、modelingのQuick節、必要なmodeling rules／CLI | reconstruct、SDF、写真再現、未使用template |
| 「このSCADをSTLへ出力」 | SKILL、validate-exportのExport節、必要なCLI | modeling、STL再構築、言語reference全文 |
| 「このSTLへ直径4 mmの穴を追加」 | SKILL、modify-stl、必要なvalidation／CLI | パラメトリック化が不要ならreconstruct |
| 「このSTLを寸法変更できるSCADへ再構築」 | SKILL、reconstruct-stl、必要なtechniques／CLI | 写真がなければreplicate-image |

すべてのreferenceはSKILLから直接到達でき、必読document欠落時はそのmodeをblockedにする。referenceを全件一括読込する指示を置かない。モデルの読込挙動はprompt指示だけで保証されたとせず、実際のCodexセッションで確認する。

### AC-03: 八つのmodeと境界

Quick、Modify、Design、Replicate、Reconstruct、Refine、Export、Analyzeそれぞれについて一件以上の入力・mode選択・必要file読込・成果物・未確認項目を記録する。Quickが安全に仮定できない嵌合寸法を発明しないこと、Modifyが不要な全面再構築を始めないこと、Refineが依頼外の部分を変更しないこと、Exportが新規設計を始めないことを含める。

「寸法が不明な軸の圧入部を今すぐ作って」のような例では、未知寸法を実測値として埋めない。「再構築不要、穴だけ追加」という指示をReconstructで処理しない。追加作業や外部library installを無断で行わない。

## 4. Windowsと基本機能の受け入れ条件

### AC-04: バイナリ探索と依存分離

`C:\Program Files\OpenSCAD\openscad.com`のような空白付き実行ファイルを明示指定し、version、成功時と失敗時の終了値、stdout、stderr、終了待ちを確認する。明示指定が存在しないとき、PATHに別OpenSCADがあっても黙って切り替えずexit 3となること。

NumPy／trimesh／SciPyが未導入でも、標準libraryだけのhelp、project管理、OpenSCADを使う基本render／exportが動くこと。mesh commandだけが不足packageを示してblockedとなり、pip、winget、PATH変更、sandbox緩和を自動実行しないこと。

### AC-05: パスと引数

workspaceを`C:\work\試作 部品\O'Brien`とし、そこからSCAD、STL、PNG、JSONを扱う。入力pathをPython sourceへ埋め込まず、directoryを誤分割しないこと。文字列parameterに空白、apostrophe、double quote、backslashを含めても意図した`-D`値がOpenSCADへ届くこと。Windows file名に使えないdouble quoteをfile名の正常系には使わない。

既存`OPENSCADPATH`が`C:\libA;D:\libB`の場合、両方とSkill側のlibraryを探索できること。親processやOSの永続環境変数を変更しないこと。Unixの`:`連結がWindowsに残っていないこと。PowerShellの実行例を記載するversionごとに実行し、PowerShell 5.1／7で異なるquoteを未検証のまま同一と表明しないこと。

### AC-06: パラメーター、基本形状、shape identity

独自に生成したbox fixtureを幅10、奥行20、高さ30 mmとする。STLのbboxは10／20／30 mm、体積計測を実施する場合の体積は6000 mm3となること。`--define width=12`ではbboxが12／20／30 mm、体積が7200 mm3となり、source fileは変更されないこと。

fixtureの座標・bbox許容誤差は0.01 mm、体積の相対許容誤差は0.1%とする。これは検証用単純形状の基準であり、任意モデルや実際の印刷精度の保証値ではない。結果には適用したtoleranceを保存する。

root SCADを変えず、`include`先だけ変更するfixture、`--define width=10`と`width=12`のfixtureを用意する。resultの`source_identity`が依存hashとeffective overrideの差を検出すること。`width=12`でexportしたSTLのartifact hashを`analyze`へ渡した場合はそのartifact identityを継承し、default `width=10`のsource analysis結果を同一candidateの証拠として結合しないこと。動的依存でclosureが確定できない場合は`identity_complete=false`となり、cross-command同一性を成功扱いしないこと。

### AC-07: PNG、評価条件、複数面visual coverage

形状を新規作成または変更するQuick／Design／Refine／Modify／Replicate／Reconstructでは、最終verifyとしてiso／front／right／topの4枚を生成する。fileが新runのものか、非空か、PNGとして有効か、指定sizeかを確認する。非対称fixtureを使いfrontとrightの取り違えも検出する。

`$preview`で形状寸法が変わるfixtureを用意し、例えば`$preview ? 10 : 20`でX寸法を切り替える。`render --purpose explore`がpreview評価を使う構成ではX=10の探索画像を許可する一方、`render --purpose verify`と`export --format all`の最終PNG、STL、3MFは`$preview=false`のX=20を同じsource identityとoverrideで評価すること。探索画像を最終形状確認済みとして扱わず、resultに`evaluation_mode`を保存すること。

基本4方向では見えない背面・下面featureを持つfixtureを用意し、`back`または`bottom`等の追加viewを要求する。required／changed featureごとに`feature_id`、期待状態、確認view ID、画像hash、実閲覧状態、所見を`visual_feature_coverage`へ記録する。各featureが少なくとも一つの実閲覧verify viewで確認されること。内部featureでsection診断viewを使う場合はfinal geometryと別artifact IDにし、生成方法とsource identityを残す。

Codexがrequired verify PNGを実際に開き、図形の向き、穴、slot等について所見を返す。一枚でもrequired viewが生成失敗、破損、未閲覧なら`visual_review=passed`にしない。画像tool不在なら`unavailable`、要求と矛盾する場合は`failed`とし、数値検証成功で上書きしない。Export単独でvisual確認が要求されていない場合は無条件に4枚要求しない。

### AC-08: warning、異常、古い成果物

正常SCAD、括弧欠落、未定義module、空形状、存在しないinclude、renderer異常終了を与える。未定義moduleまたは欠落includeと正常cubeを同居させ、OpenSCAD自体がexit 0かつ非空STLを作るversionでもvalidationが成功しないことを確認する。対応versionで`--hardwarnings`を使う場合は非0になること、diagnostic分類で代替する場合はblocking warningとして`checks.compile=failed`／exit 5になることを確認する。unknown warningを`Category: OK`へ落とさないこと。

warning allowlistを実装する場合は、category、OpenSCAD version、形状意味論を損なわない根拠をfixtureとともに固定する。利用者入力だけで任意warningを無視できないこと。

前runの有効STL／PNGが同じprojectにあっても、今回の失敗を成功にしない。stdout／stderr、command、入力hash、source identity、今回の生成物を追跡できること。破損または途中までのSTL、NaN座標、ASCII／binaryの区別も含める。

### AC-09: 検証範囲を誇張しない

bboxとassertだけが成功したfixtureに対して、局所壁厚全域、overhang、耐荷重、実際のprint fitまで合格と表示しないこと。ユーザーが必須にした検証が未提供なら、その項目と完了不能理由を返すこと。

「プリンター未校正」のprofileで嵌合部を作る例では、既定clearanceと実測値を区別する。実測値が入力されていないのに`profile_measured=true`へ変更しないこと。

### AC-10: 複数formatの部分失敗と最終評価条件

`export --format all`を実行し、STLだけ成功、3MF失敗、verify PNG成功という状況を再現する。成功したfileは残し、overallはpartial／exit 6とする。3MF未対応が事前判明した場合はblocked／exit 3とし、allをSTLだけに勝手に変更しない。

STL／3MF／verify PNGは同じsource identity、dependency closure、`-D` override、`$preview=false`条件で評価する。`$preview`分岐fixtureで、STLがX=20なのに最終PNGだけX=10となる構成を合格にしない。このfixtureを実行したOpenSCAD version、format capabilityとlogを保存する。過去の上流評価結果を今回の成功証拠にはしない。

## 5. 解析・失敗処理の受け入れ条件

### AC-11: 数値比較の定義

Aを10 mm立方体とし、Bを次のように与える。表のIoUは設計上の数学的期待値であり実測結果ではない。

| B | 期待するvolume IoU | missing／extra volume |
| --- | --- | --- |
| Aと同形・同位置 | 1 | 0／0 mm3 |
| AをXに5 mm移動 | 1/3 | 500／500 mm3 |
| Aと完全に離れた同サイズcube | 0 | 1000／1000 mm3 |

単純fixtureのIoU絶対誤差は0.001以内とする。ASCIIとbinaryで同じ形状を表現した場合も比較できること。bboxが同じでも内部穴が異なるfixtureでIoUが1未満となること。比較時に無断でcenter合わせしないこと。

差分生成を途中で失敗させた場合、差分fileを消した場合、破損fileを作った場合は、emptyと解釈せずmetric=nullと理由を返すこと。正当な空差分は実バイナリのempty-result応答と入力検証を記録して認定すること。

### AC-12: 数値比較と画像の独立

PNG生成が利用不能でも`compare`の数値経路は実行する。`--images`を要求していなければ数値比較だけの完了を許可し、視覚比較まで済んだとは表示しない。images要求時は画像失敗をpartialとして保持する。

overlayと差分画像は同じcameraとframingを使う。AとBをそれぞれ別々にautocenterして位置誤差を隠さない。rendererの背景modifierが効くモードを使って両形状が比較画像に存在することを確認する。

### AC-13: timeout、diagnostics ownership、retention lifecycle

子processがstdout／stderrへ別々の識別文字列を出して停止しないfixtureでtimeoutを発生させる。非0終了、timeout分類、両log保存、自分の子tree終了を確認する。別途起動した無関係なGUI/processが停止しないこと。

実行中にhelper SCADと途中成果物を作らせたうえでtimeoutまたは異常終了させる。cleanup前に`.openscad/runs/<run-id>/diagnostics/`へhelper SCAD、入力manifest、stdout／stderr、途中成果物の存在状態・hashを退避し、通常temp cleanup後にもそれらを開けること。退避後にephemeral tempだけが削除されること。診断退避自体をaccess deniedで失敗させた場合は、存在しないpathを示さず保存失敗をresultへ記録すること。全環境変数やtokenを診断へdumpしない。

`project init`でstable `project_id`を作り、run resultが同じID、`run_id`、retention情報を持つこと。既定`--retain-days 30`で完了runの`retention_until`が30日後となること。`--retain-days 1`と`3650`を受理し、0、負数、3651をexit 2で拒否すること。

期限切れのcurrent project所有run、期限内run、別project IDのrun、manifest欠落run、active runを同じrun rootへ置く。自動housekeepingと`project clean --expired-runs --apply --yes`が期限切れかつ所有確認済みの完了runだけを削除し、他は残すこと。`project clean --run-id ID`は同projectの非active runだけを明示削除できること。junction／symlinkでrun root外を指すものを削除しないこと。

### AC-14: projectの非破壊性、path実体、同時run

`project init`の二重実行、`../outside`、絶対pathをnameに指定、`CON`等の予約名を確認する。既存sourceやprofileを変更しないこと。通常output cleanはmanifest外file、入力STL、source、profile、run diagnosticsを消さないこと。

出力directoryにworkspace外へ向くjunction／symlinkを置いたケースを確認し、外部fileに変更がないこと。入力STLと出力先が別表記だが同じfile identityになるケースを拒否すること。既存同名成果物がある場合は既定でblockedとなり、明示replace時だけrun固有stagingの検証後にatomic replaceすること。入力source／STL／profileをreplace対象にできないこと。

同じfinal output名へ二つのrunを同時実行し、一方だけがtarget claimを取得すること。もう一方は待機またはblockedと明示され、相互にtemp／result／最終成果物を上書きしないこと。publish直前にもjunction／symlinkとfile identityを再確認すること。workspace外の出力は、単にCLIでpathが指定されただけでsandboxを解除してよいとは解釈しない。

### AC-15: templateとprinter profile

Skill directoryをread-onlyにして新規projectを作る。必要なlibrary／profileだけがprojectへcopyされ、測定値をproject側へ保存できること。Skill側のhashは変わらないこと。

生成sourceの必要な依存fileを揃えたprojectを別directoryへ移し、OpenSCADで再exportできること。既存の外部依存を無断でcopyしないケースでは、その依存条件とhashをmanifestに記録すること。

### AC-16: profile topology、schema、座標frame、再構築品質

profile抽出、三軸slice、feature map、parameter化したSCAD、export mesh比較の証拠を残す。入力の形状全体を復元したという無条件の保証をしない。

外周10×10、中央穴4×4の2D profile fixtureを用い、材料面積が100-16=84 mm2となること。これを高さ10 mmで押し出したcandidateは体積840 mm3となること。外周ringとhole ringを同列unionして面積100にしないこと。離れた二つのconnected componentとそれぞれのholeを持つfixtureで、最大componentだけを残さず全component／holeの包含関係がJSONへ保存されること。self-intersection等でtopologyを確定できない入力を「近い輪郭」として成功させないこと。

profile JSONは`schema_id=openscad.profile`／`schema_version=1`、slice JSONは`schema_id=openscad.feature-map`／`schema_version=1`を持つこと。対応consumerでv1を読み、schema ID違い、v2等のunsupported versionはbest-effort解釈せずblocked／exit 3、必須field欠落はexit 2となること。consumer resultへartifact hashと検査したschema ID/versionを残すこと。

元fixtureを平行移動・回転したSTLで`source_frame`と`analysis_frame`を発生させ、`source_to_analysis`と`analysis_to_source`が相互逆変換であること、profile点とfitted featureがframeを明記すること、生成candidateをsource frameへ戻して元STLと比較することを確認する。round-trip誤差を記録し、analysis frameのcandidateを元STLと直接比較しないこと。

slice位置の間に小穴があるfixtureを用い、少数sliceで見えないことから「穴は存在しない」と断定しない。axisやslice間隔を変えた再観測が必要と報告すること。凹形状のchannelをhullで勝手に埋める手順を必須規則にしないこと。

Reconstruct candidateの合格にはSCAD生成、compile、exportだけでなく複合品質gateを要求する。既定では`--min-volume-iou 0.95`、`--dimension-tolerance-mm 0.20`を適用し、source/candidateのbbox X/Y/Zすべてが0.20 mm以内、volume IoUが0.95以上、required critical featureが個別tolerance内で一致すること。`--min-volume-iou`は`0 < value <= 1`、`--dimension-tolerance-mm`は有限の`0 < value <= 1000`だけ受理する。

小体積の直径2 mm through holeまたはslotを持つfixtureを用意し、穴を塞いでもvolume IoUだけは0.95以上になるケースを作る。穴／slotを`required_features`へ含め、径・幅・位置のcheckがfailedになるためcandidate全体が不合格となること。analyzerが重要feature候補を検出したが照合できない場合は`unverified_feature`としてtaskをsucceededにしない。利用者が明示的に受け入れ範囲を狭めた場合だけscope外理由をquality specと最終報告へ残すこと。

### AC-17: SDFの対応範囲、再現性、quality spec

対応modelについてseed、sample数、bounds、solver status、生成SCADを記録する。bounds違反や非収束を成功として隠さない。生成SCADをcompile・exportし、source frameへ戻したmeshを別のmesh比較で確認する。

`solver_succeeded`、SCAD生成、compile、mesh export、volume IoU、major dimensions、critical featuresを別々に記録する。solver正常終了またはcompile成功だけでReconstruct成功にしない。sampled IoUとexport meshのvolume IoUを異なる名称で保存し、最終合否は複合品質gateで判定する。quality未達はexit 5となりcandidateは診断・調整用として残せること。

`--quality-spec FILE`で`schema_id=openscad.reconstruct-quality`／`schema_version=1`のJSONを読み、critical featureのstable ID、kind、source frame上の期待値、単位、toleranceを追加できること。unsupported schema versionはexit 3。quality specが自動抽出required featureを黙って削除しないこと。利用者が`--min-volume-iou 0.98`や`--dimension-tolerance-mm 0.10`を指定した場合はその値をresultへ残し、既定へ戻したり下げたりしないこと。

未対応modelやSCAD generatorがないmodelを指定した場合、commentだけの`.scad`を完成品として返さないこと。汎用自動再構築scriptの未実装を隠さないこと。

## 6. 配布と検証証拠

### AC-18: packageとrepository整合

Skillを実装した時点で二つのhierarchy designを同じ内容へ更新し、既存repository validatorを通す。新Skillのactive link、実際に案内するcommand、script/module、template、requirementsの参照先がすべて存在すること。

設計段階は未作成のSkillをinstalled inventoryへ登録しない。既存ChatGPT worker ZIPの8 Skill構成を変更しない。OpenSCADを同ZIPへ勝手に同梱せず、別の自動release workflowも今回の設計だけを理由に追加しない。

### AC-19: capability、shape identity、artifact schema、検証履歴

`eval/scenarios.json`はAC ID、入力、期待成果物、必要capabilityを持つシナリオ定義とする。単なる20/20等の自己申告を検証済みの意味で同梱しない。Windowsで実際に実行した履歴には、source HEAD、OS build、Codex／Python／OpenSCAD／package version、command、終了値、stdout／stderr、成果物hashを残す。

各形状検証runにはroot source hash、解決済み`use`／`include`／`import`依存hash、effective `-D` override、OpenSCAD version、evaluation modeを含むsource identityを保存する。生成artifactを次commandで解析する場合はartifact hashと親source identityを関連付ける。dependency closureを確定できないrunは`identity_complete=false`とし、別runの結果を同一形状証拠へ統合しない。

中間JSONは`openscad.profile`、`openscad.feature-map`、`openscad.reconstruct-quality`、`openscad.view-manifest`のschema IDとversionを持ち、producer／consumer両側の対応version表を同一変更単位で更新する。unsupported versionをbest-effortで読む実装を禁止する。検証scenarioには対応v1、unsupported v2、schema ID違い、必須field欠落を含める。

CodexSkillの保守にTDDは適用しない。必要なfixtureは構文・schema・CLI smoke・実機受け入れの検証用として扱い、Red/Green証拠を作るためのtestやworkflowを追加しない。新しいWindows CIを前提条件にしない。まず利用可能なWindows実行環境で検証し、CI経路を追加する必要がある場合は別途承認範囲を確認する。

### AC-20: 出典と取り込み範囲

取り込み元commit、fileごとの流用／修正／独自作成、既存copyright・license noticeを`UPSTREAM.md`等へ記録する。上流READMEのMIT表記、LICENSE fileの不在、GitHub APIのlicense判定を混同しない。上流の正式なlicense条件・noticeを確認できるまで、file一式の再配布を確定しない。著作権者や年を推測してLICENSEを補わない。

この確認はコピーによる実装の前提であり、設計文書作成を妨げない。必要なら利用者に確認してから独自実装へ切り替える。上流へのIssue作成やlicense問い合わせの投稿は今回の依頼に含めない。

## 7. 小さな実装単位

| 単位 | 内容 | 前提と終了条件 |
| --- | --- | --- |
| P66-D | 本設計、tracking、report、説明、normal design review対応 | D-01〜D-06。required findingがclosedしてから実装へ進む |
| P66-I1 | Skill入口、reference分割、出典、導入手順、構造検査 | 設計review収束・実装指示と取り込み条件確認。AC-01〜03、18、20の構造・文書部分 |
| P66-I2 | Python CLI、path／process／result、project管理、doctor | AC-04〜06、13〜14、19の基盤部分。schema／retentionを含む。基本renderとの結合はI3で確認 |
| P66-I3 | render／validate／export、template、printer profile | AC-06〜10、15、19と基盤の結合。warning gate、shape identity、新run成果物、preview／verify、基本4viewとfeature coverageを区別 |
| P66-I4 | mesh／compare／profile／slice／optimize | AC-11〜12、16〜17、19。topology、schema、frame、複合品質gate、未対応機能を正しくblocked化 |
| P66-I5 | Windows Codex受け入れ、設計同期、最終報告 | 全必須ACの証拠を確認。未実施は残しmerge readinessを主張しない |

AC番号は各単位の担当範囲を示す。例えばI1ではfile構造とroutingの整合までを確認し、まだ存在しないCLIの起動や八つのmodeの実処理は合格にせず後続へ残す。I2ではprocess・path・依存判定を確認し、未実装renderとの結合はI3へ残す。部分確認をAC全体の合格と記録しない。全必須ACの最終完了はI5で判定する。

各単位内もレビュー可能な変更ごとにcommit／pushする。変更は同じPR #66へ積む。途中の段階では提供済みcommandだけを案内し、全mode対応済みと表示しない。実装後のreviewとCIは実装HEADを対象とし、本設計時のCI成功を流用しない。

## 8. 現時点の未検証・未確定事項

Windowsでの実行、PNGの生成とCodexによる閲覧、empty boolean応答のversion別挙動、warning分類のversion差、Python packageの固定version組は実装時に確認する。これらは実装受け入れの必須証拠であり、設計の推測で成功に変えない。

設計reviewのfix verification収束、利用者による実装開始指示、上流fileの取り込み条件の確認を待つ。本PRはDraftを維持し、workerはmergeしない。

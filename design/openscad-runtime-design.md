# OpenSCAD Skill実行基盤設計

## 1. 状態と適用範囲

2026-09-06作成。PR #66の設計ドラフトであり、以下は採用する実装契約であって動作確認済みの説明ではない。Skill全体の責務と読込規則は[OpenSCAD Skill設計](openscad-skill-design.md)を正本とする。

主対象はWindowsネイティブのCodexとPowerShell。WSL、Git Bash、Bash、Unixコマンドを必須にしない。Windows 10／11 x64を対象に設計し、実装時に実際に検証したOS build、Codex版、Python版、OpenSCAD版を記録する。未検証のOSやARM64、Linux、macOSを対応済みとは表明しない。

Pythonは3.11以上の構文で実装し、初回の依存解決・受け入れ検証の基準をPython 3.12 x64とする。これは設計上の基準であり、他のPython版での互換性保証ではない。OpenSCADの機能は実バイナリの`--version`、`--help`、実際の出力で確認し、nightlyにしかないoptionを暗黙に要求しない。

## 2. 実装構造と責務

公開CLIは`python <skill-root>/scripts/openscad.py <command> ...`に統一する。PowerShellは起動例のために使い、処理本体をPowerShellとPythonへ二重実装しない。Python本体は基本操作でも必須とする。旧版の「基本操作にPython不要」という説明は引き継がない。

| ファイル候補 | 責務 |
| --- | --- |
| `scripts/openscad.py` | 引数受付、command dispatch、最終終了コード。幾何処理を書かない |
| `scripts/openscad_lib/runtime.py` | バイナリと依存機能の探索、version、プロセス実行、timeout、ログ |
| `scripts/openscad_lib/paths.py` | Skill root、workspace、許可済み出力先、SCAD用パス文字列 |
| `scripts/openscad_lib/results.py` | 結果schema、run manifest、状態集約、成果物検査、shape identity |
| `scripts/openscad_lib/project.py` | init／list／info／clean、project identity、run retention、sourceと生成物の分離 |
| `scripts/openscad_lib/render.py` | PNG、複数view、STL、3MFの生成、評価条件とview manifestの固定 |
| `scripts/openscad_lib/validate.py` | compile、warning分類、出力確認、要求値との照合 |
| `scripts/openscad_lib/mesh.py` | STL読込、基本統計、mesh検査、boolean比較 |
| `scripts/openscad_lib/profile.py` | 断面・profile抽出、穴・複数成分のtopology保持 |
| `scripts/openscad_lib/slice.py` | 適応的な多軸slice、解析座標frame管理 |
| `scripts/openscad_lib/optimize.py` | 対応model限定のSDF最適化、複合品質gate |

上記はSkill自身の内部moduleであり、別installable Skillでもrepository外shared dependencyでもない。`__init__.py`を置き、親repositoryのworking directoryや`PYTHONPATH`を要求しない。構文確認や内部moduleの小分けは行うが、未使用の拡張frameworkは作らない。

## 3. CLI契約

| Command | 入力と主option | 成果物・責務 |
| --- | --- | --- |
| `doctor` | `--capability basic|mesh|profile|optimize|png|3mf` | 実行環境の検出。存在／option検出と実行成功を区別 |
| `project init` | `--name NAME`、`--root DIR` | 新規project、stable project ID、必要なlocal template copy。既存projectは変更しない |
| `project list`／`info` | rootまたはproject | 読取だけ。root不在のlistは空一覧 |
| `project clean` | project、`--expired-runs`または`--run-id ID`、`--apply`、`--yes` | 既定は削除候補だけ表示。current project所有のrunだけを対象にする |
| `render` | SCAD、`--views iso|multi`、`--extra-view VIEW`反復、`--purpose explore|verify`、`--size W,H`、`--camera VALUE`、`--define EXPR`反復 | isoは1画像、multiはiso／front／right／topの4画像。verifyはexportと同じ最終評価条件を使う |
| `validate` | SCAD、`--define EXPR`反復 | OpenSCAD compile、warning gate、非空出力の確認。必要なmesh検査は別field |
| `export` | SCAD、`--format stl|3mf|all`、`--define EXPR`反復 | stlはbinaryを明示。allはSTL／3MF／verify PNGを要求成果物として扱う |
| `analyze` | SCADまたはSTL、`--level basic|mesh` | basicはbbox・triangleなど。meshは閉包性・体積等を追加 |
| `compare` | STL A／B、`--images` | 数値比較をPNG生成から独立実行。images指定時は画像も要求成果物 |
| `profile` | STL、`--axis x|y|z|auto` | schema付きtopology JSON、SVGまたはprofile SCAD。axis選定理由とframeを残す |
| `slice` | STL、coarse／fine間隔 | schema付きfeature-map JSON。frame、軸、slice位置、contourを持つ |
| `optimize` | STL、`--model NAME`、`--seed N`、`--samples N`、`--min-volume-iou FLOAT`、`--dimension-tolerance-mm FLOAT`、`--quality-spec FILE` | 対応modelのparameter、sampled IoU、solver状態、export後の複合品質gate、生成可能時だけSCAD |

`--min-volume-iou`は`0 < value <= 1`、既定`0.95`とする。`--dimension-tolerance-mm`は有限の`0 < value <= 1000`、既定`0.20` mmとする。範囲外は入力不正／exit 2。`--quality-spec FILE`は後述の`openscad.reconstruct-quality` schema v1で、穴、slot、主要位置などcritical feature固有の期待値と許容誤差を追加する。利用者がtargetを変更した場合は入力値と根拠をresultへ保存し、黙って既定値を下げない。

すべての書込commandは`--workspace DIR`と`--output-dir DIR`、run記録用の`--retain-days N`を共通に受け付ける。`--retain-days`は整数`1..3650`、既定30日。workspace省略時は開始時のcwdを固定する。相対入力・出力はそのcwd基準で正規化し、内部処理中のcwd変更で意味を変えない。CLIの`--define`はOpenSCADに`-D`と式を別argv要素として渡す。公開CLIに未知のOpenSCAD optionを無条件転送するescape hatchは作らない。

旧`.sh`名との互換aliasは初回対象外。移行表と全使用例を新CLIへ統一し、存在しない旧scriptを呼ばせない。`custom`の目的はrenderのcamera／size等の明示optionで引き継ぎ、任意shell実行は提供しない。

`doctor`の通常実行はpackageの自動install、設定書換え、ネットワーク接続を行わない。PNGなどの実行probeは明示選択された場合だけ小さなfixtureで行う。通常render自体が成功した場合も、そのrun内のcapability証拠にできる。`--help`にoptionがあるだけでPNG生成可能とは判定しない。

`render --purpose explore`は形状探索の高速表示に限り、OpenSCADのpreview評価を許可する。`render --purpose verify`と`export --format all`のPNGは最終形状確認であり、`--render`相当の評価条件を使って`$preview=false`にする。探索PNGとverify PNGを同じ検証証拠として混用せず、resultへ`evaluation_mode: preview|render`を保存する。最終STL／3MFとverify PNGは同じsource identity、`-D` override、library closureで評価する。

`render --views multi`の基本view IDは`iso`／`front`／`right`／`top`とする。`--extra-view`は`back|left|bottom|iso|front|right|top`または実装で検証済みのnamed custom viewを受け付ける。内部featureの確認にsection診断が必要な場合は、最終形状そのものと混同しないdiagnostic viewとして別ID・生成方法・source identityを記録する。

## 4. Windows固有契約

### 4.1 PythonとOpenSCAD

Windowsの導入例では`py -3.12 -m venv .venv`でproject環境を作り、activationを必須にせず`.venv\\Scripts\\python.exe`を明示して使う。既存の指定Pythonがあればそれを優先する。子Python処理が必要な場合は`sys.executable`を使用し、別の`python3`を再探索しない。

OpenSCADは次の順で解決する。

1. `--openscad-bin`。
2. 環境変数`OPENSCAD_BIN`。
3. WindowsではPATH上の`openscad.com`。他OSは将来対応時に専用探索を実装する。

明示指定が無効なら即時に環境エラーとし、別バイナリへ黙って切り替えない。指定値は単一の実行ファイルパスであり、引数付きcommand文字列ではない。Windowsの既定CLIは公式manualに従い`openscad.com`を使う。`openscad.exe`の明示指定は、version出力・stderr・終了待ちを確認できた構成に限る。`/opt/homebrew/bin/openscad`、Program Files以下、ユーザー名を決め打ちしない。[S1]

### 4.2 パスと環境変数

Skill rootはscriptの`__file__`から求める。`.claude`、`.codex`、`.agents`、repositoryの配置場所をscript内へ固定しない。workspaceとSkill rootを混同せず、Skill directoryはread-only resourceとして扱う。

`OPENSCADPATH`は子プロセス用environment copyに設定する。Windowsは`;`、対応するUnix実行環境は`:`で連結する。既存の利用者設定を保持し、今回使用するlibrary directoryを明示順に追加する。mixed Windows／WSL pathを自動推定で変換せず、無効な探索先を診断する。[S2]

既定出力先は`<workspace>/openscad-projects/<name>/`とする。`--root`、`--output-dir`、`OPENSCAD_PROJECTS_ROOT`で別の場所を指定する場合、優先順は明示CLI、環境変数、既定値とする。workspace外出力は利用者の明示指定と実行環境の権限を必要とし、失敗時にsandbox設定を緩めない。[S3]

パスは`pathlib`で扱い、空白・日本語・apostropheを文字列として保持する。`C:\\...`のバックスラッシュを生成Pythonコードへ埋め込まない。SCADへ`import()`等を書く場合は、slash正規化とSCAD string用の引用符・改行escapeを一つの関数で行う。NULなど表現不能な入力は拒否する。Python、JSON、SCADそれぞれのescape規則を混用しない。

### 4.3 プロセス実行とtimeout

OpenSCADはargv配列と`shell=False`で起動する。`eval`、shell command連結、`python -c`への入力埋込を禁止する。これはshell解釈を防ぐ設計であり、入力SCADの読取範囲を制限するsandboxの代替ではない。

起動時cwd、実行バイナリ、引数、開始・終了時刻、timeoutを保存する。stdoutとstderrを別ファイルへ保存し、全ログを末尾数行だけに切り詰めない。原byte列を保持し、表示用decodeで置換が起きた場合はその事実を記録する。JSON／新規SCAD／MarkdownはUTF-8で書く。

timeoutはcommandごとに有限の既定値を持ち、`--timeout`で変更可能とする。Windowsでは`.com`から起動される`.exe`を含む自分の子process treeだけを追跡・終了する。実装はWindows Job Object等で起動から終了まで管理し、無関係なOpenSCAD GUIをprocess名で一括停止しない。子treeを安全に管理できない環境は明示エラーにし、孤児processを残して成功扱いしない。

失敗・timeout時はcleanupより先に、生成したhelper SCAD、process stdout／stderr、入力manifest、途中成果物の存在・hashを`.openscad/runs/<run-id>/diagnostics/`へ退避する。退避後にだけephemeral tempを削除する。退避できない場合はその保存失敗自体をresultへ記録し、存在しないdiagnostic pathを示さない。成功runでもstdout／stderrとsource identityはrun記録として保持する。

### 4.4 一時ファイル、run ownership、非破壊性

`/tmp`、固定名`check.stl`の共有、一律`rm -rf`を使わない。許可済み出力root内に`tempfile`でrunごとの一時directoryを作り、Windowsのfile handleを閉じてから再読込・削除する。後続processが参照するfileをopenしたまま渡さない。

`project init`は`.openscad/project.json`へrandom UUIDのstable `project_id`を一度だけ作成する。各runは`project_id`、`run_id`、開始・終了時刻、`retention_until`、statusをresultへ保存し、run directoryの所有者を確定する。別projectのrun、manifest欠落、project ID不一致、active markerが残る実行中runを自動削除しない。

runの既定retentionは完了時刻から30日で、`--retain-days 1..3650`によりそのrunだけ変更できる。write command開始時のhousekeepingは、current project所有、完了済み、`retention_until`超過、path実体検査済みのrunだけを自動pruneできる。削除前にmanifestとproject IDを再検査し、junction／symlinkでrun root外へ出るもの、形式不明なrun、実行中runはskipしてwarningを残す。これによりrunを無期限保存する契約にも、所有権を見ずに無条件削除する契約にもしない。

`project clean --expired-runs`は同じexpiry ruleの候補を表示し、`--apply --yes`でcurrent project所有の期限切れrunだけを削除する。`project clean --run-id ID`はretention前でも利用者が特定runを明示削除できるが、同じproject IDと非active状態の検査を必須にする。通常のoutput cleanとrun cleanを混同せず、source、入力STL、profile、他projectのrunを削除しない。

project名はdirectory traversal、絶対パス、Windows予約名、末尾の空白・dotを拒否する。削除直前に解決済みpathがproject配下か再確認し、symlink／junctionを辿って外部を消さない。initは存在済みdirectoryを上書きしない。新規runは旧成果物の存在を今回の成功証拠に使わない。

書込先は文字列上のprefixだけで許可せず、各既存path componentを解決してjunction／symlinkによるworkspace外escapeがないことをpublish直前にも再確認する。入力と出力はWindows file identityまたは利用可能な同等手段で同一実体か確認し、同一実体なら拒否する。既存の同名成果物は既定で上書きせずblockedとし、明示的なreplace要求がある場合だけ、run固有staging fileの検証完了後にatomic replaceする。入力source、入力STL、profileをreplace対象にしない。

同時runはrun IDごとのstaging directoryを使う。共通の最終pathへpublishする場合はtarget単位の排他claimを取得し、別runがclaim中なら待機またはblockedとして明示する。固定temp名や「最後に書いたrunが勝つ」動作を許可しない。排他claim取得後もpublish直前にpath identityとallowed rootを再確認する。

## 5. 依存関係

| Capability | 必要なもの | 不足時の動作 |
| --- | --- | --- |
| project管理、help、基本STL統計 | Python標準library | Pythonがなければ導入案内。勝手にinstallしない |
| render／validate／export | 標準library＋OpenSCAD | 必要format／optionが未対応ならblocked |
| mesh検査・boolean比較 | 上記＋NumPy、trimesh | 精度や閉包性を推測せずblocked |
| profile／slice | mesh系＋Shapely | 当該解析だけblocked |
| SDF optimize | 解析系＋SciPy、rtree | optimizeだけblocked。既存SCAD編集へ勝手に変更しない |

任意依存をCLI moduleのtop-levelで一括importしない。`help`、`doctor`、基本renderがSciPy不足で落ちないようにする。requirementsは基本／mesh・profile／optimizeの導入経路を区分し、実装時にWindows wheelで解決できたversion組を記録する。未検証の「全最新版対応」は表明しない。

Modifyは正確なmesh検査を要求する場合にmesh capabilityを必要とする。写真からのReplicateは画像認識を使うが、それだけでSciPyを要求しない。依存関係はmode名ではなく実際に呼ぶcommandで決める。printer profileの読取に外部packageを要求しない。

## 6. プロジェクトと持ち運べるsource

標準projectは`src/`、`lib/`、`input/`、`output/`、`previews/`、`.openscad/runs/`を持つ。Quickは`src/`を省いた小さなprojectでもよいが、入力と成果物の分離・run識別は省略しない。

使うtemplateと`printable-lib.scad`、`printer-profile.scad`をprojectの`lib/`へ必要な分だけcopyする。生成SCADはsource位置からの相対pathで参照する。SkillがなくてもOpenSCADからsourceを再読込できるよう、依存fileとoriginをmanifestに列挙する。既存sourceで外部依存があれば、そのまま必要条件として報告し、無断で全面copy／書換えしない。

測定済みprofileはproject側だけを更新し、install済みSkillのtemplateを変更しない。初期値は`profile_measured=false`。未測定値は仮定として表示し、実測値を自動で作らない。嵌合・耐荷重・材料依存の寸法は不足を明記する。

## 7. 結果・診断契約

各実行は衝突しないrun IDを持ち、`.openscad/runs/<run-id>/result.json`と子processごとのstdout／stderrを保存する。run IDは時刻だけでなく乱数識別子を含める。出力root自体が作れない場合はstdoutの構造化エラーとstderrへ理由を返し、存在しないログpathを示さない。

`result.json`は`schema_version: 1`とし、次を必須fieldとする。

| Field | 内容 |
| --- | --- |
| `project_id`, `run_id`, `command`, `status`, `exit_code` | project／実行識別、要求、総合状態、CLI終了値 |
| `inputs` | 正規化path、content hash、parameter override、単位、要求値 |
| `source_identity` | root SCAD／STL hash、再帰的に解決できた`use`／`include`／`import`依存hash、effective override、OpenSCAD version、identity完全性 |
| `environment` | OS、Python、OpenSCAD path／version、必要package version。全環境変数は保存しない |
| `processes` | argv、cwd、各終了値、timeout、stdout／stderr path、`evaluation_mode` |
| `coordinate_frames` | source frame、analysis frame、source→analysis／analysis→source変換、単位。変換しない場合もidentityを記録 |
| `artifacts` | 今回生成したpath、kind、size、hash、検査結果、source identity／artifact parent hash、schema情報 |
| `checks` | 名前、`passed|failed|not_requested|unsupported|not_run`、数値・根拠 |
| `metrics` | 定義名、値、単位、method、tolerance、算出不能理由。未知はnull |
| `retention` | 完了時刻、retain days、retention_until、自動prune可否 |
| `errors`, `warnings` | 安定したcategory、説明、次の操作 |

`source_identity`はcommand間で「同じ形状条件を検証した」ことを確認するためのfingerprintである。`use`／`include`／`import`の依存closureを再帰的にhashし、動的path等でclosureを確定できなければ`identity_complete=false`とする。その場合、別commandの結果を同一形状の証拠として自動結合しない。`width=12`でexportしたmeshをdefault `width=10`のanalysis結果と同じcandidateとして扱わない。STL等の成果物を次commandへ渡す場合はartifact hashをparent identityとして引き継ぐ。

`status`は`succeeded|partial|failed|blocked`。全要求項目を満たした場合だけsucceeded／exit 0とする。引数・入力不正は2、環境・依存不足やunsupported schemaによるblockedは3、process失敗・timeoutは4、検証不合格は5、一部成果物だけ成功したpartialは6。未知の例外も診断を残し非0とする。非必須の未実施項目は明示し、optional skipだけで必須項目の成功を覆さない。

`--json`指定時のstdoutにはJSONを一つだけ出し、進捗や子process出力を混ぜない。通常は人向け要約を返し、同じresult pathを提示する。`export --format all`で3MFだけ失敗した場合はSTLの保存を報告してもoverall successにはしない。

画像をモデルが見たかどうかはPythonでは分からない。CLIはPNG生成とview manifestまでを記録し、Skillは別の最終報告で`visual_review: passed|failed|unavailable|not_requested`、対象run ID・画像hash・`visual_feature_coverage`・所見を記録する。CLIが`visual_review=passed`を自動生成してはならない。画像を開けなければ視覚確認未実施であり、PNG存在と区別する。

### 7.1 中間artifact schemaとconsumer契約

profile、slice、再構築品質条件など、別commandがconsumeするJSONは`result.json`とは独立したversioned schema envelopeを必須にする。

| Artifact | `schema_id` | 初期`schema_version` |
| --- | --- | ---: |
| profile topology JSON | `openscad.profile` | 1 |
| slice feature-map JSON | `openscad.feature-map` | 1 |
| reconstruct quality specification | `openscad.reconstruct-quality` | 1 |
| generated view manifest | `openscad.view-manifest` | 1 |

各JSONはtop-levelに`schema_id`、`schema_version`、producer version、source identity、必要なcoordinate frame参照を持つ。consumerはpayloadを読む前に`schema_id`と`schema_version`を検査し、サポート表に完全一致するversionだけをconsumeする。未知schema ID／unsupported versionはbest-effortで解釈せずblocked／exit 3、必須field欠落や型不正はinvalid input／exit 2とする。schema migrationを行う場合は明示的なmigration処理と変換前後schema versionを保存し、暗黙にv1として読むことを禁止する。

producer側は新versionを出すときconsumer supportを同一変更単位で更新する。古いartifactを再利用するrunでは、consumerが検査したschema ID/versionとartifact hashをresultへ記録する。

## 8. 検証・比較の正確さ

### 8.1 compile、warning、物理品質を分離する

validateの成功はcompile、warning gate、今回の非空出力確認を意味する。bbox、mesh閉包性、壁厚、overhang、bed収容、実際の印刷品質は別checkとする。パラメーターの`assert()`はその関係の確認であり、任意形状の全局所壁厚を測った証拠ではない。

OpenSCADは、未定義moduleや欠落include等でも正常bodyが残ればexit 0と非空成果物を返すversionがあるため、process exit 0やfile存在だけをcompile成功条件にしない。validation gateは、対応versionで`--hardwarnings`を使用してwarningをprocess失敗へ昇格させるか、同等のdiagnostic分類を行う。`ERROR`、parser error、unknown module／function、未定義変数に起因する評価不能、`use`／`include`／`import`の解決失敗等、形状意味論が欠落するdiagnosticはblocking warningとして`checks.compile=failed`／exit 5にする。未知warningは成功へ落とさず、分類不能ならvalidation failedとして保持する。

warningを許容する必要がある場合は、warning categoryを設計上の明示allowlistへ追加し、なぜ形状意味論を損なわないかと適用OpenSCAD versionを記録する。利用者単位で黙ってwarningを無視するoptionは初回提供しない。render／exportで成果物が生成されても、そのsource identityに対する必須validationがfailedなら成果物を検証済み成功として扱わない。

解析対象を持たない項目は`unsupported`または`not_requested`とし、全体を「印刷可能保証済み」とはしない。利用者が必須にした項目を検証できなければ完了条件を満たさない。STL基本readerはASCII／binaryを識別し、破損・切断・非有限座標を拒否する。watertight／volume等を報告するときはmesh解析の結果を使う。

### 8.2 数値比較をPNGから独立させる

上流`openscad-stl-compare.sh`はPNG成功後だけ差分STLを出し、差分file不在を体積0として扱う。また`1-(V(A-B)+V(B-A))/V(A)`をaccuracyと表示し、IoUではない。[S4]

移植版ではA／Bを同じ座標系・単位で比較し、自動center合わせ・scale変更・repairを行わない。必要な場合は利用者承認と変換matrixを記録して別runにする。STLには単位の確認が必要なので、mmなどの前提をinputsへ明記する。

入力meshが有効な閉じた正体積形状であることを確認したうえで、OpenSCADのboolean結果から`V(A-B)`と`V(B-A)`を算出する。各結果は`nonempty|empty|failed`に分類する。空差分は、検証済み入力と、実バイナリで検証したempty-result応答の組合せでだけ認定する。file不在、stderr内の単語一つ、任意の非0終了だけからemptyと判定しない。未対応versionの空結果はfailedとしてmetricをnullにする。

`V_intersection = V(A) - V(A-B)`、`V_union = V(A) + V(B-A)`、`volume_iou = V_intersection / V_union`を主metricとする。`V(B)-V(B-A)`との一致と0〜1の範囲をtolerance付きで検査する。許容誤差を超える不一致をclipで隠さず失敗にする。missing volume／extra volumeも別に報告し、旧accuracyと混同しない。

PNGが使えなくても数値比較は独立して実行可能にする。`--images`要求時に画像が失敗すればpartialとし、算出済みmetricにmethodと範囲を添えて保存する。各画像は同一camera・projection・共通bboxに基づくframingで作り、個別autocenterで位置差を隠さない。overlayにはpreview用表示方式を使い、背景modifierがfinal renderで失われないことを確認する。

### 8.3 profile topologyと座標frame

profile／sliceは輪郭を「点列の集合」だけでなく、connected componentごとのouter ringとinner ring（hole）の包含関係として保持する。外周と穴輪郭を同列にpolygonizeしてunionし、穴を材料で埋める実装を禁止する。複数componentのうち最大輪郭だけを残すことも禁止する。各componentの外周面積から所属hole面積を引いた材料面積を計算し、self-intersectionや包含関係が曖昧でtopologyを確定できない場合は成功形状を捏造せず`failed`または`unsupported`にする。

解析の都合で軸入替え、回転、平行移動を行う場合、元STLの座標を`source_frame`、解析座標を`analysis_frame`とし、同次4×4の`source_to_analysis`と`analysis_to_source`を相互逆行列として保存する。profile点、slice位置、fitted primitiveはどのframeの値かを明示する。生成candidateは原則source frameへ戻してからSCAD／mesh比較し、analysis frameのcandidateを元STLと直接比較しない。round-trip誤差と単位を結果へ保存する。

有限個のsliceにcontourがないことは、モデル全体にそのfeatureがない証明ではない。slice間隔・位置・限界を記録し、追加slice／別軸／画像照合が必要な箇所を未確定とする。bbox一致だけで再構築成功としない。

### 8.4 再構築と最適化の複合品質gate

SDF optimizerのsampled IoUとexport meshのvolume IoUは別metricとする。seed、sample数、bounds、solver終了状態を記録する。初期seedは0、sample数は30000とし、反復・実行時間に上限を設ける。得たparameterからSCADをcompile・exportし、source frameへ戻したmeshを元meshと比較するまで、製造用形状の一致を確定しない。

`solver_succeeded`、`scad_generated`、`compile_succeeded`、`mesh_exported`、`volume_iou_target_met`、`major_dimensions_target_met`、`critical_features_target_met`を別checkにする。solverが正常終了しても品質合格ではなく、SCADがcompileできても形状一致の証拠にはならない。

既定Reconstruct品質gateは次をすべて満たす場合だけpassedとする。

1. export meshの`volume_iou >= 0.95`。CLIでは`--min-volume-iou`で変更可能。
2. source meshとcandidate meshの主要bbox寸法X／Y／Zそれぞれの絶対誤差が`<= 0.20 mm`。CLIでは`--dimension-tolerance-mm`で変更可能。
3. `required_features`の全項目が個別許容誤差内で一致すること。required featureは、利用者が明示した穴・slot・位置・径等に加え、選択した再構築手法がsourceから抽出してparameter化した穴、slot、through opening、主要profile featureを含む。
4. analyzerが重要feature候補を検出したが分類・計測・candidate照合できない場合は`unverified_feature`として残し、taskをsucceededにしない。利用者が受け入れ範囲を明示的に狭めた場合だけ、そのfeatureをscope外とした理由をquality specと最終報告へ残す。

`openscad.reconstruct-quality` v1は、`volume_iou_min`、`dimension_tolerance_mm`、`required_features[]`を持つ。各featureはstable `feature_id`、kind、source frame上の期待値、単位、tolerance、measurement methodを持つ。`--quality-spec FILE`はこのschemaを追加条件として読み、既定または自動抽出されたrequired featureを黙って削除しない。target未達candidateは調査・中間成果物として保持できるが、Reconstruct taskをsucceededにせずvalidation failure／exit 5とする。

上流の`generate_scad()`は`stadium-slot`以外でgenerator未提供を示すcommentを返す。[S5] 移植版は対応modelと`can_generate_scad`を明示し、未対応modelからcommentだけのfileを成功成果物として出さない。初回のend-to-end候補は実在する`stadium-slot`に限定する。新たなmodel generatorは別の承認対象とし、汎用STL自動再構築は約束しない。

## 9. 参照

以下は設計判断の根拠。上流fileはGitHub connectorで読み取った固定commitを参照する。

- [S1: OpenSCAD公式manual・CLI／Windows notes](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_OpenSCAD_in_a_command_line_environment)
- [S2: OpenSCAD公式manual・Libraries／OPENSCADPATH](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Libraries)
- [S3: OpenAI・Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [S4: 上流STL比較実装](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-stl-compare.sh)
- [S5: 上流SDF optimizer](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-sdf-optimize.py)

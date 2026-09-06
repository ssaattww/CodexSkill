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
| `scripts/openscad_lib/results.py` | 結果schema、run manifest、状態集約、成果物検査 |
| `scripts/openscad_lib/project.py` | init／list／info／clean、sourceと生成物の分離 |
| `scripts/openscad_lib/render.py` | PNG、複数view、STL、3MFの生成 |
| `scripts/openscad_lib/validate.py` | compile、warning分類、出力確認、要求値との照合 |
| `scripts/openscad_lib/mesh.py` | STL読込、基本統計、mesh検査、boolean比較 |
| `scripts/openscad_lib/profile.py` | 断面・profile抽出 |
| `scripts/openscad_lib/slice.py` | 適応的な多軸slice |
| `scripts/openscad_lib/optimize.py` | 対応model限定のSDF最適化 |

上記はSkill自身の内部moduleであり、別installable Skillでもrepository外shared dependencyでもない。`__init__.py`を置き、親repositoryのworking directoryや`PYTHONPATH`を要求しない。構文確認や内部moduleの小分けは行うが、未使用の拡張frameworkは作らない。

## 3. CLI契約

| Command | 入力と主option | 成果物・責務 |
| --- | --- | --- |
| `doctor` | `--capability basic|mesh|profile|optimize|png|3mf` | 実行環境の検出。存在／option検出と実行成功を区別 |
| `project init` | `--name NAME`、`--root DIR` | 新規projectと必要なlocal template copy。既存projectは変更しない |
| `project list`／`info` | rootまたはproject | 読取だけ。root不在のlistは空一覧 |
| `project clean` | project、`--apply`、`--yes` | 既定は削除候補だけ表示。明示実行時もmanifest内の生成物だけ削除 |
| `render` | SCAD、`--views iso|multi`、`--size W,H`、`--camera VALUE`、`--define EXPR`反復 | isoは1画像、multiはiso／front／right／topの4画像 |
| `validate` | SCAD、`--define EXPR`反復 | OpenSCAD compile、warning、非空出力の確認。必要なmesh検査は別field |
| `export` | SCAD、`--format stl|3mf|all`、`--define EXPR`反復 | stlはbinaryを明示。allはSTL／3MF／PNGを要求成果物として扱う |
| `analyze` | SCADまたはSTL、`--level basic|mesh` | basicはbbox・triangleなど。meshは閉包性・体積等を追加 |
| `compare` | STL A／B、`--images` | 数値比較をPNG生成から独立実行。images指定時は画像も要求成果物 |
| `profile` | STL、`--axis x|y|z|auto` | JSON、SVGまたはprofile SCAD。axis選定理由を残す |
| `slice` | STL、coarse／fine間隔 | 軸・slice位置・contourを含むfeature-map JSON |
| `optimize` | STL、`--model NAME`、`--seed N`、`--samples N` | 対応modelのparameter、sampled IoU、収束状態、生成可能時だけSCAD |

すべての書込commandは`--workspace DIR`と`--output-dir DIR`を共通に受け付ける。workspace省略時は開始時のcwdを固定する。相対入力・出力はそのcwd基準で正規化し、内部処理中のcwd変更で意味を変えない。CLIの`--define`はOpenSCADに`-D`と式を別argv要素として渡す。公開CLIに未知のOpenSCAD optionを無条件転送するescape hatchは作らない。

旧`.sh`名との互換aliasは初回対象外。移行表と全使用例を新CLIへ統一し、存在しない旧scriptを呼ばせない。`custom`の目的はrenderのcamera／size等の明示optionで引き継ぎ、任意shell実行は提供しない。

`doctor`の通常実行はpackageの自動install、設定書換え、ネットワーク接続を行わない。PNGなどの実行probeは明示選択された場合だけ小さなfixtureで行う。通常render自体が成功した場合も、そのrun内のcapability証拠にできる。`--help`にoptionがあるだけでPNG生成可能とは判定しない。

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

timeoutはcommandごとに有限の既定値を持ち、`--timeout`で変更可能とする。Windowsでは`.com`から起動される`.exe`を含む自分の子プロセスtreeだけを追跡・終了する。実装はWindows Job Object等で起動から終了まで管理し、無関係なOpenSCAD GUIをprocess名で一括停止しない。子treeを安全に管理できない環境は明示エラーにし、孤児processを残して成功扱いしない。

### 4.4 一時ファイルと非破壊性

`/tmp`、固定名`check.stl`の共有、一律`rm -rf`を使わない。許可済み出力root内に`tempfile`でrunごとの一時directoryを作り、Windowsのfile handleを閉じてから再読込・削除する。後続processが参照するfileをopenしたまま渡さない。

project名はdirectory traversal、絶対パス、Windows予約名、末尾の空白・dotを拒否する。削除直前に解決済みpathがproject配下か再確認し、symlink／junctionを辿って外部を消さない。initは存在済みdirectoryを上書きしない。cleanは新旧manifestの生成物だけを候補にし、SCAD source、入力STL、測定済みprofileを消さない。新規runは旧成果物の存在を今回の成功証拠に使わない。

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
| `run_id`, `command`, `status`, `exit_code` | 実行識別、要求、総合状態、CLI終了値 |
| `inputs` | 正規化path、content hash、parameter override、単位、要求値 |
| `environment` | OS、Python、OpenSCAD path／version、必要package version。全環境変数は保存しない |
| `processes` | argv、cwd、各終了値、timeout、stdout／stderr path |
| `artifacts` | 今回生成したpath、kind、size、hash、検査結果 |
| `checks` | 名前、`passed|failed|not_requested|unsupported|not_run`、数値・根拠 |
| `metrics` | 定義名、値、単位、method、tolerance、算出不能理由。未知はnull |
| `errors`, `warnings` | 安定したcategory、説明、次の操作 |

`status`は`succeeded|partial|failed|blocked`。全要求項目を満たした場合だけsucceeded／exit 0とする。引数・入力不正は2、環境・依存不足によるblockedは3、process失敗・timeoutは4、検証不合格は5、一部成果物だけ成功したpartialは6。未知の例外も診断を残し非0とする。非必須の未実施項目は明示し、optional skipだけで必須項目の成功を覆さない。

`--json`指定時のstdoutにはJSONを一つだけ出し、進捗や子process出力を混ぜない。通常は人向け要約を返し、同じresult pathを提示する。`export --format all`で3MFだけ失敗した場合はSTLの保存を報告してもoverall successにはしない。

画像をモデルが見たかどうかはPythonでは分からない。CLIはPNG生成までを記録し、Skillは別の最終報告で`visual_review: passed|failed|unavailable|not_requested`、対象run ID・画像hash・所見を記録する。CLIが`visual_review=passed`を自動生成してはならない。画像を開けなければ視覚確認未実施であり、PNG存在と区別する。

## 8. 検証・比較の正確さ

### 8.1 compileと物理品質を分離する

validateの成功はcompile、warning policy、今回の非空出力確認を意味する。bbox、mesh閉包性、壁厚、overhang、bed収容、実際の印刷品質は別checkとする。パラメーターの`assert()`はその関係の確認であり、任意形状の全局所壁厚を測った証拠ではない。

解析対象を持たない項目は`unsupported`または`not_requested`とし、全体を「印刷可能保証済み」とはしない。利用者が必須にした項目を検証できなければ完了条件を満たさない。STL基本readerはASCII／binaryを識別し、破損・切断・非有限座標を拒否する。watertight／volume等を報告するときはmesh解析の結果を使う。

### 8.2 数値比較をPNGから独立させる

上流`openscad-stl-compare.sh`はPNG成功後だけ差分STLを出し、差分file不在を体積0として扱う。また`1-(V(A-B)+V(B-A))/V(A)`をaccuracyと表示し、IoUではない。[S4]

移植版ではA／Bを同じ座標系・単位で比較し、自動center合わせ・scale変更・repairを行わない。必要な場合は利用者承認と変換matrixを記録して別runにする。STLには単位の確認が必要なので、mmなどの前提をinputsへ明記する。

入力meshが有効な閉じた正体積形状であることを確認したうえで、OpenSCADのboolean結果から`V(A-B)`と`V(B-A)`を算出する。各結果は`nonempty|empty|failed`に分類する。空差分は、検証済み入力と、実バイナリで検証したempty-result応答の組合せでだけ認定する。file不在、stderr内の単語一つ、任意の非0終了だけからemptyと判定しない。未対応versionの空結果はfailedとしてmetricをnullにする。

`V_intersection = V(A) - V(A-B)`、`V_union = V(A) + V(B-A)`、`volume_iou = V_intersection / V_union`を主metricとする。`V(B)-V(B-A)`との一致と0〜1の範囲をtolerance付きで検査する。許容誤差を超える不一致をclipで隠さず失敗にする。missing volume／extra volumeも別に報告し、旧accuracyと混同しない。

PNGが使えなくても数値比較は独立して実行可能にする。`--images`要求時に画像が失敗すればpartialとし、算出済みmetricにmethodと範囲を添えて保存する。各画像は同一camera・projection・共通bboxに基づくframingで作り、個別autocenterで位置差を隠さない。overlayにはpreview用表示方式を使い、背景modifierがfinal renderで失われないことを確認する。

### 8.3 再構築と最適化

有限個のsliceにcontourがないことは、モデル全体にそのfeatureがない証明ではない。slice間隔・位置・限界を記録し、追加slice／別軸／画像照合が必要な箇所を未確定とする。bbox一致だけで再構築成功としない。

SDF optimizerのsampled IoUとexport meshのvolume IoUは別metricとする。seed、sample数、bounds、solver終了状態を記録する。初期seedは0、sample数は30000とし、反復・実行時間に上限を設ける。得たparameterからSCADをexportして再検証するまで、製造用形状の一致を確定しない。

上流の`generate_scad()`は`stadium-slot`以外でgenerator未提供を示すcommentを返す。[S5] 移植版は対応modelと`can_generate_scad`を明示し、未対応modelからcommentだけのfileを成功成果物として出さない。初回のend-to-end候補は実在する`stadium-slot`に限定する。新たなmodel generatorは別の承認対象とし、汎用STL自動再構築は約束しない。

## 9. 参照

以下は設計判断の根拠。上流fileはGitHub connectorで読み取った固定commitを参照する。

- [S1: OpenSCAD公式manual・CLI／Windows notes](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_OpenSCAD_in_a_command_line_environment)
- [S2: OpenSCAD公式manual・Libraries／OPENSCADPATH](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Libraries)
- [S3: OpenAI・Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [S4: 上流STL比較実装](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-stl-compare.sh)
- [S5: 上流SDF optimizer](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-sdf-optimize.py)

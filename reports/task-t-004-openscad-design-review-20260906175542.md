# T-004 / PR #66 設計レビュー

## 1. 判定と対象

- Generated: 2026-09-06T17:55:42.524330+09:00。

- Review mode: `initial_review`。通常の設計レビューであり、独立最終レビューではない。
- Verdict: **fail（設計修正が必要）**。
- Findings: **9件。high 2件、medium 7件**。全件を本報告と一つのPRコメントでまとめて提出する。
- Repository: `ssaattww/CodexSkill`。
- PR: [#66](https://github.com/ssaattww/CodexSkill/pull/66)、Draft / open。
- Task: `T-004`、Phase 9。
- Branch: `codex/openscad-windows-skill`。
- Base: `main` / `6507727986329e34e69da3680a00824eb1fbfe13`。
- Reviewed implementation HEAD: `cc9787604b2b3d6bfacaf714cf9485ec72ad0079`。ここでimplementationはレビュー対象を識別する共通field名であり、OpenSCAD Skillが実装済みという意味ではない。
- Range: `6507727986329e34e69da3680a00824eb1fbfe13..cc9787604b2b3d6bfacaf714cf9485ec72ad0079`。
- Reviewer identity: `chat-review-pr66-20260906`。本chatは設計・実装・修正を行っていない。過去の通常reviewerは確認されず、本chatを初回通常reviewerとする。既存reportとproject会話要約は参照しており、隔離された独立最終reviewとは主張しない。
- Report-attestation: `not_applicable`。本reportは通常reviewの記録であり、passing attestationではない。

開始時HEADは`8bf9d0e2d94464285044a866f447e5540e7f533c`だった。途中で4commitが追加されたため、その時点の判定を完成させず、追加差分4fileと更新後のPR情報を確認して上記HEADへ対象を更新した。元のOpenSCAD設計3文書・task/phase・初回report/handoffには、この4commitで変更がないことをcompareで確認した。旧HEADのCIを現HEADの証拠には使用しない。

## 2. 依頼・範囲・保存境界

利用者の依頼は「PR66 設計review、一度に出し切る」。対象はWindowsネイティブCodex向けOpenSCAD Skillの設計、受け入れ計画、利用者overview、階層設計、tracking、報告の整合である。追加overviewのauthoritative requestは`reports/task-t-004-user-overview-20260906174511.md`に記録されている。

アップロード済み`chatgpt-worker-skills.zip`の`chat-review-worker`、`work-context-manager`、`review-worker`、`report-writer`、`chat-handoff-manager`を参照した。repositoryの`AGENTS.md`、report命名規則、現HEADの階層設計も確認した。

設計・Skill・実装・task/phase・workflowを修正せず、mergeもしない。レビュー対象HEADを保存操作で変更しないため、詳細reportとhandoffは同じrepositoryの**報告専用branch**へ保存し、PR #66のConversationへ要約を投稿する。報告用branchのCIや旧HEADのCIを対象PRのCIとして代用しない。

CodexSkillは非TDDである。作業開始時に既存workflowを確認した。生成ZIP artifactはあるが、失敗時のstdout/stderrを一式保存する診断artifactではない。RevMem向け診断workflow追加方針は本repositoryに適用せず、変更しない。

## 3. 確認した変更範囲

| File | 確認内容 |
| --- | --- |
| `README.md` | 利用者入口、workflow順序、未実装表示、Refine、配布境界 |
| `design/openscad-skill-design.md` | 8 mode、5系統reference、共通契約、移行方針、出典 |
| `design/openscad-runtime-design.md` | CLI、Windows実行、path/process、依存、result、比較・再構築 |
| `design/openscad-acceptance-plan.md` | D-01〜06、AC-01〜20、段階別完了条件 |
| `design/skill-hierarchy-design.md` | 全追加差分、domain境界、直接関係するreview終端契約 |
| `skills/design/skill-hierarchy-design.md` | mirror内容・blob一致 |
| `tasks/tasks-status.md` | T-004全追加差分、旧taskが維持されること |
| `tasks/phases-status.md` | Phase 9全追加差分、旧phaseが維持されること |
| `reports/task-t-004-openscad-design-20260906171458.md` | 初回設計のscope・snapshot・検証の記述 |
| `reports/task-t-004-user-overview-20260906174511.md` | 追加依頼、4file変更、snapshot・CI記述 |
| `reports/handoffs/task-t-004-pr66-design-20260906171733.yaml` | 完全なpacketと埋込report、権限・未実装・過去snapshotの扱い |

直接関係する参照として、既存workflow、AGENTS、report命名規則、PRコメント/空のreview thread一覧、固定commitの上流file tree、profile extractor、SDF optimizer、OpenSCAD CLI manualを確認した。上流全fileを実行したという意味ではない。

階層設計の2fileは、現HEADでblob `36a14ff9b2f47049a6127b6d5f0f7029562b339e`が一致する。未実装OpenSCADの状態明示、既存ChatGPT worker ZIPの8 Skill維持、通常開発workflowをCAD Skillへ複製しない境界には指摘を出していない。

## 4. 指摘一覧

全findingのoriginは`introduced_by_change`。上流に存在する問題そのものへの修正要求ではなく、本PRが定める移植・実行・受け入れ契約の欠落として記録する。未実装コードに不具合が存在すると断定していない。severityの再分類・転記訂正はない。

### P66-DR-001 — high — 検証用PNGとexport形状の同一性が定義されていない

**Location:** runtime設計 §3 `render`/`export`、§7 visual review、§8.2 / AC-07。

**Description:** PNG生成と画像閲覧は分離されているが、通常renderをOpenCSG previewとして評価するのか、exportと同じ最終形状として評価するのかが未定義である。overlayにpreviewを使う契約だけでは、通常の視覚検証と最終成果物の対応を保証できない。run ID・画像hashがあっても、評価modeの相違は解消しない。

**Evidence:** OpenSCAD manualではPNGのpreviewとfull geometry評価が区別される。[S4] Linux/OpenSCAD 2021.01で同一source hashの`if ($preview) cube([10,20,30]); else cube([40,50,60]);`を確認した。通常PNGは`$preview=true`、`--render`付きPNGとSTLは`false`。STLのbboxは40/50/60だった。これはWindows受け入れ結果ではない。[E1]

**Impact:** 画像で確認した寸法・穴・組立形状とは異なるSTL/3MFを、同じ形状を確認済みとして扱う経路が残る。

**Required action / acceptance:** 対話用previewと成果物検証用renderを別用途として定義する。検証画像を最終評価またはexport済みmeshへ結び付け、評価mode・parameter・対象artifactの対応を記録する。overlayは別用途のままでよい。上記`$preview`分岐fixtureで、preview閲覧をexport形状の合格証拠にしないこと、最終形状の画像とexportの寸法が対応することをACへ追加する。

### P66-DR-002 — high — profileの穴・複数成分を保存する契約がない

**Location:** runtime設計 §3 `profile`、§8.3 / AC-16 / Skill設計 §7移行表。

**Description:** profileをJSON/SVG/SCADへ出すことは定義されているが、外周・穴・入れ子・複数の独立成分の表現と保持条件がない。上流を移植候補にする際に修正が必要な具体例が移行表とACから抜けている。

**Evidence:** 上流profile extractorは`polygonize()`の出力を一括`unary_union()`し、その後`.exterior`を前提にする。[S2] 独立したShapely 2.1.2のprobeでは、外側10×10・内側4×4の輪郭からarea84/穴1とarea16/穴0のpolygonが生成され、union後はarea100/穴0になった。離れた2輪郭では`MultiPolygon`となり、`.exterior`を持たない。[E2]

**Impact:** 中空部を埋めたSCAD、または複数成分で出力不能となる移植でも、現行の「抽出・比較の証拠を残す」だけでは期待形状との不一致を特定できない。

**Required action / acceptance:** 外周・穴・nesting・componentのschemaとSCAD変換規則を定義し、polygonizeした全領域をそのままunionしてよいとしない。上記リングはarea84・穴1、離れた2成分はcomponent数2を保持し、export後も穴と分離状態が維持されることを具体的なACへ追加する。上流移行表にも記録する。

### P66-DR-003 — medium — 解析座標から元モデル座標へ戻す契約がない

**Location:** runtime設計 §3 `profile`/`slice`/`optimize`、§8.2〜8.3 / AC-16〜17。

**Description:** compareでは無断のcenter合わせを禁止している一方、profile抽出やoptimizerの入力姿勢、断面の2D座標、生成SCADを元の座標系へ戻す方法が定義されていない。

**Evidence:** 上流profile extractorはOBB座標へ変換した`T`を返すが、SCAD generatorへ渡さず、常にZ方向へextrudeする。抽出axisはcommentに使われるだけである。[S2] 上流stadium-slot SDFとgeneratorはXY中心・Z底面0を前提とし、位置・姿勢parameterを持たない。[S3]

**Impact:** 同じ部品でも平行移動・回転された入力では、形状推定と座標誤差が混ざる。生成物の向き・位置を失うか、禁止している暗黙の位置合わせに依存することになる。

**Required action / acceptance:** 入力world座標、解析local座標、断面2D→3D、元座標への逆変換を結果schemaと生成SCADの契約に含める。内部計算上の正規化と利用者の形状を変更するtransformを区別し、必要な承認・記録を定める。非Z押出し、回転、平行移動を含む同一形状fixtureで、元座標へ戻した出力をcompareの自動位置合わせなしで検証する。SDFがその姿勢を扱えないなら、明示的なunsupported/blocked条件を定める。

### P66-DR-004 — medium — warning policyが未定義で、欠落featureを含む非空出力の判定が決まらない

**Location:** runtime設計 §2 `validate.py`、§7、§8.1 / AC-08。

**Description:** validate成功の条件に`warning policy`が登場するが、そのpolicy自体、未知warningの扱い、fatal分類、結果status/exit codeへの対応が定義されていない。AC-08も「必須validationが失敗した場合」は定めるが、正常なbodyと欠落featureが共存する入力の期待判定を確定していない。

**Evidence:** Linux/OpenSCAD 2021.01では`cube([10,20,30]); missing_feature();`も、存在しないincludeと正常cubeの組合せも、warningを出しながらexit0・非空STL・体積6000となった。`--hardwarnings`付きの前者はexit1・STLなしだった。[E1] warningを停止条件にするCLI機能はmanualにも記載される。[S4]

**Impact:** 終了値0と新規非空artifactだけでは、必要なmodule/includeを欠いた形状を成功としてしまう実装を排除できない。

**Required action / acceptance:** missing include/module等のfatal条件、許容するwarning、未知warning、version差、分類とexit/status対応を設計で確定する。`--hardwarnings`の採否自体は実装方式の選択だが、利用者要求に必要なfeatureの欠落を成功にしないことは必須にする。正常bodyが残る上記2fixtureを非0・安定categoryとし、正常fixtureとの区別をACへ追加する。

### P66-DR-005 — medium — stadium-slotのparameter相互制約がない

**Location:** runtime設計 §8.3 / AC-17。

**Description:** boundsとsolver statusを記録する規則はあるが、初回end-to-end対象のstadium-slotについて、parameterの許容域と相互制約が定義されていない。各値が正であることと、SDFとSCADが同じ幾何を表すことは別である。

**Evidence:** 上流のstadium距離式は`(length-width)/2`をclampの半区間に用い、SCADは2円のhullを使う。slotも同様に`(slot_total-slot_width)/2`へ依存する。[S3] 独立した数値probeでlength10/width20/height10、点(10,0,5)を評価すると、SDF側のXY距離は+5で外側、円hullの幾何では-5で内側となった。全parameterを正にするだけでは意味が一致しない。[E3]

**Impact:** 不正な候補を最適化し、sampled IoUとexport形状の関係が崩れる。solverが収束していても有効な設計parameterとは限らない。

**Required action / acceptance:** parameter名・単位・範囲と`length >= width`、`slot_total >= slot_width`等のモデル成立条件を確定し、探索中と生成前の適用方法を定義する。逆転区間、非有限値、境界値、非収束のfixtureを追加し、不適合parameterからSCAD完成品を成功として返さない。必要な制約を採用しない場合は、その域でもSDF/SCADが同じ幾何となる別定義を明記する。

### P66-DR-006 — medium — 要求値・単位・許容差を検証へ渡す経路がない

**Location:** runtime設計 §2 `validate.py`、§3 CLI、§7 `inputs`/`metrics` / AC-06・09・11。

**Description:** `validate.py`は要求値との照合を所有し、resultは単位・要求値・toleranceを記録する一方、公開CLIにはその入力方法やSkill側との責務分担がない。`--define`はモデルparameterの変更であり、独立した期待値の指定にはならない。

**Evidence:** CLI表にあるvalidate入力はSCADと反復`--define`、compare入力はSTL A/Bと`--images`である。入力の単位や必須check/期待寸法/許容差を受け取るschema・引数・別契約は定義されていない。§8.2では単位前提をinputsへ明記する要求がある。[S1]

**Impact:** 実装者がresultへ要求値を埋める方法や合否判定ownerを独自に決める必要があり、未依頼checkと必須check、parameter入力と検証期待値を一貫して区別できない。

**Required action / acceptance:** 要求file、明示option、またはSkillが要求照合を所有する方式のいずれかを契約化し、CLI/resultとの境界を定める。単位の既定・利用者確認、期待値、許容差、必須/任意、不明時の状態も決める。「生成幅12、必須幅10、許容差0.01」という不一致が失敗となる例と、単位未確定を確定済みとして扱わない例を追加する。新たな高度計測機能の実装を要求する指摘ではない。

### P66-DR-007 — medium — 再構築・最適化の受け入れが、品質ではなく証拠の存在だけになっている

**Location:** acceptance計画 AC-16・17 / runtime設計 §8.3 / Skill設計 Reconstruct完了条件。

**Description:** AC-16/17には分析・SCAD・比較結果を残すことや非収束を隠さないことがあるが、既知の対応形状に対する期待parameter/必要feature/許容誤差がない。比較commandの正確さを確認するAC-11は、再構築結果の品質を確認する条件ではない。

**Evidence:** AC-06/11はbbox・volume・IoUの数値基準を持つ。一方AC-16/17は、export後に比較した結果がどの程度なら受け入れ合格かを定めていない。[S1]

**Impact:** 対応modelの既知fixtureさえ復元できなくても、低いIoUの記録とlimitations説明だけでAC文面を満たせる。solver収束・計算成功・利用者要求の達成を混同する余地が残る。

**Required action / acceptance:** 少なくとも既知のprofile押出しとstadium-slotについて、期待する形状/feature、寸法またはIoU等の許容差、失敗fixtureを定める。CLIの計測成功とmodeの要求達成を分け、要求精度未達時は追加確認または未達として扱う。任意のSTLに一律100%一致を要求するのではなく、対応範囲の代表正常系と既知の非適合例に測定可能な合否を設ける。

### P66-DR-008 — medium — 読取commandと全run永続化の両立方法が未定義

**Location:** runtime設計 §3 `project list/info`、共通option、§7。

**Description:** list/infoは「読取だけ」、root不在のlistは空一覧とする。一方、§7は各実行で`.openscad/runs/<run-id>/result.json`等を保存し、出力rootが作れない場合は構造化エラーとする。読取commandの診断保存先・例外・永続化を省略できる条件がなく、共通output optionも書込commandに限定されている。

**Evidence:** 同じruntime設計のCLI表と全実行結果契約の照合による、仕様上の未決定事項である。未実装のlistが実際に失敗したとする実行証拠ではない。[S1]

**Impact:** 不存在rootに対する空一覧やread-only projectのinfoを成功させるために、対象へ書き込むか、暗黙の別出力先を作るか、保存不能で失敗するかを実装者が選ばなければならない。

**Required action / acceptance:** 読取commandのstdout-only結果、明示的な別log root、永続化optional等の方針を決める。help/通常doctor/clean dry-runにも同じ副作用境界を整理する。不在rootのlistが対象を作成せず空一覧を返す例、read-only projectのinfoがprojectを変更せず結果を返す例を具体化し、結果中に存在しないlog pathを出さないことを確認する。

### P66-DR-009 — medium — READMEの作業順序がpre-freeze gateを省いている

**Location:** `README.md`「ソフトウェア開発workflow / Codex」のフロー / hierarchy設計「Pre-freeze gate」「最終review reportの終端規則」。

**Description:** 利用者向けフローは「通常reviewと修正確認 → 独立最終review → report／PR提出」であり、通常report・tracking・handoff等を確定してからfreezeする段階がない。最終review後のreportを、予約済みfinal reportのattestationだけに限定する説明もない。

**Evidence:** 同じPRの正本hierarchyは、通常report・verification report・handoff等をfreeze前に保存し、独立最終review後は予約pathだけの1commitとHEADを変えないPR操作に限定する。[S5] READMEは正本へのlinkを持つが、図の段階区分はこの制約を表していない。[S6]

**Impact:** 図に従って通常reportを最後にcommitすると、直前の独立最終reviewを無効化する。単にreportが後に置かれていることではなく、許されるfinal attestationと非final変更の区別がない点が問題である。

**Required action / acceptance:** 通常report・handoff・trackingの確定と必要なvalidation/通常修正確認を独立最終reviewより前に置く。後段は「予約済みfinal reportの許可されたattestation、PR提出、exact-HEAD CI」のように限定する。repositoryへ追加commitが必要になった場合の通常cycleへの復帰を短く示し、READMEと階層設計で作業順序が食い違わないようにする。

## 5. 検証結果

### 現HEADのCI

| 項目 | 証拠 |
| --- | --- |
| Target/run head SHA | `cc9787604b2b3d6bfacaf714cf9485ec72ad0079`、一致をrun本体とartifact metadataで確認 |
| Workflow | `.github/workflows/release-chatgpt-worker-skills.yml` |
| Run | [34022791270](https://github.com/ssaattww/CodexSkill/actions/runs/34022791270)、pull_request、attempt 1、success |
| build job | `101458336910`、success |
| 検証step | repository Skill architecture/active links、既存ChatGPT worker ZIP build/verify、artifact uploadがsuccess |
| Artifact | `9986053406`、`chatgpt-worker-skills-34022791270`、18678 bytes、expired=false |
| Artifact digest | `sha256:e940e5d0c11895603b66d8dc017fa06443d7878318dd4bd08a8b039c7530e4b0` |
| Release jobs | PR条件でskipped |

artifactはmetadataを確認した。ZIP bytesのdownload/再展開とjob全logの取得はしていない。step successを確認したのであって、取得していないlog内容や個別processの終了値を推測していない。

既存CI成功はrepository構造・既存packageの証拠であり、Windows OpenSCAD動作や本PRの受け入れ20項目の合格ではない。

### Review-onlyのlocal probe

既設toolを使い、repository外のscratch directoryで実行した。依存packageのinstall、repository test/workflow追加、製品実装は行っていない。

| ID | Command / result |
| --- | --- |
| E1 | `python verify_design_assumptions.py`、probe driver成功。正常/unknown module/missing include/preview/export/依存file変更を確認。各OpenSCADのargv、exit、stdout、stderr、source hash、STL bbox/volumeを`results.json`へ保存 |
| E2 | `python verify_profile_topology.py`、成功。リング84→100/穴1→0、およびMultiPolygonを`profile-topology-results.json`へ保存 |
| E3 | `python verify_stadium_domain.py`、成功。正値だがlength<widthのparameterでSDF側とhull側の内外判定が異なることを`stadium-domain-results.json`へ保存 |

E1 environment: Linux `6.18.35-x86_64`、Python 3.13.5、OpenSCAD 2021.01、trimesh 4.11.1。E2: Shapely 2.1.2。PNGは既設`xvfb-run`経由。Windows/PowerShell/Codexでの実行ではない。SDF optimizer全体は実行しておらず、E3は独立した数式の反例である。

E1の依存file変更probeでは、root SCAD hashが同一でもinclude先のwidth変更でbboxとvolumeが変わった。ただし本設計の`inputs` hashがroot fileだけに限定されているとは明記されていないため、この観測だけを根拠とする追加findingは出していない。

## 6. Coverage dispositions

| Required criterion | Disposition | Evidence |
| --- | --- | --- |
| requirement/design conformance | checked_finding | DR-001、003、006、007。8mode・依頼境界も照合 |
| correctness/edge cases | checked_finding | DR-001〜005、008。local反例と上流静的読解を区別 |
| scope/unrelated changes | checked_no_finding | 全11changed file。追加overview依頼の記録あり。旧task/phase維持、コード未実装 |
| changed files/direct dependencies | checked_finding | 全差分と関係する上流profile/SDF、manual、hierarchyを確認。DR-002、003、005 |
| API/data/config/workflow/compatibility | checked_finding | DR-006、008。Windows argv/path/process/依存分離の契約も確認 |
| error handling/diagnostics | checked_finding | DR-004、008。timeout/ログ/partial/empty-result契約も照合 |
| security/secrets | checked_no_finding | shell=False、入力非破壊、junction、権限拡大禁止、環境変数dump禁止の設計。実装安全性を検証済みとはしない |
| tests/validation adequacy | checked_finding | 全AC。DR-001〜008に対応する不足例。非TDDの適用は正しい |
| current-HEAD CI | checked_no_finding | run34022791270とcc978760の一致、job/artifactを直接確認 |
| report/tracking/documentation | checked_finding | DR-009。過去snapshot表記は区別されており、古いreportを現HEAD証拠と誤認しない |
| regression/maintainability | checked_finding | DR-002、003、005、009。単一Skillと共通CLIの分割方針自体には指摘なし |

## 7. 保留・未検証・適用外

| Item | Owner / disposition / remaining risk |
| --- | --- |
| Windows実機の20 AC | 実装担当 / held。設計段階なので未実施自体はfindingにしない。I5の完了条件として残る |
| empty boolean応答・OpenSCAD版差 | 実装担当 / held。設計で検証義務とunknown時のfailed/nullが定義済み。version別の実測はない |
| Python packageのWindows固定version組 | 実装担当 / held。未解決。Linux環境の版をWindows対応証拠にしない |
| 上流copyの正式条件/notice | 利用者・実装担当 / held。コピー前のgateは維持する。法律上の許可・禁止を本reviewで断定しない |
| Markdown lint | repository maintainer / unsupported。既存reportは配線不在を記録。本reviewでも未実行。CIの構造検証を文章lintと呼ばない |
| 完成runtimeの安全性・実性能 | unexplored。Skillとscriptが未実装なので動作レビューできない。設計レビューの完了と実装承認を区別 |
| TDD / RevMem向け診断workflow追加 | not_applicable。CodexSkill policyによる |
| independent final review / passing attestation / merge | not_applicable。本依頼は通常設計review。実装・修正・mergeを行わない |

9件のrequired findingsがあるためverdictはfailである。保留事項を成功へ変換せず、逆に、計画上後続実施のWindows検証がまだないことだけを設計不具合とはしていない。

## 8. 次の作業と引継ぎ

設計作成側でDR-001〜009の対応と関連AC・READMEの整合を行い、同じPR #66へ変更を積む。実装開始の権限はこのreviewから自動付与されない。修正後はfinding ID/severityを維持し、本通常review chatでfix verificationする。HEAD更新後は新しいHEADと一致するCIを再取得する。

詳細reportとschema v3 handoffは報告専用branchへ保存する。source payloadにはcontext、reviewの完全なfindings/coverage/evidence、report全文を保持する。PRコメントは全9件の要約と詳細report参照を一括投稿する。reviewerは製品・設計の修正を行わず、mergeしない。

## 9. Source references

- S1: [runtime設計](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/openscad-runtime-design.md)、[受け入れ計画](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/openscad-acceptance-plan.md)、[Skill設計](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/openscad-skill-design.md)。
- S2: [上流profile extractor](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-profile-extract.py)。固定commitをGitHub connectorで全文読解。
- S3: [上流SDF optimizer](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-sdf-optimize.py)。固定commitをGitHub connectorで全文読解。
- S4: [OpenSCAD CLI manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_OpenSCAD_in_a_command_line_environment)。2026-09-06確認。2021.01とnightlyの説明を混同せず、local probeは2021.01に限定。
- S5: [現HEADのhierarchy設計](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/design/skill-hierarchy-design.md)。Pre-freeze gate・最終report終端規則。
- S6: [現HEADのREADME](https://github.com/ssaattww/CodexSkill/blob/cc9787604b2b3d6bfacaf714cf9485ec72ad0079/README.md)。

# OpenSCAD Skill設計

## 1. 状態と目的

- 作成日: 2026-09-06。
- 状態: 設計ドラフト作成済み。利用者確認待ち。Skill本体は未実装。
- 対象PR: [#66](https://github.com/ssaattww/CodexSkill/pull/66)。設計から実装まで同じDraft PRを使用する。
- branch: `codex/openscad-windows-skill`。base: `main`。
- 作業開始HEAD: `6507727986329e34e69da3680a00824eb1fbfe13`。
- 参照元: `andreahaku/openscad_claude_skill`、固定commit `c47ef2359a3329da45c3c2e6caa3c286133c2844`。

WindowsネイティブのCodexからOpenSCADによる設計、既存SCAD編集、STL変更、形状確認、再構築、出力を行うSkillを設計する。同時に、上流の大きな`SKILL.md`を、入口・手順・専門知識・実行処理へ分離する。

今回は設計、tracking、report、PR更新だけを行う。実行スクリプト、Skill本体、依存package、workflowは変更しない。利用者へ設計を説明した後、実装指示を受けて同じPRへ実装を積む。workerはmergeせず、設計完了だけでmerge readinessを表明しない。

## 2. 設計文書の分担

| 正本 | 所有する内容 |
| --- | --- |
| 本書 | Skillの責務、分割、読込順、mode選択、上流からの移行、配布境界 |
| [実行基盤設計](openscad-runtime-design.md) | Python module、公開CLI、Windows path／process、依存関係、結果schema、数値比較 |
| [受け入れ・実装計画](openscad-acceptance-plan.md) | 入力例と期待値、証拠、実装順序、完了／未検証の区別 |

この`design/`配下は保守者向け設計であり、配布Skillのruntime dependencyではない。配布する手順・script・templateはすべて`skills/openscad/`内へ置く。

## 3. 採用する分割方針

### 3.1 一つのSkillを内部で分割する

installable Skillは`openscad`一つとする。`openscad-codex`、`openscad-render`、`openscad-reconstruct`などへ初回から分散しない。CAD処理の入口と実行状態は共通で、同一task中にmodeを切り替えるため、独立Skillを増やすより、必要時に参照fileを読む構成を採用する。

| 候補 | 判断と理由 |
| --- | --- |
| すべてSKILLに残す | 不採用。単純なexportでも再構築・SDF等の全文がcontextへ入る |
| 八つのmodeを八つの独立Skillにする | 不採用。環境確認、path、出力契約、mode間の引継ぎが重複する |
| 一つのSKILL＋用途別reference＋Python module | 採用。入口を一つにし、詳細を必要時だけ読む |
| Claude用とCodex用に処理を複製する | 不採用。共通幾何処理と失敗判定が分岐して保守対象が増える |

OpenAIの公式説明ではSkill選択時に`SKILL.md`全文を読み、scriptやreferenceは追加resourceとして扱う。Agent Skills仕様も長い本文の分割を案内している。[S1][S2] ただしreferenceへ移動するだけで読込が自動制御されるとは考えず、本書のrouting tableをSKILLに持たせ、実際のセッションで読込挙動を検証する。

### 3.2 実装予定の配置

以下は予定構成であり、この設計commitに存在する実装file一覧ではない。

```text
skills/openscad/
├── SKILL.md
├── UPSTREAM.md
├── agents/
│   └── openai.yaml                  # 任意のCodex表示情報
├── references/
│   ├── setup-windows.md             # 初回導入と環境不足時
│   ├── cli.md                       # command、option、schema、error
│   ├── modeling.md                  # Quick／Design／Refine
│   ├── modify-stl.md                # STLをimportして局所変更
│   ├── replicate-image.md           # 写真から再現
│   ├── reconstruct-stl.md           # STLからparameter化
│   ├── validate-export.md           # Analyze／Export
│   ├── modeling-rules.md            # SCADの共通設計規則
│   ├── printer-profile.md           # 測定値と仮定、校正
│   ├── language-reference.md        # 言語仕様を調べる場合
│   └── reconstruction-techniques.md # profile／slice／SDFの専門説明
├── scripts/
│   ├── openscad.py                  # 公開CLI
│   └── openscad_lib/                # 実行・path・幾何等の内部module
├── templates/
│   ├── bracket.scad
│   ├── enclosure.scad
│   ├── printable-lib.scad
│   ├── printer-profile.scad
│   └── calibration-comb.scad
├── requirements-mesh.txt
├── requirements-optimize.txt
└── eval/
    └── scenarios.json               # シナリオ定義。成功記録ではない
```

reference名・公開CLI名・template参照は一つの変更単位で同期する。`templates/`は既存資産の役割が明瞭なため残し、形式だけのために`assets/`へ改名しない。意味の異なる資料を単に均等な行数へ切断しない。

### 3.3 SKILLに残す内容

実装時のSKILLは設計上200物理行以内を目標兼上限とする。これは本Skillの保守基準であり、Codexの必須制限ではない。Goal、Execution owner、Inputs、Outputs、Completion conditionを含め、以下の内容を省かない。

- 適用対象と非対象、八つのmodeの選択表。
- 選択したmodeで必ず読むreferenceと、条件付きで読むreference。
- Skill root／workspaceを取り違えないこと、実行capabilityの確認方法。
- 原本非破壊、未測定値を事実にしない、無断install・追加作業・権限拡大をしない、失敗を成功にしないという共通規則。
- 数値検証と画像確認を分けること、必須検証未実施時の報告・停止条件。
- 成果物、仮定、変更parameter、検証結果、残る制約を返す共通出力形式。

Bashの長い実行例、全camera preset、詳細SCAD言語解説、SDF数式、template全文、導入コマンド全文はSKILLへ置かない。commandの意味は`cli.md`、実装はscript、再利用SCADはtemplateを正本にする。

### 3.4 実行ownerと既存Skillとの境界

OpenSCAD taskのmode選択と結果説明は呼び出し元のCodex sessionが担当する。local file操作・画像確認はそのsessionの実際のtool capabilityと許可に従う。scriptはCAD処理だけを実行し、他agentを起動しない。

`openscad`は独立利用できるdomain Skillであり、`implementation-worker`、`review-worker`、`report-writer`等のソフトウェア開発lifecycleを再実装しない。Git branch、commit、PR、独立reviewの判断を持たせない。開発orchestratorから使う場合の委譲・親子判断は既存`codex-delegation-executor`等の契約に従い、このSkillに独自のsub-agent選定policyを作らない。

将来ほかのruntimeを正式対象にする場合も、共通CAD意味論を複製せず、必要なruntime固有境界だけを分離する。今回は別runtime wrapperやMCP server、Anthropic／OpenAI API呼出し層を新設しない。

## 4. 段階的読込とmode別契約

### 4.1 共通読込順

SKILLを読んでmodeを選び、下表の主referenceの該当節を読む。CLIを初めて呼ぶ場合やoption／error／schemaが不明な場合だけ`cli.md`の該当節を読む。数値計算はscriptへ任せ、通常利用でscript source全文の読込を要求しない。

導入時またはdoctorで環境不足が分かった場合だけ`setup-windows.md`を読む。modeling rulesはSCADを作成・変更するとき、printer profileは印刷条件・嵌合が関係するとき、language referenceは文法不明時に読む。SDFや複雑なsliceを使わなければreconstruction techniquesを読まない。

すべてのreferenceはSKILLから直接相対linkで到達可能にし、必読資料を深い参照chainの末端へ隠さない。主reference欠落時は対象modeをblockedとする。別modeへ切り替える場合は、その理由と新しく必要な資料を示し、依頼の範囲を超える切替には確認を取る。

### 4.2 routing table

| Mode | 選択条件 | 主reference | 主な処理と完了条件 |
| --- | --- | --- | --- |
| Quick | 単純な新規部品。不足値が安全に仮定可能 | `modeling.md`のQuick節 | SCAD作成、validation、iso一枚の確認、仮定とparameterの説明。未依頼exportはしない |
| Design | 複数featureや相互依存寸法のある新規設計 | `modeling.md`のDesign節 | 要求・寸法・部品分解、SCAD、複数view、要求値確認。承認範囲内で反復 |
| Refine | 既存SCADの局所編集 | `modeling.md`のRefine節 | 現状読解、依頼箇所だけ編集、変更前後の確認。無関係部分を保つ |
| Modify | STLの元形状をparameter化せず局所変更 | `modify-stl.md` | 原本保持、mesh／座標確認、import＋boolean、変更差分確認 |
| Replicate | 写真の物体を再現 | `replicate-image.md` | 画像と既知寸法、分解案、同じ角度で比較。画像だけで絶対寸法を断定しない |
| Reconstruct | STLを編集可能なSCADへparameter化 | `reconstruct-stl.md` | mesh・profile・slice分析、手法選択、SCAD、mesh比較、近似限界の説明 |
| Export | 既存SCADを指定formatで出力 | `validate-export.md`のExport節 | 指定parameterでvalidation／出力。要求formatを黙って減らさない |
| Analyze | 既存形状の寸法・mesh・印刷上の制約を確認 | `validate-export.md`のAnalyze節 | 計測可能項目だけ判定し、未測定・未実装checkを分離 |

Quick／Design／RefineはSCAD作成編集の共通規則が多いため同じreference内で分ける。Analyze／Exportはvalidationと成果物判定を共有するため同じreferenceへまとめる。STL再構築は専門知識と計算負荷が異なるので独立したreferenceとする。modeをまとめたことは必読節をすべて読む指示を意味しない。

### 4.3 共通契約と用途別詳細の重複を防ぐ

共通禁止事項と最終報告項目はSKILLだけを正本とする。mode文書はそれを再定義せず、入力・前提・固有手順・必要出力・固有の停止条件を持つ。共通CLI option・error codeをmodeごとにcopyしない。短い呼出例を置く場合は実CLIに対する検証対象に含める。

`modeling-rules.md`はparameter、derived dimensions、profile-first、body／additive／subtractive featureの分離、epsilon、assertの使い方を所有する。全モデルに単一のCSG順序を機械的に強制せず、必要形状と検証結果で選ぶ。

## 5. Claude依存とWindows対応の判断

| 上流の要素 | 設計上の扱い |
| --- | --- |
| `name`／`description`＋Markdown | 基本形式を維持。descriptionはOpenSCAD対象を先頭で明確にする |
| `argument-hint`、Claude tool名列挙 | Claude依存の表示・権限指定を除去。Codex権限へ機械変換しない |
| `Read`／`Edit`／`Agent`の名称 | 実際のfile編集・画像閲覧capabilityへ置き換える。sub-agentを必須にしない |
| `.claude`固定path | Skill rootから解決。生成README・SCAD comment・導入例も対象 |
| `/openscad`の例 | Codex CLI／IDEでは`$openscad`等の公式導線に合わせる |
| 六本のBash script | Pythonの公開CLIと内部moduleへ移す。BashをWindowsの必須依存にしない |
| Python数値処理 | アルゴリズムの候補として評価し、path・I/O・失敗判定を新契約へ適合させる |
| OpenSCAD template | 取り込み条件確認後に流用。必要なものだけprojectへcopy |
| `~/openscad-projects`固定出力 | workspace内を既定とし、明示指定と許可を尊重する |
| プリンター設定をSkill内で更新 | templateは不変、測定値はproject側で管理する |

`allowed-tools`というfield自体はAgent Skills仕様にも存在する実験的項目だが、上流の具体的なtool名と権限意味論をCodexへそのまま移さない。[S2] `agents/openai.yaml`は任意の表示metadataであり動作必須ではない。採用時も表示名・短い説明・既定promptに限定し、workflowや権限policyを別の正本として持たせない。[S1]

WindowsではPython本体を基本依存とし、追加packageはcommand別に確認する。`openscad.com`探索、`;`区切りのlibrary path、Unicode／quote、一時file、終了値、子process終了、成果物の新旧識別は実行基盤設計を参照する。WindowsネイティブのCodexとそのsandboxがあることを前提に設計するが、特定利用者環境での成功は実機証拠で判断する。[S3]

## 6. 形状理解と完了判定

形状の確認は、SCADの構造とparameter、PNGの複数方向の見え方、meshの寸法・体積・断面・差分を組み合わせる。PNGを一枚出しただけで内部形状・局所壁厚・製造適合性を保証しない。既存SCADのhistoryを別途復元する機構は作らない。

modeごとの必須checkを先に定め、数値checkはscriptのresult、視覚checkはsessionの実際の画像閲覧と所見で証拠を分ける。画像確認toolがなければ、その事実と未確認範囲を返す。画像を見ずに見たと報告しない。

最終報告では成果物path、選択mode、利用者指定値、仮定、変更したparameter、計測結果、視覚所見、未確認項目、必要な次の判断を示す。処理失敗、依存不足、要求外作業が必要な状態を完了として隠さない。exportだけの依頼に視覚確認を無条件で追加せず、必要性は要求とmode契約で判定する。

## 7. 上流からの移行と不整合

参照元のREADMEだけではなく、固定commitのfile tree、SKILL本文、scriptを照合した。以下は静的読解に基づく事実と、その設計上の処置である。実機再現済みという意味ではない。

| ID | 確認した状態 | 移行時の処置 |
| --- | --- | --- |
| U-01 | SKILLに`openscad-auto-reconstruct.py`の手順があるがfile treeにない | 案内を削除。汎用自動再構築の新規実装は本移植に含めない |
| U-02 | SKILLはvalidateが常に0で終了すると説明するがscript末尾は取得したexit codeを返す | 説明を修正し、結果schemaと終了値を正本にする |
| U-03 | compareは不在差分STLの体積を0とし、PNG失敗が数値算出にも影響する | 数値と画像を分離。empty／failedを分け、未知metricはnull |
| U-04 | compareのaccuracyはIoUではなく原体積で正規化した差分率 | metricを定義名で分離。旧値をIoUと呼ばない |
| U-05 | Quick等の検証説明がscriptの計測範囲より広い | compile／parameter／mesh／visual／物理印刷を別checkにする |
| U-06 | 少数SVG sliceにないfeatureは存在しないと断定する説明がある | 観測範囲外は未確定とする。別軸・密なsliceなどの条件を明記 |
| U-07 | SDFのSCAD生成は`stadium-slot`以外で未提供commentを返す | 対応modelと生成可否を明示し、commentだけのfileを成功にしない |
| U-08 | READMEの20/20成功は旧評価一行で、Windows Codexの実行証拠ではない | scenario定義だけを移行候補とし、結果は新規実行で記録 |
| U-09 | READMEはMITと記載するが独立LICENSE fileはなく、APIのlicense判定もnull | 事実を出典台帳へ記録。コピーによる再配布前に正式条件・noticeを確認 |

根拠は[S4]〜[S8]。U-09から法的な許可／禁止を断定しない。著作者・年・license全文を推測で作らない。確認できない場合の独自実装への変更や上流への問い合わせは、利用者へ確認してから行う。

## 8. 導入・配布と既存設計との関係

Codexの公式local Skill配置であるuserの`.agents/skills`、またはprojectの`.agents/skills`へ`openscad`directoryをcopyする導線を使う。管理者権限が絡むsymlink作成を標準手順にしない。resourceの参照は配置場所に依存しない。[S1]

`UPSTREAM.md`は固定commit、流用file、変更file、独自file、noticeの出典を記録する。`eval/scenarios.json`は期待結果の定義であり、実行結果と明確に区別する。既存のChatGPT worker用ZIPにはOpenSCADを追加しない。新しい自動releaseやplugin化は本設計の対象外。

実装が存在するようになった時点で`design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`をbyte-identicalに更新し、独立利用可能なCAD domain Skillとしてinventoryと責務を反映する。設計だけの現在はinstalled inventoryや既存Skillのcall graphを変更しない。runtime wrapperの依存や既存8 Skillの配布構成は変更しない。

Skill実装時は既存`skill-authoring-wrapper`の手順を使い、built-in initializerの利用可否も実環境で確認する。初期化toolが使えない場合は未使用と記録し、使ったと装わない。repository外shared dependencyや別runtimeの共通contract複製を導入しない。

## 9. 検証・提出方針

作業開始時に`.github/workflows/release-chatgpt-worker-skills.yml`を確認した。既存workflowはPR HEADをcheckoutし、repository validatorとChatGPT用ZIP buildを実行する。artifactは生成ZIPであり、失敗時のstdout・stderr等を一式保存する診断workflowではない。

CodexSkillはTDDとRevMem向け診断artifact workflow追加方針の対象外である。設計だけのためにtest、lint設定、workflowを追加しない。既存repository validator／ZIP buildの成功をWindows OpenSCAD検証と混同しない。Markdown lintのrepository配線がない場合はunsupportedとして残す。

CIはPRのcurrent HEAD SHAとrunの`head_sha`が一致するものだけを確認する。HEAD更新後は再取得し、一致runがなければCI未実施と記録する。各実装段階の具体的な終了条件と未検証事項は受け入れ・実装計画を正本にする。

詳細reportをrepositoryへ、要約をPRコメントへ保存する。実装後も同じPR #66を使い、mergeは利用者が行う。

## 10. 参照

外部仕様は2026-09-06に確認。上流repositoryはGitHub connectorで参照し、branchの移動に影響されないcommit固定linkを記す。

- [S1: OpenAI・Build skills](https://learn.chatgpt.com/docs/build-skills)
- [S2: Agent Skills specification](https://agentskills.io/specification)
- [S3: OpenAI・Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [S4: 上流SKILL](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/SKILL.md)
- [S5: 上流file tree](https://github.com/andreahaku/openscad_claude_skill/tree/c47ef2359a3329da45c3c2e6caa3c286133c2844)
- [S6: 上流validate](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-validate.sh)
- [S7: 上流compare](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-stl-compare.sh)
- [S8: 上流SDF optimizer](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/scripts/openscad-sdf-optimize.py)
- [S9: 上流README](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/README.md)
- [S10: 上流評価記録](https://github.com/andreahaku/openscad_claude_skill/blob/c47ef2359a3329da45c3c2e6caa3c286133c2844/eval/results.jsonl)

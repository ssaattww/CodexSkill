# T-004 OpenSCAD Skill設計報告

## 1. 対象と状態

- 作成日時: 2026-09-06 17:14:58 Asia/Tokyo。
- report type: `implementation_report`。対象は設計文書の作成であり、Skill機能の実装完了報告ではない。
- repository: `ssaattww/CodexSkill`。
- PR: [#66](https://github.com/ssaattww/CodexSkill/pull/66)、Draft／open。
- branch: `codex/openscad-windows-skill`。base: `main`。
- 作業開始HEAD: `6507727986329e34e69da3680a00824eb1fbfe13`。
- 本報告の設計・検証snapshot HEAD: `09d11531690dd28d1e403e33968d00c3ff6f6886`。
- 上流参照commit: `andreahaku/openscad_claude_skill@c47ef2359a3329da45c3c2e6caa3c286133c2844`。
- reviewed implementation HEAD: null。独立reviewは実施していない。

利用者の依頼に従い、詳細設計より先にPRを作成した。今回は設計3文書とtask／phase trackingを作成・更新し、実装を開始していない。同じPRへ実装を積み、実装後のmergeは利用者が行う。

## 2. 要求と成果物

依頼は、Claude向けOpenSCAD SkillのCodex／Windows対応に加え、大きなSKILL本文の分割を含めて設計し、PRへ保存して説明することである。

| 変更file | 目的 |
| --- | --- |
| [openscad-skill-design.md](../design/openscad-skill-design.md) | 一つのSkill内の責務分割、必要時読込、八つのmode、上流移行と配布境界 |
| [openscad-runtime-design.md](../design/openscad-runtime-design.md) | Python CLI、Windowsのpath／process／依存、結果schema、比較と失敗の判定 |
| [openscad-acceptance-plan.md](../design/openscad-acceptance-plan.md) | D-01〜06、実装AC-01〜20、具体的なfixture・期待値、段階別の検証 |
| [tasks-status.md](../tasks/tasks-status.md) | T-004とP66-D／I1〜I5、依存関係、終了条件、未実装状態 |
| [phases-status.md](../tasks/phases-status.md) | Phase 9と設計から実装・検証までのmilestone |

Skill本体、実行script、template、依存package、workflow、既存8 SkillのChatGPT worker ZIP構成は変更していない。未実装のSkillをinstalled inventoryへ登録していないため、二つのhierarchy designは今回変更せず、実装時の同期を計画した。

## 3. 主な設計判断

### Skill分割

`openscad`一つをinstallable unitとし、SKILLには入口・共通契約・mode routingを残す。八つの独立SkillやClaude／Codex別の処理コピーは作らない。SKILLの200物理行以内という上限は本設計の保守基準であってCodex仕様の制約ではない。

用途別referenceは、作成・編集、STL局所変更、写真再現、STL再構築、検証・出力の5系統にまとめる。環境導入、CLI、言語仕様、プリンター設定、再構築技法は必要条件に応じて追加読込する。単純なSTL出力で再構築・SDF資料を読ませない。実際の読込挙動は実装後のCodexセッションで確認する。

### Windows実行

Bashを必須にせず、公開CLIをPythonに統一する。これは基本操作にもPython本体が必要になる変更である。基本操作は標準library＋OpenSCADで扱い、NumPy／trimesh／SciPy等は必要なcommandでだけ要求する。

WindowsのCLI探索は明示指定を優先し、未指定時にPATHの`openscad.com`を使う。`;`区切りのOPENSCADPATH、空白・日本語・apostrophe、SCAD stringとargvのescape、workspace内出力、timeout時の自分の子process treeの終了、stdout／stderr保存を契約化した。自動installやsandbox緩和は行わない。

### 確認と失敗判定

SCAD構造、画像、mesh計測を併用する。PNG生成とCodexによる画像確認は別の証拠とし、画像toolがなければ視覚確認未実施とする。compile／assertの成功を全局所壁厚や実際のprint fitの保証にしない。

比較では数値計算をPNGから独立させ、差分を`nonempty|empty|failed`に分ける。file不在を体積0と解釈せず、算出不能metricはnullとする。旧accuracyとvolume IoUを混同しない。10 mm cubeで同形は1、Xへ5 mm移動は1/3、非重複は0という期待値を受け入れ条件へ記載した。

### 上流との差分

存在しないauto-reconstruct script、validate終了コードの説明不一致、比較失敗の0扱い、計測範囲の誇張、有限sliceからの不存在断定、SDFのgenerator未対応、旧20/20記録を移行上の論点として整理した。これらは固定commitの静的読解による確認であり、Windowsで再現した不具合一覧ではない。

上流READMEはMITと記載する一方、LICENSE file不在とAPIのlicense未判定を確認している。法的な許可／禁止は断定せず、コピーによる再配布前に正式条件・noticeを確認する。上流へのIssue投稿やlicense文面の創作は行っていない。

## 4. 参照した規則と証拠

アップロード済みworker skillsのwork-context、implementation、report、ChatGPT wrapper／handoff契約を読み、設計編集と報告の範囲へ適用した。repositoryのAGENTS、design-doc-maintainer、design-executor、skill-authoring-wrapper、task管理、Markdown checker、report命名規則を参照した。

外部仕様はOpenAIのBuild skills／Windows sandbox、Agent Skills specification、OpenSCAD manualのCLI／Librariesを確認した。上流はREADME、SKILL、file tree、render／validate／project／STL解析・比較・再構築、Python補助処理、評価記録を参照した。根拠URLは設計文書末尾に記載している。

repositoryの参照・branch作成・file更新・PR作成はGitHub connectorで実行した。Git CLIやCIを使ったrepository書換えは行っていない。

## 5. 検証結果

### Snapshot HEADに一致するCI

PR情報のHEADとworkflowの`head_sha`が、ともに`09d11531690dd28d1e403e33968d00c3ff6f6886`であることを確認した。

| 項目 | 結果・証拠 |
| --- | --- |
| Workflow | `Validate and release ChatGPT worker skills` |
| Run | [34021277675](https://github.com/ssaattww/CodexSkill/actions/runs/34021277675)、attempt 1、success |
| build job | `101454211990`、success |
| repository validator | `python3 scripts/verify_skill_repository.py`に対応するstepがsuccess |
| ZIP build／構造確認 | `python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip`に対応するstepがsuccess |
| artifact upload | success |
| artifact | ID `9985565871`、`chatgpt-worker-skills-34021277675`、18678 bytes、expired=false |
| artifact digest | `sha256:04c530e2e19bf21a650f7fd1fe2ad1f3bc07f3c800a5e1acc8338821f83d81d6` |
| release系job | PR条件によりskipped。releaseは実行していない |

artifactはmetadataとupload／build stepを確認した。ZIP bytesをこのチャットへdownloadして再展開する検証は行っていない。CIの成功はrepositoryの構造・active link・既存ZIPの検証であり、OpenSCADのWindows実行証拠ではない。

### 文書・scope確認

変更filenameを列挙し、設計3文書とtracking2文書以外に実装変更がないことを確認した。task／phase patchをbaseと比較し、転記中に混入した旧記録の変更を修正した。最終差分では、既存T-001〜003とPhase 1〜8の本文を変更していない。段階別のACは担当範囲を示し、未実装部分を全体合格にしないことを設計とtrackingへ追記した。

### 未実施・unsupported

| 項目 | 状態 | 理由と扱い |
| --- | --- | --- |
| focused Markdown lint | unsupported | repository rootにpackage.json／tools/lintがなく、既存checker契約を満たす配線がない |
| full Markdown lint | unsupported | 同上。成功とせず、設計提出の残リスクとして保持する |
| local repository validator／ZIP再build | not_run | 今回はconnectorとremote CIで確認。localで実行したとは報告しない |
| Windows OpenSCAD／Python package／PNG閲覧 | not_run | 設計段階で実装・実機受け入れを実行していない |
| 独立review | not_run | 本報告は設計作成者の自己点検であり、独立review verdictを生成しない |
| TDD／Red-Green証拠 | not_applicable | CodexSkillのrepository policyにより適用しない |

作業開始時に既存workflowを確認した。ZIP artifactはあるが、失敗時stdout／stderr等の一式保存は定義されていない。RevMem向けの診断artifact追加方針はCodexSkillには適用せず、今回workflowは変更していない。

## 6. 変更履歴と提出状態

設計は初期scope、Windows runtime、受け入れ、Skill分割、trackingの論理単位でcommit／pushした。追記時の転記修正も同じbranchで行った。履歴はPRのcommit一覧で追跡できる。

- PR作成前の初期scope: `5c5a4af7025d1cb2407edce5de0dbf38f0b095e8`。
- runtime設計: `a9cd90b8ee33e9bca8ce23e17e344e12907b38b9`。
- 初期受け入れ計画: `4d981403c7dde40b45a251a18ff6b40c404d4775`。
- Skill分割設計: `d9e474b04527031b0be77b40928ac27a1ae92ca5`。
- tracking追加: `aee54095db902b42e1eef6ad34b9b20640836560`、`bb37d595ff8c68356920a47c266d0db9a5d8df13`。
- tracking整合・旧記録保持: `af6e1913f6395eb61b2d3a428a7c35baed3f9cb5`、`4ec7b91387b1e25f19a781afdb0ebb03e6d79bea`、`00f4237a20fe19326740a3b715ee952211fa0b5a`、`5693b7a01251f0586bcadc948fce1d178aeaaa43`、`c61a5d8398cc1742c3d1a29a80ec016dfb2b94e3`。
- 段階別確認と最終ACの分離: `09d11531690dd28d1e403e33968d00c3ff6f6886`。

snapshot時点は`committed`、`pushed`、`ci_wait_completed`。本報告とhandoff保存後はHEADが更新されるため、その最終HEADと一致するCIを別途確認し、PRコメントへ記録する。本報告自身の未確定commit SHAは本文へ捏造しない。保存は通常のrepository fileであり、独立最終reviewのreport-attestationではない。

## 7. 残る判断と次の作業

設計ドラフトは保存済みであり、次は利用者の設計確認・実装指示である。今回の許可は設計とその提出までで、後続chatへコード実装権限を自動移譲しない。

実装時は取り込み条件を確認し、P66-I1から同じPRへ積む。Windowsの実際のOS／Codex／Python／OpenSCAD version、package組合せ、empty boolean応答、PNGを開いた証拠は未確定であり、ACで確認する。未検証を解消するまでWindows対応完了やmerge可能な完成版とは表明しない。

mergeは利用者が行う。workerはmergeしていない。

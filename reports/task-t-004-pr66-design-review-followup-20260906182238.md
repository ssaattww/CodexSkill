# PR #66 OpenSCAD設計review指摘対応report

## Metadata

- Date: 2026-09-06
- Repository: `ssaattww/CodexSkill`
- PR: #66
- Branch: `codex/openscad-windows-skill`
- Mode: review follow-up
- Review対象設計snapshot: `cc9787604b2b3d6bfacaf714cf9485ec72ad0079`
- 指摘対応開始HEAD: `ec39c07d43d61c05a297af573e28672a056bcf94`
- 設計修正HEAD: `92a10a5c35a67790b50991627a8ff4f9b461b6f2`
- Merge: 実施しない

## Scope

PR #66の設計reviewで統合された8論点だけを対象に、OpenSCAD Skillの実行基盤契約と受け入れ条件を修正した。Skill本体、Python実装、workflow、README、hierarchy設計、既存ChatGPT worker ZIP構成は変更していない。

CodexSkill repository policyによりTDDは適用しない。今回の変更は設計契約と将来の受け入れfixtureの具体化であり、Windows OpenSCAD実機受け入れを実施済みとは扱わない。

## Source review

GitHub PR review `PRR_kwDOSFr3-88AAAABMXaucw`で、次の8論点が必須修正として統合された。finding IDと元重要度表記を維持する。

| Finding | 元重要度 | 対応 |
| --- | --- | --- |
| `P66-DR-001` | P1 | warning policyを明示し、未定義module／欠落include等をexit 0・非空成果物だけで成功にしない |
| `P66-DR-002` | P1 | 探索previewと最終verify PNGを分離し、exportと最終PNGの評価条件を一致させる |
| `P66-DR-003` | P2 | profileのouter ring／hole／複数component topologyを欠落なく保持する |
| `P66-DR-004` | P2 | source frameとanalysis frameの変換・逆変換・round-trip契約を定義する |
| `P66-DR-005` | P2 | solver／compile成功と形状品質合格を分離し、Reconstruct品質gateを定義する |
| `PR66-DR-002` | medium | dependency hash、override、artifact hashを含むshape identityでcommand間の同一形状を確定する |
| `PR66-DR-005` | medium | junction、同一file identity、既存成果物、同時runのwrite collision規則を定義する |
| `PR66-DR-006` | medium | timeout／異常終了時にhelper SCAD等をcleanup前に診断領域へ退避する |

## Changed files

### `design/openscad-runtime-design.md`

実行契約へ以下を追加した。

- `render --purpose explore|verify`を定義し、verifyと`export --format all`のPNGを`$preview=false`の最終評価条件へ固定した。
- `source_identity`を追加し、root source、再帰的に解決可能な`use`／`include`／`import`依存hash、effective `-D` override、OpenSCAD version、identity completenessを保持する。
- artifact hashとparent source identityを関連付け、別条件のrunを同じcandidateの証拠として自動統合しない。
- validation gateでblocking warningを成功にしない規則を追加した。対応versionでは`--hardwarnings`または同等のdiagnostic分類を要求する。
- timeout／異常終了時はcleanup前にhelper SCAD、stdout／stderr、input manifest、途中成果物状態を`.openscad/runs/<run-id>/diagnostics/`へ退避する。
- write targetのjunction／symlink再確認、入力／出力のfile identity照合、既存成果物の既定no-clobber、明示replace時のstaging＋atomic replace、同時runのtarget claimを定義した。
- profileをconnected componentごとのouter ring／inner ringとして保持し、holeをunionで埋めたり最大componentだけ残したりしない規則を追加した。
- `source_frame`／`analysis_frame`と4x4変換matrix、逆変換、source frameへ戻したcandidateでの比較を定義した。
- Reconstructの`solver_succeeded`、SCAD生成、compile、mesh export、metric availability、quality targetを別checkにし、既定`volume_iou >= 0.95`を品質gateとした。

Commit: `4b5beb1c8d2f2489dc38699a71a3fb76b858d87a`

### `design/openscad-acceptance-plan.md`

8論点を将来の実装で再現可能なfixtureへ落とし込んだ。

- AC-06／19: dependency hash・override・artifact hashによるshape identityの一致／不一致。
- AC-07／10: `$preview ? 10 : 20` fixtureで探索PNGとverify PNG／STL／3MFの評価条件を分離。
- AC-08: 未定義module／欠落includeと正常cubeを同居させ、OpenSCADがexit 0でもvalidation成功にしないfixture。
- AC-13: timeout後、通常temp cleanup後にもhelper SCADとstdout／stderr等の診断を開けること。
- AC-14: workspace外junction、同一file identity、既存同名成果物、同時runの衝突を検査すること。
- AC-16: 外10x10・穴4x4の材料面積84 mm2、押出高10 mmの体積840 mm3、複数component／hole保持、変換matrix round-tripを確認すること。
- AC-16／17: Reconstructの既定`volume_iou >= 0.95`、solver／compile／qualityの分離、品質未達をtask完了にしないこと。

Commit: `92a10a5c35a67790b50991627a8ff4f9b461b6f2`

## Validation

設計修正HEAD `92a10a5c35a67790b50991627a8ff4f9b461b6f2`と完全一致するpull request workflow runだけを確認した。

- Workflow run: `34024453007`
- `head_sha`: `92a10a5c35a67790b50991627a8ff4f9b461b6f2`
- Conclusion: `success`
- Build job: `101462821726`
- Repository Skill architecture／active-link validation: success
- ChatGPT wrapper／core Skill ZIP build・verify: success
- Artifact upload: success
- Artifact: `chatgpt-worker-skills-34024453007`
- Artifact ID: `9986587300`
- Size: 18678 bytes
- Digest: `sha256:8c3e298e657f7fca15cd75b51234544676be7b4d71355ba409bb2d75c9fb38ff`

このCIはrepository設計・配布整合の証拠であり、Windows上でのOpenSCAD runtime、PNG閲覧、profile／SDF品質fixtureの実行証拠ではない。それらは実装後の受け入れ条件として未実施のまま保持する。

Markdown lintはrepository内のlint配線がないため`unsupported`のまま。今回その配線は追加していない。

## Intentionally untouched

- `README.md`: reviewで追加指摘なし。
- `design/skill-hierarchy-design.md`／`skills/design/skill-hierarchy-design.md`: domain Skill分離に追加指摘なし。
- `design/openscad-skill-design.md`: 8論点はruntime／acceptance契約に閉じており、mode分割契約は変更不要。
- `skills/openscad/`: 未実装。今回のreview follow-upでは実装開始しない。
- workflow: CodexSkillの既存validation経路を使用し、新しいWindows CIは追加しない。

## Remaining state

8論点に対する設計修正は上記2文書へ反映した。これは実装workerによる指摘対応であり、修正済みという独立review verdictは出さない。同じfinding IDを保持したfix verificationが次のreview actionである。

Windows実機検証、Codexによるverify PNG閲覧、OpenSCAD version別warning／empty boolean挙動、Python package固定version、上流資産の取り込み条件は引き続き未確定または未実施である。

PRはDraftのまま維持し、workerはmergeしない。

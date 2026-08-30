# PR #65 R2指摘対応レポート

## メタデータ

- repository: `ssaattww/CodexSkill`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- branch: `feat/adaptive-agent-assignment`
- 対応対象review: R2
- 対応前HEAD: `3ae8a067b648ffbbc956fdc651f3bdfa7b1316d2`
- 技術修正HEAD: `fedaeaa93f1425ada5a3cd3f8f64a604d5203c1f`
- development policy: CodexSkill repository maintenanceはnon-TDD

## 対応した指摘

### F65-R2-001 / HIGH

指摘:

`requested`と`applied`の時系列が逆転しており、spawn前に`applied`を確定した上でその値をspawn引数へ使用する契約になっていた。

対応:

- `requested`をpre-spawn instructionとして固定
- spawn前は`applied: null`、`application_status: pending_runtime_result`とする
- actual spawn argumentsには`requested` model / reasoning effortを使用
- full-historyの場合はincompatible overrideを付けず、runtime path成立後にparent inheritanceを`applied`として記録
- spawn result / rejection / fallback evidenceを得た後だけ`applied`と`application_status`を記録
- rejected requested profileを`applied`へcopyしない
- hidden runtime stateはchildではなくparentが記録する

変更:

- `skills/sub-agent-task-manager/SKILL.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`
- `skills/report-output-manager/references/sub-agent-report-template.md`
- `design/adaptive-agent-assignment-design.md`

### F65-R2-002 / HIGH

指摘:

new independent-final reviewerを`sub-agent-task-manager`経由にした結果、通常sub-agentと同じ「report fileをdispatch前に作成しchildが編集する」契約が、independent-final-reviewのreport-attestation lifecycleと衝突した。

対応:

report persistenceを2modeへ分離した。

`normal_persistence`:

- implementation / verification / normal review / fix verificationで使用
- dispatch前にstandard reportを作成可能
- freeze前にpersist / commitする

`deferred_attestation`:

- independent final review / bounded independent closureで使用
- freeze前はexact report pathをmetadataとして予約するだけ
- repository report fileを作成・pre-populate・編集しない
- reviewerはstructured review evidenceをparentへ返す
- parentがreviewer outputとdispatch profile evidenceをrepository外のlifecycle evidenceとして保持
- fail時はreportをpersistせずimplementationとnormal fix verificationへ戻る
- same independent reviewer closureでもreport pathは未作成を維持
- passing verdict後のみ`report-writer`と`report-output-manager`がreserved pathへ初回persistし、1件だけのreport-attestation commitを作る

変更:

- `skills/sub-agent-task-manager/SKILL.md`
- `skills/review-enforcer/SKILL.md`
- `skills/report-output-manager/SKILL.md`
- `design/adaptive-agent-assignment-design.md`

### F65-R2-003 / HIGH

指摘:

review taskが`sub-agent-task-manager`で`independent_workstreams`へ再分類されると、review-enforcerの1 normal reviewer / 1 fresh exhaustive independent reviewerというidentity保証が崩れる。

対応:

`review-enforcer`が作る全new reviewer taskへ次を固定した。

```yaml
decomposability: single
decomposition_policy: forbidden
parallelism_mode: single_agent
```

- normal reviewer
- replacement reviewer
- independent final reviewer

すべて1 reviewer固定とする。

`sub-agent-task-manager`とprofile selectorはcaller-owned `decomposition_policy: forbidden`を優先し、このtaskを`codex-delegation-executor`へmulti-agent decompositionとして戻さない。

review scopeが大きいこと自体はdecomposition理由にしない。multi-agent review lifecycleを正式設計していないため、現行review identity / continuity / one exhaustive passを維持する。

変更:

- `skills/review-enforcer/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `design/adaptive-agent-assignment-design.md`

## 追加整合化

### Dispatch profile section ownership

standard sub-agent report templateの`Dispatch profile` sectionをparent-ownedとして明記した。

parent pre-dispatch:

- selection inputs
- selection source
- proposed / approval
- requested
- fork / constraints

parent post-runtime:

- applied
- application status
- fallback / inheritance evidence

childはhidden spawn argumentsまたはruntime applicationを推測しない。

### 設計書

`design/adaptive-agent-assignment-design.md`を現行契約へ整理した。

- requested -> spawn -> appliedの時系列
- caller-owned decomposition prohibition
- single reviewer lifecycle
- normal persistence / deferred attestation
- independent final reportのmetadata-only reservation
- passing verdict後だけのreport attestation

## commit

R2対応の主なcommit:

- `0a967fcac5eadbeb989f10cbe9a6f639cab765f1`: dispatch timingとfinal-review report boundaryを修正
- `2d1500982d3bae78f3dccc646256b81debbbb29c`: single reviewer / deferred-attestation review lifecycleを修正
- `35e4cd2ce10ce04901f08e06773e662dd192fedd`: independent-final report pathをmetadata-only reservationへ変更
- `4820b49867ba40fbd0e961ff918430f95390b2e8`: profile schemaとdecomposition lockを修正
- `34c7aedcbc4a5ad742cb38876d6ad15fb183c50f`: standard reportのdispatch evidence ownershipを明記
- `b7d34ed8807d35a348038bdb4c66883f259646bb`: spawn application時系列を中央referenceへ明記
- `fedaeaa93f1425ada5a3cd3f8f64a604d5203c1f`: 設計書を現行contractへ同期

## 検証

技術修正HEAD:

`fedaeaa93f1425ada5a3cd3f8f64a604d5203c1f`

GitHub Actions:

- workflow: `Validate and release ChatGPT worker skills`
- run ID: `33246215564`
- run number: `181`
- run head SHA: `fedaeaa93f1425ada5a3cd3f8f64a604d5203c1f`
- build job: `99084021821`
- conclusion: `success`

成功step:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

artifact:

- name: `chatgpt-worker-skills-33246215564`
- ID: `9712913941`
- digest: `sha256:e96d321210333ae6b47aa7f0c55ac55fefba45580f4da1ea61ce2b83b5506728`
- artifact head SHA: `fedaeaa93f1425ada5a3cd3f8f64a604d5203c1f`

別SHAのrunはこの技術修正HEADの検証には使用していない。

このreport追加後はPR HEADが変わるため、final exact-head CIは新しいHEADとrun head SHAの一致を別途確認する。

## failure diagnostics

- test / validator failure: なし
- failure stdout: なし
- failure stderr: なし
- failure investigation artifact: 不要
- validation artifact: 正常生成済み

## 残存リスク

- hidden `collaboration.spawn_agent` override自体のlive integration fixtureはrepositoryに存在しない
- runtime model availability APIはrepositoryに存在しない
- multi-agent review lifecycleは今回のscope外。現行reviewはsingle reviewer固定

これらは今回のR2 findingのclosureを妨げる未解決required actionではない。

## 結果

F65-R2-001、F65-R2-002、F65-R2-003の3件に対し、spawn時系列、independent-final report attestation、reviewer identity/decompositionの各contractを修正した。

mergeは行っていない。

# PR #65 R4 指摘対応レポート

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- 対応開始時HEAD: `d56be39ce7e69a6fd051dea684f9b0be6958fec0`
- R4技術修正HEAD: `7db502a389fba91a079719fbfab1c60b4a06a6c8`
- 対象finding:
  - `F65-R4-001 / HIGH`
  - `F65-R4-002 / HIGH`
  - `F65-R4-003 / MEDIUM`

CodexSkill repository自身の保守であるため、repository policyに従いTDDは適用していない。

## F65-R4-001

### 指摘

R3で`sub-agent-task-manager`がmetadata-hidden runtimeの正常系を次の状態として許容した一方、上流`codex-delegation-executor`が依然としてexact `applied` profileを必須としていた。

```yaml
applied: null
application_status: spawn_succeeded_profile_unverified
```

このためtask managerが正しく完了してもdelegatorのcompletion contractを満たせない矛盾があった。

### 対応

`skills/codex-delegation-executor/SKILL.md`をR3 runtime-observability contractへ同期した。

sub-agent evidenceとして次を必須系列に変更した。

- `requested`
- `role_plan`
- `planned_runtime_profile`
- `profile_observability`
- exact `applied`はparent-visibleなfinal profile evidenceがある場合のみ
- exact profileが見えない場合は`spawn_succeeded_profile_unverified`等のexplicit state
- inherited / fallback / capability-gap state

Outputs / Evidence rules / Completion conditionの全てで、exact `applied`を無条件必須にしない。

また、ordinary `normal_persistence`とindependent-final `deferred_attestation`を分離し、後者ではpre-created reportの直接編集を要求しないよう修正した。

主commit:

- `350ae95ade140a9237f7f68f4eb4cb54b6a8cd31` `fix: sync delegation evidence with runtime observability`

## F65-R4-002

### 指摘

independent-final report path reservationのownerが二重化していた。

- `review-enforcer`がfreeze前にreservation-only phaseでpath予約
- その後`sub-agent-task-manager`も`deferred_attestation`でreservation phaseを再実行

2回目が別pathを返した場合、freeze前reservation identityが失われる可能性があった。

### 対応

reservation ownershipを`review-enforcer`へ一本化した。

`review-enforcer`がpre-freezeで一度だけ次を確定する。

```yaml
reservation_owner: review-enforcer
reservation_identity: <stable identity>
pre_reserved_report_path: <exact path>
reservation_state: metadata_only
```

`sub-agent-task-manager`は`deferred_attestation`時に次を行う。

- callerから上記reservation evidenceを必須inputとして受け取る
- reservation ownerが`review-enforcer`であることを確認
- pre-freeze metadata-only reservationであることを確認
- repository fileがまだ作成・変更されていないことを確認
- **reservation-only phaseを再実行しない**
- missing / ambiguous / post-freeze / materialized reservationはblockerとして扱う
- bounded independent closureでも同じreservation identityを維持する

主commit:

- `169711aacb6a9d69ab6f39793c9a9a0d2c6f732e` `fix: reuse independent review report reservation`
- `e5ecf0b5f90667427c98452a64d418d007e9ebe2` `fix: make review enforcer reservation owner`

## F65-R4-003

### 指摘

`adaptive-agent-assignment-design.md`のdeferred-attestation意味論がSkill hierarchy正本／mirrorへ同期されておらず、正本にはindependent reviewer自身がreportを作るように読める契約が残っていた。

また`codex-delegation-executor`にも全reviewerへpre-created report直接編集を要求する記述が残っていた。

### 対応

`design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`を同一blobでatomicに更新した。

正本へ次を明示した。

1. normal reviewerは`normal_persistence`
2. independent-final review前に`review-enforcer`がreservation-only phaseを一度だけ実行
3. reservation phaseでは`work-context-manager`のみを使用し、`report-writer`を呼ばない
4. `sub-agent-task-manager`はpre-reserved identityをreuseして`deferred_attestation`でfresh reviewerをdispatch
5. independent reviewerはrepository report fileを作成・編集せずstructured evidenceをparentへ返す
6. findingが出てもsame reservation identityを保持し、passing前にreportをpersistしない
7. passing verdict後だけattestation-persistence phaseで`report-writer`を呼び、reserved pathへ初回materialize
8. hierarchy共通規則でもruntime profile unverified stateとdeferred reservation例外を明記

hierarchy正本とmirrorは同一blob SHA `984c549dd78c0f4f7f91e3e73768925219c3996e`を参照するtreeとして1commitで更新した。

主commit:

- `7db502a389fba91a079719fbfab1c60b4a06a6c8` `docs: sync deferred review hierarchy contract`

## 変更ファイル

R4対応で変更したfile:

- `skills/codex-delegation-executor/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/review-enforcer/SKILL.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`

同時期にreviewer側から`reports/issue-13-pr65-r4-rereview-20260829.md`がbranchへ追加されている。これはR4 review evidenceとして保持し、本対応では削除・書換えしていない。

## 検証

### R4技術修正HEAD

- HEAD: `7db502a389fba91a079719fbfab1c60b4a06a6c8`
- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `33251174658`
- Run number: `197`
- Conclusion: `success`
- Build job: `99096989068`

成功step:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

Artifact:

- name: `chatgpt-worker-skills-33251174658`
- ID: `9714403697`
- workflow run head SHA: `7db502a389fba91a079719fbfab1c60b4a06a6c8`
- digest: `sha256:0dff6fa5ab8d0e95074b9cbca087953bb16f19143a78dae2b34feee29ac600fa`

別SHAのworkflow runはR4技術修正のCI evidenceとして使用していない。

## 最終HEADの扱い

本reportをrepositoryへ保存するcommitによりPR HEADはR4技術修正HEADから進む。

最終CIは、このreport commitを含むPR current HEADとworkflow run `head_sha`が完全一致するrunだけを確認する。別SHAの成功runは代用しない。

## 残存事項

- parent-visible final runtime profile snapshotが存在しないruntimeではexact `applied`を断定しない設計を維持する
- independent-final report reservationはcurrent lifecycleでは`review-enforcer`単独ownerとする
- multi-agent review lifecycle自体は本PRのscope外
- mergeは行わない

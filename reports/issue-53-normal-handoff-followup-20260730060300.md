# Issue #53 Normal Handoff Review Follow-upレポート

## メタデータ

- Repository: `ssaattww/CodexSkill`
- Issue: #53
- PR: #54
- Branch: `agent/issue-53-shared-workflow-contracts`
- Base: `main`
- Source fix-verification report: `reports/issue-53-independent-final-review-r2-fix-verification-20260729212800.md`
- Source reviewed implementation HEAD: `ab20b8875dd71722ada7fe4794e05d4a85671bde`
- Source report commit: `17339b357226125b1b6bd6850645bfec8c92fcab`
- Review mode: `review follow-up`
- TDD: `not applicable`
- Merge: 未実施

## 目的

独立最終レビューr2のfix verificationで唯一partialとなった`PR54-IFR2-001`へ対応する。

残存原因は、pre-freeze必須のnormal handoffをschema version 3 packetとして生成・保存せず、Issue／PR／tracking／reportのrepository discoveryで代替していたことである。

あわせて利用者指示に従い、`design/chatgpt-project-instruction-example.md`の対象固有リポジトリ名を対象URL1か所だけに集約する。別Projectへ流用するときに利用者が複数箇所を修正する必要をなくす。

## Authority

- 利用者のcurrent instruction: 最新レビュー結果へ対応する
- 利用者の追加instruction: Project Instruction例では`RevMem`を最初の1回だけ記述し、設定箇所を分散させない
- root `AGENTS.md`: CodexSkill repository自身へTDDを適用しない
- `chat-handoff-manager`: schema version 3のtyped projectionとversioned raw `source_payloads`を持つcomplete packetを生成する
- `chat-implementation-worker`: repository write可能時はhandoffを保存し、packet生成をrepository discoveryで代替しない
- source fix-verification report: complete schema version 3 packetを`reports/handoffs/`へ保存する

## 対応内容

### `PR54-IFR2-001`

次のnormal handoff packetを生成する。

```text
reports/handoffs/issue-53-pr54-normal-handoff-20260730060300.md
```

packetは少なくとも次を保持する。

- schema version 3 typed projection
- authoritative requirements、scope、non-goals、write boundary
- development policy、validation plan、required failure diagnostics、blocked state
- changed／inspected／intentionally untouched files
- commands、tests、CI run、artifact、commits
- source finding全fieldとcurrent disposition
- reviewer identity／continuity／independence
- held、unexplored、unknown、remaining risks
- report path、PR comment reference
- next Skill、mode、required references、requested permissions
- `work-context-manager`、`implementation-worker`、`review-worker`、`report-writer`のversioned raw source payload

repository discoveryはpacketの参照元として残せるが、packet自体の代替には使用しない。

### Project Instruction単一設定化

`design/chatgpt-project-instruction-example.md`を次の方針へ変更した。

- 見出しから対象固有名を除去
- 対象固有リポジトリ名は対象URLの1か所だけに記載
- TDD説明は「対象リポジトリ」と「Skill参照リポジトリ」で表現
- 冒頭へ、対象固有値を最初の対象リポジトリだけで設定する規則を追加

これにより別Projectへ流用するときは対象URLだけを変更すればよい。

## Tracking同期

- T-002はPhase 7のnormal review follow-upを継続する
- pre-freeze stateは`invalidated`のまま維持する
- normal handoff packet pathをtask／phaseへ記録した
- packet保存後も`PR54-IFR2-001`のfix verificationがpassするまではfreezeしない

## 既存検証証拠

Source report commit HEAD `17339b357226125b1b6bd6850645bfec8c92fcab`:

- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `30452219416`
- Run number: `113`
- Conclusion: `success`
- Repository Skill／active-link validation: `success`
- 8 Skill ZIP build: `success`
- Artifact ID: `8723969199`
- Artifact: `chatgpt-worker-skills-17339b357226125b1b6bd6850645bfec8c92fcab`
- Digest: `sha256:73db9250fbae30e591be184b8d04417d72920392b98c25cf75765b6878cdce9a`

## Current-HEAD検証

本report、tracking、Project Instruction例、normal handoff packetを含むnew HEADで次を再確認する。

- repository-wide Skill／active-link validation
- hierarchy design同期
- 8 Skill ZIP build
- matching workflow run
- matching artifact

## 残存状態

- `PR54-IFR2-002`: resolved維持
- `PR54-IFR2-003`: resolved維持
- `PR54-IFR2-001`: packet保存後にnormal reviewerのfix verificationが必要
- main push限定release job: held
- ChatGPT UIでの8 Skill実機確認: held
- fresh independent final review: 未実施

## 次のaction

1. schema version 3 normal handoff packetをrepositoryへ保存する
2. packet commit後のHEADでmatching CIとartifactを確認する
3. Issue #53とPR #54へpacket path、HEAD、CI evidenceを同期する
4. normal reviewerが`PR54-IFR2-001`を同じidentityでfix verificationする
5. pass後にpre-freeze gateを確定し、別fresh reviewerが独立最終レビューを実施する

## Merge boundary

TDDとmergeは実施していない。merge判断と実行は利用者が所有する。

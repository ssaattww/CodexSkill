# Issue #53 Core Skill／Runtime Wrapper Review Follow-up Report

## メタデータ

- Repository: `ssaattww/CodexSkill`
- 対象Issue: #53 `Codex／ChatGPT Skillの共通契約化とChatGPT配布ZIPの自動収集`
- 対象PR: #54 `Issue #53: 親非依存core Skillとruntime wrapperへ再構成`
- Mode: `review follow-up`
- Source review report: `reports/issue-53-independent-final-review-20260729083728.md`
- Source reviewed HEAD: `7fe8660d0fb4133bd732dd8456ff4390cf7b91e7`
- Review follow-up implementation parent HEAD: `f3293a63a2103bea2564d1f97a266bcbe7d730a1`
- Branch: `agent/issue-53-shared-workflow-contracts`
- Base: `main`
- 作成日時: 2026-07-29 17:43:38 JST
- TDD: `not applicable`
- Merge: 未実施

このreportはnormal review follow-upのimplementation／verification evidenceであり、independent-final-review report-attestationではない。本reportを保存するcommitによりPR HEADは上記parent HEADから進むため、report commit後のcurrent HEAD、workflow run、artifactはPR body／PR commentへ記録する。

## 目的

独立最終レビューで記録された5 findingを、親非依存core Skill＋runtime wrapperというaccepted architectureの範囲内で修正する。

- `PR54-IFR-001`: 削除済みshared contractへのbroken dependency
- `PR54-IFR-002`: handoff schemaのevidence欠落
- `PR54-IFR-003`: final review report persistenceによるHEAD非収束
- `PR54-IFR-004`: Issue、tracking、implementation reportの旧architecture／旧HEAD不整合
- `PR54-IFR-005`: obsolete shared-copy validatorの残存とCI未接続

## Accepted architecture

2026-07-29にIssue #53へsuperseding decisionを記録した。

### 親非依存core Skill

- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

### Codex runtime wrapper

- `implementation-executor`
- `review-enforcer`
- `report-output-manager`

### ChatGPT runtime wrapper

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`
- `chat-handoff-manager`

Skill外shared runtime fileを複数Skillから参照せず、wrapperはinstall済みcore SkillをSkill名で呼び出す。

## Finding対応

### PR54-IFR-001

**Disposition: addressed; normal fix verification待ち**

変更:

- `development-orchestrator`から削除済み`shared/workflow/`参照を除去した
- `work-context-manager`、`implementation-executor`、`implementation-worker`、`report-output-manager`、`review-enforcer`の呼び出しへ統一した
- `tdd-executor`を`work-context-manager`とcore implementation pathへ統一した
- `skill-authoring-wrapper`のshared contract作成、link、dependency packaging規則を削除した
- cross-runtime semanticsは独立core Skillとして作成し、wrapperはSkill名依存を宣言する規則へ置換した
- `scripts/verify_skill_repository.py`を追加し、active Markdown relative linkとSkill dependencyをrepository-wideに検証するようにした

### PR54-IFR-002

**Disposition: addressed; normal fix verification待ち**

`chat-handoff-manager`をschema version 3へ更新した。

保持対象:

- authoritative requirements、scope、non-goal、write boundary
- changed／inspected／intentionally untouched files
- command、test、CI run、artifact、implementation commit
- implementation outcome、addressed finding disposition
- review mode、reviewed HEAD、coverage、validation assessment、verdict
- full findingのorigin、location、description、impact、evidence、required action
- held、unexplored、unknown、not-applicable、remaining risk
- report type、path、persistence mode、PR comment reference
- next Skill、next mode、instruction、reference、requested permission

schema version 1／2のreaderはsourceに存在する情報を保持し、欠落fieldをunknownとして扱う。安全な継続に不足する場合はblocked／incompleteとする。

### PR54-IFR-003

**Disposition: addressed; normal fix verification待ち**

有限なreview終端規則を次へ反映した。

- `development-orchestrator`
- `review-worker`
- `review-enforcer`
- `chat-review-worker`
- `report-writer`
- `report-output-manager`
- `chat-handoff-manager`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
- `design/chat-worker-skill-design.md`

規則:

1. independent final review前にimplementation、design、workflow、configuration、tracking、handoff、normal review report、verification reportを含む全非final変更をcommit／pushする。
2. independent-final-review report pathを事前予約する。
3. current HEADを`reviewed implementation HEAD`としてfreezeする。
4. fresh reviewerがそのimmutable HEADをreviewする。
5. passing reportをrepositoryへ保存する場合は、予約済みreport pathだけを変更する1回の`report-attestation commit`を許可する。
6. attestation commitのfirst parent、changed path、report metadata、後続commit不在を検証する。
7. completion identityを`reviewed implementation HEAD + optional report-attestation HEAD`とする。
8. final handoffはinlineまたはPR branch外でtransportし、attestation後のrepository commitを追加しない。

条件外のpost-review commitはcompletionを無効化し、normal fix verificationとfresh independent final reviewを要求する。

### PR54-IFR-004

**Disposition: addressed; current report／tracking作成済み、normal fix verification待ち**

- Issue #53へ当初方針をhistorical／supersededとして残し、2026-07-29 superseding decisionを追加した
- current acceptance criteriaを8 Skill構成、lossless handoff、repository validator、report-attestation終端規則へ更新した
- `tasks/tasks-status.md`をcurrent architectureと5 finding対応へ更新した
- `tasks/phases-status.md`へreview follow-up phaseとfix verification／fresh final review phaseを追加した
- `reports/issue-53-shared-workflow-contracts-20260726154744.md`へsuperseded historical report bannerを追加した
- 旧report本文、旧HEAD、旧artifactはhistorical evidenceとして保持し、current stateとして使わないことを明示した
- 本reportをcurrent review-follow-up implementation／verification evidenceとして追加した

### PR54-IFR-005

**Disposition: addressed; current-HEAD CI成功、normal fix verification待ち**

- `scripts/verify_no_committed_chatgpt_skill_copies.py`を削除した
- `scripts/verify_skill_repository.py`へ置換した
- workflowへrepository-wide validation stepを接続した
- workflow triggerを`AGENTS.md`、`README.md`、全Skill、design、tasks、reports、builder、validator、workflowへ拡張した

validator確認項目:

- 全Skillのfront matter `name`とdirectory名
- duplicate Skill name
- wrapperが必要なcore SkillをSkill名で宣言していること
- required release Skill 8件の存在
- active Markdown relative linkの存在とrepository内境界
- Skill内symlink不在
- 削除済み`shared/workflow`／`shared/chat-worker` runtime directory不在
- obsolete validator不在
- hierarchy design 2件のbyte一致

## 設計書

既存内容を削除しない方針を維持し、次を残したままfinding対応を追加した。

- Codex標準開発flow
- TDD適用境界
- normal review cycleとindependent final review
- ChatGPT worker flowと入力例
- ChatGPT登録用Skillセット
- handoff規則
- Release flow
- 標準作業手順
- 全Skill一覧
- 共通規則
- 保守規則
- Project Instruction例
- CodexSkill repository検証方針
- 完了条件

`design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`は同一content blobとして更新した。

## 通常検証

### TDD

CodexSkill repository自身へTDDを適用しないroot `AGENTS.md`と利用者指示に従い、TDDは`not applicable`とした。

- Red／Green testを追加していない
- TDD用workflowを追加していない
- review finding専用の製品testを追加していない

### Repository／bundle validation

Review follow-up implementation parent HEAD:

```text
f3293a63a2103bea2564d1f97a266bcbe7d730a1
```

- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `30436818095`
- Run number: `85`
- Status: `completed`
- Conclusion: `success`
- Artifact ID: `8717740115`
- Artifact name: `chatgpt-worker-skills-f3293a63a2103bea2564d1f97a266bcbe7d730a1`
- Artifact digest: `sha256:d72dfc6c003739b3e88878189aff4079c0ea096d3f67109096c77a0ddc407547`

このrunではrepository-wide Skill／link／dependency validationと8 Skill ZIP buildが成功した。

本report commit後のcurrent HEADについてもworkflowを実行し、runとartifactをPR body／PR commentへ記録する。

## Changed areas

- core review／report semantics
- Codex orchestration／TDD／review／report wrappers
- ChatGPT review／handoff wrapper
- Skill authoring policy
- repository validator
- Release workflow
- hierarchy design 2件
- ChatGPT worker design
- Issue #53
- task／phase tracking
- historical report classification

## Intentionally untouched

- product repository implementation outsideCodexSkill: 対象外
- main push限定release jobの実行: PRでは実行されない
- GitHub Release assetの実更新: merge前のため未実施
- ChatGPT UI uploadとSkill間呼び出し: repository検証では確認できない
- PR merge: 利用者所有

## Remaining risks and next action

- normal reviewerによる5 findingのfix verificationが必要
- fix verificationでrequired findingが出た場合はreview follow-upを再開する
- fix verification pass後、全非final変更を確定し、independent-final-review report pathを予約する
- 別fresh reviewerがfrozen implementation HEADを独立最終reviewする
- passing reportを保存する場合は1回のreport-attestation commitとallowlist diff検証を行う
- main反映後のRelease更新とChatGPT UI実機確認はheld itemとして残る

## Merge boundary

mergeは実施していない。merge判断と実行は利用者が所有する。

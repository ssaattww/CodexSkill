# Issue #13 適応型agent割当 実装レポート

## メタデータ

- repository: `ssaattww/CodexSkill`
- Issue: `#13 sub-agentの使用モデル`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- branch: `feat/adaptive-agent-assignment`
- base: `main`
- base HEAD: `2ea9522d494b2b37c1d8aabb340a3113cfd18240`
- implementation HEAD: `18694e6bdfd15301afbaf57b2e6596fe52d239e7`
- report persistence: repository file
- report commit SHA: commit後にのみ確定するため本文には記載しない。final PR HEADとexact-head CIはPR commentへ記録する。

## 目的

参考記事のLuna、Terra、Solの役割分担をCodexSkillの既存delegation flowへ取り込み、bounded taskの性質に応じて次を自動選定する。

- model tier
- reasoning effort
- fork policy
- single-agent executionとmulti-agent decompositionの区別

modelをpromptへ書くだけでなく、requested profileとruntimeへ実際に適用されたprofileを分離し、選定理由、制約、fallbackをreport evidenceとして残す。

## authoritative requirements

- user instruction: 参考記事を基に適切なagentを割り当てる仕組みを実装し、PR作成まで行う。
- repository instruction: root `AGENTS.md`に従いCodexSkill保守へTDDを適用しない。
- Issue #13: 機械的実装、設計・調査、reviewで使用modelを分けるSkill契約が不足している。
- project instruction: GitHub connectorでrepository、Issue、PRを操作し、詳細reportをrepositoryへ保存し、簡易reportをPR commentへ投稿する。mergeは行わない。
- CI instruction: PR current HEAD SHAとworkflow runの`head_sha`が一致するrunだけを使用する。

## 参考資料

- https://qiita.com/azarashin/items/0a37ec8cce7c75d7f5eb
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/guides/latest-model

OpenAI公式model catalogに基づき、current model IDを`gpt-5.6-luna`、`gpt-5.6-terra`、`gpt-5.6-sol`として定義した。reasoning effortは`none`、`low`、`medium`、`high`、`xhigh`、`max`をnormalization対象とした。

参考記事のUltra相当はreasoning effortではなく、独立workstreamを複数agentへ分割するexecution strategyとして扱った。

## scope

- `sub-agent-task-manager`へper-task profile selection責務を追加
- model tierとreasoning effortを別軸で選ぶ中央matrixを追加
- Luna、Terra、Solのtask floorとtask defaultを追加
- uncertainty、change radius、criticality、repetition、decomposability、context needのassessmentを追加
- `codex-delegation-executor`へsingle-agentとmulti-agent decompositionのgateを追加
- `development-orchestrator`のroutineなimplementation model確認を廃止
- explicit userまたはrepository overrideの優先順位を追加
- requested profileとapplied profileを分離
- full-history fork、runtime rejection、fallback、capability gapの記録契約を追加
- 適応型agent割当の設計書を追加

## non-goals

- Codex runtime本体へのmodel router実装
- runtime model availability APIの追加
- model価格だけに基づくrouting
- explicit overrideのsilent変更
- full-history forkへ異なるmodelを強制すること
- `reasoning_effort: ultra`の追加
- task tracking fileの手動更新
- merge

## 責務配置

### `codex-delegation-executor`

次を所有する。

- main agent、single sub-agent、multi-agentのexecutor decision
- task assessment
- independent workstreamの分割gate
- parent synthesis

modelとreasoning effortの中央defaultは持たない。

### `sub-agent-task-manager`

次を所有する。

- bounded taskごとのmodel tier選定
- reasoning effort選定
- fork policy選定
- requested profileのspawn適用
- applied profileとfallbackのreport evidence

この配置により、`sub-agent-task-manager`が直接使われる経路でもmodel selectionが欠落しない。

### `development-orchestrator`

routineなmodel確認を要求せず、明示overrideまたはbudget constraintだけをworkflow inputとして保持する。

## 選定規則

### model tier

- Luna: low uncertainty、local、ordinary criticality、deterministic、mechanicalまたはhigh-volume
- Terra: ordinary bounded implementation、focused verification、具体的仮説があるlocalized investigation、focused fix verification
- Sol: requirement、design、open-ended investigation、cross-system、高criticality、initial review、independent final review、release audit

複数条件が該当する場合は最も高いfloorを使う。diff行数よりchange radiusとimpactを優先する。

### reasoning effort

- `low`: exactかつ低riskの変換
- `medium`: ordinary bounded implementationまたはdeterministic evidence
- `high`: 複数条件、debug、design、review
- `xhigh`: boundedで網羅性または重要度が高いreview・audit
- `max`: 一つの非常に難しく分割不能な問題

`max`はgeneric quality settingとして使わず、`execution-cost-stabilizer`を通す。

### multi-agent

次を全て満たす場合だけ分割する。

- independent workstreamが2件以上
- 各taskへscope、non-goals、evidence、report ownerを定義できる
- write ownershipが重複しない、またはread-only
- blocking dependencyがない
- parent synthesisが定義されている
- parallelismの実益がある

各taskは別々にprofileを選ぶ。

## changed files

- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
  - model tier、reasoning effort、task default、override、fork、escalation、evidence schemaを追加
- `skills/sub-agent-task-manager/SKILL.md`
  - per-task profile selectionとactual runtime applicationをrequired flowへ追加
- `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md`
  - selectionとapplicationを分離し、requested/applied、full-history、fallbackを追加
- `skills/codex-delegation-executor/SKILL.md`
  - delegation assessmentとmulti-agent decomposition gateを追加
- `skills/development-orchestrator/SKILL.md`
  - routineなimplementation model確認をautomatic selectionへ置換
- `design/adaptive-agent-assignment-design.md`
  - architecture、input schema、selection matrix、flow、examples、validation方針を追加

## intentionally untouched

- `tasks/tasks-status.md`
  - repository契約上、指定されたtask管理Skillだけが更新するため手動変更しない。
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
  - Skill hierarchy topologyとdependency edgeは変更していない。新規Skillも追加していないため同期pairは変更しない。
- `.github/workflows/release-chatgpt-worker-skills.yml`
  - CodexSkillには既にrepository validator、ZIP build、artifact uploadを行うPR workflowが存在する。RevMem向け診断artifact追加規則は本repositoryへ適用しない。
- `skills/review-enforcer/SKILL.md`
  - reviewer lifecycleは変更せず、review modeをbounded task inputとしてselectorが使用する。

## commits

- `716594ca5a19e5ad5fe3e718cd445ab4559811f8`: adaptive profile selection reference追加
- `52a9b63dd4a119aa9410133ec4e0e7e07d3f1183`: `sub-agent-task-manager`へautomatic selection追加
- `76b49304cdb9d3a54f3d202a6b072584431612e2`: spawn application contract更新
- `df3d44be01c9b7022909bd7a2ce614733c820f07`: delegation assessmentとmulti-agent gate追加
- `abf889a0e4955069a3901c99973ee401d1226ce2`: orchestratorのroutine model confirmation置換
- `18694e6bdfd15301afbaf57b2e6596fe52d239e7`: 適応型agent割当設計追加

## development policy

- method: non-TDD repository maintenance
- testing order: implementation後にrepository validatorとdistribution buildを実行
- governing source: root `AGENTS.md`
- TDD: not applicable
- Red/Green evidence: 作成していない

## validation route

- verification capability: `remote_ci_only`
- 理由: repository参照・更新はGitHub connectorを使用し、local checkoutを作らずGitHub Actionsをformal validation evidenceとして使用した。

## validation evidence for implementation HEAD

対象HEAD: `18694e6bdfd15301afbaf57b2e6596fe52d239e7`

- workflow: `Validate and release ChatGPT worker skills`
- run ID: `32929673352`
- run number: `159`
- event route: pull request
- run head SHA: `18694e6bdfd15301afbaf57b2e6596fe52d239e7`
- conclusion: `success`
- build job ID: `98059362580`

成功step:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

このrunはimplementation HEADと一致する。reportとhandoff追加後はPR HEADが変わるため、このrunをfinal HEADの代用にはしない。final exact-head runはPR commentへ記録する。

## failure diagnostics

- test failure: なし
- standard output failure: なし
- standard error failure: なし
- failure artifact inspection: not applicable
- workflow artifact: validation成功時にChatGPT worker ZIPがuploadされた。failure investigationは不要だった。

## contract review

次を差分で確認した。

- model tierとreasoning effortが別のdecisionとして記述されている
- `reasoning_effort: ultra`を生成しない
- multi-agent decompositionは`codex-delegation-executor`が所有する
- per-task profileは`sub-agent-task-manager`が所有する
- user/repository overrideをsilentに変更しない
- requested profileをapplied profileとして無条件copyしない
- full-history forkはparent profile継承として記録する
- runtime rejectionはfallbackまたはcapability gapとして記録する
- failed deterministic verificationをinvestigationへ再分類する
- existing report、review、nested Codex禁止契約を維持する

## blocked / unknown / unexplored

- blocked: なし
- unknown: 実行時に各accountまたはruntimeで利用可能なmodel一覧を取得するAPIは本repositoryに存在しない。
- unexplored: hidden `collaboration.spawn_agent` overrideのlive integration test。CodexSkillはSkill contract repositoryであり、CIにspawn fixtureは存在しない。

## remaining risks

- GPT model familyまたはsupported reasoning effortが将来変更された場合、current model mappingの更新が必要になる。
- hidden spawn overrideがruntimeでrejectされる可能性は残る。その場合はrequested/appliedを分離し、parent-owned fallbackまたはcapability gapを記録する。
- automatic classificationはSkill instructionに基づくjudgmentであり、runtime classifier codeではない。non-obvious classificationにはevidence記録を必須化した。
- final report/handoff commitについては、新しいPR HEADに紐づくworkflow runを別途確認する必要がある。

## outcome

Issue #13のmodel assignment不足に対し、既存delegation architectureを維持したまま、task特性からLuna、Terra、Solとreasoning effortを選ぶ中央contractを実装した。

PR #65を作成済み。mergeは行わない。

## next action

- reportとhandoffをrepositoryへpersistする。
- final PR HEADと一致するworkflow runだけを確認する。
- PR bodyをfinal stateへ更新し、変更内容と検証結果の簡易reportをPR commentへ投稿する。
- PRをready for reviewへ変更する。

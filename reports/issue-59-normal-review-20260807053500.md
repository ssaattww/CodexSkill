# Issue #59 / PR #60 初回レビュー報告

## メタデータ

- Repository: `ssaattww/CodexSkill`
- Issue: #59
- PR: #60
- Review mode: `initial review`
- Reviewed implementation HEAD: `a39942bdb11397099463135f0d8487aad8f0d7a6`
- Base: `aa3c1462ece21dce82f644788b9cbc36a38e76a7`
- Commit range: `aa3c1462ece21dce82f644788b9cbc36a38e76a7..a39942bdb11397099463135f0d8487aad8f0d7a6`
- Reviewer: ChatGPT normal reviewer (this chat)
- Reviewer continuity: initial review; previous normal reviewerなし
- TDD: CodexSkill repository policyにより not applicable
- Verdict: `fail`

## 対象要件

Issue #59 の要求は、ChatGPT worker配布ZIPにtask更新用Skillが含まれておらずChatGPT側からtask更新できない状態を解消することである。

PRは以下を実装対象としている。

- `task-breakdown-planner`
- `task-consistency-manager`
- `progress-sync-manager`

をChatGPT配布ZIPへ含める。

- `chat-implementation-worker`からtask整合確認、必要時のtask分割、進捗同期を実行する。
- 設計書を11 Skill構成へ同期する。
- handoffへtask tracking情報を保持する。

## 確認範囲

変更ファイル6件を全て確認した。

- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `reports/issue-59-chatgpt-task-skills-20260806.md`
- `scripts/build_chatgpt_worker_skills.py`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/design/skill-hierarchy-design.md`

直接依存として以下を確認した。

- `skills/task-breakdown-planner/SKILL.md`
- `skills/task-consistency-manager/SKILL.md`
- `skills/progress-sync-manager/SKILL.md`
- `skills/chat-handoff-manager/SKILL.md`
- `design/chatgpt-project-instruction-example.md`
- `AGENTS.md`

## CI / validation

Reviewed implementation HEADに一致するworkflow runのみを確認した。

- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `31049455223`
- Head SHA: `a39942bdb11397099463135f0d8487aad8f0d7a6`
- Conclusion: `success`
- Build job: `92452963807` / success
- Artifact: `chatgpt-worker-skills-31049455223`
- Artifact ID: `8947793340`
- Digest: `sha256:e22dc58ac5e55cef2f945d040a63ac49d4ac12de02ff01553ca5ee27fa2b9d96`

CIは11 Skill ZIPの構造とrepository validatorを通している。ただし以下のfindingはいずれもSkill contractと設計の意味論に関するもので、現行validator成功では否定できない。

## Findings

### F-60-01 — blocking — ChatGPT workerから呼ぶtask tracking Skillがparent-only contractのまま

**Origin:** introduced_by_change

**Location:**

- `skills/chat-implementation-worker/SKILL.md`
- `skills/task-breakdown-planner/SKILL.md`
- `skills/task-consistency-manager/SKILL.md`
- `skills/progress-sync-manager/SKILL.md`

**Description:**

PRは`chat-implementation-worker`が3つのtask tracking Skillを直接呼ぶ契約へ変更している。一方、配布対象へ追加した3 Skillは全て`## Execution owner`で`Run this skill as: parent`と明記し、canonical trackingの最終更新をparent-ownedとしている。ChatGPT wrapper自身の契約は「The user is the parent」であり、current chatはparentではなくworkerであるため、配布したSkillの実行主体契約とwrapperの呼び出し契約が一致していない。

さらに`task-breakdown-planner`と`task-consistency-manager`はlarge-scope時に`sub-agent-task-manager`を利用するparent flowを記述しているが、`chat-implementation-worker`は別worker/sub-agentを起動しないことをboundaryとしている。

**Impact:**

Issue #59の主目的である「ChatGPT側からtask更新できる」がSkill contract上成立していない。ZIPへ同封されても、ChatGPT workerが正規の実行主体として扱える定義になっていない。

**Required action:**

3つのtask tracking Skillをruntime-neutralにするか、ChatGPT用wrapper/adapterを設けるなどして、ChatGPT workerから実行可能なowner contractを明示すること。parent-only delegation記述もChatGPT wrapper boundaryと矛盾しない形へ整理し、設計とSkill contractを同期すること。

### F-60-02 — blocking — canonical task tracking pathを受け取れず、Project Instructionのpathと契約が不一致

**Origin:** introduced_by_change

**Location:**

- `skills/task-breakdown-planner/SKILL.md`
- `skills/task-consistency-manager/SKILL.md`
- `skills/progress-sync-manager/SKILL.md`
- `design/chatgpt-project-instruction-example.md`

**Description:**

ChatGPT Project Instruction例はtask一覧を`tasks/tasks-status.md`として指定している。しかし配布対象へ追加した3 Skillは、input/update targetとして`tasks-status.md`と`phases-status.md`を固定名で扱い、`work-context-manager`から解決されたcanonical tracking pathを入力として受け取る契約を持たない。

`chat-implementation-worker`は先に`work-context-manager`を呼ぶようになったが、そのresolved pathをtask tracking Skillへ渡すfield/contractは今回追加されていない。

**Impact:**

実際のProject Instructionが`tasks/tasks-status.md`のようなsubdirectoryを指定する場合、workerが正本ではないroot-level fileを探す・作る・更新する余地がある。Issue #59の目的を実環境で満たせない可能性がある。

**Required action:**

3 Skillのinput contractへcanonical task tracking path（必要ならphase tracking pathも）を追加し、`work-context-manager`が解決したpathをwrapperから必ず渡すこと。固定basenameではなく、対象repository/project instructionで解決された正本pathを使用すること。

### F-60-03 — high — 設計で追加したhandoff task情報が`chat-handoff-manager` schemaへ実装されていない

**Origin:** introduced_by_change

**Location:**

- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
- `skills/chat-handoff-manager/SKILL.md`

**Description:**

PR後の設計はhandoffがtask identity、tracking path、phase/state、dependencies、exit criteria、pending tracking actionを保持するとしている。一方、`chat-handoff-manager`のschema version 3にはtop-level `task_id`しかなく、task tracking path、task/phase state、dependencies、exit criteria、pending tracking actionのtyped fieldが存在しない。今回`chat-handoff-manager`自体は変更されていない。

**Impact:**

設計が要求するtask tracking stateをchat間handoffでlosslessに保持できず、次workerがtracking actionを再構成する必要が生じる。設計の完了条件「handoffにtask情報を保持」と実装が不一致になる。

**Required action:**

`chat-handoff-manager`のschema/output contractへ必要なtask tracking fieldsを追加し、compatibility/lossless transport rulesも同期すること。schema変更に伴い関連wrapper、設計書、validator対象を必要に応じて更新すること。

### F-60-04 — high — Issue #59と無関係な既存設計契約を大量削除している

**Origin:** introduced_by_change

**Location:**

- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`

**Description:**

PRはtask tracking Skill追加に必要な差分を超えて、既存設計書から次のような独立した契約を大量に削除している。

- Release / pre-release / manual releaseの詳細条件
- 標準作業手順
- Skill一覧と実行方式
- normal review continuity、severity continuity、pre-freeze、independent final review、report-attestationの詳細条件
- 共通規則、保守規則
- ChatGPT worker flowの具体的入力例や運用説明
- Project Instruction例に関する説明

base版の保守規則には「既存設計書の変更時は、構成変更と無関係な節を削除せず、矛盾する箇所だけを置換する」と明記されている。今回の削除はこの既存保守契約に反する。

**Impact:**

Issue #59と無関係な既存仕様・運用契約が正本設計から失われる。今後のworker/release/review実装が簡略化後の設計を正本として参照すると、既存保証を意図せず退行させる。

**Required action:**

baseの既存節を復元し、Issue #59で必要なtask tracking追加だけを局所的に追記・置換すること。既存契約を変更する必要が本当にある箇所は、Issue #59の要求との関連と変更理由を明示して個別に扱うこと。

## Required coverage dispositions

- Requirement/design conformance: `checked_finding` — F-60-01, F-60-02, F-60-03, F-60-04
- Correctness/edge cases: `checked_finding` — configured tracking pathとruntime owner境界に不整合
- Scope discipline/unrelated changes: `checked_finding` — F-60-04
- Changed files/direct dependencies: `checked_finding` — 全6変更fileと4直接依存Skillを確認
- API/data/config/workflow/compatibility: `checked_finding` — handoff schemaとtask path contract
- Error handling/failure diagnostics: `checked_no_finding` — 今回の変更は製品test実装ではなく、current HEAD CIは成功
- Security/secret handling: `not_applicable` — 新規secret/credential処理なし
- Tests/validation adequacy: `checked_finding` — CI成功だがcontract semantic mismatchを検出できていない
- Current-HEAD CI evidence: `checked_no_finding` — Run 31049455223がreviewed HEADに一致しsuccess
- Report/tracking/documentation accuracy: `checked_finding` — implementation reportはhandoff task情報実装済みと読めるがschema未変更
- Regression/maintainability risk: `checked_finding` — F-60-04

## Held / unexplored

- Held: なし
- Unexplored: workflow artifactの実ZIP内容はCIのarchive validationとartifact metadataで確認済みとし、artifact binary自体の再展開検査は未実施。F-60-01/F-60-02/F-60-03/F-60-04の判定には影響しない。

## Verdict

`fail`

Blocking finding 2件、高severity finding 2件があるため、修正後に同じnormal review chatでfix verificationが必要。

## 次アクション

1. F-60-01〜F-60-04を実装workerへhandoffする。
2. task tracking Skillのruntime owner/path contract、handoff schema、設計書の過剰削除を修正する。
3. 新しいHEADでrepository validator / ZIP build / artifact uploadを実行する。
4. 新しいHEAD SHAと一致するworkflow runのみを検証証拠としてfix verificationを行う。

mergeは実施しない。

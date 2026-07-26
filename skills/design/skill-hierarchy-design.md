# スキル階層設計

## 目的

本書は、`/home/ibis/AI/CodexSkill/skills`配下のlocal skillについて、次を一元的に定義する。

- 各skillの役割
- 親agent、worker、sub-agentの責務境界
- 標準開発フローの呼び出し関係
- review判断、表示、repository artifactの分離
- skillごとの入力、出力、完了条件

運用reportより本書を正本として扱う。

## 対象

- repository: `/home/ibis/AI/CodexSkill`
- scope: `skills/`配下のlocal skill
- ChatGPT chat向けstandalone workerの追加は別scopeとし、本書では共有可能なcore contractとCodex側adapter境界まで定義する

## 実行方式

### 親が実行

親agentが判断、計画、統合、完了判定を行う。

### 親が呼び出し、sub-agentが実行

親agentが`sub-agent-task-manager`を通じてbounded taskをdispatchし、sub-agentが実作業を行う。親は結果validationと採否を所有する。

### Workerが実行

repository、Markdown、PR投稿等に依存しないcore skillをworkerが実行する。

- Codexではdelegated sub-agentがworkerになる
- direct useではcurrent agentがworkerになれる
- workerは別agentをdispatchしない

## 標準開発フロー

```text
development-orchestrator [親が実行]
├─ restart-handover-manager [親が実行, resume時]
├─ task-consistency-manager [親が実行]
├─ design-doc-maintainer [親が実行]
│  ├─ codex-delegation-executor [親が実行]
│  │  └─ design-executor [worker切替対象]
│  └─ task-consistency-manager [親が実行]
├─ tdd-executor [親が実行]
│  ├─ codex-delegation-executor [親が実行]
│  │  └─ implementation-executor [worker切替対象]
│  └─ sub-agent-task-manager [親が実行, test evidence]
├─ codex-delegation-executor [親が実行]
│  ├─ implementation-executor [worker切替対象]
│  ├─ design-executor [worker切替対象]
│  ├─ sub-agent-task-manager [親が実行]
│  └─ report-output-manager [親が実行, artifact adapter]
├─ review-enforcer [親が実行, Codex review runner/gate]
│  ├─ review-policy [親が実行]
│  ├─ markdown-word-checker [親が実行, applicable時]
│  ├─ sub-agent-task-manager [親が実行, structured_result]
│  │  └─ review-core [reviewer worker]
│  ├─ review-result-renderer [親またはreport workerが実行]
│  └─ report-output-manager [親が実行, artifact adapter]
├─ progress-sync-manager [親が実行]
├─ git-workflow-manager [親が実行]
│  ├─ git-branch-starter [親が実行]
│  ├─ git-commit-manager [親が実行]
│  ├─ git-pr-submitter [親が実行]
│  └─ git-review-followup-manager [親が実行]
│     ├─ task-consistency-manager [親が実行]
│     ├─ codex-delegation-executor [親が実行]
│     │  └─ implementation-executor [worker切替対象]
│     └─ report-output-manager [親が実行]
├─ feedback-points-manager [親が実行]
│  └─ feedback-points-sanitizer [sub-agentが実行]
└─ skill-authoring-wrapper [親が実行]
```

## Review architecture

### 依存方向

```text
review-policy
  -> ReviewRequest
  -> review-core
  -> ReviewResult
  -> review-result-renderer
  -> rendered text
  -> report-output-manager / GitHub adapter
```

- `review-core`は`ReviewRequest -> ReviewResult`だけを所有する
- `review-policy`はrisk selection、criterion selection、lifecycle、stop conditionを所有する
- `review-enforcer`はCodex側のreviewer dispatchとtask completion gateを所有する
- `review-result-renderer`はReviewResultからMarkdown、chat text、簡易PR commentを生成する
- `report-output-manager`はrender済みtextをrepository artifactへ保存する
- reviewerはreport path、template、file編集、PR投稿を所有しない
- rendererとartifact adapterはfinding、verdict、follow-upを再判定しない

### Structured contract

正本は`skills/review-core/references/review-contract.md`とする。

`ReviewRequest`は次を含む。

- requirement、design、scope、non-goals
- changed target、dependency boundary
- risk profile、selected module、planned criterion
- previous finding、validation evidence
- stage、reviewer context、immutable target identity

`ReviewResult`は次を含む。

- inspected target
- criterion IDごとのcoverage disposition
- finding、origin、held、unexplored
- validation evidence
- verdict、follow-up、stop reason、merge candidate

固定状態は文面から推測しない。

- verdict: `pass | pass_with_held | fail | incomplete | unstable`
- coverage: `checked_no_finding | checked_finding | held | not_applicable | unexplored`
- follow-up: `none | fix_required | design_rework | split_required | external_owner`
- finding origin: `pre_existing | introduced_by_change | introduced_by_fix | coverage_miss | out_of_scope`

### Universal criteriaとrisk module

criterionの唯一の正本は`skills/review-policy/references/code-review-criteria.md`とする。

全reviewでuniversal coreを選ぶ。

- requirement/design
- change/dependency scope
- contract
- test
- final evidence
- document/scope/delivery consistency

変更riskに応じて次のmoduleだけを選ぶ。

- `M-STATE`: state、persistence、migration、cache
- `M-INPUT`: parser、deserializer、diff、URI、untrusted input
- `M-ATOMIC`: transaction、CAS、concurrency、source conflict
- `M-IDENTITY`: repository、context、revision、file、path identity
- `M-EXTERNAL`: Git、subprocess、network、filesystem、connector
- `M-RUNTIME`: performance、UI responsiveness、large input
- `M-DOC`: Skill、design、workflow、report contract

非選択moduleは個別の`not applicable`rowを作らない。

### Review lifecycle

stable scopeでは次の3段階を使う。

1. Initial comprehensive review
   - stable scopeにつき一回
   - Blocking/Highを見つけてもplanned criteriaを最後まで確認する
   - findingを一括で返す
2. Fix verification
   - same reviewerを再利用する
   - previous finding、fix、direct impact、同種欠陥だけを確認する
   - arbitraryな未確認領域へ拡張しない
   - 同一initial finding setにつき最大二回
3. Cold final review
   - medium/high riskだけ必須
   - fresh reviewerまたはfresh-no-history contextで一回
   - final HEADとmerge candidate条件を確認する

次の場合は`unstable`としてreviewを追加せず、design reworkまたはPR splitへ戻す。

- cold finalでnew independent Blocking/Highが見つかる
- third fix verificationが必要になる
- repeated coverage missがrisk planの不安定さを示す
- scope変更が続きstable targetを維持できない

### Merge candidate

次を全て満たす場合だけ`merge_candidate=true`とする。

- Blocking/Highがない
- universalとselected moduleのcriterionが全てdisposition済み
- high-risk判定を無効化するunexploredがない
- final HEADに結び付いたvalidation evidenceがある
- medium/high riskはcold final済み
- verdictが`pass`または`pass_with_held`

merge action自体はreview skillの責務外とする。

## Sub-agent evidence mode

`sub-agent-task-manager`はdispatch前にevidence modeを一つ選ぶ。

### `artifact_backed`

- implementation、investigation、verification等でrepository reportをprimary evidenceとする場合に使う
- 必要なら事前にreport pathとowned sectionを決める

### `structured_result`

- review等でmachine-readable resultをprimary outputとする場合に使う
- report pathやMarkdown templateを事前要求しない
- workerはstructured resultをcallerへ返す
- rendererとartifact adapterはresult validation後に呼ぶ

Review dispatchは`structured_result`を必須とする。

## 補助フロー

```text
feedback-coding-standards-enforcer [親が実行]
└─ sub-agent-task-manager [standards検出/検証]

feedback-issue-intake-fallback-manager [親が実行]
├─ sub-agent-task-manager [要件抽出/照合]
└─ report-output-manager [artifact adapter]

restart-handover-manager [親が実行]
├─ sub-agent-task-manager [大規模contextのsummary]
└─ reports/とtrackingから再開状態を復元

handover-memo-writer [親が実行]
├─ report-output-manager [handover artifact]
└─ markdown-word-checker [focused lint]

execution-cost-stabilizer [親が実行]
└─ 委譲前の実行計画とcost制御

feedback-autonomy-boundary-manager [親が実行]
└─ user confirmation boundaryを決定

skill-authoring-wrapper [親が実行]
└─ built-in skill-creatorを参照しlocal standardへ補正

task-breakdown-planner [親が実行]
└─ sub-agent-task-manager [大規模分解draft]

task-consistency-manager [親が実行]
└─ sub-agent-task-manager [大規模tracking audit]

design-doc-maintainer [親が実行]
└─ sub-agent-task-manager [大規模impact scan]

git-pr-submitter [親が実行]
└─ sub-agent-task-manager [大規模PR draft/evidence]
```

## Skill作成・更新フロー

```text
development-orchestrator
└─ skill-authoring-wrapper
   ├─ built-in skill-creatorを確認
   ├─ new skillはinitializerを使用
   ├─ existing skillは意図を保持してstandard化
   ├─実在するcanonical inventoryだけを更新
   └─ design/skill-hierarchy-design.mdとskills/design/skill-hierarchy-design.mdを同期
```

## 標準作業フロー

1. `development-orchestrator`がCodexSkillの鮮度と`AGENTS.md`を確認する。
2. resume時は`restart-handover-manager`でcurrent positionを復元する。
3. implementation sub-agent modelをuserへ確認する。
4. tracking、recent reports、feedbackを確認し、一つのtaskを選ぶ。
5. `task-consistency-manager`でtrackingを整える。
6. design impactがあれば`design-doc-maintainer`を呼ぶ。
7. `tdd-executor`で必要なtest-first方針を決める。userがTDD不要と明示した文書・policy変更等では、その判断を記録して省略できる。
8. `codex-delegation-executor`でimplementation/verification ownerを決める。
9. implementationがreview可能になったら`review-enforcer`を呼ぶ。
10. `review-policy`でrisk planを作る。
11. `sub-agent-task-manager`の`structured_result`で`review-core`をdispatchする。
12. ReviewResultへpolicyを適用し、必要なfix verificationまたはcold finalへ進む。
13. resultを`review-result-renderer`で表示し、必要なら`report-output-manager`でartifact化する。
14. findingがあれば`git-review-followup-manager`またはimplementation flowへ戻す。
15. policyが許可した場合だけ`progress-sync-manager`と`git-workflow-manager`へ進む。
16. issue/task完了時にskill actionを判断し、必要なら`skill-authoring-wrapper`と`feedback-points-manager`を呼ぶ。

## 委譲切替の暫定指標

- `task-breakdown-planner`: task候補5件以上、phase3件以上、依存4件以上、または資料4件以上
- `task-consistency-manager`: stale/missing疑い3件以上、対象task行5行以上、または調整点3件以上
- `restart-handover-manager`: recent report5本以上、evidence source4件以上、next task候補3件以上、または矛盾2系統以上
- `design-doc-maintainer`: design候補3本以上、contract面2種以上、または比較file4本以上
- `git-pr-submitter`: report参照3本以上、validation evidence3件以上、または変更group4件以上
- `codex-delegation-executor`: 実装file4本以上、module2つ以上、edit chunk4つ以上、または事前読込file5本以上
- `design-executor`: design file3本以上、edit block4つ以上、または比較file4本以上
- `implementation-executor`: file4本以上、module2つ以上、またはedit block4つ以上
- `tdd-executor`のtest authoring: test3件以上、test file3本以上、または既存test確認4本以上
- `git-review-followup-manager`: finding3件以上、file4本以上、またはbehavior area2つ以上

## Skillと役割

### 入口・委譲・全体統括

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `development-orchestrator` | task選定からdesign、implementation、review、tracking、Git、skill reflectionまで統括する | 親が実行 |
| `codex-delegation-executor` | implementation、design、verificationのexecutorを選ぶ | 親が実行 |
| `sub-agent-task-manager` | scope、profile、evidence mode、worker contractを固定してdispatchする | 親が実行 |
| `execution-cost-stabilizer` | retry、parallelism、costを安定化する | 親が実行 |
| `feedback-autonomy-boundary-manager` | 自律実行とuser confirmationの境界を決める | 親が実行 |
| `skill-authoring-wrapper` | built-in initializerをlocal standardへ補正する | 親が実行 |

### Planningとtracking

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `task-breakdown-planner` | issue/requestをtask、phase、dependencyへ分解する | 親が実行 |
| `task-consistency-manager` | trackingとactual scopeを一致させる | 親が実行 |
| `progress-sync-manager` | result、report、trackingを同期する | 親が実行 |
| `restart-handover-manager` | recorded stateからresume positionを復元する | 親が実行 |
| `handover-memo-writer` | next-chat ready handoverとartifactを作る | 親が実行 |

### Designとimplementation

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `design-doc-maintainer` | design impactと更新対象を判断する | 親が実行 |
| `design-executor` | design documentを編集する | worker切替対象 |
| `tdd-executor` | test-firstが必要なbehaviorとevidence方針を決める | 親が実行 |
| `implementation-executor` | scoped code/test変更を実施する | worker切替対象 |

### Reviewとquality gate

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | Codex review lifecycle、reviewer assignment、task gateを統括する | 親が実行 |
| `review-policy` | risk module、criterion、stage、stop、merge candidateを決める | 親またはdirect callerが実行 |
| `review-core` | ReviewRequestを直接確認しReviewResultを返す | reviewer workerが実行 |
| `review-result-renderer` | ReviewResultをMarkdown、chat、簡易PR commentへ変換する | 親またはreport workerが実行 |
| `markdown-word-checker` | Markdown lintと用語・設定gateを判定する | 親が実行 |
| `feedback-coding-standards-enforcer` | coding standardをreview/commit前に強制する | 親が実行 |
| `feedback-issue-intake-fallback-manager` | Issue要件取得失敗時にauthoritative requirementを確保する | 親が実行 |

### Feedback、Git、artifact

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `feedback-points-manager` | reusable workflow lessonとskillizationを管理する | 親が実行 |
| `feedback-points-sanitizer` | feedback setを独立整理する | sub-agentが実行 |
| `git-workflow-manager` | branch、commit、PR、follow-upを統括する | 親が実行 |
| `git-branch-starter` | taskに対応するbranchを用意する | 親が実行 |
| `git-commit-manager` | coherent commitを作る | 親が実行 |
| `git-pr-submitter` | evidence付きPRを作る | 親が実行 |
| `git-review-followup-manager` | findingをfix routeへ戻す | 親が実行 |
| `report-output-manager` | render済みtextをreports/ artifactへ保存する | 親が実行 |

## Skill契約一覧

| Skill | 主入力 | 主出力 | 完了条件 |
| --- | --- | --- | --- |
| `development-orchestrator` | tracking、reports、repo state、user-confirmed model | selected taskとworkflow route | task cycle完了またはexplicit blocker |
| `codex-delegation-executor` | work item、scope、evidence、confirmed model | executor decisionとresult | executorとevidenceが記録済み |
| `sub-agent-task-manager` | task、scope、profile、evidence mode、worker contract | validated structured resultまたはartifact | selected modeのprimary outputがvalid |
| `review-policy` | requirements、scope、risk、stage、previous result | review planとpolicy decision | selected criteria、stop、next stageがexplicit |
| `review-core` | ReviewRequest、criteria、target access | ReviewResult | planned criteriaが一回ずつdisposition済み |
| `review-enforcer` | task context、review plan、reviewer profile | structured ReviewResultとgate decision | bounded lifecycleとpolicy適用済み |
| `review-result-renderer` | ReviewResult、presentation type | rendered text | fixed result valuesを変更せずrender済み |
| `report-output-manager` | rendered text、repository、artifact metadata | report pathとwrite result | semantic changeなしでartifact保存済み |
| `markdown-word-checker` | Markdown file、repo lint config、gate context | lint evidenceとclassification | callerがdisposition可能なresultを返す |
| `task-breakdown-planner` | issue/request、constraints | tasks、phases、dependencies | next workerが推測なしで実行可能 |
| `task-consistency-manager` | current work、tracking、new scope | updated tracking | actual scopeと一致 |
| `progress-sync-manager` | latest results、reports、tracking | synchronized tracking | canonical stateと一致 |
| `restart-handover-manager` | tracking、feedback、recent reports | current positionとnext action | resume可能 |
| `handover-memo-writer` | chat context、repo/report state | handover textとartifact | next chatが独立再開可能 |
| `design-doc-maintainer` | task、behavior change、design docs | design impactとtargets | update policy確定 |
| `design-executor` | target docs、decided change | updated design | required editとcheck完了 |
| `tdd-executor` | scope、exit criteria、test/code | test-firstまたは省略判断 | implementation evidence方針がexplicit |
| `implementation-executor` | scoped task、owned files、validation target | code/test changesとrisk | review可能なstate |
| `feedback-points-manager` | process lesson、ledger | add/merge/skipとnext action | rationale記録済み |
| `feedback-points-sanitizer` | feedback set、cleanup scope | cleanup evidence | parent review可能 |
| `git-workflow-manager` | branch/commit/PR state | selected Git actions | required submission actions完了 |
| `git-branch-starter` | task、branch state | active branch | workが隔離済み |
| `git-commit-manager` | scoped change、validation | coherent commit | task commit作成済み |
| `git-pr-submitter` | branch、scope、evidence、reports | reviewable PR | context付きPR作成済み |
| `git-review-followup-manager` | findings、tracking、affected behavior | fix routeとupdated PR state | findingがresolvedまたはtracked |

## 主要な設計判断

- workflow entryは`development-orchestrator`へ固定する。
- review判断はMarkdown reportから独立したReviewResultで表す。
- `review-enforcer`はCodex runner/gateであり、review judgmentは`review-core`へ分離する。
- detailed criterionは`review-policy/references/code-review-criteria.md`だけで管理する。
- report templateはcriterion詳細を複製せず、criterion IDをmaterializeする。
- review artifactはstructured result取得後にrendererとartifact adapterで生成する。
- initial reviewはplanned coverageを完了し、fix verificationはbounded scopeに限定する。
- cold final後のnew independent Blocking/Highは追加reviewではなく`unstable`とする。
- ChatGPT chat向けstandalone workerはIssue #51で追加し、このshared contractを再利用する。
- implementationとdesignの実作業は判断系skillから分離する。
- large planning、tracking、resume、design intake、PR draftは最終判断を親へ残してsub-agent化できる。
- local skill追加・責務変更時は本書の2copyを同一内容へ同期する。

## 保守ルール

- new skill追加時はcall tree、role、contractを更新する。
- responsibilityまたは依存方向変更時は本書を先に更新する。
- structured contractのenumやcriterion IDを破壊的に変更しない。
- duplicated hierarchy fileはbyte-identicalに保つ。
- historical reportをdesign authorityとして扱わない。

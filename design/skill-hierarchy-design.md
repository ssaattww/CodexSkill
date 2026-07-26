# スキル階層設計

## 目的

Codex向け親/sub-agent flowと、利用者が親となるChatGPT chat worker flowを、共通workflow契約とruntime adapterへ分離して一元的に定義する。

この設計書をSkill hierarchyの正本とし、`skills/design/skill-hierarchy-design.md`と同一内容に保つ。

## 契約と実行方式

### runtime非依存の共通契約

`shared/workflow/`をCodexとChatGPTに共通する意味論の正本とする。

| Contract | 役割 |
| --- | --- |
| `common-work-contract.md` | authority、state discovery、scope、current HEAD、CI、report、handoff、merge boundary |
| `implementation-contract.md` | initial implementation、review follow-up、validation、implementation evidence |
| `review-contract.md` | normal review cycle、fix verification、independent final review、finding、coverage、verdict |
| `report-contract.md` | report mode、source selection、evidence fidelity、structure、write boundary |

runtime adapterは共通契約を参照し、同じ規則を再記述しない。

### runtime adapter

- `Codex adapter`
  - 親/sub-agent ownership、dispatch、Codex tool、completion gateを定義する
- `ChatGPT adapter`
  - 利用者が親となるdirect chat execution、permission、repository persistence、cross-chat handoffを定義する

### 実行方式

- `親が実行`: Codex親agentがSkillを直接実行する
- `親が呼び出し、sub-agentが実行`: Codex親agentがSkillを通じてsub-agentへ実作業を委譲する
- `利用者が親としてChatGPT chatで実行`: 利用者が独立chatを起動し、そのchatが指定Skillを直接実行する

ChatGPT workerは別workerまたはsub-agentを起動しない。

## Codex標準開発flow

```text
development-orchestrator [親]
├─ restart-handover-manager
├─ task-consistency-manager
├─ design-doc-maintainer
│  ├─ codex-delegation-executor
│  │  └─ design-executor
│  └─ task-consistency-manager
├─ tdd-executor [対象repositoryが要求する場合だけ]
│  ├─ codex-delegation-executor
│  │  └─ implementation-executor
│  └─ sub-agent-task-manager [test evidence]
├─ codex-delegation-executor
│  ├─ implementation-executor
│  │  └─ shared/workflow/implementation-contract.md
│  ├─ design-executor
│  ├─ sub-agent-task-manager [verification]
│  └─ report-output-manager
│     └─ shared/workflow/report-contract.md
├─ review-enforcer
│  ├─ shared/workflow/review-contract.md
│  ├─ markdown-word-checker
│  ├─ sub-agent-task-manager [normal reviewer]
│  ├─ sub-agent-task-manager [fresh independent final reviewer]
│  └─ report-output-manager
├─ progress-sync-manager
├─ git-workflow-manager
│  ├─ git-branch-starter
│  ├─ git-commit-manager
│  ├─ git-pr-submitter
│  └─ git-review-followup-manager
├─ feedback-points-manager
│  └─ feedback-points-sanitizer
└─ skill-authoring-wrapper
```

## 共通review lifecycle

CodexとChatGPTは`shared/workflow/review-contract.md`の同じlifecycleを使用する。

### normal review cycle

1. initial reviewでplanned coverageを定義し、全変更fileと直接依存を確認する
2. required findingがある場合はimplementationへ戻す
3. fix verificationでfinding、fix diff、直接影響、同一欠陥classを確認する
4. runtimeが許す限り同じnormal reviewerを継続する
5. finding identity、criteria、reviewed HEADを維持する

### independent final review

normal review cycle完了後、implementationとnormal reviewから独立したfresh reviewerがfinal current HEADを確認する。

共通要件:

- implementationを行っていない
- review fixを行っていない
- normal reviewerと異なる
- requirements、design、final diff、全変更file、直接依存、current HEAD固有validation evidenceを読む
- 過去review結論を読む前にindependent passを行う
- normal review reportとは別にindependent final review reportを作る
- final review後にHEADが変わればfix verificationとindependent final reviewをやり直す

### Codex adapter

- `review-enforcer`がnormal reviewer sub-agentを維持する
- independent final reviewは別のfresh reviewer sub-agentを原則`fork_turns: "none"`で起動する
- 親agent自身のreviewは代替にならない

### ChatGPT adapter

- initial reviewとfix verificationは同じnormal review chatを継続する
- independent final reviewは実装・fix・normal reviewを行っていない新規chatで実施する
- 利用者がreview chatの起動と再開を管理する

## ChatGPT chat worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [initial implementation]
├─ Chat B: chat-review-worker [initial review]
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat B: chat-review-worker [fix verification]
├─ Chat C: chat-review-worker [independent final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
```

ChatGPT adapterは次の共通契約を参照する。

- `chat-implementation-worker`
  - common work
  - implementation
  - report
  - ChatGPT handoff
- `chat-review-worker`
  - common work
  - review
  - report
  - ChatGPT handoff
- `chat-report-writer`
  - common work
  - report
  - ChatGPT handoff

## ChatGPT登録用Skillセット

Release対象は`skills/chat-*/SKILL.md`に一致する全Skillである。現在は次の3 Skillが該当する。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`

`scripts/build_chatgpt_worker_skills.py`は次を行う。

1. 全`skills/chat-*` Skillを自動検出する
2. Skill directory内の全fileをstagingへcopyする
3. Skillから参照される`shared/` dependencyを再帰的に解決する
4. dependencyを各Skillの`references/shared/`へcopyする
5. repository相対linkをSkill内相対linkへ書き換える
6. 各Skillがself-containedであることを確認する
7. root直下に全Skill directoryを持つ単一ZIPを生成する

repositoryには共通contractの手動copyを置かない。Release build時にだけ生成する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
├─ chat-review-worker/
└─ chat-report-writer/
```

各directoryは`SKILL.md`と必要な`references/shared/` dependencyを含む。

## ChatGPT固有補助文書

- `shared/chat-worker/handoff-contract.md`
  - independent chat間packet schema
- `shared/chat-worker/project-instruction-example.md`
  - ChatGPT Project Instruction例

これらはSkillではない。Skillから参照された場合にRelease ZIPへ同梱される。

## Release flow

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

### pull request

- ChatGPT adapter、共通契約、ChatGPT固有契約、build script、関連設計の変更で実行する
- ZIP build、link解決、root Skill集合、self-contained構造を検証する
- ZIPをworkflow artifactとして保存する
- Releaseとtagは更新しない

### main push

- merge後のmain HEADで同じbuildと検証を行う
- rolling tag `chatgpt-worker-skills-latest`をmerge後HEADへ更新する
- Release `ChatGPT Worker Skills`へ`chatgpt-worker-skills.zip`を添付または置換する

`workflow_dispatch`はbuild検証だけを行う。

## 標準作業手順

1. workflow開始時にCodexSkillの鮮度を確認する
2. 再開時は`restart-handover-manager`で状態を復元する
3. `development-orchestrator`がtaskを選択する
4. `task-consistency-manager`でtrackingを同期する
5. 設計影響があれば`design-doc-maintainer`を実行する
6. 対象repositoryがTDDを要求する場合だけ`tdd-executor`を適用する
7. `implementation-executor`でshared implementation contractを実行する
8. focused validationと必要なfull validationを実行する
9. `review-enforcer`でnormal review cycleを完了する
10. 別fresh reviewerによるindependent final reviewを完了する
11. `progress-sync-manager`でreportとtrackingを同期する
12. `git-workflow-manager`でcommit、push、PR更新まで行う
13. mergeは利用者が行う

CodexSkill repository自身にはTDDを適用しない。

## Skill一覧

### 入口と統括

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `development-orchestrator` | task選定から設計、実装、検証、review、Git提出までを統括する | 親が実行 |
| `codex-delegation-executor` | 実作業の委譲先と実行profileを決める | 親が実行 |
| `sub-agent-task-manager` | sub-agentのscope、model、reasoning、fork、report契約を固定する | 親が実行 |
| `execution-cost-stabilizer` | retry、parallelism、実行costを安定化する | 親が実行 |
| `feedback-autonomy-boundary-manager` | 自律継続と利用者確認の境界を決める | 親が実行 |
| `skill-authoring-wrapper` | shared contractとruntime adapterをrepository標準へ揃える | 親が実行 |

### 計画と追跡

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `task-breakdown-planner` | Issueをtaskとphaseへ分解する | 親が実行 |
| `task-consistency-manager` | task、phase、実scopeを同期する | 親が実行 |
| `progress-sync-manager` | report、tracking、実結果を同期する | 親が実行 |
| `restart-handover-manager` | recorded stateから再開位置を復元する | 親が実行 |
| `handover-memo-writer` | 別chat向けhandover memoを作成する | 親が実行 |

### 設計と実装

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `design-doc-maintainer` | 設計影響と更新対象を判断する | 親が実行 |
| `design-executor` | 決定済み設計変更を編集する | 親が実行 |
| `tdd-executor` | 対象repositoryが要求するtest-first証拠を定義する | 親が実行 |
| `implementation-executor` | shared implementation contractをCodexで実行する | 親が実行またはsub-agentへ委譲 |

### reviewと品質

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | shared review lifecycleをCodex reviewer sub-agentで強制する | 親が実行、reviewはsub-agent |
| `markdown-word-checker` | Markdown lintと表記ruleを検証する | 親が実行 |
| `feedback-coding-standards-enforcer` | coding standardを検証する | 親が実行 |
| `feedback-issue-intake-fallback-manager` | Issue取得失敗時に要件を確保する | 親が実行 |

### Gitとreport

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `git-workflow-manager` | branch、commit、push、PRを統括する | 親が実行 |
| `git-branch-starter` | 作業branchを準備する | 親が実行 |
| `git-commit-manager` | scoped commitを作成する | 親が実行 |
| `git-pr-submitter` | PRを作成または更新する | 親が実行 |
| `git-review-followup-manager` | review findingをimplementation flowへ戻す | 親が実行 |
| `report-output-manager` | shared report contractをCodexのpath・render・persistenceへ適用する | 親が実行 |

### ChatGPT worker

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `chat-implementation-worker` | shared implementation contractをdirect chatで実行する | 利用者が親としてChatGPT chatで実行 |
| `chat-review-worker` | shared review contractをdirect chatで実行する | 利用者が親としてChatGPT chatで実行 |
| `chat-report-writer` | shared report contractをdirect chatで実行する | 利用者が親としてChatGPT chatで実行 |

## 共通規則

- 対象repositoryのProject Instructionとrepository instructionを優先する
- TDD要否とtesting orderは対象repositoryが決める
- CodexSkill repository自身にはTDDを適用しない
- current HEAD SHAと一致するCI runだけをcurrent-HEAD evidenceとして使用する
- 別SHAのrunを代用しない
- detailed report、concise PR comment、handoffを混同しない
- unknown、held、unexplored、not-applicableを隠さない
- worker、sub-agent、親agentはmergeしない

## 保守規則

- CodexとChatGPTで同じ意味論が必要な場合は、先に`shared/workflow/`の正本を更新する
- runtime adapterへ共通規則をcopyしない
- `skills/chat-*/references/`へshared contract copyをcommitしない
- ChatGPT adapterまたは参照contract変更時はbundle builderを実行する
- Skill追加または責務変更時は本設計書を更新する
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`を同一内容に保つ
- ChatGPT lifecycleまたは配布構造変更時は`design/chat-worker-skill-design.md`も更新する
- review lifecycle変更時は`shared/workflow/review-contract.md`、runtime adapter、関連設計を同時更新する

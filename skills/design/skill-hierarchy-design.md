# スキル階層設計

## 目的

Codex向け親/sub-agent flowと、利用者が親となるChatGPT chat worker flowを一元的に定義する。

この設計書をskill hierarchyの正本とし、`skills/design/skill-hierarchy-design.md`と同一内容に保つ。

## 実行方式

- `親が実行`: Codex親agentがSkillを直接実行する。
- `親が呼び出し、sub-agentが実行`: 親agentがSkillを通じてsub-agentへ実作業を委譲する。
- `利用者が親としてChatGPT chatで実行`: 利用者が独立chatを起動し、そのchatが指定Skillを直接実行する。

ChatGPT workerは別workerまたはsub-agentを起動しない。Codex向けSkillとChatGPT向けSkillは別の実行系として扱う。

## Codex標準開発flow

```text
development-orchestrator [親]
├─ restart-handover-manager
├─ task-consistency-manager
├─ design-doc-maintainer
│  ├─ codex-delegation-executor
│  │  └─ design-executor
│  └─ task-consistency-manager
├─ tdd-executor
│  ├─ codex-delegation-executor
│  │  └─ implementation-executor
│  └─ sub-agent-task-manager [test evidence]
├─ codex-delegation-executor
│  ├─ implementation-executor
│  ├─ design-executor
│  ├─ sub-agent-task-manager [verification]
│  └─ report-output-manager
├─ review-enforcer
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

## Codexレビュー契約

Codexでも独立最終レビューを必須とする。

### 通常レビューcycle

1. 実装後に`review-enforcer`を実行する。
2. 専用reviewer sub-agentを選ぶ。
3. initial reviewとfix verificationは、原則として同じreviewerを継続利用する。
4. finding、review criteria、fix contextをreportへ保持する。
5. required findingがある場合は実装flowへ戻す。

### 独立最終レビュー

通常レビューcycle完了後に、別のfresh reviewer sub-agentを起動する。

- implementation sub-agentと異なること
- 通常reviewerと異なること
- review fixを実装していないこと
- 原則`fork_turns: "none"`で起動すること
- final current HEADを対象とすること
- 要件、設計、final diff、current HEAD固有validation evidenceを読むこと
- 過去review結論を読む前に独立passを行うこと
- 通常review reportとは別にindependent final review reportを作ること

独立最終レビューでrequired findingが出た場合は実装へ戻る。HEAD更新後は通常reviewerでfix verificationを行い、さらに別のfresh reviewerで独立最終レビューをやり直す。

normal reviewだけ、同じreviewerによる再reviewだけ、親agent自身のreviewだけでは完了条件を満たさない。

## ChatGPT chat worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [初回実装]
├─ Chat B: chat-review-worker [initial review]
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat C: chat-review-worker [fix verification]
├─ Chat D: chat-review-worker [cold final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
```

ChatGPTのcold final reviewは、実装またはreview fixを行っていない新規chatで実施する。

## ChatGPT登録用Skillセット

ChatGPTへ登録するSkillは次の3つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`

GitHub Releaseでは、3 Skillをルート直下に含む単一ZIPとして配布する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
│  ├─ SKILL.md
│  └─ references/handoff-contract.md
├─ chat-review-worker/
│  ├─ SKILL.md
│  └─ references/handoff-contract.md
└─ chat-report-writer/
   ├─ SKILL.md
   └─ references/handoff-contract.md
```

このZIPをChatGPTへアップロードし、3 Skillを一括登録する。

## 共通handoff contract

`handoff-contract.md`は4つ目のSkillではなく、3 Skillが同じhandoff形式を使うための補助文書である。

- 保守用原本: `shared/chat-worker/handoff-contract.md`
- 実行時copy: 各Skillの`references/handoff-contract.md`
- Release ZIPには各Skill内のcopyだけを含める
- 旧`skills/chat-worker-shared/`配置はSkillに見えるため使用しない

## Release flow

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

- 対象Skillが`main`へmergeされた後に実行する
- 3 Skillとcontract copyを検証する
- 単一`chatgpt-worker-skills.zip`を作成する
- rolling tag `chatgpt-worker-skills-latest`をmerge後HEADへ更新する
- GitHub Release `ChatGPT Worker Skills`へZIPを添付または置換する
- PR branchからReleaseを更新しない

## 標準作業手順

1. workflow開始時にCodexSkillの鮮度を確認する。
2. 再開時は`restart-handover-manager`で状態を復元する。
3. `development-orchestrator`がtaskを選択する。
4. `task-consistency-manager`でtrackingを同期する。
5. 設計影響があれば`design-doc-maintainer`を実行する。
6. 対象repositoryがTDDを要求する場合は`tdd-executor`を実行する。
7. `implementation-executor`で実装する。
8. focused validationと必要なfull validationを実行する。
9. `review-enforcer`で通常review cycleを完了する。
10. 別fresh reviewerによる独立最終reviewを完了する。
11. `progress-sync-manager`でreportとtrackingを同期する。
12. `git-workflow-manager`でcommit、push、PR更新まで行う。
13. mergeは利用者が行う。

## Skill一覧

### 入口と統括

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `development-orchestrator` | task選定から設計、実装、検証、レビュー、Git提出までを統括する | 親が実行 |
| `codex-delegation-executor` | 実作業の委譲先と実行profileを決める | 親が実行 |
| `sub-agent-task-manager` | sub-agentのscope、model、reasoning、fork、report契約を固定する | 親が実行 |
| `execution-cost-stabilizer` | retry、parallelism、実行コストを安定化する | 親が実行 |
| `feedback-autonomy-boundary-manager` | 自律継続と利用者確認の境界を決める | 親が実行 |
| `skill-authoring-wrapper` | local Skillをrepository標準へ揃える | 親が実行 |

### 計画と追跡

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `task-breakdown-planner` | issueをtaskとphaseへ分解する | 親が実行 |
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
| `implementation-executor` | code、test、documentation、configurationを実装する | 親が実行 |

### レビューと品質

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | 通常review cycleと独立最終reviewを必須化する | 親が実行、reviewはsub-agent |
| `markdown-word-checker` | Markdown lintと表記ルールを検証する | 親が実行 |
| `feedback-coding-standards-enforcer` | coding standardを検証する | 親が実行 |
| `feedback-issue-intake-fallback-manager` | Issue取得失敗時に要件を確保する | 親が実行 |

### Gitとreport

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `git-workflow-manager` | branch、commit、push、PRを統括する | 親が実行 |
| `git-branch-starter` | 作業branchを準備する | 親が実行 |
| `git-commit-manager` | scoped commitを作成する | 親が実行 |
| `git-pr-submitter` | PRを作成または更新する | 親が実行 |
| `git-review-followup-manager` | review findingを実装flowへ戻す | 親が実行 |
| `report-output-manager` | report pathとfilenameを標準化する | 親が実行 |

### ChatGPT worker

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `chat-implementation-worker` | 初回実装とreview follow-upを行う | 利用者が親としてChatGPT chatで実行 |
| `chat-review-worker` | initial、fix verification、cold final reviewを行う | 利用者が親としてChatGPT chatで実行 |
| `chat-report-writer` | evidenceを忠実にreport化する | 利用者が親としてChatGPT chatで実行 |

## 共通規則

- 対象repositoryのProject Instructionを優先する。
- CodexSkill repository自身にはTDDを適用しない。
- reviewはreportへ記録する。
- CIは対象current HEAD SHAに紐づくrunだけを使用する。
- 別SHAのrunを代用しない。
- reportとhandoffを混同しない。
- worker、sub-agent、親agentはmergeしない。

## 保守規則

- Skill追加または責務変更時は本設計書を更新する。
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`を同一内容に保つ。
- ChatGPT Skill package変更時はRelease workflowと専用設計書も更新する。
- `shared/chat-worker/handoff-contract.md`変更時は3 Skillのcopyを同期する。
- review lifecycle変更時は`review-enforcer`、本設計書、専用設計書を同時更新する。

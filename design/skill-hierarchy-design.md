# スキル階層設計

## 目的

Codex向け親／sub-agent flowと、利用者が親となるChatGPT chat worker flowを一元的に定義する。

実装、レビュー、レポート生成の意味論は親runtimeに依存しないcore Skillとして定義し、CodexとChatGPTはruntime wrapperからそれらを呼び出す。

この設計書をSkill hierarchyの正本とし、`skills/design/skill-hierarchy-design.md`と同一内容に保つ。

## 実行方式

- `親が実行`: Codex親agentがSkillを直接実行する。
- `親が呼び出し、sub-agentが実行`: Codex親agentがSkillを通じてsub-agentへ実作業を委譲する。
- `利用者が親としてChatGPT chatで実行`: 利用者が独立chatを起動し、そのchatが指定wrapper Skillを直接実行する。
- `runtime非依存Skillとして実行`: 親またはwrapperから渡されたcontextを使用し、Codex親、sub-agent、ChatGPT chat固有の制御を持たずに実作業を行う。

ChatGPT wrapperは別workerまたはsub-agentを起動しない。Codex向けwrapperとChatGPT向けwrapperは別の実行系として扱うが、実装、レビュー、レポートの意味論は同じcore Skillを使用する。

## Skill依存アーキテクチャ

```text
親非依存core Skill
├─ work-context-manager
├─ implementation-worker
├─ review-worker
└─ report-writer

runtime wrapper
├─ Codex
│  ├─ implementation-executor
│  ├─ review-enforcer
│  └─ report-output-manager
└─ ChatGPT
   ├─ chat-implementation-worker
   ├─ chat-review-worker
   ├─ chat-report-writer
   └─ chat-handoff-manager
```

### Core Skill

- `work-context-manager`
  - authority、scope、target identity、development policy、validation target、current-HEAD CI evidence、write boundaryを解決する
- `implementation-worker`
  - initial implementationとreview follow-upを実行する
- `review-worker`
  - initial review、fix verification、independent final reviewを実行する
- `report-writer`
  - evidenceの意味を変えずにreportと簡易PR commentを生成する

全core SkillはCodex親、Codex sub-agent、ChatGPT親chatのいずれにも依存しない。

### Runtime wrapper

Codex wrapperはsub-agent dispatch、reviewer identity、normal review continuity、fresh independent reviewer、report path、persistence、completion gateを所有する。

ChatGPT wrapperはcurrent-chat permission、connector、repository／PR persistence、chat continuity、cross-chat handoffを所有する。

共通動作を複数Skillから同一fileとして参照しない。共通動作は独立Skillとして定義し、wrapperまたは他のSkillがSkill名で呼び出す。

## Codex標準開発flow

```text
development-orchestrator [親]
├─ restart-handover-manager
├─ task-consistency-manager
├─ design-doc-maintainer
│  ├─ codex-delegation-executor
│  │  └─ design-executor
│  └─ task-consistency-manager
├─ tdd-executor [対象repositoryが明示要求する場合だけ]
│  ├─ codex-delegation-executor
│  │  └─ implementation-executor [wrapper]
│  │     ├─ work-context-manager
│  │     └─ implementation-worker
│  └─ sub-agent-task-manager [test evidence]
├─ codex-delegation-executor
│  ├─ implementation-executor [wrapper]
│  │  ├─ work-context-manager
│  │  └─ implementation-worker
│  ├─ design-executor
│  ├─ sub-agent-task-manager [verification]
│  └─ report-output-manager [wrapper]
│     ├─ work-context-manager
│     └─ report-writer
├─ review-enforcer [wrapper]
│  ├─ markdown-word-checker
│  ├─ sub-agent-task-manager [normal reviewer]
│  │  └─ review-worker
│  ├─ sub-agent-task-manager [fresh independent final reviewer]
│  │  └─ review-worker
│  └─ report-output-manager
│     └─ report-writer
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

## TDD適用境界

TDD要否は対象repositoryの明示的なinstruction、accepted design、または利用者指示が決める。

- `development-orchestrator`はgoverning sourceを確認する
- TDDが明示要求される場合だけ`tdd-executor`を呼ぶ
- TDDが要求されない場合は`not applicable`として通常implementationへ進む
- codeまたはtestを変更するという事実だけではTDD適用理由にならない
- CodexSkill repository自身の保守にはTDDを適用しない

CodexSkill固有の非TDD方針はroot `AGENTS.md`をrepository-level authorityとする。

## Codexレビュー契約

Codexでも独立最終レビューを必須とし、技術レビューの意味論には`review-worker`を使用する。

### 通常レビューcycle

1. 実装後に`review-enforcer`を実行する。
2. 専用normal reviewer sub-agentを選ぶ。
3. reviewerは`work-context-manager`でtargetとevidenceを解決する。
4. initial reviewとして`review-worker`を実行する。
5. finding、review criteria、reviewed HEAD、fix contextをreportへ保持する。
6. required findingがある場合はimplementation flowへ戻す。
7. fix後は原則として同じnormal reviewerを継続利用する。
8. `review-worker`のfix verificationでfinding解消、fix diff、直接影響、同一欠陥classを確認する。
9. required findingが解消または明示的にdispositionされるまで、bounded normal cycleを継続する。

元のnormal reviewerを継続できない場合は、replacement identityと理由を記録し、finding identity、criteria、reviewed HEAD、fix contextを完全に引き継ぐ。

### 独立最終レビュー

通常レビューcycle完了後に、別のfresh reviewer sub-agentを起動する。

- implementation sub-agentと異なること
- 通常reviewerと異なること
- review fixを実装していないこと
- 原則`fork_turns: "none"`で起動すること
- final current HEADを対象とすること
- 要件、設計、final diff、全変更file、直接依存、current HEAD固有validation evidenceを読むこと
- `review-worker`のindependent final reviewを実行すること
- 過去review結論を読む前に独立passを行うこと
- normal review reportとは別にindependent final review reportを作ること

独立最終レビューでrequired findingが出た場合はimplementationへ戻る。HEAD更新後はnormal reviewerでfix verificationを行い、さらに別のfresh reviewerで独立最終レビューをやり直す。

normal reviewだけ、同じreviewerによる再reviewだけ、親agent自身のreviewだけでは完了条件を満たさない。

## ChatGPT chat worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [initial implementation]
│  ├─ work-context-manager
│  ├─ implementation-worker
│  ├─ report-writer
│  └─ chat-handoff-manager
├─ Chat B: chat-review-worker [initial review]
│  ├─ work-context-manager
│  ├─ review-worker
│  ├─ report-writer
│  └─ chat-handoff-manager
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat B: chat-review-worker [fix verification]
├─ Chat C: chat-review-worker [independent final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
   ├─ work-context-manager
   ├─ report-writer
   └─ chat-handoff-manager
```

initial reviewとfix verificationは同じnormal review chatを継続する。independent final reviewは、implementation、review fix、normal reviewに参加していない新規chatで実施する。

### 初回実装

```text
Issue #<number>を開始してください。
```

`chat-implementation-worker`がrepository stateと権限を管理し、`work-context-manager`と`implementation-worker`を呼び出す。

### 初回レビュー

```text
PR #<number>を初回レビューしてください。
```

`chat-review-worker`がreview modeとreviewer identityを管理し、`review-worker`のinitial reviewを呼び出す。

### レビュー対応

```text
レビュー結果に対応してください。
```

初回実装chatを継続し、`implementation-worker`のreview follow-upでfinding、直接原因、影響境界、同一欠陥classだけを修正する。

### 修正確認

```text
PR #<number>の修正確認をしてください。
```

初回レビューと同じnormal review chatを継続し、`review-worker`のfix verificationを実行する。

### 独立最終レビュー

```text
PR #<number>を独立レビューしてください。
```

新規chatで`review-worker`のindependent final reviewを実行する。過去reviewの結論は独立pass後に照合する。

## ChatGPT登録用Skillセット

ChatGPTへ登録するwrapper Skillは次の4つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`
- `chat-handoff-manager`

必須依存core Skillは次の4つである。

- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

GitHub Releaseでは、8 Skillをそれぞれ独立したroot directoryとして含む単一ZIPを配布する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
├─ chat-review-worker/
├─ chat-report-writer/
├─ chat-handoff-manager/
├─ work-context-manager/
├─ implementation-worker/
├─ review-worker/
└─ report-writer/
```

各directoryには少なくとも`SKILL.md`が存在し、front matterの`name`とdirectory名を一致させる。

このZIPをChatGPTへuploadし、wrapperと依存core Skillを一括登録する。

## Handoff

handoff contractを複数Skillから同一fileとして参照しない。`chat-handoff-manager`を独立Skillとして使用する。

- reportとhandoffを別成果物とする
- repository write可能時はhandoffを`reports/handoffs/`へ保存する
- PRまたはIssueから一意に特定できる場合は次workerがconnectorで取得する
- 一意に特定できない場合だけ利用者へpathまたはpacket本文を求める
- 前workerの権限は次chatへ自動継承しない
- unknownを推測で補完しない
- target Skill、mode、必要権限、参照先をpacketへ記録する

## Release flow

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

### pull request

- ChatGPT wrapper、core Skill、builder、関連設計の変更で実行する
- build jobは`contents: read`だけを持ち、checkout credentialを保持しない
- PRのsynthetic merge SHAではなく実PR HEAD SHAをcheckoutする
- 全`chat-*` wrapperと必須core Skillを検出する
- missing Skill、front matter name不一致、symlink、Skill外`shared/`参照を拒否する
- 単一`chatgpt-worker-skills.zip`を作成する
- ZIP rootが検出Skill集合と一致することを確認する
- ZIPをworkflow artifactとして保存する
- rolling tagとGitHub Releaseは更新しない

### main push

- merge後のmain HEADでread-only build jobを実行する
- build成功後だけ別release jobへ`contents: write`を付与する
- build jobの検証済みartifactをrelease jobへ渡す
- rolling tag `chatgpt-worker-skills-latest`をmerge後HEADへ更新する
- GitHub Release `ChatGPT Worker Skills`へZIPを添付または置換する

`workflow_dispatch`はread-only build検証だけを行い、Releaseを更新しない。

Release時の共通file複製とrepository相対link書換は行わない。

## 標準作業手順

1. workflow開始時にCodexSkillの鮮度を確認する。
2. 再開時は`restart-handover-manager`で状態を復元する。
3. `development-orchestrator`がtaskを選択する。
4. `task-consistency-manager`でtrackingを同期する。
5. 設計影響があれば`design-doc-maintainer`を実行する。
6. `work-context-manager`でauthority、scope、target identity、development policy、validation target、write boundaryを解決する。
7. 対象repositoryがTDDを要求する場合は`tdd-executor`を実行する。
8. `implementation-executor`から`implementation-worker`を呼び出して実装する。
9. focused validationと必要なfull validationを実行する。
10. `review-enforcer`から`review-worker`を呼び出して通常review cycleを完了する。
11. 別fresh reviewerによる独立最終reviewを完了する。
12. `report-output-manager`から`report-writer`を呼び出してreportを保存する。
13. `progress-sync-manager`でreportとtrackingを同期する。
14. `git-workflow-manager`でcommit、push、PR更新まで行う。
15. mergeは利用者が行う。

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

### 親非依存core Skill

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `work-context-manager` | authority、scope、target identity、policy、validation、CI、write boundaryを解決する | runtime非依存Skillとして実行 |
| `implementation-worker` | initial implementationとreview follow-upを実施する | runtime非依存Skillとして実行 |
| `review-worker` | initial review、fix verification、independent final reviewを実施する | runtime非依存Skillとして実行 |
| `report-writer` | evidence-faithfulなreportと簡易PR commentを生成する | runtime非依存Skillとして実行 |

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
| `implementation-executor` | executorを管理し、`implementation-worker`を呼び出すCodex wrapper | 親が実行 |

### レビューと品質

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | reviewer identityと通常review cycle、独立最終reviewを管理するCodex wrapper | 親が実行、reviewはsub-agent |
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
| `git-review-followup-manager` | review findingをimplementation flowへ戻す | 親が実行 |
| `report-output-manager` | report pathとpersistenceを管理し、`report-writer`を呼び出すCodex wrapper | 親が実行 |

### ChatGPT runtime wrapper

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `chat-implementation-worker` | ChatGPT上の初回実装とreview follow-upを統括する | 利用者が親としてChatGPT chatで実行 |
| `chat-review-worker` | ChatGPT上のinitial、fix verification、independent final reviewを統括する | 利用者が親としてChatGPT chatで実行 |
| `chat-report-writer` | ChatGPT上のsource discovery、report永続化、PR commentを統括する | 利用者が親としてChatGPT chatで実行 |
| `chat-handoff-manager` | 独立chat間handoff packetを生成する | ChatGPT wrapperから呼び出す |

## 共通規則

- 対象repositoryのProject Instructionを優先する。
- 解決可能なrepository stateを利用者へ再質問しない。
- CodexSkill repository自身にはTDDを適用しない。
- implementationは自分の変更へreview verdictを出さない。
- reviewerはfindingを実装しない。
- reviewは詳細reportへ記録する。
- CIは対象current HEAD SHAに紐づくrunだけを使用する。
- 別SHAのrunを代用しない。
- reportとhandoffを混同しない。
- unknown、held、unexplored、失敗結果を消さない。
- core Skillとwrapperは自directory外の`shared/`fileへ依存しない。
- dependency Skillが存在しない場合、wrapperは処理を複製せずmissing dependencyとして停止する。
- worker、sub-agent、親agentはmergeしない。

## 保守規則

- Skill追加または責務変更時は本設計書を更新する。
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`を同一内容に保つ。
- ChatGPT Skill package変更時はRelease workflowと`design/chat-worker-skill-design.md`も更新する。
- ChatGPT Project Instruction例を変更する場合は`design/chatgpt-project-instruction-example.md`を更新する。
- review lifecycle変更時は`review-worker`、`review-enforcer`、`chat-review-worker`、本設計書、専用設計書を同時更新する。
- core Skill dependency変更時はCodex wrapper、ChatGPT wrapper、Release builder、両設計書を同時更新する。
- 既存設計書の変更時は、構成変更と無関係な節を削除せず、矛盾する箇所だけを置換する。

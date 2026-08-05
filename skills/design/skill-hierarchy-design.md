# スキル階層設計

## 目的

Codex向け親／sub-agent flowと、利用者が親となるChatGPT chat worker flowを一元的に定義する。

実装、レビュー、レポート生成の意味論は親runtimeに依存しないcore Skillとして定義し、task trackingは専用Skill、runtime固有処理はwrapperへ分離する。

この設計書をSkill hierarchyの正本とし、`skills/design/skill-hierarchy-design.md`と同一内容に保つ。

## 実行方式

- `親が実行`: Codex親agentがSkillを直接実行する。
- `親が呼び出し、sub-agentが実行`: Codex親agentがSkillを通じてsub-agentへ実作業を委譲する。
- `利用者が親としてChatGPT chatで実行`: 利用者が独立chatを起動し、そのchatが指定wrapper Skillを直接実行する。
- `runtime非依存Skillとして実行`: 親またはwrapperから渡されたcontextを使用し、runtime固有の制御を持たずに実作業を行う。

ChatGPT wrapperは別workerまたはsub-agentを起動しない。CodexとChatGPTは別runtime wrapperを使用するが、implementation、review、reportの意味論は同じcore Skillを使用する。

## Skill依存アーキテクチャ

```text
親非依存core Skill
├─ work-context-manager
├─ implementation-worker
├─ review-worker
└─ report-writer

task tracking Skill
├─ task-breakdown-planner
├─ task-consistency-manager
└─ progress-sync-manager

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

## Core Skill

- `work-context-manager`
  - authority、scope、target identity、development policy、validation target、current-HEAD CI evidence、write boundaryを解決する
- `implementation-worker`
  - initial implementationとreview follow-upを実行する
- `review-worker`
  - initial review、fix verification、independent final reviewを実行する
- `report-writer`
  - evidenceの意味を変えずにreportと簡易PR commentを生成する

全core SkillはCodex親、Codex sub-agent、ChatGPT chatのいずれにも依存しない。

## task tracking Skill

- `task-breakdown-planner`
  - taskを完了判定可能な単位へ分割し、dependencies、exit criteria、estimate、phaseを定義する
- `task-consistency-manager`
  - significant workの開始前とscope変更時にcanonical task trackingとの整合を確認する
- `progress-sync-manager`
  - active、blocked、verification、PR、完了状態をtask／phaseへ同期する

canonical task tracking fileはこれらの専用Skill経由で更新する。runtime wrapperまたはimplementation core Skillがtask更新規則を複製しない。

## Runtime wrapper

Codex wrapperはsub-agent dispatch、reviewer identity、normal review continuity、fresh independent reviewer、report path、persistence、completion gateを所有する。

ChatGPT wrapperはcurrent-chat permission、connector、repository／PR persistence、chat continuity、cross-chat handoffを所有する。

共通動作を複数Skillから同一fileとして参照しない。共通動作は独立Skillとして定義し、wrapperまたは他のSkillがSkill名で呼び出す。

## Codex標準開発flow

```text
development-orchestrator [親]
├─ restart-handover-manager
├─ work-context-manager
├─ task-consistency-manager
├─ task-breakdown-planner [必要時]
├─ design-doc-maintainer
├─ tdd-executor [対象repositoryが明示要求する場合だけ]
├─ implementation-executor [wrapper]
│  ├─ work-context-manager
│  └─ implementation-worker
├─ progress-sync-manager
├─ review-enforcer [wrapper]
│  ├─ work-context-manager
│  ├─ review-worker [normal reviewer]
│  └─ review-worker [fresh independent final reviewer]
├─ report-output-manager [wrapper]
│  ├─ work-context-manager
│  └─ report-writer
├─ git-workflow-manager
├─ feedback-points-manager
└─ skill-authoring-wrapper
```

significant workは`task-consistency-manager`確認後に開始する。taskが未登録、大きい、曖昧、依存またはexit criteria不足の場合だけ`task-breakdown-planner`を実行する。実装、検証、review follow-up、blocked、完了は`progress-sync-manager`で同期する。

## TDD適用境界

TDD要否は対象repositoryの明示的なinstruction、accepted design、または利用者指示が決める。

- TDDが明示要求される場合だけ`tdd-executor`を呼ぶ
- TDDが要求されない場合は`not applicable`として通常implementationへ進む
- codeまたはtestを変更するという事実だけではTDD適用理由にならない
- CodexSkill repository自身の保守にはTDDを適用しない

CodexSkill固有の非TDD方針はroot `AGENTS.md`をrepository-level authorityとする。

## Codexレビュー契約

Codexでも独立最終レビューを必須とし、技術レビューの意味論には`review-worker`を使用する。

### 通常レビューcycle

1. 実装後に専用normal reviewerを選ぶ。
2. `review-worker`のinitial reviewを実行する。
3. finding、review criteria、reviewed HEAD、fix context、held、unexploredを維持する。
4. required findingがある場合はimplementation flowへ戻す。
5. review findingが新しいscopeを要求する場合、実装前にtask trackingへ反映する。
6. fix後は原則として同じnormal reviewerがfix verificationを行う。
7. report、tracking、design、validationを保存してcommit／pushする。

### Pre-freeze gate

normal review cycle収束後、次を完了する。

- end-of-Issue Skill-gap decision
- feedback classificationとledger同期
- repository-backed normal handoff
- implementation、design、workflow、configuration、tracking、各report
- current-HEAD validationとCI evidence

上記でrepositoryが変わった場合はnormal reviewまたはfix verificationへ戻る。

### 独立最終レビュー

全非final変更をcommit／pushした後、その時点のHEADを`reviewed implementation HEAD`として固定し、implementation、review fix、normal reviewに参加していないfresh reviewerがindependent final reviewを実行する。

passing reportをrepositoryへ保存する場合は、予約済みreport pathだけを変更する1回のreport-attestation commitを許可する。attestation後はrepository commitを追加しない。

## ChatGPT chat worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [initial implementation]
│  ├─ work-context-manager
│  ├─ task-consistency-manager
│  ├─ task-breakdown-planner [必要時]
│  ├─ implementation-worker
│  ├─ progress-sync-manager
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

### ChatGPT実装契約

`chat-implementation-worker`は次の順でSkillを呼び出す。

1. `work-context-manager`
2. `task-consistency-manager`
3. 必要時のみ`task-breakdown-planner`
4. `implementation-worker`
5. `progress-sync-manager`
6. `report-writer`
7. `chat-handoff-manager`

実装開始前にtask tracking整合を確認し、taskが未登録または不十分なら先に更新する。progress、blocked、検証、PR、完了をtrackingへ同期した後にreportとhandoffを確定する。

initial reviewとfix verificationは同じnormal review chatを継続する。independent final reviewは、implementation、review fix、normal reviewに参加していない新規chatで実施する。

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

必須task tracking Skillは次の3つである。

- `task-breakdown-planner`
- `task-consistency-manager`
- `progress-sync-manager`

GitHub Releaseでは、11 Skillをそれぞれ独立したroot directoryとして含む単一ZIPを配布する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
├─ chat-review-worker/
├─ chat-report-writer/
├─ chat-handoff-manager/
├─ work-context-manager/
├─ implementation-worker/
├─ review-worker/
├─ report-writer/
├─ task-breakdown-planner/
├─ task-consistency-manager/
└─ progress-sync-manager/
```

build scriptは全`chat-*`wrapper、必須core Skill、必須task tracking Skillを検出し、ZIP root集合と一致することを検証する。

## Handoff

handoffは次を保持する。

- target repository、Issue、PR、branch、current HEAD
- task identity、tracking path、phase、state、dependencies、exit criteria
- accepted scope、non-goal、development policy、planned validation
- implementation evidence、failure diagnostics、blocked items
- finding、reviewed HEAD、held、unexplored
- report、PR comment、workflow run、artifact参照
- next workerが実行すべきtracking action

CI evidenceはpacketのtarget HEADと一致させ、別SHAのrunを代用しない。

## Skill dependencyの扱い

- wrapperは必要なcore Skillとtask tracking SkillをSkill名で呼び出す
- Skill間で同一fileを共有しない
- 各Skillは自directory内で完結する
- dependency Skillが利用できない場合、wrapperは処理を複製せずmissing dependencyとして停止する
- ChatGPT登録用ZIPにはwrapper、必須core Skill、必須task tracking Skillを同時に含める

## CodexSkill repositoryの検証方針

CodexSkill repository自身にはTDDを適用しない。

- Red/Green用testを追加しない
- この変更専用のcontract testを追加しない
- TDD用workflowを追加しない
- repository validator、Skill dependency validation、ZIP build、配布物構造確認を使用する
- 自動検証がない部分は設計書、Skill、workflow、Issue、PR説明の整合性をreviewする

## Merge境界

core Skill、task tracking Skill、wrapper、sub-agent、親agentはいずれもmergeを行わず、利用者がmerge判断と実行を所有する。

## 完了条件

- implementation、review、reportの意味論が親非依存core Skillとして定義されている
- task trackingの分割、整合、進捗同期が専用Skillへ分離されている
- ChatGPT実装workerがtask整合確認後に実装を開始する
- wrapperがtask更新規則を独自実装しない
- wrapper、core Skill、task tracking Skillの11 Skillを単一ZIPで登録できる
- hierarchy design、ChatGPT worker design、Skill contract、build scriptが同期している
- current HEAD固有CI規則が反映されている
- CodexSkill repositoryへTDDを適用しない
- reportとhandoffが別成果物として維持される
- mergeを実施しない

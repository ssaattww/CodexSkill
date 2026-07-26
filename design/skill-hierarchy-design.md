# Skill Hierarchy Design

## 目的

実装、レビュー、レポート生成を親runtime非依存のcore Skillとして定義し、CodexとChatGPTはruntime wrapperから呼び出す。

## Core Skill

```text
work-context-manager
├─ implementation-worker
├─ review-worker
└─ report-writer
```

- `work-context-manager`: authority、scope、target identity、development policy、validation、CI、write boundaryを解決する。
- `implementation-worker`: initial implementationとreview follow-upを実行する。
- `review-worker`: initial review、fix verification、independent final reviewを実行する。
- `report-writer`: evidence-faithfulなreportを生成する。

全core SkillはCodex親、Codex sub-agent、ChatGPT親chatのいずれにも依存しない。

## Codex flow

```text
development-orchestrator [parent]
├─ implementation-executor [wrapper]
│  ├─ work-context-manager
│  └─ implementation-worker
├─ review-enforcer [wrapper]
│  ├─ work-context-manager
│  ├─ review-worker
│  └─ report-writer
└─ report-output-manager [wrapper]
   ├─ work-context-manager
   └─ report-writer
```

Codex wrapperはsub-agent dispatch、reviewer identity、normal review continuity、fresh independent reviewer、report path、persistence、completion gateを所有する。

## ChatGPT flow

```text
user [parent]
├─ chat-implementation-worker [wrapper]
│  ├─ work-context-manager
│  ├─ implementation-worker
│  ├─ report-writer
│  └─ chat-handoff-manager
├─ chat-review-worker [wrapper]
│  ├─ work-context-manager
│  ├─ review-worker
│  ├─ report-writer
│  └─ chat-handoff-manager
└─ chat-report-writer [wrapper]
   ├─ work-context-manager
   ├─ report-writer
   └─ chat-handoff-manager
```

ChatGPT wrapperはcurrent-chat permission、connector、repository/PR persistence、chat continuity、cross-chat handoffを所有する。別workerまたはsub-agentを起動しない。

## Review lifecycle

1. normal reviewerがinitial reviewを行う。
2. finding修正後は同じnormal reviewerがfix verificationを行う。
3. normal cycle convergence後、実装・fix・normal reviewに参加していないfresh reviewerがindependent final reviewを行う。
4. HEADが変わった場合はfix verificationとindependent final reviewをやり直す。

## Skill dependency rule

共通動作を複数Skillから同一fileとして参照しない。共通動作は独立Skillとして定義し、wrapperまたは他のSkillがSkill名で呼び出す。

Skillは自ディレクトリ外の`shared/`fileへ依存しない。

## ChatGPT Release

Release ZIPは次を独立したroot Skill directoryとして含む。

- 全`chat-*` Skill
- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

release時の共通file複製は行わない。

## TDD適用境界

対象repositoryのinstructionがTDD要否を決める。CodexSkill repository自身には、利用者が明示変更しない限りTDDを適用しない。

## Merge境界

全Skillはmergeを行わず、利用者がmergeを所有する。

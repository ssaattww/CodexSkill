# ChatGPT Worker Skill Design

## 目的

実装、レビュー、レポート生成を親runtimeに依存しない独立Skillとして定義し、CodexとChatGPTはruntime固有wrapperからそれらを呼び出す。

repository外の`shared/`file参照には依存しない。

## アーキテクチャ

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

core Skillが作業の意味論を保持する。wrapperはruntime固有の起動方法、権限、永続化、reviewer identity、sub-agentまたはchatの継続、handoff transportだけを保持する。

## Core Skill

### work-context-manager

authority、repository state、accepted scope、target identity、development policy、validation target、current-HEAD CI evidence、write boundaryを解決する。

### implementation-worker

resolved contextを受け取り、initial implementationまたはreview follow-upを実行する。Codex親やChatGPT chatを前提とせず、自分の実装にreview verdictを出さない。

### review-worker

initial review、fix verification、independent final reviewを実行する。Codex親やChatGPT chatを前提とせず、findingを自分で実装しない。

### report-writer

evidence-faithfulなreportと簡易PR commentを生成する。repositoryへの保存方法はcallerが所有し、新しいtechnical judgmentを作らない。

## ChatGPT wrapper

- `chat-implementation-worker`は`work-context-manager`、`implementation-worker`、`report-writer`、`chat-handoff-manager`を呼び出す。
- `chat-review-worker`は`work-context-manager`、`review-worker`、`report-writer`、`chat-handoff-manager`を呼び出す。
- `chat-report-writer`は`work-context-manager`、`report-writer`、`chat-handoff-manager`を呼び出す。
- `chat-handoff-manager`は独立chat間packetの生成を所有する。

依存先は全て別のinstall済みSkillである。Skill外fileを共有参照しない。

## Codex wrapper

- `implementation-executor`はexecutorを選択・dispatchし、core implementation Skillを呼び出す。
- `review-enforcer`はnormal review continuityとfresh independent final reviewerを管理し、core review/report Skillを呼び出す。
- `report-output-manager`はreport pathと永続化を管理し、core report Skillを呼び出す。

## Release ZIP

`scripts/build_chatgpt_worker_skills.py`は次をZIP rootへ独立Skillとして収録する。

- 全`skills/chat-*/SKILL.md`
- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

builderはmissing Skill、front matter name不一致、symlink、Skill外`shared/`参照を拒否する。release時のfile複製は行わない。

## Project Instruction例

設定例はruntime Skillではないため、`design/chatgpt-project-instruction-example.md`へ置く。

## TDD適用境界

開発方法は対象repositoryが決める。CodexSkill repository自身の保守には、利用者が明示変更しない限りTDDを適用しない。

## Merge境界

core Skillとwrapperはいずれもmergeを行わず、利用者がmerge判断と実行を所有する。

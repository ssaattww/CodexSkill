# ChatGPT Chat Worker Skill Design

## 目的

利用者が親として複数のChatGPT chatを起動し、実装、レビュー、レポート作成を独立したworker Skillへ割り当てる構成を定義する。

同じ実装・レビュー・レポート規則をCodex用SkillとChatGPT用Skillへ重複記述せず、runtime非依存の共通契約とruntime固有adapterへ分離する。

ChatGPT chat同士は会話履歴を自動共有しない。repository、Issue、PR、report、handoffを永続的な引継ぎ情報として使用する。

## アーキテクチャ

```text
shared workflow contracts [runtime非依存の正本]
├─ common-work-contract.md
├─ implementation-contract.md
├─ review-contract.md
└─ report-contract.md
        │
        ├─ Codex adapters
        │  ├─ implementation-executor
        │  ├─ review-enforcer
        │  └─ report-output-manager
        │
        └─ ChatGPT adapters
           ├─ chat-implementation-worker
           ├─ chat-review-worker
           └─ chat-report-writer
```

共通契約は`shared/workflow/`に置く。CodexとChatGPTの各Skillは、同じ意味論を再記述せず、実行方式、委譲方式、権限境界、永続化方式だけを定義する。

### 共通契約

- `shared/workflow/common-work-contract.md`
  - authority、state discovery、scope、current HEAD、CI、report、handoff、merge boundary
- `shared/workflow/implementation-contract.md`
  - initial implementation、review follow-up、validation、implementation evidence
- `shared/workflow/review-contract.md`
  - normal review cycle、fix verification、independent final review、finding、coverage、verdict
- `shared/workflow/report-contract.md`
  - report mode、source selection、evidence fidelity、structure、write boundary

### ChatGPT固有契約

- `shared/chat-worker/handoff-contract.md`
  - 独立chat間で移送するpacket schema
- `shared/chat-worker/project-instruction-example.md`
  - ChatGPT Project Instructionの設定例

これらはSkillではない。ChatGPT Skillから参照される補助文書である。

## 対象Skill

現在のChatGPT用Skillは次の3つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`

Release対象は固定リストではなく、`skills/chat-*/SKILL.md`に一致する全Skillである。将来ChatGPT用Skillを追加した場合、命名規則を満たせばbuild対象へ自動追加される。

各ChatGPT Skillは別workerまたはsub-agentを起動しない。

## repository sourceと配布物

### repository source

ChatGPT adapterの`SKILL.md`は、repository上の共通契約を相対linkで参照する。

```text
skills/chat-implementation-worker/SKILL.md
  -> ../../shared/workflow/common-work-contract.md
  -> ../../shared/workflow/implementation-contract.md
  -> ../../shared/workflow/report-contract.md
  -> ../../shared/chat-worker/handoff-contract.md
  -> ../../shared/chat-worker/project-instruction-example.md
```

`skills/chat-*/references/`へ共通契約のcopyをcommitしない。保守時に編集する正本は`shared/`だけである。

### ChatGPT登録用ZIP

GitHub Releaseへ、単一ファイル`chatgpt-worker-skills.zip`を添付する。

生成物はルート直下にSkill directoryだけを持つ。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
│  ├─ SKILL.md
│  └─ references/shared/
│     ├─ workflow/
│     │  ├─ common-work-contract.md
│     │  ├─ implementation-contract.md
│     │  └─ report-contract.md
│     └─ chat-worker/
│        ├─ handoff-contract.md
│        └─ project-instruction-example.md
├─ chat-review-worker/
│  ├─ SKILL.md
│  └─ references/shared/
│     ├─ workflow/
│     │  ├─ common-work-contract.md
│     │  ├─ review-contract.md
│     │  └─ report-contract.md
│     └─ chat-worker/
│        └─ handoff-contract.md
└─ chat-report-writer/
   ├─ SKILL.md
   └─ references/shared/
      ├─ workflow/
      │  ├─ common-work-contract.md
      │  └─ report-contract.md
      └─ chat-worker/
         └─ handoff-contract.md
```

実際のdependency集合はlink解析結果で決まる。上記は現在の構成例である。

このZIPをChatGPTのSkill uploadへ指定し、複数Skillを一括登録する。

## Release build

`scripts/build_chatgpt_worker_skills.py`が配布物を生成する。

1. `skills/chat-*/SKILL.md`を全件検出する。
2. directory名とfront matterの`name`が一致することを確認する。
3. Skill directory内の全fileをstagingへcopyする。
4. Markdown linkから`shared/`配下のdependencyを再帰的に解決する。
5. dependencyを各Skillの`references/shared/`へcopyする。
6. repository相対linkをSkill内相対linkへ書き換える。
7. package内linkがSkill directory外へ出ないことを確認する。
8. ZIP root directoryが検出したSkill集合と一致することを確認する。
9. 同一sourceから再現可能なZIPを生成する。

この方式により、ChatGPT adapter内のfileと、そのadapterが参照するChatGPT固有・共通runtime dependencyはRelease ZIPへ全て含まれる。

設計書、GitHub Actions workflow、build script自体はrepository保守物であり、ChatGPTへinstallするruntime dependencyではないためSkill ZIPのrootへ追加しない。

## GitHub Actions

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

### PR

- ChatGPT adapter、共通契約、ChatGPT固有契約、build script、関連設計の変更で実行する
- ZIPを生成して構造とlinkを検証する
- 生成ZIPをworkflow artifactとして保存する
- GitHub Releaseとrolling tagは更新しない

### main push

- merge後の`main` HEADをcheckoutする
- PRと同じbuildと検証を実行する
- rolling tag `chatgpt-worker-skills-latest`をmerge後HEADへ更新する
- Release `ChatGPT Worker Skills`へ`chatgpt-worker-skills.zip`を添付または置換する

`workflow_dispatch`はbuild検証だけを行い、Releaseは更新しない。

## Project Instruction

Skill ZIPとは別に、対象ChatGPT Projectへ実際のProject Instructionを設定する。

維持する例は`shared/chat-worker/project-instruction-example.md`である。`chat-implementation-worker`が参照するためRelease ZIPにも含まれる。

Project Instructionは対象projectの正本であり、例をそのまま全projectへ強制しない。特にTDD要否は対象projectが決める。

## ChatGPT worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [initial implementation]
├─ Chat B: chat-review-worker [initial review]
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat B: chat-review-worker [fix verification]
├─ Chat C: chat-review-worker [independent final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
```

initial reviewとfix verificationは、利用可能であれば同じnormal review chatを継続する。finding identity、review criteria、reviewed HEADを維持するためである。

independent final reviewは、実装、review fix、normal reviewを行っていない新規chatで実施する。

### 初回実装

```text
Issue #<number>を開始してください。
```

implementation workerはIssue、task list、design、branch、PR、validation、current HEADをrepositoryから解決する。

### 初回レビュー

```text
PR #<number>を初回レビューしてください。
```

normal reviewerは全変更file、直接依存、要件、設計、current HEAD固有のvalidation evidenceを確認する。

### レビュー対応

```text
レビュー結果に対応してください。
```

初回実装chatを継続し、finding、直接原因、影響境界、同一欠陥classのsibling caseを対象に修正する。

### 修正確認

```text
PR #<number>の修正確認をしてください。
```

初回review chatを継続し、previous reviewed HEAD以降のfix、finding解消、regression evidence、直接影響を確認する。

### 独立最終レビュー

```text
PR #<number>を独立レビューしてください。
```

新規chatでfinal current HEADを独立確認する。過去reviewの結論は独立pass後に照合する。

## Codex reviewとの共通部分

CodexとChatGPTは`shared/workflow/review-contract.md`の同じlifecycleを使用する。

- normal review cycleはreviewer continuityを維持する
- final current HEADに対してindependent final reviewを行う
- final review後にHEADが変わればfix verificationとindependent final reviewをやり直す
- finding、coverage、verdict、report evidenceの意味は共通である

runtime差分は次だけである。

- Codex: `review-enforcer`がnormal reviewerとfresh reviewer sub-agentをdispatchする
- ChatGPT: 利用者がnormal review chatとfresh independent review chatを起動・再開する

## Worker責務

### `chat-implementation-worker`

- shared implementation contractをdirect chatで実行する
- target Projectのtesting policyに従う
- implementation report、PR簡易comment、handoffを出力する
- review verdictを出さない
- mergeしない

### `chat-review-worker`

- shared review contractをdirect chatで実行する
- initial review、fix verification、independent final reviewを扱う
- product code、test、workflowを変更しない
- review report、PR簡易comment、handoffを出力する
- mergeしない

### `chat-report-writer`

- shared report contractをdirect chatで実行する
- repository上のevidenceを忠実に統合する
- technical finding、test結果、CI結論を発明しない
- report、PR簡易comment、handoffだけを作成する
- mergeしない

## Handoff

- reportとhandoffは別成果物とする
- repository write可能時はhandoffを`reports/handoffs/`へ保存する
- PRまたはIssueから一意に特定できる場合は次workerがconnectorで取得する
- 一意に特定できない場合だけ利用者へpathまたはpacket本文を求める
- 前workerの権限は次chatへ自動継承しない
- handoff schemaは特定3 Skill名へ固定しない

## CodexSkill repositoryの検証方針

CodexSkill repository自身にはTDDを適用しない。

- Red/Green用testを追加しない
- 変更専用contract testを追加しない
- TDD用workflowを追加しない
- Python構文確認、bundle build、ZIP構造確認、link解決、既存lint、設計整合を通常検証として使用する

Release packaging workflowは製品codeのTDDではなく、配布物生成と構造検証のための運用workflowである。

## 完了条件

- runtime非依存の規則が`shared/workflow/`で一元管理されている
- CodexとChatGPTのSkillがruntime adapterに限定されている
- repository内に共通契約の手動copyがない
- 全`skills/chat-*` Skillが自動的にZIPへ含まれる
- 各Skillが参照するshared dependencyがZIP内へ同梱される
- ZIP rootにinstallable Skill directory以外を置かない
- PRでbundle validationが実行される
- main反映後にRelease assetが更新される
- ChatGPTとCodexの双方で独立最終レビューが必須である
- workerまたはagentがmergeしない

# ChatGPT Chat Worker Skill Design

## 目的

利用者が親として複数のChatGPT chatを起動し、実装、レビュー、レポート作成を独立したworker Skillへ割り当てる構成を定義する。

ChatGPT chat同士は自動的に会話履歴を共有しない。repository、Issue、PR、report、handoffを永続的な引継ぎ情報として使用する。

## 対象Skill

ChatGPT用Skillは次の3つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`

各Skillは別workerまたはsub-agentを起動しない。

## ChatGPT登録用ZIP

GitHub Releaseへ、次の構造を持つ単一ファイル`chatgpt-worker-skills.zip`を添付する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
│  ├─ SKILL.md
│  └─ references/
│     └─ handoff-contract.md
├─ chat-review-worker/
│  ├─ SKILL.md
│  └─ references/
│     └─ handoff-contract.md
└─ chat-report-writer/
   ├─ SKILL.md
   └─ references/
      └─ handoff-contract.md
```

このZIPをChatGPTのSkillアップロードへ指定し、3 Skillを一括登録する。

### shared contractの意味

`handoff-contract.md`はSkillではなく、3 Skillが共通利用する補助文書である。

- repository上の保守用原本: `shared/chat-worker/handoff-contract.md`
- 各Skillへ同梱する実行時copy: `<skill>/references/handoff-contract.md`
- 保守用原本そのものはChatGPTへ登録しない
- 3つのcopyは保守用原本と同一内容にする

以前の`skills/chat-worker-shared/`という配置は、4つ目のSkillに見えるため廃止する。

## Release生成

`.github/workflows/release-chatgpt-worker-skills.yml`は、対象ファイルが`main`へmergeされた後に実行する。

1. merge後の`main` HEADをcheckoutする。
2. 3 Skillの`SKILL.md`と`references/handoff-contract.md`の存在を確認する。
3. 3つのcontract copyが`shared/chat-worker/handoff-contract.md`と一致することを確認する。
4. 3 Skill directoryをルート直下に持つ単一ZIPを生成する。
5. rolling release tag `chatgpt-worker-skills-latest`をmerge後HEADへ更新する。
6. Release `ChatGPT Worker Skills`へ`chatgpt-worker-skills.zip`を添付または置換する。

merge前のPR branchではReleaseを更新しない。

## Project Instruction

Skill ZIPとは別に、対象ChatGPT ProjectへProject Instructionを設定する。

### RevMem向け例

```text
対象リポジトリ:
https://github.com/ssaattww/RevMem

タスク一覧:
tasks/tasks-status.md

Codex用Skillの参照リポジトリ:
https://github.com/ssaattww/CodexSkill

必要な作業手順やSkillの構成は、この参照リポジトリを確認してください。

リポジトリの参照・更新、IssueとPRの作成・更新、PRコメントの投稿にはGitHub connectorを使用してください。

作業開始時に、テスト失敗時の原因調査に必要な情報をartifactとして保存するworkflowが存在するか確認してください。存在しない場合は、対象workflowへ追加してください。artifactには、少なくともテスト結果、標準出力、標準エラー、および失敗原因の調査に必要なログを含めてください。

実装はTDDを基本とし、先にテストを追加して失敗を確認してから実装してください。このTDD方針と診断artifact workflowの追加方針はRevMemの実装作業に適用し、参照先のCodexSkillリポジトリには適用しません。

変更は、レビュー可能な小さな論理単位でcommit/pushしてください。

作業完了時は、詳細reportをrepositoryへ保存してください。それとは別に、変更内容と検証結果を要約した簡易reportをPRコメントへ投稿してください。

PRの作成または既存PRの更新まで行ってください。mergeは利用者が行うため、workerはmergeしないでください。

「最新のworkflow run」ではなく、対象PRのcurrent HEAD SHAとrunのhead SHAが一致するworkflow runだけをCI確認の対象としてください。HEAD更新後は新しいHEADに紐づくrunを確認してください。一致するrunがない場合はCI未実施として報告し、別SHAのrunを代用しないでください。
```

## ChatGPT worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [初回実装]
├─ Chat B: chat-review-worker [initial review]
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat C: chat-review-worker [fix verification]
├─ Chat D: chat-review-worker [cold final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
```

### 初回実装

```text
Issue #<number>を開始してください。
```

implementation workerはIssue、task list、design、branch、PR、validation、current HEADを自己解決する。

### 初回レビュー

```text
PR #<number>を初回レビューしてください。
```

initial reviewerは全変更ファイル、直接依存、要件、設計、current HEAD固有の検証証拠を確認する。

### レビュー対応

```text
レビュー結果に対応してください。
```

初回実装chatを継続し、該当findingと同一欠陥クラスのsibling caseだけを対象に修正する。

### 修正確認

```text
PR #<number>の修正確認をしてください。
```

previous reviewed HEAD以降のfix、finding解消、regression evidence、影響範囲を確認する。

### 独立最終レビュー

```text
PR #<number>を独立レビューしてください。
```

実装またはreview fixを行っていない新規chatで、final current HEADを独立確認する。過去reviewの結論は独立pass後に照合する。

## Codex review flow

Codexでも独立最終レビューを必須とする。

### 通常レビューcycle

- `review-enforcer`が専用reviewer sub-agentを起動する。
- initial reviewとfix verificationは、原則として同じreviewerを継続利用する。
- finding identity、review criteria、fix contextを維持する。

### 独立最終レビュー

通常レビューcycle完了後、別のfresh reviewer sub-agentを起動する。

- implementation sub-agentとは別であること
- 通常reviewerとは別であること
- review fixを実装していないこと
- 原則`fork_turns: "none"`で起動すること
- final current HEAD、要件、設計、final diff、validation evidenceを対象とすること
- 過去review結論を読む前に独立passを行うこと
- 独立最終review reportを別に作成すること

独立最終レビューでrequired findingが出た場合は実装へ戻る。HEAD更新後は、通常reviewerによるfix verificationを行い、その後さらに別のfresh reviewerで独立最終レビューをやり直す。

## Worker責務

### `chat-implementation-worker`

- 初回実装とreview follow-upを扱う
- 対象Projectのtesting policyに従う
- implementation report、handoff、PR簡易コメントを出力する
- review verdictを出さない
- mergeしない

### `chat-review-worker`

- initial review、fix verification、cold final reviewを扱う
- product code、test、workflowを変更しない
- review report、handoff、PR簡易コメントを出力する
- mergeしない

### `chat-report-writer`

- repository上のevidenceを忠実に統合する
- technical finding、test結果、CI結論を発明しない
- report、handoff、PR簡易コメントだけを作成する
- mergeしない

## Handoff

- reportとhandoffは別成果物とする
- repository write可能時はhandoffを`reports/handoffs/`へ保存する
- PRまたはIssueから一意に特定できる場合は次workerがconnectorで取得する
- 一意に特定できない場合だけ利用者へpathまたはpacket本文を求める
- 前workerの権限は次chatへ自動継承しない

## CodexSkill repositoryの検証方針

CodexSkill repository自身にはTDDを適用しない。

- Red/Green用testを追加しない
- この変更専用のcontract testを追加しない
- TDD用workflowを追加しない
- 既存lintまたはschema validationがあれば通常検証として使用する
- 自動検証がない場合は設計書、Skill、workflow、Issue、PR説明の整合性をreviewする

Release packaging workflowは製品コードのTDDではなく、配布物生成と構造検証のための運用workflowである。

## 完了条件

- ChatGPT用3 Skillが自己完結している
- 単一ZIPで3 Skillを一括登録できる構造になっている
- merge後にRelease assetが生成される
- shared contractがSkillとして誤認されない配置になっている
- ChatGPTとCodexの双方で独立最終レビューが必須になっている
- Codexの通常reviewerと独立最終reviewerが分離されている
- Project Instruction例が反映されている
- current HEAD固有CI規則が反映されている
- workerはmergeしない

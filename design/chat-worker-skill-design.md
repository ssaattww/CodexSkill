# ChatGPT Chat Worker Skill Design

## 目的

利用者が親として複数のChatGPT chatを起動し、実装、レビュー、レポート作成を独立したworker Skillへ割り当てる構成を定義する。

実装、レビュー、レポート生成の意味論は親runtimeに依存しないcore Skillへ置き、ChatGPT側はruntime固有wrapperからそれらを呼び出す。

ChatGPT chat同士は自動的に会話履歴を共有しない。repository、Issue、PR、report、handoffを永続的な引継ぎ情報として使用する。

Skill外の`shared/`file参照や、複数Skillから同一fileを直接参照する構成には依存しない。

## アーキテクチャ

```text
親非依存core Skill
├─ work-context-manager
├─ implementation-worker
├─ review-worker
└─ report-writer

ChatGPT runtime wrapper
├─ chat-implementation-worker
├─ chat-review-worker
├─ chat-report-writer
└─ chat-handoff-manager
```

core Skillが作業の意味論を保持する。wrapperはChatGPT固有の権限、connector利用、repository／PRへの永続化、chat continuity、handoff transportだけを保持する。

wrapperとcore Skillの依存は、同一fileへのpath参照ではなく、install済みSkill名による呼び出しとして表現する。

## 対象Skill

### ChatGPT runtime wrapper

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`
- `chat-handoff-manager`

各wrapperは別workerまたはsub-agentを起動しない。利用者が親としてchatを開始し、そのchat内で必要なcore Skillを呼び出す。

### 親非依存core Skill

- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

core SkillはCodex親、Codex sub-agent、ChatGPT chatのいずれにも依存しない。

## Core Skill責務

### `work-context-manager`

- user instruction、repository instruction、Issue、task、design、PR、report、handoffのauthorityを解決する
- accepted scope、non-goal、target identity、development policy、validation target、current-HEAD CI evidenceを解決する
- allowed writeとforbidden writeを明示する
- 解決可能なrepository stateを利用者へ再質問しない
- authority conflictまたは一意に解決できないproduct decisionは明示的に停止する

### `implementation-worker`

- initial implementationとreview follow-upを扱う
- 対象Projectのdevelopment／testing policyに従う
- accepted scope内で最小の一貫した変更を実施する
- focused validationと必要なbroader validationの証拠を返す
- 自分の実装へreview verdictを出さない
- mergeしない

### `review-worker`

- initial review、fix verification、independent final reviewを扱う
- 全変更file、直接依存、要件、設計、current HEAD固有の検証証拠を確認する
- finding、coverage、held、unexplored、verdictを返す
- product code、test、workflow、configurationを変更しない
- findingを自分で実装しない
- mergeしない

### `report-writer`

- implementation、review、verification、consolidated reportと簡易PR commentを生成する
- repository上のevidenceを忠実に表現する
- technical finding、severity、test結果、CI結論を発明しない
- unknown、held、unexplored、失敗結果を消さない
- 保存先と永続化はcallerへ委ねる
- mergeしない

## ChatGPT wrapper責務

### `chat-implementation-worker`

次のSkillを呼び出す。

1. `work-context-manager`
2. `implementation-worker`
3. `report-writer`
4. `chat-handoff-manager`

wrapperはcurrent chatの権限、GitHub connector、commit／push／PR操作、report保存、PR簡易コメント投稿を管理する。

### `chat-review-worker`

次のSkillを呼び出す。

1. `work-context-manager`
2. `review-worker`
3. `report-writer`
4. `chat-handoff-manager`

wrapperはreview mode、reviewer continuity、independent reviewer条件、report保存、PR comment投稿を管理する。

### `chat-report-writer`

次のSkillを呼び出す。

1. `work-context-manager`
2. `report-writer`
3. `chat-handoff-manager`

wrapperはsource discovery、保存先、PR comment投稿、権限境界だけを管理し、新しいtechnical judgmentを追加しない。

### `chat-handoff-manager`

- 独立chat間のhandoff packet schemaを所有する
- reportとhandoffを別成果物として扱う
- repository write可能時は`reports/handoffs/`へ保存する
- write不可時は完全なpacket本文を返す
- 前chatの権限を次chatへ引き継がない
- target Skill名、mode、必要な権限、参照先を明示する

## ChatGPT登録用ZIP

GitHub Releaseへ、次の構造を持つ単一ファイル`chatgpt-worker-skills.zip`を添付する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
│  └─ SKILL.md
├─ chat-review-worker/
│  └─ SKILL.md
├─ chat-report-writer/
│  └─ SKILL.md
├─ chat-handoff-manager/
│  └─ SKILL.md
├─ work-context-manager/
│  └─ SKILL.md
├─ implementation-worker/
│  └─ SKILL.md
├─ review-worker/
│  └─ SKILL.md
└─ report-writer/
   └─ SKILL.md
```

このZIPをChatGPTのSkill uploadへ指定し、wrapperと依存core Skillを一括登録する。

各directoryは独立Skillであり、別Skill directory内のfileやrepository外の`shared/`fileを参照しない。

## Release生成

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

### PR build

1. PRのsynthetic merge SHAではなく実PR HEAD SHAをcheckoutする。
2. checkout credentialを保持せず、`contents: read`だけで実行する。
3. 全`skills/chat-*/SKILL.md`を検出する。
4. 必須core Skillを検出する。
5. directory名とfront matterの`name`が一致することを確認する。
6. symlink、missing Skill、Skill外`shared/`参照を拒否する。
7. wrapperとcore Skillを独立root directoryとしてZIPへ収録する。
8. ZIP rootが検出したSkill集合と一致することを確認する。
9. 生成ZIPをworkflow artifactとして保存する。
10. rolling tagとGitHub Releaseは更新しない。

### main push

1. merge後の`main` HEADをcheckoutする。
2. PRと同じread-only buildを実行する。
3. build成功後だけ別release jobへ`contents: write`を付与する。
4. build jobの検証済みartifactをrelease jobへ渡す。
5. rolling tag `chatgpt-worker-skills-latest`をmerge後HEADへ更新する。
6. Release `ChatGPT Worker Skills`へ`chatgpt-worker-skills.zip`を添付または置換する。

PR branchと`workflow_dispatch`ではReleaseを更新しない。

Release時の共通file複製とrepository相対linkの書換は行わない。

## Project Instruction

Skill ZIPとは別に、対象ChatGPT ProjectへProject Instructionを設定する。

維持する設定例は`design/chatgpt-project-instruction-example.md`に置く。対象Projectのinstructionが正本であり、設定例をすべてのrepositoryへ強制しない。

### RevMem向け例

```text
対象リポジトリ:
https://github.com/ssaattww/RevMem

タスク一覧:
tasks/tasks-status.md

Skillの参照リポジトリ:
https://github.com/ssaattww/CodexSkill

必要な作業手順やSkillの構成は、この参照リポジトリを確認してください。

リポジトリの参照・更新、IssueとPRの作成・更新、PRコメントの投稿にはGitHub connectorを使用してください。

作業開始時に、テスト失敗時の原因調査に必要な情報をartifactとして保存するworkflowが存在するか確認してください。存在しない場合は、対象workflowへ追加してください。artifactには、少なくともテスト結果、標準出力、標準エラー、および失敗原因の調査に必要なログを含めてください。

RevMemの実装はTDDを基本とし、先にテストを追加して失敗を確認してから実装してください。このTDD方針と診断artifact workflowの追加方針はRevMemの実装作業に適用し、参照先のCodexSkillリポジトリには適用しません。

変更は、レビュー可能な小さな論理単位でcommit/pushしてください。

作業完了時は、詳細reportをrepositoryへ保存してください。それとは別に、変更内容と検証結果を要約した簡易reportをPRコメントへ投稿してください。

PRの作成または既存PRの更新まで行ってください。mergeは利用者が行うため、workerはmergeしないでください。

「最新のworkflow run」ではなく、対象PRのcurrent HEAD SHAとrunのhead SHAが一致するworkflow runだけをCI確認の対象としてください。HEAD更新後は新しいHEADに紐づくrunを確認してください。一致するrunがない場合はCI未実施として報告し、別SHAのrunを代用しないでください。
```

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

initial reviewとfix verificationは、利用可能であれば同じnormal review chatを継続する。independent final reviewだけを、implementation、review fix、normal reviewに参加していない新規chatで実施する。

### 初回実装

```text
Issue #<number>を開始してください。
```

`chat-implementation-worker`は`work-context-manager`でIssue、task list、design、branch、PR、validation、current HEADを自己解決し、`implementation-worker`へ渡す。

### 初回レビュー

```text
PR #<number>を初回レビューしてください。
```

normal review chatは`work-context-manager`で対象を解決し、`review-worker`の`initial review`を実行する。全変更file、直接依存、要件、設計、current HEAD固有の検証証拠を確認する。

### レビュー対応

```text
レビュー結果に対応してください。
```

初回実装chatを継続し、該当finding、直接原因、影響境界、同一欠陥classのsibling caseだけを対象に`implementation-worker`の`review follow-up`を実行する。

### 修正確認

```text
PR #<number>の修正確認をしてください。
```

初回レビューと同じnormal review chatを継続し、previous reviewed HEAD以降のfix、finding解消、regression evidence、影響範囲を`review-worker`の`fix verification`で確認する。

元のnormal review chatを利用できない場合、implementationへ参加していない別chatがfinding identity、review criteria、reviewed HEAD、fix contextを復元し、continuity変更をreportへ記録する。

### 独立最終レビュー

```text
PR #<number>を独立レビューしてください。
```

実装、review fix、normal reviewを行っていない新規chatで、final current HEADを`review-worker`の`independent final review`として独立確認する。過去reviewの結論は独立pass後に照合する。

独立最終レビュー後にHEADが変わった場合、normal reviewerによるfix verificationと、さらに別のfresh chatによる独立最終レビューをやり直す。

## Codex review flowとの共通性

Codexでも同じ`review-worker`を使用し、独立最終レビューを必須とする。

### 通常レビューcycle

- `review-enforcer`が専用reviewer sub-agentを起動する。
- initial reviewとfix verificationは、原則として同じreviewerを継続利用する。
- finding identity、review criteria、reviewed HEAD、fix contextを維持する。
- required findingがある場合はimplementation flowへ戻す。

### 独立最終レビュー

通常review cycle完了後、別のfresh reviewer sub-agentを起動する。

- implementation sub-agentと異なること
- 通常reviewerと異なること
- review fixを実装していないこと
- 原則`fork_turns: "none"`で起動すること
- final current HEADを対象とすること
- 要件、設計、final diff、全変更file、直接依存、current HEAD固有validation evidenceを読むこと
- 過去review結論を読む前に独立passを行うこと
- normal review reportとは別にindependent final review reportを作ること

normal reviewだけ、同じreviewerによる再reviewだけ、親agent自身のreviewだけでは完了条件を満たさない。

## Handoff

- reportとhandoffは別成果物とする
- `chat-handoff-manager`がhandoff packetのschemaと生成を所有する
- repository write可能時はhandoffを`reports/handoffs/`へ保存する
- PRまたはIssueから一意に特定できる場合は次workerがconnectorで取得する
- 一意に特定できない場合だけ利用者へpathまたはpacket本文を求める
- 前workerの権限は次chatへ自動継承しない
- CI evidenceはpacketのtarget HEADと一致させる
- unknownを推測で補完しない

## Skill dependencyの扱い

- wrapperは必要なcore SkillをSkill名で呼び出す
- core Skillとwrapperの間で同一fileを共有しない
- 各Skillは自directory内で完結する
- dependency Skillが利用できない場合、wrapperはcore処理を複製しない
- missing dependencyとして停止し、不足しているSkill名を明示する
- ChatGPT登録用ZIPにはwrapperと必須core Skillを同時に含める

## CodexSkill repositoryの検証方針

CodexSkill repository自身にはTDDを適用しない。

- Red/Green用testを追加しない
- この変更専用のcontract testを追加しない
- TDD用workflowを追加しない
- 既存lintまたはschema validationがあれば通常検証として使用する
- Skill front matter、依存Skill、ZIP構造、symlink、外部参照を通常検証する
- 自動検証がない部分は設計書、Skill、workflow、Issue、PR説明の整合性をreviewする

Release packaging workflowは製品コードのTDDではなく、配布物生成と構造検証のための運用workflowである。

## Merge境界

core Skillとwrapperはいずれもmergeを行わず、利用者がmerge判断と実行を所有する。

## 完了条件

- 実装、レビュー、レポートの意味論が親非依存core Skillとして定義されている
- ChatGPT wrapperがruntime固有責務だけを持つ
- wrapperとcore SkillがSkill外`shared/`fileへ依存していない
- wrapperと必須core Skillを単一ZIPで登録できる構造になっている
- merge後にRelease assetが生成される
- ChatGPTとCodexの双方で同じreview lifecycleを使用する
- initial reviewとfix verificationがnormal reviewer continuityを維持する
- 独立最終レビューが実装者とnormal reviewerから分離されている
- Project Instruction例が維持されている
- current HEAD固有CI規則が反映されている
- reportとhandoffが別成果物として維持されている
- core Skill、wrapper、sub-agent、親agentはmergeしない

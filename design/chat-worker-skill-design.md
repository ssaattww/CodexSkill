# ChatGPT Chat Worker Skill Design

## 目的

利用者が親として複数のChatGPT chatを起動し、実装、レビュー、レポート作成を独立したworker Skillへ割り当てる構成を定義する。

実装、レビュー、レポート生成の意味論は親runtimeに依存しないcore Skillへ置き、ChatGPT側はruntime固有wrapperからそれらを呼び出す。task trackingの正本更新は専用Skillへ委譲し、ChatGPT workerがtask更新規則を独自実装しない。

ChatGPT chat同士は会話履歴を自動共有しない。repository、Issue、PR、task tracking、report、handoffを永続的な引継ぎ情報として使用する。

Skill外の`shared/`file参照や、複数Skillから同一fileを直接参照する構成には依存しない。

## アーキテクチャ

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

ChatGPT runtime wrapper
├─ chat-implementation-worker
├─ chat-review-worker
├─ chat-report-writer
└─ chat-handoff-manager
```

core Skillが作業の意味論を保持する。task tracking Skillはtask分割、開始前整合、進捗・完了同期を所有する。wrapperはChatGPT固有の権限、connector利用、repository／PRへの永続化、chat continuity、handoff transportだけを保持する。

依存は同一fileへのpath参照ではなく、install済みSkill名による呼び出しとして表現する。

## 対象Skill

### ChatGPT runtime wrapper

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`
- `chat-handoff-manager`

各wrapperは別workerまたはsub-agentを起動しない。利用者が親としてchatを開始し、そのchat内で必要なSkillを呼び出す。

### 親非依存core Skill

- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

### task tracking Skill

- `task-breakdown-planner`
- `task-consistency-manager`
- `progress-sync-manager`

`task-consistency-manager`は実装開始前に対象作業がcanonical task trackingへ表現されていることを確認する。taskが大きい、曖昧、または未登録の場合は`task-breakdown-planner`で分割・明確化した後に実装へ進む。進捗、blocked、完了、PR、検証結果は`progress-sync-manager`でtask／phaseへ同期する。

## Core Skill責務

### `work-context-manager`

- user instruction、repository instruction、Issue、task、design、PR、report、handoffのauthorityを解決する
- accepted scope、non-goal、target identity、development policy、validation target、current-HEAD CI evidenceを解決する
- planned validationとrequired failure diagnosticsを明示する
- blocked、unknown、held、unexploredを区別する
- allowed writeとforbidden writeを明示する
- 解決可能なrepository stateを利用者へ再質問しない
- authority conflictまたは一意に解決できないproduct decisionは明示的に停止する

### `implementation-worker`

- initial implementationとreview follow-upを扱う
- 対象Projectのdevelopment／testing policyに従う
- accepted scope内で最小の一貫した変更を実施する
- focused validationと必要なbroader validationの証拠を返す
- failure diagnosticsとblocked itemsを構造化して返す
- 自分の実装へreview verdictを出さない
- mergeしない

### `review-worker`

- initial review、fix verification、independent final reviewを扱う
- 全変更file、直接依存、要件、設計、current HEAD固有の検証証拠を確認する
- reviewer identity、continuity、independence evidenceを返す
- finding、coverage、held、unexplored、verdictを返す
- independent final review時はreserved report pathとattestation条件を返す
- product code、test、workflow、configurationを変更しない
- findingを自分で実装しない
- mergeしない

### `report-writer`

- implementation、review、verification、consolidated reportと簡易PR commentを生成する
- repository上のevidenceを忠実に表現する
- technical finding、severity、test結果、CI結論を発明しない
- unknown、blocked、held、unexplored、失敗結果を消さない
- 保存先と永続化はcallerへ委ねる
- mergeしない

## task tracking Skill責務

### `task-breakdown-planner`

- 未登録または大きすぎる作業を、完了判定可能なtaskへ分割する
- dependencies、exit criteria、estimate、phaseを明示する
- canonical tracking fileの更新規則を維持する

### `task-consistency-manager`

- 実装開始前とscope変更時にtask／phaseと実作業を照合する
- significant workがtrackingへ存在しない場合は実装を開始しない
- reviewで追加作業が発生した場合は先にtrackingへ反映する

### `progress-sync-manager`

- active、blocked、verification、PR、完了状態をcanonical trackingへ同期する
- workerの実装結果とtrackingの記述を一致させる
- task完了時にexit criteriaと検証証拠を記録する

## ChatGPT wrapper責務

### `chat-implementation-worker`

次のSkillを順に呼び出す。

1. `work-context-manager`
2. `task-consistency-manager`
3. 必要時のみ`task-breakdown-planner`
4. `implementation-worker`
5. `progress-sync-manager`
6. `report-writer`
7. `chat-handoff-manager`

全7 Skillを配布ZIPへ含める。`task-breakdown-planner`はtaskが未登録、大きい、曖昧、依存またはexit criteria不足の場合だけ実行する。

wrapperはcurrent chatの権限、GitHub connector、commit／push／PR操作、report保存、PR簡易コメント投稿を管理する。task tracking fileは専用task tracking Skill経由でのみ更新する。

### `chat-review-worker`

次のSkillを呼び出す。

1. `work-context-manager`
2. `review-worker`
3. `report-writer`
4. `chat-handoff-manager`

review findingが新しい作業を要求する場合は、実装workerへhandoffし、実装workerが`task-consistency-manager`または`task-breakdown-planner`でtrackingへ反映する。

### `chat-report-writer`

次のSkillを呼び出す。

1. `work-context-manager`
2. `report-writer`
3. `chat-handoff-manager`

### `chat-handoff-manager`

- 独立chat間のhandoff packet schemaを所有する
- reportとhandoffを別成果物として扱う
- typed projectionとversioned raw source payloadを両方保持する
- task identity、task tracking path、tracking state、pending tracking actionを保持する
- repository write可能時は通常handoffを`reports/handoffs/`へ保存する
- write不可時は完全なpacket本文を返す
- 前chatの権限を次chatへ引き継がない

## ChatGPT登録用ZIP

GitHub Releaseへ、次の構造を持つ単一ファイル`chatgpt-worker-skills.zip`を添付する。

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

各directoryは`SKILL.md`を持つ独立Skillである。このZIPをChatGPTのSkill uploadへ指定し、wrapper、core Skill、task tracking Skillを一括登録する。

build scriptは全`chat-*`wrapper、必須core Skill、必須task tracking Skillを検出し、ZIP rootが期待集合と一致することを検証する。missing Skill、directory名とfront matter nameの不一致、symlink、Skill外`shared/`参照を拒否する。

## Release生成

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

### PR validation build

1. PRの実HEAD SHAをcheckoutする。
2. repository-wide validatorを実行する。
3. wrapper、core Skill、task tracking Skillを単一ZIPへ収録する。
4. ZIP rootと必須Skill集合を照合する。
5. 生成ZIPをworkflow artifactとして保存する。
6. PR validationではReleaseを更新しない。

### main反映後

main push時に同じvalidationとbuildを実行し、成功したartifactだけをrolling Releaseとversioned pre-releaseへ公開する。

`workflow_dispatch`はread-only validation／buildだけを行い、Releaseを更新しない。

## ChatGPT worker flow

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
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat B: chat-review-worker [fix verification]
├─ Chat C: chat-review-worker [independent final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
```

### 初回実装

`chat-implementation-worker`はIssue、task list、design、branch、PR、validation、current HEADを自己解決する。実装前にtask整合を確認し、必要ならtaskを分割・登録してから`implementation-worker`へ渡す。

### レビュー対応

review findingがtask scopeを追加または変更する場合、実装前にtrackingを同期する。単なる既存taskのfinding解消は同一taskのreview follow-upとして扱い、進捗と検証結果を`progress-sync-manager`で更新する。

### Pre-freeze gate

独立最終レビュー開始前に、implementation、design、workflow、configuration、tracking、normal review report、fix-verification report、verification report、Skill-gap decision、feedback classification、normal handoff、current-HEAD CI evidenceを保存する。

これらの処理でrepositoryが変わった場合はnormal review／fix verificationへ戻る。全pre-freeze変更を含むnormal cycleが収束するまでHEADをfreezeしない。

### 独立最終レビュー

実装、review fix、normal reviewを行っていない新規chatでfrozen HEADを独立確認する。passing reportをrepositoryへ保存する場合は、予約済みreport pathだけを変更する1回のreport-attestation commitを許可し、その後repository commitを追加しない。

## Handoff

handoffは次を保持する。

- target repository、Issue、PR、branch、current HEAD
- task identity、task tracking path、task state、phase、dependencies、exit criteria
- accepted scope、non-goal、development policy、planned validation
- implementation evidence、failure diagnostics、blocked items
- review finding、reviewed HEAD、held、unexplored
- report、PR comment、workflow run、artifact参照
- next workerが実行すべきtracking action

CI evidenceはpacketのtarget HEADと一致させ、別SHAのrunを代用しない。

## CodexSkill repositoryの検証方針

CodexSkill repository自身にはTDDを適用しない。

- Red/Green用testを追加しない
- この変更専用のcontract testを追加しない
- TDD用workflowを追加しない
- repository validator、Skill dependency validation、ZIP build、配布物構造確認を使用する
- 自動検証がない部分は設計書、Skill、workflow、Issue、PR説明の整合性をreviewする

## Merge境界

core Skill、task tracking Skill、wrapperはいずれもmergeを行わず、利用者がmerge判断と実行を所有する。

## 設計書保守方針

構成変更時はSkill contract、配布ZIP構成、hierarchy design、workflow、task tracking、reportを同期する。新しい構成と矛盾する記述を残さない。

## 完了条件

- ChatGPT実装workerが実装前にtask tracking整合を確認する
- taskが未登録または不十分な場合に専用Skillで分割・更新できる
- 実装進捗、blocked、検証、完了を専用Skillで同期できる
- wrapperがtask更新規則を独自実装しない
- wrapper、core Skill、task tracking Skillを単一ZIPで登録できる
- ZIP rootが11 Skillと一致する
- current HEAD固有のvalidation、workflow、artifactを確認できる
- reportとhandoffが別成果物として維持される
- TDDをCodexSkill repositoryへ適用しない
- mergeを実施しない

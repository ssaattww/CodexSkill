# スキル階層設計

## 目的

この設計書は、`/home/ibis/AI/CodexSkill/skills` 配下のローカル skill 群について、次の内容を一元的に定義する。

- 各 skill の役割
- 親 agent から見た呼び出し関係
- 親が実行する skill と、親が呼び出して sub-agent が実行する skill の区別
- 標準開発フローにおける責務分担

運用中のレポートよりも、この設計書を正本として扱う。

## 対象

- 対象リポジトリ: `/home/ibis/AI/CodexSkill`
- 対象範囲: `skills/` 配下のローカル skill

## 実行方式の定義

- `親が実行`: 親 agent がその skill を直接実行する。
- `親が呼び出し、sub-agent が実行`: 親 agent が skill を起動し、実作業は sub-agent が担当する。

補足:

- `親が実行` の skill でも、内部の一部工程を `sub-agent-task-manager` 経由で sub-agent に委譲する場合がある。
- その場合でも skill 全体の責務と完了判定は親が持つ。

## 標準開発フローの呼び出しツリー

```text
development-orchestrator [親が実行]
├─ restart-handover-manager [親が実行, 再開時のみ]
├─ task-consistency-manager [親が実行]
├─ design-doc-maintainer [親が実行]
│  ├─ codex-delegation-executor [親が実行]
│  │  └─ design-executor [親が実行, 実作業は切替対象]
│  └─ task-consistency-manager [親が実行]
├─ tdd-executor [親が実行]
│  ├─ codex-delegation-executor [親が実行]
│  │  └─ implementation-executor [親が実行, 実作業は切替対象]
│  └─ sub-agent-task-manager [親が実行, test実行はsub-agent]
├─ codex-delegation-executor [親が実行]
│  ├─ implementation-executor [親が実行, 実作業は切替対象]
│  ├─ design-executor [親が実行, 実作業は切替対象]
│  ├─ sub-agent-task-manager [親が実行, review/verificationはsub-agent]
│  └─ report-output-manager [親が実行]
├─ review-enforcer [親が実行]
│  ├─ sub-agent-task-manager [親が実行, reviewerは常にsub-agent]
│  └─ report-output-manager [親が実行]
├─ progress-sync-manager [親が実行]
├─ git-workflow-manager [親が実行]
│  ├─ git-branch-starter [親が実行]
│  ├─ git-commit-manager [親が実行]
│  ├─ git-pr-submitter [親が実行]
│  └─ git-review-followup-manager [親が実行]
│     ├─ task-consistency-manager [親が実行]
│     ├─ codex-delegation-executor [親が実行]
│     │  └─ implementation-executor [親が実行, 実作業は切替対象]
│     └─ report-output-manager [親が実行]
├─ feedback-points-manager [親が実行]
│  └─ feedback-points-sanitizer [親が呼び出し、sub-agent が実行]
└─ skill-authoring-wrapper [親が実行, issue完了時の親判断でlocal skill作成/更新が必要な場合]
```

## 補助フローの呼び出し関係

```text
feedback-coding-standards-enforcer [親が実行]
└─ sub-agent-task-manager [親が実行, standards検出/検証はsub-agent]

feedback-issue-intake-fallback-manager [親が実行]
├─ sub-agent-task-manager [親が実行, 要件抽出/照合はsub-agent]
└─ report-output-manager [親が実行]

restart-handover-manager [親が実行]
├─ sub-agent-task-manager [親が実行, 大きい再開文脈ではresume summaryをsub-agent化可能]
└─ reports/ と進捗ファイルを参照して再開状態を組み立てる

execution-cost-stabilizer [親が実行]
└─ 委譲前の実行計画とコスト制御を支援する

feedback-autonomy-boundary-manager [親が実行]
└─ 親が止まるべき確認境界を決める

skill-authoring-wrapper [親が実行]
└─ built-in `skill-creator` を内部利用して local skill を repo 標準へ補正する

task-breakdown-planner [親が実行]
└─ sub-agent-task-manager [親が実行, 大きい分解ではdraft作成をsub-agent化可能]

task-consistency-manager [親が実行]
└─ sub-agent-task-manager [親が実行, 大きいtracking監査ではauditをsub-agent化可能]

design-doc-maintainer [親が実行]
└─ sub-agent-task-manager [親が実行, 大きい設計影響調査ではimpact scanをsub-agent化可能]

git-pr-submitter [親が実行]
└─ sub-agent-task-manager [親が実行, 大きいPR文脈ではdraft準備をsub-agent化可能]
```

## skill 作成・更新フローの呼び出しツリー

```text
development-orchestrator [親が実行]
└─ skill-authoring-wrapper [親が実行]
   ├─ built-in `skill-creator` を参照して初期化経路を決める
   ├─ 新規 skill の場合は built-in `skill-creator` の初期化フローを使う
   ├─ 既存 skill の場合は既存 `SKILL.md` を読み、repo 標準へ正規化する
   ├─ 実在する canonical skill inventory がある場合だけそれを更新する
   └─ `skills/design/skill-hierarchy-design.md` と `design/skill-hierarchy-design.md` を同期更新する
```

## 標準作業フロー

### 1. 標準開発サイクル

通常の task は、親が次の順番で進める。

1. workflow 冒頭で `/home/ibis/AI/CodexSkill` が最新か確認し、安全に更新できるなら最新取得してから先へ進む。
2. 再開セッションなら `restart-handover-manager` を呼び、再開文脈を復元してから同じ workflow に戻る。
3. 新規着手で今回の作業対象がまだ曖昧なら、`development-orchestrator` がユーザーに何の作業をするか確認してから task 選定へ進む。
4. `development-orchestrator` が現在状態を確認し、次の task を 1 つ選ぶ。
5. `task-consistency-manager` で task と phase の追跡状態を整える。
6. 設計影響がある場合は `design-doc-maintainer` を呼ぶ。
7. 設計文書の実編集が必要なら、`codex-delegation-executor` を通して `design-executor` に流す。
8. `tdd-executor` で最小の testable behavior と failing test 方針を定める。
9. テスト作成やコード作成が必要なら、`codex-delegation-executor` を通して `implementation-executor` に流す。
10. build、test、environment verification のような証拠作業が必要なら、`codex-delegation-executor` から `sub-agent-task-manager` を使って sub-agent に流す。
11. 実装が一段落したら `review-enforcer` を呼び、レビュー専用 sub-agent を実行する。
12. 指摘があれば `git-review-followup-manager` または通常の実装フローに戻して修正する。
13. `progress-sync-manager` で report と tracking を同期する。
14. `git-workflow-manager` で branch、commit、PR まで進める。
15. issue または task が完了したら、親が skill 化判断を行い、必要に応じて `feedback-points-manager` を呼び、commit 時点で skill 改善 loop を issue へ引き継ぐ。

大きい task では、`task-breakdown-planner`、`task-consistency-manager`、`design-doc-maintainer`、`restart-handover-manager`、`git-pr-submitter` の内部作業の一部を `sub-agent-task-manager` 経由で draft/audit/scan へ切り出してよい。ただし最終判断と反映は親が持つ。

暫定の切替指標は次を使う。

- `task-breakdown-planner`: task 候補 5 件以上、phase 3 件以上、依存関係 4 件以上、または分解前に読む資料 4 件以上
- `task-consistency-manager`: stale/missing の疑い 3 件以上、対象 task 行 5 行以上、または review/discovery 起点の調整点 3 件以上
- `restart-handover-manager`: recent report 5 本以上、証拠ソース 4 件以上、候補 next task 3 件以上、または tracking 間の矛盾 2 系統以上
- `design-doc-maintainer`: 候補設計書 3 本以上、契約面 2 種以上、比較対象設計ファイル 4 本以上
- `git-pr-submitter`: report 参照 3 本以上、validation evidence 3 件以上、要約すべき変更グループ 4 件以上
- `codex-delegation-executor`: 実装対象ファイル 4 本以上、対象 module/dir 2 つ以上、実 edit chunk 4 つ以上、または安全に書く前に読む実装ファイル 5 本以上
- `design-executor`: 対象設計ファイル 3 本以上、1 ファイル内の edit block 4 つ以上、または比較対象設計ファイル 4 本以上
- `implementation-executor`: 対象ファイル 4 本以上、対象 module 2 つ以上、実 edit block 4 つ以上
- `tdd-executor` の test authoring 部分: 追加・更新する test 3 件以上、test file 3 本以上、または事前確認が必要な既存 test file 4 本以上
- `git-review-followup-manager`: 対応 finding 3 件以上、対象 file 4 本以上、対象 behavior area 2 つ以上

### 2. sub-agent を使うときの内部順

sub-agent を使う作業は、親が必ず次の順番で準備してから実行する。

1. `codex-delegation-executor` または呼び出し元 skill が、sub-agent を使うべき作業だと判断する。
2. `sub-agent-task-manager` が task purpose、scope、non-goals、読むべき skill を定義する。
3. `report-output-manager` を呼び、`reports/` 配下の report path を決める。
4. 親が標準テンプレートで report file を先に作る。
5. 親が sub-agent に、読むべき `SKILL.md`、report path、既存 report を先に読んで空欄または placeholder だけ埋めること、format を変えないことを明示して dispatch する。
6. review や investigation では、sub-agent は parent が切った diff だけに閉じず、必要な周辺コードを workspace から直接読む。
7. sub-agent が作業し、既存 report の見出し順、空行、既存記述を保持したまま結果を書く。
8. 親が report を確認し、完了条件を満たしているか判定する。

### 3. レビュー差し戻し時の再入フロー

レビューで指摘が出た場合は、次の順番で元の実装フローへ戻す。

1. `review-enforcer` が findings を report に残した状態で task を未完了に戻す。
2. `git-review-followup-manager` が、その指摘を現 task で直すか、新 task に切るかを決める。
3. tracking 変更が必要なら `task-consistency-manager` を呼ぶ。
4. 修正作業は `codex-delegation-executor` を通し、必要に応じて `implementation-executor` に流す。
5. 修正後は再度 `review-enforcer` に戻し、再レビューを通す。
6. 問題がなければ `progress-sync-manager` と `git-workflow-manager` に進む。

### 4. skill 作成・更新フロー

local skill を新規作成または実質更新するときは、親が次の順番で進める。

1. `development-orchestrator` が end-of-issue の親判断として local skill 作成または更新が必要だと決め、`skill-authoring-wrapper` を呼ぶ。
2. `skill-authoring-wrapper` を入口にして、対象 skill の目的、配置先、new/update 区分を定める。
3. built-in `skill-creator` を読み、初期化に使う部分と、repo 標準へ補正する部分を切り分ける。
4. 新規 skill の場合は built-in `skill-creator` の初期化フローを使って skill directory を作る。
5. 既存 skill の更新の場合は、既存 `SKILL.md` の意図を残すべき部分と、repo 標準へ正規化すべき部分を分ける。
6. `skill-authoring-wrapper` が `SKILL.md` を repo 標準の section と契約粒度へ揃える。
7. 実行委譲や switchable な実装系があるなら、`codex-delegation-executor` 前提の書き方と暫定数値基準を入れる。
8. canonical file の更新経路制約が必要なら、その skill からしか触らないことを `SKILL.md` に明記する。
9. 実在する canonical skill inventory または registry file がある場合だけ、それを最終的な skill 意図に合わせて更新する。
10. skill inventory、呼び出しツリー、役割、契約一覧のどれかが変わるなら `skills/design/skill-hierarchy-design.md` と `design/skill-hierarchy-design.md` を同期更新する。
11. skill 設計が repo 標準に揃ったら、その skill を採用対象として扱う。

## skillと役割

この章では、各 skill について「何の責務を持つか」を役割として明示する。

### 入口と全体統括

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `development-orchestrator` | 全体フローの入口として、task 選定から設計、TDD、委譲、レビュー、進捗同期、Git、issue 完了時の振り返りまでを統括する。 | `親が実行` |
| `codex-delegation-executor` | 実装・検証・調査を誰が実行するかを決め、sub-agent 必須カテゴリを正しく委譲する。 | `親が実行` |
| `sub-agent-task-manager` | sub-agent へ渡す task の範囲、読むべき skill、report path、report template 保持ルール、完了条件を固定する。 | `親が実行` |
| `execution-cost-stabilizer` | 無駄な再実行や過剰並列を抑え、委譲実行のコストと不安定さを下げる。 | `親が実行` |
| `feedback-autonomy-boundary-manager` | 自律実行してよい範囲と、ユーザー確認で止まるべき境界を決める。 | `親が実行` |
| `skill-authoring-wrapper` | built-in `skill-creator` をラップし、この repo 標準の粒度で local skill を作成・更新する。 | `親が実行` |

### 計画と追跡

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `task-breakdown-planner` | 大きな issue や依頼を task と phase に分解し、依存関係と exit criteria を明確にする。 | `親が実行` |
| `task-consistency-manager` | 実際に必要な作業が `tasks-status.md` と `phases-status.md` に漏れなく反映されている状態を保つ。 | `親が実行` |
| `progress-sync-manager` | report や進捗管理ファイルを、実際の作業結果に合わせて同期する。 | `親が実行` |
| `restart-handover-manager` | tracking と reports から現在地を復元し、再開時の次アクションを明確にする。大きい文脈では要約下書きを sub-agent に切り出せる。 | `親が実行` |

### 設計

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `design-doc-maintainer` | 設計変更が必要かを判断し、どの設計成果物を更新するべきかを決める。大きい設計影響調査は sub-agent に切り出せる。 | `親が実行` |
| `design-executor` | 決定済みの設計変更に基づいて、設計文書や breaking changes 記録を実際に編集する。 | `親が実行` |

### 実装と TDD

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `tdd-executor` | 実装前にテスト方針と failing test を定義し、実装が従うべき証拠を先に作る。 | `親が実行` |
| `implementation-executor` | task scope に沿って、コード作成とテスト作成の実作業を担う。 | `親が実行` |

### レビューと品質ゲート

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | task 完了前に必ずレビューを通し、review report が残るまで完了扱いにしない。 | `親が実行` |
| `feedback-coding-standards-enforcer` | API ドキュメント、命名、解析ルールなどのコーディング規約を review/commit 前に強制する。 | `親が実行` |
| `feedback-issue-intake-fallback-manager` | issue 要件の取得が失敗したときに、代替経路で authoritative な要件を確保する。 | `親が実行` |

### Feedback ガバナンスと skill 化

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `feedback-points-manager` | 再利用可能な workflow lesson を `feedback-points.md` で管理し、skill 化するかどうかを判断する。 | `親が実行` |
| `feedback-points-sanitizer` | noisy な feedback points を独立した立場で整理し、親が判断しやすい状態に整える。 | `親が呼び出し、sub-agent が実行` |

### Git 提出フロー

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `git-workflow-manager` | branch、commit、PR、review follow-up まで含めた Git 提出フロー全体を統括し、`1 task -> 1 commit` の既定方針も持つ。 | `親が実行` |
| `git-branch-starter` | 現在の task や issue に合う作業 branch を作る。 | `親が実行` |
| `git-commit-manager` | スコープのきれいな commit を作り、コミット文フォーマットを管理する。 | `親が実行` |
| `git-pr-submitter` | review 可能な形で PR を作成する。大きい PR 文脈では本文下書きや evidence 収集を sub-agent に切り出せる。 | `親が実行` |
| `git-review-followup-manager` | review 指摘を task 化し、修正作業を実装フローへ戻す。 | `親が実行` |

### レポート

| Skill名 | 役割 | 実行方式 |
| --- | --- | --- |
| `report-output-manager` | `reports/` 配下の report 配置、ファイル名、テンプレート参照を標準化する。 | `親が実行` |

## skill契約一覧

この章では、各 skill の入力、出力、完了条件を設計レベルで要約する。

### 入口と全体統括

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `development-orchestrator` | tasks/phases、recent reports、feedback-points、repo state | 現在 task と次の実行経路 | 1 task 分の標準サイクル完了または明確な blocking 状態 |
| `codex-delegation-executor` | 実行対象の work item、scope、evidence 要件 | executor 決定、委譲結果、report evidence | executor 決定と結果記録が完了 |
| `sub-agent-task-manager` | task purpose、scope、読むべき skill、report path 要件、workspace context 方針 | dispatch 済み sub-agent task、pre-created report、review 済み evidence | report 作成と review 済み evidence の確認完了 |
| `execution-cost-stabilizer` | delegated task plan、retry pressure、parallelism 候補 | 安定化された実行計画 | 次アクションが無駄なく scoped されている |
| `feedback-autonomy-boundary-manager` | 次の planned action、assumption、approval risk | continue または stop の明示判断 | continue/stop 判断が理由付きで明確 |
| `skill-authoring-wrapper` | skill purpose、target location、new/update distinction、repo standards | repo-standard local skill、updated hierarchy design documents、必要なら実在 inventory の更新 | built-in `skill-creator` 出力が repo 標準に補正されている |

### 計画と追跡

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `task-breakdown-planner` | issue/request scope、constraints、existing tasks/phases | tasks、phases、dependencies、exit criteria | 次 task を他 agent が推測なしで実行できる。大きい分解では sub-agent draft を parent が採用する |
| `task-consistency-manager` | current work item、tasks/phases、new scope | 更新済み tracking、明確な next step | tracking が実 scope と一致。大きい監査では sub-agent audit を parent が確認する |
| `progress-sync-manager` | 最新の task/review/verification/git 結果、reports | 同期済み tracking と references | canonical tracking が実状態と一致 |
| `restart-handover-manager` | feedback-points、tasks/phases、recent reports | current position、next task、open deps | 再開時の次アクションが明示されている。大きい文脈では sub-agent summary を parent が採用する |

### 設計

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `design-doc-maintainer` | task/issue scope、behavior change、related design docs | design impact 判断、更新対象の設計成果物 | design reflection と必要な更新方針が確定。大きい影響面では sub-agent scan を parent が採用する |
| `design-executor` | target design files、intended change、breaking change 要否 | 更新済み design docs、残 ambiguity の報告 | 必要な設計文書編集が完了 |

### 実装と TDD

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `tdd-executor` | task scope、exit criteria、relevant tests/code | test targets、failing test 方針、期待挙動 | 実装前に test-driven な証拠が定義済み |
| `implementation-executor` | scoped task、target files、validation target | code/test changes、changed files、remaining risks | scoped 実装が review/validation 可能な状態 |

### レビューと品質ゲート

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `review-enforcer` | task-scoped diff、review scope、workspace context、validation context | review report、findings または no findings、disposition | review evidence が report に残り disposition 済み |
| `feedback-coding-standards-enforcer` | changed files、API diff、repo standards | standards evidence、violation fixes または rationale | standards-sensitive change の確認と記録が完了 |
| `feedback-issue-intake-fallback-manager` | issue id/URL、available retrieval paths、partial context | authoritative requirements report、confidence、gaps | requirements と confidence が report に明示済み |

### Feedback ガバナンスと skill 化

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `feedback-points-manager` | candidate process lesson、active FP ledger、duplicate context | FP add/merge/skip 判断、skillization status、次アクション対応 | FP 判断と rationale が ledger か report に残る |
| `feedback-points-sanitizer` | active FP set、cleanup scope、duplicate references | cleanup report、classification result、candidate groups | parent review 用の cleanup evidence が report に残る |

### Git 提出フロー

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `git-workflow-manager` | branch/commit/PR state、task readiness | selected Git actions、submission path、commit shape decision | branch/commit/PR の必要アクション完了と、その task の commit 形が決定済み |
| `git-branch-starter` | task or issue scope、branch state、naming basis | active branch context | 適切な branch に作業が隔離されている |
| `git-commit-manager` | scoped changes、review/validation state、commit convention | coherent commit(s)、formatted commit message | task に対応した commit 作成完了 |
| `git-pr-submitter` | branch、task scope、review/validation evidence、report refs | reviewable PR | 必要コンテキスト付きの PR 作成完了。大きい PR 文脈では sub-agent draft を parent が確定する |
| `git-review-followup-manager` | review findings、tracking state、affected behavior | tracked follow-up、fix route、updated PR state | findings が解決または明示 tracking 済み |

### レポート

| Skill名 | 入力 | 出力 | 完了条件 |
| --- | --- | --- | --- |
| `report-output-manager` | repo root、item name、issue/task/topic prefix | concrete report path と filename | caller が使う report path が明示済み |

## 主要な設計判断

- workflow 入口は `development-orchestrator` の一箇所に固定し、再開時も `restart-handover-manager` から直接始めず `development-orchestrator` へ戻して続行する。
- レビューは親がゲートを持つが、レビュワー実行は必ず sub-agent とする。
- 設計文書編集とコード/テスト作成は、判断系 skill から分離し、`design-executor` と `implementation-executor` に寄せる。
- `sub-agent` は単独で存在する主体ではなく、常に親から呼び出される実行形態として扱う。
- `feedback-points-sanitizer` は、独立視点での整理が価値になるため、例外的に「親が呼び出し、sub-agent が実行」として明示する。
- 大きい planning/tracking/restart/design-intake/pr-draft 系作業は、最終判断を親に残したまま draft/audit/scan を `sub-agent` へ切り出してよい。
- switchable な skill の「大きい」の判定は、上記の暫定数値基準を使う。
- local skill の新規作成と実質更新は、できるだけ `skill-authoring-wrapper` を共通入口にする。
- `skill-authoring-wrapper` の既定 caller は `development-orchestrator` とし、宙ぶらりんな local skill authoring を作らない。
- 判断責務を上位 skill に寄せるのは、その判断が固定 caller を持つサブツリー内部で閉じる場合に限る。`1対多` 構造や単独利用されうる下位 skill では、上位に寄せすぎず、下位は参照先を明示して従う形を基本とする。
- local skill 群の最新維持責任は workflow 入口の `development-orchestrator` が持ち、作業着手前に `/home/ibis/AI/CodexSkill` の鮮度確認を行う。
- skill 改善ループの継続確認は active FP ではなく issue を正本とし、issue 作成後の FP は active ledger から外す。
- commit 時点では active `feedback-points.md` が再び空になる運用を既定とし、skill 改善ループは issue 側へ引き継いでから commit を通す。

## 保守ルール

- 新しい skill を追加したら、この設計書のツリーと一覧を更新する。
- 呼び出し関係が変わったら、まずこの設計書を更新してから関連 report を更新する。
- 実行方式の表現は `親が実行` と `親が呼び出し、sub-agent が実行` に統一する。

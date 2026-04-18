# CodexSkill スキル階層一覧

## 概要

- リポジトリ: `/home/ibis/AI/CodexSkill`
- 対象: `skills/` 配下のローカル skill
- 総数: 24
- 実行方式の内訳:
  - `親が実行`: 23
  - `親が呼び出し、sub-agent が実行`: 1

## 読み方

- `実行方式 = 親が実行` は、親 agent がその skill を直接実行することを意味します。
- `実行方式 = 親が呼び出し、sub-agent が実行` は、親 agent が起動し、実作業は sub-agent が担当することを意味します。
- `親が実行` の skill でも、内部処理の一部を sub-agent に委譲するものがあります。その場合は用途欄に補足しています。
- 下のツリーは「親がどの skill を呼ぶか」を優先して表現しています。
- 同じ skill が複数の親から呼ばれる場合は、ツリー上で重複して登場します。

## 1. 呼び出しツリー

### 1-1. 標準開発フローの親子関係

```text
development-orchestrator [親が実行]
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
└─ feedback-points-manager [親が実行]
   └─ feedback-points-sanitizer [親が呼び出し、sub-agent が実行]
```

### 1-2. 補助的な呼び出し関係

```text
feedback-coding-standards-enforcer [親が実行]
└─ sub-agent-task-manager [親が実行, standards検出/検証はsub-agent]

feedback-issue-intake-fallback-manager [親が実行]
├─ sub-agent-task-manager [親が実行, 要件抽出/照合はsub-agent]
└─ report-output-manager [親が実行]

restart-handover-manager [親が実行]
└─ reports/ と進捗ファイルを参照して再開状態を組み立てる

execution-cost-stabilizer [親が実行]
└─ 委譲前の実行計画とコスト制御を支援する

feedback-autonomy-boundary-manager [親が実行]
└─ 親が止まるべき確認境界を決める
```

## 2. 入口と全体統括

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `development-orchestrator` | 次の task を選び、設計、TDD、委譲、レビュー、進捗同期、Git、issue 完了時の振り返りまで全体フローを統括する入口 skill。 | `親が実行` |
| `codex-delegation-executor` | 実装系作業を親でやるか sub-agent に回すかを決め、レビューや検証のような mandatory sub-agent 作業も管理する委譲ポリシー skill。 | `親が実行` |
| `sub-agent-task-manager` | sub-agent への依頼内容、読むべき skill、report file、完了条件を整えて dispatch する skill。 | `親が実行` |
| `execution-cost-stabilizer` | 再実行の無駄や過剰並列を抑え、委譲実行のコストと不安定さを減らすための skill。 | `親が実行` |
| `feedback-autonomy-boundary-manager` | そのまま自律実行するか、ユーザー確認で止まるかの境界を決める skill。 | `親が実行` |

## 3. 計画と追跡

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `task-breakdown-planner` | 大きな issue や依頼を task と phase に分解し、依存関係や exit criteria を明確にする skill。 | `親が実行` |
| `task-consistency-manager` | 実装前後の作業内容が `tasks-status.md` と `phases-status.md` に正しく表現されているかを保証する skill。 | `親が実行` |
| `progress-sync-manager` | 進捗管理ファイルや report 参照を実際の状態に同期する skill。 | `親が実行` |
| `restart-handover-manager` | tracking と reports から現在地を復元し、再開時の次アクションを明確にする skill。 | `親が実行` |

## 4. 設計

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `design-doc-maintainer` | 設計文書の更新が必要かを判断し、どの設計成果物を変えるべきかを決める skill。 | `親が実行` |
| `design-executor` | すでに決まった設計変更に基づいて、設計文書や breaking changes 記録を実際に編集する skill。委譲ポリシーにより親または sub-agent に実作業が割り当てられます。 | `親が実行` |

## 5. 実装と TDD

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `tdd-executor` | 実装前にテスト方針と failing test の期待を定義する skill。検証用の test 実行は別途 mandatory sub-agent 作業です。 | `親が実行` |
| `implementation-executor` | task scope が決まった後に、コード作成とテスト作成の実作業を行う skill。委譲ポリシーにより親または sub-agent に実作業が割り当てられます。 | `親が実行` |

## 6. レビューと品質ゲート

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | task 完了前に必ずレビューを通すためのゲート skill。判定は親が持ちますが、実レビュワーは常に sub-agent です。 | `親が実行` |
| `feedback-coding-standards-enforcer` | API ドキュメント、命名、解析ルールなどのコーディング規約を review/commit 前に強制する skill。検出や検証の一部は sub-agent を使います。 | `親が実行` |
| `feedback-issue-intake-fallback-manager` | 通常経路で issue 要件が取れないときに、代替手段で authoritative な要件を確保する skill。要件抽出や照合の一部は sub-agent を使います。 | `親が実行` |

## 7. Feedback ガバナンスと skill 化

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `feedback-points-manager` | 再利用可能な workflow lesson を `feedback-points.md` で管理し、skill 化判断を行う skill。 | `親が実行` |
| `feedback-points-sanitizer` | noisy な feedback points を独立した立場で整理・分類し、親が最終判断しやすい状態にする skill。 | `親が呼び出し、sub-agent が実行` |

## 8. Git 提出フロー

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `git-workflow-manager` | branch、commit、PR、review follow-up まで含めた Git 提出フロー全体をまとめる skill。 | `親が実行` |
| `git-branch-starter` | 現在の task や issue に合う作業 branch を作る skill。 | `親が実行` |
| `git-commit-manager` | スコープのきれいな commit を作り、コミット文フォーマットも管理する skill。 | `親が実行` |
| `git-pr-submitter` | review 可能な形で PR を作成する skill。 | `親が実行` |
| `git-review-followup-manager` | review 指摘を task 化し、修正作業を実装フローへ戻す skill。 | `親が実行` |

## 9. レポート

| Skill名 | 何をするためのものか | 実行方式 |
| --- | --- | --- |
| `report-output-manager` | `reports/` 配下の report 配置、ファイル名、テンプレート参照を決める skill。 | `親が実行` |

## 10. 依存関係の見取り図

| 親 skill | よく使う下位 skill / 関連 skill |
| --- | --- |
| `development-orchestrator` | `task-consistency-manager`, `design-doc-maintainer`, `tdd-executor`, `codex-delegation-executor`, `review-enforcer`, `progress-sync-manager`, `git-workflow-manager`, `feedback-points-manager` |
| `design-doc-maintainer` | `design-executor`, `task-consistency-manager` |
| `tdd-executor` | `implementation-executor`, `sub-agent-task-manager` |
| `codex-delegation-executor` | `implementation-executor`, `design-executor`, `sub-agent-task-manager`, `report-output-manager` |
| `review-enforcer` | `sub-agent-task-manager`, `report-output-manager` |
| `git-workflow-manager` | `git-branch-starter`, `git-commit-manager`, `git-pr-submitter`, `git-review-followup-manager` |
| `feedback-points-manager` | `feedback-points-sanitizer` |

## 11. 現在の責務境界メモ

- コード実装は、オーケストレーションや委譲説明に散らばるのではなく、実作業としては `implementation-executor` に寄せています。
- 設計文書編集は、設計判断の副作用として散らばるのではなく、実作業としては `design-executor` に寄せています。
- レビューは parent がゲートを持ちますが、レビュワー実行は常に sub-agent です。
- 現在、skill 単体としては `feedback-points-sanitizer` だけが「親が呼び出し、sub-agent が実行」に分類されています。

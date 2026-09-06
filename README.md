# CodexSkill

CodexとChatGPTで使うSkillを管理するリポジトリです。

このREADMEは利用者向けの入口です。Skill間の厳密な責務、依存関係、review lifecycle、CI契約は[スキル階層設計](design/skill-hierarchy-design.md)を正本とします。

## まず何を使うか

| やりたいこと | 主な入口 | 状態 |
| --- | --- | --- |
| CodexでIssue対応、設計、実装、検証、レビュー、PR提出まで進める | `development-orchestrator` | 利用可能 |
| ChatGPTの別chatを使って実装する | `chat-implementation-worker` | 利用可能 |
| ChatGPTの別chatでレビューする | `chat-review-worker` | 利用可能 |
| ChatGPTでレポートを作成・保存する | `chat-report-writer` | 利用可能 |
| OpenSCADで3D CADを作成、理解、修正、検証する | `openscad` | PR #66で設計中。まだ未実装 |

内部Skillを個別に選ぶ必要がない場合は、上記の入口から開始します。`work-context-manager`、`implementation-worker`、`review-worker`、`report-writer`などは、入口Skillから呼び出される共通処理です。

## 全体構成

```text
利用者
├─ ソフトウェア開発workflow
│  ├─ Codex
│  │  └─ development-orchestrator
│  │     ├─ 計画・tracking
│  │     ├─ 設計
│  │     ├─ 実装
│  │     ├─ validation
│  │     ├─ review
│  │     ├─ report
│  │     └─ Git／PR
│  │
│  └─ ChatGPT
│     ├─ chat-implementation-worker
│     ├─ chat-review-worker
│     ├─ chat-report-writer
│     └─ chat-handoff-manager
│        └─ runtime非依存core Skillを共有
│
└─ 利用者向けdomain Skill
   └─ openscad [PR #66で設計中、未実装]
```

開発workflow Skillとdomain Skillは役割が異なります。

- **開発workflow Skill**: repositoryのIssue対応、設計、実装、review、report、Git提出など、ソフトウェア開発の進め方を管理します。
- **domain Skill**: CADなど特定分野の成果物を直接作成・解析・修正します。domain Skill自身はGit提出や独立reviewの仕組みを再実装しません。

## ソフトウェア開発workflow

### Codex

通常の入口は`development-orchestrator`です。

大まかな流れは次の通りです。

```text
要件とrepository stateを確認
  ↓
task／phaseを確認・更新
  ↓
必要なら設計を更新
  ↓
実装
  ↓
validation
  ↓
通常reviewと修正確認
  ↓
独立最終review
  ↓
report／PR提出
  ↓
mergeは利用者が実施
```

実装、レビュー、レポートの意味論は、Codex固有処理から分離したcore Skillに置いています。

| Core Skill | 主な役割 |
| --- | --- |
| `work-context-manager` | authority、scope、branch、HEAD、validation、write boundaryを解決する |
| `implementation-worker` | 初回実装とreview follow-upを実行する |
| `review-worker` | initial review、fix verification、independent final reviewを実行する |
| `report-writer` | evidenceを変形せず詳細reportとPR要約を生成する |

Codex側のwrapperやmanagerが、sub-agent、Git、report保存、review lifecycleなどのruntime固有処理を管理します。

### ChatGPT

ChatGPTでは利用者が親となり、用途ごとに独立chatを使えます。

| Skill | 用途 |
| --- | --- |
| `chat-implementation-worker` | 初回実装とreview指摘対応 |
| `chat-review-worker` | initial review、fix verification、independent final review |
| `chat-report-writer` | report生成と永続化 |
| `chat-handoff-manager` | chat間のhandoff |

ChatGPT用配布ZIPは、この4 wrapperと4 core Skillの計8 Skillを含みます。OpenSCADのようなdomain Skillはこのworker ZIPとは別の配布単位です。

詳細は[ChatGPT worker設計](design/chat-worker-skill-design.md)を参照してください。

## OpenSCAD Skill

`openscad`は、WindowsネイティブのCodexからOpenSCADを扱う利用者向けdomain SkillとしてPR #66で設計中です。**現在は設計段階で、`skills/openscad/`はまだ存在しません。**

実装後は次の用途を一つのSkillで扱う設計です。

| Mode | 用途 |
| --- | --- |
| Quick | スペーサー、ブラケットなど単純な部品を素早く作成する |
| Design | 複数featureや相互依存寸法を持つ新規部品を設計する |
| Refine | **既存SCADの構造とparameter依存を理解し、設計意図を維持して修正する** |
| Modify | STLを全面再構築せず、穴追加などの局所変更を行う |
| Replicate | 写真と既知寸法から形状を再現する |
| Reconstruct | STLを編集可能なparametric SCADへ再構築する |
| Analyze | 寸法、mesh、印刷上の確認可能な項目を解析する |
| Export | SCADからSTL、3MF、PNGを出力する |

### 既存SCADの修正

Refineでは単純な文字列置換ではなく、既存SCADを読んで次の関係を確認してから変更します。

```text
parameters
  ↓
derived dimensions
  ↓
modules
  ↓
body / additive features / subtractive features
  ↓
final assembly
```

例えば「ケースを5 mm高くする」という依頼でも、`height`だけでなくlid位置、post高さ、vent位置などが派生していないか確認し、必要最小限の修正を行います。依頼が単純な数値変更だけで済む場合に、無関係なrefactoringを勝手に行う設計にはしません。

### Skill内部の分割

OpenSCAD Skillはmodeごとの別Skillにはせず、一つのSkill内部を段階的に読み込む構成です。

```text
openscad/
├─ SKILL.md              # 入口、共通ルール、mode routing
├─ references/           # 選択modeに必要な手順だけ読む
├─ scripts/              # Windows対応Python CLIと実行処理
├─ templates/            # 再利用SCAD
└─ eval/                 # 受け入れシナリオ
```

単純なExportでSTL再構築やSDFの詳細を読ませず、必要になった資料だけを追加で読むことを狙います。

OpenSCADの設計詳細:

- [Skill構成と責務分割](design/openscad-skill-design.md)
- [Windows実行基盤](design/openscad-runtime-design.md)
- [受け入れ条件と実装計画](design/openscad-acceptance-plan.md)

## リポジトリの見方

| Path | 内容 |
| --- | --- |
| `skills/` | installable Skill本体 |
| `design/` | Skill architectureや各機能の保守者向け設計 |
| `tasks/` | 現在のtaskとphase |
| `reports/` | 実装、validation、review等の詳細記録 |
| `feedback-points/` | 再発防止やSkill改善のfeedback |
| `.github/workflows/` | repository validationと配布処理 |

現在の作業状況は[tasks/tasks-status.md](tasks/tasks-status.md)と[tasks/phases-status.md](tasks/phases-status.md)を参照してください。

## 設計の正本

- Skill全体の階層、依存、実行方式: [design/skill-hierarchy-design.md](design/skill-hierarchy-design.md)
- ChatGPT worker flow: [design/chat-worker-skill-design.md](design/chat-worker-skill-design.md)
- OpenSCAD Skill: [design/openscad-skill-design.md](design/openscad-skill-design.md)

Skillの追加、削除、利用可否、主要入口が変わる場合は、このREADMEとSkill hierarchy設計を同期して更新します。

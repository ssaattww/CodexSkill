# Sub-agent実行レポート

## タスク

`design/markdown-word-check-skill-design.md` の設計レビュー。

## sub-agentを使う理由

`review-enforcer` が review gate を sub-agent 必須としており、PR 作成前に設計の妥当性を独立確認するため。

## 対象範囲

- `design/markdown-word-check-skill-design.md`
- 必要に応じた既存 skill / 設計文書の参照

## 対象外

- 設計文書の修正
- skill 実体の作成
- 既存 skill の変更
- commit / PR 作成

## 実行コマンド

- `sed -n '1,240p' /home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md`
- `sed -n '1,240p' /home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md`
- `sed -n '1,240p' /home/ibis/AI/CodexSkill/reports/task-markdown-word-check-design-review-20260520230107.md`
- `nl -ba design/markdown-word-check-skill-design.md`
- `nl -ba design/review-enforcer-markdown-whitelist-rebuild-design.md`
- `nl -ba design/skill-hierarchy-design.md`
- `nl -ba skills/design-executor/SKILL.md`
- `nl -ba skills/handover-memo-writer/SKILL.md`
- `find skills/review-enforcer/scripts -maxdepth 1 -type f -printf '%P\n' | sort`
- `grep -RInE "lint:md|markdown-word|markdown-whitelist|prh|sub-agent|親が実行|design-executor|handover-memo-writer|review-enforcer" design skills/review-enforcer/SKILL.md skills/design-executor/SKILL.md skills/handover-memo-writer/SKILL.md`
- `nl -ba skills/review-enforcer/scripts/list-markdown-targets.js | sed -n '1,90p'`
- `nl -ba skills/review-enforcer/scripts/check-markdown-whitelist.js | sed -n '1,130p'`
- `nl -ba skills/review-enforcer/scripts/run-cspell-markdown.js | sed -n '1,100p'`
- `nl -ba skills/sub-agent-task-manager/SKILL.md | sed -n '24,60p'`
- `nl -ba skills/review-enforcer/SKILL.md | sed -n '34,90p'`
- `node -e "const p=require('./package.json'); console.log(Object.keys(p.scripts||{}).filter(k=>k.includes('lint')).map(k=>k+': '+p.scripts[k]).join('\n'))"`
- `find . -maxdepth 4 -name package.json -print`
- `git status --short`

## 対象ファイル

- 主対象:
  - `design/markdown-word-check-skill-design.md`
- 参照:
  - `design/review-enforcer-markdown-whitelist-rebuild-design.md`
  - `design/skill-hierarchy-design.md`
  - `skills/review-enforcer/SKILL.md`
  - `skills/sub-agent-task-manager/SKILL.md`
  - `skills/design-executor/SKILL.md`
  - `skills/handover-memo-writer/SKILL.md`
  - `skills/review-enforcer/scripts/list-markdown-targets.js`
  - `skills/review-enforcer/scripts/check-markdown-whitelist.js`
  - `skills/review-enforcer/scripts/run-cspell-markdown.js`

## 指摘事項

1. [中] 複数リポジトリ対応時の最低構成と fallback が設計上まだ曖昧です。
   - `design/markdown-word-check-skill-design.md:53-64` は `tools/lint/`、`package.json` などを「持てる」とし、必須は導入段階で変わるとしています。一方で required flow は `package.json` の `lint:md` と shared script explicit file mode を選ぶだけです（`design/markdown-word-check-skill-design.md:158-160`）。
   - 既存 shared script は初期実装で移動しない前提ですが、`skills/review-enforcer/scripts/list-markdown-targets.js:7-10` と `:88-90` は `process.cwd()` 配下の `tools/lint/markdown-targets.json` を必須にしています。`skills/review-enforcer/scripts/check-markdown-whitelist.js:8-17` は target repo の `package.json`、`yaml`、`tools/lint/markdown-whitelist.yaml`、`markdown-targets.json` を前提にしています。`skills/review-enforcer/scripts/run-cspell-markdown.js:9-16` と `:65-66` は target repo の `package.json`、`yaml`、`cspell.config.jsonc`、`node_modules/.bin/cspell` を前提にしています。
   - このままだと、IbisDuck 型の lint 構成が揃っている repo では動きますが、複数 repo で使える skill としては「どのファイルがない場合にどの検査を skip / unsupported / failed gate とするか」を実装者が推測する必要があります。IbisDuck 固有語を持ち込んではいませんが、IbisDuck 型の配線が暗黙前提として残るリスクがあります。

2. [中] `markdown-word-checker` が sub-agent へ lint 証跡収集を委譲する場合の report 契約が呼び出し関係に出ていません。
   - `design/markdown-word-check-skill-design.md:49` と `:113-118` は、大きい lint 証跡収集を `sub-agent-task-manager` 経由で sub-agent に委譲できる設計にしています。
   - しかし `sub-agent-task-manager` は sub-agent dispatch 前に `report-output-manager` で report path を決め、report file を事前作成し、commands/outcome/risks を report に残すことを必須にしています（`skills/sub-agent-task-manager/SKILL.md:39-50`）。
   - `markdown-word-checker` の required flow は結果を呼び出し元へ返すところで終わっており（`design/markdown-word-check-skill-design.md:151-168`）、call tree にも `report-output-manager` または既存 review report への添付方針がありません。実装時に sub-agent を使うと、report-backed delegation ルールと衝突するか、呼び出し元 report との二重管理が発生します。

3. [低] backtick 回避チェックが required flow の完了条件として明示されていません。
   - `markdown-word-checker` の役割には「回避的な backtick 使用」を確認するとあります（`design/markdown-word-check-skill-design.md:31-35`）。
   - ただし required flow は lint 実行と指摘分類が中心で、backtick / quote による lint evasion をどの段階で検査し、結果へ含めるかが明示されていません（`design/markdown-word-check-skill-design.md:151-168`）。
   - 現行 `review-enforcer` には lint evasion を reviewer が見るルールがあります（`skills/review-enforcer/SKILL.md:86-87`）。詳細 lint 手順を `review-enforcer` から外す方針（`design/markdown-word-check-skill-design.md:194-205`）なら、この検査が新 skill 側の required flow または output contract に残っている方が安全です。

## 結果

findings あり。

設計の大枠は妥当です。IbisDuck 固有用語を CodexSkill 側へ登録しない方針、repo 固有設定を対象 repo の `tools/lint/` から読む方針、作業者には lint 実行と指摘対応だけを求める方針、whitelist / prh 変更に利用者の exact entry レビューを残す方針は確認できました。

一方で、複数 repo 対応の実装可能性、sub-agent 委譲時の report 契約、backtick 回避チェックの required flow 化に未解決リスクがあります。設計文書の修正、skill 実体の作成、commit、PR 作成は行っていません。今回の明示制約により、`codex exec`、ネストした Codex、別 sub-agent 起動、`development-orchestrator` への再入場も行っていません。

## リスク

今回のレビューは、利用者指示により sub-agent を起動せず親 agent が実施しました。そのため、`review-enforcer` が通常要求する「reviewer は sub-agent」という gate 形式とは一致していません。

`rg` は環境に存在しなかったため、検索は `grep` で代替しました。

`/home/ibis/AI/CodexSkill` 直下に `package.json` は見つからず、`node -e "require('./package.json')"` は `MODULE_NOT_FOUND` で失敗しました。Markdown lint の実行コマンド自体は、この repo 側の npm wiring がないため確認できていません。

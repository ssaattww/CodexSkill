# Sub-agent実行レポート

## タスク

- 目的: `markdown-word-checker` を実際に使う想定で `design/markdown-word-check-skill-design.md` を検査し、リストの抜け漏れではなくフローの穴をレビューする。
- タスク種別: 設計フローレビュー

## sub-agentを使う理由

- 理由: 利用者からレビューを sub-agent に回し、実際に skill を使って設計書を検査するよう明示されたため。

## 対象範囲

- 対象: `design/markdown-word-check-skill-design.md`、`skills/markdown-word-checker/SKILL.md`、関連する呼び出し skill のフロー。

## 対象外

- 対象外: 単なるリスト項目の抜け漏れ指摘、shared script の移動、repo 固有 whitelist / prh 実データ変更、PR merge。

## 実行コマンド

- 実行コマンド:
  - `nl -ba skills/markdown-word-checker/SKILL.md | sed -n '1,260p'`
  - `nl -ba skills/review-enforcer/SKILL.md | sed -n '1,320p'`
  - `nl -ba skills/design-executor/SKILL.md | sed -n '1,260p'`
  - `nl -ba skills/handover-memo-writer/SKILL.md | sed -n '1,280p'`
  - `nl -ba design/markdown-word-check-skill-design.md | sed -n '1,360p'`
  - `nl -ba design/skill-hierarchy-design.md | sed -n '1,260p'`
  - `nl -ba skills/design/skill-hierarchy-design.md | sed -n '1,260p'`
  - `find tools/lint -maxdepth 2 -type f -print 2>/dev/null | sort`
  - `find skills/review-enforcer/scripts -maxdepth 1 -type f -print | sort`
  - `nl -ba skills/review-enforcer/scripts/list-markdown-targets.js | sed -n '1,260p'`
  - `nl -ba skills/review-enforcer/scripts/run-cspell-markdown.js | sed -n '1,320p'`
  - `nl -ba skills/review-enforcer/scripts/check-markdown-whitelist.js | sed -n '1,340p'`
  - `git diff --check -- design/markdown-word-check-skill-design.md skills/markdown-word-checker/SKILL.md skills/review-enforcer/SKILL.md skills/design-executor/SKILL.md skills/handover-memo-writer/SKILL.md reports/task-markdown-word-check-design-flow-review-20260522163846.md`

## 対象ファイル

- 変更または確認したファイル:
  - 確認: `design/markdown-word-check-skill-design.md`
  - 確認: `skills/markdown-word-checker/SKILL.md`
  - 確認: `skills/review-enforcer/SKILL.md`
  - 確認: `skills/design-executor/SKILL.md`
  - 確認: `skills/handover-memo-writer/SKILL.md`
  - 確認: `design/skill-hierarchy-design.md`
  - 確認: `skills/design/skill-hierarchy-design.md`
  - 確認: `skills/review-enforcer/scripts/list-markdown-targets.js`
  - 確認: `skills/review-enforcer/scripts/run-cspell-markdown.js`
  - 確認: `skills/review-enforcer/scripts/check-markdown-whitelist.js`
  - 変更: `reports/task-markdown-word-check-design-flow-review-20260522163846.md`

## 指摘事項

- 指摘要約または「指摘なし」:
  - High: focused lint と full lint の両方を検討または実行した場合の集約結果が定義されていない。`design/markdown-word-check-skill-design.md:159` は作成直後の focused lint と task 完了/review gate の full lint 検討を分けているが、`design/markdown-word-check-skill-design.md:216` 以降の output contract は command と exit status を単数の結果として返す。`skills/markdown-word-checker/SKILL.md:77` も focused または full のどちらかが run/skip/unsupported/failed gate になれば完了できる書き方で、片方の `failed gate` が片方の pass で上書きされない集約規則がない。実運用では design-executor の focused pass と review-enforcer の full failure が同じ caller report 上で混ざり、review gate の閉じ方が破綻し得る。
  - Medium: exact entry user review で停止した後の再開フローが不足している。`design/markdown-word-check-skill-design.md:199` と `skills/markdown-word-checker/SKILL.md:52` は exact entry を提示して利用者レビューで止めることを求めるが、承認後に誰が repo 固有設定を編集し、どの focused/full lint を再実行し、どの caller report の判定を更新するかが明示されていない。`skills/review-enforcer/SKILL.md:39` は exact entry レビュー済み確認を完了条件にするため、承認後の戻し先がないと gate が「レビュー済み」だけで閉じられるか、逆に再開不能になる。
  - Medium: `unsupported` を caller gate で受け入れてよい条件が caller ごとに固定されていない。`skills/markdown-word-checker/SKILL.md:97` は `unsupported` を pass/fail 扱いできない状態と定義する一方、`skills/review-enforcer/SKILL.md:77` は caller が許容すれば `unsupported` でも review-complete にできる書き方になっている。実際の `/home/ibis/AI/CodexSkill` には `package.json` と `tools/lint/` がなく、shared script も repo root の `package.json` や `tools/lint/markdown-targets.json` を読むため、今回の対象ファイルを渡すと lint 実行不能になりやすい。review gate で Markdown lint を必須にする場面と、導入前 repo としてリスク記録で閉じる場面の境界が曖昧。

## 結果

- 結果:
  - 指摘あり。設計本文や skill 本体は変更していない。
  - `git diff --check` は report 記入前と記入後の両方で成功した。

## リスク

- 未解決のリスクまたは後続対応:
  - 本レビューはフロー穴に限定した。単語リスト、分類項目、repo 固有 whitelist / prh 実データの網羅性は対象外。
  - 指摘を修正する場合は、`markdown-word-checker` の output contract に focused/full の個別結果と aggregate gate state を追加し、exact entry 承認後の owner/re-run/report update を明文化し、caller 別の `unsupported` 許容条件を固定する必要がある。

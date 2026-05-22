# Sub-agent実行レポート

## タスク

- 目的: Markdown 単語チェック skill 設計について、新たな単語が出たときに本文修正、whitelist、prh、alias のどれへ寄せるかの仕組みに不適合リスクがないか監査する。
- タスク種別: 設計監査

## sub-agentを使う理由

- 理由: 利用者から設計作業も sub-agent に依頼する方針が明示されたため。親はマネージャーとして、監査範囲と report を管理し、判断は report と設計文書を照合して行う。

## 対象範囲

- 対象: `design/markdown-word-check-skill-design.md`、`skills/review-enforcer/SKILL.md`、`skills/design-executor/SKILL.md`、`skills/handover-memo-writer/SKILL.md`、`design/skill-hierarchy-design.md`、`skills/design/skill-hierarchy-design.md`

## 対象外

- 対象外: 実装、設計文書の編集、PR #41 の merge、branch 作成、whitelist / prh の実データ変更。

## 実行コマンド

- 実行コマンド: `sed -n '1,220p' /home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md`
- 実行コマンド: `sed -n '1,220p' /home/ibis/AI/CodexSkill/skills/report-output-manager/SKILL.md`
- 実行コマンド: `sed -n '1,260p' /home/ibis/AI/CodexSkill/reports/task-markdown-word-check-term-routing-design-audit-20260521204755.md`
- 実行コマンド: `sed -n '1,260p' design/markdown-word-check-skill-design.md`
- 実行コマンド: `sed -n '261,520p' design/markdown-word-check-skill-design.md`
- 実行コマンド: `sed -n '1,240p' skills/review-enforcer/SKILL.md`
- 実行コマンド: `sed -n '1,240p' skills/design-executor/SKILL.md`
- 実行コマンド: `sed -n '1,240p' skills/handover-memo-writer/SKILL.md`
- 実行コマンド: `sed -n '1,260p' design/skill-hierarchy-design.md`
- 実行コマンド: `sed -n '1,260p' skills/design/skill-hierarchy-design.md`
- 実行コマンド: `grep -RIn "markdown-word-checker\\|Markdown lint\\|whitelist\\|prh\\|aliases" design/markdown-word-check-skill-design.md skills/review-enforcer/SKILL.md skills/design-executor/SKILL.md skills/handover-memo-writer/SKILL.md design/skill-hierarchy-design.md skills/design/skill-hierarchy-design.md`
- 実行コマンド: `nl -ba design/markdown-word-check-skill-design.md | sed -n '13,24p;64,94p;176,219p;238,258p;264,288p'`
- 実行コマンド: `nl -ba skills/review-enforcer/SKILL.md | sed -n '28,42p;74,88p'`
- 実行コマンド: `nl -ba skills/design-executor/SKILL.md | sed -n '1,90p'`
- 実行コマンド: `nl -ba skills/handover-memo-writer/SKILL.md | sed -n '1,105p'`
- 実行コマンド: `nl -ba design/skill-hierarchy-design.md | sed -n '34,58p;66,86p;214,238p;260,313p'`

## 対象ファイル

- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/skills/report-output-manager/SKILL.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/design/markdown-word-check-skill-design.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/skills/design-executor/SKILL.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/skills/handover-memo-writer/SKILL.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/design/skill-hierarchy-design.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/skills/design/skill-hierarchy-design.md` を確認。
- 変更または確認したファイル: `/home/ibis/AI/CodexSkill/reports/task-markdown-word-check-term-routing-design-audit-20260521204755.md` の placeholder のみ更新。

## 指摘事項

- 指摘要約または「指摘なし」: [Major] `design/markdown-word-check-skill-design.md:176-196` の required flow は「本文修正」「repo 固有設定見直し」「stricter gate」「skip / unsupported / failed gate」へ分類することを求めているが、新語を本文修正、`markdown-whitelist.yaml` の `term`、`aliases`、`prh.yml`、lint 設定見直し、`unsupported` / `failed gate` のどれへ寄せるかの決定表または決定手順が不足している。`term` / `aliases` / `prh` の定義は `design/markdown-word-check-skill-design.md:85-93` にあるが、分類時の優先順位、判断根拠、迷った場合の利用者確認境界が明示されていないため、利用者の質問「新たな単語が出てきた時にどちらへ寄せるかの仕組みで不適合が起きないか」には現設計だけでは十分に答えられない。
- 指摘要約または「指摘なし」: [Major] `review-enforcer` は現状、Markdown lint の細則と whitelist/prh 判断を直接持っている。`skills/review-enforcer/SKILL.md:77-87` は compound term、single generic word、`aliases`、`prh`、ChikkarPy、backtick 回避まで具体規則を持つ一方、設計側は変更後の `review-enforcer` を `markdown-word-checker` 呼び出しと gate 判断へ寄せる方針を `design/markdown-word-check-skill-design.md:238-245` で示している。`markdown-word-checker` 追加後にこの責務移管を実施しないと、同じ語彙規則が複数 skill に残り、片方だけ更新される不適合を誘発する。
- 指摘要約または「指摘なし」: [Major] `design-executor` と `handover-memo-writer` に `markdown-word-checker` 呼び出し契約がまだ入っていない。設計は Markdown 資料作成 skill が作成後に `markdown-word-checker` を呼ぶことを `design/markdown-word-check-skill-design.md:249-258` と完了条件 `design/markdown-word-check-skill-design.md:267` で求めているが、現行 `skills/design-executor/SKILL.md:35-41` と `skills/handover-memo-writer/SKILL.md:33-52` には Markdown lint / `markdown-word-checker` gate がない。これにより review 前まで語彙判定が遅れ、資料作成 skill の契約としては抜けがある。
- 指摘要約または「指摘なし」: [Minor] `design/skill-hierarchy-design.md` と `skills/design/skill-hierarchy-design.md` は `markdown-word-checker` を呼び出しツリー、役割一覧、契約一覧にまだ反映していない。設計自身は hierarchy design 更新を完了条件にしているが、現行ツリーでは `review-enforcer` が `sub-agent-task-manager` と `report-output-manager` だけを持ち、`markdown-word-checker` が表に存在しない。実装前の設計としては予定事項だが、追加後に同期漏れがあると呼び出し契約が読めなくなる。

## 結果

- 結果: 現設計は「細かい語彙規則を作業者へ知らせず、repo 固有設定と `markdown-word-checker` に閉じ込める」方針、および「whitelist / prh 変更は利用者 exact entry review 必須」という方針を両立できる構造を持っている。作業者は lint 指摘に従い、不適切な指摘を設定見直しとして報告するだけでよく、実際の `term` / `aliases` / `prh` entry 変更は利用者レビューで止めるため、方針同士は矛盾しない。
- 結果: ただし、利用者の質問に対する中核である新語分類の決定経路はまだ粗い。最小修正案は、`markdown-word-check-skill-design.md` の required flow 付近に「新語ルーティング決定表」を追加し、少なくとも次を明文化すること。既存語で表記だけ揺れており今後直したい場合は `prh.yml`、同じ概念として今後も許可する別表記だけは `aliases`、新しい概念として資料中で許可する必要がある場合は意味付き `term`、単独では意味が薄い英単語や UI token は本文を文脈付き複合語へ修正または複合 term 候補、lint 対象や repo 設定の欠落は `skip` / `unsupported` / `failed gate` の設定状態、判定不能または設定変更を伴う場合は exact entry を利用者レビュー、という順序にする。
- 結果: `review-enforcer` / `design-executor` / `handover-memo-writer` / hierarchy design には、`markdown-word-checker` 追加時に契約反映が必要である。特に `review-enforcer` から詳細な語彙規則を削り、結果証跡と gate owner に寄せる修正が必要。

## リスク

- 未解決のリスクまたは後続対応: 決定表なしで実装すると、未登録語を安易に単独 `term` へ追加する、`aliases` に意味違いを混ぜる、直すべき表記を許可別名として残す、本文修正で済む語を lint 設定へ逃がす、という不適合が起きうる。
- 未解決のリスクまたは後続対応: 作業者向けには細かい規則を出さない方針でよいが、`markdown-word-checker` の内部契約には細かい決定表が必要。ここを省くと「作業者に知らせない」が「どこにも判断基準がない」に変わる。
- 未解決のリスクまたは後続対応: 本監査ではファイル編集、実装、whitelist / prh 実データ変更、PR 操作は対象外とし、設計修正案の提示までに留めた。

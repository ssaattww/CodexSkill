# Sub-agent実行レポート

## タスク

Markdown 資料編集後の Codex hook による lint 自動実行方針を設計面から確認する。

## sub-agentを使う理由

利用者から設計も sub-agent に依頼する方針が示されており、親 agent はマネージャーとして判断と統合に限定するため。

## 対象範囲

- `markdown-word-checker` の設計と skill 契約
- Markdown 資料作成 skill からの呼び出し契約
- 「Markdown 編集後に lint を自動実行する」ために必要な Codex hook 境界
- Codex hook と既存 skill workflow の切り分け

## 対象外

- 実装変更
- repo 固有 whitelist / `prh` の変更
- CodexSkill repo への Markdown lint 設定導入
- shared script の移動

## 実行コマンド

- Serena `initial_instructions`
- Serena `activate_project` `/home/ibis/AI/CodexSkill`
- `grep -nE "markdown-word-checker|markdown-word-check-skill-design|edit-hook|PostToolUse|hook|Duck cwd" /home/ibis/.codex/memories/MEMORY.md`
- `sed -n '1,220p' /home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md`
- `sed -n '1,240p' /home/ibis/AI/CodexSkill/skills/design-doc-maintainer/SKILL.md`
- `sed -n '1,220p' /home/ibis/AI/CodexSkill/skills/markdown-word-checker/SKILL.md`
- `sed -n '1,260p' /home/ibis/AI/CodexSkill/design/markdown-word-check-skill-design.md`
- `sed -n '1,260p' /home/ibis/AI/CodexSkill/reports/task-markdown-word-check-handover-r2-20260527055108.md`
- `sed -n '1,260p' /home/ibis/AI/CodexSkill/reports/task-markdown-word-check-edit-hook-design-audit-20260530091410.md`
- `sed -n '1,240p' /home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md`
- `sed -n '1,220p' /home/ibis/AI/CodexSkill/skills/design-executor/SKILL.md`
- `sed -n '1,220p' /home/ibis/AI/CodexSkill/skills/handover-memo-writer/SKILL.md`
- `sed -n '1,240p' /home/ibis/AI/CodexSkill/AGENTS.md`
- `git -C /home/ibis/AI/CodexSkill status --short --branch`
- `grep -RInE "PostToolUse|PreToolUse|Stop|hook|hooks|markdown-document-writer|markdown-word-checker" /home/ibis/AI/CodexSkill/design /home/ibis/AI/CodexSkill/skills /home/ibis/AI/CodexSkill/reports/task-markdown-word-check-edit-hook-design-audit-20260530091410.md 2>/dev/null`
- `find /home/ibis/AI/CodexSkill -maxdepth 3 -type f \( -name 'AGENTS.md' -o -name 'package.json' -o -path '*/tools/lint/*' \) -print`
- `git -C /home/ibis/AI/CodexSkill diff -- /home/ibis/AI/CodexSkill/design/markdown-word-check-skill-design.md /home/ibis/AI/CodexSkill/skills/markdown-word-checker/SKILL.md /home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md /home/ibis/AI/CodexSkill/skills/design-executor/SKILL.md /home/ibis/AI/CodexSkill/skills/handover-memo-writer/SKILL.md`
- `git -C /home/ibis/AI/CodexSkill log --oneline --decorate -5`
- `nl -ba /home/ibis/AI/CodexSkill/design/markdown-word-check-skill-design.md | sed -n '120,180p'`
- `nl -ba /home/ibis/AI/CodexSkill/design/markdown-word-check-skill-design.md | sed -n '217,250p'`
- `nl -ba /home/ibis/AI/CodexSkill/skills/markdown-word-checker/SKILL.md | sed -n '24,80p'`
- `nl -ba /home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md | sed -n '34,88p'`
- `apply_patch` による本 report の `未記入` 欄更新
- `git -C /home/ibis/AI/CodexSkill diff --check`

## 対象ファイル

- `/home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md`
- `/home/ibis/AI/CodexSkill/skills/design-doc-maintainer/SKILL.md`
- `/home/ibis/AI/CodexSkill/skills/markdown-word-checker/SKILL.md`
- `/home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md`
- `/home/ibis/AI/CodexSkill/skills/design-executor/SKILL.md`
- `/home/ibis/AI/CodexSkill/skills/handover-memo-writer/SKILL.md`
- `/home/ibis/AI/CodexSkill/design/markdown-word-check-skill-design.md`
- `/home/ibis/AI/CodexSkill/design/skill-hierarchy-design.md`
- `/home/ibis/AI/CodexSkill/skills/design/skill-hierarchy-design.md`
- `/home/ibis/AI/CodexSkill/reports/task-markdown-word-check-handover-r2-20260527055108.md`
- `/home/ibis/AI/CodexSkill/reports/task-markdown-word-check-edit-hook-design-audit-20260530091410.md`
- `/home/ibis/AI/CodexSkill/AGENTS.md`
- `/home/ibis/.codex/memories/MEMORY.md`

## 指摘事項

- Major: Codex hook を既存の `markdown-word-checker` 呼び出し契約の代替として扱うと、Bash/MCP 経由の Markdown 編集が漏れたときに gate が閉じたように見える。既存設計は資料作成 skill が明示 Markdown file list を渡し、review-enforcer が完了前 gate として結果を要求する構造なので、hook は「編集直後の早期 feedback」として追加し、authoring skill / review-enforcer の gate を置き換えないことを設計に明記する必要がある。
- Major: PostToolUse hook で apply_patch / Edit / Write 後の Markdown file list をどう確定するかが設計にない。`markdown-word-checker` は explicit file focused lint を前提にしているため、hook 側は tool input / tool result から対象 repo 内の作成・変更済み `.md` を抽出し、存在しない削除済み file と非 Markdown を除外し、重複排除した list を focused lint へ渡す契約を持つ必要がある。抽出不能時は pass 扱いにせず、`unsupported` または hook 捕捉不能 risk として model feedback / report に残す必要がある。
- Major: hook の `decision:block` は副作用を undo できないため、「編集を防ぐ gate」として設計してはいけない。lint 失敗、`needs user review`、必須 check の `unsupported` では、元 tool result を hook feedback に置き換えて model に修正継続させる feedback gate として扱い、最終完了可否は `markdown-word-checker` の aggregate gate state と review-enforcer の disposition で判断する必要がある。
- Minor: PreToolUse は Markdown 編集後 lint には早すぎ、初期範囲には不要。Stop hook は Bash/MCP 漏れの保険になり得るが、既存 review-enforcer の完了前 gate と重複しやすい。PR #41 への反映は PostToolUse 中心に絞り、Stop hook は将来の hardening 候補として risk に残すのが妥当である。
- Minor: hook 結果の report 反映先を分ける必要がある。hook は即時 model context へ focused lint の結果を返すが、恒久証跡は既存 caller report または review report に集約する。hook 自体が sub-agent report を新規作成する設計にすると、sub-agent-task-manager / report-output-manager の report 所有境界と衝突しやすい。

## 結果

- PR #41 の既存設計へは、`markdown-word-checker` の下位実装詳細ではなく「Codex PostToolUse hook による早期 lint feedback」節として反映するのが適切である。
- hook の中心 event は PostToolUse とし、初期 matcher は apply_patch / Edit / Write 系に限定する。PreToolUse は対象外、Stop hook は初期実装範囲外の将来候補とする。
- hook は Codex hook であり、Git hook / editor hook ではないことを明記する。
- hook は apply_patch / Edit / Write 後に対象 repo 内の変更済み Markdown file list を抽出し、`markdown-word-checker` の focused lint 入力と同じ形へ渡す。
- Bash / MCP / shell / unified_exec 経由の編集は捕捉不完全として、hook の成功だけでは gate 完了としない。既存の資料作成 skill からの明示呼び出しと review-enforcer の完了前 gate を必須の最終 safety net として維持する。
- lint 結果は、`pass` / `skip` / `unsupported` / `failed gate` / `needs user review` の既存分類を再利用する。`failed gate` と `needs user review` は hook feedback で model に修正または停止理由を返し、必須 check の `unsupported` も pass 扱いにしない。
- 推奨する実装範囲は 1 つに絞る: PostToolUse hook で apply_patch / Edit / Write による `.md` 変更を検出し、抽出した explicit Markdown file list に対して focused lint を自動実行し、その結果を hook feedback と既存 caller/review report に接続する最小範囲。

## リスク

- shell / unified_exec / MCP tool calls 経由の Markdown 編集は hook 捕捉が不完全なため、hook だけに依存すると漏れが残る。
- PostToolUse hook は副作用を undo できないため、失敗時は編集済み状態から model に修正継続させる運用になる。
- apply_patch の path 抽出では rename、delete、生成物、repo 外 path、複数 repo 混在の扱いを誤る可能性がある。初期実装では存在する `.md` の作成・変更に限定し、曖昧な場合は `unsupported` として扱うのが安全である。
- CodexSkill repo には現時点で `package.json` と `tools/lint/` がなく、この repo 自体に focused Markdown lint を実行すると `unsupported` になる。hook 設計は対象 repo ごとの lint 設定有無を既存分類で扱う必要がある。
- Stop hook を同時に導入すると、PostToolUse と review-enforcer の結果が重複し、どの gate が完了判定を所有するか曖昧になる可能性がある。

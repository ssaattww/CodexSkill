# Feedback Points Backlog

Canonical archive and backlog for feedback-point records.

Location rule:

- real repository root: `feedback-points/feedback-points-backlog.md`
- keep completed, archived, or non-active entries here

Update rule:

- このファイルは `feedback-points-manager` または `feedback-points-sanitizer` を通してのみ更新する
- それ以外の経路で直接追記・修正しない

| FP | 記録起点 | 内容 | カテゴリ | 重複グループ | 指摘回数 | skill化状態 | 関連skill | 状態 | 記録日 | 直近指摘日 | 最終更新日 | 次アクション対応 | 根拠リンク |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FP-001 | `親判断` | 大きめの一括差分は崩れやすいため、手動編集は数本ずつの小さな差分に分けて確実に適用する。ユーザーが明示的に `FP` と言わなくても、こうした reusable な実行上の気づきは記録する。issue 化後は active FP ではなく issue を正本として追跡する。 | `cost-control` | `split_large_manual_patches_and_record_execution_lessons` | 1 | `skill化済み` | `feedback-points-manager`, `development-orchestrator` | `対応済み` | `2026-04-18` | `2026-04-18` | `2026-04-21` | `issue #5 を正本として追跡` | `https://github.com/ssaattww/CodexSkill/issues/5`, `skills/feedback-points-manager/SKILL.md`, `skills/development-orchestrator/SKILL.md` |
| FP-002 | `親判断` | `1対多` の skill ツリーでは、親が持つ判断責務や数値閾値を child skill に重複して持たせすぎない。child 側は owner と参照先を明示するに留め、親未決定でも破綻しない最小限だけを書く。現状の switchable 実装系には、まだこの観点で点検余地が残っている。issue 化後は active FP ではなく issue を正本として追跡する。 | `governance` | `avoid_duplicate_decision_ownership_in_one_to_many_skill_trees` | 1 | `skill化済み` | `skill-authoring-wrapper`, `codex-delegation-executor`, `implementation-executor`, `design-executor`, `tdd-executor` | `対応中` | `2026-04-18` | `2026-04-18` | `2026-04-21` | `issue #4 の残作業を正本として追跡` | `https://github.com/ssaattww/CodexSkill/issues/4`, `skills/skill-authoring-wrapper/references/responsibility-placement-policy.md`, `skills/codex-delegation-executor/SKILL.md`, `skills/implementation-executor/SKILL.md`, `skills/design-executor/SKILL.md`, `skills/tdd-executor/SKILL.md` |
| FP-003 | `親判断` | 運用用語や出力項目名は、英語をそのまま残す前に自然な日本語表現を先に検討する。特に workflow や feedback の説明では、`next owner` のような曖昧な英語より `次アクション対応` のように役割が分かる日本語を優先する。issue 化後は active FP ではなく issue を正本として追跡する。 | `communication` | `prefer_clear_japanese_operational_terms` | 1 | `skill化済み` | `feedback-points-manager` | `対応済み` | `2026-04-18` | `2026-04-18` | `2026-04-21` | `issue #6 を正本として追跡` | `https://github.com/ssaattww/CodexSkill/issues/6`, `skills/feedback-points-manager/SKILL.md`, `skills/design/skill-hierarchy-design.md` |
| FP-004 | `ユーザー指示` | mandatory な `sub-agent` 手順を current run で満たせない場合、親判断で代替して進めず、必ずユーザー確認で止まる。特に `review-enforcer` の mandatory `sub-agent` review は親レビューで黙って代替してはならない。issue 化後は active FP ではなく issue を正本として追跡する。 | `governance` | `stop_and_ask_when_mandatory_sub_agent_execution_is_blocked` | 2 | `skill化済み` | `feedback-autonomy-boundary-manager`, `review-enforcer` | `対応済み` | `2026-04-21` | `2026-04-21` | `2026-04-21` | `issue #9 を正本として追跡` | `https://github.com/ssaattww/CodexSkill/issues/9`, `skills/feedback-autonomy-boundary-manager/SKILL.md`, `skills/review-enforcer/SKILL.md`, `reports/issue3-skill-presence-guard-20260421092352.md`, `reports/issue3-review-20260421092352.md` |
| FP-005 | `ユーザー指示` | ユーザーが `〜べきです` と述べた場合は 100% 指摘として扱い、指示待ちにせず即時 `feedback-points-manager` の記録対象にする。issue 化後は active FP ではなく issue を正本として追跡する。 | `governance` | `treat_user_should_statements_as_immediate_feedback_points` | 1 | `skill化済み` | `feedback-points-manager` | `対応済み` | `2026-04-21` | `2026-04-21` | `2026-04-21` | `issue #11 を正本として追跡` | `https://github.com/ssaattww/CodexSkill/issues/11`, `skills/feedback-points-manager/SKILL.md`, `skills/feedback-points-manager/references/feedback-format-and-cleanup.md`, `reports/fp-format-and-review-trigger-hardening-20260421094402.md` |

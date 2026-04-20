# Feedback Points Backlog

Canonical archive and backlog for feedback-point records.

Location rule:

- real repository root: `feedback-points/feedback-points-backlog.md`
- keep completed, archived, or non-active entries here

Update rule:

- このファイルは `feedback-points-manager` または `feedback-points-sanitizer` を通してのみ更新する
- それ以外の経路で直接追記・修正しない

| FP | 内容 | カテゴリ | 重複グループ | skill化状態 | 関連skill | 状態 | 記録日 | 最終更新日 | 根拠リンク |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FP-002 | `1対多` の skill ツリーでは、親が持つ判断責務や数値閾値を child skill に重複して持たせすぎない。child 側は owner と参照先を明示するに留め、親未決定でも破綻しない最小限だけを書く。現状の switchable 実装系には、まだこの観点で点検余地が残っている。issue 化後は active FP ではなく issue を正本として追跡する。 | `governance` | `avoid_duplicate_decision_ownership_in_one_to_many_skill_trees` | `skill化済み` | `skill-authoring-wrapper`, `codex-delegation-executor`, `implementation-executor`, `design-executor`, `tdd-executor` | `対応中` | `2026-04-18` | `2026-04-21` | `https://github.com/ssaattww/CodexSkill/issues/4`, `skills/skill-authoring-wrapper/references/responsibility-placement-policy.md`, `skills/codex-delegation-executor/SKILL.md`, `skills/implementation-executor/SKILL.md`, `skills/design-executor/SKILL.md`, `skills/tdd-executor/SKILL.md` |

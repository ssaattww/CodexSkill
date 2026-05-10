# Feedback Points

Canonical active feedback-point ledger for the SKILL repository.

Location rule:

- canonical path: `/home/ibis/AI/CodexSkill/feedback-points/feedback-points.md`
- do not keep the active ledger in a consuming project repository

Update rule:

- このファイルは `feedback-points-manager` または `feedback-points-sanitizer` を通してのみ更新する
- それ以外の経路で直接追記・修正しない

| FP | 記録起点 | 内容 | カテゴリ | 重複グループ | 指摘回数 | skill化状態 | 関連skill | 状態 | 記録日 | 直近指摘日 | 最終更新日 | 次アクション対応 | 根拠リンク |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FP-20260511-001 | ユーザー明示指示 | IbisDuck では調査・コーディング作業を SubAgent に任せ、親 Codex はマネージャーとしてのみ動く。親は方針決定、追跡、委譲、report 確認、レビュー統合、git 操作の管理を担い、調査・実装・テストコード作成は worker sub-agent に委譲する。sub-agent は `gpt-5.5 high` で統一する。コメント、テスト説明コメント、設計書は日本語にする。 | delegation-policy | manager-only-coding-delegation | 4 | skill更新候補 | development-orchestrator, codex-delegation-executor, sub-agent-task-manager, implementation-executor | active | 2026-05-11 | 2026-05-11 | 2026-05-11 | このチャットでは即時運用に反映する。恒久化は development-orchestrator / delegation 系 skill へ「IbisDuck では調査・coding worker 委譲を標準にする」「sub-agent は gpt-5.5 high に統一する」「コメントと設計書は日本語にする」ルール追加を検討する。issue 化は未実施。 | ユーザー発言: 「今後ここでは、コーディング作業もSubAgentに任せることにします。あなたはマネージャーとしてのみ動くこととします。」「設計書も日本語ね当たり前だけど」「調査も基本はサブエージェントに任せてくださいあなたは、レポートをみて判断してください。」「sub-agentはすべてgpt5.5 highで統一ね。」 |

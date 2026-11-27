# Sub-agent実行レポート

## タスク

- 目的:
- タスク種別:

## sub-agentを使う理由

- 理由:

## 対象範囲

- 対象:

## 対象外

- 対象外:

## Dispatch profile

<!-- This section is parent-owned. The child must not infer or rewrite hidden runtime state or authorization evidence. -->

- selection inputs (parent, pre-dispatch):
- selection source (parent, pre-dispatch):
- observed decomposability (parent, pre-dispatch):
- decomposition policy / disposition (parent, pre-dispatch):
- proposed profile (parent, pre-dispatch if applicable):
- approval status / evidence (parent):
- Astra eligibility / prior-attempt and blocker evidence / expected benefit (parent, if applicable):
- Astra cost notice / baseline / evidence date / unknown actual cost (parent, if applicable):
- Astra grant ID / mode / status / explicit approval evidence (parent, if applicable):
- Astra task / scope / completion conditions / parent context / agent binding (parent, if applicable):
- Astra per-operation ID / work unit / target HEAD / grant usage and pre-submission consumption / outcome (parent, if applicable):
- Astra revocation / expiry / invalidation reason and preserved grant history (parent, if applicable):
- complete `astra_authorization` schema version 1 extension (parent; not applicable for ordinary non-Astra work):
- requested profile (parent, pre-dispatch):
- agent role / default-role plan (parent, pre-dispatch):
- role config evidence / profile effect (parent, pre-dispatch):
- complete [dispatch observability evidence](../../sub-agent-task-manager/references/agent-profile-selection.md#dispatch-profile-schema), including checked schema, role inspection, and call acceptance (parent):
- planned runtime profile after known role constraints (parent, pre-dispatch):
- applied profile (parent, post-runtime exact evidence only; null when unverified):
- application status (parent, post-runtime evidence only):
- runtime profile observability (parent, post-runtime):
- reviewer continuity (parent, if applicable):
- fork policy (parent):
- reasons / constraints (parent):

Preserve this extension in both ordinary reports and deferred-attestation handoffs without materializing the deferred report early. When reusing a reviewer or a legacy record, retain its original evidence and mark unavailable observations as unknown; do not backfill unsupported claims.

## 実行コマンド

- 実行コマンド:

## 対象ファイル

- 変更または確認したファイル:

## 指摘事項

- 指摘要約または「指摘なし」:

## 結果

- 結果:

## リスク

- 未解決のリスクまたは後続対応:

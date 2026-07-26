# コードレビュー報告書

## Review metadata

- Review ID: `{{review_id}}`
- Stage: `{{stage}}`
- Risk profile: `{{risk_profile}}`
- Selected modules: `{{selected_modules}}`
- Target: `{{target}}`
- Base: `{{base}}`
- HEAD SHA: `{{head_sha}}`
- Reviewer context: `{{reviewer_context}}`

## Coverage

Criterionの詳細は`review-policy/references/code-review-criteria.md`を正本とする。

rendererは`ReviewResult.coverage`から、selected criterionだけを次の表へ展開する。

| Criterion ID | 表示名 | Disposition | Evidence | Notes | Remaining risk |
| --- | --- | --- | --- | --- | --- |
| `{{criterion_id}}` | `{{criterion_label}}` | `{{disposition}}` | `{{evidence_refs}}` | `{{notes}}` | `{{remaining_risk}}` |

## Inspected targets

{{inspected_targets}}

## Findings

findingsをseverity順に展開する。findingがない場合は`指摘なし`と明記する。

### {{severity}} — {{finding_id}}

- Origin: `{{origin}}`
- Summary: {{summary}}
- Location: {{locations}}
- Evidence: {{evidence_refs}}
- Required change: {{required_change}}
- Related criteria: {{related_criterion_ids}}

## Held concerns

{{held_concerns}}

## Unexplored areas

{{unexplored}}

## Validation evidence

{{validation_evidence}}

## Final result

- Verdict: `{{verdict}}`
- Follow-up: `{{follow_up}}`
- Stop reason: `{{stop_reason}}`
- Merge candidate: `{{merge_candidate}}`

## Renderer notes

- このtemplateはcriterion詳細を保持しない。
- rendererはstructured fieldを忠実に表示し、verdictやseverityを再判定しない。
- repository path、filename、commit、PR投稿はartifact adapterの責務とする。
- mergeは実行しない。

# Skillization Policy

Open this only when deciding duplicate grouping, recurrence handling, or whether a point should become a skill.

## Duplicate grouping

When a new point appears:

1. detect whether equivalent intent already exists
2. append the FP to the same duplicate group
3. avoid isolated near-duplicate rows
4. keep traceability to all source FP IDs

Group by intent, not literal wording.

## Default skillization threshold

- first occurrence: record only
- second occurrence: set to `検討中`
- third occurrence or more: skillize by default unless clearly one-off

Early skillization is allowed when all are true:

- cross-repository applicability is obvious
- recurrence cost is high
- omission risk is high if not automated by skill

Do not skillize:

- issue-specific design content
- one-time feature decisions
- externally constrained rules that are not reusable as workflow

## Actions after skillization

When a point is skillized:

1. set `skill化状態` to `skill化済み`
2. set `関連skill`
3. preserve links to source FP IDs
4. rewrite wording from incident-specific to reusable rule

If an existing skill is close, prefer extending it over creating a near-duplicate skill.

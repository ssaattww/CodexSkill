# Report Filename Policy

Open this only when you need filename structure, prefix selection, or placement rules.

## Placement

Always place report files in:

- `<repo-root>/reports/`

Do not place new report files inside `skills/`, `task/`, or nested feature folders unless the user explicitly asks for an exception.

## Filename format

Use this format for new report files:

- `<issue-prefix>-<item-name>-<yyyymmddhhmmss>.md`

If the same logical report needs another revision, use:

- `<issue-prefix>-<item-name>-r<revision>-<yyyymmddhhmmss>.md`

Revision rules:

- first report uses no revision suffix
- second revision uses `r2`
- third revision uses `r3`
- keep the same prefix and item name across revisions
- increment the revision number only when the later file supersedes the earlier report for the same logical review/evidence thread
- if the helper script does not yet support revision output, choose the revisioned filename manually instead of overloading `item-name`

Examples:

- `issue-128-review-summary-20260418153022.md`
- `issue-128-test-evidence-20260418154409.md`
- `task-phase-2-intake-note-20260418160140.md`
- `task-tracker-006-review-r2-20260509150434.md`
- `topic-skill-review-policy-review-r3-20260509185626.md`

## Prefix selection

Choose exactly one canonical prefix source:

1. GitHub issue number:
   - `issue-<number>`
2. Stable task identifier when no issue number exists:
   - `task-<normalized-task-id>`
3. Stable topic key only when neither issue nor task identifier exists:
   - `topic-<normalized-topic>`

Normalization rules:

- lowercase only
- use letters, digits, and hyphens only
- collapse spaces, underscores, and punctuation to a single hyphen

## Consistency rules

- If a report already exists for the same issue/task/topic, reuse the same prefix family.
- If a report revision already exists for the same logical thread, reuse the same prefix family and item name, and only increment the `r<revision>` segment.
- When an issue number exists, do not invent a natural-language prefix. Use `issue-<number>`.
- Keep `item-name` short and descriptive:
  - `review-summary`
  - `test-evidence`
  - `intake-note`
  - `skill-gap-analysis`

## Timestamp

Use `yyyymmddhhmmss` in local execution time.

Do not omit the time portion for new reports.

## Legacy compatibility

Older reports may use date-only names or other formats.

- leave them as-is unless the user asks for renaming
- apply this policy only to new report files and deliberate rewrites

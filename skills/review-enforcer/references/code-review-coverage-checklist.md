# Code Review Coverage Checklist

Use this checklist for implementation review and re-review. It defines the minimum
review surface; repository-specific design and task criteria may add stricter rules.
Do not replace direct code inspection with a checklist-only confirmation.

For every section, record one of these states in the review report coverage matrix:

- `checked - no finding`
- `checked - finding`
- `held`
- `not applicable` with a reason
- `unexplored` with the concrete blocker or remaining work

A review cannot be reported as complete while a required section is silently
unexplored.

## Review Basis

- Read the task exit criteria, issue or request, authoritative design, and relevant
  repository instructions.
- Identify the intended normal path, explicit non-goals, and ownership boundaries.
- Confirm that the implementation and tests address the current requirement rather
  than an outdated report or earlier design revision.
- Record task-specific criteria established by prior audits, design decisions, or
  user instructions.

## Change and Dependency Scope

- Inspect every changed file, including tests, generated configuration, reports,
  task tracking, and design documents.
- Inspect direct callers, consumers, serializers, validators, persistence adapters,
  and UI or API surfaces that depend on changed contracts.
- Check whether new files duplicate an existing contract, parser, validator, helper,
  or policy.
- Check behavior when the change is combined with current default-branch code and
  adjacent in-flight work.
- Confirm that unrelated files and work owned by another task or pull request were
  not modified.
- Record any dependency defect that affects the change but belongs outside the
  current scope as an explicit held finding.

## Contract and Specification

- Compare behavior with task exit criteria and authoritative design.
- Reuse existing domain contracts when they preserve required identity and data;
  reject simplified parallel models that lose status, paths, revisions, or metadata.
- Validate public API inputs and outputs, including coordinate bases, nullability,
  zero-value semantics, ordering, error behavior, and unsupported values.
- Check that runtime validation matches the static type contract at external,
  persistence, cache, parser, and deserialization boundaries.
- Check that downstream tasks and consumers receive all required information.

## State, Identity, and Persistence

- Verify identity consistency across map keys, payload IDs, paths, revisions,
  contexts, repositories, base and head revisions, and persisted keys.
- Reject stale state or cached data that can be paired with a newer context.
- Validate line counts, interval bounds, canonical ordering, uniqueness, and required
  metadata before use and before persistence.
- Verify owner, source, or context precedence when multiple states can contribute.
- Check creation, deletion, recreation, rename-back, promotion, and migration cases.
- Preserve owner-wide or repository-wide state when a new child context is created.
- Apply the same validator to existing state, generated state, and final output.
- Verify persistence round trips and backward-compatible optional metadata.

## Boundary and Malformed Input

- Add or inspect cases for empty, zero, minimum, maximum, missing, duplicate,
  contradictory, partial, stale, unknown, and unsupported input.
- Reject malformed input atomically; do not silently skip required fields or return
  a partial result that appears complete.
- Check paired metadata for one-sided absence and duplicate occurrence.
- Check status or mode matrices against path, side, count, and metadata invariants.
- Check canonicalization before uniqueness and collision validation.
- Ensure policy decisions such as exclusion do not bypass structural validation.
- For parsed formats, verify header and body counts, ordering, cursor movement,
  anchors, gaps, and complete-input requirements.
- Distinguish expected absence from unknown operational failure instead of collapsing
  broad error codes into one benign result.

## Atomicity and Failure Behavior

- Identify the transaction boundary and count actual writes or commits.
- Verify that one logical operation does not persist ranges, metadata, baselines, or
  sources in separate partially successful steps unless the design explicitly
  allows it.
- Test failed compare-and-swap, write, parse, validation, and external-command paths.
- Confirm that retries or repeated reads use one coherent source observation when
  the operation requires snapshot consistency.
- Ensure failure leaves recoverable state and actionable diagnostics.

## Test Quality and Regression Retention

- Verify tests were added before the implementation fix when TDD is required.
- Confirm fixtures represent inputs the real protocol, parser, API, or tool can
  actually produce.
- Test normal, partial, excluded, malformed, stale, and cross-revision behavior at
  file-level and aggregate-level outputs.
- Assert exact results, not only that a call succeeds or throws.
- Confirm tests are connected to the normal test command and CI workflow.
- Preserve earlier review regressions when adding new cases; do not replace the
  suite with only the latest finding.
- Compare implementation reports and PR claims with the current test suite.
- Treat CI success as insufficient when the reviewed failure condition lacks a
  regression test.

## Performance and Side Effects

- Check repeated filesystem, network, Git, process, parser, and persistence work.
- Estimate operation count on the normal path and remote or large-input paths.
- Check algorithmic complexity for nested scans, repeated normalization, and
  expansion proportional to untrusted numeric ranges.
- Prefer changed-item or interval-based work over expanding large ranges item by
  item.
- Verify caching and deduplication do not weaken freshness or identity checks.
- Check synchronous work that can block an extension host, UI thread, request
  handler, or other latency-sensitive runtime.

## Documentation and Design Consistency

- Ensure public APIs, DTOs, schemas, and important runtime boundaries document their
  contracts, coordinate systems, failure behavior, and invariants.
- Compare design documents with actual file layout, implementation behavior, and
  persistence format.
- Organize authoritative design by feature rather than by issue, task, or review
  round unless the repository explicitly requires otherwise.
- Consolidate overlapping design documents when multiple files claim authority for
  one feature.
- Keep implementation reports and PR descriptions synchronized with the current
  code, tests, Red and Green commits, final HEAD, and CI run.
- Apply the separate source-shape and Markdown policies when those scopes are
  present.

## CI and Evidence

- Confirm the workflow run belongs to the reviewed branch HEAD SHA; do not rely on
  the repository's latest run.
- Verify all required jobs, including build, lint, unit, integration, packaging, and
  host tests that apply to the repository.
- When a run fails, inspect preserved stdout, stderr, environment, source, tests,
  configuration, generated output, and test result artifacts.
- Record the exact HEAD SHA, run ID, conclusion, and relevant artifact IDs.
- Re-run validation after every fix that changes code, tests, configuration, or
  documentation gates.
- Do not infer a pass from an older commit or another branch.

## Re-review Expansion

- First verify each previous finding against the new implementation and tests.
- Then inspect code paths, files, dependencies, and invariants that were not the
  direct target of the last fix.
- Search for sibling cases of the same defect pattern rather than checking only the
  reported example.
- Recheck earlier regression tests to confirm they were not removed or weakened.
- Re-evaluate performance, documentation, result contracts, and failure behavior
  after refactoring done to address findings.
- Record newly checked areas and remaining unexplored areas in the coverage matrix.
- Do not declare re-review complete merely because all prior comments have replies
  or are marked resolved.

## Minimum Review Report Evidence

The report must include:

- the coverage matrix for every section in this checklist
- changed files and dependent files inspected
- tests and commands examined or run
- findings with severity and file or line references when available
- held and out-of-scope findings with ownership rationale
- unexplored areas and the reason they remain unexplored
- branch HEAD SHA and the exact CI run used for the verdict
- explicit confirmation that re-review expanded beyond the previous fixes

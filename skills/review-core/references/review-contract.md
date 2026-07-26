# Review Contract

この文書は、review実行と表示・repository artifact生成の間で使用する、表示形式非依存の正本contractである。

Markdown、chat response、PR comment、report path、repository filesystemをこのcontractへ含めない。

## Contract version

- `contract_version`: `1`

未知のversionは推測で処理せず、`incomplete`としてcallerへ返す。

## ReviewRequest

```text
ReviewRequest
  contract_version
  review_id
  stage
  target
  requirements
  scope
  risk_profile
  selected_modules
  planned_criteria
  previous_findings
  validation_evidence
  reviewer_context
```

### 必須field

- `contract_version`: `1`
- `review_id`: review cycle内で一意な文字列
- `stage`: `initial | fix_verification | cold_final`
- `target`
  - `repository`: 任意。repositoryがないchat reviewでは省略可能
  - `item`: PR、branch、commit、diff、task等の識別子
  - `base`: 任意
  - `head_sha`: 判明している場合はimmutable SHA
- `requirements`: authoritative requirement、design、repository instructionの参照
- `scope`
  - `changed_targets`: 変更file、diff、document等
  - `dependency_boundaries`: caller、consumer、validator、persistence、UI等
  - `non_goals`: review対象外
- `risk_profile`: `low | medium | high`
- `selected_modules`: `review-policy`が選んだrisk module ID
- `planned_criteria`: universal criterionとselected module criterionのstable ID
- `previous_findings`: `fix_verification`と`cold_final`で必要な既存finding
- `validation_evidence`: test、command、CI、artifact等の利用可能な証跡
- `reviewer_context`: `same_reviewer | fresh_no_history | direct`

## ReviewResult

```text
ReviewResult
  contract_version
  review_id
  stage
  risk_profile
  selected_modules
  inspected_targets
  coverage
  findings
  held_concerns
  unexplored
  validation_evidence
  verdict
  follow_up
  stop_reason
  merge_candidate
```

### 必須field

- `contract_version`: requestと同じversion
- `review_id`: requestと一致
- `stage`: requestと一致
- `risk_profile`: requestと一致
- `selected_modules`: requestと一致
- `inspected_targets`: 実際に確認したfile、dependency、contract、evidence
- `coverage`: planned criterionごとのdisposition
- `findings`: severity順のfinding
- `held_concerns`: 現在scopeでは対応しないconcern
- `unexplored`: 確認できなかった領域、理由、残存risk
- `validation_evidence`: 実際に確認したtest、command、CI、artifact
- `verdict`: 固定値
- `follow_up`: 固定値
- `stop_reason`: reviewを終了または停止した理由
- `merge_candidate`: policy上merge可能候補かを示すboolean。merge自体は実行しない

## Fixed values

### Stage

- `initial`
- `fix_verification`
- `cold_final`

### Verdict

- `pass`
- `pass_with_held`
- `fail`
- `incomplete`
- `unstable`

### Coverage disposition

- `checked_no_finding`
- `checked_finding`
- `held`
- `not_applicable`
- `unexplored`

### Follow-up

- `none`
- `fix_required`
- `design_rework`
- `split_required`
- `external_owner`

### Finding severity

- `blocking`
- `high`
- `medium`
- `low`

### Finding origin

- `pre_existing`
- `introduced_by_change`
- `introduced_by_fix`
- `coverage_miss`
- `out_of_scope`

## Coverage entry

各entryは次を持つ。

- `criterion_id`: `review-policy`のstable criterion ID
- `disposition`: coverage固定値
- `evidence_refs`: file、line、command、test、CI等
- `notes`: 確認内容
- `remaining_risk`: `held`、`not_applicable`、`unexplored`では必須

`planned_criteria`に含まれないcriterionを、完了条件を満たすためだけに後付けしてはならない。新しいriskが判明してplan変更が必要な場合は、current stageを終了し、`review-policy`でcycleを再計画する。

## Finding entry

各findingは次を持つ。

- `finding_id`: review cycle内で安定したID
- `severity`
- `origin`
- `summary`
- `locations`: file、line、contract等
- `evidence_refs`
- `required_change`
- `related_criterion_ids`

## Result invariants

- `coverage`は`planned_criteria`の全IDをちょうど1回含む。
- 非選択risk moduleのcriterionをcoverage rowへ要求しない。
- `not_applicable`、`held`、`unexplored`は理由と残存riskを持つ。
- BlockingまたはHigh findingがある場合、`verdict`は`pass`または`pass_with_held`にならない。
- `unstable`では`follow_up`を`design_rework`または`split_required`にする。
- `merge_candidate=true`は`review-policy`のmerge可能条件を全て満たす場合だけ許可する。
- rendererやartifact adapterは`verdict`、`follow_up`、finding severityを文面から再計算しない。
- review結果はMarkdown fileの存在やheading構造に依存しない。

## Presentation boundary

- review core: `ReviewRequest -> ReviewResult`
- review result renderer: `ReviewResult -> Markdown | chat text | concise PR comment`
- artifact adapter: rendered textとartifact metadataをrepository file、commit、PR commentへ反映

presentationまたはartifact生成が失敗しても、既に得られた`ReviewResult`を変更しない。

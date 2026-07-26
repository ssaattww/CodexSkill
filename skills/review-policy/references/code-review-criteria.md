# Code Review Criteria

この文書は、code reviewで使用するcriterion IDと確認内容の唯一のsource of truthである。

report template、PR本文、review promptへ詳細項目を複製しない。rendererはこの文書のIDと短い表示名を参照してcoverage表を生成する。

## Universal core

全reviewで必須とする。

### U-REQ — 要件・設計基準

- task、Issue、request、authoritative design、repository instructionを確認する。
- intended normal path、non-goals、ownership境界を特定する。
- outdated reportまたは旧design revisionではなく、現在の要求を基準にする。

### U-SCOPE — 変更・依存範囲

- 全変更targetを確認する。
- 直接caller、consumer、validator、serializer、persistence、UI、公開API等の依存境界を確認する。
- 他taskまたは他PRの所有範囲を勝手に変更していないか確認する。
- scope外だが影響する問題はheldまたはexternal ownerとして分離する。

### U-CONTRACT — 契約・結果整合

- publicまたはshared contractの入力、出力、null、zero、ordering、failure semanticsを確認する。
- 既存domain contractを不必要に複製または簡略化していないか確認する。
- downstream consumerが必要なidentity、status、path、revision、metadataを失っていないか確認する。

### U-TEST — テストと再現性

- behavior changeに対応するtest evidenceを確認する。
- fixtureが実protocol、file format、API、toolで成立する入力か確認する。
- exact result、failure classification、回帰保持を確認する。
- TDDはtaskまたは利用者が要求した場合だけcriterionとする。

### U-EVIDENCE — 最終証跡

- 実際に確認したcommand、test、CI、artifact、HEAD SHAを記録する。
- CIがある場合は対象branch HEAD SHAに紐づくrunだけを判定に使う。
- CI successだけでは未テストのfailure conditionを解消したことにしない。

### U-DELIVERY — 文書・scope・提出整合

- source documentation、design、implementation report、PR本文がcurrent behaviorと一致するか確認する。
- finding、held、unexplored、remaining riskがfinal verdictと矛盾しないか確認する。
- mergeはreview resultとは別actionであり、reviewerは実行しない。

## Risk module: M-STATE — State and persistence

state、永続化、migration、reviewed range、cache等を変更する場合に選択する。

### M-STATE-01 — State invariant

- schema、ID、path、line count、interval、hash、ordering、uniquenessを利用前と出力前に検証する。
- existing、generated、final stateへ同等のvalidatorを適用する。

### M-STATE-02 — Persistence and migration

- load、save、round-trip、optional metadata、backward compatibilityを確認する。
- child context作成時にowner-wideまたはrepository-wide stateを破壊しないか確認する。

### M-STATE-03 — Lifecycle transition

- create、delete、recreate、rename-back、promotion、migration、stale baselineを確認する。

## Risk module: M-INPUT — Parser and untrusted input

parser、deserializer、external payload、diff、URI、configurationを扱う場合に選択する。

### M-INPUT-01 — Malformed input

- empty、missing、duplicate、partial、contradictory、unknown、unsupported inputを確認する。
- required field欠落をsilent skipしない。

### M-INPUT-02 — Format consistency

- header/body count、cursor、order、anchor、gap、pair metadata、status matrixを確認する。
- canonical decode後にvalidationする。

### M-INPUT-03 — Complete evidence

- incomplete patch、truncated payload、unrelated full text等をcomplete inputとして受理しない。

## Risk module: M-ATOMIC — Atomicity and concurrency

複数write、CAS、transaction、並行更新、複数source統合を扱う場合に選択する。

### M-ATOMIC-01 — Transaction boundary

- logical operationのwrite、commit、CAS回数を確認する。
- range、metadata、baseline、source等の部分成功を残さない。

### M-ATOMIC-02 — Coherent observation

- 一つのoperationで必要なsourceを一回のcoherent snapshotとして扱う。
- retryまたはre-readで異なるobservationを混在させない。

### M-ATOMIC-03 — Conflict policy

- source priority、conflict resolution、compare-and-swap failure、recoveryを確認する。

## Risk module: M-IDENTITY — Identity and canonicalization

repository、context、revision、file、path、cache key、URI等のidentityを扱う場合に選択する。

### M-IDENTITY-01 — Identity binding

- map key、payload ID、context、base/head revision、file state、cacheを相互照合する。
- stale dataを新しいcontextへ組み合わせられないようにする。

### M-IDENTITY-02 — Canonicalization and uniqueness

- path、URI、authority、revision keyをcanonicalizeしてからcollisionとuniquenessを判定する。

### M-IDENTITY-03 — Immutable source

- immutable contractでmoving ref、mutable alias、short ID等を受理しない。
- 同一identityが時間経過で別内容を返さないことを確認する。

## Risk module: M-EXTERNAL — External process, network, and filesystem

Git、network、filesystem、connector、subprocess等を扱う場合に選択する。

### M-EXTERNAL-01 — Failure classification

- expected absenceとfatal operational failureを区別する。
- broad exit codeを理由に関係なくbenign resultへ変換しない。
- invocation、stdout、stderr、signal、timeout等の診断を保持する。

### M-EXTERNAL-02 — Resource boundary

- buffer上限、大容量入力、encoding、timeout、termination、stream closeを確認する。
- silent truncationまたはreplacement decodeを許容しない。

### M-EXTERNAL-03 — Side-effect count

- process起動、network request、filesystem scan、Git inspectionの重複を確認する。

## Risk module: M-RUNTIME — Performance and responsiveness

UI、Extension Host、request handler、大規模入力、同期処理へ影響する場合に選択する。

### M-RUNTIME-01 — Complexity

- nested scan、repeated normalization、O(n²)、untrusted numeric range展開を確認する。

### M-RUNTIME-02 — Blocking behavior

- UI thread、Extension Host、request handlerを同期的に長時間blockしないか確認する。

### M-RUNTIME-03 — Cache trade-off

- cache、deduplication、memoizationがfreshnessまたはidentity validationを弱めないか確認する。

## Risk module: M-DOC — Documentation and workflow-only changes

Markdown、Skill、design、workflow policy、report contractだけを変更する場合に選択する。

### M-DOC-01 — Single source of truth

- 同じcriteria、contract、enum、design authorityを複数fileへ手作業で重複管理しない。

### M-DOC-02 — Responsibility boundary

- policy、core logic、runner、renderer、artifact adapterの責務と依存方向を確認する。

### M-DOC-03 — Executable workflow consistency

- Skillのcaller、input、output、completion conditionがhierarchy designと実運用に一致するか確認する。
- proseだけでmachine stateを推測するcontractになっていないか確認する。

## Criterion stability

- criterion IDは既存reportとhandoffの参照keyである。
- wording変更だけでIDを変更しない。
- semanticsを破壊的に変更する場合は新IDを追加し、旧IDをdeprecatedとして記録する。
- reportにはselected criterion IDだけをmaterializeする。

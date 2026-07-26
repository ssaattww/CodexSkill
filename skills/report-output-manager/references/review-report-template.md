# コードレビュー報告書

## タスクとレビュー情報

- タスク識別子:
- レビュー対象:
- レビュー種別: 初回レビュー / 再レビュー
- reviewer:
- reviewer再利用判断または変更理由:
- 対象branch:
- 対象HEAD SHA:
- 基準branchまたは比較元:
- 適用した設計書・終了条件・repository指示:

## 対象範囲

- 変更ファイル:
- 依存先・利用側・関連境界:
- 対象外:
- scope外だが影響する既知事項:

## 確認項目

状態は次のいずれかを記入する。

- `確認済み・指摘なし`
- `確認済み・指摘あり`
- `保留`
- `対象外`
- `未確認`

`保留`、`対象外`、`未確認`には理由と残存リスクを必ず記入する。

| ID | 確認項目 | 状態 | 確認内容・証跡 | finding・保留・残存リスク |
| --- | --- | --- | --- | --- |
| CR-01 | レビュー基準 |  |  |  |
| CR-02 | 変更・依存範囲 |  |  |  |
| CR-03 | 契約・仕様 |  |  |  |
| CR-04 | 状態・identity・永続化 |  |  |  |
| CR-05 | 境界・不正入力 |  |  |  |
| CR-06 | Atomicity・失敗動作 |  |  |  |
| CR-07 | テスト品質・回帰保持 |  |  |  |
| CR-08 | 性能・副作用 |  |  |  |
| CR-09 | 文書・設計整合 |  |  |  |
| CR-10 | CI・証跡 |  |  |  |
| CR-11 | 再レビュー拡張 |  |  |  |

### CR-01 レビュー基準

- taskまたはIssueの終了条件を確認したか:
- authoritativeな設計書とrepository指示を確認したか:
- intended normal path、non-goals、ownership境界を確認したか:
- 過去の監査・設計・利用者指示による追加基準:

### CR-02 変更・依存範囲

- 全変更ファイルを確認したか:
- 直接caller、consumer、serializer、validator、persistence、UIまたはAPIを確認したか:
- 既存contract、parser、validator、helper、policyとの重複を確認したか:
- default branchおよび隣接変更との組合せを確認したか:
- 他taskまたは他PRの所有範囲を変更していないか:

### CR-03 契約・仕様

- 実装が終了条件と設計を満たすか:
- 既存domain contractを適切に再利用しているか:
- public APIの入力、出力、null、zero、順序、例外を確認したか:
- static typeだけに依存せずruntime boundaryを検証しているか:
- 後続consumerに必要な情報を失っていないか:

### CR-04 状態・identity・永続化

- map key、payload ID、path、revision、context、repository identityが一致するか:
- stale stateまたはstale cacheを新しいcontextへ混在できないか:
- line count、interval、canonical order、unique constraintを確認したか:
- contextまたはownerの優先順位を確認したか:
- create、delete、recreate、rename-back、promotion、migrationを確認したか:
- load、save、round-trip、backward compatibilityを確認したか:

### CR-05 境界・不正入力

- empty、zero、minimum、maximum、missingを確認したか:
- duplicate、contradictory、partial、stale、unknown、unsupportedを確認したか:
- 必須field欠落や不正入力をsilent skipしていないか:
- canonicalize後にcollisionとuniquenessを確認しているか:
- policyまたはexclusionがstructural validationを迂回しないか:
- parserのheader、body、count、order、cursor、anchor、gapを確認したか:
- expected absenceとunknown operational failureを区別しているか:

### CR-06 Atomicity・失敗動作

- logical operationのtransaction boundaryを確認したか:
- 実write、commit、CAS、external commandの回数を確認したか:
- partial persistenceまたはpartial resultが残らないか:
- failure、retry、re-readがcoherent snapshotを維持するか:
- failure diagnosticsが原因調査に十分か:

### CR-07 テスト品質・回帰保持

- TDDが必要な場合にtest-first証跡があるか:
- fixtureが実protocol、parser、API、toolで成立する入力か:
- normal、partial、excluded、malformed、stale、cross-revisionを確認したか:
- file-levelとaggregate-levelのexact resultをassertしているか:
- testが通常commandとCIへ接続されているか:
- 過去findingのregression testが削除または弱体化されていないか:
- reportとPR本文のtest記載がcurrent suiteと一致するか:

### CR-08 性能・副作用

- filesystem、network、Git、process、parser、persistenceの重複を確認したか:
- normal、remote、大規模入力でoperation countを見積もったか:
- nested scan、repeated normalization、range expansionの計算量を確認したか:
- UI thread、Extension Host、request handlerを同期blockしないか:
- cacheまたはdeduplicationがfreshnessとidentityを弱めないか:

### CR-09 文書・設計整合

- public API、DTO、schema、runtime boundaryのcontractが文書化されているか:
- 設計書のfile layout、behavior、persistence formatが実装と一致するか:
- authoritative designが機能単位に整理されているか:
- 重複するauthoritative designがないか:
- implementation reportとPR本文がcurrent code、test、Red、Green、HEAD、CIと一致するか:
- source shapeおよびMarkdown policyを適用したか:

### CR-10 CI・証跡

- 対象branch HEAD SHAに紐づくworkflow runか:
- 必須のbuild、lint、unit、integration、package、host testを確認したか:
- failure時にstdout、stderr、environment、source、test、config、generated output、test result artifactを確認したか:
- HEAD SHA、run ID、conclusion、artifact IDを記録したか:
- code、test、config、document gate変更後に再検証したか:

### CR-11 再レビュー拡張

初回レビューでは`対象外`とし、理由に「初回レビュー」を記録してよい。

- 前回findingを実装とtestの両方で再確認したか:
- 前回修正の直接対象外だったfile、dependency、invariantを追加確認したか:
- 同種欠陥のsibling caseを探索したか:
- 過去regression testの保持を再確認したか:
- refactor後の性能、文書、結果contract、failure behaviorを再評価したか:
- 今回新たに確認した範囲を明示したか:

## 確認したファイル

### 変更ファイル

- 

### 依存ファイル・利用側・関連境界

- 

### 確認しなかった変更ファイル

- なし / ファイルと理由:

## 実行・確認したテストとコマンド

| 種別 | コマンドまたはtest | 対象 | 結果 | 証跡 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 指摘事項

findings first、severity順で記録する。指摘がない場合は`指摘なし`と明記する。

### Blocking / High

- 指摘なし / finding:

### Medium

- 指摘なし / finding:

### Low

- 指摘なし / finding:

## 保留・対象外

| 項目 | disposition | 所有範囲・理由 | 残存リスク | 後続先 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 未確認領域

| 領域 | 未確認理由・blocker | 残存リスク | final判定への影響 | 必要な後続確認 |
| --- | --- | --- | --- | --- |
| なし /  |  |  |  |  |

## Markdown確認

- 対象Markdown:
- focused/full command:
- per-scope結果:
- aggregate gate:
- `skip` / `unsupported` / `failed gate` / `needs user review`:
- exact entry review要否と利用者確認状態:
- 残存リスク:

## CI証跡

- 対象branch:
- 対象HEAD SHA:
- Workflow:
- Run ID:
- Conclusion:
- 確認したjobs:
- Failure artifact ID:
- Artifactから確認した原因:
- 別branchまたは別SHAのrunを判定に使用していないこと:

## 再レビューで追加確認した範囲

初回レビューでは`対象外: 初回レビュー`と記録する。

- 前回findingの解消確認:
- 今回新たに確認したfile・dependency・contract・boundary:
- 同種欠陥の横展開確認:
- regression test保持確認:

## 最終判定

- 判定: Pass / Pass with held concerns / Fail / Review not completed
- BlockingまたはHigh finding:
- follow-up要否:
- coverage matrix未完了項目:
- 未確認領域が判定へ与える影響:
- 判定理由:
- マージ実施: しない

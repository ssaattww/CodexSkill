# RevMem PRレビュー確認観点分析

- 作成日: 2026-07-26
- 調査元: `ssaattww/RevMem`
- 対象: PR #15、PR #24、PR #25
- 目的: 実際のレビューで確認していた事項を抽出し、`review-enforcer`で再利用できる確認観点へ整理する

## 結論

3件のレビューでは、変更行だけでなく、仕様、依存先、runtime境界、状態不変条件、不正入力、atomicity、テストの現実性、回帰テスト保持、性能、設計書、PR証跡、CI対象SHA、scope保護まで確認していた。

共通していた確認観点は次のとおり。

1. 実装を見る前に、task終了条件、Issue、設計書、repository指示を確認する。
2. 全変更ファイルに加え、変更したcontractを利用するcaller、validator、persistence、UI、後続taskへの影響を確認する。
3. static typeを信用するだけでなく、外部入力、cache、parser、永続化境界でruntime validationを確認する。
4. malformed、partial、contradictory、stale、duplicate、unknown inputを正常扱いしない。
5. 複数stateや複数sourceが関係する処理では、identity、優先順位、snapshot一貫性、atomicityを確認する。
6. テストfixtureが実際のGit diff、protocol、APIで成立する入力か確認する。
7. 再レビューで新しいtestを追加するとき、過去のfindingを固定した回帰testを削除しない。
8. 重複I/O、process起動回数、transaction回数、計算量、同期blockを確認する。
9. 実装、設計書、公開API文書、implementation report、PR本文を現状へ同期する。
10. CI判定には対象branchのHEAD SHAに紐づくrunだけを使用する。
11. scope外の問題はheldとして記録し、他taskや他PRの所有範囲を勝手に変更しない。
12. 再レビューでは、前回findingの解消確認だけでなく、未確認領域と同種欠陥を追加探索する。

## PR #15で確認していた事項

対象機能は、document context routingとreview state ownership。

### Owner解決とidentity

- Git管理の有無をworkspace membershipより先に判定しているか。
- Git working tree、untracked file、detached HEAD、非Git workspace、external file、remote、UNCを意図した優先順位で分類しているか。
- repository、context、file、branch、detached revision、workspace、external-fileのidentityがcanonicalか。
- UNCではserver authorityを含めて同一性を判定しているか。
- Git command失敗をnon-repository、unborn HEAD、missing object、unknown failureへ適切に分類しているか。

### 永続化とatomicity

- 新しいbranchまたはdetached context作成時にrepository-wide Global stateを空で上書きしないか。
- lower ownerにfile stateがない場合でも、明示的な空baselineを記録するか。
- 初回promotion、全source delta、全baselineを一つのplanned snapshotへ集約しているか。
- 一つのlogical operationでCAS commitを複数回行い、部分状態を残さないか。
- commit失敗時にrangeだけ、baselineだけ、一部sourceだけが残らないか。
- reconciliation metadataが正式なcore contractとvalidatorに含まれるか。
- persisted intervalがcanonicalで、`lineCount`内に収まるか。
- schema既存データとの後方互換とfilesystem round-tripを維持するか。

### Reconciliation

- 同一open内でlower ownerを複数回読み、promotionとbaselineへ異なるsnapshotを使用しないか。
- workspaceとexternal-fileのaddition/removalが競合した場合の優先順位が明示されているか。
- lower ownerを削除・再作成した後も、古いbaselineをcommon baselineとして誤用しないか。
- 高優先sourceの判断を低優先sourceが上書きしないか。
- owner昇格後のdelta計算が同じimmutable source observationに基づくか。

### 性能と副作用

- writable openとdecoration refreshでGit inspectionを重複実行していないか。
- remote repositoryで一操作あたりのprocess起動数が過大にならないか。
- state更新と表示更新を理由に同じrepository inspectionを再実行していないか。

### 設計書、テスト、CI、scope

- 設計書をIssue番号やTask番号単位でなく、機能単位で整理しているか。
- ownership、storage、reconciliationのauthoritative designを一つへ統合しているか。
- branch、detached HEAD、untracked、external、UNC、empty baseline、source競合、malformed metadata、CAS失敗をテストしているか。
- 対象branch HEAD SHAのCI runだけを最終判定へ使用しているか。
- T300、PR #22、他のマージ済み変更をscope外として保護しているか。
- `objectExists`のexit code分類など別担当の問題をheldとして分離しているか。

## PR #24で確認していた事項

対象機能は、Git diffのfile-level transitionをreview stateへ適用する処理。

### Transition semantics

- rename chain、directory move、swap、copy、addition、deletion、ambiguous rename、split相当を順序非依存で処理できるか。
- source file IDを変更前snapshotから解決しているか。
- copy元stateを保持し、copy先だけを意図した未確認stateへするか。
- renameで過去pathへ戻る場合、`previousPaths`からcurrent pathを適切に除去するか。
- 同一sourceのdeleteとrenameを同時に受理し、`files`と`deletedFileIds`に同じfileを残さないか。
- rename、copy、additionのdestination collisionをatomicに拒否するか。

### Parserとvalidatorの整合

- authoritative parserとvalidatorで、quoted path、TAB、timestamp、`/dev/null`の解釈が一致するか。
- `rename from`と`rename to`をexactly onceのpairとして検証するか。
- `new file mode`、`deleted file mode`とold/new sideの`/dev/null`が矛盾しないか。
- copy、rename、plain additionが同じdestinationへ収束する入力を拒否するか。
- 必須path欠落、malformed section、duplicate metadata、partial transitionをsilent `continue`で無視しないか。
- parserとvalidatorにpath/section解析が二重実装され、将来乖離する構造になっていないか。

### Snapshotとruntime state

- 既存state、生成state、最終resultを同じpublic validatorへ通しているか。
- `schemaVersion`、`fileId`、`currentPath`、`previousPaths`、`lineCount`、`contentHash`を検証するか。
- `modifiedReviewed`と`originalReviewedByDiff`がsafe integer、非負、半開区間、sort済み、非重複、非隣接か。
- snapshot内のfile IDとcurrent pathが一意か。
- unchecked engine返却後のresultを再検証しているか。
- new file生成経路だけvalidatorを迂回しないか。

### Textとdiff evidence

- whitespace/EOL-only判定を不完全hunkだけから推測していないか。
- old/new全文が対象path、revision、line count、diff hunkと結び付いているか。
- 全文から再構成したremoved/added linesがzero-context diffと完全一致するか。
- 無関係な全文を与えて実変更を無視できないか。

### テスト、性能、CI

- malformed rename、modeと`/dev/null`矛盾、destination重複、timestamp header、generated state、rename history、delete+rename conflictをテストしているか。
- 修正前に失敗testを追加し、通常unit suiteへ接続しているか。
- failure時にstdout、stderr、source、test、config、generated filesをartifactへ保存しているか。
- main取り込み後のbranch HEAD SHAに紐づくCIを確認しているか。
- destination数に比例してO(n²)となる走査を行っていないか。

## PR #25で確認していた事項

対象機能は、PRの追加・削除行を分母とするreview progress計算。

### 分子と分母

- 実際のaddition/deletion座標だけを分子へ算入しているか。
- context line、unknown coordinate、Global state、別revision、別contextを算入しないか。
- unique addition/deletion座標数とGitHub統計値をside別に厳密一致させるか。
- 不一致を上限丸めで隠さずfailureへ倒すか。
- file単位とPR aggregateのreviewed、total、progressが整合するか。
- 分母0の扱いを明示しているか。
- addition/deletion内訳を後続UIへ渡せるか。

### Contractとidentity

- 既存`PullRequestFileChange`、`DiffHunk`、`DiffLine`を再利用しているか。
- 簡略modelによりfile ID、status、old/new path、hunkを失っていないか。
- context ID、base SHA、head SHA、original diff ID、changed filesを一体のvalidated snapshotへ持たせているか。
- stale cacheのfilesをcurrent PR contextと組み合わせられないか。
- diff identityをbase/head revisionと照合しているか。
- review stateのmap key、payload file ID、revision、current path、line count、interval boundsがchanged fileと一致するか。

### Unified diff validation

- runtimeの`DiffLine.kind`とfile statusをexhaustiveに検証するか。
- hunk header countとbody countが一致するか。
- old/new cursor、opposite-side coordinate absence、hunk order、gap、cumulative deltaが整合するか。
- duplicate coordinate、missing coordinate、zero-zero hunk、context-only hunkを拒否するか。
- added/deleted fileでpartial patchをcomplete file diffとして受理しないか。
- modified-side hunk extentとzero-count anchorをcurrent fileの`lineCount`へ結び付けるか。
- added、deleted、modified、renamed、copiedごとのpath、side、count matrixを検証するか。

### Exclusion policy

- binaryまたはglob exclusionが集計だけを除外し、diff/state validationを迂回しないか。
- 非binary fileの構造検証をexclusion判定前に完了しているか。
- old/new両pathをrepository-relativeにcanonicalizeしているか。
- file IDが異なってもcanonical path重複を拒否するか。
- excluded resultでもsource count、status、exclusion reasonを保持するか。
- excluded fileだけstale stateやinvalid intervalの検証をskipしないか。

### テスト品質と回帰保持

- fixtureが実際にGitが生成できるunified diffか。
- addition、deletion、replacement、multiple hunk、partial progress、exclusion、binary、stale identity、non-PR context、invalid state、duplicate ID/path、malformed coordinate、zero denominatorをテストするか。
- file-level progressとaggregate progressのexact valueをassertするか。
- 新しいreview対応でtest suiteを組み替える際、過去findingの回帰testを削除しないか。
- implementation reportに記載したcaseがcurrent suiteへ残っているか。

### 文書、性能、CI

- public DTOとcalculatorでcoordinate base、normalized path、exclusion、zero denominator、order、validation failureを説明しているか。
- `@param`、`@returns`、`@throws`を含む公開contractがあるか。
- PR本文とimplementation reportを最新のRed、Green、final HEAD、CIへ同期しているか。
- reviewed intervalを一行ずつ巨大な`Set`へ展開せず、changed coordinate中心の計算量にしているか。
- CI successだけでmalformed caseの未テストを見逃していないか。
- branch HEAD SHAのrunとfailure artifactだけを判定・診断へ使用しているか。

## CodexSkillへ反映する確認項目

レビュー報告書では、最低限、次の区分を明示的に確認またはdispositionする。

- レビュー基準
- 変更・依存範囲
- 契約・仕様
- 状態・identity・永続化
- 境界・不正入力
- Atomicity・失敗動作
- テスト品質・回帰保持
- 性能・副作用
- 文書・設計整合
- CI・証跡
- 再レビュー拡張

各区分は、確認済み、指摘あり、保留、対象外、未確認のいずれかを記録する。保留、対象外、未確認には理由と残存リスクを記録する。

実際の確認項目は次のファイルへ反映する。

- `skills/review-enforcer/references/code-review-coverage-checklist.md`
- `skills/report-output-manager/references/review-report-template.md`

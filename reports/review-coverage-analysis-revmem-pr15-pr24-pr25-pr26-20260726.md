# RevMem PRレビュー確認観点分析

- 作成日: 2026-07-26
- 調査元: `ssaattww/RevMem`
- 対象: PR #15、PR #24、PR #25、PR #26
- 目的: 実際のレビューで確認していた事項とfindingが小出しになった原因を整理し、risk-based review policyへ反映する

## 結論

4件のレビューでは、変更行だけでなく、仕様、依存先、runtime境界、state、identity、不正入力、atomicity、test fixture、回帰保持、performance、document、CI対象SHA、scope protectionまで確認していた。

一方、PR #15、#24、#25、#26では、最初のfindingを発見した時点でplanned coverageを完了せず、修正後の再レビューで別領域を追加探索したため、重要findingが小出しになった。必要なのは無制限な再レビューではなく、次の運用である。

1. 初回review前にrisk profileとplanned criteriaを確定する。
2. 初回reviewはBlockingを見つけても終了せず、planned coverageを最後まで完了する。
3. 修正確認は既存finding、fix、直接影響、同種欠陥へ限定する。
4. medium/high riskだけfresh contextによるcold finalを1回行う。
5. cold final後も新しい独立Blocking/Highが出る場合は`unstable`として設計見直しまたはPR分割へ戻す。
6. report文面ではなくmachine-readableな`ReviewResult`でworkflow stateを表す。

## 共通していたuniversal確認観点

### 要件・設計

- task終了条件、Issue、authoritative design、repository instructionを確認する。
- intended normal path、non-goals、ownership境界を確認する。
- outdated reportや旧design revisionを基準にしない。

### 変更・依存範囲

- 全変更fileを確認する。
- caller、consumer、validator、serializer、persistence、UI、API等の直接依存を確認する。
- 他taskまたは他PRの所有範囲を勝手に変更しない。
- scope外の問題はheldまたはexternal ownerへ分離する。

### Contract

- public/shared contractのinput、output、null、zero、ordering、failure semanticsを確認する。
- 既存domain modelを簡略modelで置換して必要情報を失っていないか確認する。
- downstream taskへidentity、status、path、revision、metadataを渡せるか確認する。

### Testとevidence

- fixtureが実protocol、Git diff、file format、APIで成立するか確認する。
- exact result、failure classification、回帰保持を確認する。
- CI successだけで未テスト境界を解消したことにしない。
- 最終判定は対象branch HEAD SHAに紐づくrunを使う。

## PR #15で確認していた事項

対象機能はdocument context routingとreview state ownership。

### Owner解決とidentity

- Git管理の有無をworkspace membershipより先に判定する。
- working tree、untracked、detached HEAD、非Git workspace、external、remote、UNCを意図した優先順位で分類する。
- repository、context、file、revision、workspace、external-file identityをcanonicalにする。
- UNCはserver authorityを含める。
- Git failureをnon-repository、unborn HEAD、missing object、unknown failureへ分類する。

### State、persistence、atomicity

- 新しいbranch/detached contextがrepository-wide Global stateを空で上書きしない。
- lower ownerにfile stateがなくても明示的なempty baselineを記録する。
- promotion、全source delta、全baselineを一つのplanned snapshotと一つのCASへ集約する。
- commit失敗でrange、baseline、一部sourceだけを残さない。
- reconciliation metadataを正式なcore contractとしてload/save/commit時に検証する。
- intervalをcanonicalかつ`lineCount`内に保つ。

### Reconciliation

- 同一open内でlower ownerを複数回読み、promotionとbaselineへ異なるsnapshotを使わない。
- workspaceとexternal-fileのconflict priorityを明示する。
- lower ownerのdelete/recreate後に旧baselineをcommon baselineとして使わない。
- low priority sourceがhigh priority decisionを上書きしない。

### Performance、document、scope

- writable openとdecoration refreshでGit inspectionを重複しない。
- remote repositoryでprocess起動数を見積もる。
- designをIssue/Task単位でなくfeature単位へ統合する。
- T300、PR #22、他のmerged workをscope外として保護する。

### 小出しになった原因

初期review後も、empty baseline、single CAS、single observation、source priority、persisted metadata、Global preservation等が別roundで見つかった。初回のrisk planに`M-STATE`、`M-ATOMIC`、`M-IDENTITY`を選び、planned criteriaを最後まで確認していれば、多くを一回のfinding setへまとめられた。

## PR #24で確認していた事項

対象機能はGit diffのfile-level transition適用。

### Transition semantics

- rename chain、directory move、swap、copy、addition、deletion、ambiguous rename、split相当をorder independentに処理する。
- source file IDをpre-change snapshotから解決する。
- copy元stateを保持し、copy先を意図したstateへする。
- rename-backで`previousPaths`を正しく更新する。
- deleteとrenameの同一source、duplicate destinationをatomicに拒否する。

### Parserとvalidator

- quoted path、TAB、timestamp、`/dev/null`解釈をauthoritative parserとvalidatorで一致させる。
- `rename from`/`rename to`をexactly onceのpairとして検証する。
- `new file mode`/`deleted file mode`とsideを整合させる。
- missing path、duplicate metadata、partial transitionをsilent skipしない。
- parser/validatorの二重実装による将来乖離を確認する。

### Snapshot、text evidence、performance

- existing、generated、final stateを同じvalidatorへ通す。
- schema、file ID、path、line count、hash、reviewed intervalを検証する。
- old/new全文をpath、revision、line count、hunkへ結び付ける。
- zero-context diffとreconstructed linesを完全一致させる。
- destination scan等のO(n²)処理を確認する。

### 小出しになった原因

初回finding対応後、duplicate destination、timestamp path、malformed transition、state invariant、generated state、text/diff evidence、rename-back、delete+renameが順番に見つかった。初回に`M-INPUT`、`M-STATE`、`M-ATOMIC`を計画し、valid/invalid matrixとfinal-output validationを一通り完了すべきだった。

## PR #25で確認していた事項

対象機能はPRの追加・削除行を分母とするreview progress計算。

### 分子・分母とcontract

- actual addition/deletion coordinateだけを分子へ算入する。
- context、unknown、Global、別revision、別contextを算入しない。
- unique coordinate数とsource statisticsをside別に一致させる。
- fileとaggregateのreviewed、total、progressを整合させる。
- existing `PullRequestFileChange`、`DiffHunk`、`DiffLine`を再利用する。

### Identityとunified diff

- context ID、base/head SHA、diff ID、changed filesを一つのvalidated snapshotへ束ねる。
- stale cacheとcurrent contextを組み合わせられないようにする。
- map key、payload file ID、revision、current path、line countを照合する。
- hunk header/body count、cursor、opposite-side absence、order、gap、deltaを検証する。
- duplicate/missing coordinate、no-op/context-only hunkを拒否する。
- added/deleted fileをcomplete file diffへ限定する。

### Exclusion、test、performance

- binary/glob exclusionがvalidationを迂回しない。
- old/new pathをcanonicalizeし、canonical duplicateを拒否する。
- excluded resultでもcount、status、reasonを保持する。
- Gitが生成可能なfixtureを使う。
- 過去findingのregression testを後続roundで削除しない。
- reviewed intervalを一行ずつ巨大なSetへ展開しない。

### 小出しになった原因

initial model mismatch、statistics、snapshot identity、hunk coordinate、zero-count anchor、runtime discriminant、status matrix、exclusion validation、complete added/deleted diff、lineCount boundsが複数roundで見つかった。初回に`M-INPUT`、`M-IDENTITY`、`M-RUNTIME`を選び、realistic fixture、runtime discriminant、status matrix、boundsをplanned coverageへ含める必要があった。

## PR #26で確認していた事項

対象機能は仮想diff URIとrevision content provider。

### 最初のfinding

最初のreviewでは、Git exit code 128を理由に関係なく`missing-revision`/`missing-file`へ変換する問題をBlockingとして確認した。

- repository破損
- permission failure
- dubious ownership
- I/O系fatal

これらがexpected absenceへ誤分類され、diagnosticが失われる問題だった。

### 後続reviewで追加されたfinding

最初のfindingを発見した時点で初回reviewを終了したため、次の重要境界は後続reviewで見つかった。

1. **moving ref**
   - `HEAD`、branch、tag等をimmutable URI sourceとして受理していた。
   - 同一URIがref更新後に別内容を返し得た。
   - immutable identityとrevision bindingの問題だった。
2. **large blob**
   - subprocess stdoutの4 MiB buffer上限により通常textを取得できなかった。
   - application contractに存在しないhidden resource limitだった。
3. **UTF-8 boundary**
   - invalid UTF-8をreplacement characterへsilent変換し、exact text contractを破壊した。
   - raw bytes、fatal decode、binary/exclusion policyの境界だった。
4. **process lifecycle**
   - timeout、SIGTERM、SIGKILL、close event、partial stdout/stderr、bounded failureを確認した。
5. **architecture and discovery**
   - architecture positive/negative gateとdesign contract testの通常CI discoveryを確認した。

### PR #26から得たreview policy

PR #26は、初回reviewで一つのBlockingを見つけても、予定した`M-EXTERNAL`、`M-IDENTITY`、`M-INPUT`、`M-RUNTIME`を最後まで確認する必要性を示す。

特に次をinitial planned coverageへ含める。

- benign absenceとfatal failureの分類
- mutable refとimmutable identity
- buffer、stream、size、encoding
- timeout、signal、process close
- architecture boundaryとCI discovery

これらを後続roundで無制限に追加するのではなく、初回で一括確認し、fix verificationはfinding setへ限定し、cold finalをfresh contextで一度だけ行う。

## 新しいreview architectureへの反映

### Structured boundary

- `ReviewRequest`はrequirement、scope、risk profile、selected module、planned criteria、previous finding、evidenceを持つ。
- `ReviewResult`はcoverage、finding、held、unexplored、evidence、verdict、follow-up、stop reasonを持つ。
- report textは`ReviewResult`のrendererであり、workflow stateのsourceではない。

### Universal coreとrisk module

全reviewでuniversal coreを確認する。

- requirement/design
- change/dependency scope
- contract
- test
- final evidence
- document/scope/delivery consistency

変更riskに応じて次を選ぶ。

- `M-STATE`
- `M-INPUT`
- `M-ATOMIC`
- `M-IDENTITY`
- `M-EXTERNAL`
- `M-RUNTIME`
- `M-DOC`

非選択moduleは個別rowを作らない。

### Stop conditions

- initial comprehensive reviewはstable scopeにつき一回。
- fix verificationは同一finding setにつき最大二回。
- medium/high riskのcold finalはfresh contextで一回。
- cold finalのnew independent Blocking/High、repeated coverage miss、scope instabilityは`unstable`。
- `unstable`後はreviewを追加せず、design reworkまたはPR splitへ戻す。

## 正本

- Review contract: `skills/review-core/references/review-contract.md`
- Criterion source: `skills/review-policy/references/code-review-criteria.md`
- Lifecycle and stop policy: `skills/review-policy/SKILL.md`
- Rendering: `skills/review-result-renderer/SKILL.md`
- Repository artifact: `skills/report-output-manager/SKILL.md`

ChatGPT chat向けstandalone workerの追加はIssue #51で扱い、このPRではshared contractとCodex側の責務分離までを対象とする。

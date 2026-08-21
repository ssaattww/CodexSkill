# スキル階層設計

## 目的

Codex向け親／sub-agent flowと、利用者が親となるChatGPT chat worker flowを一元的に定義する。

実装、レビュー、レポート生成の意味論は親runtimeに依存しないcore Skillとして定義し、CodexとChatGPTはruntime wrapperからそれらを呼び出す。

この設計書をSkill hierarchyの正本とし、`skills/design/skill-hierarchy-design.md`と同一内容に保つ。

## 実行方式

- `親が実行`: Codex親agentがSkillを直接実行する。
- `親が呼び出し、sub-agentが実行`: Codex親agentがSkillを通じてsub-agentへ実作業を委譲する。
- `利用者が親としてChatGPT chatで実行`: 利用者が独立chatを起動し、そのchatが指定wrapper Skillを直接実行する。
- `runtime非依存Skillとして実行`: 親またはwrapperから渡されたcontextを使用し、Codex親、sub-agent、ChatGPT chat固有の制御を持たずに実作業を行う。

ChatGPT wrapperは別workerまたはsub-agentを起動しない。Codex向けwrapperとChatGPT向けwrapperは別の実行系として扱うが、実装、レビュー、レポートの意味論は同じcore Skillを使用する。

## Skill依存アーキテクチャ

```text
親非依存core Skill
├─ work-context-manager
├─ implementation-worker
├─ review-worker
└─ report-writer

runtime wrapper
├─ Codex
│  ├─ implementation-executor
│  ├─ review-enforcer
│  └─ report-output-manager
└─ ChatGPT
   ├─ chat-implementation-worker
   ├─ chat-review-worker
   ├─ chat-report-writer
   └─ chat-handoff-manager
```

### Core Skill

- `work-context-manager`
  - authority、scope、target identity、development policy、validation target、current-HEAD CI evidence、write boundaryを解決する
  - 実tool capabilityから`verification_capability`を`local_execution_available`または`remote_ci_only`として解決する
- `implementation-worker`
  - initial implementationとreview follow-upを実行する
  - routeに共通のvalidation evidenceを返し、runtime別のCI待機規則を保持しない
- `review-worker`
  - initial review、fix verification、independent final reviewを実行する
  - closure前のrequired-action completeness matrixを確認し、不足したfindingをclosure reviewへ渡さない
- `report-writer`
  - evidenceの意味を変えずにreportと簡易PR commentを生成する

全core SkillはCodex親、Codex sub-agent、ChatGPT親chatのいずれにも依存しない。

### Runtime wrapper

Codex wrapperはsub-agent dispatch、reviewer identity、normal review continuity、一度だけのfresh independent reviewerと同reviewerによるbounded closure、report path、persistence、completion gateを所有する。

ChatGPT wrapperはcurrent-chat permission、connector、repository／PR persistence、chat continuity、cross-chat handoffを所有する。

## Verification capabilityと状態遷移

`work-context-manager`はruntime名ではなく実際のtool capabilityでrouteを決め、context、report、handoffに`verification_capability`を記録する。

- `local_execution_available`: local test executorを利用できる。Codexだけでなくlocal executorを利用可能なChatGPT chatもこのrouteを使う。
- `remote_ci_only`: local test executorを利用できない。ChatGPTだけでなくshellを利用不能なCodex runtimeもこのrouteを使う。

commit、push、CI waitは別状態である。review対象を固定するcommitは両routeで必須だが、commitだけでpushまたはCI waitを意味しない。runtime-neutral coreはevidenceとreviewの意味論を扱い、Codex／ChatGPT wrapperはそれぞれ実行能力、authorized push、CI evidence取得と待機を管理する。

### Local route

`local_execution_available`では、変更範囲のlocal testを実行してからreview対象commitを作成し、reviewする。findingごとのreview/fix loopはlocal fix、該当local validation、commit、finding-limited closureで進め、CI完了を待たない。closure依頼前に、全required action、production実装、actual composition fixture、focused evidenceをfindingごとに揃えたcompleteness matrixを確認する。

CIを発火するpush前には該当local validationをGreenにする。normal cycle収束後のfinal push前にはrepository-defined full local gateをGreenにし、inner-loop focused testで代用しない。final attestation後にfinal pushを行い、exact-head `pull_request` required CIだけをmerge gateとして一度待つ。repository policyが要求しない`push` runは待たない。

### Remote CI route

`remote_ci_only`ではlocal validationを実行できないため、authorized push後のmatching current-HEAD CIを正式なverification evidenceとして待機できる。matching runが不在、未完了、または失敗なら成功扱いにせず、reportとhandoffへ記録する。review前commit、closure前completeness matrix、final attestation後のexact-head `pull_request` required CIは両routeの共通gateである。

共通動作を複数Skillから同一fileとして参照しない。共通動作は独立Skillとして定義し、wrapperまたは他のSkillがSkill名で呼び出す。

## Codex標準開発flow

```text
development-orchestrator [親]
├─ restart-handover-manager
├─ work-context-manager
├─ task-consistency-manager
├─ design-doc-maintainer
│  ├─ codex-delegation-executor
│  │  └─ design-executor
│  └─ task-consistency-manager
├─ tdd-executor [対象repositoryが明示要求する場合だけ]
│  ├─ work-context-manager
│  ├─ codex-delegation-executor
│  │  └─ implementation-executor [wrapper]
│  │     ├─ work-context-manager
│  │     └─ implementation-worker
│  └─ sub-agent-task-manager [test evidence]
├─ codex-delegation-executor
│  ├─ implementation-executor [wrapper]
│  │  ├─ work-context-manager
│  │  └─ implementation-worker
│  ├─ design-executor
│  ├─ sub-agent-task-manager [verification]
│  └─ report-output-manager [wrapper]
│     ├─ work-context-manager
│     └─ report-writer
├─ review-enforcer [wrapper]
│  ├─ work-context-manager
│  ├─ markdown-word-checker
│  ├─ sub-agent-task-manager [normal reviewer]
│  │  └─ review-worker
│  ├─ sub-agent-task-manager [fresh independent final reviewer]
│  │  └─ review-worker
│  └─ report-output-manager
│     └─ report-writer
├─ progress-sync-manager
├─ git-workflow-manager
│  ├─ git-branch-starter
│  ├─ git-commit-manager
│  ├─ git-pr-submitter
│  └─ git-review-followup-manager
├─ feedback-points-manager
│  └─ feedback-points-sanitizer
└─ skill-authoring-wrapper
```

## TDD適用境界

TDD要否は対象repositoryの明示的なinstruction、accepted design、または利用者指示が決める。

- `development-orchestrator`は`work-context-manager`でgoverning sourceを確認する
- TDDが明示要求される場合だけ`tdd-executor`を呼ぶ
- `tdd-executor`は`implementation-executor`から`implementation-worker`を呼び出す
- TDDが要求されない場合は`not applicable`として通常implementationへ進む
- codeまたはtestを変更するという事実だけではTDD適用理由にならない
- CodexSkill repository自身の保守にはTDDを適用しない

CodexSkill固有の非TDD方針はroot `AGENTS.md`をrepository-level authorityとする。

## Codexレビュー契約

Codexでも独立最終レビューを必須とし、技術レビューの意味論には`review-worker`を使用する。

### 通常レビューcycle

1. 実装後に`review-enforcer`を実行する。
2. 専用normal reviewer sub-agentを選ぶ。
3. reviewerは`work-context-manager`でtargetとevidenceを解決する。
4. initial reviewとして`review-worker`を実行する。
5. finding、review criteria、reviewed HEAD、fix context、held、unexploredをreportへ保持する。
6. required findingがある場合はimplementation flowへ戻す。
7. fix後は原則として同じnormal reviewerを継続利用する。
8. `review-worker`のfix verificationでfinding解消、fix diff、直接影響、同一欠陥class、新規変更領域を確認する。
9. closure依頼前に、findingごとの全required action、production実装、actual composition fixture、focused evidenceをcompleteness matrixで確認する。不足があればreviewerへ渡さない。
10. normal review／fix verification report、implementation report、verification report、tracking、designを保存してcommitする。pushとCI waitはverification routeに従う別状態であり、local routeのreview/fix loopに含めない。
11. required findingが解消または明示的にdispositionされるまで、bounded normal cycleを継続する。

元のnormal reviewerを継続できない場合は、replacement identityと理由を記録し、finding identity、criteria、reviewed HEAD、fix context、held、unexploredを完全に引き継ぐ。

finding identityとsource severityはcontinuity-bearing evidenceとして維持する。severityを変更する場合は、source severity、new severity、evidence-based reason、approving authorityを明示する。downstream reportの転記誤りはhistorical reportを黙って書き換えず、current erratumとして記録する。

### Pre-freeze gate

normal review cycleが収束した後、independent final reviewのtargetをfreezeする前に、次を完了する。

- parent-owned end-of-Issue Skill-gap decision
- current scopeで実行する`skill-authoring-wrapper`作業
- feedback classificationと`feedback-points-manager`によるledger同期
- repository-backed normal handoff
- implementation、design、workflow、configuration、tracking、normal review report、fix-verification report、verification report
- routeに応じたcurrent-HEAD validation evidence。`remote_ci_only`ではmatching current-HEAD CIを正式evidenceとして待機でき、`local_execution_available`ではfinal attestation後のexact-head `pull_request` required CIだけをmerge gateとして一度待つ

上記の処理でrepository fileが変わった場合、validation、report、tracking、commitを行い、verification routeに従ってpushし、normal reviewまたはfix verificationへ戻る。新しいrepository writeが残った状態でfreezeしてはならない。

### 独立最終レビュー

pre-freeze gateを通過し、全ての非final変更がcommitされた後に、independent-final-review report pathを予約する。`local_execution_available`ではvalidated local committed HEADをpushせずに、`remote_ci_only`ではauthorized pre-review pushとmatching current-HEAD CIをformal evidenceとして、そのHEADを`reviewed implementation HEAD`に固定する。

fresh reviewerは次を満たす。

- implementation sub-agentと異なること
- 通常reviewerと異なること
- review fixを実装していないこと
- 原則`fork_turns: "none"`で起動すること
- frozen reviewed implementation HEADを対象とすること
- 要件、設計、final diff、全変更file、直接依存、tracking、report、current HEAD固有validation evidenceを読むこと
- reviewer identityとindependence evidenceを記録すること
- `review-worker`のindependent final reviewを実行すること
- 過去review結論を読む前に独立passを行うこと
- normal review reportとは別にindependent final review reportを作ること

独立最終レビューはtask lifecycleで一度だけの全coverage passである。required findingまたは新しいrepository write obligationが出た場合はterminal stateを無効化し、implementationとnormal reviewerのfix verificationへ戻る。HEAD更新後は最初の独立reviewerが、completeness matrixを満たしたfinding／CI-deltaだけをbounded closureとして確認し、新しい観点や再度の全coverage passを行わない。

normal reviewだけ、同じreviewerによる再reviewだけ、親agent自身のreviewだけでは完了条件を満たさない。

## 最終review reportの終端規則

独立最終レビューのtechnical verdictは`reviewed implementation HEAD`へ結び付ける。

詳細reportをrepositoryへ保存する必要がある場合、次の条件を全て満たす1回だけの`report-attestation commit`を許可する。

- independent-final-review report pathはreview開始前に予約済みである
- report-attestation commitのfirst parentはreviewed implementation HEADである
- reviewed implementation HEADの後に存在するcommitはこの1件だけである
- diffは予約済みindependent-final-review report pathだけを変更する
- reportはreviewed implementation HEADとadministrative attestationであることを明記する
- executable、Skill、design、workflow、configuration、tracking、feedback、handoff、product fileを変更しない
- report-attestation commit以後にrepository commitを作らない
- 親またはwrapperがallowlist diffを検証し、結果をPR bodyまたはPR commentへ記録する

report-attestation commit後のfinal push、PR作成または更新、exact-head `pull_request` required CI待機は、report-attestation後にGit HEADを変更しないmerge gateであり、attestationを無効化しない。local routeではこの一回だけを待ち、`push` runはrepository policyが要求しない限り待たない。

完了identityは次のpairで表す。

```yaml
reviewed_implementation_head: full_sha
report_attestation_head: full_sha | null
```

report-attestation commitは新しいimplementation contentへverdictを転用するものではない。条件外のpost-review commitが1件でも発生した場合、完了状態を無効化し、normal fix verificationと同一independent reviewerのbounded finding／CI-delta closureへ戻る。

attestation後に許可するのはGit HEADを変更しない処理だけである。

- PR body／PR commentの更新
- review request
- external Issueの作成または更新
- inlineまたはPR branch外のhandoff transport

attestation後にrepository writeの必要性が判明した場合はterminal stateを無効化し、normal cycleへ戻る。

## ChatGPT chat worker flow

```text
利用者 [親]
├─ Chat A: chat-implementation-worker [initial implementation]
│  ├─ work-context-manager
│  ├─ implementation-worker
│  ├─ report-writer
│  └─ chat-handoff-manager
├─ Chat B: chat-review-worker [initial review]
│  ├─ work-context-manager
│  ├─ review-worker
│  ├─ report-writer
│  └─ chat-handoff-manager
├─ Chat A: chat-implementation-worker [review follow-up]
├─ Chat B: chat-review-worker [fix verification]
├─ Chat C: chat-review-worker [independent final review]
└─ Report chat: chat-report-writer [必要な場合のみ]
   ├─ work-context-manager
   ├─ report-writer
   └─ chat-handoff-manager
```

initial reviewとfix verificationは同じnormal review chatを継続する。independent final reviewは、implementation、review fix、normal reviewに参加していない新規chatで実施する。

### 初回実装

```text
Issue #<number>を開始してください。
```

`chat-implementation-worker`がrepository stateと権限を管理し、`work-context-manager`と`implementation-worker`を呼び出す。

### 初回レビュー

```text
PR #<number>を初回レビューしてください。
```

`chat-review-worker`がreview modeとreviewer identityを管理し、`review-worker`のinitial reviewを呼び出す。

### レビュー対応

```text
レビュー結果に対応してください。
```

初回実装chatを継続し、`implementation-worker`のreview follow-upでfinding、直接原因、影響境界、同一欠陥classだけを修正する。

### 修正確認

```text
PR #<number>の修正確認をしてください。
```

初回レビューと同じnormal review chatを継続し、`review-worker`のfix verificationを実行する。

### 独立最終レビュー

```text
PR #<number>を独立レビューしてください。
```

新規chatでfrozen reviewed implementation HEADを対象に`review-worker`のindependent final reviewを実行する。過去reviewの結論は独立pass後に照合する。

passing reportをrepositoryへ保存する場合は、Codexと同じreport-attestation終端規則を適用する。final handoffはattestation後にinlineで返し、repository commitを追加しない。

## ChatGPT登録用Skillセット

ChatGPTへ登録するwrapper Skillは次の4つである。

- `chat-implementation-worker`
- `chat-review-worker`
- `chat-report-writer`
- `chat-handoff-manager`

必須依存core Skillは次の4つである。

- `work-context-manager`
- `implementation-worker`
- `review-worker`
- `report-writer`

GitHub Releaseでは、8 Skillをそれぞれ独立したroot directoryとして含む単一ZIPを配布する。

```text
chatgpt-worker-skills.zip
├─ chat-implementation-worker/
├─ chat-review-worker/
├─ chat-report-writer/
├─ chat-handoff-manager/
├─ work-context-manager/
├─ implementation-worker/
├─ review-worker/
└─ report-writer/
```

各directoryには少なくとも`SKILL.md`が存在し、front matterの`name`とdirectory名を一致させる。

このZIPをChatGPTへuploadし、wrapperと依存core Skillを一括登録する。

## Handoff

handoff contractを複数Skillから同一fileとして参照しない。`chat-handoff-manager`を独立Skillとして使用する。

- reportとhandoffを別成果物とする
- schema version 3を使用する
- typed projectionとversioned `source_payloads`の両方を保持する
- source core Skillのcomplete outputをraw payloadとして保持し、typed fieldに表現できない情報を失わない
- development policy、planned validation、required failure diagnostics、blocked stateを保持する
- implementation failure diagnosticsとblocked itemsを保持する
- reviewer identity、reviewer continuity、independence evidenceを保持する
- reserved report pathsとreport-attestation allowed flag、first-parent、allowlist、forbidden path class、validation resultを保持する
- full findingのorigin、location、impact、evidence、required actionを保持する
- reviewed HEAD、required coverage、held、unexplored、requirements、intentionally untouched、test、CI artifact、commit、report／comment referenceを保持する
- schema version 1／2のoriginal packetを`source_payloads`として保存し、mapping不能fieldを捨てない
- repository write可能時は通常handoffを`reports/handoffs/`へ保存する
- PRまたはIssueから一意に特定できる場合は次workerがconnectorで取得する
- 一意に特定できない場合だけ利用者へpathまたはpacket本文を求める
- 前workerの権限は次chatへ自動継承しない
- unknownを推測で補完しない
- target Skill、mode、必要権限、参照先をpacketへ記録する
- final independent review後のhandoffはinlineまたはPR branch外でtransportし、report-attestation後のcommitを追加しない

## Release flow

`.github/workflows/release-chatgpt-worker-skills.yml`を使用する。

### pull request validation

- `AGENTS.md`、`README.md`、全Skill、`shared/**`、design、tasks、reports、builder、repository validator、workflowの変更で実行する
- forbidden shared runtime pathだけを追加する変更でもvalidation workflowを起動する
- `opened`、`synchronize`、`reopened`では実PR HEAD SHAをcheckoutする
- build jobは`contents: read`だけを持ち、checkout credentialを保持しない
- `scripts/verify_skill_repository.py`で全Skillのfront matter、Skill名依存、active Markdown link、symlink、削除済みshared runtime path、hierarchy design同期を検証する
- 全`chat-*` wrapperと必須core Skillを検出する
- missing Skill、front matter name不一致、symlink、Skill外shared参照を拒否する
- 単一`chatgpt-worker-skills.zip`を作成する
- ZIP rootが検出Skill集合と一致することを確認する
- ZIPをworkflow artifactとして保存する
- GitHub Releaseは更新しない

### Rolling normal Release

- 対象変更が`main`へpushされた場合に実行する
- push後の`main` HEADでread-only validation／build jobを実行する
- build成功後だけ別publish jobへ`contents: write`を付与する
- build jobの検証済みartifactをpublish jobへ渡す
- rolling tag `chatgpt-worker-skills-latest`を対象HEADへ更新する
- 固定通常Release `ChatGPT Worker Skills`へZIPを添付または置換する

### PR merge Pre-release

- `pull_request.closed`かつ`merged == true`の場合だけ実行し、未merge closeでは実行しない
- `merge_commit_sha`でread-only validation／build jobを再実行する
- build成功後だけ別publish jobへ`contents: write`を付与する
- build jobの検証済みartifactをpublish jobへ渡す
- tag `chatgpt-worker-skills-pr-<PR番号>`をmerge commitへ作成する
- `ChatGPT Worker Skills PR #<PR番号>`をPre-releaseとして作成する
- Pre-releaseへ`chatgpt-worker-skills.zip`を添付する
- job再実行時は同じPR tag／Pre-releaseとAssetを更新する
- 自動Pre-releaseの`release.published`イベントはtag prefixで除外し、二重build／uploadしない

### 手動Release／Pre-release

- 利用者がGitHub UIまたはAPIで公開した`release.published`イベントで実行する
- Release tagが指すcommitでread-only validation／build jobを実行する
- build成功後だけ別upload jobへ`contents: write`を付与する
- build jobの検証済みZIPを、公開された同じReleaseへ添付する
- 同名Assetがある場合は置換する
- 自動PR merge Pre-release用tag prefix `chatgpt-worker-skills-pr-`は対象外とする
- Workflowの`GITHUB_TOKEN`で作成または更新したReleaseイベントは再帰的なWorkflow runを生成しない

`workflow_dispatch`はread-only validation／buildだけを行い、Releaseを更新しない。

Release時の共通file複製とrepository相対link書換は行わない。

## 標準作業手順

1. workflow開始時にCodexSkillの鮮度を確認する。
2. 再開時は`restart-handover-manager`で状態を復元する。
3. `work-context-manager`でauthority、scope、target identity、development policy、validation target、write boundaryを解決する。
4. `development-orchestrator`がtaskを選択する。
5. `task-consistency-manager`でtrackingを同期する。
6. 設計影響があれば`design-doc-maintainer`を実行する。
7. 対象repositoryがTDDを要求する場合は`tdd-executor`を実行する。
8. `implementation-executor`から`implementation-worker`を呼び出して実装する。
9. focused validationと必要なfull validationを実行する。
10. `report-output-manager`から`report-writer`を呼び出してimplementation／verification reportを保存する。reportとtrackingは自己を含む将来のcommit SHAを要求せず、pre-commit stateは`commit_pending`としてtechnical HEADとadministrative parentを区別する。
11. `progress-sync-manager`でreportとtrackingを同期し、全非final変更をcommitする。
12. `review-enforcer`から`review-worker`を呼び出して通常review cycleを完了する。review前commitは必須であり、closure依頼前にrequired-action completeness matrixを完了する。
13. fixがあれば実装、routeに応じたvalidation、report、tracking、commit、normal fix verificationを繰り返す。local routeではCI完了を待たず、CI-triggering push前に該当local validationをGreenにする。
14. normal cycle収束後、end-of-Issue Skill-gap decisionを行う。
15. current scopeで必要な`skill-authoring-wrapper`処理を実行し、feedback classification、feedback ledger、normal handoffを保存する。
16. steps 14から15でrepositoryが変わった場合、validation、report、tracking、commit、verification routeに従うpush、normal fix verificationを再実施する。
17. 全pre-freeze変更を含むnormal cycleが収束したことを確認し、independent-final-review report pathを予約する。
18. current HEADをreviewed implementation HEADとしてfreezeする。
19. 別fresh reviewerによる独立最終reviewを実施する。
20. repository changeが必要になった場合はterminal stateを無効化し、normal cycleと同一independent reviewerのbounded finding／CI-delta closureへ戻る。
21. passing reportを保存する場合は、予約済みreport pathだけを変更する1回のreport-attestation commitを作成し、allowlist diffを検証する。
22. report-attestation commitをfinal pushし、exact-head `pull_request` required CIをmerge gateとして一度待つ。`remote_ci_only`ではroute内のmatching current-HEAD CIも正式verification evidenceとして扱う。
23. final push後にPRを作成または更新し、PR body／PR commentへreviewed implementation HEAD、report-attestation HEAD、validation evidenceを記録する。
24. attestation後にrepository-writing Skillを呼ばず、repository commitを追加しない。final handoffはinlineまたはbranch外でtransportする。
25. mergeは利用者が行う。

## Skill一覧

### 入口と統括

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `development-orchestrator` | task選定から設計、実装、検証、レビュー、Git提出、pre-freeze gate、final attestation boundaryまでを統括する | 親が実行 |
| `codex-delegation-executor` | 実作業の委譲先と実行profileを決める | 親が実行 |
| `sub-agent-task-manager` | sub-agentのscope、model、reasoning、fork、report契約を固定する | 親が実行 |
| `execution-cost-stabilizer` | retry、parallelism、実行コストを安定化する | 親が実行 |
| `feedback-autonomy-boundary-manager` | 自律継続と利用者確認の境界を決める | 親が実行 |
| `skill-authoring-wrapper` | core Skill／runtime wrapperをrepository標準へ揃える | 親が実行 |

### 親非依存core Skill

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `work-context-manager` | authority、scope、target identity、policy、validation、CI、`verification_capability`、write boundaryを解決する | runtime非依存Skillとして実行 |
| `implementation-worker` | initial implementationとreview follow-upを実施する | runtime非依存Skillとして実行 |
| `review-worker` | initial review、fix verification、independent final reviewとattestation条件を返す | runtime非依存Skillとして実行 |
| `report-writer` | evidence-faithfulなreport、簡易PR comment、persistence metadataを生成する | runtime非依存Skillとして実行 |

### 計画と追跡

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `task-breakdown-planner` | issueをtaskとphaseへ分解する | 親が実行 |
| `task-consistency-manager` | task、phase、実scopeを同期する | 親が実行 |
| `progress-sync-manager` | report、tracking、実結果を同期する | 親が実行 |
| `restart-handover-manager` | recorded stateから再開位置を復元する | 親が実行 |
| `handover-memo-writer` | 別chat向けhandover memoを作成する | 親が実行 |

### 設計と実装

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `design-doc-maintainer` | 設計影響と更新対象を判断する | 親が実行 |
| `design-executor` | 決定済み設計変更を編集する | 親が実行 |
| `tdd-executor` | 対象repositoryが要求するtest-first証拠をcore Skill経由で定義する | 親が実行 |
| `implementation-executor` | executorを管理し、`implementation-worker`を呼び出すCodex wrapper | 親が実行 |

### レビューと品質

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `review-enforcer` | reviewer identity、通常review cycle、pre-freeze gate、独立最終review、report-attestation gateを管理するCodex wrapper | 親が実行、reviewはsub-agent |
| `markdown-word-checker` | Markdown lintと表記ルールを検証する | 親が実行 |
| `feedback-coding-standards-enforcer` | coding standardを検証する | 親が実行 |
| `feedback-issue-intake-fallback-manager` | Issue取得失敗時に要件を確保する | 親が実行 |

### Gitとreport

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `git-workflow-manager` | branch、commit、push、PRを統括する | 親が実行 |
| `git-branch-starter` | 作業branchを準備する | 親が実行 |
| `git-commit-manager` | scoped commitを作成する | 親が実行 |
| `git-pr-submitter` | PRを作成または更新する | 親が実行 |
| `git-review-followup-manager` | review findingをimplementation flowへ戻す | 親が実行 |
| `report-output-manager` | report path／persistence／report-attestationを管理し、`report-writer`を呼び出すCodex wrapper | 親が実行 |

### ChatGPT runtime wrapper

| Skill | 役割 | 実行方式 |
| --- | --- | --- |
| `chat-implementation-worker` | ChatGPT上の初回実装とreview follow-upを統括する | 利用者が親としてChatGPT chatで実行 |
| `chat-review-worker` | ChatGPT上のinitial、fix verification、independent final review、report-attestationを統括する | 利用者が親としてChatGPT chatで実行 |
| `chat-report-writer` | ChatGPT上のsource discovery、report永続化、PR commentを統括する | 利用者が親としてChatGPT chatで実行 |
| `chat-handoff-manager` | 独立chat間のlossless typed／raw handoff packetを生成する | ChatGPT wrapperから呼び出す |

## 共通規則

- 対象repositoryのProject Instructionを優先する。
- 解決可能なrepository stateを利用者へ再質問しない。
- CodexSkill repository自身にはTDDを適用しない。
- implementationは自分の変更へreview verdictを出さない。
- reviewerはfindingを実装しない。
- finding identityとsource severityを維持し、severity変更はsource／new severity、理由、承認主体を明示する。
- reviewは詳細reportへ記録する。
- CIは対象current HEAD SHAに紐づくrunだけを使用する。
- 別SHAのrunを代用しない。
- report、tracking、handoffは自己を含む将来のcommit SHAを要求しない。`commit_pending`、technical HEAD、administrative parentを区別する。
- reportとhandoffを混同しない。
- handoffはtyped projectionとversioned raw source payloadでcore Skill outputを欠落なくtransportする。
- unknown、blocked、held、unexplored、失敗結果を消さない。
- core Skillとwrapperは自directory外のshared fileへ依存しない。
- dependency Skillが存在しない場合、wrapperは処理を複製せずmissing dependencyとして停止する。
- end-of-Issue Skill decision、feedback ledger、normal handoff、report、trackingをindependent final review前に確定する。
- pre-freeze処理でrepositoryが変わった場合はnormal reviewへ戻る。
- independent final review後は条件を満たす1回のreport-attestation commit以外のGit commitを作らない。
- attestation後はrepository-writing Skillを呼ばない。
- worker、sub-agent、親agentはmergeしない。

## 保守規則

- Skill追加または責務変更時は本設計書を更新する。
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`を同一内容に保つ。
- ChatGPT Skill package変更時はRelease workflowと`design/chat-worker-skill-design.md`も更新する。
- ChatGPT Project Instruction例を変更する場合は`design/chatgpt-project-instruction-example.md`を更新する。
- review lifecycle変更時は`review-worker`、`review-enforcer`、`chat-review-worker`、`report-writer`、`report-output-manager`、本設計書、専用設計書を同時更新する。
- handoff schema変更時は`chat-handoff-manager`、ChatGPT wrapper、両設計書、Issue／trackingを同期する。
- core Skill dependency変更時はCodex wrapper、ChatGPT wrapper、Release builder、repository validator、両設計書を同時更新する。
- `scripts/verify_skill_repository.py`でactive Markdown link、Skill依存、front matter、symlink、削除済みshared runtime path、hierarchy design同期を検証する。
- workflow trigger変更時はforbidden pathだけの変更でもvalidatorが起動するcoverageを両設計書とPR説明へ同期する。
- 既存設計書の変更時は、構成変更と無関係な節を削除せず、矛盾する箇所だけを置換する。

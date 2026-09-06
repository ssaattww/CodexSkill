# Astraエスカレーションと承認の設計

## 目的と適用範囲

Issue #67に対応し、既存の適応型agent割当へ`gpt-6-astra` / `high`を追加する。Astraは通常の自動選択先ではなく、同じ対象タスクで既存モデルを実行し、問題が発生して継続しても解決が見込めないと判断した場合の、ユーザー承認付きエスカレーション先とする。

本書は[適応型agent割当設計](adaptive-agent-assignment-design.md)の承認ライフサイクルを拡張する。Luna / Terra / Solの通常default、Sol `xhigh/max`の既存承認、reviewer identity、single-reviewer policy、report予約・attestationの所有者は変更しない。

実行時の選定・承認規則の正本は`sub-agent-task-manager`のSkill内referenceとする。他のSkillはこのSkillを呼び出し、承認規則を独自実装しない。

## 根拠とモデル設定

- 要求元: [Issue #67](https://github.com/ssaattww/CodexSkill/issues/67)
- 正式なruntime model ID: `gpt-6-astra`
- このリポジトリで許可するAstraのreasoning effort: `high`のみ
- OpenAIのモデル説明ではcomplex reasoning、coding、computer use等を対象とし、`high`をサポートしている。
- Issueで挙げられたcomputer useや未知のルール把握は、個別タスクでAstraを提案する際の期待効果を説明する観点とする。ベンチマークから当該タスクの解決を保証しない。

2026-09-06確認の公式API標準単価は、短いcontextの入力/出力100万tokenあたりAstraが10/50米ドル、Solが4/20米ドルで、同条件の単価比は2.5倍である。Issue記載の2.4倍は要求者のコスト前提として区別し、固定料金や実行全体の費用比として実装しない。Codex契約、token量、context長、cache、processing tier、tool費用を含む実際の費用は別途確認が必要である。承認要求には比較対象、確認日時、利用可能な費用根拠、不明な費用を記録する。

参照: [Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra)、[API pricing](https://developers.openai.com/api/docs/pricing)、[Codex subagents](https://developers.openai.com/codex/subagents)。

## エスカレーションの前提

親は次を同じtask identityに紐付けて記録する。

1. 対象タスクの安定したID、scope、完了条件。
2. 既存モデルでの実行記録。modelのrequested / applied / observabilityを区別し、実際の実行結果、試行内容、失敗や未解決blockerの証拠を含める。
3. そのまま続けても解決を見込めない具体的理由と、追加の通常調査・scope縮小・既存証拠再利用を検討した結果。
4. Astraで改善を期待する点。例えば、操作結果から未知のUIルールを推定する、既存仮説では説明できない挙動を整理するなど。
5. `gpt-6-astra` / `high`という提案profile、cost notice、承認対象の次の作業単位。

単に高難度、file数が多い、computer useを使う、reviewである、最初のテストが失敗した、というだけではAstraを提案・実行しない。認証不足、接続障害、権限不足、未入手の必須入力など、モデル変更では解消できないblockerをAstraで迂回しない。全ての既存tierを順に試す必要はないが、未実行の試行やprofileを捏造しない。

明示的な「Astraを使う」という指示はprofileの意思表示であり、欠けている既存モデル実行証拠、対象scope、cost notice、承認範囲を補完するものではない。

## 承認単位

承認はモデル利用の許可であり、コード変更、破壊的操作、computer use、ネットワーク、merge、他のagent起動に対する実行権限を増やさない。

| mode | 有効範囲 | 失効 |
| --- | --- | --- |
| `single_turn` | 明示された1 agent・1 task・1回の作業開始または追加依頼 | 対象の開始要求を発行する直前に消費。完了、失敗、中断後の再依頼には再承認 |
| `task_until_completion` | ユーザーが明示した同一task、同一scopeの完了条件までの継続 | 完了、取消、scope拡大、別taskまたは新lifecycleへの移行 |

既定は`single_turn`。タスク完了までの継続利用はユーザーが明示的に選択した場合だけ許可する。曖昧な了承や通常の「続けて」を、未提示の費用・新task・無期限利用への了承と解釈しない。明確に提示済みの1ターン承認要求への直接の肯定は、その要求と対応付けて記録できる。

ここでの1ターンは、親がAstra sub-agentへ1回の作業要求を渡してから、そのagentが結果・失敗・入力要求等を返すまでとする。内部の推論tokenやtool呼び出し1回ごとではない。親の同じ発話中でも、追加作業を渡す`send_input`や実行を再開する操作は別ターンである。状態を読むだけのpoll、wait、既に得られた結果取得、実行を始めないresumeは承認を消費しない。

単一ターンにはboundedな作業と停止条件を設定し、内部で他agentを起動したり、返答後に自動再queueしたりして継続承認を回避しない。

## 状態と実行順序

```text
既存モデルの実行とblocker証拠
  -> Astra適格性の確認
  -> proposed_profile=Astra high / requested=null
  -> 費用・scope・single_turn/task_until_completionを提示
  -> pending（Astraは実行しない）
      |-- reject -> rejected（Astraを除外して再計画）
      `-- approve -> approved
          -> task/scope/profile/role/実行境界を再確認
          -> single_turnなら対象operationへ割当・消費
          -> 実行
          -> exact applied または unverified
          -> 完了/失敗/中断
              |-- single_turnの追加作業 -> 新たな承認要求
              `-- task_until_completion -> 同一scope内だけ継続可能
```

承認の確認と消費は親が直列化する。同じgrantを複数agentや複数operationへ使わない。要求送信後のtimeoutなど、実行が開始されたか不明な場合もsingle-turn grantを再利用しない。実行前のrole検査で停止しただけなら、未消費のgrantはscopeとprofileが変わらない限り保持できる。

承認拒否後にAstraを同じ判断材料だけで再提案し続けない。ユーザーの再検討指示または具体的な新証拠が必要である。拒否によってSol `xhigh/max`が自動承認されることはない。

## task identityと継続

承認をrepository、Issue、PR、branch全体に暗黙拡大しない。accepted task IDとscope identityを記録し、scopeや完了条件が拡大した場合は新しい承認を取得する。同一scopeで通常発生する修正commitだけではtask identityを変えないが、各作業証拠には対象HEADを記録する。

`task_until_completion`は無制限のretry予算ではない。進展がない場合は既存のcost-stabilizerに戻り、blockerを報告する。分割で生まれた別bounded task、並列agent、後続taskへgrantを継承しない。完了後の再openも新lifecycleとして扱う。

handoffの承認記録は証拠であって、新しい親への権限移譲ではない。新sessionでは現在のユーザー指示から権限を再確認する。元のparent context内の継続では、同じgrantと消費台帳を保持する。

## 適用経路と迂回防止

`sub-agent-task-manager`はnew dispatchと`authorization_only`を提供する。後者は既存agentへの追加作業前に承認だけを確認し、agentを作り直さず、task defaultを再適用せず、reportを再予約しない。

次の全経路でAstraの適格性と承認を確認する。

- automatic selection、user override、repository policyからの提案
- explicit/default roleによるprofile上書き
- model availabilityによるsame/higher-tier置換
- full-history forkでの親profile継承
- 既存reviewerのcontinuity reuse、追加依頼、作業を開始するresume
- 失敗後のretryとfallback

Astra利用時はrequestedと事前に確認したplanned runtime profileがともに`gpt-6-astra` / `high`であることを確認する。aliasを用いるruntimeでは、同じモデルへの解決根拠が必要である。未知のroleや継承profileでは`capability_gap`として実行前に停止する。full-history経路でAstra highとscopeを保証できない場合はfresh/partial contextへ再計画するか停止し、継承を承認回避に使わない。

Issue #67の許可はsub-agent利用だけである。Astraのspawnが失敗しても、親の`codex exec`や親モデル切替で代用しない。利用不能ならcapability gapを記録し、非Astraの再計画またはユーザー判断へ戻る。

spawn成功だけで`applied=requested`としない。final profileが観測できなければ`applied: null`とunverified状態を残す。観測したprofileがAstra highから逸脱した場合は違反証拠を残し、追加の作業を投入せず、利用可能な安全な停止手段を使う。承認の取消でも新たな作業投入を止め、進行中の処理の停止可否を事実通り記録する。

## Reviewerとreportの整合

既存Sol `xhigh/max` reviewerの同一lifecycle再利用規則は変更しない。Astra reviewerでは、同じagentを再利用する場合も`single_turn`の再承認または有効な`task_until_completion`を必要とする。

Astraへの変更だけを理由にreviewerを暗黙交換しない。既存reviewerのmodelを変更して同一profileだったと記録することも禁止する。正常なreplacement手続や独立reviewerのidentity制約と両立しない場合は、review lifecycle blockerとして扱う。Astra承認は新しい独立full reviewやreviewer分割への承認ではない。

親がproposal、既存モデル実行証拠、grant ID、task/scope、mode、approval evidence、operationごとの消費・継続記録、失効理由、runtime observabilityを保持する。normal reportではparent-owned `Dispatch profile`に保存し、deferred attestationでは既存の予約・freeze境界を守って親側に保持する。

## 具体的な受け入れ条件

| ID | 入力・操作 | 期待する結果 |
| --- | --- | --- |
| A67-01 | 新規の通常実装タスク | 既存Luna/Terra/Sol defaultを使用し、Astraを自動選択しない |
| A67-02 | 既存モデル未実行の難しいcomputer-useタスク | 難度や用途だけではAstra提案の適格性を満たさない |
| A67-03 | 同一taskの既存モデル実行・未解決理由・期待効果あり | Astra highをproposalとして提示し、承認前はrequested=null・実行なし |
| A67-04 | 承認要求にユーザーが応答しない、またはrepository policyだけがAstraを指定 | pendingのまま実行しない |
| A67-05 | 次の1ターンだけ明示承認 | 対応する1 agent/operationにだけgrantを消費して開始 |
| A67-06 | A67-05の結果取得・poll・wait | 新しい実行や承認消費をしない |
| A67-07 | A67-05後にsend_inputで追加調査、retry、作業再開 | 新たな承認前には開始しない |
| A67-08 | 1回の要求がtimeoutで開始不明、別要求が同じgrantを利用 | 元grantを再使用せず、二重投入しない |
| A67-09 | 明示的task_until_completion承認、同一scopeの次ターン | grant有効性を確認して継続し、毎回の承認確認質問は不要 |
| A67-10 | task完了、取消、scope拡大、別task、並列agent、新session | 元grantを利用しない。必要な新承認を取得 |
| A67-11 | 拒否、または費用根拠不明 | 拒否ではAstraを除外。不明費用を既知と偽らず承認要求へ明記 |
| A67-12 | Sol high requestedをroleがAstra highへ変更 | 同じ適格性・承認gateを再適用し、roleだけでは実行しない |
| A67-13 | roleがAstra xhigh、未知のprofile、full-historyで不明の親profile | high固定や事前安全確認を満たさず実行しない |
| A67-14 | 通常モデルが利用不能でAstraだけ利用可能 | 自動的なhigher-tier fallbackをしない |
| A67-15 | Astra spawn拒否 | 親のcodex execに迂回せずcapability gapを記録 |
| A67-16 | Astra reviewerのfix verificationやbounded closure | identityを維持し、次ターン承認を確認。report予約を増やさない |
| A67-17 | 承認済みSol xhigh reviewerの既存continuity reuse | 既存の再利用規則を維持し、Astra用承認を要求しない |
| A67-18 | spawn成功だがfinal profile非公開 | applied=nullとunverifiedを保存し、適用成功と捏造しない |
| A67-19 | 承認済みAstraのactual profileが不一致 | 不一致を記録し、追加投入せず安全に停止・再計画 |
| A67-20 | 認証不足だけがblocker、または一般的なPR作成指示 | Astra適格性やモデル費用承認とは扱わない |

## 検証と非対象

CodexSkill自身の保守はnon-TDD。上記はSkill contractを確認する具体例であり、実際のAstra呼び出し成功を表すものではない。既存repository validator、YAML例の構文確認、配布ZIP生成・構造確認、current PR HEADと一致するCI、変更contractのシナリオ照合で検証する。

新規の有料モデル実行、Codex runtimeへの強制機構追加、料金API、review lifecycle再設計、TDD導入、診断artifact workflowの新設、mergeは本変更の対象外。Skillは親が守る運用contractであり、runtimeが提供しない強制停止や権限管理を実装済みとは表現しない。

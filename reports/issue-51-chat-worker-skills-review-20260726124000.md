# Issue #51 ChatGPT Chat Worker Skill コードレビュー報告書

## レビュー情報

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- Pull Request: #52
- Review mode: initial review + fix verification
- Branch: `agent/issue-51-chat-worker-skills`
- Base: `main`
- 対象実装HEAD: `15b226e629330b466443865fc56c0d25376bd57b`
- 判定: Pass with held concerns
- Merge: 実施しない

## レビュー目的

次を確認した。

1. 利用者が親として複数のChatGPT chatを起動する前提になっているか。
2. Workerが別workerを起動せず、単一chat内で完結するか。
3. implementation、review、reportの責務とwrite boundaryが分離されているか。
4. chat間handoffだけで次chatが再開できるか。
5. 過剰reviewを避けつつ、初回reviewの抜け漏れを減らすlifecycleになっているか。
6. 既存Codex向けSkillを変更していないか。
7. test-firstとfailure diagnosticsが成立しているか。
8. 最終判定に対象branch HEAD SHA固有のCIだけを使用しているか。

## 確認した変更ファイル

- `.github/workflows/chat-worker-skill-contract.yml`
- `design/chat-worker-skill-design.md`
- `reports/issue-51-chat-worker-skills-implementation-20260726123510.md`
- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`
- `skills/design/chat-worker-skill-design.md`
- `tests/test_chat_worker_skills_contract.py`

## 確認した依存先と既存契約

- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
- `skills/implementation-executor/SKILL.md`
- `skills/review-enforcer/SKILL.md`
- `skills/report-output-manager/SKILL.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `tasks/tasks-status.md`
- Issue #51
- PR #52

既存Codex向けSkillと既存hierarchyは変更されていない。

## Coverage

| 領域 | 状態 | 確認内容 |
| --- | --- | --- |
| Requirements | 確認済み・指摘なし | Issue #51と利用者の「利用者が親」「Markdown配置可能」「別chatは自動起動不可」という前提を照合した |
| Scope | 確認済み・指摘なし | standalone worker 3件、shared contract、専用設計、test、workflow、reportだけを変更している |
| Worker separation | 確認済み・指摘なし | implementation、review、reportの禁止事項とwrite対象が分離されている |
| Handoff completeness | 確認済み・指摘なし | repository、HEAD、scope、evidence、finding、report、unknown、next chatを保持する |
| Authorization boundary | 確認済み・指摘なし | current executionとnext chat proposalを分離し、前worker権限の自動継承を禁止した |
| Review lifecycle | 確認済み・指摘なし | initial、fix verification、cold final、unstableの停止条件が定義されている |
| Test quality | 確認済み・指摘なし | file存在、frontmatter、standalone性、role marker、shared field、design同期をcontract testで固定している |
| CI and diagnostics | 確認済み・指摘なし | branch HEADをcheckoutしてactual SHAを検証し、failure artifactへ必要情報を保存する |
| Existing Codex compatibility | 確認済み・指摘なし | 既存Codex Skillを変更せず、専用designへ分離した |
| Performance / runtime | 対象外 | Markdown Skill contractと小規模Python contract testであり、製品runtime処理はない |
| Operational trial | 保留 | 別々の実ChatGPT chatへbundleを配置したend-to-end運用試験は未実施 |

## レビュー中に確認し、修正した事項

### High 1: PR eventのmerge refを検証していた

#### 問題

初期workflowはPR eventの既定checkoutを使用していたため、branch HEADではなくGitHub生成のmerge refをtestしていた。

利用者指示では、自分のbranch HEAD SHAに紐づくworkflow runだけをCI判定へ使用する必要がある。

#### 修正

- `TARGET_HEAD_SHA`をPR head SHAまたはpush SHAから決定
- `actions/checkout`へ対象SHAを明示
- `git rev-parse HEAD`と`TARGET_HEAD_SHA`の一致を独立stepで検証

#### 結果

解消済み。

### High 2: implementation workerとreport責務の境界が曖昧だった

#### 問題

初期implementation workerは、利用者が明示すればnarrative implementation reportも作成できる表現だった。

「実装だけのSkill」と「レポートだけのSkill」を切り出す目的に対して、implementation workerの責務が広すぎた。

#### 修正

- implementation workerはcode、test、validation evidence、構造化handoffだけを所有
- narrative reportを明示的に禁止
- implementation reportは`chat-report-writer`へ渡す
- review verdictもimplementation workerの対象外とした

#### 結果

解消済み。

### Medium 3: handoffに許可操作とreport outputの構造がなかった

#### 問題

初期handoffは作業結果を保持できたが、workerが実行してよい操作とpathを表現できなかった。また、report writerが作成したpath、PR comment、source packet、outcomeを構造化できなかった。

#### 修正

- `authorized_actions`
- `write_boundary`
- `report.report_type`
- `report.outcome`
- `report.source_packets`
- `report.paths`
- `report.pr_comments`

を追加した。

#### 結果

解消済み。

### Medium 4: 前workerの権限を次chatが継承できるように読めた

#### 問題

Top-levelの`authorized_actions`と`write_boundary`が、producerの実行権限か、次workerへの権限付与かが曖昧だった。

Source packetをそのまま次chatへ渡すと、前workerのwrite権限を次workerが引き継ぐか、逆に必要なreport権限を持たない可能性がある。

#### TDD

- Test commit: `092629cffe0334fbd84c97e20af11e72ec8df0c8`
- Workflow Run: `30186468150`
- Result: failure
- Diagnostic artifact:
  - ID: `8627185141`
  - Name: `chat-worker-skill-contract-diagnostics-30186468150-1`

#### 修正

- Top-level権限はcurrent executionの記録と定義
- `next_chat_input.requested_authorized_actions`を追加
- `next_chat_input.requested_write_boundary`を追加
- requested fieldは権限付与ではなくworkerから利用者への提案と定義
- 利用者が確認して次chatへ新しいtop-level権限として付与
- 次chatは前workerの権限を自動継承しない
- 権限が新規付与されない場合はwrite、commit、push、PR操作を禁止

#### 結果

解消済み。

## TDDとCI証跡

### 初回Red

- HEAD: `f5b2107dfdce2e9c66944f1bf5d313c0ea9e341d`
- Run: `30185865727`
- Result: failure
- Artifact: `8626998950`

### 初回Green

- HEAD: `1a189b243fe215eaa0ddc3259a4c6ec599464ba1`
- Run: `30186081623`
- Result: success

### Role boundary強化Red

- HEAD: `32e55938644acf7530cdfd4365ed7e2a9d6695e0`
- Run: `30186176348`
- Result: failure
- Artifact: `8627103321`

### Branch HEAD workflow Green

- HEAD: `b626eab469bd46e5350991b69c5790c41e9b4edc`
- Run: `30186397394`
- Result: success

### Authorization non-inheritance Red

- HEAD: `092629cffe0334fbd84c97e20af11e72ec8df0c8`
- Run: `30186468150`
- Result: failure
- Artifact: `8627185141`

### Review対象HEAD Green

- HEAD: `15b226e629330b466443865fc56c0d25376bd57b`
- Run: `30186500197`
- Result: success
- Job: `contract`
- `Checkout target branch HEAD`: success
- `Verify checked out HEAD`: success
- `Run chat worker skill contract`: success

このreview report追加後の最終HEAD runはPR commentへ記録する。

## 指摘事項

### Blocking / High

- 指摘なし

### Medium

- 指摘なし

### Low

- 指摘なし

## Held concerns

### 実ChatGPT環境でのend-to-end operational trial

- Status: held
- Reason: 今回はrepository上のSkill contractとCIまでをscopeとし、複数の実ChatGPT chatへbundleを配置して一連の実装、review、reportを完走する試験は実施していない
- Remaining risk: handoff記入負荷、実際のSkill導入経路、chatごとのconnector差異が運用時に判明する可能性がある
- Verdict impact: repository contractのPassを妨げない。初回実運用で確認し、反復する問題だけを後続Issue化する

### Machine-readable schema

- Status: held
- Reason: 今回はMarkdown上のcanonical packetとPython contract testを採用した
- Remaining risk: packet fieldの値型やenumを完全には機械検証しない
- Verdict impact: 初期chat運用には支障しない。自動tool連携が必要になった時点でJSON Schema化を検討する

## Scope protection

- `main`に対してbehind 0を確認した
- PR #50のbranchまたは未merge変更を取り込んでいない
- 既存Codex向けSkillを変更していない
- 他Issueのtrackingを変更していない
- mergeしていない

## 最終判定

- Verdict: Pass with held concerns
- Blocking / High findings: 0
- Required follow-up before review request: なし
- Merge: 実施しない
- Remaining action:
  - review report追加後の最終HEADに紐づくCIを確認する
  - PR本文を最終状態へ更新する
  - 詳細reportとは別に簡易PR commentを投稿する

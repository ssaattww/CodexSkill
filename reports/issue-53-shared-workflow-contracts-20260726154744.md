> [!WARNING]
> このreportは、2026-07-26時点の旧`shared/workflow/`方式と旧3 Skill配布物を記録した**historical evidence**である。
> 2026-07-29のsuperseding decisionにより、current architectureは親非依存core Skill 4件、ChatGPT runtime wrapper 4件、Skill外shared runtime依存なしへ変更された。
> current implementation／review-follow-up evidenceは`reports/issue-53-core-skill-wrapper-review-followup-20260729174338.md`を参照すること。
> 本文中の旧file、旧HEAD、旧artifact、旧完了条件をcurrent stateとして使用しないこと。以下の本文は歴史的証拠を保持するため変更しない。

# Issue #53 Codex／ChatGPT Skill共通契約化 実装レポート

## メタデータ

- 対象Issue: #53 `Codex／ChatGPT Skillの共通契約化とChatGPT配布ZIPの自動収集`
- 対象PR: #54 `Issue #53: Codex／ChatGPT Skillを共通契約へ統合する`
- Branch: `agent/issue-53-shared-workflow-contracts`
- Base: `main`
- 実装・artifact検証対象HEAD: `cbe0004d133ec71570c76bdcb47122fab963d86a`
- 作成日時: 2026-07-26 15:47 JST
- Report mode: implementation report
- TDD: `not applicable`
- Merge: 未実施

このreportをrepositoryへ保存するcommitと、その後のtracking・設計整合commitはbranch HEADを更新する。最終current HEAD固有のworkflow runはPR本文およびPR commentで記録する。このreportは、下記HEADで実施した実装・artifact検証の証拠を記録する。

## 目的

Codex向けSkillとChatGPT向けSkillに重複していた実装、レビュー、レポート、current HEAD、CI evidence、merge boundaryの規則をruntime非依存の共通contractへ集約し、各runtime固有Skillをadapterへ縮小する。

ChatGPT向けReleaseでは、固定された3 Skillだけを列挙する方式を廃止し、全ChatGPT SkillとChatGPT runtime依存物を単一ZIPへ自動収集する。

## 対象範囲

- runtime非依存の共通workflow contract作成
- Codex向けimplementation、review、report、orchestration、TDD applicability、Skill authoring adapter更新
- ChatGPT向けimplementation、review、report adapter更新
- ChatGPT handoff schemaの一般化と後方互換
- Project Instruction例の独立reference化
- ChatGPT配布ZIP builder作成
- GitHub ActionsによるPR validationとmain反映後Release更新
- hierarchy designとChatGPT worker design更新
- CodexSkill repository自身の非TDD方針の明文化

## 対象外

- PRのmerge
- PR branchからのGitHub Release更新
- ChatGPT UIへの実際のSkill upload
- main反映後のrelease job実行
- 本実装chatによる独立最終レビュー
- 対象外Skillの全面的な再設計

## 共通化したcontract

`shared/workflow/`へ次を追加した。

- `common-work-contract.md`
  - authority、state discovery、scope、current HEAD、CI evidence、report、handoff、merge boundary
- `implementation-contract.md`
  - initial implementation、review follow-up、validation、implementation evidence
- `review-contract.md`
  - normal review cycle、fix verification、independent final review、finding、coverage、verdict
- `report-contract.md`
  - report mode、source selection、evidence fidelity、structure、write boundary

Codex側とChatGPT側は上記contractを参照し、runtime固有のexecution、delegation、permission、persistence、handoffだけを保持するadapterへ変更した。

## ChatGPT adapter

次の3 Skillを共通contract参照型adapterへ変更した。

- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`

通常review cycleではinitial reviewとfix verificationを同じnormal review chatで継続し、independent final reviewだけをimplementation、fix、normal reviewに参加していないfresh chatで行う。

各Skillに存在した`references/handoff-contract.md`の手動copy 3件は削除した。repository上の正本は`shared/chat-worker/handoff-contract.md`だけとし、Release build時に各Skillへ必要なdependencyを生成する。

## Codex adapter

次を共通contract参照型adapterへ変更した。

- `skills/implementation-executor/SKILL.md`
- `skills/review-enforcer/SKILL.md`
- `skills/report-output-manager/SKILL.md`
- `skills/development-orchestrator/SKILL.md`
- `skills/tdd-executor/SKILL.md`
- `skills/skill-authoring-wrapper/SKILL.md`

`development-orchestrator`と`tdd-executor`にはTDD applicability gateを追加した。対象repositoryが明示的にTDDを要求する場合だけ`tdd-executor`を使用する。

CodexSkill repository自身についてはroot `AGENTS.md`へ非TDD方針を追加した。

- `tdd-executor`を起動しない
- Red/Green evidence作成を目的とするtestまたはworkflowを追加しない
- lint、schema validation、syntax、build、package、structure、design/contract整合を通常検証として使用する

## Handoff contract

`shared/chat-worker/handoff-contract.md`をschema version 2へ更新した。

- producer Skill名とnext Skill名を固定3 Skillへ限定しない
- canonical review modeを`independent_final_review`とする
- version 1 packetの読み取りを継続する
- version 1の`cold_final_review`を`independent_final_review`へ正規化する
- 未対応の将来schemaは推測せずblockedまたはincompleteとする

## ChatGPT bundle builder

`scripts/build_chatgpt_worker_skills.py`を追加した。

処理内容:

1. `skills/chat-*/SKILL.md`を全件検出する
2. directory名とfront matter `name`の一致を確認する
3. 各Skill directory内の全fileをcopyする
4. Skill sourceとdependencyのsymlinkを拒否する
5. Markdown linkから`shared/` dependencyを再帰解決する
6. dependencyを各Skillの`references/shared/`へcopyする
7. repository相対linkをSkill内相対linkへ書き換える
8. packaged linkがSkill外へ出ないことを確認する
9. `shared/chat-worker/`配下の全runtime fileが少なくとも1つのSkillへ同梱されることを確認する
10. 未同梱のChatGPT runtime fileがあればbuildを失敗させる
11. root直下に全ChatGPT Skill directoryだけを持つ再現可能な単一ZIPを生成する

## Release workflow

`.github/workflows/release-chatgpt-worker-skills.yml`を更新した。

### PR build

- `contents: read`のみ
- checkout credentialを保持しない
- `pull_request.head.sha`をcheckoutし、synthetic merge refを検証対象にしない
- artifact名にも実PR HEAD SHAを使用する
- bundle buildと構造検証を実行する
- artifactを保存する
- Releaseとtagを更新しない

### main push release

- read-only build jobの成功を要求する
- build済みartifactを別release jobへ渡す
- release jobだけに`contents: write`を付与する
- rolling tagとRelease assetをmain反映後HEADへ更新する

main pushのrelease jobはPR上では実行条件を満たさないため、未実施である。

## 通常検証

### TDD

利用者からCodexSkill repositoryへTDDを適用しない明示指示があるため、TDDは`not applicable`とした。

Red/Green用test、変更専用contract test、TDD用workflowは追加していない。

### GitHub Actions

- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `30191605925`
- Run number: `26`
- Target HEAD: `cbe0004d133ec71570c76bdcb47122fab963d86a`
- Status: completed
- Conclusion: success

### Artifact

- Artifact ID: `8628733240`
- Name: `chatgpt-worker-skills-cbe0004d133ec71570c76bdcb47122fab963d86a`
- Digest: `sha256:1811aec09a87f83781f8630aa8210e19fdc3dff6c37a697900ee9de32d175ea9`
- Expired: false

artifact outer ZIPから`chatgpt-worker-skills.zip`を取り出し、次を確認した。

- ZIP root directoryは次の3件だけである
  - `chat-implementation-worker`
  - `chat-review-worker`
  - `chat-report-writer`
- 各Skillに`SKILL.md`が存在する
- implementation Skillにcommon、implementation、report、handoff、Project Instruction例が含まれる
- review Skillにcommon、review、report、handoffが含まれる
- report Skillにcommon、report、handoffが含まれる
- `shared/chat-worker/`の2 fileが配布対象へ含まれる
- package内に未解決の`../../shared/` linkが存在しない
- `unzip -t`でcompressed data errorがない
- ZIP rootにinstallable Skill以外のfileまたはdirectoryが存在しない

## 実装中に検出して修正した問題

1. PR validation jobにも`contents: write`が付与されていた
   - read-only build jobとmain限定write release jobへ分離した
2. `development-orchestrator`がTDDを無条件に呼ぶ既存契約だった
   - target repository policyによるapplicability gateへ変更した
3. 将来`shared/chat-worker/`へ追加したfileがReleaseから黙って漏れる可能性があった
   - 未参照・未同梱fileがあればbuilderを失敗させるよう変更した
4. handoff schema version 2のみを受理すると既存packetを読めなくなる可能性があった
   - version 1読み取り互換とmode正規化を追加した
5. PR eventの`${{ github.sha }}`がsynthetic merge SHAを指していた
   - checkoutとartifact identityを`pull_request.head.sha`へ変更した
6. 変更したMarkdown fileの一部に末尾改行がなかった
   - 内容を変更せず末尾改行を正規化した

## 設計・追跡

更新対象:

- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`
- `tasks/tasks-status.md`
- `tasks/phases-status.md`

2つのhierarchy designは同一内容として維持する。

## 未実施・残リスク

- main push限定のrelease jobはPR上では未実施である
- GitHub Release assetの実置換はmerge後まで未確認である
- 生成ZIPをChatGPT UIへuploadする実機確認は未実施である
- 独立したfresh reviewerによる最終レビューは未実施である
- report、tracking、最終設計整合commit後のcurrent HEAD固有workflowを再確認する必要がある

上記のためPR #54はDraftのまま維持する。

## 次のaction

1. tracking、report、設計整合commit後のcurrent HEADに紐づくbundle workflowとartifactを確認する
2. implementation、normal review、review fixに参加していないfresh reviewerがindependent final reviewを実施する
3. reviewで修正が発生した場合はnormal fix verification後、新しいHEADでindependent final reviewをやり直す
4. 利用者がmergeを判断する

## Merge boundary

mergeは実施していない。merge判断と実行は利用者が行う。

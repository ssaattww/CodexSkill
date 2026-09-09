# PR #68 初回レビュー

## 判定と対象

- 判定: `pass_with_held`。必須修正0件、非blockingの記述不整合1件（low）。
- Review mode: `initial_review`。独立最終レビューやmerge承認ではない。
- Reviewer identity: `chatgpt-pr68-normal-review-20260906`。
- 日付: 2026-09-06。
- Repository / Issue / PR: `ssaattww/CodexSkill` / #67 / #68。
- Branch: `feat/issue-67-astra-approval`。
- Base: `main` / `6507727986329e34e69da3680a00824eb1fbfe13`。
- Reviewed implementation HEAD: `8d3f96a0ec5f01247c4092f7bb0f690168ba627e`。
- Review range: `6507727986329e34e69da3680a00824eb1fbfe13...8d3f96a0ec5f01247c4092f7bb0f690168ba627e`。
- 開始時とreport保存直前にPR metadataを再取得し、HEAD不変を確認した。

本レビューは上記HEADの全15変更file、関連Skill、要求、設計、実装report、handoff、追跡表、同一HEADのCIを対象とした。このchatは実装・修正をしていない。normal reviewerとして初回レビューを行い、別reviewerを起動していない。以前の会話の要約は提供されているため、会話情報の完全な非継承を独立性の根拠にはしない。

技術判定は上記HEADに限定する。本reportと別handoffの保存は通常レビュー証跡の追加であり、independent-final report attestationではない。保存後のSHA、差分確認、同じ新HEADのCIはPRコメントへ記録する。将来の自己commit SHAを捏造せず、生成時の保存状態は`commit_pending`とする。後続HEADへ本判定を自動継承しない。

## 要求・権限・非対象

要求元は[Issue #67](https://github.com/ssaattww/CodexSkill/issues/67)。同じtaskで既存モデルを実行し、問題と継続困難の具体的証拠がある場合だけ、ユーザー承認後にAstra highをsub-agentとして使う。既定はターン単位、明示オプションはtask完了までの承認である。

Project Instruction、root `AGENTS.md`、アップロードされた`chat-review-worker` → `work-context-manager` → `review-worker` → `report-writer` → `chat-handoff-manager`の責務を適用した。GitHubの参照・保存・PR操作はconnectorで行う。許可された書込範囲は本レビューのreport、handoff、PRレビューコメントであり、Skill・設計・tracking・workflowの修正、モデル課金実行、mergeは行わない。

CodexSkill保守はnon-TDD。開始時に既存workflowを確認した。成果物は配布ZIPで、テスト結果・stdout・stderrをまとめる失敗診断bundleではない。RevMem向けのTDD・診断artifact workflow追加方針は本repositoryには適用せず、不備として指摘しない。

## 指摘

### PR68-R1-001 — task-wide grantにも複数operationへの使用禁止を適用する設計文

- Severity: `low`。
- Origin: `introduced_by_change`。
- Disposition: 非blocking保留。修正推奨であり、必須修正には数えない。
- Location: [`design/astra-escalation-design.md:71`](https://github.com/ssaattww/CodexSkill/blob/8d3f96a0ec5f01247c4092f7bb0f690168ba627e/design/astra-escalation-design.md#L71)。
- Description: 「同じgrantを複数agentや複数operationへ使わない」が承認modeの限定なしで記載されている。同書の`task_until_completion`とA67-09は、同一task/scopeの複数operationを同じ有効grantで継続する設計なので、文字どおりには両立しない。
- Example: task完了まで明示承認したgrant Gでspawnした後、未完了の同一task・同一agentへ追加調査を送る。A67-09と正本referenceではGの有効性確認後に継続できるが、71行目だけを適用すると新grantが必要になる。
- Impact: 設計を読む人や後続の保守で、不要な再承認またはtask-wide利用の拒否を導く可能性がある。実際に未承認のAstra呼出しが発生した、または現在の正本Skillがこの誤動作を指示している、という指摘ではない。
- Evidence: 正本[`references/astra-escalation.md`](https://github.com/ssaattww/CodexSkill/blob/8d3f96a0ec5f01247c4092f7bb0f690168ba627e/skills/sub-agent-task-manager/references/astra-escalation.md)の`Authorization modes and turn boundary`とoperation gate step 5は、single-turnの消費とtask-wideの操作記録を区別する。設計書自身も実行contractの正本をこのreferenceと指定している。このため実行contractのblocking defectとは扱わない。
- Required action / resolution: 記述を整合させる場合は、複数operationへの再使用禁止を`single_turn`に限定し、`task_until_completion`は同一task/scope/agentの有効期間内で操作ごとに検証して利用可能と明記する。別agentへのgrant転用は禁止したままとする。reviewerによる本文修正は行っていない。
- Owner: PR実装担当。修正する場合は、single-turn再使用拒否、task-wide同一agentでの継続許可、別agentへの転用拒否の3ケースを併せて照合する。

Severityの変更・erratumはない。上記以外の確定指摘は、このレビュー範囲では得られなかった。

## 必須観点のcoverage

| 観点 | Disposition | 確認内容 |
| --- | --- | --- |
| 要求・設計準拠 | checked_finding | Issue67とA67-01〜20を照合。設計文の非blocking不整合PR68-R1-001 |
| 正しさ・境界条件 | checked_no_finding | 提案前適格性、承認前requested未設定、ターン定義、送信前消費、timeout・再試行、失効・撤回を追跡 |
| scope・無関係な変更 | checked_no_finding | Astra追加へ限定。tasks差分は日付とT-004の追加で、他task履歴を変更しない |
| 全変更file・直接影響先 | checked_no_finding | 下記15fileと実行・再開・コスト・report・validator・workflowの接点を確認 |
| API・data・config・workflow・互換 | checked_no_finding | dispatch schema v4のAstra拡張、既存Sol continuity、role/fork/availability、配布集合不変を確認 |
| エラー・失敗診断 | checked_no_finding | spawn拒否・開始不明・profile不一致を成功にしない。CIは成功。診断bundle未追加は適用境界どおり |
| 権限・機密 | checked_no_finding | 承認をwrite/network/merge権限に転用しない。別task/agent/parentへgrant転用禁止。変更内にcredentialを確認していない |
| 検証の妥当性 | checked_no_finding | 構造検証と本文シナリオ照合の範囲を確認。実モデル動作テストと混同しない |
| current-HEAD CI | checked_no_finding | run/job/artifactのhead_shaがreviewed HEADと一致し、build成功 |
| report・tracking・文書の正確性 | checked_finding | PR68-R1-001。旧reportの生成元SHAと最終PR SHAは明示的に区別されている |
| regression・保守性 | checked_no_finding | gateの所有者をtask managerへ集約。呼出し側が承認を独自発行せず、reviewer/report予約を維持 |

## A67受け入れケースの照合

以下は本文からの静的な契約照合であり、Astraを20回起動したテストやruntime強制機構の証明ではない。

| ID | 確認結果 |
| --- | --- |
| A67-01 | 通常floor/defaultはLuna/Terra/Sol。Astraを自動選定しない |
| A67-02 | 既存モデルの実行証拠なしでは、難度やcomputer useだけで適格としない |
| A67-03 | 同一taskの試行・blocker・期待効果からproposalを作り、承認前はAstra requested/dispatchなし |
| A67-04 | 無応答、repository policy、他taskの承認だけでは実行しない |
| A67-05 | single-turn grantを1 agent/operationへ送信直前に消費 |
| A67-06 | poll/wait/既存結果取得は新しい作業ではない |
| A67-07 | send_input/retry/work-starting resumeは新たなsingle-turn承認が必要 |
| A67-08 | 拒否・timeout・開始不明でも送信済みsingle-turn grantは再使用しない |
| A67-09 | 正本は有効なtask-wide grantで同一scopeを継続可能。設計71行目のみPR68-R1-001 |
| A67-10 | 完了・取消・scope拡大・別task/agent/session・再openでは元grantを利用しない |
| A67-11 | 拒否時はAstraを除外し、費用不明は不明と開示。Solの別承認を捏造しない |
| A67-12 | role/default roleがSol等をAstraへ変更する場合も適格性・承認を再確認 |
| A67-13 | high以外・安全に解決できないrole/継承profileでは開始しない |
| A67-14 | 通常モデル利用不能でもAstraを自動higher-tier fallbackにしない |
| A67-15 | Astra spawn拒否を親codex execや親model切替へ迂回しない |
| A67-16 | 既存Astra reviewerへの作業はauthorization_only。identityとreport予約を維持 |
| A67-17 | 既存の承認済みSol xhigh/max reviewerへAstra固有の再承認を課さない |
| A67-18 | spawn成功だけではexact appliedを推測せず、非公開はapplied:null |
| A67-19 | 観測profile不一致は記録し、追加投入停止・利用可能な安全な中断・再計画 |
| A67-20 | 認証や入力不足などモデル変更で解決しないblocker、一般的PR作成指示を承認にしない |

追加で、aliasの同一モデル解決根拠、明示モデルpinの保持、役割によるeffort上書き、unknown既存profile、task分割時のgrant非継承、single-turn消費と呼出結果の分離、取消時のin-flight停止可否、deferred attestation中の証跡保持、pending continuationを実行済みと記録しないことを照合した。正本はunknownなAstra露出をcapability gapにする。単にfinal metadataが非公開というだけで、既知SolをAstra不明と扱う規則にはしていない。

## 確認したfile

| 変更file | 主な確認対象 |
| --- | --- |
| design/adaptive-agent-assignment-design.md | 既存選定、承認、role、fork、continuityとの整合 |
| design/astra-escalation-design.md | 要求、状態遷移、scope、A67-01〜20 |
| design/skill-hierarchy-design.md | gate所有者、呼出し関係、core/ChatGPT配布境界 |
| skills/design/skill-hierarchy-design.md | 正本と同じblob a376c226fd7e547bb541e327af3abad0e2b52173 |
| skills/sub-agent-task-manager/SKILL.md | new_dispatchとauthorization_only、親所有の承認・証跡 |
| skills/sub-agent-task-manager/references/agent-profile-selection.md | 通常floor、Sol承認、Astra適格性、schema互換 |
| skills/sub-agent-task-manager/references/astra-escalation.md | 承認ライフサイクル全体の正本 |
| skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md | 実tool引数、role、full-history、availability、fallback |
| skills/codex-delegation-executor/SKILL.md | 委譲・分割時のtask境界と親実行への迂回禁止 |
| skills/development-orchestrator/SKILL.md | 上位flowのapproval/capability stopと次task/handoff |
| skills/review-enforcer/SKILL.md | reviewer continuity、operation承認、独立reviewとreport予約 |
| skills/report-output-manager/references/sub-agent-report-template.md | eligibility/cost/grant/usage/historyの親所有欄 |
| tasks/tasks-status.md | T-004の具体的終了条件、旧HEAD検証の非転用 |
| reports/issue-67-astra-implementation-20260906.md | 実施/未実施、manual照合、CI snapshotの区別 |
| reports/handoffs/issue-67-pr68-implementation-20260906.yaml | 569行全体、typed projection、raw source payload、権限非継承 |

直接参照した周辺file: `AGENTS.md`、`.github/workflows/release-chatgpt-worker-skills.yml`、`scripts/verify_skill_repository.py`、`skills/execution-cost-stabilizer/SKILL.md`、`skills/restart-handover-manager/SKILL.md`、`skills/report-output-manager/SKILL.md`。アップロードされた8-Skill bundleのうち本review flowに必要なwrapper/coreも読んだ。

GitHub検索の`send_input`は結果なしだったが、default branch検索の不一致を「対象branchに存在しない」という証拠には採用していない。対象fileは固定SHAで直接取得した。

## CI・検証証拠

- Workflow: `.github/workflows/release-chatgpt-worker-skills.yml`。
- Run: [34023404043](https://github.com/ssaattww/CodexSkill/actions/runs/34023404043)、attempt 1、`pull_request`、`completed / success`。
- Run head_sha: `8d3f96a0ec5f01247c4092f7bb0f690168ba627e`。
- Build job: [101460012763](https://github.com/ssaattww/CodexSkill/actions/runs/34023404043/job/101460012763)、同一head_sha、success。
- 対象HEAD checkout、repository validator、ZIP build/検証、artifact uploadの各stepがsuccess。publish/release 3 jobsはPR条件によりskipped。
- Artifact: `9986258020` / `chatgpt-worker-skills-34023404043`、18,678 bytes、取得metadata上expired=false、workflow_run.head_shaも一致。
- Digest: `sha256:de13d29d04cbd1428fe08fb9ce7cc0bb94c0a37d608cf8b06fbab93029c0e77c`。

| 検証 | 結果・限界 |
| --- | --- |
| python3 scripts/verify_skill_repository.py | 同一HEADのCI step success。実装を読み、Skill名・依存・active相対link・symlink・削除済み構造・階層ミラーの検査と確認 |
| python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip | 同一HEADのCI build step success。reviewerのlocal再実行ではない |
| python3 -m zipfile -l chatgpt-worker-skills.zip | 上記workflow stepに含まれsuccess |
| artifact | metadataと保存stepを確認。binaryをdownload・展開したとは記録しない |
| 全差分・A67本文照合 | 本reviewで実施。モデル動作テストではない |
| full local repository validation / git diff --check | 本reviewでは未実施。全repositoryをlocal checkoutしていない |
| Astra実行・利用者runtime | 未実施。課金実行やsub-agent起動をしていない |
| Markdown lint / skill-creator validator | reviewer側では未実施。既存reportの未実施を成功へ置換しない |

[公式Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra)と[公式Sol model](https://developers.openai.com/api/docs/models/gpt-5.6-sol)、[model比較](https://developers.openai.com/api/docs/models/compare)を照合し、Astra high対応、入力/出力100万tokenあたり10/50米ドル、Solの現行promotion 4/20米ドルを確認した。モデルページはSol promotionの期限条件も説明する。pricing一覧には旧料金の取得結果もあったため、それだけでPRの料金を誤りとは判定していない。現行モデル資料はPRの同条件2.5倍という計算を裏付けるが、利用者のCodex実費は確認できていない。承認時の再確認と費用不明の開示が正本にあるため、固定倍率の実費保証として扱われていない。

## 保留・未探索・残るリスク

- Held H1: PR68-R1-001の設計文整合。OwnerはPR実装担当。正本のmode別規則が明確なため非blocking。
- Unexplored U1: 利用者環境の実モデルavailability、role設定、profile観測、取消時の停止能力。Ownerはその環境で実行する利用者/実装担当。未承認の課金実行をせず、本PRもruntime強制機構を非対象としているため今回の静的review verdictを妨げない。ただし運用成功を証明したわけではない。
- Unknown: 実際の契約・usage・token量を含む総費用、非公開runtime内部挙動。
- 本reviewではCodex runtime本体を実行・検証していない。Skill契約をruntimeレベルの安全性証明として扱わない。
- 独立最終reviewは未実施。本normal reviewと後続のreport/handoff追加を、独立最終reviewのpassing attestationへ読み替えない。

## 次の扱い・保存境界

低優先度の文言修正を行う場合は、実装担当がPR68-R1-001のIDを保持して修正し、変更HEADを本normal review chatで確認する。本reviewerは修正を実装しない。修正しない場合も、この保留判断と実環境未確認の限界を残す。

本reportとは別に`reports/handoffs/issue-67-pr68-normal-review-20260906.yaml`へschema version 3のhandoffを保存する。context、review-worker出力、report-writerのcomplete_bodyを省略せず保持する。保存後の新HEADはconnectorで再取得し、そのHEADのCIだけをPRコメントへ記録する。旧runを新HEADの証拠には代用しない。mergeは利用者が行う。

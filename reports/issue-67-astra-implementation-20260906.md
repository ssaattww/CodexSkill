# Issue #67 Astra承認付きエスカレーション実装レポート

## 対象と状態

- 日付: 2026-09-06
- Repository: `ssaattww/CodexSkill`
- Issue: [#67](https://github.com/ssaattww/CodexSkill/issues/67)
- PR: [#68](https://github.com/ssaattww/CodexSkill/pull/68)
- Branch: `feat/issue-67-astra-approval`
- Base: `main` / `6507727986329e34e69da3680a00824eb1fbfe13`
- Skill・設計のtechnical HEAD: `8bdb6aa77c668ff9b13aaa6b3e302f57dcbd393e`
- 追跡表を含む生成元HEAD: `97c7958da5e7fd84e21e7dde5b5d31ac8df7b54e`
- 実装状態: 要求されたSkill・設計変更をcommit/pushし、PR作成済み。
- Review状態: 本chatは実装担当。独立reviewは未実施で、review verdictを発行していない。
- Persistence: 通常のimplementation report。independent-review attestationではない。

本reportとhandoffのcommit SHAは生成時点で存在しないため`commit_pending`とし、保存後のPR current HEAD、対応するCI、簡易reportコメントのURLはPR metadata／commentへ記録する。本書のCIを、後続の別SHAのCIに代用しない。

## 要求・作業方針

Issue #67は、既存モデルを先に使用し、問題が発生して継続しても解決が見込めない場合だけ、ユーザー承認付きでAstraを対象taskのsub-agentとして使用する要求である。継続は原則ターンごとの承認とし、明示オプションとしてtask完了までの承認を認め、reasoning effortはhighに固定する。

Project Instruction、root `AGENTS.md`、添付ZIPの`chat-implementation-worker`、`work-context-manager`、`implementation-worker`、`report-writer`、`chat-handoff-manager`を基準とした。GitHubの参照・更新・commit/push・PR操作はconnectorで実施した。CodexSkill自身の保守はnon-TDDであり、RevMem向けのRed先行・診断artifact workflow追加は適用しない。

既存workflowを開始時に確認した。`.github/workflows/release-chatgpt-worker-skills.yml`はrepository validator、配布ZIP生成・構造確認、ZIP artifact保存を持つが、失敗時のテスト結果・標準出力・標準エラーをまとめる専用診断artifactは持たない。上記の適用境界によりworkflowは変更しなかった。

## 設計と実装内容

| 変更file | 目的 |
| --- | --- |
| `design/astra-escalation-design.md` | 要求、状態遷移、承認範囲、具体的受け入れ条件A67-01〜20を追加 |
| `design/adaptive-agent-assignment-design.md` | 既存の選定・runtime適用・report・reviewer continuity設計へAstraを統合 |
| `design/skill-hierarchy-design.md`、`skills/design/skill-hierarchy-design.md` | 承認管理の責務とauthorization-only呼び出しを同一内容で同期 |
| `skills/sub-agent-task-manager/references/astra-escalation.md` | 適格性、費用通知、grant、操作単位の消費・失効、迂回防止の正本 |
| `skills/sub-agent-task-manager/SKILL.md` | 新規dispatchと既存agent向けauthorization-onlyを接続 |
| `skills/sub-agent-task-manager/references/agent-profile-selection.md` | Astraを自動default/floorにせず、適格性と承認後だけ選定 |
| `skills/sub-agent-task-manager/references/spawn-agent-model-overrides.md` | role、継承、availability、fallback経路でも承認を確認 |
| `skills/codex-delegation-executor/SKILL.md` | task-local証拠とgrantを渡し、別agent/taskや親実行への迂回を禁止 |
| `skills/development-orchestrator/SKILL.md` | 承認・capability stopを上位flowで保持 |
| `skills/review-enforcer/SKILL.md` | 同じAstra reviewerへの追加作業にもauthorization-onlyを適用 |
| `skills/report-output-manager/references/sub-agent-report-template.md` | parent-ownedの適格性・承認・scope・操作消費証拠を追加 |
| `tasks/tasks-status.md` | T-004、具体的終了条件、生成元HEADの検証、report参照を追加 |

新規Skillは追加せず、承認管理は既存`sub-agent-task-manager`へ集約した。Skill-gap判定は`update existing skill`。別の恒常的feedback ledger変更は行っていない。

### 承認の具体的な挙動

`single_turn`は1 agent・1 taskに対する1回のboundedな作業要求を許可する。開始要求の送信直前にgrantを消費し、返答後の`send_input`、retry、実作業を再開するresumeには新たな承認を要求する。内部tool呼び出しごとには分割しない。poll、wait、既存結果の取得は新規実行ではない。

`task_until_completion`はユーザーが明示的に選択した同一task/scope/完了条件内だけで継続できる。各操作前に有効性を確認し、完了・取消・scope拡大・別task/agent/lifecycle・別parent sessionへ移行したgrantは利用しない。無制限retryや暗黙のPR全体承認とは扱わない。

親が確認・消費・送信を直列化する。要求を送った後のtimeout、拒否、開始不明でもsingle-turn grantを再使用しない。既存agentの承認確認だけの場合はprofileを再選定せず、spawnやreport再予約を行わない。

role/default role、full-history継承、availability置換を含め、Astraは`gpt-6-astra` / `high`だけを許可する。profileが安全に解決できなければ実行前にcapability gapとして停止する。spawn成功からexact appliedを推測せず、非公開なら`applied: null`を保持する。Astra spawn失敗を親の`codex exec`や親モデル切替で代用しない。

## 受け入れ条件の照合

以下は実装担当によるSkill本文とのcontract照合であり、自動テスト20件の成功や実モデルの実行結果を表さない。正本は`references/astra-escalation.md`。独立reviewの代替でもない。

| ID | 条件 | 対応箇所・確認結果 |
| --- | --- | --- |
| A67-01 | 通常task | selectorの通常default/floorはLuna/Terra/Solのまま |
| A67-02 | 既存モデル未実行 | Eligibility before proposalがAstraを除外 |
| A67-03 | 試行・blocker・期待効果あり | Proposal and explicit consentでproposal提示、requested未設定 |
| A67-04 | 無応答・repository policyだけ | 明示consentがない限りpending・実行なし |
| A67-05 | 次の1ターンを承認 | Authorization modesとoperation gateで単一operationへ消費 |
| A67-06 | poll・wait・結果取得 | 新しい作業・承認消費に含めない |
| A67-07 | 追加依頼・retry・作業再開 | single-turnなら新たなgrantが必要 |
| A67-08 | timeout・二重投入 | issued requestは消費済み、親が直列化して再利用しない |
| A67-09 | task完了まで明示承認 | 同一scopeの有効grantを操作ごとに確認して継続 |
| A67-10 | 完了・取消・別scope/agent/session | 失効またはbinding不一致として元grantを利用しない |
| A67-11 | 拒否・費用不明 | Astraを除外、不明費用は不明と明示 |
| A67-12 | roleが通常モデルをAstraへ変更 | selector/spawn両方で同じ適格性・承認gateを再適用 |
| A67-13 | Astra high以外・未知の継承 | 高さ固定・事前安全確認を満たさずcapability gap |
| A67-14 | availability fallback | Astraを自動higher-tier置換にしない |
| A67-15 | Astra spawn拒否 | 親codex execへ迂回せずcapability gap |
| A67-16 | Astra reviewer継続 | authorization-only、identityとreport予約を維持 |
| A67-17 | 既存Sol xhigh/max reviewer | 同一lifecycle再利用の従来承認を保持 |
| A67-18 | final profile非公開 | applied=nullとunverifiedを維持 |
| A67-19 | 実profile不一致 | 不一致を保存し追加投入停止・安全な停止を検討 |
| A67-20 | 認証不足・一般的実装指示 | モデル変更で解消できないblockerや費用承認とは扱わない |

## 検証結果

Repository全体はconnector経由のremote CIで検証した。ローカルにはrepository全体を展開しておらず、full local validationや`git diff --check`を実施したとは記録しない。

| 検証 | 結果・証拠 |
| --- | --- |
| `python3 scripts/verify_skill_repository.py` | 生成元HEADのCI build jobでsuccess。Skill構造、依存、active relative link、階層設計同期等 |
| `python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip` | 同じCI jobでsuccess |
| `python3 -m zipfile -l chatgpt-worker-skills.zip` | ZIP生成・検証stepでsuccess |
| ZIP artifact upload | 同じHEADのrunでsuccess、下記ID/digest参照 |
| Astra YAML例の構文 | connector取得の例をPython/PyYAMLでparseしexit 0。high proposal、pending single-turn、承認null、usage空をassert |
| A67-01〜20 | 上表の本文照合。runtime実行テストではない |
| Markdown lint | `tools/`と`package.json`不在のためrepository定義lintはunsupported |
| built-in skill-creator validator | 確認したローカルSkill配置に存在せず未実施。CI repository validatorとは区別 |
| 実Astra呼び出し・費用消費 | 未実施 |
| 独立review | 未実施 |

### 生成元HEADと一致するCI

- HEAD: `97c7958da5e7fd84e21e7dde5b5d31ac8df7b54e`
- Event: `pull_request`、PR #68
- Run: [34023178976](https://github.com/ssaattww/CodexSkill/actions/runs/34023178976)、`completed / success`
- Build job: `101459387233`、validator・ZIP build・artifact uploadの各stepがsuccess
- Artifact: `9986182499` / `chatgpt-worker-skills-34023178976`
- Artifact digest: `sha256:9b2341a402846222d0279af33d67687f911d4dda7957a64b415e6321af8f301c`
- Artifact size: 18,678 bytes、確認時expired=false
- Publish/release jobs: PR eventのためskipped

runとartifactの`head_sha`が上記HEADと一致することをAPIで確認した。Artifactの保存・metadataを確認したが、binary ZIPをローカルへdownloadして別途調べたとは主張しない。配布ZIPは従来の8つのChatGPT wrapper/core Skillであり、AstraのCodex用referenceを新たに同梱する変更ではない。

technical HEAD `8bdb6aa77c668ff9b13aaa6b3e302f57dcbd393e`にもrun `34022757470`のsuccessがあるが、本reportでは追跡表を含む生成元HEADのrunを主証拠とする。report/handoff保存後の最終HEADは、さらにそのHEAD固有のrunを確認してPR commentへ記録する。

## 費用根拠と不明点

[公式Astraモデル説明](https://developers.openai.com/api/docs/models/gpt-6-astra)でモデルIDとhigh対応を確認した。2026-09-06確認の[公式API pricing](https://developers.openai.com/api/docs/pricing)では、standard短contextの100万tokenあたり入力/出力はAstraが10/50米ドル、Solが4/20米ドルで、同条件の単価比は2.5倍。Issue記載の2.4倍は要求者の前提として区別した。

実際のCodex契約での費用・usage、token量、context長、cache、tier、tool費用を含む総額は不明であり、固定倍率として実装しない。実際の承認提案時に利用条件と費用情報を再確認し、不明点を明示するcontractにした。利用者環境でのモデルavailability、role設定、profile observability、停止機能は実行確認していない。

## 意図して変更しなかった範囲

通常のLuna/Terra/Sol default、Sol xhigh/maxの既存承認、reviewer identityと独立reviewの終端規則、ChatGPT core/wrapperの配布集合、workflowとvalidator実装は変更していない。他Issueのtracking履歴は内容を維持した。Astra利用を強制するruntimeコード、料金API、nested agent、親モデル切替、mergeは対象外。

## 残る確認と引き継ぎ

本変更は運用Skillのcontractであり、runtimeレベルの技術的強制機構を実装したものではない。独立したreviewerによる本文・経路の検証と、許可された実環境でのavailability／profile確認は未実施である。未実施項目を合格へ置き換えない。

引き継ぎは別成果物`reports/handoffs/issue-67-pr68-implementation-20260906.yaml`へschema version 3で保存する。次のreview chatはPR current HEADをconnectorで再取得し、同じHEADのCIだけを採用する。本chatの書込権限やAstra承認を継承しない。

PRはreview用に提出する。mergeは行わず、利用者が判断する。

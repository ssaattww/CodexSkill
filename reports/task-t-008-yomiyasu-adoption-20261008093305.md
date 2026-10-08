# T-008: yomiyasu の利用先展開手順 追加実施報告

## 1. 結果と対象

他のリポジトリでも日本語の推敲を小さく試せるよう、既存の `markdown-word-checker` に導入手順への入口を追加し、手順書と手動記録用テンプレートを作成した。限定した契約確認で見つかった medium 2件は修正し、同じ確認担当が closed を確認した。
技術変更は commit・push 済みで、[draft PR #91](https://github.com/ssaattww/CodexSkill/pull/91) を作成済み。本報告・引継ぎ・追跡更新の commit、push、最終 HEAD に対する CI 待機は、本文生成時点では未完了である。

| 項目 | 値 |
| --- | --- |
| 種別・作業 | `implementation_report` / `T-008` |
| リポジトリ・branch | `ssaattww/CodexSkill` / `docs/yomiyasu-rollout-guide` |
| base ref・基点 | `main` / `8ee6e9f80a0362a4d066c4ea39fd3e87002fc829` |
| 現在の技術 HEAD | `a9aa807fb70228d83b383b72ee9a3587d2f8eee6` |
| 技術変更の比較範囲 | `8ee6e9f80a0362a4d066c4ea39fd3e87002fc829..a9aa807fb70228d83b383b72ee9a3587d2f8eee6` |
| `technical_head` / `administrative_parent` | いずれも `a9aa807fb70228d83b383b72ee9a3587d2f8eee6` |
| 次の保存・公開状態 | `commit_pending` / `push_pending` / `ci_wait_pending` |
| 検証能力 | `local_execution_available`。接続 PC の専用 clone で実行可能 |
| 独立最終レビュー対象 | `reviewed_implementation_head: null`。正式な独立最終レビューは未実施 |
| 保存方式・予約先 | `repository_file` / `reports/task-t-008-yomiyasu-adoption-20261008093305.md` |

本文に、まだ存在しない自己 commit の SHA は記載しない。最終保存後の commit SHA、push、全件検証、CI の結果は PR コメントに記録する。この文書は独立最終レビューの attestation report ではなく、merge の許可も表さない。

## 2. 目的と責務配置の判断

依頼は、Duck #66 で試した `yomiyasu` を他の利用先へ展開するための手順を CodexSkill に置き、既存のホワイトリスト運用を参考にすることだった。通常の lint の入口と利用先設定の契約を持つ既存 Skill に参照文書を追加する構成とした。
導入時だけ必要な説明を参照文書へ置き、通常の lint 実行・分類は [既存 Skill](../skills/markdown-word-checker/SKILL.md) に戻す。新しい Skill や runtime hook を作る必要はないと判断した。

| 担当・配置 | 今回明確にした責務 |
| --- | --- |
| CodexSkill | 再利用する手順、記録様式、既存の lint 実行・分類との接続 |
| 利用先リポジトリ | 対象文書、用語、許可一覧、表記規則、実 lint コマンド、採用版、試行範囲、記録先 |
| 作業を管理する親 | 対象 root、focused/full、必須 gate、既に得た権限、結果の集約 |
| 内容の判断担当 | 意味・条件の保持、読みやすさ、内容受入、継続利用の判断 |

ホワイトリスト運用から引き継ぐのは、候補の抽出、採否の判断、設定への反映、再検査を分ける責務である。Duck の用語・許可一覧・件数・環境を共通の必須値として移植しない。
正式語・別表記・修正すべき表記は、既存の `term` / `description`、`aliases`、`prh` の判断へ接続する。SudachiPy・ChikkarPy や推敲ツールの候補を自動登録せず、正確な差分に対する既存のレビューと反映後の再検査を使う。既に得た確認を取り直す承認手順は追加していない。
根拠は [Markdown word check の設計](../design/markdown-word-check-skill-design.md) と [ホワイトリスト再構築の設計](../design/review-enforcer-markdown-whitelist-rebuild-design.md)、既存 Skill の分類・新語経路である。

## 3. 変更したものと変更していないもの

| ファイル・範囲 | 内容・本文生成時点の状態 |
| --- | --- |
| `skills/markdown-word-checker/SKILL.md` | 導入・採用版更新・展開時に読む手順への入口を追加。技術 commit に収録済み |
| [導入手順書](../skills/markdown-word-checker/references/yomiyasu-adoption-guide.md) | 責務、事前記録、専用 checkout、版固定、段落選定、候補比較、lint、最終照合、公開、継続・停止を説明。技術 commit に収録済み |
| [記録テンプレート](../skills/markdown-word-checker/assets/prose-pilot-record.yaml) | 提案版と確認済み版、原文・試案・最終文、各検査の出所、実ファイル照合、内容受入を分離。技術 commit に収録済み |
| task/phase の追跡文書、本報告、schema 3 引継ぎ、証跡 | 最終保存・検証の対象。本文生成時点では次の commit が未確定 |

テンプレートは人が記入する YAML であり、自動実行の設定ではない。段落数、合否基準、採用 SHA、担当者は利用先が決める。
利用先の用語・許可一覧・対象除外、既存 gate の判定規則、workflow、実行スクリプト、hook は変更していない。共有 CodexSkill checkout、Duck checkout、PC の全体設定、個人 Skill のインストールも変更対象外とした。
既存 `PostToolUse` の早期 lint フィードバックを、推敲や最終 lint、review gate の代用にはしていない。

## 4. 実行環境と証跡の識別

実リポジトリへの書き込み、実コマンド、Git、gh は接続 Windows PC 上で実施した。実行結果の記載は、その記録を親作業が収集した結果に基づく。起草・利用演習の現在の実行環境を、実リポジトリの検証環境と同一視しない。

| 項目 | 確認した値 |
| --- | --- |
| 実行手段 | `RDMCP + gh CLI`、node/machine `local`、Windows、`cmd.exe` |
| 作業領域 | `C:/Users/donabe/RemoteDesktopWorkspace/CodexSkill-yomiyasu-guide-20261008`。今回所有する専用 clone |
| PC 上の診断保存先 | 上記と同じ親にある `CodexSkill-yomiyasu-evidence-20261008` |
| 依存実版 | Python `3.14.7`、Git `2.46.0.windows.1`、gh `2.101.0`、PyYAML `6.0.3` |
| 依存確認 | clone・branch 切替・Git SHA 読取、gh の repo 読取、Python 実行が成功。PyYAML は作業所有の `checks-env` に導入 |
| ソースの識別 | 技術 HEAD と未 commit の状態を併記し、実行時の対象・スクリプトをファイル指紋で識別。集約指紋は `d08d59bbe7b086b5588f2c54133910abc3f10349066c95417618f0f1545acc59` |

永続参照先は [evidence.zip](diagnostics/task-t-008-yomiyasu-adoption/evidence.zip) と [manifest.json](diagnostics/task-t-008-yomiyasu-adoption/manifest.json)。証跡 archive の SHA-256 は `62a41f6f74835ee15b995787816a9dba24a7b930af01e3bf214a047a8a4d4cb8`。
archive 内の元の PC パスや演習担当の `/workspace/` パスは実行・作成場所の記録であり、公開 artifact の参照先ではない。argv、cwd、時刻、終了コード、stdout/stderr、source identity、依存実版、成功・失敗を上書きせず保持する。

## 5. 実行例と実施済みの検証

手順書の接続例は `python scripts/link_consumer_skills.py "<consumer-repo-absolute-path>"` を使う。専用の一時利用先 `consumer with spaces` で実行し、`.agents/skills` が当該 clone の `skills` を指すことを確認した。
外部ツールは専用の `yomiyasu tool` に取得し、`fetch --depth=1`、detached checkout、`rev-parse HEAD` で `0df47749139dfd64ad3d55e7d53d3839e5874848` と照合した。これは v1.1.0 の再現例であり、現在の最新版や全利用先の採用決定を示さない。
実行した静的検査は `python -B <tool>/skills/yomiyasu/scripts/yomiyasu_lint.py <file> --json` と `python -B <tool>/skills/yomiyasu/scripts/yomiyasu_diff.py <original> <candidate> --stance=説明 --json`。実際の絶対パスを含む argv は証跡に残した。

| 検証 | 結果と有効範囲 |
| --- | --- |
| `command-examples-01` | source 読取、構造検査、diff 検査、接続、固定版取得、lint・diff、依存導入、YAML 検査の15コマンドが期待した終了コードで成功 |
| 静的検査の出力 | lint JSON の `findings`・`score` と diff JSON を確認。原本・候補の bytes が検査前後で同一。スクリプトは意味保持の合格を主張していない |
| `document-checks-02.json` | YAML 構文・初期状態、skill-creator の `quick_validate.py`、`python scripts/verify_skill_repository.py`、`git diff --check` が成功 |
| `document-checks-03.json` | 契約指摘の修正後、技術 commit 前に同じ4項目が成功 |
| CodexSkill の focused/full Markdown 用語 lint | 両 scope とも `unsupported`。利用先型の用語設定・package 配線がないため。今回の文書変更では caller が理由付きでリスクを受容 |
| 最終差分全体の `scripts/run_validation.py` | 未実施。報告・追跡・引継ぎを含む最終 candidate を用意してから実行する |

文書用 lint の `unsupported` は、既存の構造・build 検証の免除を意味しない。また、警告があっても通常の yomiyasu lint は終了コード 0 になり得るため、点数や終了コードだけで読みやすさ・意味保持・必須 gate の合格を決めない。

## 6. 新しい担当による2件の利用演習

演習は、渡した手順書・様式とシナリオから記録を作れるかの確認である。演習用の利用先へ接続した実導入や、引継ぎ済み検査の再実行ではない。原記録 `usage-missing-lint.yaml` と `usage-candidate.yaml` は証跡から参照する。

| 演習・担当 | 観察できた判断 | 未完了として保持した内容 |
| --- | --- | --- |
| lint 未構成 / `/root/guide_use_missing_lint` | 存在しない lint コマンドや段落原文を補作せず、共有 checkout を切り替えない準備手順を記録。固定 SHA は未取得の提案として保持 | 段落選定・実検査は0件、lint の必須性と caller の受容は未決、内容受入と継続利用は `pending` |
| 条件を失う候補 / `/root/guide_use_candidate` | 提供要約では原文・候補とも score 100 でも、接続失敗時だけ再試行する条件と3回失敗後の停止条件を失う候補を不採用にし、原文維持と判断 | 選定1・候補1・変更0・原文維持1。実ファイル照合は `not_run`、内容受入は `pending`。候補の検査成功で既存 full lint 失敗を消さない |

後者では `500 ms` の一致だけで同義とせず、「再試行」から「再接続」への置換も根拠不足と記録した。別見出しにある同じ文との誤照合を避け、見出しと2行全文で対象を特定する次の確認を残した。
演習のフィードバックから、提案版と取得済み版、候補と最終文の意味評価、実ファイル照合、記録内 ID と実行 ID、提供要約と未実施の最終検査を手順・様式で明示した。利用先 lint を新設する設計や、各 shell に対する証跡保存手順の網羅までは追加していない。
これらの演習結果は演習時の入力に対する観察であり、修正後の全手順を実利用先で完走した結果としては扱わない。

## 7. 契約確認の指摘と修正確認

確認担当は `/root/guide_contract_check`。以下は今回の変更に対する限定した契約確認であり、リポジトリ全体の独立最終レビューではない。元の severity は2件とも `medium` のまま保持し、変更・格下げはしていない。

### YAD-CR-001 — 必須 lint の実行不能を unsupported に寄せる記述

- severity: `medium`、origin: `introduced_by_change`、location: `skills/markdown-word-checker/references/yomiyasu-adoption-guide.md` の節2。
- 内容・影響: 必須 lint の実行可能な代替経路がない場合も一律 `unsupported` と読め、利用先の必須 gate が既存 checker の `failed gate` 分類と食い違った。
- 元の根拠: v2 guide の30/32行と、既存 Skill の `Typical classification` にある package.json 不在・必須 gate の代替経路不在の扱いの不一致。
- 必要な対応と実施: 既存分類へリンクし、npm 経路の `unsupported` と、必須 gate の代替 script 経路もない場合の `failed gate` を明記した。
- disposition: `closed`。同じ確認担当が当該 finding と対応差分だけを再確認し、修正を認めた。構造上の確認は修正後の `document-checks-03.json` でも成功。実利用先の必須 gate を実行した証拠とは区別する。

### YAD-CR-002 — full 対象設定によって focused から報告を外せる記述

- severity: `medium`、origin: `introduced_by_change`、location: guide の節7項目3、および `assets/prose-pilot-record.yaml` の `final_diff_scope.files`。
- 内容・影響: full の対象設定を使って今回変更した reports 等も focused から外せる読み方になり、今回作成・編集した Markdown 明示ファイルの可否・結果を記録する既存契約を満たさなかった。
- 元の根拠: v2 guide の143行・template の174行と、Markdown word check 設計の `Markdown authoring integration` の不一致。
- 必要な対応と実施: focused は今回作成・編集した Markdown の明示一覧、full は利用先設定で解決した集合と区別した。full 対象外の報告にも focused の実行可否・結果・理由を残すと両ファイルへ明記した。
- disposition: `closed`。同じ確認担当が当該 finding と対応差分だけを再確認し、修正を認めた。修正後の4項目検査も成功し、対象除外の追加は行っていない。

元の確認・closure は文書版と限定差分に対して行われた。独立最終レビューの初回 HEAD・closure HEAD 列は提供されていないため補作しない。今回閉じた2件を根拠に、後続の管理文書や最終 CI まで確認済みとは結論づけない。

## 8. 文字コード方針と運用上の失敗

PC 上の既存 `SKILL.md` は UTF-8 BOM無し・CRLF を維持した。既存 validator と `quick_validate` が先頭の `---` を読む契約との互換性を保つためである。新規 guide/template は UTF-8 BOM付き・CRLF で転送し、SHA を照合した。
追跡文書2件は既存の UTF-8 BOM無し・CRLF を維持し、報告・引継ぎは UTF-8 BOM付き・CRLF で保存する予定。最終 bytes の情報は manifest に残す。本文生成時点では、これから生成するファイルの bytes 検査を完了したとは扱わない。
実行例の原本・候補は UTF-8 BOM付き・CRLF の fixture とし、静的検査前後の raw bytes SHA-256 一致を確認した。利用先へは文字コード・BOM・改行を先に記録し、修正は編集として行ってから読み取り専用の検査をやり直す手順を示した。

| 起きた事象 | 影響と回復 |
| --- | --- |
| `TODO_STALE` による4回の書き込み拒否 | 変更前に拒否された。Todo を更新してから再試行し、失敗を成功記録に置き換えなかった |
| 最終文書検査の起動失敗 | `cmd.exe` が引用した相対実行ファイルパスを `..` と解釈し、process `vvDEaNu6vJmvkGVWxosCm_xGhOSrrahq_PekjtTN0Bs` が exit 1。Python の `subprocess` argv 経由で再試行し成功。失敗した起動でソース文書は変わっていない |
| scratch 上の重複した guarded patch の拒否 | 対象 YAML の項目は既に `runs` 配下にあった。実体を読み直して補正不要と確認し、リポジトリ変更は発生しなかった |

## 9. 未実施、CI の確認方法、次の境界

最終全件検証は `not_started`、最終 candidate HEAD は未確定である。技術 HEAD の成功を、これから追加する報告・引継ぎ・追跡更新へ転用しない。最終内容を固定した後、新しい外部証跡ディレクトリを指定して `python scripts/run_validation.py --output-dir <new-external-evidence-dir>` を実行する。
最終 push 後の一致する CI run・conclusion は、本文生成時点では未確認。CI は次のイベント差を踏まえ、PR の現在の HEAD、実 checkout SHA、実行した job、artifact を照合する。

| workflow | 必要な確認 |
| --- | --- |
| `Validate and release ChatGPT worker skills` | `pull_request` では PR head を checkout する。最終 HEAD に対する必要な検査の実行・結果を確認する |
| `PR commit artifacts` | 同一リポジトリの `synchronize` は no-op。`push` の収集・検証の実行を確認し、synchronize の緑だけを実検査の成功とみなさない |

残る限界は、手順追加だけでは自動連携が有効にならないこと、CodexSkill 自体の Markdown 用語 lint が未構成であること、他の実利用先での導入・内容受入・継続利用をこの作業では実施していないことである。版更新時の再検査や、利用先の必要な lint 導入・修復は各利用先で行う。
次は schema 3 の [引継ぎ](handoffs/task-t-008-yomiyasu-adoption-20261008093305.yaml) と追跡更新・証跡を保存し、必要な commit と全件検証を最終 push 前に完了させる。push 後は最終 HEAD の CI を確認し、PR コメントへ実測結果を記録する。本文生成後に失敗・差分が生じた場合はその事実を残し、影響する検証をやり直す。
その後の review は、この実施報告、最終差分、実行証跡、現在の HEAD に対して行う。独立最終レビューが必要な運用では、対象 HEAD を固定して別途その手順へ渡す。PR は draft のままレビューへ引き継ぎ、merge、main への直接反映、Duck issue の close は今回の実施範囲に含めない。

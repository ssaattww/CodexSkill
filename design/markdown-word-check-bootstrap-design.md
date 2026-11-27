# Markdown用語検査bootstrap設計

## 目的と適用範囲

Issue #87として、用語検査をまだ導入していない他リポジトリへ、対象リポジトリ内で完結する `tools/lint/` を安全に導入する。CodexSkill自身への適用である #79 / PR #80 は保留とし、本設計の完了条件に含めない。

対象リポジトリのroot package設定に依存せず、WindowsとLinuxで同じファイル構成、衝突規則、監査結果、合否条件を使う。Sudachi checkerの判定ロジックは既存のものを再利用する。用語検査と意味・読みやすさの評価は別の作業・証拠として扱う。

## 固定する導入ファイル

通常導入では次の7ファイルだけを作成する。`--with-ci` が明示されたときだけ8番目を加える。列挙外のファイルを探索して自動追加してはならない。

| # | 固定パス | 目的 |
|---:|---|---|
| 1 | `tools/lint/.gitignore` | venv、診断、Python生成物を除外 |
| 2 | `tools/lint/README.md` | Windows/Linux共通の利用方法と合否契約 |
| 3 | `tools/lint/requirements.txt` | 固定した checker 依存 |
| 4 | `tools/lint/markdown-targets.json` | 対象と除外の初期設定 |
| 5 | `tools/lint/markdown-whitelist.yaml` | `entries: []` から開始する許可一覧 |
| 6 | `tools/lint/scripts/run_markdown_word_check.py` | repo-local 実行wrapper |
| 7 | `tools/lint/scripts/check-markdown-whitelist-sudachi.py` | 既存Sudachi checkerのコピー |
| CIのみ | `.github/workflows/markdown-word-check.yml` | 初期audit workflow |

上記以外のインストール先、root `package.json`、製品コード、既存workflowは変更しない。CI用workflowを置けない・置かない場合も通常の7ファイル導入は独立して使える。

## R01–R06 受け入れ契約

| ID | 要件 | 合格条件 |
|---|---|---|
| R01 | 固定manifest | 既定は上記7パスのみ。`--with-ci` のときだけCI pathを追加。追加・欠落・別名は計画へ混ぜない。manifest外のsourceは無視し、必須sourceの欠落・通常file以外の型は拒否する。計画結果は後続の書き込み許可ではない。 |
| R02 | 許可位置・非上書き・dry-run | targetは既存Git worktreeのroot。各destinationは許可manifest内に限る。既存ファイル、symlink、dangling symlink、Windows junction/reparse point、非directoryの親が1つでもあれば、変更前に全衝突を報告して停止。forceなし。dry-runは予定先・供給元を表示し、ファイル・ディレクトリ・診断領域を一切作成しない。 |
| R03 | 失敗時の所有権 | 途中失敗時に削除できるのは、この実行が新規作成したと証明できるfileと空directoryだけ。事前存在物、他プロセスが作成した物、所有を証明できない物は残し、そのpathと理由を診断する。 |
| R04 | 引数・診断位置 | mode/scope/target/files/outputを副作用前に検査する。不正引数では導入物・診断領域とも作らない。実行診断の正本は既存 `tools/lint/artifacts/` 配下とし、別の自動作成先を追加しない。読み取り専用plannerは診断directoryを作らずstdout/stderrだけに結果を出す。 |
| R05 | 結果の区別 | 各実行で `stdout.log`、`stderr.log`、`result.json` を保存する。`needs_user_review` はcheckerが未登録語違反を返した状態、`failed` は依存不足・設定不正・対象解決失敗・起動失敗・予期しない終了など実行不能状態。auditの未登録語だけはプロセス成功でも用語合格ではない。enforceの未登録語は非zero。 |
| R06 | CIの証跡と基準 | checkout直後に期待するPR head SHAと `git rev-parse HEAD` を照合。一致しなければcheckerを起動しない。各run/attemptで新しいrunner-temp diagnostics directoryを作り、既存結果を採用しない。checkout・Python準備actionの内部ログはjob log、artifactにはstep outcomeを記録する。利用可能なshell診断はstdout/stderrと状態を保存し、venv・pip・診断準備を個別にsuccess/failure/not_runで記録する。実行したcheckerの結果だけを収集し、必須diagnosticまたはartifactの欠落・保存失敗はjob failureにする。`always()` でuploadを試みる。初期modeはaudit。未登録語候補はartifactに残し、初期CIをblockingにしない。 |

R02の衝突確認は書き込み時の競合にも対応する。初回確認後に他プロセスがdestinationを作った場合、そのpathを上書きせずR03に従う。作成したdirectoryが途中で他の内容を含むようになった場合は削除しない。

## 導入の安全境界と失敗時の後始末

bootstrapはworktree rootを明示し、root外へのpath、symlink経由のroot外書き込み、再parse pointを通じた迂回を拒否する。manifestと実出力が一致することを確認してから処理する。

複数ファイル作成は、各作成を排他的に行い、今回作成した対象の識別情報を保つ。途中で失敗した場合は作成物を一つずつ識別してから除去し、同一性を再確認できないfile、既存file、共有・非空directoryは触らない。処理中に所有を区別できる仕組みが示せない実装は受け入れない。診断には残存物、削除した自分所有物、削除できなかった理由を記録する。

## 対象範囲と既存checker契約

| scope | 入力 | 失敗条件 |
|---|---|---|
| `full` | `markdown-targets.json` に従う全Markdown | 設定の欠落・破損、target root解決不能、checker実行不能は `failed` |
| `changed` | tracked worktree差分、stage差分、未追跡Markdown | いずれかのgit取得コマンドが失敗した場合に「変更なし」へ置き換えない。失敗内容を保存して `failed` とし、全体を無変更扱いにしない |
| `files` | 利用者が明示した各ファイル | 欠落、repo外、除外対象、非対応拡張子、重複や解決不能を成功扱いしない。対象候補は既存checkerの明示file検証を通す |

既存Sudachi checkerは `--files` を使う場合もtarget設定とwhitelistを読み、whitelistのterm/aliases/descriptionを検査入力として評価する。したがってfocused lintは「明示Markdownだけ」と「許可一覧の自己検査」を含む契約であり、明示ファイルだけでchecker全体が終わるとは説明しない。この振る舞いと既存の明示file時のallowlist評価を維持し、checkerの語彙判定は変更しない。

`changed` の取得で `git diff`、`git diff --cached`、未追跡file列挙のいずれかが失敗したとき、空集合で処理続行してpassにすることは禁止する。対象一覧の取得成否を診断へ残す。

## audit / enforce と合否例

| 入力・実行状態 | audit | enforce |
|---|---|---|
| 検査実行成功、違反なし | `pass`, exit 0 | `pass`, exit 0 |
| checkerが未登録語違反を検出 | `needs_user_review`, exit 0。用語合格ではない | `needs_user_review`, exit nonzero |
| 設定不正、依存不足、checker起動不可 | `failed`, exit nonzero | `failed`, exit nonzero |
| changed取得コマンド失敗 | `failed`, 診断を保存しexit nonzero | 同左 |
| filesに不存在・repo外・除外対象を指定 | `failed`, 理由を保存しexit nonzero | 同左 |
| 引数不正 | 実行前に拒否。診断も作らない | 同左 |

未登録語候補をwhitelist、aliases、description、prh、対象除外へ自動登録しない。具体的な許可や除外変更は利用者がexact entryを確認した後に行う。enforceをblocking gateにするのは対象範囲と初期許可一覧の確認後とする。CLIの `--output-dir` はR04の専用run directoryを指定し、毎回異なるrun-idを使う。

## WindowsとLinuxの同一条件

| 項目 | Windows | Linux |
|---|---|---|
| パス比較 | OS pathを正規化してroot内を検証。大文字小文字や区切り差で衝突を見逃さない | 同じmanifestとroot内検証 |
| root判定 | `git rev-parse --show-toplevel` を使い、指定target自体がworktree rootであることを要求 | 同じGit root条件 |
| 非上書き | 通常file、directory、symlink、dangling link、junction/reparse pointを衝突扱い | 通常file、directory、symlink、dangling linkを衝突扱い |
| 出力 | UTF-8で固定manifest、診断3点セットを保存 | 同じUTF-8、manifest、診断3点セット |
| 環境 | `tools/lint/.venv/Scripts/python` を使用 | `tools/lint/.venv/bin/python` を使用 |
| 合否 | R01–R06の同じ状態定義、exit条件 | 同じ状態定義、exit条件 |

OS間で一方だけforce、fallback、衝突無視を許さない。Windowsの再parse point検出能力が不足する場合は安全に停止し、弱い確認へfallbackしない。

## CIテンプレート

`--with-ci` のworkflowはPR head SHAをcheckoutし、期待SHAと実checkout SHAを確認する。checkout/Python setup actionの内部ログはGitHub job logに残し、取得できないstdout/stderrをartifact内に捏造しない。venv、pip、repository診断準備は個別の状態（success/failure/not_run）を記録し、利用可能なshell出力はrunner-temp diagnosticsへ保存する。diagnostics directoryは各run/attemptで新規作成し、checker出力もrun/attempt固有のpathを使う。checker直前にも当回出力先の既存物を拒否する。実行完了を示す当回の行を確認してから、結果とその参照先の標準出力・標準エラーを同じ収集先に保存する。未完了時は既存結果を採用しない。実行済みの処理では空でもログの存在を確認する。checkerが実行されたときの結果ファイル、必須diagnostics、artifact保存が欠ければworkflowを失敗させる。`always()` でuploadを試みる。初期auditは候補を集め、未登録語だけでworkflowを失敗させない。checker自体の実行不能やhead不一致は失敗とする。

## 実装方式の比較と推奨

| 方式 | root package/npm非依存 | Windows/Linux共通 | R01–R06適合範囲 | 判断 |
|---|---|---|---|---|
| 既存Python writerを無変更で実行 | 適合 | Pythonがあれば実行可能 | R01 manifest固定なし、R02の全衝突・リンク検出と排他的作成なし、R03所有追跡なし、R04専用診断なし、R05部分失敗診断不足。R06 HEAD検査なし | consumer treeへ実行しない |
| Node.js の読み取り専用の計画 | 適合。Node.js 18 以上が必要 | 対象の作業場所・コミット、固定パス、既存ファイルとハッシュを表示 | 計画の固定、事前確認、無変更を提供 | 既定。計画だけでは導入しない |
| 同じ計画を使う明示導入コマンド | 適合。追加のパッケージは不要 | 同じコマンドで排他作成と後始末を行う候補。Windows のパスと権限は別途検証 | 作成前に再確認し、自分が作った物だけを片付ける | 隔離した作業場所で検証する候補 |

**推奨:** 読み取り専用の計画を既定にする。隔離検証用の導入候補は `bootstrap_markdown_word_check.mjs` を使い、対象、完全なコミット識別子、`--install` を明示した場合だけ固定の7ファイル、または `--with-ci` を含む8ファイルを作る。既存の `tools/lint/` は上書き・移行しない。検証とレビューが終わるまで実際の利用先には使わない。診断は導入物の件数とは分け、`tools/lint/artifacts/bootstrap/` に残す。用語の判定と承認条件は変えない。

### 現在の入口が実装する受け入れ条件

| ID | plannerでの状態 | 残る条件 |
|---|---|---|
| R01 | 固定7 pathと明示時のみ8番目のCI path、予定hashをJSON/stdoutに表示 | 実書込み結果のmanifest照合 |
| R02 | targetがGit worktree rootか確認し、既存先/unsafe parentを検出。書込みなし | 排他stageと安全な公開・競合後処理 |
| R03 | 書込みをしないためcleanup対象なし | writerの所有識別とrollback |
| R04 | CLI引数を先に検査。plan以外の診断作成なし | 既存 `tools/lint/artifacts/` 配下への安全な診断保存 |
| R05 | planner実行エラーとdestination拒否をexit codeで区別 | checker実行、unknown/error分類、3診断ファイル |
| R06 | `--expected-head` があればcheckout HEAD一致を検査 | GHA段階ログ/artifactと実CI確認 |

## 検証順と非目標

CodexSkill保守は非TDD。まず隔離したGit fixtureでdry-run無変更、固定manifest、衝突全列挙、dangling symlink/reparse point、書き込み競合、途中失敗後の所有物だけの後始末、診断位置、full/changed/files、audit/enforceを確認する。Windowsで先に実行し、同じfixtureと期待結果をLinuxでも確認してからCI templateを検査する。現行CIまたは以前の別SHA成功は新候補の合格根拠にしない。

- #79 / PR #80は対象外。
- Sudachi checkerの用語判定は変更しない。
- 未登録語、aliases、prh、文書除外は自動登録しない。
- 現行のconsumer Skill links設計とhierarchy正本/mirrorを保持する。
- root package manager設定、製品コード、既存CIを変更しない。
- 利用者のmergeを代行しない。

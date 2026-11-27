# PR #100 共通インストーラーのYomiyasu対応：実装・検証・通常レビュー統合報告

## 対象と保存状態

- リポジトリ: `ssaattww/CodexSkill`
- 作業: T-009 / Phase 13。新規 Issue は作成しない。旧導入の [#93](https://github.com/ssaattww/CodexSkill/issues/93)、展開手順の [PR #91](https://github.com/ssaattww/CodexSkill/pull/91) は参照のみ。
- [Draft PR #100](https://github.com/ssaattww/CodexSkill/pull/100)、ブランチ `feat/cloud-yomiyasu-installer`、base `main`。
- 基点: `a18080938d7525f8b3e9f80fe237991a8c4e0562`。
- 通常レビュー対象の製品差分を保存した技術 HEAD と公開 HEAD: `522403500da83fba191fb5fd7c8a1885d15ffa60`。
- 完全パッチ（17,123 バイト）の SHA-256: `a263a4ff33e2d79183f9f39e5f678dc780a21aac1fec9737833001745d2b6b17`。
- `verification_capability: local_execution_available`。Codex Cloud の Linux x86_64、Bash 5.2.37、Node.js 24.22.3、Python 3.12.14。対象 checkout は `/workspace/CodexSkill`。
- 報告作成時点の報告・追跡は `commit_pending`、技術 HEAD と管理上の親は上記 SHA。製品コミットは公開済み。非製品3ファイルの保存コミットと通常 push を親が承認した。保存コミットの SHA と新しい CI は作成後に外部で記録する。
- 通常報告であり、独立最終レビュー報告・予約・attestation ではない。

## 要件・実装範囲

初期環境の Python と Skill リンクは利用できたが共有導入に Yomiyasu が含まれていなかった。利用先が任意に有効化したときだけ、共通側が公式固定版と照合値を管理し、起動時の通信や毎回の再導入なしで使用できるようにする。

| 変更ファイル | 内容 |
| --- | --- |
| `design/cloud-tools-installer-design.md` | 共通側と利用先の責任分界、任意有効化、取得・照合・再利用、検証条件 |
| `scripts/install-cloud-tools.sh` | 既存スキーマと .NET SDK 導入・再利用を維持し、任意の `yomiyasu: true` に対応 |
| `scripts/cloud-yomiyasu.sh` | 固定コミットから公式ファイルを取得し、SHA-256 と配置構造を検証。既存キャッシュを上書きせず、実行時にも照合した一時コピーで純正スクリプトを起動 |

公式固定コミットは `0df47749139dfd64ad3d55e7d53d3839e5874848`。

| ファイル | SHA-256 |
| --- | --- |
| `scripts/yomiyasu_lint.py` | `998ceb5b7f46a78b8d11cb4ef229f639b3b095e830f16cec80ea3a89c4755ec4` |
| `scripts/markdown_visibility.py` | `e0cc01d3263d65f4c1ccddb939972b4098fdd1453fc0de8fc7e8e25522ec5c8d` |
| `LICENSE` | `79d802f15bc8caf67f1a83c1bdbe214ccb41a0a0275f9046b329b89c65ee1fca` |
| `UNICODE-LICENSE.txt` | `e7a93b009565cfce55919a381437ac4db883e9da2126fa28b91d12732bc53d96` |

新規 Python ラッパーは利用者の既存方針に従い採用せず、Bash へ置換した。`scripts/install-cloud-tools.sh` 内の既存の設定 JSON 解析用 Python には、任意の `yomiyasu` 項目と真偽値の判定、および有効・無効を Bash 側へ渡す出力の変更を追加した。新規 `.py` ファイルは作成せず、Python の実装変更を既存解析の範囲に留める判断とした。公式上流の純正 Python スクリプトは未変更。AGENTS.md により TDD は適用しない。

Duck の入口と対象指定、Start skill、既存レポート、一括 lint、許可一覧、公開クラウド設定、FA780、既存 PR #99、マージは本 PR の対象外。Duck の候補は本 PR に含まれていない。後工程で対応版の正規確定後に利用先側の固定版を扱う。

## 実装・検証の証拠

元のローカルレビュー成果物は `Yomiyasu-review-20261126-Bash-Node.zip`（SHA-256 `4a42f93a124cad90116a502084e9382173a4786f8e8a151b5df5495ddf52cb09`）。内部の `CodexSkill.patch`、`manifest.txt`、`diagnostics/summary.json`、`diagnostics/results.json`、`validate.js`、`reproduce.sh` を実施担当が保存した。元のローカル場所は `/workspace/scratch/yomiyasu-review-bash-node.NZRaDZ/`。通常レビュー担当による Library 経由の ZIP 本体取得は HTTP 401 で失敗した。再試行・権限変更は行っていない。共通側パッチの実物を gzip + Base64 と照合値で直接受け渡し、通常レビュー担当は復元した `CodexSkill.patch` を照合した。ZIP 全体とその添付マニフェストは取得不能のため通常レビュー担当自身では未検証である。ここに列挙する証拠はリポジトリ内の追跡ファイルではない。

検証時の製品ソース SHA-256（公開 HEAD の該当ファイルと一致）:

- `design/cloud-tools-installer-design.md`: `6c526332c6adb5a3c85713ed1022885c537f663447fc07590efc44b6ca1b163b`
- `scripts/install-cloud-tools.sh`: `6446cb6bc9c9c9643bda5b1df9c1462f29cd5ed624e4a36c87052937ef7cd588`
- `scripts/cloud-yomiyasu.sh`: `b843e127be21e5c51ef1f095a9f0b0825c6016f46e62d57fc1e77ad0de86c55c`

`node validate.js` を隔離した一時領域で実行し、30件すべて期待終了状態と一致した。SDK は既存の 10.0.401 を複製した。実行証拠 `diagnostics/results.json`。再現手順そのものも終了 0。検証 fixture のソースハッシュと公開製品差分の一致を確認した。

| 共通側の確認 | 実測終了状態 / 判定 |
| --- | --- |
| 旧 .NET 設定で既存 SDK 再利用 | 0、Yomiyasu 配置なし、通信・展開なし |
| 明示無効 / 不正な設定型 | 0 / 1、不要な配置なし |
| 既存 SDK ありで有効化 | 0、公式4ファイルのハッシュ照合成功 |
| キャッシュ再利用 | 0、ハッシュと更新時刻を保存、curl/tar 拒否ガードの呼び出しなし、strace の AF_INET/AF_INET6 なし |
| 改ざんされたキャッシュの再利用 / 実行 | 1 / 2、既存値を保持 |
| 欠損・余分なバイトコード・別名リンクのあるキャッシュ | 実行 2、別名リンクの導入 1 |
| 従来の新規 SDK 導入（模擬アーカイブ） / 不正 SHA-512 | 0 / 1 |
| Yomiyasu の取得時ハッシュ不一致 | 1、固定版ディレクトリは未配置 |

組み合わせの検証で Duck 入口からの架空 README と設計書の JSON 出力、厳格モードの警告 (1)、未指定、対象外、リポジトリ外、親ディレクトリ移動、模擬レポートの直接・絶対パスと別名リンクの拒否、無効設定・欠損キャッシュの拒否を確認した。模擬レポートは `openat` の記録でも読み込んでいないことを確認した。実 README と `Testing/duck-development-udp-design.md` の JSON 出力はともに 0。これは消費側との組み合わせの証拠であり、Duck の候補を本 PR でレビューしたという主張ではない。

- `bash -n scripts/install-cloud-tools.sh`、`bash -n scripts/cloud-yomiyasu.sh`、差分検査: 成功。
- push 前に `python3 -B scripts/run_validation.py --output-dir <新規一時ディレクトリ>` を再実行: repository、bundle、zip-integrity、zip-contents の4項目成功。診断は `/tmp/codexskill-yomiyasu-prepush.d2lYL6/repository/`（実行機ローカル）。
- 旧 SDK の実アーカイブ新規取得は未実施（模擬アーカイブ）。公式 Yomiyasu の固定4ファイルの実取得・照合は成功。実際のクラウド再起動は未実施。公開済みキャッシュを変更していない。
- CodexSkill 自身の Markdown 用語検査はローカル設定・package 配線不在で `unsupported`。レポートへ Yomiyasu は実行しない。

## 通常レビューと自動 CI

親担当による通常レビュー原文の確認（2026-11-26）:

- 対象: CodexSkill の共通インストーラーのみ。基点 `a18080938d7525f8b3e9f80fe237991a8c4e0562`、完全パッチ 17,123 バイト、SHA-256 `a263a4ff33e2d79183f9f39e5f678dc780a21aac1fec9737833001745d2b6b17` と製品3ファイルの blob の一致を確認。公開した技術 HEAD は当該差分と同一。
- 通常レビューの応答 ID: `01a21718-1626-7105-a7c0-727a09d78b79`。指定モデル・推論: GPT-6.2 Sol High。適用された実行 profile、role/default-role の詳細はこの報告の受領証拠では確認できないため不明とする。
- 判定: `pass_with_held`。必須指摘は0件。実施担当が自己レビューを代替した結果ではない。
- レビュー担当が確認した項目: 直接受け渡した実物パッチの照合、`git apply --check`、Bash 構文、公式固定4ファイルの取得・照合、SDK 模擬データによる既存設定・導入・キャッシュ再利用、取得コマンドの遮断時の再利用、リンクと不正キャッシュの拒否、JSON 出力、既存リポジトリ検証。
- レビュー担当自身による実 SDK の導入、取得できなかった ZIP 全体と添付マニフェスト、OS レベルでネットワーク自体を遮断した状態での再利用は未検証。取得コマンドの遮断は OS レベルのネットワーク遮断とは区別する。実施担当による別検証では既存の実 SDK 10.0.401 を隔離領域に複製して Yomiyasu 導入・再利用を確認し、新規 .NET アーカイブの導入は模擬データで確認した。また、取得コマンドの拒否ガードと strace による外部通信用ソケットの使用がないことの確認を行ったが、OS レベルのネットワーク遮断試験は行っていない。Duck の入口はこの通常レビューの対象外。

任意指摘と扱い:

| 任意指摘 | 扱い |
| --- | --- |
| Python の使用は既存設定解析に限定する旨を追加で明記する | 既存の設定解析用 Python に任意項目の判定と出力の変更を加えた。新規 `.py` ファイルは作成せず、Python の実装変更を既存解析の範囲に留める判断とした。公式上流の純正 Python スクリプトは未変更。本報告で区別を明示し、レビュー済み製品差分は変更しない。 |
| キャッシュ側のハードリンクは通常ファイルとして扱われる | 受け入れ条件は検証済み版とハッシュの使用。追加拒否は任意事項であり、必須修正として扱わない。 |
| 共通側を先に確定する順序 | CodexSkill 側を先に確定し、後続の Duck 固定版指定は別作業とする。 |

親が確認した原文から上記を受領した。任意指摘の ID・個別 severity 等、提供されていない詳細は推測しない。独立最終レビューの判定ではない。製品3ファイルは変更しない。

GitHub の参照で次の自動 CI はすべて HEAD `522403500da83fba191fb5fd7c8a1885d15ffa60`、完了・success と確認した。

| Event | Workflow | Run |
| --- | --- | --- |
| pull_request | PR commit artifacts | [45789845620](https://github.com/ssaattww/CodexSkill/actions/runs/45789845620) |
| pull_request | Validate and release ChatGPT worker skills | [45789845667](https://github.com/ssaattww/CodexSkill/actions/runs/45789845667) |
| push | PR commit artifacts | [45789758166](https://github.com/ssaattww/CodexSkill/actions/runs/45789758166) |

2件の pull_request CI と push CI を区別した。release 関連の公開 job は skipped であり公開を実施していない。CI artifact ID、内容の再取得は未実施。ここで CI を待機・再実行していない。将来の報告・追跡コミットおよび最終 attestation HEAD の CI 成功として流用しない。

## 凍結前の残作業・引き渡し

- 既存 T-008 / Phase 12 は旧 #93 の .NET 専用範囲、当時の状態の記録であり、今回の Yomiyasu 追加を含めない。このため T-009 / Phase 13 とこの統合通常報告を別の最小候補として追加する。旧課題の追跡を今回は清掃しない。
- Skill-gap 判断: `no skill action needed`。既存 Skill が報告・追跡・通常レビュー順序を明示しており、今回不足したのは適用であって新契約を要する不足ではない。既存の Python 制約を再確認して反映した。
- FP 分類: 記録起点は親の凍結前確認指示と既存ユーザー方針。今回の導入範囲・任意指摘は機能上の事項、追跡漏れは既存ルールで是正する。新規 FP 行・重複グループ・Skill 化・Issue 作成は不要。次アクションは通常報告と追跡の同期。既存の別案件 FP-20260511-001 は変更しない。
- 通常引継ぎはすでにチャット・外部成果物・PR で行われた。今回の範囲で新規のリポジトリ保存型 handoff は選択していない。原文のない部分を補って損失のない schema 3 packet と称することはしない。この報告は詳細通常報告であり、引継ぎそのものの代替ではない。
- 次: 親が確認した通常レビュー原文の証拠を反映した非製品3ファイルを保存コミットとし、その同一 HEAD で既存全体検証を行って PR #100 の専用ブランチへ通常 push する。後続の通常レビューで非製品差分を確認する。全非最終変更が通常レビューで確定し、候補 HEAD の全体検証が揃ってから review-enforcer に引き渡す。本報告では独立最終報告の予約・作成や凍結は行わない。
- 今回の非製品3ファイルの commit と通常 push のみ承認済み。マージ、手動 CI、PR 編集、Duck 依存 pin・公開環境設定変更は実施しない。

本報告・追跡の追加差分の通常レビューは後続担当の作業。製品3ファイルはレビュー済みの内容から変更しない。

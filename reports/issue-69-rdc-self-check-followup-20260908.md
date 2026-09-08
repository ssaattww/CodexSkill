# Issue #69 / PR #71：PC経由の自己点検への接続

## 対象と結果

2026-09-08。#70の対応はPR #72としてmainの `62a7ddf3dce5c40df0a7c36a5aff27b4702cb47c` に取り込まれている。Issue #70自体のopen/closedではなく、この取り込み内容と実機を確認した。PR #71の開始HEADは `50ab0688f1fe6ea860b36956bea96141005e8c9c`。

`I69-DEP-70` の利用側実装と実機での自己点検を実施した。実装担当として `addressed` とするが、通常レビュワーによる修正確認と独立最終レビューは未実施。過去の通常レビューの `incomplete` 判定を自分でclosedやpassへ変更していない。

## 変更

- mainの#70経路を作業ブランチへ取り込み、階層設計と作業一覧の競合を解消した。T-004/Phase 9とT-005/Phase 10の両方を残し、別タスクの作業ツリーは変更していない。
- Chat用wrapperから `references/document-wording-self-check.md` を必須参照する。現在のChatが `document-wording-review` を `author_self_check` として実施し、別エージェントには委任しない。
- スキルの取得元と版、対象文書の版、実行場所、実際に読んだ範囲、不足資料を `read_evidence` に記録する。資料の省略やハッシュ照合だけを読了としない。
- PC経由では依存確認と既存の検査を同じPCで実施する。通常チャットを明示選択した場合は、読める文章を自分で確認し、利用できない機械検査を未実施として分離する。
- スキル不足、依存不足、接続失敗、対象変更、未実施を成功にせず、無断で別経路へ切り替えない。単独語禁止、用語承認、通常・独立レビューの境界は維持する。
- 設計書の8スキルという記述を、#70単独時の履歴と#69統合後の9スキル構成に分けた。成功・失敗の診断保存は既存のPR #71実装を利用し、接続経路へ重複実装していない。

## 実行環境と資料の取得

Remote Desktop Commanderの接続先はFA780、device IDは `4eae589f-096b-4362-9bec-0f392d77d44f`。作業場所は `C:\Users\donabe\Project\CodexSkill`、ブランチは `issue-69-document-wording-review`。Python 3.14.7、Node.js 24.20.0、Git 2.46.0.windows.1を実行確認した。YAML確認には既存のタスク用venvにあるPyYAML 6.0.3を使用し、グローバルインストールや認証変更は行っていない。

開始時のローカルHEADは74794fdでcleanだった。GitHubから取得した通常レビュー報告と引き継ぎを原文のblob SHAで照合して50ab068へ同期し、mainの署名付きcommitも取得内容からSHA一致を確認して取り込んだ。GitHubへの参照・公開はGitHubコネクタを使った。ローカルのGit信頼設定はこのプロセスと指定パスだけに限定し、PCの恒久設定は変更していない。

未コミットの統合ソースはHEADだけで識別せず、stage treeと `source.json` のファイル別SHA-256を保存した。初回の統合検証treeは `e21cb8b2d498b73e276b15239e1f83ed1feba042`。その後、残っていた8スキル表記と進捗説明を補正したため、公開前に現行内容で再検証する。保存後のcommit SHAとそのCIはPR本文・コメントで記録し、この報告が自分を含む将来SHAを要求することはない。

## Chat自身による自己点検

担当は現在の実装Chat。モードは `author_self_check`。次をPCから取得して読んだ。

| 資料 | 読んだ範囲・比較 |
| --- | --- |
| 新しいChat用自己点検手順 | 全79行。取得、依存確認、結果分離、5つの実行条件例。 |
| `document-wording-review` | 全94行と既存18判断例全48行。追加した入力・実読・read_evidenceを既存の四観点と照合。 |
| Chat実装wrapperとimplementation-worker | #70の元契約と変更差分。経路選択・依存準備・別エージェント禁止を保持。 |
| 専用設計とPC接続設計 | 追加節と変更前後、入力・権限・配布の文脈。 |
| Chat配布設計と階層設計 | 接続・自己点検・配布構成の変更範囲。階層設計の複製は全体のバイト一致も確認。 |
| 作業一覧 | T-004/Phase 9の更新範囲。T-005/Phase 10は取り込み内容を保持。 |

意味・識別性・読みやすさは、今回の追加文章について問題を検出しなかった。用語承認一覧は対象リポジトリにないため承認用法は `not_applicable` とし、暗黙の単独語許可を作っていない。自己点検中に残存した「配布構成は8スキルのまま」という不整合を見つけ、9スキル構成との区別を修正した。これは実装者の自己点検であり、通常レビューの新規findingや独立レビューの合格ではない。

## 実機検証

保存先は `validation-artifacts/issue69-rdc-after70-20260908/`。

| 確認 | 実測結果 |
| --- | --- |
| 共通runnerによるrepository・bundle・zip-integrity・zip-contents | 4処理すべて終了値0。結果JSON/XML、source.json、処理別stdout/stderrを保存。 |
| 必要な実行ファイルがない入力 | `missing-tool`はfailed、終了値はnull、理由とstderrを保存。成功扱いにしない。 |
| 終了値7の入力 | failedとしてstdoutとstderrの識別文字列を保存。成功入力と分けたXMLでは失敗2件。 |
| ZIP内容 | 9ルート、全収録ファイルのバイト列がPC側ソースと一致。新しいChat用参照資料も収録。CRC異常なし。 |
| 再生成 | 同一入力からのZIPがバイト一致。測定値は `921a9ee56d09f7615b5f40180792af3446b8ec0f63c8bb4ce15a0720a3d872b3`。 |
| Pythonと設定 | 3スクリプトのAST解析、Skill front matterとworkflow YAML、always upload、read-only権限、runnerの起動対象を確認。 |
| 設計・差分 | 階層設計2ファイルはバイト一致、git diff --checkで指摘なし。 |

意図的な失敗は診断経路の確認であり、製品テストの成功に読み替えていない。TDDは適用せず、新しいテスト用workflowは追加していない。機械的Markdown用語検査はpackage.json・対象設定・許可一覧がなく、focused/fullとも `unsupported`。文章判定やrepository構造検査でこの状態を上書きしていない。

## 残る確認と公開

通常レビュワーは `chatgpt-pr71-normal-review-20260908`。新しい対象HEADとこの実機証拠を用いて修正確認し、その後に独立最終レビューを行う必要がある。現在のChatはどちらの代行もしていない。

実際の通信切断を発生させる検証、別モデルによる判断精度評価、CI artifactのバイナリ検査、実失敗Actions runからのupload観測は未実施。PC接続障害は実際に起きたと装わず、手順上の停止条件として確認した。既存のPre-release設計とworkflowの不一致は今回の範囲外として維持する。

自己点検の詳細、実行場所、依存状態、コマンド結果は別の引き継ぎ資料へ保持する。PRはドラフトを維持し、PRのマージは行わない。

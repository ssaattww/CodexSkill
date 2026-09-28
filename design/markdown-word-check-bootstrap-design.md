# Markdown用語検査bootstrap設計

## 目的

Issue #87として、CodexSkillのMarkdown用語検査を他リポジトリへ安全に導入するbootstrapを定義する。
CodexSkill自身へ適用する#79 / PR #80は保留し、本設計の完了条件には含めない。

対象リポジトリの実装言語やrootのNode.js構成に依存せず、導入後は対象リポジトリだけで用語検査を実行できる状態を作る。
機械的な用語検査とdocument-wording-reviewによる意味・読みやすさの確認は別の証拠として扱う。

## 導入先の構成

標準ではtools/lint配下に、README、requirements、対象設定、空の許可一覧、checker、実行wrapperを配置する。
with-ci指定時だけ.github/workflows/markdown-word-check.ymlも配置する。
対象リポジトリのroot package.jsonや製品コードは変更しない。Python依存はtools/lint/.venvへ閉じ込める。

## checkerの供給元

用語判定をbootstrap用に再実装しない。
導入時点のCodexSkillにあるskills/review-enforcer/scripts/check-markdown-whitelist-sudachi.pyを対象リポジトリへコピーする。
これによりPR #81で修正された全文走査、明示ファイル検査、日本語許可語境界、半角片仮名処理を再利用する。
供給元checkerが存在しない場合は停止し、簡易checkerへフォールバックしない。

## 初期設定

初期除外はbootstrap自身の生成物と一般的な実行生成物だけに限定する。
reports、docs、design、skillsなど意味を持つ文書ディレクトリは自動除外しない。
許可一覧はentriesが空の状態から開始し、初回auditの結果から大量のentryを自動追加しない。
term、aliases、description、prh、文書対象除外の具体的変更は利用者レビューを要求する。

## auditとenforce

run_markdown_word_check.pyは同じcheckerを使い、モードだけを変える。

audit:
- 未登録語をstdout.logへ保存する。
- checkerのstderrをstderr.logへ保存する。
- result.jsonにchecker終了値、scope、対象HEAD、状態を保存する。
- 未登録語が存在する場合はneeds_user_reviewとする。
- 未登録語だけならwrapperは0で終了するが、合格とは表現しない。
- dependency不足、設定破損、checker実行不能は非0終了する。

enforce:
- auditと同じ診断情報を保存する。
- 未登録語が存在する場合は非0終了する。
- blocking CIへ切り替えるのは対象範囲と初期許可一覧のレビュー後とする。

## scope

fullは対象設定に従う全Markdown、changedはGit差分・stage済み差分・未追跡Markdown、filesは明示ファイルだけを扱う。
明示ファイルが不存在、repo外、除外対象、非対応拡張子の場合は成功扱いしない。

## CIテンプレート

with-ciで導入するworkflowの初期値はauditとする。
Python環境を準備し、requirementsをtools/lint/.venvへ導入し、full auditを実行する。
成功・未登録語・失敗のいずれでもresult.json、stdout、stderrをartifactへ保存する。
enforceへ切り替えた場合は未登録語でworkflowを失敗させる。
CI証拠は対象PR current HEAD SHAとrun head SHAが一致するものだけを採用する。

## 安全境界

bootstrapは既存ファイルを上書きしない。
出力予定pathが1件でも存在する場合は、全書き込み前に衝突一覧を返して停止する。
dry-runでは出力予定pathと供給元checkerを表示し、書き込みを行わない。
初期実装ではforce overwriteを提供しない。
targetはGit worktree rootであることを確認し、repo外pathやroot不明の状態では書き込まない。

## ローカル検証

CodexSkill自身にはTDDを適用しない。
一時fixture repositoryでdry-run、初回導入、再導入時の衝突、audit、enforce、files scopeを確認する。
空許可一覧のauditは未登録語をneeds_user_reviewとして保持し、enforceは非0終了する。
fixture用に承認した複合語を追加した後は該当用例が通ることを確認する。
Windows上のローカル検証をCIより先に実行する。

## 非目標

- #79 / PR #80を再開しない。
- 既存文書を自動翻訳・自動修正しない。
- 未登録語を自動許可しない。
- 意味を持つ文書群をbootstrap判断だけで除外しない。
- prh規則を自動生成しない。
- root package manager設定を変更しない。

## 完了条件

- markdown-word-checkerからbootstrap手順を発見できる。
- bootstrap scriptとrepo-local templateが実装されている。
- audit、enforce、full、changed、filesを区別できる。
- 既存ファイル衝突時に無変更で停止する。
- CIテンプレートが成功・失敗双方の診断artifactを残す。
- fixtureローカル検証が成功している。
- 詳細reportとPR簡易reportを保存する。
- mergeしない。

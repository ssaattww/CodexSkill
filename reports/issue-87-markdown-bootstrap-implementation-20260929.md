# Issue #87 Markdown用語検査bootstrap 実装報告

## 対象と結果

2026-09-29。`ssaattww/CodexSkill` Issue #87 / draft PR #88 を対象に、Markdown用語検査が未導入の他リポジトリへ自己完結した `tools/lint/` を導入するbootstrapを実装・検証した。

- Branch: `issue-87-md-bootstrap`
- Base: `8783a6bec6039ec1325372fa0dc80b2133ba0d3f`
- 技術HEAD: `5f3e7ebaa95935cf9e727ca52ee3e1ec63372265`
- CodexSkill自身への導入である #79 / PR #80 は保留し、本Issueの完了条件へ含めない。
- CodexSkill自身の保守方針に従いTDDは適用せず、設計・構造検査・fixture・package検証を用いた。
- 本Chatは実装担当であり、通常レビューまたは独立最終レビューの合否は出していない。
- mergeは行っていない。

## 実装内容

`markdown-word-checker` から `skills/markdown-word-checker/scripts/bootstrap_markdown_word_check.py` を発見・利用できるようにし、対象Git worktree rootへ次を配置する。

```text
tools/lint/.gitignore
tools/lint/README.md
tools/lint/requirements.txt
tools/lint/markdown-targets.json
tools/lint/markdown-whitelist.yaml
tools/lint/scripts/run_markdown_word_check.py
tools/lint/scripts/check-markdown-whitelist-sudachi.py
.github/workflows/markdown-word-check.yml   # --with-ci指定時のみ
```

bootstrapは対象rootの `package.json` や製品コードを変更しない。Python依存は導入先の `tools/lint/.venv` に閉じる。checkerは別実装せず、導入時点のCodexSkillにあるSudachi checkerをrepo-localへコピーする。

安全境界として、targetがGit worktree rootであることを確認し、出力予定pathが1件でも存在すれば全書き込み前にexit 3で停止する。force overwriteは持たない。`--dry-run` は予定pathとchecker SHA-256だけを表示し、書き込まない。

初期 `markdown-whitelist.yaml` は `entries: []` とする。`term`、`aliases`、`description`、`prh`、文書対象除外はbootstrapが自動追加しない。これらは対象プロジェクトの利用者レビュー後に反映する。

## 実行モード

repo-local runnerは同じcheckerを使い、次を分離する。

- `audit`: 未登録語を `needs_user_review` として保持するが、それだけではwrapperを非0終了にしない。
- `enforce`: 未登録語が残る場合は非0終了する。
- `full`: `markdown-targets.json` に従う全Markdown。
- `changed`: Git差分、stage済み差分、未追跡Markdown。
- `files`: 明示ファイルだけ。

各実行は `result.json`、`stdout.log`、`stderr.log` を指定output directoryへ保存する。不存在・対象除外など、明示filesを安全に検査できない場合は `failed` として成功扱いしない。

CI templateは初期値を `audit` とする。依存導入ログとchecker診断を `tools/lint/artifacts/ci/` へ残し、`always()` で14日間artifact保存する。対象範囲と初期許可一覧のレビュー後にのみ `enforce` へ切り替える設計である。

## CodexSkill側の検証と診断

作業開始時に既存Release workflowを確認したところ、失敗時の標準出力・標準エラー・結果をartifact保存する経路がなかったため、既存 `scripts/run_validation.py` を再接続した。

成功・失敗の両方で次を `skill-validation-<run>-<attempt>` として保存する。

- `results.json`
- `results.xml`
- `source.json`
- 処理別stdout/stderr
- runner stdout/stderr
- `job-status.json`

配布用 `chatgpt-worker-skills.zip` は検証成功時だけ別artifactへ保存する。

## Windows fixture検証

RDMCPからWindows上の `C:\Users\donabe\Project\CodexSkill-issue-87-md-bootstrap` を使用し、`validation-artifacts/` 配下に使い捨てGit repositoryを作成して検証した。

| 確認 | 実測結果 |
| --- | --- |
| dry-run | exit 0。8出力pathを列挙し、対象fixtureへ書き込みなし。 |
| `--with-ci` 初回導入 | exit 0。CI workflowを含む8ファイルを作成。 |
| CIなし初回導入 | exit 0。7ファイルを作成し、`.github/workflows/markdown-word-check.yml` は作成しない。 |
| 再導入 | exit 3。既存8 pathを列挙して停止。 |
| 衝突時原子性 | CIなしfixtureの7導入ファイルをSHA-256前後比較し、変更0件。 |
| 依存導入 | fixture-local venvへ PyYAML 6.0.3 / SudachiPy 0.6.11 / SudachiDict-core 20260428 を導入、exit 0。 |
| full audit | checker exit 1 / state `needs_user_review` / wrapper exit 0。 |
| full enforce | checker exit 1 / state `needs_user_review` / wrapper exit 1。 |
| files audit | state `needs_user_review` / wrapper exit 0。 |
| changed audit | state `needs_user_review` / wrapper exit 0。 |
| 承認済み複合語control | fixture限定で `SIMD テスト document` を承認し、files enforceがstate `pass` / exit 0。 |
| 不存在files | state `failed` / checker exit 2 / wrapper exit 2。 |
| 除外対象files | `tools/lint/README.md` を明示し、state `failed` / checker exit 2 / wrapper exit 2。 |

fixtureでの許可語変更は検証専用であり、CodexSkillまたは実導入先のwhitelistへ反映していない。

## repository検証

技術HEAD `5f3e7ebaa95935cf9e727ca52ee3e1ec63372265` のclean作業ツリーで次を実行した。

```text
python scripts/run_validation.py --output-dir validation-artifacts/issue87-5f3e7eb-clean
```

`repository`、`bundle`、`zip-integrity`、`zip-contents` は全てexit 0。`source.json` のHEADは技術HEADと一致した。存在しないコマンドを使った診断probeではstate `failed`、exit code `null`、stderr log保存を確認した。

repository validatorにはbootstrap設計・script・templateの必須asset検査と、templateへ `__pycache__` / `.pyc` / `.pyo` を混入させない検査を追加している。

## exact-head CI

PR #88の技術HEAD `5f3e7ebaa95935cf9e727ca52ee3e1ec63372265` と完全一致する `pull_request` runだけを確認した。

- Workflow run: `36486562265`
- event: `pull_request`
- attempt: 1
- head SHA: `5f3e7ebaa95935cf9e727ca52ee3e1ec63372265`
- conclusion: `success`
- build job: `109144774109`
- 診断artifact: `skill-validation-36486562265-1` / ID `10999621964` / 39,617 bytes
- 配布artifact: `chatgpt-worker-skills-36486562265` / ID `10999357159` / 22,904 bytes

別SHAのrunは代用していない。詳細reportを含む永続化commitのSHAは本文生成時点では未確定であるため自己参照せず、そのcommit後のcurrent HEAD一致CIはPR本文・コメントで別途記録する。

## 文書自己点検

現在の実装Chatがbootstrap設計、markdown-word-checkerのbootstrap手順、template README、task/phase更新、本詳細reportを実際に読み、意味・識別性・読みやすさを自己点検した。機械的用語検査や構造検査の成功を文章品質の証拠には置き換えていない。今回の変更範囲では必須の文章指摘を検出しなかった。この自己点検は通常レビューまたは独立最終レビューの代用ではない。

## 残る確認とリスク

- 生成するGitHub Actions template自体を別の実リポジトリへpushしてLinux runnerで実行する確認は、このIssueでは未実施。templateはGitHub Actions/Linux用pathを持ち、Windows fixtureと同じrepo-local設定を使用する。
- 実導入先のwhitelist、aliases、prh、意味を持つ文書除外は利用者承認が必要であり、bootstrapは決定しない。
- `document-wording-review` による意味・読みやすさ評価は機械的用語検査とは別証拠であり、本bootstrapは代替しない。
- 通常レビューと独立最終レビューは未実施。実装者のfixture確認をその代用にしない。
- PRはdraftを維持し、mergeしない。

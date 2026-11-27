# CodexSkill PR #89 consumer skill symlink 対応報告

日付: 2026-10-01

## 目的

consumer repository から CodexSkill の `skills/` を参照する手順が `ln -s` など OS 固有コマンドに寄らないようにし、Windows と Unix 系環境で同じ入口を使えるようにする。

## 変更

- `scripts/link_consumer_skills.py` を追加した。
- CodexSkill checkout の `skills/` を source とし、consumer repository の `.agents/skills` へディレクトリ symlink を作成する。
- 既に同じ target を指す symlink がある場合は成功扱いにし、再実行を冪等にした。
- 既存の実ディレクトリ、壊れた symlink、別 target の symlink は自動置換せず失敗する。
- Windows で symlink 作成権限が無い場合は、管理者権限または Developer Mode が必要であることを明示する。
- `AGENTS.md` に、consumer repository の Skill link は OS 固有の `ln -s` / `mklink` を直接手順化せず helper を使う方針を追加した。
- `skills/review-enforcer/scripts/run-cspell-markdown.js` は Windows の `.cmd` 直接起動をやめ、`node` から CSpell の JavaScript CLI を直接起動するよう修正した。

## Windows 検証

管理者権限で動作する Windows 環境で次を確認した。

- 新規 consumer repository への `.agents/skills` 作成: 成功。
- `Path.is_symlink()`: `True`。
- symlink target: `C:\Users\donabe\RemoteDesktopWorkspace\CodexSkill\skills`。
- 同一 consumer repository への再実行: `Skill symlink already configured` として成功。
- Duck PR #30 からこの checkout の `skills/` を symlink 参照し、CSpell を含む全 Markdown lint 18文書が終了値0。

## Repository validation

`python scripts/run_validation.py --output-dir C:\Users\donabe\RemoteDesktopWorkspace\CodexSkill-validation-pr-002`

結果:

- repository: pass
- bundle: pass
- zip-integrity: pass
- zip-contents: pass

診断 artifact は `C:\Users\donabe\RemoteDesktopWorkspace\CodexSkill-validation-pr-002` に保存した。

## Pull request

- PR: #89
- branch: `fix/cross-platform-skill-symlink`
- symlink helper commit: `e6deafa`
- Windows CSpell launch commit: `583a959`

## レビュー指摘対応

前回レビューで残った3点を追加対応した。

- Markdown hook の CSpell 実行可否判定を、`.bin/cspell(.cmd)` ではなく実際の runner と同じ `node_modules/cspell/bin.mjs` の存在確認へ統一した。commit: `a11895f`。
- `scripts/link_consumer_skills.py` で `.agents` の作成自体が失敗した場合も `OSError` を捕捉し、traceback ではなく診断を標準エラーへ出して終了コード2を返すようにした。commit: `9e55755`。
- consumer repository の `.agents/skills` から checkout の `skills/` への symlink 契約、既存pathを自動置換しない方針、Windows権限不足時の扱いを Skill hierarchy の正本設計と同期コピーへ追記した。commit: `5f05536`。

## レビュー指摘対応の検証

- `python -m py_compile scripts/link_consumer_skills.py skills/markdown-word-checker/hooks/post_tool_use_markdown_lint.py`: 成功。
- `.agents` が実ファイルの一時consumer fixture: `Failed to prepare consumer skill link directory ...` を出力し、終了コード2。tracebackなし。
- `.bin/cspell.cmd` を作らず `node_modules/cspell/bin.mjs` だけを置いた一時fixture: focused lint 判定は `pass` となり、`run-cspell-markdown.js` 実行経路まで到達。
- `design/skill-hierarchy-design.md` と `skills/design/skill-hierarchy-design.md` の byte 比較: 一致。
- `python scripts/verify_skill_repository.py`: pass。
- `python scripts/run_validation.py --output-dir C:\\Users\\donabe\\RemoteDesktopWorkspace\\CodexSkill-validation-pr89-followup-20261001-0652`: repository / bundle / zip-integrity / zip-contents がすべて pass。
- CodexSkill には repo-local `tools/lint/` と `package.json` の Markdown lint wiring が無いため、`markdown-word-checker` の focused lint は `unsupported`。追加設計文の inline code は path、command、identifier に限定されていることを確認した。

## 独立レビュー PR89-IR-001 対応

独立レビューで、consumer/destination boundary が helper 実装で強制されていない点が指摘された。

- `scripts/link_consumer_skills.py` は CodexSkill checkout 自身またはその配下を consumer repository として拒否する。commit: `5d98a6d`。
- 既存 `.agents` は consumer repository 内の実ディレクトリだけを許可し、symlink、Windows reparse point、非ディレクトリを拒否する。
- `.agents` を新規作成した場合も、その実体が consumer repository 内に解決されることを確認してから `skills` symlink を作成する。
- Skill hierarchy 正本と同期コピーへ同じ境界契約を追記した。commit: `cbad114`。

### PR89-IR-001 focused verification

- CodexSkill checkout 自身を consumer に指定: exit 2、拒否。
- CodexSkill checkout 配下の `reports/` を consumer に指定: exit 2、拒否。
- consumer 外ディレクトリへ向く `.agents` symlink: exit 2、外部側へ `skills` を作成しない。
- `.agents` が未作成の通常 consumer: exit 0、実ディレクトリ `.agents` と `skills` symlink を作成。
- `.agents` が既存実ディレクトリの通常 consumer: exit 0、`skills` symlink を作成。
- `design/skill-hierarchy-design.md` と `skills/design/skill-hierarchy-design.md` の byte 比較: 一致。
- `python scripts/verify_skill_repository.py`: pass。
- `python scripts/run_validation.py --output-dir C:\\Users\\donabe\\RemoteDesktopWorkspace\\CodexSkill-validation-pr89-ir001-20261001-0818`: repository / bundle / zip-integrity / zip-contents がすべて pass。


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

## Windows 検証

管理者権限で動作する Windows 環境で次を確認した。

- 新規 consumer repository への `.agents/skills` 作成: 成功。
- `Path.is_symlink()`: `True`。
- symlink target: `C:\Users\donabe\RemoteDesktopWorkspace\CodexSkill\skills`。
- 同一 consumer repository への再実行: `Skill symlink already configured` として成功。

## Repository validation

`python scripts/run_validation.py --output-dir C:\Users\donabe\RemoteDesktopWorkspace\CodexSkill-validation-pr-001`

結果:

- repository: pass
- bundle: pass
- zip-integrity: pass
- zip-contents: pass

診断 artifact は `C:\Users\donabe\RemoteDesktopWorkspace\CodexSkill-validation-pr-001` に保存した。

## Pull request

- PR: #89
- branch: `fix/cross-platform-skill-symlink`
- implementation commit: `e6deafa`


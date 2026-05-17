# ChikkarPy 語彙グルーピング レビュー記録

## 対象

- `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py`
- `skills/review-enforcer/SKILL.md`
- `design/review-enforcer-markdown-whitelist-rebuild-design.md`
- IbisDuck 側の `tools/lint/README.md`
- IbisDuck 側の `tools/lint/requirements.txt`

## 変更概要

- SudachiPy 語彙抽出に ChikkarPy の同義語候補を加えた。
- TSV / JSON 出力に `synonyms` を追加した。
- `groupKey` は ChikkarPy 候補がある場合に同義語候補グループへ寄せる。
- ChikkarPy 候補は whitelist や prh へ自動反映しない方針を設計書と Skill に明記した。
- IbisDuck の文書検査環境に ChikkarPy と build helper を追加し、`PIP_NO_BUILD_ISOLATION=1` を使う準備手順を記録した。

## 検証

- `python3 -m py_compile skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py`
- `PIP_NO_BUILD_ISOLATION=1 .codex-doc-lint-venv/bin/python -m pip install -r tools/lint/requirements.txt`
- `.codex-doc-lint-venv/bin/python .agents/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py --files tools/lint/README.md`
- `.codex-doc-lint-venv/bin/python .agents/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py --files tools/lint/README.md --synonyms none`
- `. .codex-doc-lint-venv/bin/activate && npm --silent run lint:md:vocab -- --files tools/lint/README.md --format json`

## 既知の未解消事項

- `. .codex-doc-lint-venv/bin/activate && npm run lint:md:whitelist -- --files tools/lint/README.md` は失敗する。
- 失敗理由は、既存 whitelist がまだ日本語語彙を再構築していないためであり、今回の変更で大量自動追加はしていない。
- `tools/lint/markdown-whitelist.yaml` の変更は利用者の明示レビューが必要なため、この作業では追加していない。

## レビュー結果

阻害指摘なし。

- ChikkarPy 同義語候補は `extract-markdown-vocabulary-sudachi.py` の出力用 `synonyms` と `groupKey` 更新だけに使われており、`tools/lint/markdown-whitelist.yaml` や `tools/lint/prh.yml` を自動更新する処理は確認されなかった。該当箇所: `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:75`, `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:361`, `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:459`, `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:481`
- `--synonyms none` は `argparse` の選択肢として残っており、指定時は ChikkarPy 初期化を通らず SudachiPy 抽出だけで TSV / JSON を出力できることを実行確認した。該当箇所: `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:95`, `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:75`
- TSV は `synonyms` 列を `count` の前に追加し、JSON は `synonyms` を配列として追加している。既存フィールド名は維持されており、今回確認した出力は妥当だった。該当箇所: `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:459`, `skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py:481`
- Skill と設計書は、ChikkarPy 候補を `aliases` / `prh` へ自動変換しない方針を明記している。該当箇所: `skills/review-enforcer/SKILL.md:85`, `design/review-enforcer-markdown-whitelist-rebuild-design.md:93`
- IbisDuck の環境構築メモは `PIP_NO_BUILD_ISOLATION=1` と build helper 前提を記載しており、Python 3.12.3 の既存検査環境で既定の ChikkarPy 経路と `--synonyms none` 経路が動作することを確認した。該当箇所: `/home/ibis/ssl/IbisDuck/tools/lint/README.md:13`, `/home/ibis/ssl/IbisDuck/tools/lint/README.md:16`, `/home/ibis/ssl/IbisDuck/tools/lint/requirements.txt:1`

## 対応

実行したコマンド:

- `nl -ba /home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md`
- `nl -ba /home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md`
- `nl -ba /home/ibis/AI/CodexSkill/reports/chikkarpy-vocabulary-groups-review-20260517135422.md`
- `git -C /home/ibis/AI/CodexSkill diff --unified=80 HEAD -- skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py skills/review-enforcer/SKILL.md design/review-enforcer-markdown-whitelist-rebuild-design.md`
- `git -C /home/ibis/ssl/IbisDuck diff --unified=80 HEAD -- tools/lint/README.md tools/lint/requirements.txt`
- `nl -ba /home/ibis/AI/CodexSkill/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py`
- `nl -ba /home/ibis/AI/CodexSkill/design/review-enforcer-markdown-whitelist-rebuild-design.md`
- `nl -ba /home/ibis/ssl/IbisDuck/tools/lint/README.md`
- `nl -ba /home/ibis/ssl/IbisDuck/tools/lint/requirements.txt`
- `PYTHONDONTWRITEBYTECODE=1 python3 -c "import ast, pathlib; ast.parse(pathlib.Path('skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py').read_text(encoding='utf-8'))"`
- `PYTHONDONTWRITEBYTECODE=1 .codex-doc-lint-venv/bin/python .agents/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py --files tools/lint/README.md --synonyms none`
- `PYTHONDONTWRITEBYTECODE=1 .codex-doc-lint-venv/bin/python .agents/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py --files tools/lint/README.md --format json --synonyms none`
- `PYTHONDONTWRITEBYTECODE=1 .codex-doc-lint-venv/bin/python .agents/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py --files tools/lint/README.md`
- `python3 --version`
- `PYTHONDONTWRITEBYTECODE=1 .codex-doc-lint-venv/bin/python -c "import sys; print(sys.version)"`
- `rg -n "partOfSpeech|groupKey|synonyms|lint:md:vocab|extract-markdown-vocabulary-sudachi" /home/ibis/AI/CodexSkill /home/ibis/ssl/IbisDuck --glob '!**/.git/**' --glob '!**/node_modules/**' --glob '!**/__pycache__/**'`

確認した主要ファイル:

- `/home/ibis/AI/CodexSkill/skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py`
- `/home/ibis/AI/CodexSkill/skills/review-enforcer/SKILL.md`
- `/home/ibis/AI/CodexSkill/skills/sub-agent-task-manager/SKILL.md`
- `/home/ibis/AI/CodexSkill/design/review-enforcer-markdown-whitelist-rebuild-design.md`
- `/home/ibis/ssl/IbisDuck/tools/lint/README.md`
- `/home/ibis/ssl/IbisDuck/tools/lint/requirements.txt`
- `/home/ibis/ssl/IbisDuck/package.json`

未解消リスク:

- IbisDuck の作業ツリー差分では `tools/lint/markdown-whitelist.yaml` と `tools/lint/prh.yml` に変更はなかった。一方で `main...HEAD` のブランチ差分には同 2 ファイルの追加が含まれるため、ブランチ全体の whitelist 利用者レビュー済み状態はこのレビューでは判定していない。
- `npm run lint:md:whitelist -- --files tools/lint/README.md` の既知失敗は、既存 whitelist 再構築前であることを既存レポートの記載として確認したが、このレビューでは修正対象外とした。

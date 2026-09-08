# Issue #70 Remote Desktop Commander既定化 追補報告

## 変更

利用者指示により、ChatGPT workerの基本経路をRemote Desktop CommanderによるPC接続へ変更した。

- 利用者の明示指定を最優先し、その次にProject Instructionを適用する。
- どちらにも経路指定がない場合はRemote Desktop Commanderを使用する。
- 通常チャットは利用者またはProject Instructionが明示した場合だけ使用する。
- PC接続が失敗した場合は通常チャットや別PCへ無断で切り替えず、依存作業を停止する。

実装、レビュー、報告の3 wrapper、専用設計、worker設計、Project Instruction例、階層設計2ファイルを同期した。配布する8 Skillの構成は変更していない。

## 検証

Windowsの専用ワークツリー `C:/Users/donabe/Project/CodexSkill-issue-70` で `scripts/verify_skill_repository.py`、8 Skill ZIP生成、`git diff --check` を実行し成功した。ローカルのstaged tree `f90694e96fcb530695239bd36c70bfbbf09bdbbe` とGitHubコネクタで作成したtreeが一致した。

実装commitは `81770b3546edb89a39635b15d75932bca51c719f`。この追補報告保存後のPR current HEADに一致するCIだけを最終確認対象とする。

作業中に誤って `tmp-ignore` を追加したcommitと直後に削除したcommitが履歴へ残ったが、削除後のtreeは変更前と同一であり、最終成果物に `tmp-ignore` は存在しない。

通常・独立レビューは未実施。マージは行わない。

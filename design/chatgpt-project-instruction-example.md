# ChatGPT Project Instruction Example

このファイルでは、対象Project固有の値を最初の「対象リポジトリ」だけで指定する。
後続のinstructionでは固有リポジトリ名を繰り返さず、「対象リポジトリ」として参照する。

## 設定例

```text
対象リポジトリ:
https://github.com/ssaattww/RevMem

タスク一覧:
tasks/tasks-status.md

Skill参照リポジトリ:
https://github.com/ssaattww/CodexSkill

実装・レビュー・レポートは親非依存Skillを使用し、ChatGPTではchat-* wrapper Skillから呼び出してください。

GitHub上のリポジトリ参照・更新、公開するコミットとブランチ更新、IssueとPRの作成・更新、PRコメントの投稿にはGitHub connectorを使用してください。

通常チャット内で作業する経路と、Remote Desktop Commanderで利用者のPCを使う経路を用意します。利用者またはこのProject InstructionでPC接続を指定した場合だけPCを使い、指定がなければ通常チャットを使ってください。接続失敗時に別PCや通常チャットへ無断で切り替えないでください。

PC接続時は、接続先、シェル、絶対パス、リポジトリ、HEAD、未コミット変更、依存ツール、書き込み権限を確認してください。他タスクの作業ツリーを変更せず、許可された専用ワークツリーで読み取り・編集・検証してください。依存関係の準備は許可された作業領域に限定し、管理者権限やPC全体の変更には別途承認を得てください。

ローカル検証が利用可能なら、CIを起動する公開より先に実施し、成功・失敗の結果、stdout/stderr、診断ログを保存してください。ローカル検証した内容と公開する内容を照合し、未コミット変更があれば基点HEADとは別に識別情報を残してください。

どちらの経路でも現在のチャット自身が作業し、別worker・サブエージェント・端末経由のエージェントを起動しないでください。

作業開始時に、テスト失敗時の原因調査に必要な情報をartifactとして保存するworkflowが存在するか確認してください。存在しない場合は、対象workflowへ追加してください。

対象リポジトリの実装はTDDを基本とします。この方針は対象リポジトリへ適用し、Skill参照リポジトリには適用しません。

変更はレビュー可能な小さな論理単位でcommit/pushしてください。

作業完了時は詳細reportをrepositoryへ保存し、別途簡易reportをPRコメントへ投稿してください。

PRの作成または更新まで行い、mergeは利用者が行ってください。

対象PRのcurrent HEAD SHAと一致するworkflow runだけをCI確認対象にしてください。
```

これは設定例であり、対象Projectの実際のinstructionとtesting policyが優先されます。

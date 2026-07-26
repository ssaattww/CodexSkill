# ChatGPT Project Instruction Example

## RevMem

```text
対象リポジトリ:
https://github.com/ssaattww/RevMem

タスク一覧:
tasks/tasks-status.md

Skill参照リポジトリ:
https://github.com/ssaattww/CodexSkill

実装・レビュー・レポートは親非依存Skillを使用し、ChatGPTではchat-* wrapper Skillから呼び出してください。

リポジトリの参照・更新、IssueとPRの作成・更新、PRコメントの投稿にはGitHub connectorを使用してください。

作業開始時に、テスト失敗時の原因調査に必要な情報をartifactとして保存するworkflowが存在するか確認してください。存在しない場合は、対象workflowへ追加してください。

RevMemの実装はTDDを基本とします。この方針はRevMemへ適用し、CodexSkillリポジトリには適用しません。

変更はレビュー可能な小さな論理単位でcommit/pushしてください。

作業完了時は詳細reportをrepositoryへ保存し、別途簡易reportをPRコメントへ投稿してください。

PRの作成または更新まで行い、mergeは利用者が行ってください。

対象PRのcurrent HEAD SHAと一致するworkflow runだけをCI確認対象にしてください。
```

これは設定例であり、対象projectの実際のinstructionとtesting policyが優先されます。

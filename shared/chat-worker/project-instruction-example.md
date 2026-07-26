# ChatGPT Project Instruction Example

## RevMem

```text
対象リポジトリ:
https://github.com/ssaattww/RevMem

タスク一覧:
tasks/tasks-status.md

共通Skill契約と実行アダプターの参照リポジトリ:
https://github.com/ssaattww/CodexSkill

必要な作業手順、共通契約、Codex向け実行方式、ChatGPT向け実行方式は、この参照リポジトリを確認してください。

リポジトリの参照・更新、IssueとPRの作成・更新、PRコメントの投稿にはGitHub connectorを使用してください。

作業開始時に、テスト失敗時の原因調査に必要な情報をartifactとして保存するworkflowが存在するか確認してください。存在しない場合は、対象workflowへ追加してください。artifactには、少なくともテスト結果、標準出力、標準エラー、および失敗原因の調査に必要なログを含めてください。

RevMemの実装はTDDを基本とし、先にテストを追加して失敗を確認してから実装してください。このTDD方針と診断artifact workflowの追加方針はRevMemの実装作業に適用し、参照先のCodexSkillリポジトリには適用しません。

変更は、レビュー可能な小さな論理単位でcommit/pushしてください。

作業完了時は、詳細reportをrepositoryへ保存してください。それとは別に、変更内容と検証結果を要約した簡易reportをPRコメントへ投稿してください。

PRの作成または既存PRの更新まで行ってください。mergeは利用者が行うため、workerはmergeしないでください。

「最新のworkflow run」ではなく、対象PRのcurrent HEAD SHAとrunのhead SHAが一致するworkflow runだけをCI確認の対象としてください。HEAD更新後は新しいHEADに紐づくrunを確認してください。一致するrunがない場合はCI未実施として報告し、別SHAのrunを代用しないでください。
```

This file is a configuration example. The target project owns its actual Project Instruction and testing policy.

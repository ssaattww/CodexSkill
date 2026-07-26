# Issue #51 ChatGPT Chat Worker Skill 実装レポート R6

## 概要

PR #52の設計書へ、RevMemで使用するProject Instructionの完成例を追加した。

利用者が提示した内容を、Project Instructionへそのまま設定できる文章として整理し、曖昧だったCI確認対象とworkerの責務境界を明確化した。

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- PR: #52
- Branch: `agent/issue-51-chat-worker-skills`
- 更新前HEAD: `bf583f24203246dad0979cda0c7479795a5f8e4e`
- 設計書更新commit: `2b0392c502d70d3fb71cb898b1acbd253ed8c362`
- 対象ファイル: `design/chat-worker-skill-design.md`

## 反映したProject Instruction

次の固定情報と運用規則を、コピー可能な`text` blockとして設計書へ追加した。

- 対象repository: `https://github.com/ssaattww/RevMem`
- task list: `tasks/tasks-status.md`
- Codex用Skill参照先: `https://github.com/ssaattww/CodexSkill`
- repository、Issue、PR、PR commentの操作にGitHub connectorを使用する
- 作業開始時に、テスト失敗時の診断artifactを保存するworkflowの有無を確認し、存在しなければ追加する
- TDDを基本とし、テスト追加と失敗確認を実装より先に行う
- 変更をレビュー可能な小さな論理単位でcommit/pushする
- 詳細reportとは別に、変更内容と検証結果を要約した簡易reportをPR commentへ投稿する
- workerはPR作成・更新まで行い、mergeは利用者が行う
- repository全体の「最新run」ではなく、対象PRのhead branchのcurrent HEAD SHAとhead SHAが一致するworkflow runだけをCI確認対象とする
- HEAD更新後は、更新後のSHAに紐づくrunを改めて確認する

## 推敲方針

- repository内のpath表記を`tasks/tasks-status.md`へ統一した
- 「細かくpush」を「レビュー可能な小さな論理単位でcommit/push」と具体化した
- artifactにはテスト結果と原因調査に必要なログを含めることを明記した
- merge禁止と、workerが担当するPR作成・更新までの境界を一文で示した
- CI runの選択条件を`head SHA`一致として明示した

## 変更範囲

Project Instruction例を設計書へ追加した。Skill本体、product code、test、workflowは変更していない。

## 検証

更新後のbranchから`design/chat-worker-skill-design.md`を再取得し、次を確認した。

- 3つのURL/pathが正しい
- 利用者が提示した全運用規則が記載されている
- instruction例が閉じたcode blockとして成立している
- 既存のChat prompt方針およびCodexSkill固有の検証方針を変更していない

CodexSkill repositoryには有効なMarkdown lintまたは正式なSkill schema検証がないため、このdocumentation-only変更のための形式的なtestは追加・実行していない。

## CI確認方針

本report追加後のPR head SHAを取得し、そのSHAに紐づくworkflow runだけを確認する。repository全体の「最新run」は使用しない。結果はreportとは別にPR commentへ記録する。

## マージ

マージは実施しない。

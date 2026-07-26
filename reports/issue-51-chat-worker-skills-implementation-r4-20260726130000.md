# Issue #51 ChatGPT Chat Worker Skill 実装レポート R4

## 概要

利用者が親として複数のChatGPT chatを運用するときに、新規chatを立ち上げる時点、既存chatを継続する時点、および各段階で使用するpromptを設計書へ追加した。

## 対象

- Repository: `ssaattww/CodexSkill`
- PR: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Scope: 利用者向けworkflow例とprompt例の追加
- Non-goals: worker Skillの責務変更、既存Codex向けSkill変更、merge

## TDD

### Red

先に`tests/test_chat_worker_skills_contract.py`へ次の設計contractを追加した。

- `## 利用者向け実行例`
- Chat A: 初回実装
- Chat B: 初回レビュー
- Chat Aを継続: レビュー対応
- Chat C: 修正確認
- Chat D: 独立最終レビュー
- 新規chatへ送るprompt
- 既存chatへ送るprompt
- handoff path

Red commit:

- `840eb50c92c0d477ed4c406b3ac2d04d68538fe3`

### Green

次の2設計書へ同一内容を追加した。

- `design/chat-worker-skill-design.md`
- `skills/design/chat-worker-skill-design.md`

設計書はbyte-identicalである。

## 追加した利用者flow

### Chat A

- 初回実装時に新規作成する
- review follow-upでも同じchatを継続する
- TDD、PR更新、handoff保存を担当する

### Chat B

- 初回レビュー用に新規作成する
- 実装chatとは分離する
- planned coverageを最後まで実施する

### Chat C

- 修正確認用に原則新規作成する
- 前回finding、修正diff、直接影響、同種欠陥へ確認範囲を限定する

### Chat D

- 独立最終レビュー用に必ず新規作成する
- 過去reviewの結論を前提にせず、最終HEADをfreshに確認する

### Report chat

- workerが詳細reportを配置済みなら省略できる
- 複数handoffの統合やrepository固有templateへの整形が必要な場合だけ新規作成する

## Prompt例

設計書へ次の完成prompt例を追加した。

- 初回実装chatの開始prompt
- 初回レビューchatの開始prompt
- 既存実装chatへレビュー対応を依頼するprompt
- 修正確認chatの開始prompt
- 独立最終レビューchatの開始prompt
- report-only chatの開始prompt

各promptにはrepository、Issue/PR、HEAD SHA、handoff path、許可操作、禁止操作、merge禁止を含めた。

## Handoff運用

- 新規chatへはhandoff pathまたはGitHub URLを明示的に渡す
- repositoryへ保存できない場合はpacket全文をcopy and pasteする
- 前chatの会話履歴や権限を自動継承しない

## 検証

設計書更新後HEAD:

- `61d9ef59d94579a244374b501617da41f346efb9`

同HEADに紐づくWorkflow Run:

- Workflow: `Chat worker skill contract`
- Run ID: `30187029412`
- Conclusion: `success`

別branchまたは別SHAのrunを判定に使用していない。

## 残存事項

- 実際の複数ChatGPT chatでのoperational trialは未実施
- prompt例はrepository、Issue、PR、pathをplaceholderとしており、利用時に利用者が置換する

## マージ

マージは実施していない。

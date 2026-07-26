# Issue #51 ChatGPT chat worker Skill 実装報告 R3

## 概要

利用者が親として独立したChatGPT chatを起動する前提で、standalone worker Skillとchat間handoff transportを更新した。

## 対応内容

- `skills/chat-implementation-worker/SKILL.md`を英語化
- `skills/chat-review-worker/SKILL.md`を英語化
- `skills/chat-report-writer/SKILL.md`を英語化
- shared handoff contractを英語化
- 日本人利用者向け設計書2ファイルを日本語でbyte-identicalに同期
- handoff packetはchat間で自動共有されないことを明文化
- 標準transportとして`reports/handoffs/`へのrepository-backed保存を定義
- write不可時のcopy and paste fallbackを定義
- `write_handoff`権限と`handoff_transport.packet_path`をcontractへ追加
- 前workerの権限を次chatへ自動継承しない契約を維持

## Handoff packetの運用

前chatがpacketを出力しただけでは、別chatから自動参照できない。

標準運用は次のとおり。

1. workerがpacketを`reports/handoffs/`へ保存する
2. 利用者が次chatへrepository pathまたはGitHub URLを渡す
3. 次chatがconnectorでそのfileを読む

`write_handoff`がない場合は、workerがpacket全文を返し、利用者が次chatへcopy and pasteする。

## TDD・診断

### 追加contract Red

- Commit: `4d630a94182e54273f5c6048c049dce4e056d73e`
- 英語SKILL.mdとdurable handoff transportを要求するtestを先行追加

### 初回Green移行時の失敗

- HEAD: `477636a04bb242205a4d85ea6ca38d3aeb0650fa`
- Run: `30186698944`
- 結果: failure
- 原因: contract testの見出し期待値が小文字、実contractが`Repository-backed transport`で不一致
- Artifact: `chat-worker-skill-contract-diagnostics-30186698944-1`
- Artifact ID: `8627248025`

### Final Green

- HEAD: `a79f338f5acdc4a4149bc291ad28e0bed1080716`
- Run: `30186753613`
- Workflow: `Chat worker skill contract`
- Conclusion: success

## 変更ファイル

- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`
- `skills/chat-worker-shared/references/handoff-contract.md`
- `design/chat-worker-skill-design.md`
- `skills/design/chat-worker-skill-design.md`
- `tests/test_chat_worker_skills_contract.py`

## Scope保護

既存Codex向けorchestrator、delegation、sub-agent実行contractは変更していない。PR #50のreview coverage変更も取り込んでいない。

## 残存事項

- 独立review
- review指摘がある場合のfollow-up
- review通過後のPR ready化

マージは行っていない。

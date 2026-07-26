# Issue #51 ChatGPT Chat Worker Skill 実装レポート R2

## 対象

- Repository: `ssaattww/CodexSkill`
- Issue: #51
- Pull Request: #52
- Branch: `agent/issue-51-chat-worker-skills`
- Base: `main`
- 実装確認HEAD: `34641942a3af72b76a25093179a01f774acb8def`

## R2の目的

初回実装では、利用者が親として3つのworker chatを順番に起動し、構造化handoffを渡す責務分離を実装した。

追加のcontract reviewにより、次の可搬性条件が不足していることが判明した。

- ChatGPTの別chatは、前chatの最終応答を自動的には参照できない
- ChatGPT向け`SKILL.md`は、別環境へ移植しやすい英語記述にする必要がある
- handoffを次chatへ実際に渡すtransportが必要である
- implementation workerがhandoff fileを書いても、narrative report責務を持ったことにはしない境界が必要である

R2ではこれらを追加した。

## 追加したcontract

### Skill本文の英語化

次の3ファイルを英語化した。

- `skills/chat-implementation-worker/SKILL.md`
- `skills/chat-review-worker/SKILL.md`
- `skills/chat-report-writer/SKILL.md`

設計理由は日本語の設計書へ残し、Skill本体には実行規則だけを記載した。

### Handoff transport

`skills/chat-worker-shared/references/handoff-contract.md`へ次を追加した。

#### Repository-backed transport

- `write_handoff`が許可されている場合に使用する
- packetを`reports/handoffs/`へ保存する
- filenameは`<task-id>-<producer>-<mode>-<head-short>-<timestamp>.md`を基準にする
- Markdown内へcanonical YAML packetを保持する
- pathを`handoff_transport.packet_path`へ記録する
- 利用者がpathまたはGitHub URLを次chatへ渡す
- 次chatはrepository connectorでそのfileを読む

#### Copy and paste transport

- `write_handoff`が許可されていない場合に使用する
- workerは最終応答へpacket全文を返す
- 利用者がpacket全文を次chatへ貼り付ける
- summaryだけをhandoff transportとして扱わない

### Handoff fileとnarrative reportの分離

Handoff fileはchat間で作業状態を運ぶstructured execution evidenceである。

- implementation workerはhandoff fileを書ける
- implementation workerはnarrative implementation reportを作成しない
- narrative reportは`chat-report-writer`の責務である

この区別により、「実装だけのSkill」と、実際に次chatへ渡せるdurable handoffを両立した。

### Permission contract

- `write_handoff`を`authorized_actions`へ追加した
- current workerのtop-level権限は次chatへ継承しない
- `next_chat_input.requested_authorized_actions`は提案であり、権限付与ではない
- 利用者が次chat用のtop-level権限を改めて付与する
- 新しい権限付与がない場合、次workerはread-onlyとする

## 設計更新

次の2ファイルをbyte-identicalに更新した。

- `design/chat-worker-skill-design.md`
- `skills/design/chat-worker-skill-design.md`

設計書へ次を追加した。

- Skill本文は英語、利用者向け設計書は日本語とする言語方針
- 前chatのpacketは次chatから自動的には参照できないこと
- `reports/handoffs/`を使うrepository-backed transport
- copy and paste fallback
- `write_handoff`と次chat権限再付与
- implementation handoffとnarrative reportの責務差

## TDD証跡

### Portability contract Red

- HEAD: `0c3e6479a4fe6b4ed999e389297cb2005177037c`
- Workflow Run: `30186554823`
- Result: failure
- Diagnostic artifact:
  - ID: `8627208829`
  - Name: `chat-worker-skill-contract-diagnostics-30186554823-1`

検出内容:

- 3つの`SKILL.md`が日本語を含む
- `write_handoff`がない
- `handoff_transport`と`packet_path`がない
- `reports/handoffs/`がない
- packetが別chatから自動参照できないことを設計で固定していない

### Skill・contract移行中のRed

- HEAD: `a403dfaa31e088e6aeb824793ecbe9d4dbf4006c`
- Workflow Run: `30186633760`
- Result: failure
- Diagnostic artifact:
  - ID: `8627230307`
  - Name: `chat-worker-skill-contract-diagnostics-30186633760-1`

この時点で3つのSkill本文は英語化済みだったが、設計書とshared contractの表現がcontract testを満たしていなかった。

### Final Green before R2 reports

- HEAD: `34641942a3af72b76a25093179a01f774acb8def`
- Workflow Run: `30186704991`
- Result: success
- Job: `contract`
- `Checkout target branch HEAD`: success
- `Verify checked out HEAD`: success
- `Run chat worker skill contract`: success

R2 report追加後の最終HEAD runはPR commentへ記録する。

## Scope保護

- 既存Codex向けSkillを変更していない
- 既存Codex向けhierarchyを変更していない
- PR #50のbranchまたは未merge変更を取り込んでいない
- ChatGPT worker、shared contract、ChatGPT向けdesign、contract test、workflow、Issue #51 reportだけを変更した
- mergeしていない

## Remaining risks

- 実際の複数ChatGPT chatでrepository-backed handoffとcopy/paste handoffを一連で試すoperational trialは未実施である
- handoff packetはMarkdown contractであり、JSON Schemaによる値型の完全検証は今回のscope外である

## 結果

ChatGPT向けworker bundleを、別chatが前chatを自動参照できない実行環境でも使用できる構成へ更新した。

# Issue #13 Sol高コストprofile承認gate 追補レポート

## メタデータ

- repository: `ssaattww/CodexSkill`
- Issue: `#13 sub-agentの使用モデル`
- PR: `#65 feat: task特性に応じてsub-agent profileを自動選定する`
- branch: `feat/adaptive-agent-assignment`
- user request date: `2026-08-27`
- development policy: CodexSkill repository maintenanceはnon-TDD

## 追加要求

コスト最適化のため、次のprofileは自動選定・自動dispatchせず、ユーザーへ提案して処理を停止し、明示的な了承を得た後だけ選択する。

- `Sol xhigh`
- `Sol max`

## 実装内容

### `agent-profile-selection.md`

- `Sol xhigh` / `Sol max`をmandatory user-approval gate対象に変更した。
- automatic classificationやrepository policyが該当profileを要求しても、まず`proposed_profile`として保持する。
- proposal時にSol `high`では不足する理由と、higher reasoning effortによるexecution cost増加をユーザーへ提示する。
- approval前は`requested: null`、`applied: null`、`application_status: awaiting_user_approval`とする。
- current taskでの明示的なuser instructionのみapproval evidenceとして扱う。
- repository policy、過去の別taskでのapproval、silence、inferred preferenceはapprovalとして扱わない。
- rejectされた場合は`Sol xhigh` / `Sol max`を除外してprofileを再計算する。
- dispatch profile schemaをversion 2へ更新し、proposalとapproval stateを追加した。

### `sub-agent-task-manager`

- profile selection flowへproposal / approval stopを追加した。
- `Sol xhigh` / `Sol max`候補ではsub-agentをspawnせず、ユーザー確認までintentional incomplete stateとして停止する。
- independent final review / release auditの従来の`Sol xhigh` defaultを、自動dispatchではなくapproval-gated proposalへ変更した。
- approval evidenceをreport minimum contentsとcompletion gateへ追加した。
- `Never dispatch Sol xhigh or Sol max without explicit current-task user approval`をstrong operational ruleとして追加した。

### `development-orchestrator`

- routine profileは従来どおり自動選定し、`Sol xhigh` / `Sol max`だけをuser confirmation boundaryとした。
- implementation、normal review、independent final reviewのどのphaseでも、approval-gated profileが提案された場合はworkflowを停止する。
- repository policyがapprovalを代替できないことを明記した。
- task completion条件へexpensive Sol dispatchのapproval evidenceを追加した。

### 設計書

`design/adaptive-agent-assignment-design.md`を更新し、次の状態遷移を設計正本へ反映した。

```text
automatic classification
  -> proposed_profile = Sol xhigh | Sol max
  -> userへ理由とcost noticeを提示
  -> STOP
      |-- approve -> requestedへ昇格 -> runtime application
      `-- reject  -> xhigh/maxを除外して再計算
```

## 変更ファイル

- `skills/sub-agent-task-manager/references/agent-profile-selection.md`
- `skills/sub-agent-task-manager/SKILL.md`
- `skills/development-orchestrator/SKILL.md`
- `design/adaptive-agent-assignment-design.md`
- `reports/issue-13-sol-expensive-profile-approval-followup-20260827.md`

## TDD

CodexSkill repositoryの方針に従いTDDは適用していない。

- Red/Green専用test: 追加していない
- repository validator / distribution build: GitHub Actionsで確認する

## contract review

次の条件を確認した。

- `Sol high`以下は通常のautomatic selectionを継続する。
- `Sol xhigh`と`Sol max`だけがuser approval boundaryになる。
- approval前にspawnしない。
- approval前にproposalを`requested`へ昇格しない。
- repository policyはapprovalの代わりにならない。
- current-task explicit requestはapproval evidenceになりうる。
- rejection時はprofileを再計算し、rejected profileをsilent dispatchしない。
- independent final reviewにも同じgateを適用する。
- multi-agentと`Ultra`の扱いは変更しない。
- full-history forkおよびrequested/applied分離の既存contractを維持する。

## 検証

このreport commit後のPR current HEADと一致するGitHub Actions runだけをfinal CI evidenceとして使用する。

確認対象:

- `python3 scripts/verify_skill_repository.py`
- `python3 scripts/build_chatgpt_worker_skills.py --output chatgpt-worker-skills.zip`
- ZIP listing
- validation artifact upload

final exact-head run ID、job ID、artifact IDはGitHub上のPR commentへ記録する。別SHAのrunは代用しない。

## 残存リスク

- approval gateはSkill contractであり、Codex runtime本体の強制機構ではない。callerがSkillを無視するruntimeまでは防止しない。
- `Sol xhigh` / `Sol max`のcost差額そのものはruntime price情報を取得していないため、定量表示ではなくhigher-cost noticeとして扱う。

## 結果

ユーザー要求どおり、`Sol xhigh`と`Sol max`を「自動選択」から「提案して停止し、明示承認後のみ選択」へ変更した。PR #65へ追補し、mergeは行わない。

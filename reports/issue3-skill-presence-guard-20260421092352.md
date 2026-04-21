# issue #3 対応確認と修正

## 対象 issue

- Repository: `ssaattww/CodexSkill`
- Issue: `#3`
- Title: `何か作業する際に迷ったらskill不足を疑う。必ずskillが有るか確かめながら動く`
- Source: `https://github.com/ssaattww/CodexSkill/issues/3`

## 確認結果

issue #3 の要求は、確認時点では未対応だった。

- repo root に `AGENTS.md` が存在しなかった
- entry skill である `skills/development-orchestrator/SKILL.md` に、`AGENTS.md` の必須記述確認と不足時のユーザー通知が書かれていなかった

## 実施内容

1. repo root に `AGENTS.md` を新規追加
2. `AGENTS.md` に次の 2 条件を最大優先制約として記載
   - 作業前・作業中に relevant skill の有無を必ず確認する
   - 迷ったらまず skill 不足を疑う
3. `skills/development-orchestrator/SKILL.md` を更新
   - Inputs に `AGENTS.md` 必須確認を追加
   - Required flow に `AGENTS.md` 確認と不足時のユーザー通知を追加
   - Core rules に `AGENTS.md` 未整備のまま entry を信用しないルールを追加

## 変更ファイル

- `AGENTS.md`
- `skills/development-orchestrator/SKILL.md`

## 検証

- `git diff -- AGENTS.md skills/development-orchestrator/SKILL.md` で差分を確認
- `rg` で `AGENTS.md` と `development-orchestrator` の両方に必要文言が存在することを確認

## 備考

- 作業ブランチは `feat/issue-3-skill-presence-guard` を新規作成した
- follow-up:
  - review-enforcer の mandatory `sub-agent` review を current run で満たせない場合は、親判断で代替せずユーザー確認へ切り替えるべきというユーザー指摘を受けた
  - この指摘に合わせて `feedback-autonomy-boundary-manager` と `review-enforcer` に stop condition を追加した
  - 上記指摘は reusable process lesson として issue `#9` に handoff し、`feedback-points/feedback-points-backlog.md` にも記録した

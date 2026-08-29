# Issue #13 / PR #65 R5 指摘対応レポート

## 目的

PR #65 のfix verificationで再オープンされた`F65-R4-002`と、新規`F65-R5-001`へ対応し、independent-final terminal lifecycleのownerをrepository全体で`review-enforcer`へ一本化する。

## 対象PR

- Repository: `ssaattww/CodexSkill`
- PR: #65 `feat: task特性に応じてsub-agent profileを自動選定する`
- Branch: `feat/adaptive-agent-assignment`

## 対象finding

### F65-R4-002 / HIGH — fix verificationで再オープン

`review-enforcer`と`sub-agent-task-manager`間の二重reservationは解消していたが、`development-orchestrator` step 20がindependent-final report reservation-only phaseとHEAD freezeを直接実行していた。

その後`review-enforcer`も自分のstep 12でexactly-once reservationとfreezeを行うため、repository全体ではreservation ownerが一意になっていなかった。

### F65-R5-001 / HIGH

`development-orchestrator`は`review-enforcer`が独立最終reviewからattestation persistence、final push、PR publication、exact-head CIまで完了した後に、同じattestation persistence / publication / CI waitを再度実行する契約を持っていた。

これにより次のinvariantを破りうる状態だった。

- independent-final reservationは1件のみ
- report-attestation commitは最大1件
- final publicationは1 owner
- exact-head merge-gate CI waitは1回

## 原因

R4で`review-enforcer`をreservation ownerへ一本化した際、downstreamの`sub-agent-task-manager`は同期したが、上位`development-orchestrator`のterminal stepsが旧owner modelのまま残っていた。

つまり責務境界が次のように二重化していた。

```text
development-orchestrator
  -> reservation / freeze
  -> review-enforcer
       -> reservation / freeze / independent review / attestation / publish / CI
  -> attestation / publish / CI again
```

## 修正内容

### development-orchestratorのterminal ownershipを修正

`skills/development-orchestrator/SKILL.md`を更新した。

新しい責務境界は次のとおり。

```text
development-orchestrator
  -> implementation / validation / normal review / end-of-Issue work
  -> pre_freeze_ready
  -> review-enforcer
       -> exactly-once reservation
       -> reviewed implementation HEAD freeze
       -> independent reviewer lifecycle
       -> same-reviewer bounded closure
       -> at most one report-attestation commit
       -> attestation diff validation
       -> final push
       -> PR publication
       -> exact-head required pull_request CI wait
  -> consume terminal evidence only
  -> optional Git-HEAD-neutral PR comment / external handoff
```

具体的には以下を変更した。

- orchestrator step 20からindependent-final reservation-only phase直接実行を削除
- orchestrator step 20からreviewed implementation HEAD freeze直接実行を削除
- step 20は`pre_freeze_ready` evidenceを`review-enforcer`へ渡すだけに変更
- step 21で`review-enforcer`がterminal lifecycleの唯一のownerであることを明記
- finding修正時は同じ`review-enforcer` lifecycleへ戻し、新しいreservation/terminal ownerを作らない
- passing terminal result後は`review-enforcer`の結果をconsumeするだけに変更
- orchestratorから次の再実行を禁止
  - attestation persistence
  - second attestation commit
  - final push
  - `git-pr-submitter`
  - exact-head CI wait
- `Independent-final terminal ownership` sectionを追加
- Core rules / Outputs / Completion conditionを同じowner modelへ同期

Implementation commit:

- `f4cd160c3908d581b0b2b8b32bee5903188ae38b` — `fix: delegate terminal review lifecycle to review enforcer`

## 設計整合

新規の設計方針は追加していない。

既存`design/skill-hierarchy-design.md`とmirrorはR4で既に次を定義していた。

- `review-enforcer`がindependent reservation-only phaseを一度だけ実行
- stable reservation identityを保持
- independent reviewerはpre-reserved identityをreuse
- passing verdict後だけattestation persistence
- report-attestation commitは最大1件

今回の修正は、`development-orchestrator`をその既存正本へ戻すcontract alignmentであるため、hierarchy正本の意味論変更は不要と判断した。

## TDD

CodexSkill repositoryの保守方針に従い、TDDは適用していない。

本変更はSkill contractの整合修正であり、repository workflowのvalidator/buildを検証に使用した。

## 実装HEAD検証

Report作成前の実装修正HEAD:

- HEAD: `f4cd160c3908d581b0b2b8b32bee5903188ae38b`
- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `33259174217`
- Run number: `200`
- Run `head_sha`: `f4cd160c3908d581b0b2b8b32bee5903188ae38b`
- Build job: `99118045557`
- Conclusion: `success`

成功step:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

Artifact:

- Name: `chatgpt-worker-skills-33259174217`
- Artifact ID: `9716737676`
- Artifact run head SHA: `f4cd160c3908d581b0b2b8b32bee5903188ae38b`
- Digest: `sha256:998af0f9467a15dfeac639b148b394a7b9629066eb767c944d0d2522b097da21`

別SHAのrunは検証証跡として使用していない。

## 最終exact-head CIの扱い

このreport自体をcommitするとPR HEADが変わるため、上記run #200を最終CIとして代用しない。

report commitを含むPR current HEADに対するworkflow runを別途確認し、run `head_sha`がcurrent HEADと完全一致する場合だけ最終CIとしてPR本文・PRコメントへ記録する。

## Finding closure条件

`F65-R4-002`をclosure可能とする条件:

- `development-orchestrator`がreservation-only phaseを直接呼ばない
- `development-orchestrator`がreviewed implementation HEADを直接freezeしない
- `review-enforcer`だけがreservation ownerになる
- `sub-agent-task-manager`はcaller reservationをreuseする

`F65-R5-001`をclosure可能とする条件:

- `review-enforcer` terminal result後にorchestratorがattestation persistenceを再実行しない
- second attestation commitを作らない
- final push / PR publication / exact-head CI waitを重複しない
- orchestratorはterminal evidenceをconsumeするだけ

## 残存リスク

- runtimeがfinal sub-agent model/reasoningをparentへ公開しない場合の`applied` observability制約は継続する
- role/default-role profile impactをspawn前に確認できないruntimeではcost approval gate保証のためcapability gapとして停止する
- multi-agent review lifecycleは今回のscope外であり、現行review lifecycleはsingle reviewer execution policyを維持する

## Merge

mergeは実施しない。利用者がmergeを行う。

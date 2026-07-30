# PR #55 ChatGPT Skill ZIP Release Automation Report

## Summary

PR #55で、ChatGPT worker Skill ZIPの配布を次の4経路へ整理した。

1. PR作業中はread-only validation／buildとworkflow artifact生成だけを行う。
2. 対象変更が`main`へpushされた場合、既存のrolling tag `chatgpt-worker-skills-latest`と固定通常Releaseを更新し、ZIP Assetを添付または置換する。
3. PRがmergeされた場合、PR番号単位のGitHub Pre-releaseを自動作成し、`chatgpt-worker-skills.zip`をAssetへ添付する。
4. 利用者がGitHub ReleaseまたはPre-releaseを手動公開した場合、そのtagが指すcommitからZIPを生成し、同じReleaseへAssetとして添付する。

固定通常Release、PR単位Pre-release、手動ReleaseへのAsset添付は併存する。

## Scope

### Changed files

- `.github/workflows/release-chatgpt-worker-skills.yml`
- `design/chat-worker-skill-design.md`
- `design/skill-hierarchy-design.md`
- `skills/design/skill-hierarchy-design.md`

### Workflow behavior

#### PR validation

- `pull_request`の`opened`、`synchronize`、`reopened`で実PR HEADをcheckoutする。
- repository validatorとChatGPT Skill ZIP buildを実行する。
- ZIPをworkflow artifactとして保存する。
- Releaseは変更しない。

#### Rolling normal Release

- 対象変更の`main` pushで実行する。
- merge後の`main` HEADでvalidatorとZIP buildを実行する。
- rolling tag `chatgpt-worker-skills-latest`を対象HEADへ更新する。
- 固定通常Release `ChatGPT Worker Skills`を作成または更新する。
- `chatgpt-worker-skills.zip`をAssetとして添付または置換する。

#### PR merge Pre-release

- `pull_request.closed`かつ`merged == true`の場合だけ実行する。
- `merge_commit_sha`でvalidatorとZIP buildを再実行する。
- tag `chatgpt-worker-skills-pr-<PR番号>`を使用する。
- `ChatGPT Worker Skills PR #<PR番号>`をPre-releaseとして作成する。
- `chatgpt-worker-skills.zip`をPre-release Assetとして添付する。
- 再実行時は同じReleaseと同名Assetを更新する。

#### Manual Release asset

- 利用者による`release.published`で対象tagのcommitをcheckoutする。
- validatorとZIP buildを実行する。
- 公開された同じRelease／Pre-releaseへZIPを添付する。
- 同名Assetは置換する。
- 自動PR merge Pre-releaseのtag prefixは二重処理を防ぐため除外する。
- Workflowが`GITHUB_TOKEN`で作成・更新したReleaseイベントはGitHub Actionsを再帰起動しないため、rolling通常Releaseと自動Pre-releaseの作成から手動Release添付jobが重複実行されない。

## Design synchronization

- `design/chat-worker-skill-design.md`のRelease生成節と完了条件を更新対象とする。
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`は同一内容を維持する。
- Release時に共通fileを複製せず、repository相対linkを書き換えない既存方針は維持する。
- Project Instruction例、review lifecycle、handoff、Merge境界などRelease変更と無関係な既存節は維持する。

## Validation

### Current verified implementation HEAD

```text
9b89b487e077a91707f3b07859447d90292c905a
```

### GitHub Actions

- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `30577431643`
- Run number: `135`
- Head SHA: `9b89b487e077a91707f3b07859447d90292c905a`
- Conclusion: `success`

Successful build steps:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

PR作業中のため、次のpublish jobは設計どおり`skipped`だった。

- `publish-rolling-release`
- `publish-merge-prerelease`
- `attach-published-release-asset`

### Artifact

- Artifact ID: `8773247546`
- Name: `chatgpt-worker-skills-30577431643`
- Size: `15586` bytes
- Digest: `sha256:3b465c5b7a04a0a96e52b7a1607edf5da9d2ee8102b451d7403423625841c6b5`

## Event-specific verification boundary

PR merge Pre-release jobは実際のmerge後にだけ実行される。rolling通常Release jobは`main` push後にだけ実行される。手動Release asset jobは利用者による実際の`release.published`イベント後にだけ実行される。

PR #55をmergeしていない現在時点では、rolling通常Release更新、PR単位Pre-release作成、手動ReleaseへのAsset uploadの実行結果は未確認である。

PR #55のWorkflowがmainへ反映される前に公開済みだったReleaseには遡ってAssetを添付しない。main反映後に新しく公開されるRelease／Pre-releaseが自動添付の対象になる。

ただし、Workflow YAML、PR eventでの条件評価、repository validator、ZIP build、run ID基準のartifact受け渡しはcurrent HEAD固有runで成功している。

## Testing policy

CodexSkill repositoryの`AGENTS.md`に従い、TDDとこの変更専用のRed／Green testは実施していない。既存repository validator、package build、ZIP構造確認、設計同期、Workflow event条件の差分reviewを検証に使用した。

## Merge boundary

mergeは実施していない。利用者がPR #55のmerge判断と実行を所有する。

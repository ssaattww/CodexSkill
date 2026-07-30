# PR #55 ChatGPT Skill ZIP Release Automation Report

## Summary

PR #55で、ChatGPT worker Skill ZIPの配布契機を次の3経路へ分離した。

1. PR作業中はread-only validation／buildとworkflow artifact生成だけを行う。
2. PRがmergeされた場合、PR番号単位のGitHub Pre-releaseを自動作成し、`chatgpt-worker-skills.zip`をAssetへ添付する。
3. 利用者がGitHub ReleaseまたはPre-releaseを手動公開した場合、そのtagが指すcommitからZIPを生成し、同じReleaseへAssetとして添付する。

既存のrolling tag `chatgpt-worker-skills-latest`と固定通常Releaseの自動更新は廃止した。

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

#### PR merge Pre-release

- `pull_request.closed`かつ`merged == true`の場合だけ実行する。
- `merge_commit_sha`でvalidatorとZIP buildを再実行する。
- tag `chatgpt-worker-skills-pr-<PR番号>`を使用する。
- `ChatGPT Worker Skills PR #<PR番号>`をPre-releaseとして作成する。
- `chatgpt-worker-skills.zip`をPre-release Assetとして添付する。
- 再実行時は同じReleaseと同名Assetを更新する。

#### Manual Release asset

- `release.published`で対象tagのcommitをcheckoutする。
- validatorとZIP buildを実行する。
- 公開された同じRelease／Pre-releaseへZIPを添付する。
- 同名Assetは置換する。
- 自動PR merge Pre-releaseのtag prefixは二重処理を防ぐため除外する。

## Design synchronization

- `design/chat-worker-skill-design.md`のRelease生成節と完了条件を更新した。
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`は同一blob SHA `65a8fd7f33cb0ce2f067e9c93eca0fd323c5d8bf`へ同期した。
- Release時に共通fileを複製せず、repository相対linkを書き換えない既存方針は維持した。
- Project Instruction例、review lifecycle、handoff、Merge境界などRelease変更と無関係な既存節は維持した。

## Validation

### Current verified implementation HEAD

```text
77016ce8164cd804d72ed0b8e5a0d656b234be64
```

### GitHub Actions

- Workflow: `Validate and release ChatGPT worker skills`
- Run ID: `30504279374`
- Run number: `131`
- Head SHA: `77016ce8164cd804d72ed0b8e5a0d656b234be64`
- Conclusion: `success`

Successful build steps:

- Checkout target HEAD without write credentials
- Validate repository Skill architecture and active links
- Build and verify ChatGPT wrapper and core Skill ZIP
- Upload validation artifact

PR作業中のため、次のpublish jobは設計どおり`skipped`だった。

- `publish-merge-prerelease`
- `attach-published-release-asset`

### Artifact

- Artifact ID: `8744689225`
- Name: `chatgpt-worker-skills-77016ce8164cd804d72ed0b8e5a0d656b234be64`
- Size: `15586` bytes
- Digest: `sha256:c0bf732d960050ded0feb7cbf361d22f9ca6ecbf0062a4a9e49fc1322b213ee4`

## Event-specific verification boundary

PR merge Pre-release jobは実際のmerge後にだけ実行される。手動Release asset jobは実際の`release.published`イベント後にだけ実行される。そのため、PR #55をmergeしていない現在時点では、GitHub Releaseの作成およびRelease Asset uploadの実行結果は未確認である。

ただし、Workflow YAMLの構文、PR eventでの条件評価、repository validator、ZIP build、artifact uploadはcurrent HEAD固有runで成功している。

## Testing policy

CodexSkill repositoryの`AGENTS.md`に従い、TDDとこの変更専用のRed／Green testは実施していない。既存repository validator、package build、ZIP構造確認、設計同期、Workflow event条件の差分reviewを検証に使用した。

## Merge boundary

mergeは実施していない。利用者がPR #55のmerge判断と実行を所有する。

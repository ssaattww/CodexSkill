# PR #55 ChatGPT Skill ZIP Release Automation Report

## Summary

PR #55で、ChatGPT worker Skill ZIPの配布を次の4経路へ整理した。

1. PR作業中はread-only validation／buildとworkflow artifact生成だけを行う。
2. 対象変更が`main`へpushされた場合、既存のrolling tag `chatgpt-worker-skills-latest`と固定通常Releaseを更新する。
3. 同じ`main` pushで、最新の安定版SemVer tagを基準にPATCHを進めた新しい`x.y.z-pre` Pre-releaseを作成する。
4. 利用者がGitHub ReleaseまたはPre-releaseを手動公開した場合、そのtagが指すcommitからZIPを生成し、同じReleaseへAssetとして添付する。

固定通常Release、連番Pre-release、手動ReleaseへのAsset添付は併存する。

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
- merge後の最新`main` HEADでvalidatorとZIP buildを実行する。
- rolling tag `chatgpt-worker-skills-latest`を対象HEADへ更新する。
- 固定通常Release `ChatGPT Worker Skills`を作成または更新する。
- 最新`main` HEADから生成した`chatgpt-worker-skills.zip`をAssetとして添付または置換する。

#### Incremented Pre-release

- 対象変更の`main` pushで実行する。
- SSCの`.github/workflows/publish-nuget.yml`と同じ考え方で、最新の安定版tagから`HEAD`までのcommit数をPATCHへ加算する。
- 安定版tagは`v`の有無を許容する`major.minor.patch`形式だけを対象とし、`-pre` tagは基準から除外する。
- 例として安定版`1.1.0`から1回スカッシュマージされた場合は`1.1.1-pre`、2回目は`1.1.2-pre`を新規作成する。
- 既存Pre-release tagやAssetを上書きせず、同名tagが既に存在する場合は失敗させる。
- Pre-releaseへ添付するZIPは、前回安定版のAssetではなく、その`main` pushの最新HEADから同じWorkflow runで生成したZIPである。
- 関連PR番号をcommitから取得できた場合はRelease notesへ記載する。

#### Manual Release asset

- 利用者による`release.published`で対象tagのcommitをcheckoutする。
- validatorとZIP buildを実行する。
- 公開された同じRelease／Pre-releaseへ、そのtagが指すcommitから新しく生成したZIPを添付する。
- 同名Assetは置換する。
- Workflowが`GITHUB_TOKEN`で作成・更新したReleaseイベントはGitHub Actionsを再帰起動しない。

## Design synchronization

- `design/chat-worker-skill-design.md`のRelease生成節と完了条件を更新対象とする。
- `design/skill-hierarchy-design.md`と`skills/design/skill-hierarchy-design.md`は同一内容を維持する。
- Release時に共通fileを複製せず、repository相対linkを書き換えない既存方針は維持する。
- Project Instruction例、review lifecycle、handoff、Merge境界などRelease変更と無関係な既存節は維持する。

## Validation

Workflow変更後のcurrent HEADに紐づくGitHub Actionsで、repository validator、ZIP build、artifact uploadを確認する。

PR eventではRelease publish jobsが`skipped`となる。実際のrolling Release更新と連番Pre-release作成は`main` push後、手動ReleaseへのAsset添付は利用者による`release.published`後に実行される。

## Event-specific verification boundary

PR #55をmergeしていない現在時点では、rolling通常Release更新、連番Pre-release作成、手動ReleaseへのAsset uploadの実行結果は未確認である。

PR #55のWorkflowがmainへ反映される前に公開済みだったReleaseには遡ってAssetを添付しない。main反映後に新しく公開されるRelease／Pre-releaseが自動添付の対象になる。

## Testing policy

CodexSkill repositoryの`AGENTS.md`に従い、TDDとこの変更専用のRed／Green testは実施しない。既存repository validator、package build、ZIP構造確認、設計同期、Workflow event条件の差分reviewを検証に使用する。

## Merge boundary

mergeは実施していない。利用者がPR #55のmerge判断と実行を所有する。

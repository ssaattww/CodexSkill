# 通常統合報告: Issue #104 調査担当への図出力指示

## 対象・状態

- [Issue #104](https://github.com/ssaattww/CodexSkill/issues/104) / [Draft PR #105](https://github.com/ssaattww/CodexSkill/pull/105)。基点 `main` の SHA: `dfe07e81d6a1c209f99b908acc8109f70b38a773`。
- ブランチ `issue-104-investigation-diagram-guidance`、公開技術 HEAD (`technical_head`): `e965a7085b9f29eaf3175609c6217b321a2e6def`。親コミットは基点と一致。
- `verification_capability: local_execution_available`。技術変更はコミット・公開済み（Git push の認証不足後、親が GitHub コネクタで同一内容を公開）。本通常報告・追跡は `commit_pending`、公開・CI 待機は未実施。本記録は独立最終報告ではない。

## 実装と範囲

- 要件は Issue #104 の完了条件。現行 main の調査担当向け prompt 要件に同等指示がないことを確認し、`skills/sub-agent-task-manager/SKILL.md` の「For investigation tasks also include」へ旧案と同じ1行だけ追加した。
- 調査中は原則として図の描画・画像出力を省略し、調査に必要な場合を例外とする。ユーザーへの提示時には必要な図だけを出力・確認する。
- 公開差分は1ファイル・1行追加、削除なし。対象ファイル SHA-256: `d692acb729ec6f218101ca38745774effbdaf0223e3630f8c7cb3e4d621a31d2`。公開ツリーで一致を確認した。
- 図面スキル自体、設計文書の納品要件、設計・Skill 階層、依存関係、旧成果物は変更しない。別の実装開始条件は範囲外。設計更新は不要。TDD は `AGENTS.md` の CodexSkill 保守方針により非適用。

## 標準検証

レビュー前のローカル差分候補で `git diff --check` と `python3 scripts/run_validation.py --output-dir <新規診断ディレクトリ>` を実行した。

| 検査 | 結果 |
| --- | --- |
| 差分・空白検査 | 成功 |
| repository | PASS (0) |
| bundle | PASS (0) |
| zip-integrity | PASS (0) |
| zip-contents | PASS (0) |

- 4工程の標準エラーは空。診断成果物は `results.json`、`results.xml`、`source.json`、各工程の stdout/stderr、`chatgpt-worker-skills.zip`（リポジトリ外のローカル診断）。当時の Git HEAD は基点、検証対象には未コミットの1行を含む。
- 公開技術 HEAD を取得し、診断の source SHA-256 265件と ZIP 内8件を公開ツリーに照合し、全件一致を再確認した。未コミット検証の内容と公開技術差分の同一性を示すものであり、後続の記録込み HEAD の検証を代替しない。
- 公開技術 HEAD を指定した GitHub コネクタの pull_request workflow run 取得では、PR commit artifacts（run 46003956864）と Validate and release ChatGPT worker skills（run 46003956632）が completed / success。返却概要には各 run の head_sha が明示されないため、個別 run の正確な HEAD と artifact の再取得は未確認。最終 CI 成功とは扱わない。

## 通常レビュー（親による原本確認）

- 実装担当とは別の担当による通常レビュー。正式判定は `pass_with_held`、必須指摘0件。保留は実際の調査委譲における指示適用のみで、実行時適用は未確認。
- レビュー対象は未コミットの差分。基点 `dfe07e81d6a1c209f99b908acc8109f70b38a773`、対象ファイル SHA-256 `d692acb729ec6f218101ca38745774effbdaf0223e3630f8c7cb3e4d621a31d2`。公開技術 HEAD の内容と一致するが、公開コミット自体をレビューしたと主張しない。
- 検証記録のソース265ファイルと ZIP 内8ファイルを候補と照合し全件一致。標準検査4工程および差分チェックに問題なし。
- 親の原本確認では GPT-6.2 Sol High を指定。実行時に適用されたプロファイルは未確認。通常レビューは分割なし。role/default-role、fork policy 等は未観測。内部識別子は記録しない。自己レビューによる代替ではない。
- 今回の報告・追跡3ファイルは先の技術差分レビューの対象外。内容確定後に追加の通常レビュー（必要なら修正・再確認）を行う。

## 非最終記録の確定と残作業

- 親の end-of-Issue Skill-gap 判断は `no skill action needed`（今回の既存 Skill 変更以外に追加対応なし）。FP 台帳への追加なし。旧案 #99 のライフサイクル上の問題は別スコープとして記録済み。旧記録は変更しない。新規保存型 handoff は選択せず、親へ inline で引き渡す。
- 通常レビュー原本の確認と親の Skill-gap/FP 判断は完了。次に報告・追跡を含む非最終差分を追加通常レビューで収束させ、必要な検証とコミットを完了する。
- 収束後に限り、記録込み最終公開候補の正確なコミット HEAD でリポジトリ所定の全体ローカル同等性検証を1回実施する。内容が変わった場合だけ旧検証を無効化して再実行する。先の検証とは区別する。
- 独立最終レビューの予約・凍結・独立レビュー・attestation・最終公開・正確な HEAD の CI 待機は `review-enforcer` の後続工程。今回は未実施。マージしない。

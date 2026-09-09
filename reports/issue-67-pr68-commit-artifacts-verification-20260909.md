# PR #68 コミット検知・artifact保存の確認

## 変更

対象は `ssaattww/CodexSkill` の `feat/issue-67-astra-approval`。
Issue #75に従い、Chat側のファイルを正本にし、RDCで検証した内容をGitHub Connectorから反映した。
`.github/workflows/pr-commit-artifacts.yml` を追加し、既存mainの `scripts/run_validation.py` を利用する。
PRの更新とpushを検知し、対象PRのHEADとイベントのSHAを照合する。ソースZIP、worker ZIP、検証結果、標準出力、標準エラー、対象識別情報をartifactへ保存する。
初回のworkflowはジョブ開始前に失敗したが、`runner.temp` の参照位置をstep内へ変更した `a144bf8c394767277ddce28ff96a6d13b97a9727` で実行成功を確認した。

## 検証済みの実行

- RDC: PR判定13ケース、通常のrepository検証、ZIP生成・破損検査が成功。
- RDC: 終了コード7を返す診断保存確認で、標準出力・標準エラー・結果JSON・JUnit XMLの保存を確認。TDDのRedではない。
- RDC: 修正版workflowの構文と結果メタデータ3ケースを確認。
- Run `34295168119`: event `push`、HEAD `a144bf8c394767277ddce28ff96a6d13b97a9727`、成功。
- Artifact `10082836356`: SHA-256 `e7d99b477d6b0721ecca1b65e8245aa8ba992ede009063ccb53795ef2da4e851`。
- 後続コミットのRun `34295264332`: event `push`、HEAD `650e013c4371300eb279e0e970597d5b24021150`、成功。
- Artifact `10082872792`: SHA-256 `6212397abf97181a729e76bdb87013a18e2ff5f129500c825cb544e43e06afa8`。

## 境界

上記はそれぞれ記載したSHAの実行結果であり、本報告保存後のHEADに対するCI結果ではない。
新しいHEADの結果はPRコメントで記録し、別SHAのrunを代用しない。
`push`経路の成功を、競合解消や`pull_request`経路の実行成功へ読み替えない。
PR #68のmainとの競合と独立レビュワーによる修正確認は別の残作業である。PRはマージしていない。

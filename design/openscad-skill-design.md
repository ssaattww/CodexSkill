# OpenSCAD Skill設計

## 状態

- 設計開始日: 2026-09-06
- 状態: 設計中。実装は未着手。
- 対象: `skills/openscad/`の新規追加計画。
- 対象環境: WindowsネイティブのCodex。WSL、Git Bashを必須としない。
- 本PRを設計から実装まで継続使用する。設計完了だけではマージせず、マージは利用者が実施する。

## 依頼と境界

参照元のOpenSCAD Skillについて、Claude依存の除去、Windows対応、および大きな`SKILL.md`の責務分割を設計する。今回は設計文書と進捗・報告文書だけを変更し、Skill本体、実行スクリプト、依存パッケージ、CI workflowは変更しない。

参照元: https://github.com/andreahaku/openscad_claude_skill

本リポジトリの作業開始HEAD: `6507727986329e34e69da3680a00824eb1fbfe13`。

## 設計で確定させる事項

1. `SKILL.md`に残す入口・共通契約と、必要時に読むモード別参照文書の境界。
2. 一つのinstallable Skillに同梱するスクリプト・参照資料・テンプレートと、既存workflow Skillとの責務の違い。
3. Windowsの実行ファイル探索、パス、引数、一時ファイル、依存関係、画像確認の契約。
4. 上流の欠落ファイル・説明と実装の不整合・比較失敗の扱いを移植時にどう解消するか。
5. 具体的な受け入れ条件、実装の論理単位、Windowsで未検証の項目。

## 作業開始時の検証経路確認

`.github/workflows/release-chatgpt-worker-skills.yml`を確認した。既存workflowはPR HEADをcheckoutし、repository validatorとChatGPT用ZIP buildを実行する。artifactは生成されたZIPであり、失敗時の標準出力・標準エラー・診断ログをまとめて常時保存するworkflowではない。

CodexSkillはTDDおよびRevMem用の診断artifact workflow追加方針の適用対象外である。本設計のためにテストやworkflowを追加しない。設計段階は文書整合と既存CIを検証し、OpenSCADのWindows実行結果と混同しない。

CIは対象PRのcurrent HEAD SHAとrunの`head_sha`が一致するものだけを扱う。一致するrunがなければCI未実施として報告する。

# Task routine 状態の可視化とレビュー工程の互換性設計

## 目的と境界

[Issue #47](https://github.com/ssaattww/CodexSkill/issues/47) と Draft PR [#48](https://github.com/ssaattww/CodexSkill/pull/48) の既存CLIを使い、task routineの現在位置と証跡を読み取り表示する。初版は可視化のみで、#47の完了とは扱わない。

既存の認可・承認、検証ルート、通常レビュー、`review-enforcer`の終端所有は維持する。表示から承認済み、公開可能、公開済みとは推測しない。PR #48には `Closes #47` が記載されているため、要件と終了条件が合意されるまではDraftのままマージしない。正式な終了対象は追加・変更しない。

## レビュー工程と状態の導出

レビュー状態は対象HEAD、検証ルート、レビュー種別、保存済みの報告・検証・公開証拠からのみ導出する。証拠が欠ける場合は「判定不能」と表示する。

| 検証ルート | 通常レビュー前の順序 | レビュー証拠に必要な項目 |
|---|---|---|
| `local_execution_available` | 対象検証 → 報告・進捗同期 → commit → 通常レビュー | 対象HEAD、対象検証の結果、報告状態、commitとレビュー対象HEADの対応 |
| `remote_ci_only` | 報告・進捗同期 → 認可済みcommit・push → 対象HEADと完全一致する自動CI → 通常レビュー | 対象HEAD、報告状態、commit・pushの証拠、同一HEADの自動CI結果 |

報告作成時点で対象HEADがまだcommitされていない場合は、SHAを補完せず `commit_pending` と記録する。commit後に対象HEADとの対応が確認できたら、その値を明示する。

通常レビューで修正が必要になった場合と、レビュー後の反省・追跡作業が対象を変更した場合は、変更の再検証・報告・保存を経て通常レビューへ戻る。検証、報告、commit、push、CIの実行順と権限は現行仕様に従い、状態表示がそれらを実行・許可しない。独立最終レビュー、予約、HEAD凍結、最終公開、必須CIは引き続き `review-enforcer` の所有とする。

## 初版の読み取り・表示契約

データ元は既存 `status --json` が返す JSON・終了コード・エラー診断とする。エラーでは JSON が返らない場合を扱う。失敗理由の詳細やバージョン番号は既存の出力から確定できる場合にのみ表示し、根拠のない分類は判定不能とする。既存の通常表示形式は変えず、可視化用の表示を別に設ける。初版ではJSONを読み、保存済みstateと証跡から表示するだけとし、stateの更新・復旧、hook、gate、installer、永続設定変更は含めない。

| 読み取り状態 | 表示内容・期待結果 |
|---|---|
| stateなしを特定できる | routine未開始。次工程やレビュー状態は判定不能 |
| 読取不可・破損を区別できない | 既存の読み取りエラーを表示し、詳細理由は判定不能。修復・初期化はしない |
| 未対応schema／version | 既存診断の範囲で表示。version の実値が出ない場合は不明。変換しない |
| 停止中・pause | 停止中と記録済み理由を表示。再開可能・認可済みとは推測しない |
| 必須条件・証跡不足 | 不足項目、期待する証跡、判定不能な段階を列挙 |
| 条件と証跡が揃う | 対象HEAD・ルート・レビュー種別・工程証拠に基づく状態を表示。公開可否は推測しない |

## 未確認点と後続作業

PR #48の記録では初期11件と差分対象8件は個別に成功していますが、全19件の一括実行は未確認です。現在のconnectorが渡す実tool名形式、実runtimeのhook payload、既存CLIのJSON出力と現行報告・検証証拠との対応も未確認です。初版はhookを有効化しないため、runtime上の強制動作を保証するものではありません。

#47の元要件にある永続stateの強制、lifecycle hook、編集・提出gate、Stop継続、再開時の自動注入、installer、PR本文gate、テストは初版の範囲外で、別工程として残す。現行mainの非TDD方針を維持し、TDDを追加しない。

## 参照

- [Issue #47](https://github.com/ssaattww/CodexSkill/issues/47) — 元要件と受入条件
- [#12の置換記録](https://github.com/ssaattww/CodexSkill/issues/12#issuecomment-4941156918) — #47を継続の正本とする記録
- [Draft PR #48](https://github.com/ssaattww/CodexSkill/pull/48) — 既存CLI・state・hook案
- [現行 development-orchestrator](https://github.com/ssaattww/CodexSkill/blob/dfe07e81d6a1c209f99b908acc8109f70b38a773/skills/development-orchestrator/SKILL.md)
- [検証ルートとレビュー終端の設計](https://github.com/ssaattww/CodexSkill/blob/dfe07e81d6a1c209f99b908acc8109f70b38a773/design/skill-hierarchy-design.md)

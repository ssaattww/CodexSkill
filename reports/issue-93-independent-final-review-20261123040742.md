# Issue #93 / PR #94 独立最終レビュー記録

## 判定と対象

**技術判定は合格（`pass_with_held`）。** この判定は固定した `reviewed_implementation_head` に適用する。本報告を追加するコミットは管理上の証跡（`report_attestation_commit`）であり、技術レビューの対象 SHA は下記の実装 HEAD とする。

- リポジトリ `ssaattww/CodexSkill`、対象 `issue-93-cloud-tools-installer` → `main`。 [Issue #93](https://github.com/ssaattww/CodexSkill/issues/93) · [Draft PR #94](https://github.com/ssaattww/CodexSkill/pull/94)
- `reviewed_implementation_head` / `technical_head` / `administrative_parent` は `ea477ec4309639b73d4aae89d52941fe1fda81b6`。Base は `8ee6e9f80a0362a4d066c4ea39fd3e87002fc829`。
- 独立レビューは `c360d200ce877804f9e968fd39d33b0900fc73fb` で開始し、`0e6734d358d18632b79a08a144ceaf0bf78a2cc5`、`ea477ec4309639b73d4aae89d52941fe1fda81b6` の順に、同じ独立担当が指摘と CI 差分に範囲を絞って再確認した。担当は実装、修正、通常レビューに関与していない。 [初回](https://github.com/ssaattww/CodexSkill/pull/94#issuecomment-7091012207) · [再レビュー](https://github.com/ssaattww/CodexSkill/pull/94#issuecomment-7091180218) · [合格記録](https://github.com/ssaattww/CodexSkill/pull/94#issuecomment-7091270597)
- `review-enforcer` 担当が 2026-11-23 04:07:43 UTC に `codexskill-issue-93-pr-94-ifr-20261123040742` として、`reports/issue-93-independent-final-review-20261123040742.md` をメタデータのみで予約した。予約時に固定候補の Git tree とローカル作業ツリーでパスの不存在を確認した。
- 今回の固定判定は 2026-11-23 04:08:01 UTC。以前の技術レビュー時点は未予約と記録し、今回の固定判定で同一 SHA の既存証拠を採用した。永続化の直前にも、隔離した Linux の clone と GitHub のブランチおよび PR が同一の実装 HEAD を指すことを確認した。

## 要件と確認範囲

Cloud Install script から固定版の共有インストーラーを直接呼び、Duck 側が設定・SDK の版とチェックサムを管理する。対象差分は設計、共有インストーラー、実装報告、タスク・フェーズ追跡の5ファイル。CLI と Linux x64・設定スキーマ・パスの事前検査、公式 URL の組み立てと展開前の SHA-512 照合、ステージによる配置、既存 SDK の再利用、失敗時の後始末と環境引き渡しを確認した。対応ライフサイクルはリポジトリ方針に沿った実装後の検証。 [設計](https://github.com/ssaattww/CodexSkill/blob/ea477ec4309639b73d4aae89d52941fe1fda81b6/design/cloud-tools-installer-design.md) · [技術差分](https://github.com/ssaattww/CodexSkill/compare/8ee6e9f80a0362a4d066c4ea39fd3e87002fc829...ea477ec4309639b73d4aae89d52941fe1fda81b6)

## 指摘と解消根拠

| 指摘 | 必須修正と解消根拠 |
| --- | --- |
| `PR94-IFR-001` 高・解消 | 存在確認と配置の間に別実行が SDK を配置すると、従来の移動は先行側に入れ子を作って成功し得た。`mv --no-target-directory --no-clobber` と移動元の残存検査で、先行側を保全して後続を非ゼロで終了させる。作者の同期した2プロセスの合成試験では片方だけ成功。独立側は Linux の GNU `mv` 9.7 と一時領域で分岐を確認し、`mv` が `0` で移動をスキップしても配置処理は `1` を返した。先行内容は保全され、入れ子やステージの残存もなかった。 [実装 L189–200](https://github.com/ssaattww/CodexSkill/blob/ea477ec4309639b73d4aae89d52941fe1fda81b6/scripts/install-cloud-tools.sh#L189-L200) |
| `PR94-IFR-002` 高・解消 | 正規化後の制御文字および Python の標準出力設定により、検証した値が Bash で変化し得た。キャッシュを一度だけ正規化し、境界と制御文字を検査した値を `os.fsencode` とバイナリ標準出力で渡す。パス中の改行は拒否され、コマンド置換で落ちる末尾改行は区切りだけになる。Bash は受け取った値をそのまま使う。作者の隔離した合成試験では `PYTHONIOENCODING=ascii:backslashreplace` 下で、正規化した日本語のキャッシュパスへの SDK 配置と出力 `DOTNET_ROOT` が一致した。 [境界と制御文字](https://github.com/ssaattww/CodexSkill/blob/ea477ec4309639b73d4aae89d52941fe1fda81b6/scripts/install-cloud-tools.sh#L66-L82) · [バイト列の引き渡し](https://github.com/ssaattww/CodexSkill/blob/ea477ec4309639b73d4aae89d52941fe1fda81b6/scripts/install-cloud-tools.sh#L115-L131) |
| `PR94-IFR-003` 中・解消 | 従来の呼び出し例では導入失敗後に `export` が成功し、全体が成功して見えた。例に `set -euo pipefail` を適用し、失敗時は環境変数設定前に終了させる。作者の不正ハッシュ試験では呼び出し元が非ゼロで終了し、後続の PATH 設定に到達しなかった。 [公開例](https://github.com/ssaattww/CodexSkill/blob/ea477ec4309639b73d4aae89d52941fe1fda81b6/reports/issue-93-implementation-20261123033558.md#L45-L55) |

重要度の変更はなし。最終の修正差分はキャッシュパスの受け渡しと対応する設計・検証記録に限定され、CLI と解消済みの競合・失敗伝播の処理は維持されている。 [固定版の修正差分](https://github.com/ssaattww/CodexSkill/compare/0e6734d358d18632b79a08a144ceaf0bf78a2cc5...ea477ec4309639b73d4aae89d52941fe1fda81b6)

## 検証と CI

- 作者の合成試験は一時的な consumer、キャッシュ、合成アーカイブとコマンドの置き換えを使用。正常配置、ハッシュ不一致による未配置、既存 SDK の再利用、事前拒否、追跡ファイルの保全、ステージの後始末の証拠を記録した。初期検証の実装 SHA は `34c34e5eaa37614f774348fc592d0e08305b48a1`。追加修正の検証範囲は上記3件の根拠に記載した。 [実装・検証報告](https://github.com/ssaattww/CodexSkill/blob/ea477ec4309639b73d4aae89d52941fe1fda81b6/reports/issue-93-implementation-20261123033558.md#L26-L75)
- 技術 HEAD の `pull_request` CI `45109325489` は対象 SHA の checkout、Skill 検証、ZIP ビルドを完了した。同じイベントの `45109325598` は成功表示で、checkout・アーカイブ・検証の各ステップはスキップ。`push` CI `45109321090` は同じ技術 SHA の取得、アーカイブ、リポジトリ検証、成果物収集を完了した。CI が実行したのは Skill とリポジトリの検証で、インストーラーの挙動は合成試験の証拠に基づく。 [PR Skill CI](https://github.com/ssaattww/CodexSkill/actions/runs/45109325489) · [PR 成果物 CI](https://github.com/ssaattww/CodexSkill/actions/runs/45109325598) · [push CI](https://github.com/ssaattww/CodexSkill/actions/runs/45109321090)
- 今回の永続化では、既存の独立レビュー、合成試験、技術 HEAD の CI を再利用した。ShellCheck は未実施。構成済み Markdown lint は実装報告で `unsupported` と記録されている。

## 保留と永続化

- 公式 SDK への疎通・取得・展開・起動、新規 Codex Cloud 環境の復元とセッション間の PATH 引き渡しは未確認。Duck の固定設定を組み込む製品連携段階の受入として扱う。
- 専用 `review-enforcer` ロールの実行基盤設定、モデル、推論プロファイルの適用詳細は未確認。確認した継続性は、実装から独立した同一チャットのレビュー記録に基づく。
- 永続化モードは `report_attestation_commit`。`commit_pending` 時点の `technical_head` と `administrative_parent` は上記の実装 HEAD。これを第一親とし、予約パス1件の追加のみを含む1コミットを許容する。コミット SHA は作成後にブランチ外の引き継ぎに記録し、公開後の必須 `pull_request` CI はその SHA で確認する。
- 後続の Git コミットが加わった場合、完了扱いは失効する。通常の修正確認と同じ独立担当による指摘・CI 差分に限定した確認が必要になる。マージは利用者が判断する。

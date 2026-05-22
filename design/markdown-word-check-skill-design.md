# Markdown 単語チェック skill 設計

## 目的

Markdown 資料を書く agent やレビューする agent に、細かい用語規則を覚えさせない。

各リポジトリは、リポジトリ固有の用語、許可語、表記揺れ、対象ファイルを lint 設定として持つ。CodexSkill 側は、その設定を読み込み、Markdown 資料に適用する共通 skill と shared script を提供する。

この設計では、`markdown-word-checker` skill を新規追加し、`review-enforcer` と Markdown 資料を作成する skill から利用できるようにする。

## 背景

IbisDuck では `tools/lint/markdown-whitelist.yaml`、`tools/lint/prh.yml`、`tools/lint/markdown-targets.json` を使い、Markdown 文書の用語と表記揺れを検査している。

ただし、このルールを作業者に細かく説明すると、作業者が単語登録、`aliases`、`prh`、複合語、UI ラベルの扱いを都度判断する形になる。これは本来 lint システムが担うべき責務である。

作業者に知らせるルールは次だけにする。

1. Markdown を作成または編集したら、リポジトリの Markdown lint を実行する。
2. lint の指摘に従って直す。
3. 指摘が不適切なら、回避せず lint 設定の見直しとして報告する。

細かい用語判断は、repo 固有設定と `markdown-word-checker` skill に閉じ込める。

## 新規 skill

### 名前

`markdown-word-checker`

### 役割

Markdown 資料に対し、対象リポジトリの lint 設定を読み込んで、用語、表記揺れ、未登録語、回避的な backtick 使用を確認する。

この skill は、単語ルールそのものをグローバルに持たない。各リポジトリ固有の語彙は、対象リポジトリの `tools/lint/` 配下から読む。

### 実行 owner

`親が実行`

親 agent が次を判断する。

- どのリポジトリを対象にするか。
- どの Markdown ファイルを対象にするか。
- full lint か focused lint か。
- lint 失敗を修正対象にするか、意図的な stricter gate として記録するか。
- repo 固有設定の追加、削除、変更に利用者レビューが必要か。

実際の検査コマンド実行や広い証跡収集は、必要に応じて `sub-agent-task-manager` 経由で sub-agent に委譲できる。

## repo 固有設定の契約

対象リポジトリは、標準形として次を持てる。

```text
tools/lint/markdown-targets.json
tools/lint/markdown-whitelist.yaml
tools/lint/prh.yml
tools/lint/README.md
tools/lint/requirements.txt
package.json
```

必須は対象リポジトリの導入段階によって変わる。`markdown-word-checker` は、存在する設定だけを前提にして実行経路を選ぶ。

複数リポジトリで使うため、IbisDuck 型の `tools/lint/` 構成を暗黙の前提にしない。`markdown-word-checker` は、対象リポジトリごとに次の最低構成と fallback を判定してから実行する。

| 対象 | 不足時の扱い |
| --- | --- |
| Markdown 変更対象ファイル | 対象がない場合は `skip`。対象候補があるが root やファイルを解決できない場合は `unsupported`。 |
| `package.json` | `lint:md` 経路は `unsupported`。shared script 経路に必要な依存関係も解決できない場合は、Markdown lint gate を実施できない `unsupported` として記録する。呼び出し元が review gate として Markdown lint を必須にしている場合は `failed gate`。 |
| `package.json` の `lint:md` | 不足時は npm script 経路を `skip` し、focused validation の shared script 経路を検討する。shared script 経路も成立しない場合は `unsupported`。 |
| `tools/lint/markdown-targets.json` | full lint の対象集合を決められないため full lint は `unsupported`。明示ファイルがある focused lint では、その明示ファイルだけで続行できる。repo の `lint:md` がこのファイルを必須として失敗した場合は `failed gate`。 |
| `tools/lint/markdown-whitelist.yaml` | whitelist 検査は `unsupported`。cspell や prh など他の検査が独立して実行できる場合は続行する。repo が whitelist 検査を有効にしていて command が失敗した場合は `failed gate`。 |
| `tools/lint/prh.yml` | prh 検査は `skip`。repo が prh 検査を必須として command が失敗した場合は `failed gate`。 |
| `cspell.config.jsonc` | cspell 検査は `skip`。repo が cspell 検査を必須として command が失敗した場合は `failed gate`。 |
| `tools/lint/README.md` | 実行方法の説明がないリスクとして記録するが、検査可能な command が見つかる場合は gate 失敗にしない。 |

`skip` は対象がない、または任意検査が設定されていない状態を示す。`unsupported` は対象 repo がまだ `markdown-word-checker` の実行契約を満たしておらず、検査結果を合否として扱えない状態を示す。`failed gate` は、呼び出し元が必須 gate とした検査、または repo が設定済みとして宣言している検査が失敗した状態を示す。

### `markdown-targets.json`

Markdown lint 対象を定義する。生成物、外部取り込み物、build output、reports など、通常資料作成者が編集しないファイルはここで除外する。

### `markdown-whitelist.yaml`

資料中で使ってよい語を、意味付きで定義する。

`term` は許可語、`description` は人が意味を確認する説明、`aliases` は今後も同じ概念として許可する別表記だけに使う。

### `prh.yml`

今後は正式表記へ寄せたい揺れを定義する。許可する別名ではなく、直すべき表記だけを置く。

### `README.md`

そのリポジトリでの lint 実行方法と、指摘が不適切な場合の報告方法を書く。作業者へ細かい用語規則は書かない。

## shared script の配置

shared script は CodexSkill 側に置く。

既存の実体は `skills/review-enforcer/scripts/` にある。

```text
skills/review-enforcer/scripts/list-markdown-targets.js
skills/review-enforcer/scripts/run-cspell-markdown.js
skills/review-enforcer/scripts/check-markdown-whitelist.js
skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py
skills/review-enforcer/scripts/extract-markdown-vocabulary-sudachi.py
```

`markdown-word-checker` 導入時は、次のどちらかを選ぶ。

1. 初期段階では既存 script をそのまま参照し、skill だけを追加する。
2. 後続整理で script を `skills/markdown-word-checker/scripts/` へ移し、`review-enforcer` は新 skill を呼ぶ。

初期実装では 1 を選ぶ。理由は、script 移動による import/path 破壊を避け、skill 呼び出し関係を先に安定させるためである。

## 呼び出し関係

### review-enforcer からの利用

`review-enforcer` は、Markdown、Markdown lint 設定、reports、task tracking、設計文書、review-facing text を変更する task のレビュー前に `markdown-word-checker` を呼ぶ。

`review-enforcer` は review gate の owner であり続ける。`markdown-word-checker` は、Markdown 用語検査の実行と結果整理だけを担当する。

```text
review-enforcer [親が実行]
├─ markdown-word-checker [親が実行]
│  ├─ sub-agent-task-manager [親が実行, 大きい lint 証跡収集は sub-agent]
│  └─ report-output-manager [親が実行, sub-agent report path 決定]
├─ sub-agent-task-manager [親が実行, reviewer は sub-agent]
└─ report-output-manager [親が実行]
```

`markdown-word-checker` が lint 証跡収集を sub-agent に委譲する場合は、`sub-agent-task-manager` の契約に従う。親 agent は dispatch 前に `report-output-manager` で report path を決め、標準 report file を事前作成する。sub-agent には、その report file を先に読み、見出し順、空行、既存記述を保持して、実行コマンド、確認ファイル、結果、未解決リスクだけを記録させる。

呼び出し元 skill が既に review report や task report を持っている場合でも、sub-agent 作業の一次証跡は次のどちらかに固定する。

- sub-agent 用の独立 report を `reports/` 配下へ作成し、呼び出し元 report にはその path と要約を添付する。
- 呼び出し元の既存 report に sub-agent 証跡欄が事前に用意されている場合だけ、その既存 report を sub-agent report として再利用し、空欄または placeholder だけを埋める。

どちらの場合も、`markdown-word-checker` は report path、check scope ごとの lint 実行結果、`skip` / `unsupported` / `failed gate` / `needs user review` の判定、aggregate gate state、backtick 回避チェック結果を呼び出し元へ返す。

### Markdown 資料作成 skill からの利用

Markdown 資料を作成する skill は、資料作成後に `markdown-word-checker` を呼ぶ。

対象例:

- `design-executor`: 設計文書を編集した後。
- `handover-memo-writer`: handover report を作った後。
- `report-output-manager`: report 本文テンプレートや report 生成方針を変えるとき。
- 将来追加する `markdown-document-writer`: 汎用 Markdown 資料を作成するとき。

資料作成 skill は、作業者向けに細かい用語ルールを説明しない。作成した Markdown を lint にかけ、指摘があれば通常の修正作業として扱う。

資料作成 skill は、自分が作成または編集した Markdown ファイル一覧を `markdown-word-checker` へ明示ファイルとして渡す。作成直後は、その明示ファイルを対象にした focused lint を既定とする。task 完了時または review gate では、focused lint とは別に full lint を実行または要求するかを検討する。

明示ファイルが `reports/` 配下など通常の full lint 対象外になり得る場合でも、資料作成 skill は focused lint の可否と理由を確認し、その結果を呼び出し元 report に残す。

```text
design-executor / handover-memo-writer / markdown-document-writer
└─ markdown-word-checker [親が実行]
```

## 作業者向け表示

資料作成者へ提示するルールは次の短文だけにする。

```text
Markdown 資料を作成または編集したら、このリポジトリの Markdown lint を実行してください。
lint の指摘に従って本文を直してください。
指摘が不適切に見える場合は、回避せず lint 設定見直しとして報告してください。
```

`markdown-word-checker` の詳細、`whitelist`、`prh`、`aliases`、複合語、個別語句の扱いは、作業者向け表示に出さない。

## `markdown-word-checker` の required flow

1. 対象リポジトリの root を確認する。
2. repo 固有 lint 設定の存在を確認する。
3. 対象ファイルを決める。
   - 明示ファイルがある場合は focused lint を優先する。
   - task 完了や review gate では full lint を検討する。
4. 利用可能な lint コマンドを選ぶ。
   - repo の `package.json` に `lint:md` があれば優先する。
   - focused validation では shared script の explicit file mode を使う。
5. lint を実行する。
6. backtick や quote による lint 回避がないか確認する。
   - コード、識別子、実際の UI 表示など、Markdown 上の inline code として妥当な箇所は検査対象外にする。
   - 一般語、未登録語、表記揺れを lint から逃がす目的の backtick は指摘に含める。
7. 指摘を分類する。
   - 本文修正で直す指摘。
   - repo 固有設定の見直しが必要な指摘。
   - 意図的な stricter gate として記録する指摘。
   - `skip` / `unsupported` / `failed gate` として記録する検査状態。
8. repo 固有設定の変更が必要な場合、利用者に exact entry をレビューしてもらう。
9. exact entry review が必要になった場合は gate を停止し、候補、理由、対象ファイル、呼び出し元 report path を呼び出し元へ返す。
10. 結果を呼び出し元 skill へ返す。

### 新語ルーティング決定表

`markdown-word-checker` は、lint 指摘や抽出候補に新しい語句が含まれる場合、次の順で分類する。この表は `markdown-word-checker` 内部の判断基準であり、作業者向け表示には展開しない。

| 判断対象 | 寄せ先 |
| --- | --- |
| typo、冗長な英単語、文脈不足の語句 | 本文修正。単独語で意味が薄い場合は、文脈が分かる複合語または日本語表現へ直す。 |
| 新しい概念として今後も資料中で許可する必要がある語句 | `markdown-whitelist.yaml` の意味付き `term` 候補。`description` で概念境界を確認できる形にする。 |
| 既存または新規の同じ概念として今後も許可する別表記 | `markdown-whitelist.yaml` の `aliases` 候補。意味が違う語句は `aliases` に混ぜない。 |
| 今後は正式表記へ直したい表記揺れ | `prh.yml` 候補。許可する別名ではなく、直すべき表記として扱う。 |
| lint 対象、root、`package.json`、`markdown-targets.json`、whitelist、prh など repo 設定の欠落 | 本文や語彙候補ではなく、`skip` / `unsupported` / `failed gate` の設定状態として分類する。 |
| 判断不能、または repo 固有設定の追加、削除、変更を伴う候補 | exact entry と理由を利用者レビューへ回す。承認前に repo 固有設定を編集しない。 |
| ChikkarPy / SudachiPy が出した候補 | 自動反映しない。候補整理、頻度、出現元、利用者レビュー材料に留める。 |

## `markdown-word-checker` の output contract

`markdown-word-checker` は、呼び出し元 skill へ次を返す。

- 対象リポジトリ root。
- 対象 Markdown ファイル。
- check scope ごとの個別 result。
  - `focused`: 対象ファイル、実行した command と exit status、`pass` / `skip` / `unsupported` / `failed gate` / `needs user review`、理由、残リスク。
  - `full`: 対象ファイルまたは target set、実行した command と exit status、`pass` / `skip` / `unsupported` / `failed gate` / `needs user review`、理由、残リスク。
- 実行しなかった検査の `skip` / `unsupported` 理由。
- 必須 gate または repo 設定済み検査が失敗した場合の `failed gate` 判定。
- aggregate gate state。
  - `failed gate` を最優先する。
  - 次に `needs user review`、`unsupported`、`skip`、`pass` 相当の順で caller が判断できる材料を返す。
  - focused と full の両方が対象になった場合、片方の `pass` は片方の `failed gate`、`needs user review`、`unsupported` を上書きしない。
- lint 指摘の分類結果。
- backtick 回避チェックの結果。
- lint 設定見直し要否。
- repo 固有設定変更が必要な場合の利用者レビュー要否。
- exact entry review 要否、候補、理由、対象ファイル、呼び出し元 report path。
- sub-agent に委譲した場合の report path。

`needs user review` は exact entry review 待ちで gate が停止している状態である。利用者承認後は、呼び出し元が適切な実装 owner に repo 固有設定編集を渡し、該当する focused lint または full lint、必要ならその両方を再実行し、同じ呼び出し元 report に更新結果と aggregate gate state を残す。exact entry がレビュー済みになっただけでは gate を閉じない。

`unsupported` は pass ではなく、呼び出し元の disposition が必要な状態である。呼び出し元は、必須 gate か任意 check か、repo が該当 check を設定済みか、normal path を満たすために残リスクとして許容できるかを report に記録して扱う。

## 利用者レビューが必要な変更

次は、agent review だけで完了扱いにしない。

- `markdown-whitelist.yaml` の `term` 追加、削除、変更。
- `markdown-whitelist.yaml` の `aliases` 追加、削除、変更。
- `markdown-whitelist.yaml` の `description` 変更。
- `prh.yml` の置換規則追加、削除、変更。
- repo 固有の target 除外範囲を広げる変更。

利用者は、最終的に追加、削除、変更される exact entry を見る必要がある。

## ChikkarPy / SudachiPy の扱い

SudachiPy は語彙抽出と日本語形態素単位の whitelist 検査に使う。

ChikkarPy は同義語候補の grouping に使う。ChikkarPy が返した候補は、候補整理の材料であり、`aliases` や `prh` へ自動反映してはならない。

`markdown-word-checker` は、同義語候補を次の形で扱う。

- 候補グループを作る。
- 頻度と出現元を示す。
- 利用者レビュー用の小さい候補単位に分ける。
- 承認前に whitelist / prh を編集しない。

## review-enforcer の変更方針

`review-enforcer` には、Markdown 変更時の詳細 lint 手順を持たせない。

変更後の `review-enforcer` は、次だけを持つ。

- Markdown 関連変更は `markdown-word-checker` を呼ぶ。
- Markdown lint gate が失敗した場合、task 完了扱いにしない。
- focused / full の個別 result と aggregate gate state を review report に含め、片方の pass で片方の失敗や user review 待ちを消さない。
- whitelist / prh 変更は利用者の exact entry レビューが必要。
- exact entry がレビュー済みでも、repo 固有設定編集と該当 lint 再実行が済むまで review gate を閉じない。
- Markdown lint が task/review gate として必須、または repo が該当 check を設定済みの場合、`unsupported` だけでは完了扱いにしない。
- Markdown lint 未導入 repo で focused lint も full lint も実行できない場合に限り、unsupported 理由と残リスクを review report に記録し、利用者意図を満たせる normal path なら hold/disposition として扱える。
- review report には `markdown-word-checker` の結果を証跡として含める。

これにより、review skill が単語検査の細則を持ち続けて肥大化することを防ぐ。

## Markdown 資料作成 skill の変更方針

Markdown 資料を作る skill は、次の共通契約を持つ。

- 資料作成者へ細かい語彙規則を説明しない。
- 作成後に `markdown-word-checker` を呼ぶ。
- 作成または編集した Markdown ファイル一覧を明示ファイルとして `markdown-word-checker` へ渡す。
- 作成直後は focused lint を既定にし、task 完了または review gate では full lint を別途検討する。
- `reports/` 配下など通常の full lint 対象外になり得る Markdown でも、明示ファイルとして focused lint 可否と理由を確認し、結果を呼び出し元 report に残す。
- focused lint と full lint の両方を扱う場合は、scope ごとの個別 result と aggregate gate state を呼び出し元 report に残す。
- lint 指摘は本文修正か lint 設定見直しとして扱う。
- lint 設定見直しが必要な場合、利用者レビューなしに repo 固有設定を変更しない。
- exact entry review 後は、適切な実装 owner が repo 固有設定を編集し、該当 lint を再実行した結果で呼び出し元 report を更新する。
- sub-agent を使わず focused lint を実行した場合でも、lint 結果、分類結果、`skip` / `unsupported` / `failed gate` / `needs user review`、aggregate gate state、lint 設定見直し要否、exact entry review 要否を呼び出し元 report に記録する。

既存 skill では、まず `design-executor` と `handover-memo-writer` を対象にする。将来、汎用の `markdown-document-writer` skill を追加する場合も同じ契約に従う。

## 完了条件

この設計の実装は、次を満たしたとき完了とする。

- `skills/markdown-word-checker/SKILL.md` が追加されている。
- `markdown-word-checker` が repo 固有 `tools/lint/` 設定を読むことを明記している。
- `review-enforcer` が Markdown lint 詳細を直接持たず、`markdown-word-checker` を呼ぶ構造になっている。
- Markdown 資料作成 skill が、作成後に `markdown-word-checker` を使う契約を持っている。
- repo 固有 whitelist / prh 変更には利用者の exact entry レビューが必要であることが残っている。
- shared script の移動有無が明示され、初期実装では script を移動しない。
- skill hierarchy design を更新し、新 skill と呼び出し関係を反映している。
- 複数リポジトリ向けの最低構成と、`skip` / `unsupported` / `failed gate` の扱いが `markdown-word-checker` に明記されている。
- `markdown-word-checker` が sub-agent に lint 証跡収集を委譲する場合の report 契約が明記されている。
- backtick 回避チェックが required flow と output contract に残っている。

## 非目標

- CodexSkill 側に IbisDuck 固有用語を登録しない。
- 作業者向け資料に細かい用語規則を列挙しない。
- ChikkarPy 候補を自動で whitelist / prh に反映しない。
- 初期実装で shared script を移動しない。
- lint を通すために大量の whitelist entry を自動追加しない。

## 初期実装タスク案

1. `skills/markdown-word-checker/SKILL.md` を追加する。
2. `review-enforcer/SKILL.md` から Markdown lint 詳細を `markdown-word-checker` 参照へ寄せる。
3. `design-executor` と `handover-memo-writer` に、Markdown 作成後の `markdown-word-checker` 呼び出し契約を追加する。
4. `design/skill-hierarchy-design.md` と `skills/design/skill-hierarchy-design.md` を同期更新する。
5. 必要なら `review-enforcer` 配下の script 移動は後続 task として切り出す。

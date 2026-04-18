# 開始時インテーク方針

`development-orchestrator` が workflow に入る前に、ユーザーが今回何をしたいのかを確認する必要があるかを判断するときは、この方針を使う。

## この reference を読むタイミング

- 新規着手で、今回の作業目的がまだ task として固定されていないとき
- 再開ではない通常着手だが、ユーザーの依頼が broad で、どの task に入るべきか即断しづらいとき
- `tasks-status.md` や `reports/` から候補 task は見えるが、今回そのどれを優先すべきかがユーザー意図に依存するとき

次のときは通常この reference を読まなくてよい。

- ユーザーが今回の作業対象をすでに明示している
- 再開セッションで、`restart-handover-manager` により次 task が十分明確になっている
- 単一の active task しかなく、ユーザー意図とのズレ余地がほぼない

## 基本原則

- workflow 入口は `development-orchestrator` の一箇所に固定する。
- その入口で、必要な場合だけ「今回は何の作業をするか」をユーザーに確認する。
- 毎回機械的に質問するのではなく、既存 tracking と直近依頼で足りるならそのまま進める。
- 聞くなら、task 選定前に聞く。

## 確認する内容

必要な場合は、少なくとも次を揃える。

- 今回の作業対象
- 新規着手か再開か
- 既存 task を進めるのか、新しい task を起こすのか

## 確認後の流れ

1. ユーザー意図を current run の対象として固定する。
2. その意図を `tasks-status.md` と `phases-status.md` と照合する。
3. 既存 task に対応するなら、その task を current task 候補にする。
4. 対応 task が足りなければ `task-consistency-manager` や `task-breakdown-planner` 側へつなぐ。
5. その後に標準 workflow へ入る。

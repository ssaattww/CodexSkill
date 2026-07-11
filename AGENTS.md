# AGENTS.md

## Skill-First Constraints

- 作業前と作業中は、該当する skill が既にあるかを必ず確認しながら進めること。
- 判断に迷いが出たら、まず skill 不足を疑い、既存 skill の再確認または skill の追加・更新要否を先に検討すること。
- Git リポジトリを変更する作業は、`development-orchestrator/scripts/task_routine.py` で 1 task の routine を開始し、現在 step と証拠を永続化してから進めること。
- task 完了前に、既存 skill 改善の要否と、agent が直接繰り返している出力の tool/script 化要否を必ず記録すること。既存責務内の低リスクで可逆な改善は自動実施し、新規 skill や外部公開 tool は確認境界を維持すること。
- GitHub Issue と feedback point は履歴・重複・follow-up の正本として使うが、実行を思い出す唯一の trigger にしないこと。現在の次工程は local task routine state と hook を正本とすること。
- 上記制約はこのリポジトリ内で最大優先の制約として扱うこと。

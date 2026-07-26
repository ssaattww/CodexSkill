# AGENTS.md

## Skill-First Constraints

- 作業前と作業中は、該当する skill が既にあるかを必ず確認しながら進めること。
- 判断に迷いが出たら、まず skill 不足を疑い、既存 skill の再確認または skill の追加・更新要否を先に検討すること。
- 上記 2 点はこのリポジトリ内で最大優先の制約として扱うこと。

## Repository Development Policy

- CodexSkillリポジトリ自身の保守にはTDDを適用しないこと。
- このリポジトリの作業では、`tdd-executor`を起動せず、Red/Green証拠を目的としたtestまたはworkflowを追加しないこと。
- 検証には、既存lint、schema validation、scriptの構文確認、build、package生成、配布物構造確認、設計とSkill contractの整合確認を使用すること。
- 利用者がCodexSkillリポジトリの方針変更を明示した場合だけ、変更後の指示を優先すること。

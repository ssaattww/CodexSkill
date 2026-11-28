# READMEの記載指針

READMEは入口としてすぐ読める長さにし、詳しい設計や運用手順は詳細文書へ分けてリンクする。

## ルートREADME

できること、前提、最短の動作コマンドを簡潔に示し、全体設計と各プロジェクトのREADMEへリンクする。コマンドを実行する場所も明記する。

## プロジェクトREADME

役割を一文で示し、最小の利用例と個別設計へのリンクを置く。相対リンクはREADME自身の場所から解決する。表は条件や結果を比較するときに限り、通常の手順や利用例は短いコードブロックにする。

## 記入例

名前と値は架空の例。ルートのコマンドはリポジトリ直下で実行する。

```markdown
# Acme Session Tools
Records and replays operator sessions.
Requires .NET 10 SDK.
[Overall design](docs/basic-design.md) · [Capture](src/Acme.Capture/README.md) · [Replay](src/Acme.Replay/README.md)
```

ルートREADMEの起動コマンド（リポジトリ直下で実行）:

```sh
dotnet run --project src/Acme.Capture/Acme.Capture.csproj -- --output artifacts/demo.json
```

プロジェクト例のコマンドはリポジトリ直下で実行する。設計リンクは `src/Acme.Capture/README.md` からの相対パスで、`src/Acme.Capture/docs/design.md` を指す。

```markdown
# Acme.Capture
Records the sample session to `artifacts/demo.json`.
[Capture design](docs/design.md)
```

プロジェクトREADMEの利用コマンド（リポジトリ直下で実行）:

```sh
dotnet run --project src/Acme.Capture/Acme.Capture.csproj -- --output artifacts/demo.json
```

---
title: 【実践】Databricks Agent SkillsでClaude CodeにLakeflowパイプラインを作らせてみた
tags:
  - Databricks
  - LakeFlow
  - ClaudeCode
  - バイブコーディング
  - AgentSkills
private: false
updated_at: '2026-06-30T13:58:35+09:00'
id: baaab4e6ed75a7c0dd0d
organization_url_name: databricks
slide: false
ignorePublish: false
---
# はじめに

DAIS週のタイミングで、コーディングエージェント向けのDatabricks知識キット `databricks-solutions/ai-dev-kit` がdeprecatedとなり、公式org配下の `databricks/databricks-agent-skills` が「今後の正典(source of truth)」として登場しました。

実は前回、ai-dev-kitをClaude Codeから使ってDatabricksをバイブコーディングする記事を書きました。

https://qiita.com/taka_yayoi/items/2c596f1e4993fe3ba3ac

前回紹介したai-dev-kitは Skills(知識)/ MCP Server(実行)/ Core Library の3コンポーネント構成で、自然言語でSQL Warehouseの一覧取得からUnity Catalogの探索、AI/BIダッシュボードの自動作成まで一気通貫で実行できるものでした。今回はそのai-dev-kitがdeprecatedされ、後継のdatabricks-agent-skillsに移行したことを受けて、前半でai-dev-kitとの違いを整理し、後半で新版を使って実際に何ができるのかを、コーディングエージェントにDatabricks上のパイプラインを作らせる実践を通じて示します。

関連リポジトリとドキュメント。

- 新(正典): https://github.com/databricks/databricks-agent-skills
- 旧(deprecated): https://github.com/databricks-solutions/ai-dev-kit
- 公式ドキュメント(日本語): https://docs.databricks.com/aws/ja/agent-skills/
- Agent Skills標準: https://agentskills.io/specification

# ai-dev-kitとの違い

## リポジトリと位置づけの変化

旧 ai-dev-kit はフィールドエンジニアリングが提供する `databricks-solutions` org のキットでした。新 databricks-agent-skills は公式 `databricks` org に移管され、Databricksのドキュメントにも正式機能「Agent skills」として掲載されています。フィールド発の実験的キットから、プロダクトの一部への格上げです。

https://github.com/databricks/databricks-agent-skills

## stable と experimental の二層構造

旧版はスキルがすべて `databricks-skills/` 配下にフラットに並んでいました。新版は正式サポートの `skills/`(stable)と、ai-dev-kit由来をベストエフォートで取り込んだ `experimental/` に分離されています。experimentalはデフォルトではインストールされず、`--experimental` を明示したときだけ入ります。普通の利用ではstableを使えば十分です。

experimentalの一覧と注意書きはこちらにまとまっています。

https://github.com/databricks/databricks-agent-skills/tree/main/experimental

## インストールとアップデートの統合

旧版は `curl | bash install.sh` という単一スクリプトが入口でした。新版はDatabricks CLIの `databricks aitools install` が正典の経路となり、更新も `databricks aitools update` に統合されています。加えてClaude Code / Codex / Copilot / Cursor の4ターゲットにプラグインマーケットプレイス経由でも配布されます。

## スキルの親子階層

旧版にはスキル間の親子関係がありませんでした(parent宣言ゼロのフラット構造)。新版は `databricks-core` を入口の親スキルとし、各プロダクトスキルが `parent: databricks-core` を宣言する階層構造になっています。エージェントはまず `databricks-core` でCLI確認・認証・プロファイル選択・データ探索の基礎を押さえ、そこから目的のプロダクトスキルへ進みます。

| 観点 | 旧 ai-dev-kit | 新 databricks-agent-skills |
|------|---------------|----------------------------|
| org | databricks-solutions(フィールド) | databricks(公式) |
| 構成 | stable/experimentalの区別なし | skills(stable)+ experimental に分離 |
| インストール | install.sh 単一スクリプト | databricks aitools install(CLIが正典)+ 4ターゲットのプラグイン |
| 更新 | install.sh 再実行 | databricks aitools update |
| スキル階層 | フラット(parent宣言ゼロ) | databricks-core を根とする親子構造 |
| commands/hooks | hooks.json 1個 | setup/doctorコマンド + ルーティング/コンテキスト/認証ヒントのhooks |

## 知識と実行の分離

設計思想として最も大きい変化がこれです。前回の記事で動かしたai-dev-kitは4つの部品から成る「キット」でした。

- databricks-skills(知識レイヤー)
- databricks-mcp-server(MCP実行レイヤー)
- databricks-tools-core(再利用可能なツールAPI)
- databricks-builder-app(チャットUI付きスターターアプリ)

前回 `List my SQL warehouses` と打つとMCPの `list_warehouses` ツールが呼ばれ、`covidスキーマのテーブルからダッシュボードを作って` でAI/BIダッシュボードが自動生成されていた、あの「実行」を担っていたのがMCP Serverとtools-coreです。

新 databricks-agent-skills は、このうち知識レイヤー(スキル)単体に絞られています。MCPサーバー・tools-core・builder-appはリポジトリに含まれません。つまり「エージェントに何を知らせるか(知識)」と「エージェントが実際にワークスペースを操作する手段(実行)」が分離されました。

新版では、実行はエージェントが叩くDatabricks CLI(あるいはManaged MCP)が担い、ガバナンスはUnity Catalogが担います。スキルは「現行のAPIとベストプラクティスでCLIをどう使うべきか」を教える知識に専念します。この分離により、知識の更新(スキルのバージョンアップ)と実行基盤(CLIやManaged MCP)の進化を独立して回せるようになりました。

# 新版で何ができるか(実践)

ここからが本題です。新版を入れると、コーディングエージェントがDatabricks固有の現行知識を持つことで、APIをハルシネートせずに正しくワークスペース上にリソースを構築できるようになります。それを、Lakeflow Spark宣言型パイプライン(旧DLT)をエージェントに作らせる例で確認します。stableスキルのみで完結します。

## 前提

- Databricks CLI v1.0.0 以上(`databricks --version` で確認)
- コーディングエージェント(本記事ではClaude Code を想定。Cursor / Codex CLI / Copilot でも可)
- 書き込み可能なワークスペースのプロファイル(`databricks auth profiles` で確認)
- Unity Catalog 上に書き込めるカタログ/スキーマ

agent skillsを使うにはCLIがGA(v1.0.0以上)である必要があります。v0.205〜0.299はPublic Previewで、`aitools` が無かったり古い挙動になります。Homebrewで上げる場合、Homebrew 6.0.0以降はサードパーティtapの明示的な信頼が必要なので、初回は次の順で実行します。

```bash
brew trust databricks/tap
brew upgrade databricks
databricks --version
```

CLI認証の手順は Databricks のドキュメントを参照してください。

https://docs.databricks.com/aws/ja/dev-tools/cli/authentication

## 手順1: stableスキルをインストールする

正典であるCLI経由で入れます。

```bash
databricks aitools install
```

実行すると、検出されたエージェントと、インストールされたスキルのバージョン・数が表示されます。

```text
Installing Databricks AI skills for Claude Code, Cursor, Codex CLI...
Using skills version 0.2.5
Installed 10 skills.
```

CLIがコーディングエージェントを自動検出し、stableスキルを各エージェントのスキルディレクトリに配置します(Claude Codeなら `~/.claude/skills/`)。experimentalは入りません。これがデフォルトかつ推奨の挙動です。

なお、ここでインストールされるのはCLIのリリース版に紐づくセット(本記事執筆時点の skills version 0.2.5 では10スキル)です。GitHubのmainブランチには先行マージされたスキルがさらに並んでいますが、CLIが入れるのはあくまでリリース版なので、本記事はこの10スキルを前提に進めます。

特定のスキルだけ入れたい場合は名前を指定します。

```bash
databricks aitools install databricks-pipelines
```

![Screenshot 2026-06-30 at 12.55.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4703dfd2-f317-4f85-82ce-8b978da301ba.png)

## 手順2: 配置されたことを確認する

何が入ったかは目視で確認できます。

```bash
ls ~/.claude/skills/
```

v0.2.5では以下の10スキルが配置されます。

```text
databricks-app-design   databricks-lakebase
databricks-apps         databricks-model-serving
databricks-core         databricks-pipelines
databricks-dabs         databricks-serverless-migration
databricks-jobs         databricks-vector-search
```

各スキルは frontmatter 付きのMarkdown(`SKILL.md`)と、必要に応じて読み込まれる `references/` から成ります。親子関係は frontmatter の `parent` で表現されており、たとえば `databricks-pipelines` は `databricks-core` を親に持ちます。エージェントはまず親を読み、次に目的のスキルを読みます。

![Screenshot 2026-06-30 at 12.56.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2a4e3099-48e3-40dd-9a9f-0c10e838cfcb.png)

## 手順2.5: 旧スキルの残骸に注意(移行時の落とし穴)

ai-dev-kitを以前使っていた場合、新版インストール時にこんな案内が出ることがあります。

```text
Found skills installed before state tracking was added. Run 'databricks aitools install' to refresh.
```

これは状態管理が入る前に置かれた古いスキルが残っているサインです。実際に確認すると、新版の10スキルに混じって `databricks` という名前のスキルが残っていました(新版では `databricks-core` に改名されています)。中身を見ると旧Asset Bundles(`asset-bundles.md`)を抱えたままで、`compatibility` も古いバージョンを指していました。

新版の `databricks-core` と役割が重複し、しかも知識が古いままなので、残すとエージェントが旧APIを拾うリスクがあります。削除ではなく退避しておくと、切り分けにも使えて安全です。

```bash
mv ~/.claude/skills/databricks ~/databricks-skill-backup-ai-dev-kit
ls ~/.claude/skills/
```

退避後、`ls` の結果がaitools管理元(`~/.databricks/aitools/skills/`)と同じ10スキルちょうどになっていれば、新版だけが効くクリーンな状態です。「旧スキルが残っていると新旧の知識が混在する」という、ai-dev-kitからの移行で実際に踏みやすいポイントです。

## 手順3: スキルが効いているかの確認ポイント

スキルが働いているかどうかは、エージェントの挙動を見れば分かります。チェックすべきは次の点です。

- 実装に入る前に `databricks-pipelines` スキルを読み込む宣言があるか
- 親の `databricks-core` の作法どおり、CLI・認証を先に確認し、プロファイルを勝手に選ばずユーザーに選ばせるか
- 生成コードが現行のLakeflow構文か(レガシーDLTの `import dlt` / `@dlt.table` ではないか)

スキルが無いエージェントは、古い学習データからレガシーDLTを出したり古いAPIをハルシネートしがちです。スキルを入れた後はこの3点が満たされ、それ自体が「知識が効いている」証拠になります。具体的にどの記述がこの挙動を生んでいるかは、後述の「スキルの中身を覗く」で確認します。

## 手順4: エージェントにパイプラインを作らせる

生成ファイルが散らからないよう、専用ディレクトリで起動するのがおすすめです。

```bash
mkdir -p ~/lakeflow-skill-demo && cd ~/lakeflow-skill-demo
claude
```

Claude Code(または任意のエージェント)に、たとえば次のように指示します。

```text
Databricksにサンプルデータを取り込むLakeflowのSpark宣言型パイプラインを作ってください。
Auto Loaderでブロンズテーブルに取り込み、Expectationsでデータ品質チェックを入れてください。
まずはバンドルなしで素早く試したいです。
```

スキルが入っていれば、エージェントは概ね次の流れで動きます。実際に試したところ、ほぼこの通りに進みました。

1. `databricks-pipelines` スキルを読み込み(`Skill(databricks-pipelines)` と表示)、親の `databricks-core` の作法に従って認証状態を確認
2. プロファイルを自動選択せず、書き込み先のカタログ/スキーマも含めて候補を提示してユーザーに選ばせる
3. プロトタイプ用の「バンドルなしCLIイテレーション」ワークフロー(スキル内のWorkflow C)を選択
4. サーバーレスを既定として、パイプラインの `.sql` をローカルに生成
5. 認証が切れていれば `databricks auth login --profile <プロファイル>` を案内
6. `databricks workspace import-dir` でアップロードし、`databricks pipelines create` でサーバーレスパイプラインを作成・更新

Auto Loader や Expectations、AUTO CDC といった個別パターンは、スキルの `references/` から必要なときだけ読み込まれます。今回はSQLのAuto Loaderとexpectationsのリファレンスが読み込まれました。

![Screenshot 2026-06-30 at 12.54.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5fff207e-d584-45ad-85b6-2cb00cc0dca4.png)
![Screenshot 2026-06-30 at 12.55.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/213452ba-bf47-403d-880e-33516671119c.png)

## スキルの中身を覗く(なぜ正しく動いたのか)

「知識レイヤー」が具体的に何を渡しているのかを、今回使われたスキルの中身で確認します。エージェントの挙動が、そのまま `SKILL.md` の記述に対応していることが分かります。

[`databricks-pipelines`](https://github.com/databricks/databricks-agent-skills/blob/main/skills/databricks-pipelines/SKILL.md) の冒頭(frontmatter)はこうなっています。`parent` で `databricks-core` を親に指定し、対象が現行のLakeflow Spark宣言型パイプライン(旧DLT)であること、実装前に読み込むことが宣言されています。

```yaml
---
name: databricks-pipelines
description: Develop Lakeflow Spark Declarative Pipelines (formerly Delta Live Tables) on Databricks. Use when building batch or streaming data pipelines with Python or SQL. Invoke BEFORE starting implementation.
compatibility: Requires databricks CLI (>= v1.0.0)
metadata:
  version: "0.3.0"
parent: databricks-core
---
```

エージェントがプロファイルを勝手に選ばなかったのは、親の [`databricks-core`](https://github.com/databricks/databricks-agent-skills/blob/main/skills/databricks-core/SKILL.md) に明確な作法が書かれているからです。

```text
## Profile Selection - CRITICAL

**NEVER auto-select a profile.**
```

そして生成SQLのデータ品質チェックは、[`references/expectations-sql.md`](https://github.com/databricks/databricks-agent-skills/blob/main/skills/databricks-pipelines/references/expectations-sql.md) の知識そのものです。warn(既定)・行破棄・パイプライン失敗を `ON VIOLATION` で書き分けるパターンが、リファレンスにこう書かれています。

```sql
CONSTRAINT name1 EXPECT (cond1),                       -- warn (default)
CONSTRAINT name2 EXPECT (cond2) ON VIOLATION DROP ROW, -- drop violating rows
CONSTRAINT name3 EXPECT (cond3) ON VIOLATION FAIL UPDATE -- fail on first violation
```

この知識を受けて、エージェントが生成した `bronze_events.sql` のExpectations部分が以下です。`time` がNULLの行は記録だけ残し(warn)、想定外の `action` は破棄(drop)する、という意図どおりの書き分けになっています。

```sql
-- time が NULL の行は記録だけして残す（warn）
CONSTRAINT valid_time   EXPECT (time IS NOT NULL),
-- action は open / close のみ許可。違反行は破棄（drop）
CONSTRAINT valid_action EXPECT (action IN ('open','close')) ON VIOLATION DROP ROW
```

取り込み部分もレガシーDLTの `import dlt` / `@dlt.table` ではなく、現行の `STREAM read_files(...)` で書かれていました。スキル(知識)が、現行APIでの実装(実行)を正しく駆動していることが、コードレベルで確認できます。

![Screenshot 2026-06-30 at 13.51.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3a078f29-9daa-431c-8e4b-edf3db79eb79.png)

## 手順5: 実行結果を確認する

エージェント任せにせず、自分の目でワークスペース側を確認します。

```bash
databricks pipelines list --profile <your-profile>
```

確認したいポイントは3つです。

- 生成されたコードが現行のLakeflow構文になっているか(レガシーDLTでないか)
- パイプラインがワークスペースに作成され、実行できているか
- Unity Catalog の対象カタログ/スキーマにテーブルが生成されているか

ここで「スキル(知識)がCLI(実行)を正しく駆動し、Unity Catalog(ガバナンス)の下でリソースができた」という、知識と実行の分離が具体的な形で見えます。

![Screenshot 2026-06-30 at 13.52.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d134347c-d576-486a-bc05-f426d60c8a8b.png)
![Screenshot 2026-06-30 at 13.53.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0b1e20cf-43f4-4f4c-ae45-995186e1e240.png)

## 手順6: 本番化したくなったら

プロトタイプが固まったら、同じスキルがDAB(Declarative Automation Bundles、旧Asset Bundles)ベースの本番ワークフローへ誘導します。`databricks pipelines init` でバンドル化し、`databricks bundle deploy` でデプロイする流れです。プロトタイプから本番まで、同一スキルの知識で一貫して進められます。

## 手順7: 後片付け

検証で作ったものは片付けておきます。

```bash
databricks pipelines list --profile <your-profile>
databricks pipelines delete <pipeline-id> --profile <your-profile>
```

ワークスペースにアップロードしたファイルも不要なら削除します。生成されたUCテーブルも検証用であれば削除しておきます。

## 次に試すstableスキル

同じ要領で、他のstableスキルも試せます。いずれもエージェントにDatabricks固有の現行知識を与えます。今回入った10スキルのうち、パイプライン以外の代表例です。

- [databricks-jobs](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-jobs): Lakeflow Jobs のオーケストレーション
- [databricks-apps](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-apps) と [databricks-app-design](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-app-design): AppKit(TypeScript)によるフルスタックアプリ構築とUX設計
- [databricks-dabs](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-dabs): DAB によるリソースのデプロイ管理
- [databricks-vector-search](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-vector-search): RAG向けのVector Searchエンドポイントとインデックス
- [databricks-lakebase](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-lakebase): Lakebase Postgres(branching、autoscaling、synced tables、Data API)
- [databricks-model-serving](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-model-serving): Model Serving エンドポイントとAI Gateway
- [databricks-serverless-migration](https://github.com/databricks/databricks-agent-skills/tree/main/skills/databricks-serverless-migration): クラシックコンピュートからサーバーレスへの移行

# まとめ

ai-dev-kitからdatabricks-agent-skillsへの移行は、単なるリポジトリの引っ越しではなく、知識(スキル)と実行(CLI / Managed MCP)を分離し、知識レイヤーを公式プロダクトとして階層化・標準化する設計変更です。前回の記事ではMCPサーバー込みで実行までを一つのキットで担っていましたが、新版は知識レイヤーに専念し、実行はCLIやManaged MCPへ委ねる形になりました。実際に使うと、コーディングエージェントが現行のLakeflow / DAB / サーバーレスのパターンで、Unity Catalogのガバナンス下にリソースを構築できることが、生成コードのレベルまで確認できます。まずはstableの `databricks aitools install` から始めるのがおすすめです。

参考リポジトリとドキュメント。

- https://github.com/databricks/databricks-agent-skills
- https://github.com/databricks-solutions/ai-dev-kit
- https://docs.databricks.com/aws/ja/agent-skills/

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

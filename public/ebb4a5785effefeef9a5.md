---
title: DatabricksアシスタントにおけるMCP経由でのUC関数へのアクセス
tags:
  - MCP
  - Databricks
  - Databricksアシスタント
private: false
updated_at: '2026-02-05T20:38:46+09:00'
id: ebb4a5785effefeef9a5
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

Databricksアシスタントが[MCPサーバーへの接続](https://docs.databricks.com/aws/ja/assistant/mcp)をサポートしました。接続先の一つとしてUnity Catalog関数を選択できます。

この記事では、UC関数をMCPサーバーとしてアシスタントに公開するデモを通じて、「この機能の何が嬉しいのか」を考えます。

# UC関数をMCPで公開する意味は何か

最初に結論を書きます。

UC関数をMCPで公開する価値は「汎用的なデータツールを作れること」ではありません。
価値があるのは**ビジネスロジックのカプセル化**です。

「売上」という一つの数字を出すだけでも、実際には以下のようなルールが必要です:

- 返品・キャンセル済み注文は除外する
- 商品ごとの割引率を適用する
- カテゴリに応じた税率を適用する(標準税率10%、食品・飲料は軽減税率8%)

ビューやCTEでもロジックの統一はできますが、それはSQLを書ける人が
`SELECT * FROM v_net_sales WHERE region = '関東'`と書ける前提です。
UC関数をMCPサーバーとしてアシスタントに公開すると、
SQLを書けない人が「関東の先月の売上を教えて」と聞くだけで、
同じロジックに基づいた正しい結果を得られます。

整理すると:

- **定義の統一**: 誰が使っても同じ計算ロジックで「売上」が算出される
- **セルフサービス**: SQLを書けない人が自然言語で正しい結果を得られる
- **ガバナンス**: Unity CatalogのACL・リネージ・監査ログで、
  誰がいつ何を実行したか記録される
# デモの概要

ECサイトの注文データを題材に、以下の4つのUC関数を作成してアシスタントに接続します。

| 関数 | 引数 | カプセル化されるルール |
|------|------|----------------------|
| `net_sales` | 開始日, 終了日, リージョン | 返品除外・割引適用・カテゴリ別税率で算出する「正味売上」の定義 |
| `monthly_kpi` | 年月 | 正味売上・有効注文数・客単価・返品率の公式算出方法 |
| `product_profitability` | カテゴリ, 開始日, 終了日 | 粗利 = 割引後**税抜**売上 - 仕入原価(経理基準) |
| `target_achievement` | 年月 | 予実管理の「実績」をnet_salesと同一定義で算出 |

各関数は参照するテーブルを内部に固定しており、引数はフィルタ条件(期間・リージョン・カテゴリ)や閾値など、分析の観点を制御するパラメータに限定しています。

# 環境構築

## テーブル構成

5つのテーブルを作成します。軽減税率対象カテゴリ(食品・飲料)を含めることで、売上計算にビジネスルールが必要なデータにしています。

```python
CATALOG = "main"
SCHEMA = "mcp_demo"
S = f"{CATALOG}.{SCHEMA}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {S}")
spark.sql(f"USE {S}")
```

- `products`: 商品マスタ(定価と仕入原価を持つ)
- `category_tax_rates`: カテゴリ別税率(電子機器/家具/文具は10%、食品/飲料は8%)
- `orders`: 注文ヘッダ(ステータスにconfirmed/shipped/returned/cancelledを含む)
- `order_items`: 注文明細(商品ごとの割引率を持つ)
- `monthly_targets`: リージョン別月次売上目標

データ生成コードの全体はノートブックを参照してください。ノートブックはGitHubリポジトリに公開しています。

https://github.com/taka-yayoi/mcp_assistant

## UC関数の作成

各関数のCOMMENTがアシスタントへのツール説明になります。何を計算するのかだけでなく、なぜこの関数を使うべきかが伝わるように記述しています。

### net_sales: 正味売上

返品・キャンセル済み注文を除外し、商品ごとの割引率を適用後、カテゴリ別税率で税込み金額を計算します。

```sql
CREATE OR REPLACE FUNCTION net_sales(
    start_date STRING COMMENT '集計開始日(YYYY-MM-DD形式)',
    end_date STRING COMMENT '集計終了日(YYYY-MM-DD形式)',
    region_filter STRING COMMENT 'リージョン名。全リージョンの場合は ALL を指定'
)
RETURNS TABLE (
    region STRING, gross_sales BIGINT, discount_amount BIGINT,
    tax_amount BIGINT, net_sales_amount BIGINT, valid_order_count BIGINT
)
COMMENT '正味売上をリージョン別に算出します。返品・キャンセル済み注文を除外し、
商品ごとの割引率を適用後、カテゴリ別税率(標準10%/軽減8%)で税込み金額を計算します。
これが当社の「売上」の公式定義です。'
RETURN
    SELECT
        o.region,
        CAST(SUM(oi.quantity * oi.unit_price) AS BIGINT) AS gross_sales,
        CAST(SUM(oi.quantity * oi.unit_price * oi.discount_rate) AS BIGINT) AS discount_amount,
        CAST(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_rate) * ct.tax_rate) AS BIGINT) AS tax_amount,
        CAST(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_rate) * (1 + ct.tax_rate)) AS BIGINT) AS net_sales_amount,
        COUNT(DISTINCT o.order_id) AS valid_order_count
    FROM {schema}.orders o
    JOIN {schema}.order_items oi ON o.order_id = oi.order_id
    JOIN {schema}.products p ON oi.product_id = p.product_id
    JOIN {schema}.category_tax_rates ct ON p.category = ct.category
    WHERE o.status IN ('confirmed', 'shipped')
      AND o.order_date BETWEEN start_date AND end_date
      AND (region_filter = 'ALL' OR o.region = region_filter)
    GROUP BY o.region
    ORDER BY net_sales_amount DESC
```

**この関数がないと起こる問題**: 返品済み注文を含めて売上を計算してしまう、税率を一律10%で計算してしまう、割引前の定価で集計してしまう等。

### monthly_kpi: 月次KPIレポート

客単価は「ユニーク顧客数」で割る公式定義です。注文数で割ると数字が変わります。返品率の分母は全注文(キャンセル含む)です。

**この関数がないと起こる問題**: 部門ごとにKPIの定義がバラバラになり、経営会議で数字が合わない。

### product_profitability: 商品別収益性

粗利は「割引後**税抜**売上 - 仕入原価」で計算します。税込み金額で粗利を出すとカテゴリ間で税率差(食品8% vs 電子機器10%)が入り込み、不公平な比較になります。

**この関数がないと起こる問題**: 税込み金額で粗利を計算してしまい、正しい収益性が見えない。

### target_achievement: 予実管理

実績は`net_sales`と同じ定義(返品除外・割引後・税込み)で算出します。目標設定時と実績集計時で「売上」の定義が一致していることを保証します。

**この関数がないと起こる問題**: 目標設定時と実績集計時で異なるSQLを使い、達成率の数字が信頼できない。

## 動作確認

関数を作成したら、アシスタントに接続する前にSQLで直接実行して動作確認します。

```sql
SELECT * FROM net_sales('2025-01-01', '2025-03-31', 'ALL')
```

![Screenshot 2026-02-05 at 20.28.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/26ad42f5-8993-4d11-a40c-0dd712dd10c0.png)

```sql
SELECT * FROM monthly_kpi('2025-01')
```

![Screenshot 2026-02-05 at 20.29.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/632749ad-fada-4004-b5f8-176f818977aa.png)

```sql
SELECT * FROM product_profitability('ALL', '2025-01-01', '2025-06-30')
```

![Screenshot 2026-02-05 at 20.29.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f5426711-0b1c-4a28-a550-82ba74d78f86.png)

```sql
SELECT * FROM target_achievement('2025-03')
```

![Screenshot 2026-02-05 at 20.30.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fb9fc523-50ef-4d39-b791-08636d0455b3.png)

# MCPサーバーとしてアシスタントに接続する

## 設定手順

1. アシスタントパネルを開く(右側の吹き出しアイコン)
2. ⚙ 設定(歯車アイコン)をクリック
3. **MCPサーバー**セクションで **＋ サーバーを追加** をクリック
4. **Unity Catalog関数**を選択
5. 対象のカタログ → スキーマを選択
6. **保存**をクリック

![Screenshot 2026-02-05 at 13.55.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b97d2da1-be9e-4dc6-82a6-8a0a0bd3b24c.png)
![Screenshot 2026-02-05 at 13.55.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/80cad6c1-6c1a-430f-8cb6-5c2f813d1297.png)
![Screenshot 2026-02-05 at 17.23.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ab340c45-b595-4e47-aecd-f691d0fdc3b0.png)
![Screenshot 2026-02-05 at 17.24.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ad989745-107a-4042-bd4f-ac44817c9973.png)

## エージェントモードに切り替え

MCPサーバーは[エージェントモード](https://docs.databricks.com/aws/ja/notebooks/use-databricks-assistant#assistant-modes)でのみ動作します。アシスタントパネルの入力欄左のモード切替で**エージェント**を選択してください。

# デモシナリオ

## シナリオ 1: 「Q1の売上はいくら?」

営業マネージャーが経営会議の準備で売上を確認するシーンです。

**プロンプト:**

> 2025年の第1四半期のリージョン別売上を教えてください。

![Screenshot 2026-02-05 at 17.24.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4d239ea6-782c-45b0-b13b-8ee33a7a064b.png)

ここで注目すべきは以下の点です:

- アシスタントが「第1四半期」を`2025-01-01`〜`2025-03-31`に自動変換している
- `net_sales`関数が選択され、返品除外・割引適用・カテゴリ別税率がすべて適用されている
- ユーザーはこれらのルールを知らなくても正しい数字を得られる

もしこの関数がなければ、ユーザーが自力で書くSQLは`SELECT region, SUM(quantity * unit_price) FROM orders ...`のように、返品を含み割引も税率も無視したものになりがちです。

## シナリオ 2: 「今月のKPIをまとめて見たい」

**プロンプト:**

> 2025年3月のKPIを教えてください。

![Screenshot 2026-02-05 at 17.25.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a5c27535-6d84-4fe5-afa1-14abffad2a33.png)

`monthly_kpi`関数が呼ばれ、正味売上・有効注文数・客単価・返品率が一度に返ります。客単価の分母がユニーク顧客数であること、返品率の分母が全注文(キャンセル含む)であることは、関数内部で保証されています。

## シナリオ 3: 「食品カテゴリの利益率は?」

**プロンプト:**

> 上半期の食品カテゴリの商品別利益を見せてください。粗利率が低い商品はどれですか?

![Screenshot 2026-02-05 at 17.26.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8d6ec253-6d53-42fc-abc2-75c147c6e796.png)
![Screenshot 2026-02-05 at 17.26.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4b9c39fe-0b39-4cb7-87ad-3db25028fb07.png)
![Screenshot 2026-02-05 at 17.27.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0dd6ceb3-aee9-46aa-8c80-48a6eaab4fdf.png)

`product_profitability('食品', '2025-01-01', '2025-06-30')`が呼ばれます。粗利が「割引後税抜売上 - 原価」で正しく計算されていることがポイントです。

## シナリオ 4: 「3月の目標達成率は?」

**プロンプト:**

> 2025年3月の売上目標の達成率をリージョン別に教えてください。未達のリージョンはどこですか?

![Screenshot 2026-02-05 at 17.29.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/58c25410-6f2b-48fc-b05a-5da7ace2fae3.png)

`target_achievement`関数内の実績計算は`net_sales`と同じロジックを使っているため、目標と実績で基準がずれません。アシスタントは結果を解釈して未達リージョンを特定し、コメントを付けて回答します。

## シナリオ 5: 複数関数の連携

**プロンプト:**

> 2025年3月のKPIと目標達成率を確認して、目標未達のリージョンについてそのリージョンの商品別利益も教えてください。

![Screenshot 2026-02-05 at 17.30.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f35bc8be-2725-43c2-97c7-7f56ca790565.png)
![Screenshot 2026-02-05 at 17.30.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/419934c5-92d9-4419-ad74-0bf135cb4391.png)

エージェントモードのアシスタントが、以下のように複数の関数を自律的に呼び分けます:

1. `monthly_kpi('2025-03')`で全体のKPIを取得
2. `target_achievement('2025-03')`で未達リージョンを特定
3. 未達リージョンに対して`product_profitability`で深掘り
4. 結果を統合して分析コメントを生成

一つの自然言語の質問から、適切な関数を適切な引数で複数回呼び出し、結果を統合して回答する。これがMCPサーバーとしてUC関数を公開する実用的な価値です。

# UC関数のCOMMENTを書くコツ

アシスタントがツールを正しく選択・利用できるかは、関数のCOMMENTの書き方に大きく依存します。実際に試して効果があったポイントをまとめます。

- **何を計算するかだけでなく、どういうルールで計算するかを書く**: 「売上を返します」ではなく「返品・キャンセル除外、割引後、カテゴリ別税率適用の正味売上を返します」
- **引数のCOMMENTに具体的な値の例を入れる**: `COMMENT '集計開始日(YYYY-MM-DD形式)'`のようにフォーマットを明示すると、アシスタントが自然言語から正しく変換できる
- **ALLのような特別な値がある場合は明記する**: `COMMENT '全リージョンを集計する場合は ALL を指定'`

# まとめ

UC関数をMCPサーバーとして公開する利点は、ビジネスロジックのカプセル化とガバナンスの両立にあります。

関数内部で対象テーブルや計算ルール(返品除外、税率適用など)を固定しているため、ユーザーは期間やリージョンといったフィルタ条件を自然言語で指定するだけで、正しいロジックに基づいた結果を得られます。そしてUnity Catalogに乗っているからこそ、ACL・リネージ・監査ログによるガバナンスが効きます。

ただし、UC関数はアシスタントが接続できるMCPサーバーの一つに過ぎません。Genieスペース(構造化データへの自然言語クエリ)、Vector Search(非構造化データの検索)、外部MCPサーバー(Confluenceなどのドキュメントシステム)と組み合わせることで、Assistantはワークスペース上の「何でも聞ける窓口」になります。

データチームがUC関数でロジックを整備し、Genieスペースで探索的分析を可能にし、Vector Searchでナレッジベースを構築する。ユーザーはどのバックエンドが使われているかを意識せず、アシスタントに自然言語で質問するだけで適切な回答を得られる。これが、アシスタントのMCP連携が目指す姿です。

# 補足: アシスタント + MCP と Genie の違い

DatabricksアシスタントにMCP経由でGenieスペースやUC関数を接続すると、アシスタント上でGenie的な自然言語データクエリが可能になります。「それならGenieでよくない?」という疑問が出てくるので、両者の位置づけを整理します。

## アシスタントは「ワークスペースの統合インターフェース」

ここまでの内容を読むと「ノートブック上でUC関数を自然言語で呼べて便利」という印象を受けるかもしれません。しかし、アシスタントのMCP連携の本質はそこではありません。

Databricksアシスタントはノートブック上だけでなく、**ワークスペースにアクセスできるすべてのユーザー**が利用できるAIアシスタントです。MCP連携によって、アシスタントは裏側で適切なツールを自律的に使い分けて回答を返します。

- 「先月の売上教えて」→ GenieスペースがSQLを生成・実行
- 「このエラーの対処法は?」→ Vector Searchが社内ドキュメントを検索
- 「デプロイ前チェックして」→ UC関数が定型処理を実行
- 「Confluenceの設計ドキュメントを確認して」→ 外部MCPサーバーがドキュメントを取得

ユーザーはどのMCPサーバーが呼ばれているかを意識する必要はありません。自然言語で質問するだけで、アシスタントが適切なバックエンドを選択します。

## Genieとの違い

Genieは**キュレーションされたText-to-SQL体験**に特化しています。ドメインエキスパートがデータセット、サンプルクエリ、テキストガイドラインでスペースを設定することで、ビジネスユーザー向けに精度の高い自然言語クエリを提供します。ダッシュボードからコンパニオンGenieスペースが自動作成される仕組みもあり、セルフサービス分析の入口として設計されています。

一方、アシスタント + MCPは**複数のバックエンドを統合するインターフェース**です。Genieスペースもその一つとしてMCPサーバー経由で組み込めますが、それだけに閉じません。

| 観点 | Genie | アシスタント + MCP |
|------|-------|-----------------|
| 設計思想 | 特定データセットへのText-to-SQL特化 | 複数ツールを統合する汎用AIインターフェース |
| データアクセス | 構造化データ(SQL) | 構造化 + 非構造化 + 外部ツール |
| ツール選択 | 不要(SQL生成に特化) | LLMが自律的に判断 |
| キュレーション | サンプルクエリ・ガイドラインで精度向上 | 各MCPサーバー側で管理 |
| 主な利用場面 | ビジネスユーザーのセルフサービス分析 | ワークスペース上でのあらゆる作業支援 |

## 本記事のUC関数はMCPサーバーの一例

本記事ではUC関数をMCPサーバーとしてアシスタントに接続するデモを紹介しましたが、これはアシスタントが統合できるバックエンドの一例です。実運用では、Genieスペース、Vector Search、UC関数、外部MCPサーバーを組み合わせて接続することで、アシスタントがワークスペース上の「何でも聞ける窓口」として機能するようになります。

# 参考リンク

- [Databricks Assistant を MCP サーバーに接続する](https://docs.databricks.com/aws/ja/assistant/mcp)
- [Databricks のモデル コンテキスト プロトコル(MCP)](https://docs.databricks.com/aws/ja/generative-ai/mcp/)
- [Databricks Assistantのエージェントモード](https://docs.databricks.com/aws/ja/notebooks/use-databricks-assistant#assistant-modes)
- [Unity Catalog関数の作成](https://docs.databricks.com/aws/ja/generative-ai/agent-framework/create-custom-tool)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

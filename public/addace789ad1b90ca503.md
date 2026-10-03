---
title: 【実践】Lakeflow Designer で始めるノーコードETL — 日本語の指示だけでパイプラインを作る
tags:
  - Databricks
  - LakeFlowDesigner
  - ETL
  - ノーコード
  - 生成AI
private: false
updated_at: '2026-10-02T17:34:12+09:00'
id: addace789ad1b90ca503
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Databricks の [**Lakeflow Designer**](https://docs.databricks.com/aws/ja/designer/) を、実際に手を動かして一通り触ってみた記録です。カタログのテーブルを入力に、**ソース → フィルタ → 結合 → 集計 → 出力** のパイプラインを1本組み、同じことを **日本語の指示だけ（Genie Code）** でも作らせます。

:::note info
この記事は日本語UIで実機ウォークスルーした結果に基づきます。画面の文言・挙動は執筆時点（2026年10月）のもので、UI は今後更新され得ます。
:::

# Lakeflow Designer とは

- **ノーコード／AIネイティブなビジュアル ETL**。演算子（オペレーター）をキャンバスに置き、線でつないでデータ加工パイプラインを作る。
- 出力は **Unity Catalog のテーブル／マテリアライズドビュー／ファイル**。作ったパイプラインはそのまま **Lakeflow Jobs** でスケジュール実行できる（＝試作から本番まで地続き）。
- **Genie Code**：チャットに日本語で指示すると、複数の演算子を自動で配置・設定してくれる。生成後も各ノードの中身を開いて確認・修正できるので「ブラックボックス」にならない。
- 公式ドキュメント：[Lakeflow Designer の組み込み演算子](https://docs.databricks.com/aws/ja/designer/built-in-operators)（日本語）。

対象読者：Unity Catalog が有効な Databricks ワークスペースを使える人。Serverless 推奨。

# Part 0. 準備：スキーマとサンプルデータ

作業用スキーマ（例 `designer_handson`）を作り、EC/小売を題材にサンプルデータを生成します。ノートブックで以下を実行（`<カタログ>` は自分の環境値に読み替え）。

```python
from pyspark.sql import functions as F

CATALOG = "<カタログ>"
SCHEMA  = "designer_handson"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")

# customers（ディメンション：2,000件）
regions   = ["北海道・東北","関東","中部","近畿","中国・四国","九州・沖縄"]
segments  = ["Basic","Standard","Premium"]
ages      = ["20代","30代","40代","50代","60代以上"]
(spark.range(1, 2001).withColumnRenamed("id","customer_id")
  .withColumn("customer_name", F.concat(F.lit("顧客"), F.col("customer_id")))
  .withColumn("segment", F.element_at(F.array(*[F.lit(x) for x in segments]), (F.rand(1)*3+1).cast("int")))
  .withColumn("region",  F.element_at(F.array(*[F.lit(x) for x in regions]),  (F.rand(2)*6+1).cast("int")))
  .withColumn("age_group",F.element_at(F.array(*[F.lit(x) for x in ages]),    (F.rand(3)*5+1).cast("int")))
  .write.mode("overwrite").saveAsTable("customers"))

# orders（ファクト：20,000件、直近約15ヶ月）
(spark.range(1, 20001).withColumnRenamed("id","order_id")
  .withColumn("customer_id",(F.rand(7)*2000+1).cast("int"))
  .withColumn("product_id", (F.rand(8)*200+1).cast("int"))
  .withColumn("order_date", F.expr("date_add(current_date(), -cast(rand(9)*450 as int))"))
  .withColumn("quantity",   (F.rand(10)*5+1).cast("int"))
  .withColumn("amount",     (F.rand(11)*18000+2000).cast("int"))
  .withColumn("channel",    F.when(F.rand(12)>0.5,"店舗").otherwise("オンライン"))
  .write.mode("overwrite").saveAsTable("orders"))

print([t.name for t in spark.catalog.listTables()])
```

**確認**：`orders`（20,000行）と `customers`（2,000行）が `<カタログ>.designer_handson` にできていること。Lakeflow Designer は「既存の UC テーブル」を入力にできます。

# Part 1. 画面を開く

左サイドバー「**＋ 新規**」→「**ビジュアルデータの準備**」で新しいキャンバスを開きます。中央の「始めましょう」の下にあるのが Genie Code の入力欄です（Part 6 で使います）。

![01_start_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/adb1d20a-daec-48e5-8b86-478bd798a31b.png)

画面構成は **左＝演算子パレット／中央＝キャンバス／下＝プレビュー**。基本の操作は「**演算子を置く → 線でつなぐ → 設定して適用 → プレビューで確認**」の反復です。

:::note info
**接続のコツ**：ノードを選択した状態で左パレットの演算子をクリックすると、**選択中ノードの出力に自動で接続**されて配置されます。ドラッグ＆ドロップより確実です。
:::

# Part 2. ソース：テーブルを取り込む

ソース演算子を置き、ダブルクリック →「**既存を参照**」→ アセットセレクターで `orders` を選びます。

![m1_source_orders_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5f47c482-bc1f-473a-9b4b-39f750cc709b.png)

:::note info
アセットセレクターは既定で「すべて」。同名テーブルが多数ヒットしてカタログが区別しづらいときは「**自分用**」フィルタに切り替えると、自分のカタログと「最近使用したアイテム（フルパス付き）」が上位に出ます。選んだらプレビューの列・所有者で正しいテーブルか確認しましょう。
:::

同じ要領で `customers` も追加しておきます（Part 4 の結合で使います）。

# Part 3. フィルタ：対象期間に絞る

`orders` を選択 → パレットの「**フィルタ**」をクリック（自動接続）。ダブルクリックして条件を設定します。

- 列 `order_date` ／ 演算子「**後**」／ 値＝直近12ヶ月の開始日（例 `2025/10/01`）→ 適用。

![Screenshot 2026-10-02 at 14.49.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/26a63738-d09c-4071-aa86-dc3a93eea254.png)

出力（True）の件数が減ります（この例では 1,000 → 816 行）。フィルタは **True / False の2系統**に行を振り分けます（除外行も後段で使えます）。

:::note warn
**日本語UIの癖（執筆時点）**：演算子に「後」(After) を選ぶと、適用後の条件チップは「`order_date 超 2025年10月1日`」と **「超」** で表示されます。意味は「`order_date` が … **より後**」です。表示の訳が揺れているだけなので、操作は「後」を選べば OK。
:::

# Part 4. 結合：顧客マスタを付与する

`orders`（フィルタ後）を選択 →「**結合**」をクリック（左入力に自動接続）。右入力は、先ほど置いた `customers` を「**入力を結合**」の右ドロップダウンから選びます。

- 結合条件：左右とも `customer_id`（**列名が一致すると自動検出**され「列名で一致しました」と表示）。
- 結合タイプ：**Left join**（＝ 左＝注文の全行に顧客属性を付与）。

![m3_join_types_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a6439e56-7249-423f-acf4-f1bd4f7de955.png)
![m4_join_leftjoin_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4c3b8b64-58d8-439a-b233-94e0b1e2aa87.png)

`customer_name / segment / region / age_group` の列が増えます。

:::note warn
**結合タイプの表示について**：選択肢は「**分割結合 / Full join / Inner join / Left Join / Right join**」の5種です。
- 「**分割結合（Split join）**」は誤訳ではなく**実在の既定タイプ**で、「一致した行（内部結合）／左のみ／右のみ」の **3つの出力**を生成します。
- 気になるのは「**5種のうち分割結合だけ日本語で、残り4つ（Full/Inner/Left/Right join）は英語のまま**」という点。訳が中途半端なだけで機能は問題ありません。
- 全行に属性を付けたい今回は **Left join** を選びます。
:::

# Part 5. 集計：顧客別に合計する

「結合」を選択 →「**集計**」をクリック。

- **集計を追加**：列 `amount` ／ 関数 `SUM` ／ 表示名 `total_amount`
- **グループ化を追加**：`customer_id`（必要に応じて `segment` `region` も）

![集計](screenshots/m5_aggregate_ja.png)

行が顧客数程度に集約されます（この例では 816 → 681 行）。

# Part 6. 出力：テーブルとして保存する

「集計」を選択 →「**出力**」をクリック → 出力タイプ「**テーブル**」。

- モード「**作成または置換モード**」（＝上書き）
- 場所：`<カタログ>` → `designer_handson`
- テーブル名：`customer_360_summary` → 適用 →「**実行**」

![m6_output_config_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d9ac05f2-09af-4400-a3a1-f5218e11a38c.png)
![m7_output_run_success_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fda42f51-9082-4b31-bd4d-c04fb77cd468.png)

「✓ 成功 上書き」と表示され、出力ペインには書き込み結果（`num_affected_rows` / `num_inserted_rows`）が出ます（Output 演算子は行ではなく書き込み統計を返すため「行が返されませんでした」と出るのは正常です）。Catalog Explorer に `customer_360_summary`（MANAGED テーブル）ができていることを確認できます。

ここまでで“いつもの処理”が1本通りました。

:::note info
本番運用：上部「**スケジュール**」から頻度・時刻・タイムゾーンを指定すれば Lakeflow Jobs で定期実行できます（コードに書き直さず、試作がそのまま本番に）。
:::

# Part 7. 日本語でAI生成する（Genie Code）

同じことを、**日本語の指示だけ**で作らせてみます。新規「ビジュアルデータの準備」を開き、入力欄にプロンプトを入力。

:::note info
例：`<カタログ>.designer_handson.orders と <カタログ>.designer_handson.customers を使って、顧客別の売上合計（amount の合計）を多い順に並べて出して。`
:::

![02_prompt_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6990c887-7d67-450c-b92f-949cd910237e.png)

送信すると数十秒で**複数の演算子が自動配置**され、プレビューに結果が出ます。生成されたのは **Orders／Customers →（結合）→（顧客別売上合計の集計）→（売上降順の並べ替え）**。

![03_generated_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fb604db9-869e-48fe-b475-5cdf27114136.png)

内容を確認して「**すべて承認**」。各ノードをクリックすれば設定を確認できます＝**ブラックボックスにならない**のが Designer の強み。

![04_approved_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1d210375-76ad-4a24-8ae6-ca4b54a1cd89.png)

生成されたノードの中身も日本語UIで確認できます。

- 結合ノード：結合条件 `customer_id ↔ customer_id`、Genie は Inner join を選択

   ![05_join_config_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d5a0971f-ee05-4ffb-8f52-34a44bc07821.png)

- 集計ノード：`amount` の合計を `customer_name` 単位で

   ![06_aggregate_config_ja.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/84682c20-e09e-4532-b8c1-10a22c92dd34.png)

追加指示も日本語でそのまま足せます：「上位20顧客だけ」「金額を千円単位に」など。

**使い分け**：Part 2〜6 の手組みで演算子の意味を理解し、Part 7 の日本語生成で高速化。両方できると「理解しながら速く試行錯誤」できます。

# オペレーター早見表（執筆時点・docs準拠）

出典：[Lakeflow Designer の組み込み演算子](https://docs.databricks.com/aws/ja/designer/built-in-operators)

- **ソース／出力**：Source（取り込み）、Enter Data（手入力表）、Output（テーブル/MV/ファイルへ出力）
- **変換**：Aggregate（集計）、Combine（和・積・差の集合演算）、Unique（重複除去）、Filter（条件分岐）、Guardrail（データ検証）、Join（結合）、Limit（行数制限）、Pivot（行列入替）、Sort（並べ替え）、SQL（任意SQL）、Select（列の選択・改名・並替）、Prepare（列のクリーニング・派生をチェーン）、Python（PySpark）
- **AI関数**：`ai_analyze_sentiment`（感情分析）、`ai_classify`（分類）、`ai_extract`（構造化抽出）、`ai_fix_grammar`、`ai_forecast`（時系列予測）、`ai_gen`、`ai_mask`（PIIマスク）、`ai_parse_document`（文書解析）、`ai_prep_search`（RAG前処理）、`ai_query`、`ai_similarity`、`ai_summarize`（要約）、`ai_translate`（翻訳）
- **オーガナイズ**：Note（注釈）、Group（グループ化）、Visualization（可視化）

:::note info
本記事では基本の変換とソース/出力を手で触りました。**AI関数（forecast / extract / parse_document 等）・Guardrail・Combine・Pivot** は実務で効く反面、既存記事で薄い領域なので、別記事で手を動かして掘り下げる予定です。
:::

# まとめ

- Lakeflow Designer は「演算子を置いて線でつなぐ」だけで、**抽出・結合・集計・出力**をノーコードで組めます。
- 出力は Unity Catalog 管理。リネージュや権限もそのまま効き、Lakeflow Jobs で本番化も地続きです。
- **Genie Code** で日本語生成しても、各ノードを開けば中身が見えるので安心して使えます。
- 日本語UIには訳の揺れ（Filterの「超」、結合タイプの英日混在）がまだありますが、意味を押さえれば実務に支障はありません（改善は要望中）。

手を動かすと「どの演算子が何をするか」が一気に腹落ちします。まずは本記事の1本を、自分のテーブルで通してみてください。




### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

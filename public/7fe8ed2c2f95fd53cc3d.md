---
title: Delta Live Tablesクイックスタート
tags:
  - Databricks
  - Databricksクイックスタートガイド
  - DeltaLiveTables
private: false
updated_at: '2023-01-02T10:59:19+09:00'
id: 7fe8ed2c2f95fd53cc3d
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Delta Live Tables quickstart \| Databricks on AWS](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-quickstart.html) [2021/5/25時点]の翻訳です。

> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

> **プレビュー**
この機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。アクセスする際にはDatabricks担当者にお問い合わせください。

3分紹介動画です。

<iframe width="560" height="315" src="https://www.youtube.com/embed/_7HSZsYpiek" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Delta Live Tablesは、信頼性が高く、維持が容易でテスト可能なデータ処理パイプラインを構築するためのフレームワークです。データに対する変換処理を定義すると、Delta Live Tablesはタスクのオーケストレーション、クラスター管理、モニタリング、データ品質、エラー処理を行います。

一連の分割されたSparkのタスクを用いてデータパイプラインを定義する代わりに、Delta Live Tablesはそれぞれの処理ステップであなたが定義したターゲットスキーマに基づき、どのようにデータが変換されるのかを管理します。Delta Live Tablesの*expectation(期待)*を活用してデータ品質を維持することもできます。エクスペクテーションによって、期待されるデータ品質を定義し、エクスペクテーションに沿わないデータをどのように取り扱うのかを定義することができます。

Databricksノートブックを使用して簡単にDelta Live Tablesのパイプラインを作成することができます。本記事ではDelta Live TablesパイプラインとWikipediaクリックストリームデータを用いてデモをお見せします。Wikipediaクリックストリームデータを用いて以下のことを行います。

- 生のJSONクリックストリームデータをテーブルに読み込みます。
- 生データテーブルからレコードを読み込み、Delta Live Tablesの[エクスペクテーション](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-user-guide.html#expectations-overview)を用いて、クレンジングされたデータを格納する新たなテーブルを作成します。
- Delta Live Tablesのクエリーを行い、クレンジングデータテーブルのレコードから新たなデータセットを作成します。

このクイックスタートでは、以下のことを実施します。

1. 新規ノートブックを作成し、パイプラインを実装するためのコードを追加します。
1. ノートブックを用いて新たなパイプラインジョブを作成します。
1. パイプラインジョブの[アップデート](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-user-guide.html#dlt-concepts-updates)をスタートします。
1. パイプラインジョブの結果を参照します。

# ノートブックの作成

Delta Live Tablesを実行するには、[サンプルノートブック](#サンプルノートブック)を利用するか、新たなノートブックを作成します。

1. Databricksランディングページに移動し、**Create Blank Notebook**を選択します。
1. **Create Notebook**ダイアログで、ノートブック名を指定し、**Default Language**から**Python**か**SQL**を選択します。**Cluster**はデフォルト値のままで構いません。Delta Live Tablesランタイムはパイプラインを実行する前にクラスターを作成します。
1. **Create**をクリックします。
1. 好きな言語のコードサンプルをコピーし、新たなノートブックに貼り付けます。サンプルコードは一つのセル、あるいは複数のセルに貼り付けることができます。

> **注意**
Jobのユーザーインタフェースからパイプラインを実行します。ノートブック上で![](https://docs.databricks.com/_images/run-cell.png)をクリックするとエラーとなります。

## コードサンプル

**Python**

```python
from pyspark.sql.functions import *
from pyspark.sql.types import *


json_path = "/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json"
@create_table(
  comment="The raw wikipedia click stream dataset, ingested from /databricks-datasets.",
  table_properties={
    "quality": "bronze"
  }
)
def clickstream_raw():
  return (
    spark.read.json(json_path)
  )


@create_table(
  comment="Wikipedia clickstream dataset with cleaned-up datatypes / column names and quality expectations.",
  table_properties={
    "quality": "silver"
  }
)
@expect("valid_current_page", "current_page_id IS NOT NULL AND current_page_title IS NOT NULL")
@expect_or_fail("valid_count", "click_count > 0")
def clickstream_clean():
  return (
    read("clickstream_raw")
      .withColumn("current_page_id", expr("CAST(curr_id AS INT)"))
      .withColumn("click_count", expr("CAST(n AS INT)"))
      .withColumn("previous_page_id", expr("CAST(prev_id AS INT)"))
      .withColumnRenamed("curr_title", "current_page_title")
      .withColumnRenamed("prev_title", "previous_page_title")
      .select("current_page_id", "current_page_title", "click_count", "previous_page_id", "previous_page_title")
  )


@create_table(
  comment="A table of the most common pages that link to the Apache Spark page.",
  table_properties={
    "quality": "gold"
  }
)
def top_spark_referrers():
  return (
    read("clickstream_clean")
      .filter(expr("current_page_title == 'Apache_Spark'"))
      .withColumnRenamed("previous_page_title", "referrer")
      .sort(desc("click_count"))
      .select("referrer", "click_count")
      .limit(10)
  )


@create_table(
  comment="A list of the top 50 pages by number of clicks.",
  table_properties={
    "quality": "gold"
  }
)
def top_pages():
  return (
    read("clickstream_clean")
      .groupBy("current_page_title")
      .agg(sum("click_count").alias("total_clicks"))
      .sort(desc("total_clicks"))
      .limit(50)
  )
```

**SQL**

```sql
CREATE LIVE TABLE clickstream_raw
COMMENT "The raw wikipedia click stream dataset, ingested from /databricks-datasets."
TBLPROPERTIES ("quality" = "bronze")
AS SELECT * FROM json.`/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json`

CREATE LIVE TABLE clickstream_clean(
  CONSTRAINT valid_current_page EXPECT (current_page_id IS NOT NULL and current_page_title IS NOT NULL),
  CONSTRAINT valid_count EXPECT (click_count > 0) ON VIOLATION FAIL UPDATE
)
COMMENT "Wikipedia clickstream dataset with cleaned-up datatypes / column names and quality expectations."
TBLPROPERTIES ("quality" = "silver")
AS SELECT
  CAST (curr_id AS INT) AS current_page_id,
  curr_title AS current_page_title,
  CAST(n AS INT) AS click_count,
  CAST (prev_id AS INT) AS previous_page_id,
  prev_title AS previous_page_title
FROM live.clickstream_raw

CREATE LIVE TABLE top_spark_referers
COMMENT "A table of the most common pages that link to the Apache Spark page."
TBLPROPERTIES ("quality" = "gold")
AS SELECT
  previous_page_title as referrer,
  click_count
FROM live.clickstream_clean
WHERE current_page_title = 'Apache_Spark'
ORDER BY click_count DESC
LIMIT 10

CREATE LIVE TABLE top_pages
COMMENT "A list of the top 50 pages by number of clicks."
TBLPROPERTIES ("quality" = "gold")
AS SELECT
  current_page_title,
  SUM(click_count) as total_clicks
FROM live.clickstream_clean
GROUP BY current_page_title
ORDER BY 2 DESC
LIMIT 50
```

# パイプラインの作成

Delta Live Tablesノートブックを用いて新たにパイプラインを作成します。

1. サイドバーの![](https://docs.databricks.com/_images/jobs-icon.png)をクリックし、**Pipelines**タブをクリック、**Create Pipeline**をクリックします。
1. パイプライン名を指定し、![](https://docs.databricks.com/_images/file-picker.png)をクリックしてノートブックを選択します。
1. 任意で、パイプラインの出力データのストレージを指定します。**Storage Location**を空にした場合、システムはデフォルトの位置を使用します。
1. **Pipeline Mode**に対して**Triggered**を選択します。
1. **Create**を作成します。

![](https://docs.databricks.com/_images/dlt-create-notebook-pipeline.png)

**Create**をクリック後、**Pipeline Details**ページが表示されます。**Pipelines**タブでパイプライン名をクリックすることでパイプラインの詳細を表示することができます。

# パイプラインのスタート

新たなパイプラインのアップデートを実行するには、トップパネルの![](https://docs.databricks.com/_images/dlt-start-button.png)ボタンをクリックします。パイプラインの開始を示すメッセージが表示されます。
![](https://docs.databricks.com/_images/dlt-notebook-pipeline-successful-start.png)

アップデートのスタートが成功した後、Delta Live Tablesシステムは以下のことを行います。

1. Delta Live Tablesで作成されたクラスター設定を用いてクラスターを起動します。カスタムの[クラスター設定](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-configuration.html#cluster-config)を行うことも可能です。
1. 存在しないテーブルを作成し、既存テーブルと整合性を持つスキーマを設定します。
1. 最新のデータを用いてテーブルをアップデートします。
1. アップデートが完了したらクラスターをシャットダウンします。

**Pipeline Details**ページの下部にあるイベントログでアップデートの進捗状況を追跡できます。
![](https://docs.databricks.com/_images/dlt-wikipedia-log.png)

# 結果の参照

パイプライン処理の詳細を確認するためにDelta Live Tablesのユーザーインタフェースを利用できます。これには、パイプライングラフとスキーマ、処理されたレコード数、検証に失敗したレコード数などの処理詳細が含まれます。

## パイプライングラフの参照

パイプラインの処理グラフを参照するには、**Graph**タブをクリックします。グラフパネルの右上にある![](https://docs.databricks.com/_images/dlt-graph-buttons.png)ボタンやマウスで表示を調整できます。
![](https://docs.databricks.com/_images/dlt-wikipedia-graph.png)

## データセット情報の参照

データセットのスキーマ情報を参照するにはデータセットをクリックします。
![](https://docs.databricks.com/_images/dlt-example-schema.png)

## 処理詳細の参照

処理レコード数、データ品質メトリクスなどの処理詳細を参照するには、イベントログのエントリーを選択し、**JSON**タブをクリックします。
![](https://docs.databricks.com/_images/dlt-event-log-detail.png)

# パイプライン設定の参照

パイプラインで生成された設定を参照するには、**Settings**をクリックします。パイプライン設定を変更するには**Edit Settings**ボタンをクリックします。設定の詳細に関しては、[Delta Live Tables configuration](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-configuration.html)を参照ください。

#　データセットの公開

Databricksメタストアにテーブルを公開することで、パイプラインの出力結果にクエリーを行うことが可能になります。

1. **Edit Settings**ボタンをクリックします。
1. テーブルに対するデータベースを設定するために*target setting*を追加します。
![](https://docs.databricks.com/_images/dlt-settings-publish.png)
1. **Save**をクリックします。
1. パイプラインの新たなアップデートを実行するには、![](https://docs.databricks.com/_images/dlt-start-button.png)をクリックします。

アップデートが終了すると、[データベースとテーブルを参照](https://docs.databricks.com/data/tables.html#view-databases-and-tables)できるようになり、データに対してクエリーを行えるようになります。加えて、下流のアプリケーションで活用することもできます。
![](https://docs.databricks.com/_images/dlt-wikipedia-query.png)

# サンプルノートブック

Delta Live Tablesのパイプラインを実装したPythonとSQLのサンプルノートブックとなります。以下の処理を行います。

- 生のJSONクリックストリームデータをテーブルに読み込みます。
- 生データテーブルからレコードを読み込み、Delta Live Tablesの[エクスペクテーション](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-user-guide.html#expectations-overview)を用いて、クレンジングされたデータを格納する新たなテーブルを作成します。
- Delta Live Tablesのクエリーを行い、クレンジングデータテーブルのレコードから新たなデータセットを作成します。

## Delta Live Tables Pythonノートブック

[Delta Live Tables quickstart \(Python\) \- Databricks](https://github.com/taka-yayoi/public_repo/blob/main/delta_live_tables/Delta%20Live%20Tables%20Quickstart%20(Python).html)

## Delta Live Tables SQLノートブック

[Delta Live Tables quickstart \(SQL\) \- Databricks](https://github.com/taka-yayoi/public_repo/blob/main/delta_live_tables/Delta%20Live%20Tables%20Quickstart%20(SQL).html)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

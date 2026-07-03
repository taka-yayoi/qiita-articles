---
title: Databricksアシスタントを日本語で試してオッサン再びびっくり
tags:
  - Databricks
  - LLM
private: false
updated_at: '2023-08-03T10:39:11+09:00'
id: db3e9d976f9f7dbec86e
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの続きです。

https://qiita.com/taka_yayoi/items/810bcdf589a33ee8c828

最後の部分で日本語を試しましたが、本格的に日本語でどこまでいけるのか試してみます。

こちらのサンプルタスクを日本語でトライしてみます。

https://docs.databricks.com/ja/notebooks/notebook-assistant-examples.html

:::note
マニュアルが日本語化されましたが、出来立てほやほやなので質に関しては生暖かく見守ってください。
:::

# コードサンプルの生成

セルに以下のコードを入力します。セルが選択されている状態で、画面左の学帽マークをクリックして、アシスタントを開きます。

```py
import pandas as pd

# Read the sample NYC Taxi Trips dataset and load it into a DataFrame
df = spark.read.table('samples.nyctaxi.trips')
```

プロンプトを入力します。

> pysparkデータフレームをpandasデータフレームに変換し、fare_amountカラムに基づいてdfから最も高価なtripの上位10件を選択するpandasコードを生成してください

![Screenshot 2023-08-03 at 10.21.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3061ee37-13a3-3a23-efeb-9aa61c797552.png)

**新しいセルに挿入**アイコンをクリックすると、新規セルにコードが挿入されます。
![Screenshot 2023-08-03 at 10.22.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9e806586-6fb8-68cd-d487-9f4f6de1bd55.png)
![Screenshot 2023-08-03 at 10.22.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/07a90253-f2ab-285d-22bf-ec30fccff356.png)

セルを実行すると期待した結果を得ることができます。すごい。
![Screenshot 2023-08-03 at 10.23.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d26c82bb-0bde-70b8-5558-4f1f621af526.png)

# データフレームリーダーの作成

```py
display(dbutils.fs.ls("dbfs:/databricks-datasets/bikeSharing/data-001/"))
```

**プロンプト**

> bikeSharingデータセットのday.csvファイルを読み込むコードを生成してください

**レスポンス**

> 以下のコードによって、bikeSharingデータセットのday.csvファイルを読み込むことができます。

```python
bikeSharingDF = sqlContext.read.format('csv')\
  .option("header", "true")\
  .option("inferSchema", "true")\
  .load("dbfs:/databricks-datasets/bikeSharing/data-001/day.csv")
```
> これは、day.csvファイルを読み取り、結果のDataFrameをbikeSharingDFに割り当てます。必要に応じて、ファイルパスを変更することができます。

これも期待通りに動作します。
![Screenshot 2023-08-03 at 10.25.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cd5523fd-19d9-9ff8-c626-4a46b143355e.png)

# コードの変換

```py
import pandas as pd

# Convert Spark DataFrame to Pandas DataFrame
pdf = df.toPandas()

# Select the 10 most expensive trips based on the fare_amount column
most_expensive_trips = pdf.nlargest(10, 'fare_amount')

# Show the result
most_expensive_trips
```

**プロンプト**

> このコードをPySparkに変換してください

**レスポンス**

> PandasのコードをPySparkに変換すると以下のようになります。

```python
# Select the 10 most expensive trips based on the fare_amount column
from pyspark.sql.functions import desc

most_expensive_trips = df.orderBy(desc("fare_amount")).limit(10)

# Show the result
most_expensive_trips.show()
```

> ここでは、desc()関数を使用して、カラムfare_amountを降順に並べ替えます。その後、limit(10)関数を使用して、上位10件のレコードを選択します。最後に、show()関数を使用して、結果を表示します。

これも動作します。もう、当たり前の世界だ。

```
+--------------------+---------------------+-------------+-----------+----------+-----------+
|tpep_pickup_datetime|tpep_dropoff_datetime|trip_distance|fare_amount|pickup_zip|dropoff_zip|
+--------------------+---------------------+-------------+-----------+----------+-----------+
| 2016-02-12 20:55:19|  2016-02-12 21:52:38|        20.85|      275.0|     10013|       7008|
| 2016-02-29 12:16:16|  2016-02-29 12:16:53|          0.0|      260.0|      8876|       8876|
| 2016-01-30 22:28:42|  2016-01-30 22:30:14|          0.0|      188.0|      7974|       7974|
| 2016-02-17 22:23:14|  2016-02-17 23:06:15|        25.46|      130.0|     10103|       7901|
| 2016-01-28 17:36:17|  2016-01-28 18:27:48|         21.3|      115.0|     10017|      11042|
| 2016-01-04 18:58:23|  2016-01-04 18:58:45|          0.0|      105.0|      7114|       7114|
| 2016-01-16 18:09:15|  2016-01-16 18:09:23|          0.0|      105.0|      7310|       7310|
| 2016-02-22 21:17:27|  2016-02-22 22:00:58|         30.6|       95.0|     11371|       7114|
| 2016-01-04 09:19:53|  2016-01-04 09:19:57|          5.2|       95.0|     10009|      10009|
| 2016-02-24 22:19:55|  2016-02-24 22:36:02|        12.49|       95.0|     11369|      10803|
+--------------------+---------------------+-------------+-----------+----------+-----------+
```

# オートコンプリート

セルにコメントだけ入力します。挿入される場所にカーソルを移動します。

```py
# 文字列を反転させるコードを書いてください
```

Macの場合、Option+Shift+Spaceを押します。

灰色で提案が表示されます。数秒のラグがあるのでお待ちください。
![Screenshot 2023-08-03 at 10.31.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6ead7669-96ef-80fb-c248-05a5519f9365.png)

受け入れるにはTabを押します。変数を定義して実行します。
![Screenshot 2023-08-03 at 10.31.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/eda9f972-da98-f871-bea9-b3dd3e89aa2b.png)

# コードの説明

```py
import pyspark.sql.functions as F

fare_by_route = df.groupBy(
'pickup_zip', 'dropoff_zip'
).agg(
    F.sum('fare_amount').alias('total_fare'),
    F.count('fare_amount').alias('num_trips')
).sort(F.col('num_trips').desc())

display(fare_by_route)
```

**プロンプト**

> このコードが何をするのかを説明して下さい

**レスポンス**

> このコードは、タクシーの料金データを含むPySpark DataFrame df を元に、出発地の郵便番号pickup_zipと目的地の郵便番号dropoff_zipに基づいて、total_fareとnum_tripsをグループ化し、num_tripsを降順で並べ替え、結果を表示します。
>
> 具体的には、DataFrameの groupBy() メソッドを使用して、pickup_zipとdropoff_zipをキーにしてグループ化します。agg() メソッドを使用して、各グループ内の fare_amount カラムの合計値を total_fare に集計し、 同じく fare_amount カラム内のトリップの数を num_trips に集計します。最後に、 sort() メソッドを使用して、num_tripsを昇順で並べ替えます。結果は fare_by_route という変数に保存され、 display() 関数を使って表示されます。

# ドキュメント検索

**プロンプト**

> Apache Sparkではどのような時にrepartition()とcoalesce()を使うべきですか

**レスポンス**

> repartition()とcoalesce()は、Apache Sparkでパフォーマンスを調整するために使用できる2つのオペレーションです。どちらもデータフレームのパーティショニング（データの物理的な分割）に影響を与え、データのシャッフルが発生します。しかし、2つのオペレーションは異なる要件によって異なる方法で使用されます。
> 
> - repartition(): パーティショニング数を増やすために使用され、より高速な並列処理を可能にします。生成されるパーティション数を指定することができます。repartition()は、より大きなパーティション数により大量のシャッフルが発生するため、小さなパーティション数に比べて高コストとなります。
> 
> - coalesce(): パーティショニング数を減らすために使用され、シャッフルを最小限に抑えます。coalesce()は、必ずしも同じパーティション数を指定する必要がなく、データのサイズに基づいて自動的に最適な分割を作成することができます。
> 
> 例えば、以下のような場合に、repartition()またはcoalesce()を使用することができます。
> 
> 1. データサイズが増えてシャッフルが発生している場合、データサイズが一定の場合はrepartition()、データサイズが可変の場合はcoalesce()を使用します。
> 1. パイプライン中でのシャッフルの発生を減らすために、パーティション数を制御する場合、coalesce()を使用します。
> 1. パイプラインの途中で正確なパーティション数を指定したい場合, repartition()を使用します。
>
> 注意事項として、データの復元や再配分に必要な時間とコストが両方の操作で考慮する必要があります。常に最適なパーティション数を選ぶことが重要であるため、データに応じて異なるオプションを試してみ���ことが重要です。

うーん、やはりスゴイ。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

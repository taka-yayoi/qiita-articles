---
title: Lakeflow Spark宣言型パイプラインのチュートリアル
tags:
  - Databricks
  - データエンジニアリング
  - LakeFlow
private: false
updated_at: '2025-10-28T15:28:48+09:00'
id: bb5ccb3fa1dae1b8915e
organization_url_name: databricks
slide: false
ignorePublish: false
---
気づいたら色々機能が更新されていました。

https://docs.databricks.com/aws/ja/getting-started/data-pipeline-get-started

そして、製品ページはSpark Declarative Pipelinesに、今後はSpark宣言型パイプラインと呼ばせていただきます。

https://www.databricks.com/jp/product/data-engineering/spark-declarative-pipelines

# Lakeflow Spark宣言型パイプラインとは

https://docs.databricks.com/aws/ja/ldp/

Lakeflow Spark宣言型パイプラインは、DatabricksがSQLとPythonで提供するバッチおよびストリーミングデータパイプラインの構築フレームワークです。従来のデータパイプライン開発で必要だった複雑なオーケストレーション、エラーハンドリング、インクリメンタル処理のコードを大幅に削減し、宣言的なアプローチでデータ変換を定義できます。クラウドストレージやメッセージバスからのデータ取り込み、変更データキャプチャ(CDC)、リアルタイムストリーム処理などの用途に対応し、データエンジニアだけでなくSQLアナリストも利用可能です。

Lakeflow Spark宣言型パイプラインは、データパイプラインの開発と実行を簡素化する宣言型フレームワークです。パフォーマンス最適化されたDatabricks Runtime上で動作し、Apache SparkのデータフレームAPIと構造化ストリーミングを基盤としています。

Lakeflow Spark宣言型パイプラインは以下の概念で構成されています。

| 要素 | 説明 | 種類 |
|------|------|------|
| **フロー(Flow)** | データ処理の基本単位。ソースからデータを読み取り、処理ロジックを適用してターゲットに書き込む | ストリーミング/バッチ |
| **ストリーミングテーブル** | ストリーミングデータを格納するUnity Catalogマネージドテーブル。追加フローやAuto CDCフローを受け付ける | ストリーミング |
| **マテリアライズドビュー** | バッチ処理結果を格納するUnity Catalogマネージドテーブル。インクリメンタル処理をサポート | バッチ |
| **シンク(Sink)** | ストリーミングデータの出力先。Deltaテーブル、Kafka、EventHubsなどに対応 | ストリーミング |
| **パイプライン** | 上記の要素を組み合わせた開発・実行の単位。依存関係を自動分析し実行順序を最適化 | 統合 |

以下では、冒頭のチュートリアルをウォークスルーします。

# 事前準備

パイプラインのソースコードを保存するフォルダと、生成されるテーブル(マテリアライズドビューやストリーミングテーブル)を格納するカタログ、スキーマを準備しておきます。

![Screenshot 2025-10-28 at 14.39.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/58e28648-80dd-488f-9f7d-e2bd8e56800b.png)

# ステップ 1: パイプラインを作成する

**新規 > ETLパイプライン**を選択します。
![Screenshot 2025-10-28 at 14.38.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d673a2be-22a3-487a-9bf4-b1261a3b0d73.png)

パイプライン作成画面が開くので、適切な名前をつけます。
![Screenshot 2025-10-28 at 14.38.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0fa12423-e06c-4502-b09d-df9333facbeb.png)

上で準備したカタログとスキーマを選択します。
![Screenshot 2025-10-28 at 14.39.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ba394bc4-2cd3-4b07-bea2-7dab58ebbaa2.png)

**空のファイルで開始**をクリックすると、ソースコードを格納するフォルダを聞かれるので選択します。ファイルの種類は`Python`にします。
![Screenshot 2025-10-28 at 14.40.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/03e2311a-40d9-405f-99f0-0e9280e7d7ce.png)

すると、パイプラインエディタが表示されます。
![Screenshot 2025-10-28 at 14.40.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/de6f6bd8-67bb-4762-b6e1-b56aa8654f38.png)

# ステップ 2: パイプラインロジックを開発する

デフォルトで作成されているファイル`transformations/my_transformation.py`二以下のコードを記述します。ライブラリやデコレーターが`dp`に統一されていますね。

```py
# モジュールのインポート
from pyspark import pipelines as dp
from pyspark.sql.functions import *
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructType, StructField

# ソースデータのパスを定義
file_path = f"/databricks-datasets/songs/data-001/"

# ボリュームからデータを取り込むストリーミングテーブルを定義
schema = StructType(
  [
    StructField("artist_id", StringType(), True),
    StructField("artist_lat", DoubleType(), True),
    StructField("artist_long", DoubleType(), True),
    StructField("artist_location", StringType(), True),
    StructField("artist_name", StringType(), True),
    StructField("duration", DoubleType(), True),
    StructField("end_of_fade_in", DoubleType(), True),
    StructField("key", IntegerType(), True),
    StructField("key_confidence", DoubleType(), True),
    StructField("loudness", DoubleType(), True),
    StructField("release", StringType(), True),
    StructField("song_hotnes", DoubleType(), True),
    StructField("song_id", StringType(), True),
    StructField("start_of_fade_out", DoubleType(), True),
    StructField("tempo", DoubleType(), True),
    StructField("time_signature", DoubleType(), True),
    StructField("time_signature_confidence", DoubleType(), True),
    StructField("title", StringType(), True),
    StructField("year", IntegerType(), True),
    StructField("partial_sequence", IntegerType(), True)
  ]
)

@dp.table(
  comment="Million Song Datasetのサブセットからの生データ。現代音楽トラックの特徴量とメタデータのコレクション。"
)
def songs_raw():
  return (spark.readStream
    .format("cloudFiles")
    .schema(schema)
    .option("cloudFiles.format", "csv")
    .option("sep","\t")
    .load(file_path))

# データを検証し、カラム名を変更するマテリアライズドビューを定義
@dp.materialized_view(
  comment="分析用にクリーンアップ・準備されたMillion Song Dataset。"
)
@dp.expect("有効なアーティスト名", "artist_name IS NOT NULL")
@dp.expect("有効なタイトル", "song_title IS NOT NULL")
@dp.expect("有効な再生時間", "duration > 0")
def songs_prepared():
  return (
    spark.read.table("songs_raw")
      .withColumnRenamed("title", "song_title")
      .select("artist_id", "artist_name", "duration", "release", "tempo", "time_signature", "song_title", "year")
  )

# データをフィルタ・集計・ソートしたマテリアライズドビューを定義
@dp.materialized_view(
  comment="各年で最も多くの曲をリリースしたアーティストごとの曲数を集計したテーブル。"
)
def top_artists_by_year():
  return (
    spark.read.table("songs_prepared")
      .filter(expr("year > 0"))
      .groupBy("artist_name", "year")
      .count().withColumnRenamed("count", "total_number_of_songs")
      .sort(desc("total_number_of_songs"), desc("year"))
  )
```

これで、ロジックが実装できたので右上の**パイプラインを実行**をクリックします。
![Screenshot 2025-10-28 at 14.41.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ae49355b-acc1-4819-b9f6-7a0e32c7bda5.png)

処理がスタートします。
![Screenshot 2025-10-28 at 14.42.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1b3e876f-7ee2-468f-a7c6-719119b83308.png)

右側にパイプラインのDAG(有効非循回グラフ)が表示されます。
![Screenshot 2025-10-28 at 14.42.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cc3fc4a8-fdca-45f9-8b35-426dfbf612ac.png)

なお、右下の設定ボタンで、DAGの縦向き横向き表示を変更できます。データ処理の進捗をリアルタイムで確認できます。
![Screenshot 2025-10-28 at 14.42.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d518dfea-f924-480a-8805-10798704167f.png)

処理が完了するとグラフのすべてのノードが緑(エラーが起きたら赤)になります。
![Screenshot 2025-10-28 at 14.43.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/42fc2ff2-a424-48a3-9674-fe6fd089cdd9.png)

この時点で、処理されたデータを格納するテーブルが生成されているので、次のステップではこれらを探索します。
![Screenshot 2025-10-28 at 14.47.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c6ee4c66-9ba2-45e4-a0d4-77e6f1629f95.png)


# ステップ 3: パイプラインによって作成されたデータセットを探索する

**追加 > 探索**を選択して、探索用のファイルを作成します。
![Screenshot 2025-10-28 at 14.43.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/801d9d26-afb4-41fa-88ec-8fbafaa572ae.png)

名前をつけます。今回は言語を`SQL`にします。
![Screenshot 2025-10-28 at 14.43.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fc9da756-fcbe-4ee8-b1b8-e360e5cb63c7.png)

```sql
-- 各年ごとに最も多くの曲をリリースしたアーティストを1990年以降で抽出
SELECT artist_name, total_number_of_songs, year
  -- 利用しているカタログ/スキーマ名に置き換えてください:
  FROM takaakiyayoi_catalog.ldp.top_artists_by_year
  WHERE year >= 1990
  ORDER BY total_number_of_songs DESC, year DESC;
```

テーブルの中身を確認できます。
![Screenshot 2025-10-28 at 14.47.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4a54824b-a28f-44b7-b6c4-3fe0a1d3f59a.png)

また、DAGのノードをクリックすることで処理の詳細を確認することもできます。
![Screenshot 2025-10-28 at 14.47.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4957201b-dbab-4a21-b8ce-58ec419317cb.png)

画面下部にあるインジケーターをクリックするとイベントログを確認できます。
![Screenshot 2025-10-28 at 14.49.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2965182d-666a-488d-8221-7fa7d9ba11bd.png)
![Screenshot 2025-10-28 at 14.49.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/dc20c5eb-70cf-4f33-bc12-e6a89e279319.png)

[エクスペクテーション](https://docs.databricks.com/aws/ja/ldp/expectations)を定義している場合には、判定結果も確認できます。
![Screenshot 2025-10-28 at 14.50.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/87e8f727-38d4-4e9d-99d7-88e8119e8e27.png)

画面右上の**設定**からはパイプライン自身の設定を確認、変更できます。
![Screenshot 2025-10-28 at 14.50.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6f5bc460-7ad5-43f6-99f3-75e6f5c6c7ce.png)

# 手順 4: パイプラインを実行するジョブを作成する

このデータパイプラインを定期実行したい場合には、画面右上の**スケジュール**ボタンをクリックし、処理のスケジューリングを行います。
![Screenshot 2025-10-28 at 14.49.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/210e4819-59c1-47a6-8fb6-3faf51ab0df1.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

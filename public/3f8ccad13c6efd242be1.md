---
title: Databricksサンプルデータセットの説明
tags:
  - Databricks
  - Databricksチュートリアル
private: false
updated_at: '2022-06-10T08:25:14+09:00'
id: 3f8ccad13c6efd242be1
organization_url_name: databricks
slide: false
ignorePublish: false
---
Databricksにおけるファイルシステムである[DBFS(Databricksファイルシステム)](https://qiita.com/taka_yayoi/items/897264c486e179d72247)には最初から[サンプルデータ](https://qiita.com/taka_yayoi/items/dcf77d0b007fae774ce5)が格納されており、これらは`/databricks-datasets`のパスに存在します。

本記事では、2022/6/9時点(日々更新されます)で格納されているサンプルデータセットを説明します。データを読み込むサンプルコード、データの中身のスクリーンショットをカバーしています。

以下のコマンドをまとめたノートブックはこちらです。

https://github.com/taka-yayoi/public_repo/tree/main/databricks_datasets_datail

まず、`/databricks-datasets`の中のフォルダを表示するには、ノートブックで以下のコマンドを実行します。

```py:Python
%fs
ls /databricks-datasets/
```

|パス                                                           |名前                                 |説明                                                                                                   |データタイプ       |
|-------------------------------------------------------------|-----------------------------------|-----------------------------------------------------------------------------------------------------|-------------|
|dbfs:/databricks-datasets/COVID/                             |[COVID/](#covid)                             |COVID-19関連のデータ。定期的に更新される。                                                                            |構造化データ、テキストなど|
|dbfs:/databricks-datasets/README.md                          |README.md                          |/databricks-dataset自体の説明                                                                             |テキスト         |
|dbfs:/databricks-datasets/Rdatasets/                         |[Rdatasets/](#rdatasets)                         |元々はRで配布されているデータセット                                                                                   |構造化データなど     |
|dbfs:/databricks-datasets/SPARK_README.md                    |SPARK_README.md                    |SparkのReadme                                                                                         |テキスト         |
|dbfs:/databricks-datasets/adult/                             |[adult/](#adult)                             |"Census Income"データセット。国勢調査のデータに基づいて年収を予測するモデルを構築する際に使用される。                                           |構造化データ       |
|dbfs:/databricks-datasets/airlines/                          |[airlines/](#airlines)                          |アメリカの国内線の発着時刻のデータ                                                                                    |構造化データ       |
|dbfs:/databricks-datasets/amazon/                            |[amazon/](#amazon)                            |Amazonレビューのデータセット                                                                                    |構造化データ、テキストなど|
|dbfs:/databricks-datasets/asa/                               |[asa/](#asa)                               |Flight Performance Datasets 1997-2008                                                                |構造化データ       |
|dbfs:/databricks-datasets/atlas_higgs/                       |[atlas_higgs/](#atlas_higgs)                       |Dataset from the ATLAS Higgs Boson Machine Learning Challenge 2014 http://opendata.cern.ch/record/328|構造化データ       |
|dbfs:/databricks-datasets/bikeSharing/                       |[bikeSharing/](#bikesharing)                       |Bike Sharing Dataset: バイクシェアリングの実績および気候                                                              |構造化データ       |
|dbfs:/databricks-datasets/cctvVideos/                        |[cctvVideos/](#cctvvideos)                        |カメラから取得した動画、静止画                                                                                      |動画、画像        |
|dbfs:/databricks-datasets/credit-card-fraud/                 |[credit-card-fraud/](#credit-card-fraud)                 |クレジットカードトランザクションデータ                                                                                  |構造化データ       |
|dbfs:/databricks-datasets/cs100/                             |[cs100/](#cs100)                             |英語テキスト、ログデータなど                                                                                       |テキスト、準構造化データ |
|dbfs:/databricks-datasets/cs110x/                            |[cs110x/](#cs110x)                            |映画のレビュー                                                                                              |テキスト         |
|dbfs:/databricks-datasets/cs190/                             |[cs190/](#cs190)                             |millionsong.txt, neuro.txt https://github.com/theofpa/datascience/tree/master/spark/data/cs190       |構造化データ       |
|dbfs:/databricks-datasets/data.gov/                          |[data.gov/](#datagov)                          |Data.govデータセット                                                                                       |構造化データ       |
|dbfs:/databricks-datasets/definitive-guide/                  |[definitive-guide/](#definitive-guide)                  |Spark Definitive Guideで使用されているデータセット                                                                 |さまざま         |
|dbfs:/databricks-datasets/delta-sharing/                     |[delta-sharing/](#delta-sharing)                     |Delta Sharingサンプルデータセット                                                                              |構造化データ       |
|dbfs:/databricks-datasets/flights/                           |[flights/](#flights)                           |On-Time Performanceデータセット                                                                            |構造化データ       |
|dbfs:/databricks-datasets/flower_photos/                     |[flower_photos/](#flower_photos)                     |花の画像                                                                                                 |画像           |
|dbfs:/databricks-datasets/flowers/                           |[flowers/](#flowers)                           |花のデータを格納しているDeltaテーブル                                                                                |構造化データ、画像       |
|dbfs:/databricks-datasets/genomics/                          |[genomics/](#genomics)                          |ゲノムデータ                                                                                               |準構造化データ      |
|dbfs:/databricks-datasets/hail/                              |[hail/](#hail)                              |hail用データ。サンプル、人口グループ、属性とVCF                                                                          |構造化データ       |
|dbfs:/databricks-datasets/identifying-campaign-effectiveness/|[identifying-campaign-effectiveness/](#identifying-campaign-effectiveness)|SafeGraph FootTraffic Dataset                                                                        |構造化データ       |
|dbfs:/databricks-datasets/iot/                               |[iot/](#iot)                               |IoTセンサーデータ                                                                                           |構造化データ       |
|dbfs:/databricks-datasets/iot-stream/                        |[iot-stream/](#iot-stream)                        |IOT Device Data(合成)                                                                                  |構造化データ       |
|dbfs:/databricks-datasets/learning-spark/                    |[learning-spark/](#learning-spark)                    |書籍Learning Sparkで使用されているデータセット                                                                       |さまざま         |
|dbfs:/databricks-datasets/learning-spark-v2/                 |[learning-spark-v2/](#learning-spark-v2)                 |MnM Datasetなど                                                                                        |さまざま         |
|dbfs:/databricks-datasets/lending-club-loan-stats/           |[lending-club-loan-stats/](#lending-club-loan-stats)           |融資データ                                                                                                |構造化データ       |
|dbfs:/databricks-datasets/med-images/                        |[med-images/](#med-images)                        |病理画像 Camelyon16 Grand Challenge                                                                      |画像           |
|dbfs:/databricks-datasets/media/                             |[media/](#media)                             |OpenRTB BidStream Sample Dataset                                                                     |構造化データ       |
|dbfs:/databricks-datasets/mnist-digits/                      |[mnist-digits/](#mnist-digits)                      |MNIST handwritten digits dataset 手書き数字データ                                                            |画像           |
|dbfs:/databricks-datasets/news20.binary/                     |[news20.binary/](#news20binary)                     |20 Newsgroups Dataset 2値分類                                                                           |構造化データ       |
|dbfs:/databricks-datasets/nyctaxi/                           |[nyctaxi/](#nyctaxi)                           |NYC Taxi Dataset タクシー乗降記録                                                                            |構造化データ       |
|dbfs:/databricks-datasets/nyctaxi-with-zipcodes/             |[nyctaxi-with-zipcodes/](#nyctaxi-with-zipcodes)             |NYC Taxi with Zipcodes Dataset                                                                       |構造化データ       |
|dbfs:/databricks-datasets/online_retail/                     |[online_retail/](#online_retail)                     |オンラインストアの注文データ                                                                                       |構造化データ       |
|dbfs:/databricks-datasets/overlap-join/                      |[overlap-join/](#overlap-join)                      |不明                                                                                                   |構造化データ       |
|dbfs:/databricks-datasets/power-plant/                       |[power-plant/](#power-plant)                       |Combined Cycle Power Plant Data Set 電力プラントのデータ                                                       |構造化データ       |
|dbfs:/databricks-datasets/retail-org/                        |[retail-org/](#retail-org)                        |Synthetic Retail Dataset 合成小売データ                                                                     |構造化データ       |
|dbfs:/databricks-datasets/rwe/                               |[rwe/](#rwe)                               |Simulated Patient Data シミュレートした患者データ                                                                 |構造化データ       |
|dbfs:/databricks-datasets/sai-summit-2019-sf/                |[sai-summit-2019-sf/](#sai-summit-2019-sf)                |Fire Calls-For-Service 消防署への電話記録                                                                     |構造化データ       |
|dbfs:/databricks-datasets/sample_logs/                       |[sample_logs/](#sample_logs)                       |Webサーバーログのサンプル                                                                                       |準構造化データ      |
|dbfs:/databricks-datasets/samples/                           |[samples/](#samples)                           |サンプルデータ                                                                                              |さまざま         |
|dbfs:/databricks-datasets/sfo_customer_survey/               |[sfo_customer_survey/](#sfo_customer_survey)               |2013 SFO Customer Survey Data Set + Dictionary                                                       |構造化データ       |
|dbfs:/databricks-datasets/sms_spam_collection/               |[sms_spam_collection/](#sms_spam_collection)               |SMS Spam Collection                                                                                  |テキスト         |
|dbfs:/databricks-datasets/songs/                             |[songs/](#songs)                             |Sample of Million Song Dataset                                                                       |構造化データ       |
|dbfs:/databricks-datasets/structured-streaming/              |[structured-streaming/](#structured-streaming)              |構造化ストリーミングのサンプルデータ                                                                                   |構造化データ       |
|dbfs:/databricks-datasets/timeseries/                        |[timeseries/](#timeseries)                        |Fire Department Calls for Service                                                                    |構造化データ       |
|dbfs:/databricks-datasets/tpch/                              |[tpch/](#tpch)                              |TPC-H Data                                                                                           |構造化データ       |
|dbfs:/databricks-datasets/warmup/                            |[warmup/](#warmup)                            |TCP-DS Data                                                                                          |構造化データ       |
|dbfs:/databricks-datasets/weather/                           |[weather/](#weather)                           |Seattle Temperature Recordings Data Set                                                              |構造化データ       |
|dbfs:/databricks-datasets/wiki/                              |[wiki/](#wiki)                              |Wikipediaデータ                                                                                         |テキスト         |
|dbfs:/databricks-datasets/wikipedia-datasets/                |[wikipedia-datasets/](#wikipedia-datasets)                |Wikipediaデータ                                                                                         |テキスト、構造化データ  |
|dbfs:/databricks-datasets/wine-quality/                      |[wine-quality/](#wine-quality)                      |Wine Quality Data Set                                                                                |構造化データ       |

# COVID

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/COVID/CORD-19/2021-03-28/metadata.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.28.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/495605d7-98da-12cf-bee0-c4588b16b4bc.png)

# RDatasets

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.29.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1ed5f835-9b4d-3d13-8d6a-5f3a47fe5644.png)

# adult

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/adult/adult.data")
display(df)
```

![Screen Shot 2022-06-09 at 21.30.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d533b235-b892-85ba-a524-9cbe5e58495d.png)

# airlines

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/airlines/part-00000")
display(df)
```

![Screen Shot 2022-06-09 at 21.30.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f4b31062-9657-5b36-3a56-a697101be273.png)

# amazon

```py:Python
df = spark.read.format("parquet").option("header", True).load("dbfs:/databricks-datasets/amazon/data20K/")
display(df)
```

![Screen Shot 2022-06-09 at 21.31.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a11d808e-4115-95fc-af59-1315d2d30f5d.png)

# asa

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/asa/airlines/1987.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.32.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a39429a3-4b3a-248a-6937-085e82a0dee7.png)

# atlas_higgs

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/atlas_higgs/atlas_higgs.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.32.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b3776914-1864-0936-9d7b-b636cd31f073.png)

# bikeSharing

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/bikeSharing/data-001/day.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.33.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8e9c912c-f794-b8d9-049c-a26b59d03e5f.png)

# cctvVideos

```py:Python
df = spark.read.format("image").load("dbfs:/databricks-datasets/cctvVideos/train_images/")
display(df)
```

![Screen Shot 2022-06-09 at 21.33.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3eb569c7-0837-8d18-2199-d88ad99178a2.png)

# credit-card-fraud

```py:Python
df = spark.read.format("parquet").option("header", True).load("dbfs:/databricks-datasets/credit-card-fraud/data/")
display(df)
```

![Screen Shot 2022-06-09 at 21.34.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cf84ac8f-92ae-13c9-4471-4f62949ae6be.png)

# cs100

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/cs100/lab2/data-001/apache.access.log.PROJECT"))
```

![Screen Shot 2022-06-09 at 21.34.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/636d47f1-94b8-f98c-a843-e55ed2cf4b72.png)

# cs110x

```py:Python
df = spark.read.option("header", False).option("delimiter", "::").csv("dbfs:/databricks-datasets/cs110x/ml-1m/data-001/movies.dat")
display(df)
```

![Screen Shot 2022-06-09 at 21.36.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c3401fbd-6385-b1f3-bac6-da36fb90ed68.png)

# cs190

```py:Python
df = spark.read.option("header", False).csv("dbfs:/databricks-datasets/cs190/data-001/millionsong.txt")
display(df)
```

![Screen Shot 2022-06-09 at 21.37.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ca054a6e-2112-ca03-6664-c9f4eb73920a.png)

# data.gov

```py:Python
df = spark.read.option("header", True).csv("dbfs:/databricks-datasets/data.gov/irs_zip_code_data/data-001/2013_soi_zipcode_agi.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.38.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1a730e83-153b-5eca-32d0-1c002bd2e0dd.png)

# definitive-guide

```py:Python
df = spark.read.format("json").load("dbfs:/databricks-datasets/definitive-guide/data/activity-data/")
display(df)
```

![Screen Shot 2022-06-09 at 21.38.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f3831cc4-66a0-a74c-da28-cb20f58b3b06.png)

# delta-sharing

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/delta-sharing/samples/README.md"))
```

![Screen Shot 2022-06-09 at 21.39.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b6a15487-aad2-4dc8-79bc-7b7969c8f792.png)

# flights

```py:Python
df = spark.read.format("csv").option("header", True).load("dbfs:/databricks-datasets/flights/departuredelays.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.39.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/620f0b25-ef4f-d712-11d9-b333173a24d7.png)

# flower_photos

```py:Python
df = spark.read.format("image").load("dbfs:/databricks-datasets/flower_photos/daisy/")
display(df)
```

![Screen Shot 2022-06-09 at 21.40.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/07aa416c-9b26-3e96-c03d-0dffd3270b98.png)

# flowers

```py:Python
df = spark.read.format("delta").load("dbfs:/databricks-datasets/flowers/delta/")
display(df)
```

![Screen Shot 2022-06-09 at 21.41.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3dd3a0bf-5792-50b9-f193-2282faffb4d1.png)

# genomics

```py:Python
df = spark.read.format("parquet").load("dbfs:/databricks-datasets/genomics/1000G/dbgenomics.data/")
display(df)
```

![Screen Shot 2022-06-09 at 21.41.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/10699630-0722-7290-8a9b-6ecbe8d8a913.png)

# hail

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/hail/data-001/1kg_annotations.txt"))
```

![Screen Shot 2022-06-09 at 21.42.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8b36c27c-28ed-097b-e516-648be8b8cb3f.png)

# identifying-campaign-effectiveness

```py:Python
df = spark.read.format("csv").option("header", True).load("dbfs:/databricks-datasets/identifying-campaign-effectiveness/subway_foot_traffic/foot_traffic.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.43.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/aa4eed41-847b-dc61-cd4a-e83ff7862c74.png)

# iot

```py:Python
df = spark.read.format("json").load("dbfs:/databricks-datasets/iot/iot_devices.json")
display(df)
```

![Screen Shot 2022-06-09 at 21.43.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/16772ab1-ccd5-c865-b68d-04d557d3f4cc.png)

# learning-spark

```py:Python
df = spark.read.format("csv").load("dbfs:/databricks-datasets/learning-spark/data-001/favourite_animals.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.45.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2176e53c-c3ff-4afb-9a29-7ebf1e737957.png)

# learning-spark-v2

```py:Python
df = spark.read.format("csv").option("header", True).load("dbfs:/databricks-datasets/learning-spark-v2/mnm_dataset.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.46.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d7b9a91a-576f-77a4-706d-db3ebb88ec5c.png)

# lending-club-loan-stats

```py:Python
df = spark.read.format("csv").option("header", True).load("dbfs:/databricks-datasets/lending-club-loan-stats/LoanStats_2018Q2.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.47.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/824e18ed-6304-3542-f52b-cee8694ae2bd.png)

# med-images

```py:Python
%pip install openslide-python
```

```py:Python
WSI_TIF_PATH = "/databricks-datasets/med-images/camelyon16/"

import numpy as np
import openslide
import matplotlib.pyplot as plt

f, axarr = plt.subplots(1,4,sharey=True)
i=0
for pid in ["normal_034","normal_036","tumor_044", "tumor_045"]:
  path = '/dbfs/%s/%s.tif' %(WSI_TIF_PATH,pid)
  slide = openslide.OpenSlide(path)
  axarr[i].imshow(slide.get_thumbnail(np.array(slide.dimensions)//50))
  axarr[i].set_title(pid)
  i+=1
display()
```

![Screen Shot 2022-06-09 at 21.47.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/af650cc7-6872-c8c7-28bf-8fe9b7af0247.png)

# media

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/media/rtb/raw_incoming_bid_stream/bidRequestSample.txt"))
```

![Screen Shot 2022-06-09 at 21.48.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/dea397c7-7fe3-119b-db13-f12ee6e2ce12.png)

# mnist-digits

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/mnist-digits/README.md"))
```

![Screen Shot 2022-06-09 at 21.49.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/44158767-25e9-943e-b98e-cb7f022946a4.png)

# news20.binary

```py:Python
df = spark.read.format("parquet").load("dbfs:/databricks-datasets/news20.binary/data-001/training/")
display(df)
```

![Screen Shot 2022-06-09 at 21.49.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8afe8940-5698-1a4a-2f65-8420a81f92e9.png)

# nyctaxi

```py:Python
df = spark.read.format("json").load("dbfs:/databricks-datasets/nyctaxi/sample/json/")
display(df)
```

![Screen Shot 2022-06-09 at 21.50.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f5b8d6ec-b5aa-bbc3-1352-899ebcb01b11.png)

# nyctaxi-with-zipcodes

```py:Python
df = spark.read.format("delta").load("dbfs:/databricks-datasets/nyctaxi-with-zipcodes/subsampled/")
display(df)
```

![Screen Shot 2022-06-09 at 21.51.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/38842380-e893-5199-4007-457ebd154d51.png)

# online_retail

```py:Python
df = spark.read.format("csv").option("header", True).load("dbfs:/databricks-datasets/online_retail/data-001/data.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.51.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2426961c-3b1e-1aa4-c585-4f028eb81c7f.png)

# overlap-join

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/overlap-join"))
```

![Screen Shot 2022-06-09 at 21.52.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/032cc86e-5d10-1fd4-5cb4-d6c875a93105.png)

# power-plant

```py:Python
df = spark.read.format("csv").option("header", True).option("delimiter", "\t").load("dbfs:/databricks-datasets/power-plant/data/Sheet1.tsv")
display(df)
```

![Screen Shot 2022-06-09 at 21.52.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0e71b3d5-24e7-5d25-1561-5444e89008b8.png)

# retail-org

```py:Python
df = spark.read.format("parquet").load("dbfs:/databricks-datasets/retail-org/active_promotions/active_promotions.parquet")
display(df)
```

![Screen Shot 2022-06-09 at 21.53.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3f07425d-a4b1-77dd-7e04-7eba841350d4.png)

# rwe

```py:Python
df = spark.read.format("csv").option("header", True).option("delimiter", ",").load("dbfs:/databricks-datasets/rwe/ehr/csv/allergies.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.53.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7d2ca967-79b0-97a3-647e-ec686469be4b.png)

# sai-summit-2019-sf

```py:Python
df = spark.read.format("csv").option("header", True).option("delimiter", ",").load("dbfs:/databricks-datasets/sai-summit-2019-sf/fire-calls.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.54.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/594354e5-653d-44bf-52c5-55d5cb33a580.png)

# sample_logs

```py:Python
df = spark.read.format("csv").load("/databricks-datasets/sample_logs/")
display(df)
```

![Screen Shot 2022-06-09 at 21.54.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9a85e92a-3c86-9e15-36db-59a4cdd07165.png)

# samples

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/samples/data/mllib/gmm_data.txt"))
```

![Screen Shot 2022-06-09 at 21.55.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5e3820a2-5c7c-5ca6-621e-70cf7b9c6744.png)

# sfo_customer_survey

```py:Python
df = spark.read.format("csv").option("header", True).load("dbfs:/databricks-datasets/sfo_customer_survey/2013_SFO_Customer_Survey.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.56.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b35311e1-97b5-d2a9-3d19-0456358fd381.png)

# sms_spam_collection

```py:Python
df = spark.read.format("csv").option("header", False).load("dbfs:/databricks-datasets/sms_spam_collection/data-001/smsData.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.56.38.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fac749fd-3381-414f-dd52-b608c44902f5.png)

# songs

```py:Python
df = spark.read.format("csv").option("header", False).option("delimiter", "\t").load("dbfs:/databricks-datasets/songs/data-001/part-00000")
display(df)
```

![Screen Shot 2022-06-09 at 21.57.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5c9ef195-cfce-a2de-9fbf-1222646d7664.png)

# structured-streaming

```py:Python
df = spark.read.format("json").load("dbfs:/databricks-datasets/structured-streaming/events/file-0.json")
display(df)
```

![Screen Shot 2022-06-09 at 21.57.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/07e8d0d5-afc5-e109-5397-3dcdfa556922.png)

# timeseries

```py:Python
df = spark.read.format("csv").option("header", True).option("delimiter", ",").load("dbfs:/databricks-datasets/timeseries/Fires/Fire_Department_Calls_for_Service.csv")
display(df)
```

![Screen Shot 2022-06-09 at 21.58.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/32832a00-ee57-d011-e71c-b9cbc6793778.png)

# tpch

```py:Python
print(dbutils.fs.head("dbfs:/databricks-datasets/tpch/README.md"))
```

![Screen Shot 2022-06-09 at 21.58.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f89112ab-09e0-69d3-0877-a40c323aeb8d.png)

# warmup

```py:Python
%fs
ls dbfs:/databricks-datasets/warmup/
```

![Screen Shot 2022-06-09 at 21.59.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fdd8b816-88be-d8e1-c7d3-e29eb9dea4f2.png)

# weather

```py:Python
df = spark.read.format("csv").option("header", True).option("delimiter", ",").load("dbfs:/databricks-datasets/weather/high_temps")
display(df)
```

![Screen Shot 2022-06-09 at 21.59.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6d355506-76bd-8008-ef52-2d6e31786555.png)

# wiki

```py:Python
df = spark.read.format("csv").load("dbfs:/databricks-datasets/wiki/")
display(df)
```

![Screen Shot 2022-06-09 at 22.00.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9fabb3b3-fae6-f3cb-e0f6-7bc244ecedf3.png)

# wikipedia-datasets

```py:Python
df = spark.read.format("json").load("dbfs:/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/")
display(df)
```

![Screen Shot 2022-06-09 at 22.01.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/176fb277-fc9c-fc8c-d738-8a92468762f2.png)

# wine-quality

```py:Python
df = spark.read.format("csv").option("header", True).option("delimiter", ";").load("dbfs:/databricks-datasets/wine-quality/winequality-red.csv")
display(df)
```

![Screen Shot 2022-06-09 at 22.01.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8e1ecdd5-8b9c-66a7-66c1-32a74cb44c0f.png)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Unity Catalogのリネージはどのように、どこまで追跡できるのか
tags:
  - Databricks
  - UnityCatalog
private: false
updated_at: '2025-03-08T08:51:15+09:00'
id: a7bfd28f2d3b28b56ecc
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
きっかけはこちらのブログ記事です。

https://qiita.com/taka_yayoi/items/2c39820ea4b8d697edcc

こちらでは、Delta Live Tables(DLT)でデータの前処理を通じて特徴量を作成し、AutoMLで時系列予測を行うという流れが説明されています。その際にはDLTにおけるリネージは追跡されるのですが、AutoMLになったところでリネージが途切れてしまいます。なお、[サーバレスの時系列予測AutoML](https://docs.databricks.com/aws/ja/machine-learning/train-model/serverless-forecasting)は特徴量ストア連携をサポートしていません。

そこで、以下のような機械学習モデルのライフサイクルを通じてどのようにリネージを追跡できるのかを調べてみました。

![Screenshot 2025-03-07 at 14.26.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4e68d360-0ad5-4c0a-acd0-ae88a660fccc.png)

参考にしたマニュアルはこちらです。

- [Unity Catalogを使用したデータリネージのキャプチャと表示 \| Databricks Documentation](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/data-lineage)
- [Unity Catalogで特徴量テーブルを使用する \| Databricks Documentation](https://docs.databricks.com/aws/ja/machine-learning/feature-store/uc/feature-tables-uc)
- [Unity Catalogでモデルのライフサイクルを管理する \| Databricks Documentation](https://docs.databricks.com/aws/ja/machine-learning/manage-model-lifecycle/)
- [特徴量のガバナンスのリネージ \| Databricks Documentation](https://docs.databricks.com/aws/ja/machine-learning/feature-store/lineage)

[こちら](https://docs.databricks.com/aws/ja/machine-learning/feature-store/online-tables#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BE%8B)のサンプルノートブックをベースとして、上のリネージを実現してみます。

# DLTにおけるリネージ

DLTでパイプラインを構成すれば、パイプラインに含まれるビューやテーブルのリネージは自動で追跡されます。

## 特徴量テーブルの準備

`wine_id`だけでワインの品質を予測するエンドポイントを構築する必要があるとします。これには、エンドポイントが`wine_id`でワインの特徴を検索できるように、Feature Storeに保存された特徴量テーブルが必要です。このデモの目的のために、まずこの特徴量テーブルを自分で準備する必要があります。手順は次のとおりです：

1. 生データを読み込み、クリーンアップする。
2. 特徴量とラベルを分離する。
3. 特徴量を特徴量テーブルに保存する。

## 生データの読み込み

生データには11の特徴量と`quality`列を含む12列があります。`quality`列は3から8の範囲の整数です。目標は`quality`値を予測するモデルを構築することです。

:::note info
**注意**
- 以下では列名にスペースを含むデータを取り扱う必要があるため、`table_properties`や`delta.minReaderVersion`を指定することで[カラムマッピング](https://docs.databricks.com/aws/ja/delta/column-mapping)を有効化してエラーを回避しています。
- DLTではデータソースとしてボリュームからファイルを読み込んでいても、現時点ではボリュームとのリネージは追跡されません。
:::


```py
# モジュールのインポート
import dlt
from pyspark.sql.functions import *

# 変数にパイプラインパラメータを割り当て
my_catalog = spark.conf.get("my_catalog")
my_schema = spark.conf.get("my_schema")
my_volume = spark.conf.get("my_volume")

# ソースデータへのパスを定義
volume_path = f"/Volumes/{my_catalog}/{my_schema}/{my_volume}/"

# ボリュームからデータを取り込むストリーミングテーブルを定義
@dlt.table(
  comment="生のワイン品質データ",
  table_properties={
    "delta.columnMapping.mode": "name",
    'delta.minReaderVersion': '3',
    'delta.minWriterVersion': '7'
  }
)
def wine_quality_raw():
  df = (spark.readStream
   .format("cloudFiles")
   .option("cloudFiles.format", "csv")
   .option("inferSchema", True)
   .option("separator", ";")
   .option("header", True)
   .load(volume_path)
  )
  return df
```

## クリーンアップ

生データにはいくつかの問題があります：
1. 列名にスペース（' '）が含まれており、これはFeature Storeと互換性がありません。
2. 後でFeature Storeで検索できるように、生データにIDを追加する必要があります。

次のセルでは、これらの問題に対処します。

```py
from pyspark.sql.types import DoubleType

# ID列を追加する関数
def addIdColumn(dataframe, id_column_name):
    columns = dataframe.columns
    new_df = dataframe.withColumn(id_column_name, monotonically_increasing_id())
    return new_df[[id_column_name] + columns]

# 列名を変更する関数
def renameColumns(df):
    renamed_df = df

    for column in df.columns:
        renamed_df = renamed_df.withColumn(column, df[column].cast(DoubleType()))

    for column in df.columns:
        renamed_df = renamed_df.withColumnRenamed(column, column.replace(' ', '_'))
    return renamed_df

# データを検証するマテリアライズドビューを定義
@dlt.table(
 comment="分析のためにクリーンアップされたワインデータ"
)
@dlt.expect("valid_quality", "quality IS NOT NULL")
def wine_quality_prepared():
  raw_data_frame = spark.table("wine_quality_raw")
  # 列名をFeature Storeに対応するように変更
  renamed_df = renameColumns(raw_data_frame)

  # ID列を追加
  id_and_data = addIdColumn(renamed_df, 'wine_id')
  return id_and_data
```

## 特徴量テーブルの作成

ワインが開封された後、アルコール度数は時間とともに変化する変数であると仮定します。この値はオンライン推論のためにリアルタイム入力として提供されます。

次に、データを2つの部分に分割し、静的特徴を含む部分のみを特徴量テーブルとして保存します。

:::note info
**注意**
- [こちら](https://docs.databricks.com/aws/ja/machine-learning/feature-store/uc/feature-tables-uc#dlt-%E3%83%91%E3%82%A4%E3%83%97%E3%83%A9%E3%82%A4%E3%83%B3%E3%81%AB%E3%82%88%E3%81%A3%E3%81%A6%E4%BD%9C%E6%88%90%E3%81%95%E3%82%8C%E3%81%9F%E3%82%B9%E3%83%88%E3%83%AA%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%81%BE%E3%81%9F%E3%81%AF%E3%83%9E%E3%83%86%E3%83%AA%E3%82%A2%E3%83%A9%E3%82%A4%E3%82%BA%E3%83%89%E3%83%93%E3%83%A5%E3%83%BC%E3%82%92%E7%89%B9%E5%BE%B4%E9%87%8F%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%81%A8%E3%81%97%E3%81%A6%E4%BD%BF%E7%94%A8%E3%81%97%E3%81%BE%E3%81%99)に記載があるように、DLTのマテリアライズドビューは主キーを設定することで特徴量テーブルとして取り扱うことができます。
:::


```py
# トレーニングと推論で使用するマテリアライズドビューを定義
@dlt.table(
  comment="静的な特徴量テーブル",
  schema="""
    wine_id bigint NOT NULL PRIMARY KEY,
    fixed_acidity double,
    volatile_acidity double,
    citric_acid double,
    residual_sugar double,
    chlorides double,
    free_sulfur_dioxide double,
    total_sulfur_dioxide double,
    density double,
    pH double,
    sulphates double
"""
)
def wine_quality_static_feature():
  id_and_data = spark.table("wine_quality_prepared")
  # wine_idと静的特徴量
  id_static_features = id_and_data.drop('alcohol', 'quality', '_rescued_data')

  return id_static_features


# トレーニングと推論で使用するマテリアライズドビューを定義
@dlt.table(
 comment="動的な特徴量と目的変数を保持するテーブル"
)
def wine_quality_id_rt_feature():
  id_and_data = spark.table("wine_quality_prepared")
  # wine_id、リアルタイム特徴量（alcohol）、ラベル（quality）
  id_rt_feature_labels = id_and_data.select('wine_id', 'alcohol', 'quality')

  return id_rt_feature_labels
```

このパイプラインを実行することで、以下のようなパイプラインのリネージが追跡されます。

![Screenshot 2025-03-07 at 14.46.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5f42ba32-a675-426e-bda8-ce5150a80c63.png)

# 特徴量と機械学習モデルのリネージ

```py
%pip install databricks-sdk==0.41.0
%pip install databricks-feature-engineering==0.8.0
%pip install mlflow>=2.9.0
dbutils.library.restartPython()
```

```py
# カタログに対する `CREATE CATALOG` 権限が必要です。
# 必要に応じて、ここでカタログとスキーマ名を変更してください。
username = spark.sql("SELECT current_user()").first()["current_user()"]
username = username.split(".")[0]

# 既存のカタログを使います
catalog_name = "users"

# スキーマ名として使用するユーザー名を取得します。
schema_name = "takaaki_yayoi"

#spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
spark.sql(f"USE CATALOG {catalog_name}")
#spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_name}.{schema_name}")
spark.sql(f"USE SCHEMA {schema_name}")
```

## Databricksオンラインテーブルの設定

このままでも、DLTのマテリアライズドビューを特徴量テーブルとして用いることで機械学習モデルとのリネージを追跡することができます。しかし、最後のモデルサービングエンドポイントでオンラインの特徴量ルックアップを行えるようにするには、オンラインテーブルにする必要があります。

カタログエクスプローラーUI、Databricks SDK、またはRest APIからオンラインテーブルを作成できます。以下に、Databricks Python SDKを使用する手順を説明します。詳細については、Databricksのドキュメントを参照してください（[AWS](https://docs.databricks.com/aws/ja/machine-learning/feature-store/online-tables) | [Azure](https://learn.microsoft.com/ja-jp/azure/databricks/machine-learning/feature-store/online-tables#create)）。必要な権限については、権限に関する情報を参照してください（[AWS](https://docs.databricks.com/ja/machine-learning/feature-store/online-tables.html#user-permissions) | [Azure](https://learn.microsoft.com/ja-jp/azure/databricks/machine-learning/feature-store/online-tables#user-permissions)）。

```py
wine_table = f"{catalog_name}.{schema_name}.wine_quality_static_feature"
online_table_name = f"{catalog_name}.{schema_name}.wine_quality_static_features_online"
```

### オンラインテーブルの作成

```py
from pprint import pprint
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import OnlineTable, OnlineTableSpec, OnlineTableSpecTriggeredSchedulingPolicy

workspace = WorkspaceClient()

# オンラインテーブルを作成
spec = OnlineTableSpec(
  primary_key_columns = ["wine_id"],
  source_table_full_name = wine_table,
  run_triggered=OnlineTableSpecTriggeredSchedulingPolicy.from_dict({'triggered': 'true'}),
  perform_full_copy=True)

online_table = OnlineTable(name=online_table_name, spec=spec)

try:
  workspace.online_tables.create_and_wait(table=online_table)
  
except Exception as e:
  if "already exists" in str(e):
    print(f"オンラインテーブル {online_table_name} は既に存在します。再作成しません。")  
  else:
    raise e

pprint(workspace.online_tables.get(online_table_name))
```

![Screenshot 2025-03-07 at 14.51.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d2c8ffd3-e1d8-4a5b-9798-c53707ecbc42.png)

## モデルのトレーニングとデプロイ

次に、特徴量を使用して分類器をトレーニングします。主キーを指定するだけで必要な特徴量を取得します。

```py
from sklearn.ensemble import RandomForestClassifier

import pandas as pd
import logging
import mlflow.sklearn

from databricks.feature_engineering import FeatureLookup
```

まず、`TrainingSet`を定義します。トレーニングセットは`feature_lookups`リストを受け取り、各アイテムはFeature Store内の特徴量テーブルからの特徴量を表します。この例では、`wine_id`をルックアップキーとして使用し、テーブル`online_feature_store_example.wine_features`からすべての特徴量を取得します。

```py
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

id_rt_feature_labels = spark.table(f"{catalog_name}.{schema_name}.wine_quality_id_rt_feature")
```

### ワイン品質トレーニングデータローダー

```py
# トレーニングセットを作成
training_set = fe.create_training_set(
    df=id_rt_feature_labels,
    label='quality',
    feature_lookups=[
        FeatureLookup(
            table_name=f"{catalog_name}.{schema_name}.wine_quality_static_feature",
            lookup_key="wine_id"
        )
    ],
    exclude_columns=['wine_id'],
)

# Feature Storeからトレーニングデータをロード
training_df = training_set.load_df()

display(training_df)
```
|alcohol|fixed_acidity|volatile_acidity|citric_acid|residual_sugar|chlorides|free_sulfur_dioxide|total_sulfur_dioxide|density|pH|sulphates|quality|
|---|---|---|---|---|---|---|---|---|---|---|---|
|10.1|11.5|0.18|0.51|4|0.104|4|23|0.9996|3.28|0.97|6|
|10.6|9.1|0.28|0.48|1.8|0.067|26|46|0.9967|3.32|1.04|6|
|10|7.6|0.42|0.08|2.7|0.084|15|48|0.9968|3.21|0.59|5|
|10.4|6.4|0.79|0.04|2.2|0.061|11|17|0.99588|3.53|0.65|6|
|11.9|6.2|0.7|0.15|5.1|0.076|13|27|0.99622|3.54|0.6|6|

次のセルでは、RandomForestClassifierモデルをトレーニングします。

```py
# トレーニングデータの特徴量とラベルを準備
X_train = training_df.drop('quality').toPandas()
y_train = training_df.select('quality').toPandas()

# モデルをトレーニング
model = RandomForestClassifier()
model.fit(X_train, y_train.values.ravel())
```

トレーニング済みモデルを`log_model`を使用して保存します。`log_model`は、モデルと特徴量（`training_set`を通じて）の間の系統情報も保存します。そのため、サービング中にモデルはルックアップキーだけで特徴量をどこから取得するかを自動的に認識します。

### MLflowによるモデル登録

```py
import mlflow

mlflow.set_registry_uri("databricks-uc")

registered_model_name = f"{catalog_name}.{schema_name}.wine_classifier"
fe.log_model(
    model=model,
    artifact_path="model",
    flavor=mlflow.sklearn,
    training_set=training_set,
    registered_model_name=registered_model_name
)

# 最新のモデルバージョンを取得
client = mlflow.tracking.MlflowClient()
versions = client.search_model_versions(f"name='{registered_model_name}'")
registered_model_version = max(int(v.version) for v in versions)
```

`log_model`を呼び出した後、新しいバージョンのモデルが保存されます。ここまでで、このようにリネージが追跡されています。

![Screenshot 2025-03-07 at 14.53.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b13b5b5c-00c2-4425-9b2f-a812c2bb5219.png)

# 機械学習モデルとモデルサービングエンドポイントのリネージ

モデルをモデルサービングエンドポイントにデプロイすることでリネージが追跡されます。

## 自動特徴量ルックアップを使用したリアルタイムクエリの提供


```py
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput

# エンドポイントを作成
endpoint_name = f"{username}_wine_classifier_endpoint"

try:
  status = workspace.serving_endpoints.create_and_wait(
    name=endpoint_name,
    config = EndpointCoreConfigInput(
      served_entities=[
        ServedEntityInput(
            entity_name=registered_model_name,
            entity_version=registered_model_version,
            scale_to_zero_enabled=True,
            workload_size="Small"
        )
      ]
    )
  )
  print(status)
except Exception as e:
  if "already exists" in str(e):
    print(f"エンドポイント {endpoint_name} は既に存在するため、作成しません。")
  else:
    raise e
```

![Screenshot 2025-03-07 at 14.55.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/94bbd20d-ef3c-480f-ad60-da4a844de6fb.png)

## クエリを送信する

さて、ワインのボトルを開けて、ボトルから現在のABVを測定するセンサーがあるとします。モデルと自動特徴量ルックアップを使用したリアルタイムサービングを使用して、測定されたABV値をリアルタイム入力「alcohol」としてワインの品質を予測できます。

```py
import mlflow.deployments

client = mlflow.deployments.get_deploy_client("databricks")
response = client.predict(
    endpoint=endpoint_name,
    inputs={
        "dataframe_records": [
            {"wine_id": 25, "alcohol": 7.9},
            {"wine_id": 25, "alcohol": 11.0},
            {"wine_id": 25, "alcohol": 27.9},
            {"wine_id": 79, "alcohol": 1.9},
            {"wine_id": 79, "alcohol": 101.0},
            {"wine_id": 37, "alcohol": 27.9},
        ]
    },
)

pprint(response)
```
```
{'predictions': [5.0, 5.0, 5.0, 4.0, 5.0, 6.0]}
```

これで、エンドポイントとのリネージも追跡されます。

![Screenshot 2025-03-07 at 14.57.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ea8b38d9-37c1-4e2c-9acd-12de1de47845.png)

# まとめ

![Screenshot 2025-03-08 at 8.50.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/26432d76-7fac-441f-b978-6bc67dfae974.png)


- **DLTのリネージ:** パイプラインによって生成されるテーブルやビューのリネージは追跡される。ボリュームとのリネージは未対応。主キーを設定することで特徴量テーブルとして使用できる。
- **特徴量テーブルと機械学習モデルのリネージ:** `mlflow.log_input`あるいは`FeatureEngineeringClient.log_model`でモデルをロギングすることでリネージが追跡される。
- **機械学習モデルとサービングエンドポイントとのリネージ:** 特徴量ルックアップを行う場合にはオンラインテーブルを作成する必要がある。モデルをサービングエンドポイントにデプロイすればリネージが追跡される


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

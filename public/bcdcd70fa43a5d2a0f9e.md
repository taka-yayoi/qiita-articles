---
title: Databricksにおける生成AIを用いた製品オンボーディング
tags:
  - Ray
  - Databricks
  - ソリューションアクセラレータ
  - 生成AI
private: false
updated_at: '2025-02-07T15:05:00+09:00'
id: bcdcd70fa43a5d2a0f9e
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらのサンプルノートブックをウォークスルーします。

**製品オンボーディング**とは新製品がサプライヤーから提供された際、小売業者がその新製品に関する情報を適切に店舗やオンラインコマースサイトに登録するプロセスです。サプライヤーから提供されるデータには色の情報がなかったり、説明文が間違っているケースがありますが、生成AIを活用することでそれらを効率的かつ正確に処理することが可能となります

https://qiita.com/taka_yayoi/items/6f8344ba2347b115b12a

オリジナルはこちら。5つのノートブックから構成されています。

https://github.com/databricks-industry-solutions/item-onboarding/tree/main

私がウォークスルーしたノートブックはこちらです。翻訳しています。

https://github.com/taka-yayoi/item-onboarding/tree/main

# 01-data-prep: データ準備

プロジェクトの開始にあたり、データの準備を行います。アイテムのオンボーディングシナリオでは、企業はさまざまな形式のデータを受け取ることがよくあります。最も一般的なケースの一部は、アイテムの色、説明、素材などのプロパティに関するデータを含むテキスト満載のCSVや、アイテムの写真です。

同様のシナリオをシミュレートできるように、類似のデータセットを探しました。[Amazon's Berkley Objects Dataset](https://amazon-berkeley-objects.s3.amazonaws.com/index.html)は、まさに私たちが探していたものです。これは、現実のシナリオで期待されるように、100%一貫していないアイテムに関するデータを特徴としています。また、製品に関する情報を抽出するためにビジョンモデルで使用できる画像も特徴としています。

このノートブックでは、環境を準備し、データをダウンロードして解凍し、後の段階で使用できるように保存します。

ここで推奨されるコンピュートは、最新のランタイムを備えたシングルノードのシンプルなマシンです。私たちは、`4 CPUコア`、`32 GBのRAMメモリ`、および`Runtime 15.4 LTS`を備えたマシンを使用しました。このノートブックではクラスターやGPUは必要ありません。

## コンテナの準備

ここでは、[Unity Catalog](https://docs.databricks.com/ja/data-governance/unity-catalog/index.html)を活用して、カタログとしてのコンテナと、テーブルを保存するためのスキーマ（データベース）を作成します。

また、このスキーマ内にファイルを保存するための[ボリューム](https://docs.databricks.com/ja/sql/language-manual/sql-ref-volumes.html)を作成します。ボリュームは、CSVや画像のような実際のファイルを保存するのに適したハードドライブのようなストレージ場所と考えることができます。

```sql
%sql
-- このノートブックでは既存のカタログをデフォルトで使用します
USE CATALOG takaakiyayoi_catalog;
-- 新しいカタログが必要な場合: CREATE CATALOG IF NOT EXISTS xyz;

-- テーブルを保持するためにそのカタログ内にスキーマを作成します
CREATE SCHEMA IF NOT EXISTS item_onboarding;

-- このノートブックのすべての操作にデフォルトでこのスキーマを使用します
USE SCHEMA item_onboarding;

-- ファイルを保持するためのボリュームを作成します
CREATE VOLUME IF NOT EXISTS landing_zone;
```

## データのダウンロード

このセクションでは、シェルスクリプトを使用してデータをダウンロードし、先ほど作成したボリュームに保存します。

### 表形式データのダウンロード

まず、表形式データから始めます。シェルスクリプトには、ダウンロードしたデータを解凍する部分も含まれています。これは、Sparkでデータを読み取る前に必要です。

```sh
%sh

# ターゲットボリュームディレクトリに移動
cd /Volumes/takaakiyayoi_catalog/item_onboarding/landing_zone

# リスティングファイルをダウンロード
echo "リスティングをダウンロード中"
wget -q https://amazon-berkeley-objects.s3.amazonaws.com/archives/abo-listings.tar

# リスティングファイルを解凍
echo "リスティングを解凍中"
tar -xf ./abo-listings.tar --no-same-owner
gunzip ./listings/metadata/*.gz

echo "完了"
```

### 画像のダウンロード

画像のダウンロードは少し異なります。同じ手順の一部に従いますが、ボリュームへの移動部分が異なります。また、データを直接ボリュームにダウンロードするのではなく、ここではSparkドライバーの一時メモリを使用して操作を実行します。

それは、多くの小さなファイル（画像など）がある場合、ボリュームの場所よりもメモリ内で解凍する方が速いためです。

```sh
%sh

# 一時ディレクトリを作成
mkdir /tmp_landing_zone

# ターゲットディレクトリに移動
cd /tmp_landing_zone

# 画像ファイルをダウンロード
echo "画像をダウンロード中"
wget -q https://amazon-berkeley-objects.s3.amazonaws.com/archives/abo-images-small.tar

# 画像ファイルを解凍
# (imagesというフォルダに解凍される)
echo "画像を解凍中"
tar -xf ./abo-images-small.tar --no-same-owner
gzip -df ./images/metadata/images.csv.gz

echo "完了"
```

**画像コピーのトリック**

少数の大きなファイルを扱う場合、通常のDatabricksユーティリティを使用してファイルをコピーするのは非常に便利ですが、ここでのように多数の小さなファイルを扱う場合にはそれほど速くありません。これは、画像を扱うシナリオで発生することがあります。そのため、スレッド化されたコピーを行う小さなユーティリティを作成しました。

このユーティリティは、ドライバのメモリから指定したボリュームパスに解凍した画像をコピーするために使用されます。通常のバージョンを使用する場合に比べて約150倍速く動作します。

```py
# Standard Imports
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# External Imports
from tqdm import tqdm


# TODO: 最適なスレッド数を確認する
def threaded_dbutils_copy(source_directory, target_directory, n_threads=10):
  """
  スレッドを使用してソースディレクトリをターゲットディレクトリにコピーします。
  
  この関数はスレッドを使用して複数のコピーコマンドを実行し、コピー処理を高速化します。
  特に画像のような小さなファイルが多数ある場合に便利です。
  
  :param source_directory: ファイルがコピーされる元のディレクトリ
  :param target_directory: ファイルがコピーされる先のディレクトリ
  :param n_threads: 使用するスレッド数。数が多いほどプロセスが速くなります。
  
  注意事項
    - パスの末尾にバックスラッシュを含めないでください。
    - n_threadsを増やすとドライバに負荷がかかるため、メトリクスを監視してドライバが過負荷にならないようにしてください。
    - 100スレッドは適切なドライバに適度な負荷をかけます。
  """
  
  print("すべてのパスをリストしています")
  
  # すべてのファイルのための空のリストを作成
  all_files = []
  
  # すべてのファイルを発見するための再帰的な検索関数
  # TODO: これをジェネレータに変える
  def recursive_search(_path):
    file_paths = dbutils.fs.ls(_path)
    for file_path in file_paths:
      if file_path.isFile():
        all_files.append(file_path.path)
      else:
        recursive_search(file_path.path)
  
  # ソースディレクトリに再帰的な検索を適用
  recursive_search(source_directory)
  
  # パス文字列のフォーマット
  all_files = [path.split(source_directory)[-1][1:] for path in all_files]
  
  n_files = len(all_files)
  print(f"{n_files} ファイルが見つかりました")
  print(f"{n_threads} スレッドでコピーを開始します")
  
  # 進行状況バーを作成するためのスレッドロックを使用してTQDMを初期化
  p_bar = tqdm(total=n_files, unit=" コピー")
  bar_lock = Lock()
  
  # 単一スレッドで実行される作業を定義
  def single_thread_copy(file_sub_path):
    dbutils.fs.cp(f"{source_directory}/{file_sub_path}", f"{target_directory}/{file_sub_path}")
    with bar_lock:
      p_bar.update(1)
  
  # すべてのパスにスレッド作業をマッピング
  with ThreadPoolExecutor(max_workers=n_threads, thread_name_prefix="copy_thread") as ex:
    ex.map(single_thread_copy, all_files)
  
  # 進行状況バーを閉じる
  p_bar.close()
  
  print("コピー完了")
  return
```

```py
# パスを指定
source_dir = "file:/tmp_landing_zone"
target_dir = "/Volumes/takaakiyayoi_catalog/item_onboarding/landing_zone/"

# コピーを実行
threaded_dbutils_copy(
  source_directory=source_dir, 
  target_directory=target_dir, 
  n_threads=150 # 同時に実行するスレッド数はどれくらいにしますか？ 数を増やすことを恐れないでください。
)
```

## 生データの読み込みと保存

生データをボリュームの場所に移動したので、それを読み込んでDeltaテーブルとして保存できます。

```py
# データを読み込む
products_df = (
    spark.read.json("/Volumes/takaakiyayoi_catalog/item_onboarding/landing_zone/listings/metadata")
)

# スキーマを上書きして生データを保存
(
    products_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.products_raw")
)

# display(products_df)
```

```py
# インポート
from pyspark.sql import functions as SF

# データを読み込む
image_meta_df = (
  spark
      .read
      .csv(
        path="/Volumes/takaakiyayoi_catalog/item_onboarding/landing_zone/images/metadata",
        sep=',',
        header=True
    ) 
)

# 画像データを保存
(
    image_meta_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.image_meta_raw")
)
```

## 基本的なクリーニング

テキストベースのデータにはいくつかのネストされた部分があります。基本的なクリーニングと抽出を行い、使用可能な形式に変換します。

```py
# インポート
from pyspark.sql import functions as SF

# データを読み込む
products_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.products_raw")


# 標準カラムから値を抽出する関数を作成
def value_extractor(df, target_col, sep=""):
    df = (
        df
        .withColumn(
            target_col,
            SF.expr(
                f"""concat_ws('{sep} ', filter({target_col}, x -> x.language_tag in ("en_US")).value)"""
            ),
        )
    )
    return df


# US製品に焦点を当てた変換データフレームを作成
products_clean_df = products_df.filter(SF.col("country").isin(["US"]))

# 変換を適用
transformation_columns = [
    ("brand", ""),
    ("bullet_point", ""),
    ("color", ""),
    ("item_keywords", " |"),
    ("item_name", ""),
    ("material", " |"),
    ("model_name", ""),
    ("product_description", ""),
    ("style", ""),
    ("fabric_type", ""),
    ("finish_type", ""),
]

for row in transformation_columns:
    products_clean_df = value_extractor(products_clean_df, row[0], row[1])

# メタカラムを指定
meta_columns = [
    ### メタ
    "item_id",
    "country",
    "main_image_id",
]

transformed_columns = []
for row in transformation_columns:
    transformed_columns.append(row[0])

in_place_transformed_columns = [
    ### インプレース変換
    "product_type.value[0] AS product_type",
    "node.node_name[0] AS node_name",
]


# カラム変換と選択を適用
products_clean_df = products_clean_df.selectExpr(
    meta_columns + transformed_columns + in_place_transformed_columns
)

# item_idに基づいて重複を削除
products_clean_df = products_clean_df.dropDuplicates(["item_id"])

# クリーンな製品データを保存
(
    products_clean_df.write.mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.products_clean")
)
```

## 画像メタデータの補強

次に、画像のメタデータを画像のパスで補強します。これにより、後で製品とメイン画像IDのパスを簡単に一致させることができます。

```py
from pyspark.sql import functions as SF

# データフレームを読み込む
products_clean_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.products_clean")
image_meta_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.image_meta_raw")

# メイン画像IDで強化
image_meta_enriched_df = image_meta_df.join(
    products_clean_df.selectExpr("main_image_id AS image_id", "item_id"),
    on="image_id",
    how="left",
)

# 実際のパスを構築
real_path_prefix = "/Volumes/takaakiyayoi_catalog/item_onboarding/landing_zone/images/small/"
image_meta_enriched_df = image_meta_enriched_df.withColumn(
    "real_path", 
    SF.concat(
        SF.lit(real_path_prefix),  # 文字列をリテラルに変換
        SF.col('path')
    )
)

# 保存
(
    image_meta_enriched_df.write.mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.image_meta_enriched")
)
```

## サンプルとテストデータの作成

速度と再現性のために、100アイテムに焦点を当てることにします。これにより、データのバッチをタイムリーに処理し、結果を再現するのにも役立ちます。ただし、プロジェクトを大規模に実行したい場合は、制限数を100からより大きな数に変更するか、制限文をコメントアウトしてフルスケールで実行してください。

```py
# テスト用に限定された数の製品を取得
sample_df = (
    spark.read.table("takaakiyayoi_catalog.item_onboarding.products_clean")
    .select("item_id")
    .limit(100)  # 必要に応じて増やすかコメントアウトしてください。
)

# テスト用に限定された数の製品を保存
(
    sample_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.sample")
)
```
```py
# クリーンな製品サンプル
products_clean_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.products_clean")
sample_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.sample")
sampled_products_clean_df = sample_df.join(products_clean_df, on="item_id", how="left")

# 保存
(
    sampled_products_clean_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.products_clean_sampled")
)
```

```py
# サンプル画像
image_meta_enriched_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.image_meta_enriched")
sample_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.sample")
sampled_image_meta_enriched_df = sample_df.join(image_meta_enriched_df, on="item_id", how="left")

# 保存
(
    sampled_image_meta_enriched_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.image_meta_enriched_sampled")
)
```

これでデータ準備ノートブックが完了です。次のノートブックでは、サンプリングされたテーブルと、Volumeに保存した画像を使用して情報抽出を開始します。

# 02-download-models: モデルウェイトのダウンロード

私たちは、オープンソースのLLAMAモデルを使用します。これらは、A100 GPUに快適に収まり、優れたパフォーマンスを持ち、簡単に仕事をこなすことができます。

プロジェクトで活用する2つのLLAMAモデルは次のとおりです：

- [LLAMA 3.2 11B Vision Model](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct)
- [LLAMA 3.1 8B Instruct Model](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)

ビジョンモデルはアイテムの画像から情報を抽出するために使用され、インストラクトモデルはテキストベースのクエリに使用されます。

ここでモデルウェイトをダウンロードする理由は、そうしないと、このワークフローを実行するたびにウェイトをダウンロードする必要があるためです。ダウンロードには数時間かかるわけではありませんが、毎回5〜10分を節約できれば、長期的には大きな節約になります。既存の場所からモデルウェイトをロードする方が効率的です。

モデルをダウンロードするためにHuggingFaceを使用します。LLAMAモデルはウェブサイトでの簡単な登録が必要です。登録が完了したら、[トークンを生成](https://huggingface.co/settings/tokens)し、それをワークフローの残りの部分で使用します。

huggingfaceパッケージはすでにランタイムにインストールされているため、再インストールする必要はありません。

データ準備ノートブックと同様に、ここではシングルノードコンピュートを使用できます。この時点ではクラスターやGPUは必要ありません。`4 CPU`と`32 GB RAMメモリ`を持ち、`15.4 ML LTS`ランタイムを実行しているマシンで十分です。ただし、**MLランタイムは必要です**。

## コンテナの作成

データ準備段階で行ったように、モデルウェイトを保存するためのボリュームロケーションを作成します。この場合、ロケーションをmodelsと呼びます。

```py
%sql
-- Use this catalog by default
USE CATALOG takaakiyayoi_catalog;

-- Use this schema by default
USE SCHEMA item_onboarding;

-- Create a volume if it doesnt exist
CREATE VOLUME IF NOT EXISTS models;
```

## 画像モデルのダウンロード

次に、シェルスクリプトを作成して画像モデルのウェイトをダウンロードします。ダウンロードの進行状況を追跡したい場合は、--quietフラグを削除できます。

```sh
%sh

# HFトークンをエクスポート
export HF_TOKEN="HFトークン"

# ダウンロードコマンドを実行
huggingface-cli \
  download \
  "meta-llama/Llama-3.2-11B-Vision-Instruct" \
  --local-dir "/Volumes/takaakiyayoi_catalog/item_onboarding/models/llama-32-11b-vision-instruct" \
  --exclude "original/*" \ # このフォルダ内の統合された重みは必要ありません
  --quiet # モデルのダウンロード進行状況を追跡したい場合はこれを削除
```

## テキストモデルのダウンロード

画像モデルと同様に、テキストモデルのウェイトもダウンロードします。

```py
%sh

# HFトークンをエクスポート
export HF_TOKEN="HFトークン"

# ダウンロードコマンドを実行
huggingface-cli \
  download \
  "meta-llama/Meta-Llama-3.1-8B-Instruct" \
  --local-dir "/Volumes/takaakiyayoi_catalog/item_onboarding/models/llama-31-8b-instruct" \
  --exclude "original/*" \ # このフォルダ内の統合された重みは必要ありません
  --quiet # モデルのダウンロード進行状況を追跡したい場合はこれを削除
```

# 03-image-analysis: 画像分析

データとモデルの準備が整ったので、画像分析を開始できます。このセクションでは、製品画像から有用な情報を抽出することが主な目標です。データからわかることは、商品の説明が明確でない場合や、サプライヤーが製品の色などの情報を提供し忘れることがあるということです。

製品の画像があるので、前のノートブックでダウンロードしたビジュアルモデルを使用して、アイテムの画像からこの情報を抽出するフローを構築することに焦点を当てます。

ビジュアルモデルはシンプルな方法で動作します。画像と「画像内のアイテムを説明してください」といったプロンプトを提供すると、テキストが返されます。

このノートブックでは、GPUが搭載されたマシンを使用します。`NVIDIA A100` GPUは、使用するモデルに十分なGPUメモリ（約80 GB）があるため、非常に適しています。Azureでは、`NC24_ads`がコンピュートの良い選択肢となります。

また、必要なパッケージがインストールされている`15.4 ML GPU`ランタイムを使用します。

## セットアップ

モデルを実行するために必要なtransformersライブラリをアップグレードする基本的なセットアッププロセスから始めます。

```sh
%sh
pip install --upgrade transformers -q
```
```
# インストール後に Python を再起動することが重要であり、このコードはインストール後に別のセルで実行する必要があります
dbutils.library.restartPython()
```
```sql
%sql
-- このノートブックでは既存のカタログをデフォルトで使用します
USE CATALOG takaakiyayoi_catalog;

-- このノートブックのすべての操作にデフォルトでこのスキーマを使用します
USE SCHEMA item_onboarding;

-- ファイルを保持するためのボリュームを作成します
CREATE VOLUME IF NOT EXISTS interim_data;
```

## 画像の読み込み

画像パスがデータフレームにリストされています。これを使用して実際の画像を読み込むことができます。以下のコードは、画像パスを持つデータフレームを読み込み、それをリストに変換します。後でこのリストを使用して画像を読み込みます。

```py
# 画像パスのテーブルを取得し、すべての画像のリストを作成
image_meta_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.image_meta_enriched_sampled")
image_meta_df = image_meta_df.select("real_path")

# 収集してリストを作成
image_paths = image_meta_df.collect()
image_paths = [x.real_path for x in image_paths if x.real_path]
```

単一の画像がどのように見えるか確認してみましょう。

```py
from PIL import Image
img = Image.open(image_paths[0])
img
```
![download.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a1fa14ef-7801-fe6e-233a-04a722bab3d3.png)

## インタラクティブプログラミング

次に、モデルを使用してインタラクティブなプログラミングとプロンプトを行うためのインターフェースを設計します。この部分では、GPU上のワークフローをより良く管理するのに役立つ[RAY](https://www.ray.io/)フレームワークを使用し始めます。RayはGPUベースのワークフローを実行するのに優れており、Databricksプラットフォーム上で非常にスムーズに動作します。

まず、RayのActor機能を使用して、モデルをGPUにActorとしてロードします。Actorの良い点は、好きなときに呼び出せることで、インタラクティブなプログラミングに役立ちます。指定しない限り、GPUからアンロードされません。

ここでの推奨事項として、コンピュートのWebターミナル（Databricks経由）にアクセスできる場合、このセクションを進める際にGPUのメモリと利用状況を確認すると非常に興味深いかもしれません。Webターミナルを開き、次のシェルコマンドを入力することで確認できます：

```sh
apt-get update
apt install nvtop
nvtop
```

これは、リアルタイムでお使いのGPUを監視する助けとなるユーティリティを実行します。

```py
# 必要なライブラリをインポート
from PIL import Image

from transformers import MllamaForConditionalGeneration, MllamaProcessor
import transformers

import ray
import torch

# Rayを初期化
ray.init(ignore_reinit_error=True)

# モデルが保存されているパスを指定（Volumeディレクトリ）
model_path = "/Volumes/takaakiyayoi_catalog/item_onboarding/models/llama-32-11b-vision-instruct"


# RAYアクターを定義

@ray.remote(num_gpus=1)
class LlamaVisionActor:
    def __init__(self, model_path: str):
        # モデルパスを登録
        self.model_path = model_path

        # コンフィグとモデルをロード
        self.model = MllamaForConditionalGeneration.from_pretrained(
            model_path,
            device_map="cuda:0",
            torch_dtype=torch.float16,
        )
        self.processor = MllamaProcessor.from_pretrained(model_path)

        # モデルをデバイスに移動
        self.model.to("cuda:0")
        self.model.eval()

    def generate(self, prompt, batch, max_new_tokens=128):

        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]}
        ]

        input_text = self.processor.apply_chat_template(messages, add_generation_prmpt=True)
        outputs = []
        for item in batch["image"]:
            image = Image.fromarray(item)
            inputs = self.processor(
                image,
                input_text,
                add_special_tokens=False,
                return_tensors="pt"
            ).to(self.model.device)
            output = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            output = self.processor.decode(output[0])
            outputs.append(output)

        return outputs


vision_actor = LlamaVisionActor.remote(model_path)
```

画面右下のターミナルボタンをクリックし、上のシェルコマンドを実行するとリアルタイムでGPUをモニタリングできるようになります。

![Screenshot 2025-02-07 at 13.11.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5941533f-7040-9af2-108a-99b79dbd19a5.png)

## 説明プロンプト
GPUがメモリにロードされたので、いくつかのプロンプトを試してみましょう。まず、RAYを使用していくつかの画像をロードする必要があります。その後、基本的な説明プロンプトを使用して、モデルに画像に何が写っているかを説明させます。プロンプトに変更を加えたい場合、ほぼプロンプトエンジニアリングに似た方法で、このインターフェースを使用してテストすることができます。

```py
# 画像を読み込む
images_df = ray.data.read_images(
    image_paths,
    include_paths=True,
    mode="RGB"
)

# 10枚の画像のバッチを作成
test_batch = images_df.take_batch(10)
```

```py
# 説明プロンプトを書く
prompt = "画像の中の製品を説明してください"

# アクターを使用して結果を生成
results = ray.get(
    vision_actor.generate.remote(
        prompt=prompt,
        batch=test_batch,
        max_new_tokens=256,
    )
)
```

この時点で結果が出たので、確認してみましょう。

```py
# 最初の結果を表示し、ヘッダーとターン終了トークンを削除
display(results[0].split("<|start_header_id|>assistant<|end_header_id|>")[1].split("<|eot_id|>")[0].strip())

# 画像も表示
img = Image.fromarray(test_batch["image"][0])
display(img)
```

```
'画像の中の製品は、カンドルホルダーのような小さな照明器具です。画像の中には、2個の製品が表示されており、どちらも同じデザインです。製品は、丸い形状をしており、内側の部分はガラスで、外側の部分は鉄でできています。ガラスの内側に、黒いテラコッタのカンドルが収まります。製品は、鉄の鎖によって吊り下げられており、下部には、平たく丸い形状をした鉄の台があります。画像の中では、製品の色は、黒です。製品は、明るい背景の下に写されており、製品の影が、下部に描かれています。'
```
![download (1).png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7de17bec-3fff-d274-8f70-5e48d5d90418.png)

## カラープロンプト

同様のフローを試すことができますが、今回はデータセット内の一部の製品に色フィールドが欠けているため、製品の色を抽出することを目指します。

コードフローは同じで、プロンプトの変更のみです。

```py
# 説明プロンプトを書く
prompt = "製品の色は何ですか？"

# アクターを使用して結果を生成
color_results = ray.get(
    vision_actor.generate.remote(
        prompt=prompt,
        batch=test_batch,
        max_new_tokens=32,
    )
)
```
```py
# 最初の結果を表示し、ヘッダーとターン終了トークンを削除
display(color_results[1].split("<|start_header_id|>assistant<|end_header_id|>")[1].split("<|eot_id|>")[0].strip())

# 画像も表示
img = Image.fromarray(test_batch["image"][1])
display(img)
```
```
'製品の色は白です。'
```
![download (2).png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9c66b323-06e3-43c3-1bf1-2199346718b2.png)

製品画像についてさらに質問したり、情報を抽出したりしたい場合は、ここでテストすることができます。インタラクティブな作業が完了したので、RayをシャットダウンしてGPUとアクターをアンロードできます。次のセクションでは、バッチ推論に焦点を当て始めます。

```py
ray.shutdown()
```

## 推論ロジックの定義

プロンプトが画像に対してどのように機能するかをほぼ理解したので、バッチ推論ロジックを定義することができます。アクターを使用することも適用可能な解決策でしたが、Rayの`map_batches` APIを使用することで、スケールで実行したい場合にバッチ推論をよりよく制御できます。

推論ロジックのコードは部分的にアクターのコードと非常に似ていますが、バッチモードで実行するために設計するクラスには、`__init__`と`__call__`の2つのメソッドを構築する必要があります。

`__init__`メソッドは、ここでのアクターのものとほぼ同じになります。バッチ推論を開始するときに一度呼び出されます。

`__call__`メソッドは、クラスがインスタンス化されたときに呼び出されるものです。

以下の設計はこれらのルールに従い、バッチ推論のためのモデルを準備します。

```py
# Imports
from transformers import MllamaForConditionalGeneration, MllamaProcessor
import transformers
from PIL import Image
import torch
import ray


class LlamaVisionPredictor:
    def __init__(self, model_path: str):
        # モデルパスを登録
        self.model_path = model_path

        # コンフィグとモデルをロード
        self.model = MllamaForConditionalGeneration.from_pretrained(
            model_path,
            device_map="cuda:0",
            torch_dtype=torch.float16,
        )
        self.processor = MllamaProcessor.from_pretrained(model_path)

        # モデルをデバイスに移動
        self.model.to("cuda:0")
        self.model.eval()

    def __call__(self, batch):
        # すべての推論ロジックはここに記述
        batch["description"] = self.generate(
            prompt="画像内の製品を100文字以内で説明してください。",
            batch=batch,
            max_new_tokens=256,
        )

        batch["color"] = self.generate(
            prompt="画像内の製品の色を10文字以内で返してください。",
            batch=batch,
            max_new_tokens=128,
        )

        return batch

    def generate(self, prompt, batch, max_new_tokens=128):

        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]}
        ]

        input_text = self.processor.apply_chat_template(messages, add_generation_prmpt=True)
        outputs = []
        for item in batch["image"]:
            image = Image.fromarray(item)
            inputs = self.processor(
                image,
                input_text,
                add_special_tokens=False,
                return_tensors="pt"
            ).to(self.model.device)
            output = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            output = self.processor.decode(output[0])
            outputs.append(output)

        return outputs
```

## 推論の実行

クラスの準備が整ったので、バッチ推論を開始できます。

画像を同じ方法でロードしますが、上記のように、ロードされたデータセットで`map_batches`機能を使用します。

```py
# Rayをインポート
import ray

# Rayを初期化
ray.init(ignore_reinit_error=True)

# モデルパスを指定
model_path = "/Volumes/takaakiyayoi_catalog/item_onboarding/models/llama-32-11b-vision-instruct"

# 画像を読み込む
image_analysis_df = ray.data.read_images(
    image_paths,
    include_paths=True,
    mode="RGB"
)

# バッチをマップ
image_analysis_df = image_analysis_df.map_batches(
        LlamaVisionPredictor,
        concurrency=1,  # LLMインスタンスの数
        num_gpus=1, # LLMインスタンスごとのGPU数
        batch_size=10, # バッチサイズ
        fn_constructor_kwargs={"model_path": model_path,},
)

# 評価
image_analysis_df = image_analysis_df.materialize()

# 画像解析の保存先を決定
save_path = "/Volumes/takaakiyayoi_catalog/item_onboarding/interim_data/image_analysis"

# ディレクトリをクリア
#dbutils.fs.rm(save_path, recurse=True)

# 保存
image_analysis_df.write_parquet(save_path)
```

## 例を一つ表示

バッチ予測の結果も確認してみましょう。

```py
# 例を表示
single_example = image_analysis_df.take(1)[0]

print(single_example["description"].split("<|start_header_id|>assistant<|end_header_id|>")[1].split("<|eot_id|>")[0].strip())
print(single_example["color"].split("<|start_header_id|>assistant<|end_header_id|>")[1].split("<|eot_id|>")[0].strip())

image = Image.fromarray(single_example["image"])
image
```

```
画像内の製品は、室内で使用することができる、外用のテーブルチェアです。テーブルチェアは、座りやすい高さのテーブルに、座れるスペースが設けられたものです。テーブルチェアは、レストランやカフェなどで、客が座って食事を楽しむのに使用されることが多いですが、現在では、家庭での使用も増えています。

テーブルチェアは、テーブルと同じように、椅子と呼ばれることもあります。テーブルチェアは、テーブルと同様に、テーブルチェアとテーブルを合わせて、テーブルセットと呼ばれることもあります。テーブルセットは、テーブルと椅子（テーブルチェア）を合わせて、テーブルと椅子を合わせたものです。テーブルセットは、レストランやカフェなどで、客が座って食事を楽しむのに使用されることが多いですが、現在では、家庭での使用も増えています。テーブルセットは、テーブルと椅子を合わせたもので、テーブルセットは、テーブルと椅子を合わせたものです。
製品の色は、茶色、白色、木目色です。
```
![download (3).png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/aca5c2a8-c033-8940-1dcb-4dce8377f153.png)

## Rayのシャットダウン

画像分析が完了したので、RAYをシャットダウンしても構いません。

```py
# Shutdown Ray
ray.shutdown()
```

# 04-text-analysis: テキスト分析

前のセクションで画像分析を完了し、観察された説明や観察された色などのデータポイントを得ました。次に、テキストベースのLLMモデルを使用して、すべてのテキストを整理します。

このノートブックの目標は、サプライヤーから提供された情報やワークフローを通じて収集されたすべての情報を考慮して、最終的な説明や最終的な色などのテキストポイントを作成することです。

コードに関しては、[vLLM](https://docs.vllm.ai/en/latest/)を除いて非常に似たフローに従います。VLLMは、実行時にモデルを最適化するのに役立つ非常に人気のあるライブラリです。ほとんどすべてのSOTAオープンソースモデルと連携します。実際、ビジョンモデル用の実験的なアプリケーションもありますが、まだ本番環境には対応していないため、前のノートブックでは使用しませんでした。

vLLMを使用する場合、特にモデルを呼び出すポイントでコードの設計が若干異なりますが、Rayを中心とした他の部分はほぼ同じです。

ここでも同様のフローに従い、最初にプロンプトを使ったインタラクティブなテストを行い、その後バッチ推論のための必要なフローを設計します。

## ライブラリのインストール

必要なライブラリ、transformersとvllmをインストールします。

```py
# 必要なライブラリをインストールするためのコード
%pip install --upgrade transformers -q
%pip install vllm -q
```

```py
# この操作は、上記のライブラリインストールセルとは別のセルで行う必要があります
dbutils.library.restartPython()
```

## デフォルトの設定

デフォルトのUnity Catalogとスキーマを指定し、中間データを保存するためのボリュームと、オンボーディングdfを保持するパスを作成します。

```sql
%sql
-- デフォルトの定義
USE CATALOG takaakiyayoi_catalog;
USE SCHEMA item_onboarding;
-- 一時データの保存場所を作成
CREATE VOLUME IF NOT EXISTS interim_data;
```

## 中間データの構築

サプライヤーから取得したデータポイントと、ビジュアルモデルから取得したデータポイントをすべて取り込み、それらを結合してテキストベースのワークフローで使用できるようにする必要があります。

RayがDatabricksのボリュームからParquetファイルを取得する方が簡単なので、セルの最後に、最終的な中間データフレームをボリュームにParquet形式で保存します。

```py
from pyspark.sql import functions as SF

# 処理対象のテーブルをparquet形式で構築
products_clean_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.products_clean_sampled")
image_meta_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.image_meta_enriched_sampled")
image_analysis_df = spark.read.parquet("/Volumes/takaakiyayoi_catalog/item_onboarding/interim_data/image_analysis")

# 基本的な変換
image_analysis_df = (
    image_analysis_df
    .drop("image")
    .selectExpr([
        "path AS real_path", 
        "description AS gen_description", 
        "color AS gen_color",
    ])
)

# 生成された説明と色のテキストをクリーンアップ
pattern = r"assistant<\|end_header_id\|>\s*([\s\S]*?)<\|eot_id\|>"
image_analysis_df = (
    image_analysis_df
    .withColumn("gen_description", SF.regexp_extract("gen_description", pattern, 1))
    .withColumn("gen_color", SF.regexp_extract("gen_color", pattern, 1))
)

# 後で使用するために画像説明のエントリを準備
onboarding_df = (
    products_clean_df
    .join(image_meta_df, on="item_id", how="left")
    .join(image_analysis_df, on="real_path", how="left")
)

# 指定された場所にparquet形式で保存
(
    onboarding_df
    .write
    .mode("overwrite")
    .parquet(onboarding_df_path)
)
# display(onboarding_df)
```

## ターゲット製品分類の構築

このセクションでは、小売業者がカタログのために事前定義された分類法を持っているシナリオをシミュレートしたいと考えました。後のタスクは、この分類法の中にアイテムを配置することです。これは通常、小売業者が製品を分類するのに役立ちます。そこで、実際のような分類法を生成し、モデルがそれでどのように機能するかを確認しようと考えました。

```py
product_taxonomy = """- 家具・家庭用品 - 椅子
- 家具・家庭用品 - テーブル
- 家具・家庭用品 - ソファ・カウチ
- 家具・家庭用品 - キャビネット、ドレッサー、ワードローブ
- 家具・家庭用品 - ランプ・照明器具
- 家具・家庭用品 - 棚・本棚
- フットウェア・アパレル - 靴
- フットウェア・アパレル - 衣類
- フットウェア・アパレル - アクセサリー
- キッチン・ダイニング - 調理器具
- キッチン・ダイニング - 食器
- キッチン・ダイニング - カトラリー・調理器具
- キッチン・ダイニング - 収納・整理
- ホームデコ・アクセサリー - 花瓶・装飾用ボウル
- ホームデコ・アクセサリー - 写真立て・壁掛けアート
- ホームデコ・アクセサリー - 装飾用クッション・スロー
- ホームデコ・アクセサリー - ラグ・マット
- 家電 - ヘッドホン・イヤホン
- 家電 - ポータブルスピーカー
- 家電 - キーボード、マウス、その他周辺機器
- 家電 - 携帯電話ケース・スタンド
- オフィス・文房具 - デスクオーガナイザー・ペンホルダー
- オフィス・文房具 - ノート・ジャーナル
- オフィス・文房具 - ペン、鉛筆、マーカー
- オフィス・文房具 - フォルダー、バインダー、ファイルオーガナイザー
- パーソナルケア・アクセサリー - ウォーターボトル・タンブラー
- パーソナルケア・アクセサリー - メイクブラシ・ヘアアクセサリー
- パーソナルケア・アクセサリー - パーソナルグルーミングツール
- おもちゃ・レジャー - アクションフィギュア・人形
- おもちゃ・レジャー - ブロック・建設セット
- おもちゃ・レジャー - ボードゲーム・パズル
- おもちゃ・レジャー - ぬいぐるみ"""
```

## インタラクティブモデルとプロンプトの構成

これからテキストモデルを使ったインタラクティブな部分を始めます。ここでの目標は、モデルの動作をテストし、テキスト分析のためのプロンプトエンジニアリングを行うことです。

画像モデルで行った方法と同様に、アクターを作成します。ここでの違いは、vLLMライブラリを使用してモデルをロードすることです。vLLMは最適化されているため、モデルのロード（ボリュームからGPUメモリへの）や推論が高速化されることが期待できます。

```py
# インポート
from vllm import LLM, SamplingParams
import ray

# Rayの初期化
ray.init(ignore_reinit_error=True)

# モデルパスの指定
model_path = "/Volumes/takaakiyayoi_catalog/item_onboarding/models/llama-31-8b-instruct/"

# LLMをGPUにロード
@ray.remote(num_gpus=1)
class LLMActor:
    def __init__(self, model_path: str):
        # モデルの初期化
        self.model = LLM(model=model_path, max_model_len=2048)

    def generate(self, prompt, sampling_params):
        raw_output = self.model.generate(
            prompt, 
            sampling_params=sampling_params
        )
        return raw_output

# LLMアクターの作成 - この部分はモデルを非同期でGPUにロードします。
llm_actor = LLMActor.remote(model_path)
```

## プロンプトテクニック

私たちはLLAMA 3.1 8B instructモデルを使用しています。このモデルは、ベースモデルとは少し異なる特定の方法で呼び出されることを期待しています。この特別な方法では、プロンプトや指示を特別なトークンと事前設定された構造でフォーマットする必要があります。この構造では、システムプロンプトを受け取ることを期待しており、これはモデルに「あなたは役に立つアシスタントです」といったことを伝えます。指示についても同様です。これらのテキストは特別なトークンの前後に配置され、トークンは次のように見えます: `<|eot_id|>`。この技術に関する詳細は、[Metaのモデルドキュメント](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/prompt_format.md)を参照してください。

以下のセルでは、システムテキストと指示テキストを与えられた場合に、正しい形式でプロンプトを構築できる基本的な関数を作成します。

```py
# Llamaプロンプト形式
def produce_prompt(system, instruction):
    prompt = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{system}<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
        f"{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    )
    return prompt

test_prompt = produce_prompt("あなたは役に立つアシスタントです", "1週間は何日ですか")
print(test_prompt)
```
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
あなたは役に立つアシスタントです<|eot_id|><|start_header_id|>user<|end_header_id|>
1週間は何日ですか<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

次に、簡単なテストを行いましょう：

```py
# アクターを呼び出して、上記で作成した生成リクエストを実行
result = ray.get(llm_actor.generate.remote(test_prompt, SamplingParams(temperature=0.1)))

# 結果のフォーマット表示
print(result)

# 実際の結果オブジェクトは出力のリストなので、最初のものにアクセスする必要があります
print("\n")
print(result[0].prompt)
print("\n")
print(" ".join([o.text for o in result[0].outputs]).strip())
print("\n")
```
```
[RequestOutput(request_id=2, prompt='<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nあなたは役に立つアシスタントです<|eot_id|><|start_header_id|>user<|end_header_id|>\n1週間は何日ですか<|eot_id|><|start_header_id|>assistant<|end_header_id|>', prompt_token_ids=[128000, 128000, 128006, 9125, 128007, 198, 30591, 112568, 15682, 107734, 20230, 80195, 59739, 39880, 57207, 105335, 52414, 38641, 128009, 128006, 882, 128007, 198, 16, 111299, 56965, 15682, 99849, 9080, 112130, 128009, 128006, 78191, 128007], encoder_prompt=None, encoder_prompt_token_ids=None, prompt_logprobs=None, outputs=[CompletionOutput(index=0, text='\n\n7日です。', token_ids=(271, 22, 9080, 38641, 1811, 128009), cumulative_logprob=None, logprobs=None, finish_reason=stop, stop_reason=None)], finished=True, metrics=RequestMetrics(arrival_time=1738904833.680964, last_token_time=1738904833.773224, first_scheduled_time=1738904833.6819067, first_token_time=1738904833.7001126, time_in_queue=0.0009427070617675781, finished_time=1738904833.773319, scheduler_time=0.000608183000167628, model_forward_time=None, model_execute_time=None), lora_request=None, num_cached_tokens=0, multi_modal_placeholders={})]


<|begin_of_text|><|start_header_id|>system<|end_header_id|>
あなたは役に立つアシスタントです<|eot_id|><|start_header_id|>user<|end_header_id|>
1週間は何日ですか<|eot_id|><|start_header_id|>assistant<|end_header_id|>


7日です。


Processed prompts:   0%|          | 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/s, output: 0.00 toks/s]
```

私たちのモデルは動作しています。いくつかの実際の例でテストを開始しましょう。以下のセルで実際のデータセットを読み込みます。

```py
# データセットを読み込んでいくつかの例を取得
onboarding_ds = ray.data.read_parquet(onboarding_df_path)

# スキーマを表示
display(onboarding_ds.schema())
```
```
Column               Type
------               ----
real_path            string
item_id              string
country              string
main_image_id        string
brand                string
bullet_point         string
color                string
item_keywords        string
item_name            string
material             string
model_name           string
product_description  string
style                string
fabric_type          string
finish_type          string
product_type         string
node_name            string
image_id             string
height               string
width                string
path                 string
gen_description      string
gen_color            string
```

このデータセットから単一のレコードがどのように見えるかを確認しましょう。

```py
# レコードを1つ取得
single_record = onboarding_ds.take(2)[1]
print(single_record)
```
```
{'real_path': '/Volumes/takaakiyayoi_catalog/item_onboarding/landing_zone/images/small/1c/1c4e48da.jpg', 'item_id': 'B000050415', 'country': 'US', 'main_image_id': '41C4BSFPSTL', 'brand': 'LIDCO', 'bullet_point': "7 light party-patio light set for festive entertaining Natural bamboo shades measure 6 inches tall by 4 inches (at widest point ) Complete with bulbs and add-on connector (up to 3 set maximum) UL listed for indoor & outdoor use 14' long", 'color': '', 'item_keywords': '', 'item_name': 'Lidco L200 Electric Patio Party Lights, 7 Light Bamboo', 'material': '', 'model_name': '', 'product_description': '', 'style': '', 'fabric_type': '', 'finish_type': '', 'product_type': 'OUTDOOR_LIVING', 'node_name': '/Categories/Event & Party Supplies', 'image_id': '41C4BSFPSTL', 'height': '312', 'width': '500', 'path': '1c/1c4e48da.jpg', 'gen_description': '', 'gen_color': '製品の色は黄色です。'}
```

## 一般的なサンプリングパラメータ

サンプリングパラメータを使用してモデルの出力を調整できます。ここで調整できる引数は多数あります。例えば、温度の設定によって、モデルをより「創造的」にするか、より「指示に従う」ようにするかを決定できます。top_pやtop_kパラメータを変更することでトークン選択プロセスを調整したり、max_tokensを変更することでモデルが返す回答の長さを決定したりできます。詳細は[vLLMサンプリングパラメータ](https://docs.vllm.ai/en/stable/dev/sampling_params.html)をご覧ください。

```py
sampling_params = SamplingParams(
    n=1, # 与えられたプロンプトに対して返される出力シーケンスの数
    temperature=0.1, # サンプリングのランダム性。値が低いほどモデルは決定論的になり、値が高いほどモデルはランダムになります。ゼロは貪欲サンプリングを意味します。
    top_p=0.9, # 考慮するトップトークンの累積確率
    top_k=50, # 考慮するトップトークンの数
    max_tokens=256,  # 特定のタスクに基づいてこの値を調整します
    stop_token_ids=[128009], # 生成が行われたときに生成を停止する
    presence_penalty=0.1, # 生成されたテキストに既に登場しているかどうかに基づいて新しいトークンをペナルティ化します
    frequency_penalty=0.1, # 生成されたテキストにおける頻度に基づいて新しいトークンをペナルティ化します
    ignore_eos=False, # EOSトークンを無視して、EOSトークンが生成された後もトークンの生成を続けるかどうか
)
```

## 説明プロンプト

説明プロンプトを始めましょう。画像モデルによって生成された視覚的な説明と、サプライヤーから受け取った情報を元に、新しい説明を生成するようモデルに依頼します。

```py
# 推奨される説明 - システムプロンプト
description_system_prompt = "あなたは小売製品の専門ライターです。"

# 推奨される説明 - 指示プロンプト
description_instruction = """
以下に、製品の2つの説明があります。重要な詳細を捉えた自然で明確な説明（50語未満）を作成してください。

説明1: {bullet_point}
説明2: {gen_description}

新しい説明のみを出力してください。引用符や追加のテキストは不要です。
"""

# プロンプトに値を埋め込む
description_instruction = description_instruction.format(
    bullet_point=single_record["bullet_point"],
    gen_description=single_record["gen_description"],
)

# プロンプトをフォーマット
description_prompt = produce_prompt(
    system = description_system_prompt,
    instruction=description_instruction
    )

print(description_prompt)

result = ray.get(llm_actor.generate.remote(description_prompt, sampling_params))
suggested_description = " ".join([o.text for o in result[0].outputs]).strip()
print(suggested_description)
```
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
あなたは小売製品の専門ライターです。<|eot_id|><|start_header_id|>user<|end_header_id|>

以下に、製品の2つの説明があります。重要な詳細を捉えた自然で明確な説明（50語未満）を作成してください。

説明1: 7 light party-patio light set for festive entertaining Natural bamboo shades measure 6 inches tall by 4 inches (at widest point ) Complete with bulbs and add-on connector (up to 3 set maximum) UL listed for indoor & outdoor use 14' long
説明2: 

新しい説明のみを出力してください。引用符や追加のテキストは不要です。
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
Processed prompts:   0%|          | 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/s, output: 0.00 toks/s]
7点のパーティー用パティオライトセット。天然の竹製シャードは6インチ高さ×4インチ幅（最も広い部分）。内外どちらでも使用可能で、最大3セットまで追加接続可能。
```

## カラープロンプト

説明が準備できたので、モデルに製品の最適な色を生成するよう依頼しましょう。サプライヤーからのデータの一部には色のフィールドが欠けているため、視覚モデルからの入力が重要になります。

```py
# 推奨される色 - システムプロンプト
color_system_prompt = "あなたは色の専門アナリストです。"

# 推奨される色 - 指示プロンプト
color_instruction = """
以下を考慮してください:
- 製品の色: {color}
- ビジョンモデルの色: {gen_color}

色を返してください。追加のテキストは不要です。
"""


# プロンプトに値を埋め込む
color_instruction = color_instruction.format(
    color=single_record["color"],
    gen_color=single_record["gen_color"],
)

# プロンプトをフォーマット
color_prompt = produce_prompt(
    system = color_system_prompt,
    instruction=color_instruction
)

print(color_prompt)

result = ray.get(llm_actor.generate.remote(color_prompt, sampling_params))
suggested_color = " ".join([o.text for o in result[0].outputs]).strip()
print(suggested_color)
```

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
あなたは色の専門アナリストです。<|eot_id|><|start_header_id|>user<|end_header_id|>

以下を考慮してください:
- 製品の色: 
- ビジョンモデルの色: 製品の色は黄色です。

色を返してください。追加のテキストは不要です。
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
黄色
Processed prompts:   0%|          | 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/s, output: 0.00 toks/s]
```

## キーワードプロンプト

サプライヤーは検索最適化のために多数のキーワードも提供してくれますが、ここからもキーワードが複数回繰り返されたり、実際のアイテムと一致しなかったりする問題のあるデータポイントが出てきます。

この部分では、同じ形式を維持しながらキーワードを最適化することを目指します。

```py
# 推奨されるキーワード - システムプロンプト
keyword_system_prompt = "あなたはSEOと製品キーワードの専門家です。"

# 推奨されるキーワード - 指示プロンプト
keyword_instruction = """
入力:
- 現在のキーワード: {item_keywords}
- 製品説明: {suggested_description}
- 製品の色: {suggested_color}

新しいキーワードを|で区切って返してください。他のテキストは不要です。説明しないでください。
"""


# プロンプトをフォーマット
keyword_prompt = produce_prompt(
    system = keyword_system_prompt,
    instruction=keyword_instruction
)

# プロンプトに値を埋め込む
keyword_prompt = keyword_prompt.format(
    item_keywords=single_record["item_keywords"],
    suggested_description=suggested_description,
    suggested_color=suggested_color,
)


print(keyword_prompt)

result = ray.get(llm_actor.generate.remote(keyword_prompt, sampling_params))
suggested_keywords = " ".join([o.text for o in result[0].outputs]).strip()
print("\n")
print(suggested_keywords)
```
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
あなたはSEOと製品キーワードの専門家です。<|eot_id|><|start_header_id|>user<|end_header_id|>

入力:
- 現在のキーワード: 
- 製品説明: 7点のパーティー用パティオライトセット。天然の竹製シャードは6インチ高さ×4インチ幅（最も広い部分）。内外どちらでも使用可能で、最大3セットまで追加接続可能。
- 製品の色: 黄色

新しいキーワードを|で区切って返してください。他のテキストは不要です。説明しないでください。
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
Processed prompts:   0%|          | 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/s, output: 0.00 toks/s]


黄色|パーティー用|パティオライト|竹製シャード|室内外用|追加接続可能|最大3セット|6インチ高さ|4インチ幅|天然竹
Processed prompts: 100%|██████████| 1/1 [00:00<00:00,  1.34it/s, est. speed input: 198.91 toks/s, output: 64.51 toks/s]
```

そして、モデルはそれも成功裏に行うことができます！

## カテゴリープロンプト

最後に、これまで生成および修正したすべての情報をもとに、アイテムをノートブックの上部で作成したカテゴリのいずれかにモデルが配置します。

この部分では、モデルは前のセルから生成したテキストも使用します。

```py
# 推奨される分類 - システムプロンプト
taxonomy_system_prompt = "あなたは専門のマーチャンダイズ分類スペシャリストです。"

# 推奨される分類 - 指示プロンプト
taxonomy_instruction = """
製品説明を確認し、提供された分類から最も適切なカテゴリを選択してください。
製品説明: 
{suggested_description}

製品分類: 
{target_taxonomy}

最も適したカテゴリを1つだけ返してください。他のテキストは不要です。
"""

# プロンプトをフォーマット
taxonomy_prompt = produce_prompt(
    system = taxonomy_system_prompt,
    instruction=taxonomy_instruction
)

# プロンプトに値を埋め込む
taxonomy_prompt = taxonomy_prompt.format(
    suggested_description=suggested_description,
    target_taxonomy=product_taxonomy,
)

print(taxonomy_prompt)

result = ray.get(llm_actor.generate.remote(taxonomy_prompt, sampling_params))
suggested_category = " ".join([o.text for o in result[0].outputs]).strip()

print("\n")
print(suggested_category)
```
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
あなたは専門のマーチャンダイズ分類スペシャリストです。<|eot_id|><|start_header_id|>user<|end_header_id|>

製品説明を確認し、提供された分類から最も適切なカテゴリを選択してください。
製品説明: 
7点のパーティー用パティオライトセット。天然の竹製シャードは6インチ高さ×4インチ幅（最も広い部分）。内外どちらでも使用可能で、最大3セットまで追加接続可能。

製品分類: 
- 家具・家庭用品 - 椅子
- 家具・家庭用品 - テーブル
- 家具・家庭用品 - ソファ・カウチ
- 家具・家庭用品 - キャビネット、ドレッサー、ワードローブ
- 家具・家庭用品 - ランプ・照明器具
- 家具・家庭用品 - 棚・本棚
- フットウェア・アパレル - 靴
- フットウェア・アパレル - 衣類
- フットウェア・アパレル - アクセサリー
- キッチン・ダイニング - 調理器具
- キッチン・ダイニング - 食器
- キッチン・ダイニング - カトラリー・調理器具
- キッチン・ダイニング - 収納・整理
- ホームデコ・アクセサリー - 花瓶・装飾用ボウル
- ホームデコ・アクセサリー - 写真立て・壁掛けアート
- ホームデコ・アクセサリー - 装飾用クッション・スロー
- ホームデコ・アクセサリー - ラグ・マット
- 家電 - ヘッドホン・イヤホン
- 家電 - ポータブルスピーカー
- 家電 - キーボード、マウス、その他周辺機器
- 家電 - 携帯電話ケース・スタンド
- オフィス・文房具 - デスクオーガナイザー・ペンホルダー
- オフィス・文房具 - ノート・ジャーナル
- オフィス・文房具 - ペン、鉛筆、マーカー
- オフィス・文房具 - フォルダー、バインダー、ファイルオーガナイザー
- パーソナルケア・アクセサリー - ウォーターボトル・タンブラー
- パーソナルケア・アクセサリー - メイクブラシ・ヘアアクセサリー
- パーソナルケア・アクセサリー - パーソナルグルーミングツール
- おもちゃ・レジャー - アクションフィギュア・人形
- おもちゃ・レジャー - ブロック・建設セット
- おもちゃ・レジャー - ボードゲーム・パズル
- おもちゃ・レジャー - ぬいぐるみ

最も適したカテゴリを1つだけ返してください。他のテキストは不要です。
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
Processed prompts:   0%|          | 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/s, output: 0.00 toks/s]


キッチン・ダイニング - 調理器具
```

モデルはアイテムを正しいカテゴリに正常に配置します。

## GPUアンロード

バッチ推論の準備が整ったので、続行する前にRayをシャットダウンしてGPUをアンロードします。

```py
ray.shutdown()
```

## バッチ推論

モデルと対話的に作業し、プロンプトがモデルとどのように機能するかを理解したので、バッチ推論のフローを設定する時が来ました。

## Rayの初期化とデータの取得

Rayを再初期化し、バッチ推論のためのデータセットを取得します。

```py
# Imports
import ray

# Init ray
ray.init()

# データを取得
onboarding_ds = ray.data.read_parquet(onboarding_df_path)

# スキーマを確認
onboarding_ds.schema
```
```
<bound method Dataset.schema of Dataset(
   num_rows=100,
   schema={
      real_path: string,
      item_id: string,
      country: string,
      main_image_id: string,
      brand: string,
      bullet_point: string,
      color: string,
      item_keywords: string,
      item_name: string,
      material: string,
      model_name: string,
      product_description: string,
      style: string,
      fabric_type: string,
      finish_type: string,
      product_type: string,
      node_name: string,
      image_id: string,
      height: string,
      width: string,
      path: string,
      gen_description: string,
      gen_color: string
   }
)>
```

## 推論ロジック

推論の設計方法は、画像モデルで行った方法と非常に似ていますが、ここではvLLMを使用する点が異なります。

`__init__`メソッドと`__call__`メソッドを持つクラスを使用し、`__call__`メソッドが推論のフローを保持します。フローは重要で、最初のステップで生成された回答が後の段階で使用されるため、順序が必要です。

また、プロンプトのフォーマットなどを標準化するためのヘルパー関数も作成します。

```py
# Imports
from vllm import LLM, SamplingParams
import numpy as np


class OnboardingLLM:
    # クラスの構築
    def __init__(self, model_path: str, target_taxonomy: str):
        # モデルの初期化
        self.model = LLM(model=model_path, max_model_len=2048)
        self.target_taxonomy = target_taxonomy

    def __call__(self, batch):
        """各バッチで実行されるロジックを定義"""
        # すべての推論ロジックはここに入る
        batch = self.generate_suggested_description(batch)
        batch = self.generate_suggested_color(batch)
        batch = self.generate_suggested_keywords(batch)
        batch = self.generate_suggested_product_category(batch)
        return batch

    @staticmethod
    def format_prompt(system, instruction):
        """プロンプトのフォーマットを支援"""
        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            f"{system}<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f"{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )
        return prompt

    @staticmethod
    def standardise_output(raw_output):
        """各推論後の標準化された出力を返す"""
        generated_outputs = []
        for _ro in raw_output:
            generated_outputs.append(" ".join([o.text for o in _ro.outputs]))
        return generated_outputs

    @staticmethod
    def build_sampling_params(max_tokens=256):
        """推論のためのサンプリングパラメータを構築"""
        sampling_params = SamplingParams(
            n=1,
            temperature=0.1,
            top_p=0.9,
            top_k=50,
            max_tokens=max_tokens,  # 特定のタスクに基づいてこの値を調整
            stop_token_ids=[128009], # LLAMA 3.1 <|eot_id|>に特有
            presence_penalty=0.1,
            frequency_penalty=0.1,
            ignore_eos=False,
        )
        return sampling_params

    def generate_suggested_description(self, batch):
        # 推奨される説明 - システムプロンプト
        system_prompt = "あなたは小売製品の専門ライターです。"

        # 推奨される説明 - 指示プロンプト
        instruction = """
        以下は製品の2つの説明です。主要な詳細を捉えた自然で明確な説明（50語以内）を作成してください。

        説明1: {bullet_point}
        説明2: {gen_description}

        新しい説明のみを出力してください。引用符や追加のテキストは不要です。
        """

        # プロンプトを構築
        prompt_template = produce_prompt(system=system_prompt, instruction=instruction)
        prompts = np.vectorize(prompt_template.format)(
            bullet_point=batch["bullet_point"], gen_description=batch["gen_description"]
        )

        # サンプリングパラメータを構築
        sampling_params = self.build_sampling_params(max_tokens=256)

        # 推論
        raw_output = self.model.generate(prompts, sampling_params=sampling_params)

        # バッチに戻す
        batch["suggested_description"] = self.standardise_output(raw_output)

        return batch

    def generate_suggested_color(self, batch):
        # 推奨される色 - システムプロンプト
        system_prompt = "あなたは色の専門アナリストです。"

        # 推奨される色 - 指示プロンプト
        instruction = """
        製品の:
        - 説明された色: {color}
        - 観察された色: {gen_color}

        色を返してください。追加のテキストは不要です。
        """

        # プロンプトをフォーマット
        prompt_template = produce_prompt(system=system_prompt, instruction=instruction)
        prompts = np.vectorize(prompt_template.format)(
            color=batch["color"], gen_color=batch["gen_color"]
        )

        # サンプリングパラメータを構築
        sampling_params = self.build_sampling_params(max_tokens=16)

        # 推論
        raw_output = self.model.generate(prompts, sampling_params=sampling_params)

        # バッチに戻す
        batch["suggested_color"] = self.standardise_output(raw_output)

        return batch

    def generate_suggested_keywords(self, batch):
        # 推奨されるキーワード - システムプロンプト
        system_prompt = "あなたはSEOと製品キーワードの専門家です。"

        # 推奨されるキーワード - 指示プロンプト
        instruction = """
        入力:
        - 現在のキーワード: {item_keywords}
        - 製品説明: {suggested_description}
        - 製品の色: {suggested_color}

        新しいキーワードを|で区切って返してください。その他のテキストは不要です。説明しないでください。
        """

        # プロンプトをフォーマット
        prompt_template = produce_prompt(system=system_prompt, instruction=instruction)
        prompts = np.vectorize(prompt_template.format)(
            item_keywords=batch["item_keywords"],
            suggested_description=batch["suggested_description"],
            suggested_color=batch["suggested_color"],
        )

        # サンプリングパラメータを構築
        sampling_params = self.build_sampling_params(max_tokens=256)
        
        # 推論
        raw_output = self.model.generate(prompts, sampling_params=sampling_params)

        # バッチに戻す
        batch["suggested_keywords"] = self.standardise_output(raw_output)

        return batch
    
    def generate_suggested_product_category(self, batch):

        # 推奨されるカテゴリ - システムプロンプト
        system_prompt = "あなたは商品分類の専門家です。"

        # 推奨されるカテゴリ - 指示プロンプト
        instruction = """
        製品説明を確認し、提供された分類から最も適切なカテゴリを選択してください。
        製品説明: 
        {suggested_description}

        製品分類: 
        {target_taxonomy}

        最も適したカテゴリを1つだけ返してください。その他のテキストは不要です。
        """

        # プロンプトをフォーマット
        prompt_template = produce_prompt(system=system_prompt, instruction=instruction)
        prompts = np.vectorize(prompt_template.format)(
            suggested_description=batch["suggested_description"],
            target_taxonomy=self.target_taxonomy
        )

        # サンプリングパラメータを構築
        sampling_params = self.build_sampling_params(max_tokens=256)
        
        # 推論
        raw_output = self.model.generate(prompts, sampling_params=sampling_params)

        # バッチに戻す
        batch["suggested_category"] = self.standardise_output(raw_output)

        return batch
```

## 推論の実行

クラスの準備が整ったので、推論ロジックを実行しましょう！

結果を再びボリュームにParquetファイルとして保存し、次のノートブックで結果を確認します。

```py
# モデルパスを指定
model_path = "/Volumes/takaakiyayoi_catalog/item_onboarding/models/llama-31-8b-instruct/"

# データを取得
onboarding_ds = ray.data.read_parquet(onboarding_df_path)

# フローを実行
ft_onboarding_ds = onboarding_ds.map_batches(
    OnboardingLLM,
    concurrency=1,  # LLMインスタンスの数
    num_gpus=1,  # LLMインスタンスごとのGPU数
    batch_size=32,  # OOMになるまで最大化、OOMになったらbatch_sizeを減らす
    fn_constructor_kwargs={
        "model_path": model_path,
        "target_taxonomy": product_taxonomy,
    },
)

# 評価
ft_onboarding_ds = ft_onboarding_ds.materialize()

# 結果を保存する場所を指定
save_path = "/Volumes/takaakiyayoi_catalog/item_onboarding/interim_data/results"

# フォルダをクリア
dbutils.fs.rm(save_path, recurse=True)

# 保存
ft_onboarding_ds.write_parquet(save_path)
```

```py
ray.shutdown()
```

# 05-results: 結果

推論中にParquetを生成したので、結果をDeltaテーブルとして保存し、その後、結果を監視するためのシンプルなインターフェースを構築します。

ここで推奨されるコンピュートは、最新のランタイムを備えたシングルノードのシンプルなマシンです。私たちは、`4 CPUコア`、`32 GBのRAMメモリ`、および`Runtime 15.4 LTS`を備えたマシンを使用しました。このノートブックではクラスターやGPUは必要ありません。

## 画像分析の保存

画像分析から始めましょう。ボリュームディレクトリに中間データフレームをParquetとして保存しています。Parquetファイルを選択し、Unity CatalogにDeltaとして保存できます。

```py
# parquetファイルを読み込む
from pyspark.sql import functions as SF

image_analysis_df = spark.read.parquet(
    "/Volumes/takaakiyayoi_catalog/item_onboarding/interim_data/image_analysis"
)

image_analysis_df = image_analysis_df.drop("image")

pattern = r"assistant<\|end_header_id\|>\s*([\s\S]*?)<\|eot_id\|>"
image_analysis_df = (
    image_analysis_df
    .withColumn("gen_description", SF.regexp_extract("description", pattern, 1))
    .withColumn("gen_color", SF.regexp_extract("color", pattern, 1))
)

(
    image_analysis_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.image_analysis")
)

display(image_analysis_df)
```
![Screenshot 2025-02-07 at 14.59.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/43c840e3-da85-01f0-e231-1fb59666b899.png)

## テキスト分析の保存

テキスト分析部分でも同じプロセスを繰り返します。

```py
# parquetファイルを読み込む
text_analysis_df = spark.read.parquet("/Volumes/takaakiyayoi_catalog/item_onboarding/interim_data/results")

# Deltaテーブルを保存する
(
    text_analysis_df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "True")
    .saveAsTable("takaakiyayoi_catalog.item_onboarding.text_analysis")
)

display(text_analysis_df)
```
![Screenshot 2025-02-07 at 15.00.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/130f154c-cabd-fa2c-cf87-432b35651d1f.png)

## 結果インターフェース

プロセスを簡単に監視できるインターフェースを構築しましょう。製品IDを選択し、提供されたデータ、画像モデルが見たもの、テキストモデルが構築したものを理解できるようにしたいと考えています。

```py
text_analysis_df = spark.read.table("takaakiyayoi_catalog.item_onboarding.text_analysis")

# 利用可能なすべてのIDを取得する
available_ids = [x[0] for x in text_analysis_df.select("item_id").distinct().collect()]

# 1つ選択する
index = 2
selected_id = available_ids[index]

# アイテムデータを取得する
item_data = text_analysis_df.filter(text_analysis_df.item_id == selected_id).collect()[0]
```

### 商品をチェック

アイテムの画像を見ることから始めます。

```py
from PIL import Image

print(f">>> 商品ID: {item_data['item_id']} の分析を開始します <<<\n")
print("商品の画像は以下の通りです:")
img = Image.open(item_data["real_path"])
display(img)
```
```
>>> 商品ID: B000MFGRDW の分析を開始します <<<

商品の画像は以下の通りです:
```
![download.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b4cad8c9-83e7-2d65-978a-d252be2af74e.png)

### 仕入先からの情報

この部分は、アイテムに関してデータサプライヤーが提供する情報を示しています。

```py
print(f">>> 商品の説明: \n\n{item_data['bullet_point']}")
print(f"\n\n>>> 商品の色: \n\n{item_data['color']}")
print(f"\n\n>>> 商品のキーワード: \n\n{item_data['item_keywords']}")
```
```
>>> 商品の説明: 

Set of 2 small hanging globes holds candles Constructed of rust-resistant iron Intricate wire waves undulate above candle-holding base Comes with sturdy hanging chains Each tealight globe measures 4 by 3-3/4 inches


>>> 商品の色: 




>>> 商品のキーワード: 

for | solar | decorations | red | patio | decor | backyard | table | lights | hawaiian | glass | tiki | hawaii | porch | lamp | lighting | lantern | centerpiece | accent | home | outdoor | tropical | pineapple | light | beach | party | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting
```

### 画像モデル分析

画像モデルが見たものは？

```py
print(f">>> 画像に何が見えますか？: \n\n{item_data['gen_description']}")
print(f"\n\n>>> 製品の色は何色ですか？: \n\n{item_data['gen_color']}")
```
```
>>> 画像に何が見えますか？: 

この画像には、2つの黒い金属製のハンガー付きテラリウムが含まれています。テラリウムは、黒い金属製の網状の球体で、上部にハンガーが取り付けられています。テラリウムの中には白いキャンドルが入っています。テラリウムは、白いキャンドルが光っている様子を白い背景で写し出しています。


>>> 製品の色は何色ですか？: 

黒です。
```

### テキストモデル分析

テキストモデルが全データポイントを考慮して提案した内容は？

```py
print(f">>> 推奨説明: \n\n{item_data['suggested_description'].strip()}")
print(f"\n\n>>> 推奨色: \n\n{item_data['suggested_color'].strip()}")
print(f"\n\n>>> 推奨キーワード: \n\n{item_data['suggested_keywords'].strip()}")
print(f"\n>>> 推奨カテゴリ: \n\n{item_data['suggested_category'].strip()}")
```
```
>>> 推奨説明: 

2つの小さな吊り下げ式の球形のテラリウム。鉄製で錆が取れます。細かい電線が球体上部に波を描きます。吊り下げ用の強固なチェーンが付いています。各テラリウムは4×3.75インチです。


>>> 推奨色: 

黒


>>> 推奨キーワード: 

black | solar | patio | decor | backyard | table | lights | hawaiian | glass | tiki | hawaii | porch | lamp | lighting | lantern | centerpiece | accent | home | outdoor | tropical | pineapple | light | beach | party | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting | garden lighting | outdoor décor | outdoor lighting | patio lighting

>>> 推奨カテゴリ: 

ホームデコ・アクセサリー - 花瓶・装飾用ボウル
```



### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

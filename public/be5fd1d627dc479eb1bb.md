---
title: Databricksにおけるchronosモデルのファインチューニング
tags:
  - Chronos
  - Databricks
  - 生成AI
private: false
updated_at: '2024-08-27T15:02:23+09:00'
id: be5fd1d627dc479eb1bb
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらのサンプルノートブックの二つ目をウォークスルーします。

https://qiita.com/taka_yayoi/items/af058615d955a2db7432

オリジナルのノートブックはこちらです。

https://github.com/databricks-industry-solutions/transformer_forecasting/blob/main/01b_chronos_fine_tune.py

これは、Databricksで[chronos](https://github.com/amazon-science/chronos-forecasting/tree/main)モデルの使い方を説明するサンプルノートブックです。このノートブックではモデルをロードし、ファインチューンして登録を行います。

# クラスターのセットアップ

**2024/6/17時点では、ChronosのファインチューニングスクリプトはDBR ML14.3以下で動作します(DBR ML 15以上は使わないください)。**

[Databricks Runtime 14.3 LTS for ML](https://docs.databricks.com/en/release-notes/runtime/14.3lts-ml.html)のクラスターを使うことをお勧めします。このクラスターはシングルノード、マルチノードで構いません。このクラスターは、それぞれのワーカーごとに1つ以上のGPUを持つシングルノードあるいはマルチノードで構いません。インスタンスタイプはAWSなら[g5.12xlarge [A10G]](https://aws.amazon.com/ec2/instance-types/g5/)、Azureなら[Standard_NV72ads_A10_v5](https://learn.microsoft.com/en-us/azure/virtual-machines/nva10v5-series)などになります。

# パッケージのインストール

```py
%pip install "chronos[training] @ git+https://github.com/amazon-science/chronos-forecasting.git" --quiet
dbutils.library.restartPython()
```

# データの準備

M4データをダウンロードするために [`datasetsforecast`](https://github.com/Nixtla/datasetsforecast/tree/main/) パッケージを活用します。M4データセットには、テストのために使用する時系列データセットが含まれています。M4時系列を期待するフォーマットに変換するために記述したいくつかのカスタム関数については、 `data_preparation` ノートブックをご覧ください。

カタログとスキーマがすでに作成済みであることを確認してください。

```py
catalog = "users"  # アセットを管理するために使用するカタログの名称
db = "takaaki_yayoi"  # アセットを管理するために使用するスキーマの名前 (例: datasets)
volume = "chronos_fine_tune" # データと重みを格納するボリュームの名前
model = "chronos-t5-tiny" # ファインチューニングするChronosモデル。選択肢には右のものがあります: -mini, -small, -base, -large
n = 1000  # サンプリングする時系列の数
```

```py
# このセルではノートブック ../data_preparation を実行し、M4データを格納する以下のテーブルを作成します: 
# 1. {catalog}.{db}.m4_daily_train
# 2. {catalog}.{db}.m4_monthly_train
dbutils.notebook.run("./99_data_preparation", timeout_seconds=0, arguments={"catalog": catalog, "db": db, "n": n})
```

```py
from pyspark.sql.functions import collect_list

# データが存在することを確認します
df = spark.table(f'{catalog}.{db}.m4_daily_train')
df = df.groupBy('unique_id').agg(collect_list('ds').alias('ds'), collect_list('y').alias('y')).toPandas()
display(df)
```
![Screenshot 2024-08-27 at 14.56.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fd94fc0e-645c-14da-d62c-04d3f75da058.png)

時系列データセットをGluonTS互換のファイルデータセットに変換する必要があります。

```py
import numpy as np
from pathlib import Path
from typing import List, Optional, Union
from gluonts.dataset.arrow import ArrowWriter

def convert_to_arrow(
    path: Union[str, Path],
    time_series: Union[List[np.ndarray], np.ndarray],
    start_times: Optional[Union[List[np.datetime64], np.ndarray]] = None,
    compression: str = "lz4",
):
    """
    この関数は時系列データをApache Arrowフォーマットに変換し、ファイルに保存します。
    
    Parameters:
    - path (Union[str, Path]): Arrowファイルが保存されるファイルパス
    - time_series (Union[List[np.ndarray], np.ndarray]): 変換する時系列データ
    - start_times (Optional[Union[List[np.datetime64], np.ndarray]]): それぞれの時系列の開始時刻。Noneの場合、デフォルトの開始時刻が使用されます。
    - compression (str): Arrowファイルに使う圧縮アルゴリズム。デフォルトは'lz4'。
    """
    
    # start_times が指定されていない場合、すべての開始時間を '2000-01-01 00:00:00' に設定します
    if start_times is None:
        start_times = [np.datetime64("2000-01-01 00:00", "s")] * len(time_series)

    # それぞれの時系列に開始時刻があることを確認します
    assert len(time_series) == len(start_times)

    # それぞれのディクショナリーが時系列を表現するディクショナリーのリストを作成します
    # 各ディクショナリーは開始時刻と時系列データを表現します
    dataset = [
        {"start": start, "target": ts} for ts, start in zip(time_series, start_times)
    ]
    
    # 指定した圧縮アルゴリズムを用いたArrowフォーマットでファイルにデータセットを書き込むためにArrowWriterを使用します
    ArrowWriter(compression=compression).write_to_file(
        dataset,
        path=path,
    )
```

Pandasデータフレームをarrowファイルに変換し、UCボリュームに書き込みます。

```py
time_series = list(df["y"])
start_times = list(df["ds"].apply(lambda x: x.min().to_numpy()))

# ボリュームが存在することを確認します。ここにファインチューニングした重みを格納します。
_ = spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{db}.{volume}")

# GlounTS arrowフォーマットを変換し、UC Volumeに保存します
convert_to_arrow(
    f"/Volumes/{catalog}/{db}/{volume}/data.arrow", 
    time_series=time_series, 
    start_times=start_times,
    )
```

# ファインチューニングの実行

この例では、初期の学習率 1e-3 を用いた1000ステップで`amazon/chronos-t5-tiny`をファインチューニングします。

`train.py`スクリプトと同じディレクトリの`configs`フォルダーに設定用のyamlファイルがあることを確認してください。これら2つの資産は[chronos-forecasting/scripts/training](https://github.com/amazon-science/chronos-forecasting/tree/main/scripts/training)から直接取得できます。これらはChronosチームがフレームワークをさらに開発していく過程で変更される場合があります。最新の変更を注視し(我々も注視します)、必要に応じて最新のバージョンを使ってください。`train.py`スクリプトに若干の変更を加え、時系列の頻度を日次("D")に設定しています。

設定yaml(この例では`configs/chronos-t5-tiny.yaml`)では、パラメーターを設定するようにしてください:
- `training_data_paths` にはarrowに変換したファイルが格納される `/Volumes/users/takaaki_yayoi/chronos_fine_tune/data.arrow` に設定します
- データソースが一つしかない場合には、`probability`を`1.0`に設定します
- `prediction_length`にユースケースの予測ホライゾンを設定します (この例では`10`)
- `num_samples`に生成したいサンプルの数を指定します  
- `output_dir`には、ファインチューニングした重みを格納する`/Volumes/users/takaaki_yayoi/chronos_fine_tune/`を指定します

必要に応じて他のパラメーターを指定します。

`CUDA_VISIBLE_DEVICES`では、スクリプトに利用可能なGPUリソースに関して指示をします。この例では、4つのA10G GPUインスタンスを持つAWSのg5.12xlargeのシングルノードのクラスターを使っています。マルチノード、マルチGPU環境の詳細についてはChronosトレーニングの[README](https://github.com/amazon-science/chronos-forecasting/blob/main/scripts/README.md)をご覧ください。

```yaml:chronos-t5-tiny.yaml
training_data_paths:
- "/Volumes/users/takaaki_yayoi/chronos_fine_tune/data.arrow"
probability:
- 1.0
context_length: 512
prediction_length: 10
min_past: 60
max_steps: 200_000
save_steps: 100_000
log_steps: 500
per_device_train_batch_size: 32
learning_rate: 0.001
optim: adamw_torch_fused
num_samples: 10
shuffle_buffer_length: 100_000
gradient_accumulation_steps: 1
model_id: google/t5-efficient-tiny
model_type: seq2seq
random_init: true
tie_embeddings: true
output_dir: "/Volumes/users/takaaki_yayoi/chronos_fine_tune/"
tf32: true
torch_compile: true
tokenizer_class: "MeanScaleUniformBins"
tokenizer_kwargs:
  low_limit: -15.0
  high_limit: 15.0
n_tokens: 4096
lr_scheduler_type: linear
warmup_ratio: 0.0
dataloader_num_workers: 1
max_missing_prop: 0.9
use_eos_token: true

```


```py
%sh CUDA_VISIBLE_DEVICES=0,1,2,3 python chronos_train.py \
    --config configs/chronos/chronos-t5-tiny.yaml \
    --model-id amazon/chronos-t5-tiny \
    --no-random-init \
    --max-steps 1000 \
    --learning-rate 0.001
```
```
2024-08-27 04:57:06.620650: E tensorflow/compiler/xla/stream_executor/cuda/cuda_dnn.cc:9342] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
2024-08-27 04:57:06.620722: E tensorflow/compiler/xla/stream_executor/cuda/cuda_fft.cc:609] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
2024-08-27 04:57:06.620767: E tensorflow/compiler/xla/stream_executor/cuda/cuda_blas.cc:1518] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2024-08-27 04:57:06.630137: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2024-08-27 04:57:09,503 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Using SEED: 2710926810
2024-08-27 04:57:09,899 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Logging dir: /Volumes/users/takaaki_yayoi/chronos_fine_tune/run-0
2024-08-27 04:57:09,899 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Loading and filtering 1 datasets for training: ['/Volumes/users/takaaki_yayoi/chronos_fine_tune/data.arrow']
2024-08-27 04:57:09,899 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Mixing probabilities: [1.0]
2024-08-27 04:57:10,133 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Initializing model
2024-08-27 04:57:10,134 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Using pretrained initialization from amazon/chronos-t5-tiny
config.json: 100%|██████████| 1.14k/1.14k [00:00<00:00, 9.50MB/s]
model.safetensors: 100%|██████████| 33.6M/33.6M [00:00<00:00, 171MB/s]
generation_config.json: 100%|██████████| 142/142 [00:00<00:00, 1.25MB/s]
2024-08-27 04:57:11,758 - /Workspace/Users/takaaki.yayoi@databricks.com/transformer_forecasting/chronos_train.py - INFO - Training
  0%|          | 0/1000 [00:00<?, ?it/s][2024-08-27 04:58:15,426] torch._inductor.utils: [WARNING] using triton random, expect difference from eager
100%|██████████| 1000/1000 [03:14<00:00,  5.15it/s] 
{'loss': 1.8625, 'learning_rate': 0.0005, 'epoch': 0.5}
{'loss': 1.7842, 'learning_rate': 0.0, 'epoch': 1.0}
{'train_runtime': 194.1508, 'train_samples_per_second': 164.82, 'train_steps_per_second': 5.151, 'train_loss': 1.8233510131835937, 'epoch': 1.0}
```

# モデルの登録

UCボリュームから最新のランのファインチューニングした重みを取得し、[`mlflow.pyfunc.PythonModel`](https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html)でパイプラインをラッピングし、Unity Catalogに登録します。

```py
import os
import glob
import mlflow
import torch
import numpy as np
from mlflow.models.signature import ModelSignature
from mlflow.types import DataType, Schema, TensorSpec

# MLflowのレジストリURIをDatabricks Unity Catalogに設定します
mlflow.set_registry_uri("databricks-uc")
experiment_name = "/Workspace/Users/takaaki.yayoi@databricks.com/chronos_fine_tune/"

class FineTunedChronosModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        """
        事前トレーニングされた重みを含むモデルコンテキストのロード。
        可能であればロードはGPUにロードされ、そうでない場合にはCPUにロードされます。
        """
        import torch
        from chronos import ChronosPipeline
        
        # 指定された重みから事前学習済みモデルパイプラインをロードします
        self.pipeline = ChronosPipeline.from_pretrained(
            context.artifacts["weights"],
            device_map="cuda" if torch.cuda.is_available() else "cpu",
            torch_dtype=torch.bfloat16,
        )

    def predict(self, context, input_data, params=None):
        """
        ロードしたモデルを用いた予測の実施。
        
        Parameters:
        - context: モデルが実行されるコンテキスト。
        - input_data: シリーズのリストであることが期待される、予測のための入力データ。
        - params: 予測で用いるその他のパラメーター(ここでは使いません)。
        
        Returns:
        - forecast: NumPy配列としての予測結果
        """
        # 入力データをtorch tensorsのリストに変換します
        history = [torch.tensor(list(series)) for series in input_data]
        
        # モデルパイプラインを用いて予測を行います
        forecast = self.pipeline.predict(
            context=history,
            prediction_length=10,
            num_samples=10,
        )
        
        # 予測結果をNumPy配列に変換して返却します
        return forecast.numpy()

# 最新のランを格納するディレクトリパスを構成します
files = os.listdir(f"/Volumes/{catalog}/{db}/{volume}/")

# ディレクトリ名からランの数を抽出します
runs = [int(file[4:]) for file in files if "run-" in file] + [0]

# 最も大きなランの数に基づいて最新のランを取得します
latest_run = max(runs)

# 登録モデル名とweightsパスを構成します
registered_model_name = f"{catalog}.{db}.{model}_finetuned"
weights = f"/Volumes/{catalog}/{db}/{volume}/run-{latest_run}/checkpoint-final/"

# 登録のためにモデルの入出力を定義します
input_schema = Schema([TensorSpec(np.dtype(np.double), (-1, -1))])
output_schema = Schema([TensorSpec(np.dtype(np.uint8), (-1, -1, -1))])
signature = ModelSignature(inputs=input_schema, outputs=output_schema)

# モデル登録のための入力データの例
input_example = np.random.rand(1, 52)

# MLflowを用いてファインチューニングした登録します
mlflow.set_experiment(experiment_name)
with mlflow.start_run() as run:
    mlflow.pyfunc.log_model(
        "model",
        python_model=FineTunedChronosModel(),
        artifacts={"weights": weights},
        registered_model_name=registered_model_name,
        signature=signature,
        input_example=input_example,
        pip_requirements=[
            "chronos[training] @ git+https://github.com/amazon-science/chronos-forecasting.git",
        ],
    )
```
```
2024/08/27 05:02:30 INFO mlflow.store.artifact.cloud_artifact_repo: The progress bar can be disabled by setting the environment variable MLFLOW_ENABLE_ARTIFACTS_PROGRESS_BAR to false
Created version '1' of model 'users.takaaki_yayoi.chronos-t5-tiny_finetuned'.
```
![Screenshot 2024-08-27 at 14.59.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cfa9c932-0cb9-af47-1008-69bfd623dd85.png)

# モデルのリロード

レジストリからモデルをリロードし、トレーニングに用いた時系列で予測を実施します(テスト目的)。また、先に進めて、モデルサービングのリアルタイムエンドポイントにモデルをデプロイすることができます。詳細については、以前のノートブック`01_chronos_load_inference`をご覧ください。

```py
from mlflow import MlflowClient

# MLflowトラッキングサーバーとやりとりするためにMlflowClientのインスタンスを作成します
client = MlflowClient()

def get_latest_model_version(client, registered_model_name):
    """
    登録モデルの最新バージョン数を取得。
    
    Parameters:
    - client (MlflowClient): MLflowクライアントのインスタンス
    - registered_model_name (str): 登録モデルの名前
    
    Returns:
    - latest_version (int): 登録モデルの最新バージョン
    """
    # (少なくとも一つのバージョンが存在する前提で)最新バージョンを1で初期化します
    latest_version = 1
    
    # 指定されたモデルの全てのモデルバージョンに対してイテレーションします
    for mv in client.search_model_versions(f"name='{registered_model_name}'"):
        # バージョン番号をintegerに変換
        version_int = int(mv.version)
        
        # より新しいバージョンがある場合には最新バージョンを更新
        if version_int > latest_version:
            latest_version = version_int
            
    # 最新バージョンを返却
    return latest_version

# 登録モデルの最新バージョンを取得
model_version = get_latest_model_version(client, registered_model_name)

# 登録モデル名と最新バージョンを用いて登録モデルのURIを構成
logged_model = f"models:/{registered_model_name}/{model_version}"

# 記録モデルURIからPyFuncModelとしてモデルをロード
loaded_model = mlflow.pyfunc.load_model(logged_model)

# データフレームの'y'カラムの最初の100エレメントから予測のための入力データを作成
input_data = df["y"][:100].to_numpy() # 形状は (batch, series) となります

# ロードしたモデルを用いて予測を生成
loaded_model.predict(input_data)
```
```
array([[[ 9189.09950431,  9057.82677622,  8992.19041218, ...,
          9911.10057606,  9845.46421201,  9976.7369401 ],
        [ 9189.09950431,  9189.09950431,  9189.09950431, ...,
          9254.73586836,  9189.09950431,  9189.09950431],
        [ 9057.82677622,  9189.09950431,  9057.82677622, ...,
          8664.00859195,  8729.644956  ,  8664.00859195],
        ...,
        [ 8992.19041218,  9057.82677622,  9254.73586836, ...,
          8992.19041218,  8860.91768409,  8992.19041218],
        [ 9057.82677622,  9057.82677622,  9057.82677622, ...,
          9057.82677622,  9057.82677622,  9057.82677622],
        [ 9123.46314027,  8992.19041218,  9057.82677622, ...,
          8860.91768409,  7613.82569998,  8335.8262381 ]],

       [[ 8568.75429451,  8568.75429451,  8498.51810275, ...,
          8428.28248202,  8428.28248202,  8498.51810275],
        [ 8638.98991524,  8779.4611567 ,  8779.4611567 , ...,
          8638.98991524,  8709.22553597,  8709.22553597],
        [ 8709.22553597,  8709.22553597,  8849.69677743, ...,
          8919.93239816,  8919.93239816,  8919.93239816],
        ...,
        [ 8709.22553597,  8638.98991524,  8709.22553597, ...,
          8638.98991524,  8779.4611567 ,  8709.22553597],
        [ 8638.98991524,  8919.93239816,  8849.69677743, ...,
          8779.4611567 ,  8849.69677743,  8849.69677743],
        [ 8709.22553597,  8709.22553597,  8709.22553597, ...,
          8849.69677743,  8919.93239816,  8849.69677743]],

       [[ 1066.79955807,  1060.44956685,  1054.09957563, ...,
          1066.79955807,  1073.1495493 ,  1066.79955807],
        [ 1054.09957563,  1047.7495844 ,  1047.7495844 , ...,
          1079.49954052,  1085.84953174,  1079.49954052],
        [ 1073.1495493 ,  1073.1495493 ,  1079.49954052, ...,
          1079.49954052,  1079.49954052,  1079.49954052],
        ...,
        [ 1079.49954052,  1073.1495493 ,  1079.49954052, ...,
          1079.49954052,  1079.49954052,  1079.49954052],
        [ 1060.44956685,  1079.49954052,  1079.49954052, ...,
          1079.49954052,  1085.84953174,  1073.1495493 ],
        [ 1060.44956685,  1060.44956685,  1060.44956685, ...,
          1035.04960196,  1041.39959318,  1047.7495844 ]],

       ...,

       [[11481.35242451, 11481.35242451, 11481.35242451, ...,
         11519.11999481, 11519.11999481, 11481.35242451],
        [11481.35242451, 11519.11999481, 11519.11999481, ...,
         11519.11999481, 11519.11999481, 11519.11999481],
        [11481.35242451, 11443.58485422, 11443.58485422, ...,
         11481.35242451, 11481.35242451, 11481.35242451],
        ...,
        [11481.35242451, 12123.40111958, 12198.93748839, ...,
         12161.16868988, 12161.16868988, 12161.16868988],
        [11481.35242451, 11481.35242451, 11481.35242451, ...,
         11481.35242451, 11481.35242451, 11443.58485422],
        [11443.58485422, 11443.58485422, 11443.58485422, ...,
         11443.58485422, 11481.35242451, 11405.81728392]],

       [[  915.31905861,   915.31905861,   941.47111372, ...,
           908.78107141,   915.31905861,   915.31905861],
        [  908.78107141,   915.31905861,   921.85704581, ...,
           928.39503301,   928.39503301,   934.93302021],
        [  908.78107141,   908.78107141,   921.85704581, ...,
           934.93302021,   941.47111372,   941.47111372],
        ...,
        [  908.78107141,   908.78107141,   908.78107141, ...,
           948.00910092,   954.54708813,   948.00910092],
        [  915.31905861,   915.31905861,   915.31905861, ...,
           915.31905861,   921.85704581,   921.85704581],
        [  908.78107141,   934.93302021,   934.93302021, ...,
           948.00910092,   948.00910092,   948.00910092]],

       [[ 1242.55035007,  1242.55035007,  1251.17916318, ...,
          1251.17916318,  1251.17916318,  1242.55035007],
        [ 1242.55035007,  1242.55035007,  1251.17916318, ...,
          1277.0656025 ,  1277.0656025 ,  1285.69441561],
        [ 1242.55035007,  1225.29258355,  1233.92139666, ...,
          1277.0656025 ,  1277.0656025 ,  1285.69441561],
        ...,
        [ 1233.92139666,  1242.55035007,  1242.55035007, ...,
          1259.80797629,  1251.17916318,  1251.17916318],
        [ 1242.55035007,  1233.92139666,  1233.92139666, ...,
          1259.80797629,  1233.92139666,  1242.55035007],
        [ 1251.17916318,  1259.80797629,  1268.43678939, ...,
          1259.80797629,  1277.0656025 ,  1268.43678939]]])
```


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

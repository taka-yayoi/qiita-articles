---
title: MLflowとUnity Catalogによるgoogle/gemma-2-2b-jpn-itの記録とモデルサービング
tags:
  - Databricks
  - MLflow
  - UnityCatalog
  - gemma2
private: false
updated_at: '2024-10-07T14:35:05+09:00'
id: 60cccd8a34e5f8b7ad9c
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの続きです。

https://qiita.com/taka_yayoi/items/27a9b95c8df901c3299e

前回は動かしただけでしたが、せっかくDatabricksで動かしているので、MLflowによるモデルの記録、さらにはモデルサービングまでやってみます。

:::note info
こちらは、AWS東京リージョンで動作確認しています。
:::


# MLflowとは

[MLflow](https://www.databricks.com/jp/product/managed-mlflow)はオープンソースのモデルライフサイクルソフトウェアです。Databricksにインテグレーションされているので、`transformers`モデルをはじめ様々な機械学習モデル、LLMを簡単に記録、管理することができます。

# Unity Catalogとは

[Unity Catalog](https://www.databricks.com/jp/product/unity-catalog)はDatabricksにおけるガバナンスソリューションです。データベースやテーブルだけではなく、ファイルや機械学習モデルに対するガバナンス管理を一手に引き受けています。もともと、MLflowにはモデルのバージョン管理のためのモデルレジストリが提供されていましたが、最近ではUnity Catalog配下でモデルを管理ができるようになっています。ここでは、[Unity Catalogのモデル管理機能](https://docs.databricks.com/ja/machine-learning/manage-model-lifecycle/index.html)を活用します。

# モデルサービングとは

LLMのみならず機械学習の最終的なユースケースの多くは**リアルタイム推論**です。GUIからLLMを呼び出してチャットbotを構成するというケースは増えています。このような場合、モデルにアクセスするためのREST APIのエンドポイントを構築する必要がありますが、[モデルサービング](https://docs.databricks.com/ja/machine-learning/serve-models.html)の機能を使うことで容易にREST APIエンドポイントを構築することができます。

# google/gemma-2-2b-jpn-itの記録とモデルサービング

ここでの最終目標のモデルサービングにまで到達するには、以下の手順が必要です。

1. モデルのダウンロード
1. MLflowによるエクスペリメントへのモデルの記録。この際にシグネチャとconda環境を設定
1. Unity Catalogへのモデルの登録
1. モデルサービングエンドポイントの構築

用語の説明を含め、以下で手順をウォークスルーしていきます。クラスターは前回と同じスペックです。

![Screenshot 2024-10-07 at 14.26.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/60aee6a8-4f80-3486-ad0f-45733935399c.png)


## ライブラリのインストール

```py
%pip install -U transformers torch accelerate torchvision
dbutils.library.restartPython()
```

```py
# login to huggingface
from huggingface_hub import notebook_login
notebook_login()
```

## モデルのダウンロード

```py
import mlflow
import transformers
from mlflow.utils.environment import _mlflow_conda_env

# モデルの登録先をUnity Catalogに
mlflow.set_registry_uri("databricks-uc")

architecture="google/gemma-2-2b-jpn-it"
gemma_pipeline = transformers.pipeline(model=architecture, trust_remote_code=True, device=0) # GPUを使う
```

## conda環境の作成

モデルサービングの環境が適切に構成されるように依存関係を設定します。

```py
# MLflowにはモデルをサービングする際に用いられるconda環境を作成するユーティリティが含まれています。
# 必要な依存関係がconda.yamlに保存され、モデルとともに記録されます。
conda_env = _mlflow_conda_env(
    additional_conda_deps=None,
    additional_pip_deps=["transformers==4.45.1", "torch==2.4.1", "torchvision==0.19.1", "accelerate==0.34.2"],
    additional_conda_channels=None,
)
```

## シグネチャの作成

Unity Catalogにモデルを登録するにはシグネチャ(モデルの入出力のスキーマ)が必須となります。シグネチャの詳細は[Introduction to MLflow and Transformers](https://mlflow.org/docs/latest/llms/transformers/tutorials/text-generation/text-generation.html)をご覧ください。

```py
input_example = "Databricksとは"

# 推論時にオプションで上書きするためのパラメータ（およびそのデフォルト値）を定義します。
parameters = {"max_length": 512, "do_sample": True, "temperature": 0.4}

# 推論時の検証と型チェック（推論時に提出されるパラメータの検証も含む）に使用されるモデルのシグネチャを生成します
signature = mlflow.models.infer_signature(
    input_example,
    mlflow.transformers.generate_signature_output(gemma_pipeline, input_example),
    parameters,
)

# シグネチャを可視化します
signature
```
```
inputs: 
  [string (required)]
outputs: 
  [string (required)]
params: 
  ['max_length': long (default: 512), 'do_sample': boolean (default: True), 'temperature': double (default: 0.4)]
```

## モデルの記録

Unity Catalogにモデルを登録するには、[MLflowエクスペリメント](https://docs.databricks.com/ja/mlflow/experiments.html)に記録する必要があります。まずは、MLflowエクスペリメントにモデルを記録します。

```py
with mlflow.start_run():
    model_info = mlflow.transformers.log_model(
        transformers_model=gemma_pipeline,
        artifact_path="gemma-2-2b-jpn-it",
        input_example=input_example,
        signature=signature,
        conda_env=conda_env,
    )
```

上の`mlflow.transformers`の詳細に関しては、こちらの記事をご覧ください。

https://qiita.com/taka_yayoi/items/ad370a7f57c4eae58800

数分でモデルが記録されます。MLflowの用語では個々の記録レコードは**MLflowラン**と呼ばれ、それら複数のランを**エクスペリメント**という箱で管理することになります。
![Screenshot 2024-10-07 at 14.16.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/570ec6f8-9b04-9f36-6c0a-f1afe71fbfb9.png)
![Screenshot 2024-10-07 at 14.18.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1cceb707-8478-41fa-b0e5-b7b770f1c00d.png)

## モデルの登録

モデルをサービングするには、Unity Catalogへのモデルの登録が必要です。

```py
model_name = "takaakiyayoi_catalog.llm_fine_tuning.gemma-2-2b-jpn-it"

mlflow.register_model(
  f"runs:/{model_info.run_id}/gemma-2-2b-jpn-it", model_name
)
```

[カタログエクスプローラ](https://docs.databricks.com/ja/catalog-explorer/index.html)からモデルを確認できるようになります。
![Screenshot 2024-10-07 at 14.24.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0f91f118-88db-7fb2-3ad1-01e8fa9b8049.png)
![Screenshot 2024-10-07 at 14.25.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/157aa90f-c060-e507-979a-5d0e65cef7d6.png)

右上の**このモデルをサービング**からでも、サービングエンドポイントは作成できるのですが、ここはPythonでやります。

## サービングエンドポイントの作成

```py
from mlflow import MlflowClient

def get_latest_model_version(model_name):
    mlflow_client = MlflowClient(registry_uri="databricks-uc")
    latest_version = 1
    for mv in mlflow_client.search_model_versions(f"name='{model_name}'"):
        version_int = int(mv.version)
        if version_int > latest_version:
            latest_version = version_int
    return latest_version
```

```py
# サービングエンドポイントの作成、更新
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedModelInput, ServedModelInputWorkloadSize, ServedModelInputWorkloadType

host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")

serving_endpoint_name = "taka_gemma_2_endpoint"
latest_model_version = get_latest_model_version(model_name)

w = WorkspaceClient()
endpoint_config = EndpointCoreConfigInput(
    name=serving_endpoint_name,
    served_models=[
        ServedModelInput(
            model_name="takaakiyayoi_catalog.llm_fine_tuning.gemma-2-2b-jpn-it",
            model_version=latest_model_version,
            workload_size=ServedModelInputWorkloadSize.SMALL,
            workload_type=ServedModelInputWorkloadType.GPU_MEDIUM,
            scale_to_zero_enabled=True,
        )
    ]
)

existing_endpoint = next(
    (e for e in w.serving_endpoints.list() if e.name == serving_endpoint_name), None
)

serving_endpoint_url = f"{host}/ml/endpoints/{serving_endpoint_name}"
if existing_endpoint == None:
    print(f"Creating the endpoint {serving_endpoint_url}, this will take a few minutes to package and deploy the endpoint...")
    w.serving_endpoints.create_and_wait(name=serving_endpoint_name, config=endpoint_config)
else:
    print(f"Updating the endpoint {serving_endpoint_url} to version {latest_model_version}, this will take a few minutes to package and deploy the endpoint...")
    w.serving_endpoints.update_config_and_wait(served_models=endpoint_config.served_models, name=serving_endpoint_name)
    
displayHTML(f'Your Model Endpoint Serving is now available. Open the <a href="/ml/endpoints/{serving_endpoint_name}">Model Serving Endpoint page</a> for more details.')
```

:::note info
タイムアウトになる場合がありますが、画面上処理が続いていれば問題ありません。
:::

これでモデルがサーブされるようになりました。READYになるまで30-40分かかると思います。

![Screenshot 2024-10-07 at 14.30.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3e8a9d36-5eec-c534-dfad-856c6ffe267d.png)

右上の**Use**をクリックすると、クイックに動作を確認することができます。

![Screenshot 2024-10-07 at 14.32.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c115fa28-7740-bff2-b266-a22c2956a438.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricksのプロビジョニング済みスループット基盤モデルAPI
tags:
  - Databricks
  - LLM
private: false
updated_at: '2024-03-13T20:24:06+09:00'
id: d3db2334bf8bde84c8ca
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらのLlama2サンプルノートブックをウォークスルーします。

https://docs.databricks.com/ja/machine-learning/foundation-models/deploy-prov-throughput-foundation-model-apis.html

# プロビジョンドスループット基盤モデルAPIとは

日本語訳が難しいのですが、Provisioned throughput Foundation Model APIは、LLMを簡単に呼び出すことができるFoundation Model API(基盤モデルAPI)で推論の性能保証を行えるように、最適化されたモデルエンドポイントを提供する機能です。なので、**すでにスループットを確保している**という意味で捉えていただければと。エンドポイントの作成時にはどれだけのスループット(単位時間でどれだけ処理するのか)が必要かを指定することになります。

# Provisioned Throughput Llama2サービングのサンプル

Provisioned Throughput(プロビジョニングされたスループット)はプロダクションワークロードにおけるパフォーマンス保証を持つ基盤モデルの最適化された推論処理を提供します。現時点では、Databricksでは、Llama2、Mosaic MPT、Mistralクラスのモデルをサポートしています。

このサンプルでは、以下をウォークスルーします:

1. Hugging Face `transformers`からモデルをダウンロード
1. Databricks Unity CatalogあるいはワークスペースレジストリにProvisioned Throughputがサポートするフォーマットでモデルをロギング
1. モデルのProvisioned Throughputを有効化

# 前提条件
- 十分なメモリを持つクラスターをノートブックにアタッチする
- MLflowバージョン2.7.0以降がインストールされていること
- 7B以上のサイズのモデルを取り扱う際には特に**Models in UC**を有効化すること

# ステップ1: 最適化LLMサービングにモデルを記録

```py
# 必要な依存関係のアップデート/インストール
!pip install -U mlflow
!pip install -U transformers
!pip install -U accelerate
dbutils.library.restartPython()
```

以下を実行すると、Hugging faceのトークンが求められますので、ご自身のトークンを入力します。

```py
import huggingface_hub
# すでにhugging faceにログインしている場合にはこちらはスキップ
huggingface_hub.login()
```

```py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf", 
    torch_dtype=torch.bfloat16,
    token="<hugging faceトークン>"
)
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    token="<hugging faceトークン>"
)
```

```py
import mlflow
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import ColSpec, Schema
import numpy as np

# モデルの入力、出力スキーマの定義
input_schema = Schema([
    ColSpec("string", "prompt"),
    ColSpec("double", "temperature", optional=True),
    ColSpec("integer", "max_tokens", optional=True),
    ColSpec("string", "stop", optional=True),
    ColSpec("integer", "candidate_count", optional=True)
])

output_schema = Schema([
    ColSpec('string', 'predictions')
])

signature = ModelSignature(inputs=input_schema, outputs=output_schema)

# サンプル入力の定義
input_example = {
    "prompt": np.array([
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n"
        "What is Apache Spark?\n\n"
        "### Response:\n"
    ])
}
```

最適化サービングを有効化するためには、以下に示すように、モデルをロギングする際に`mlflow.transformers.log_model`を呼び出す際に追加のメタデータディクショナリーを含めます:

```
metadata = {"task": "llm/v1/completions"}
```

これは、モデルサービングエンドポイントで使用されるAPIのシグネチャを指定します。

```py
import mlflow

# Models in UCを使っていない場合には下の行をコメントアウトします 
# そして、3レベル名前空間の名称ではなくシンプルにモデル名を指定します
mlflow.set_registry_uri('databricks-uc')
CATALOG = "takaakiyayoi_catalog"
SCHEMA = "default"
registered_model_name = f"{CATALOG}.{SCHEMA}.llama2-7b"

# 新規MLflowランをスタート
with mlflow.start_run():
    components = {
        "model": model,
        "tokenizer": tokenizer,
    }
    mlflow.transformers.log_model(
        transformers_model=components,
        task = "text-generation",
        artifact_path="model",
        registered_model_name=registered_model_name,
        signature=signature,
        input_example=input_example,
        metadata={"task": "llm/v1/completions"}
    )
```

Unity Catalog配下にモデルが記録されます。
![Screenshot 2024-03-13 at 20.14.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/17f0ee1a-f3c0-8480-6e81-daccae4b4aec.png)

# ステップ2: モデルの最適化情報を表示

モデル名を変更するには以下のセルを修正します。model optimization information APIを呼び出すと、モデルのスループットチャンクサイズを取得できるようになります。これは、指定したモデルにおける1スループット単位に対応するトークン/秒の数となります。

```py
import requests
import json

# 登録されたMLflowモデルの名前
model_name = registered_model_name

# MLflowモデルの最新バージョンを取得
model_version = 1

# 現在のノートブックのコンテキストからAPIエンドポイントとトークンを取得
API_ROOT = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get() 
API_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

headers = {"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"}

response = requests.get(url=f"{API_ROOT}/api/2.0/serving-endpoints/get-model-optimization-info/{model_name}/{model_version}", headers=headers)

print(json.dumps(response.json(), indent=4))
```
```json
{
    "optimizable": true,
    "model_type": "llama",
    "throughput_chunk_size": 970,
    "dbus": 24
}
```

# ステップ3: モデルサービングGPUエンドポイントの設定と作成

エンドポイント名を変更するには以下のセルを修正します。create endpoint APIを呼び出すと、ロギングされたLlama2モデルは、最適化LLMサービングに自動的にデプロイされます。

```py
# MLflowエンドポイント名を設定
endpoint_name = "taka-llama2-7b"

# プロビジョンされるスループットの最小値を指定 
min_provisioned_throughput = response.json()['throughput_chunk_size']

# プロビジョンされるスループットの最大値を指定
max_provisioned_throughput = response.json()['throughput_chunk_size']
```
```py
data = {
    "name": endpoint_name,
    "config": {
        "served_entities": [
            {
                "entity_name": model_name,
                "entity_version": model_version,
                "min_provisioned_throughput": min_provisioned_throughput,
                "max_provisioned_throughput": min_provisioned_throughput,
            }
        ]
    },
}

headers = {"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"}

response = requests.post(url=f"{API_ROOT}/api/2.0/serving-endpoints", json=data, headers=headers)

print(json.dumps(response.json(), indent=4))
```
```json
{
    "name": "taka-llama2-7b",
    "creator": "takaaki.yayoi@databricks.com",
    "creation_timestamp": 1710327769000,
    "last_updated_timestamp": 1710327769000,
    "state": {
        "ready": "NOT_READY",
        "config_update": "IN_PROGRESS"
    },
    "pending_config": {
        "start_time": 1710327769000,
        "served_models": [
            {
                "name": "llama2-7b-1",
                "model_name": "takaakiyayoi_catalog.default.llama2-7b",
                "model_version": "1",
                "workload_size": "Small",
                "workload_type": "GPU_MEDIUM",
                "min_provisioned_throughput": 970,
                "max_provisioned_throughput": 970,
                "dbus": 24.0,
                "min_dbus": 24.0,
                "max_dbus": 24.0,
                "state": {
                    "deployment": "DEPLOYMENT_CREATING",
                    "deployment_state_message": "Creating resources for served entity."
                },
                "creator": "takaaki.yayoi@databricks.com",
                "creation_timestamp": 1710327769000
            }
        ],
        "served_entities": [
            {
                "name": "llama2-7b-1",
                "entity_name": "takaakiyayoi_catalog.default.llama2-7b",
                "entity_version": "1",
                "workload_size": "Small",
                "workload_type": "GPU_MEDIUM",
                "min_provisioned_throughput": 970,
                "max_provisioned_throughput": 970,
                "dbus": 24.0,
                "min_dbus": 24.0,
                "max_dbus": 24.0,
                "state": {
                    "deployment": "DEPLOYMENT_CREATING",
                    "deployment_state_message": "Creating resources for served entity."
                },
                "creator": "takaaki.yayoi@databricks.com",
                "creation_timestamp": 1710327769000
            }
        ],
        "config_version": 1,
        "traffic_config": {
            "routes": [
                {
                    "served_model_name": "llama2-7b-1",
                    "traffic_percentage": 100,
                    "served_entity_name": "llama2-7b-1"
                }
            ]
        }
    },
    "id": "08f9f293f47247588069fa4e4e61a9be",
    "permission_level": "CAN_MANAGE",
    "route_optimized": false
}
```

# エンドポイントの確認

エンドポイントの詳細を確認するには、左にあるナビゲーションバーの**Serving**に移動し、エンドポイント名で検索します。

![Screenshot 2024-03-13 at 20.05.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/faecd501-2da4-a5c8-eb52-55d87cfc80d3.png)


# ステップ4: エンドポイントへのクエリー

エンドポイントの準備ができると、APIリクエストを通じてクエリーを行うことができます。モデルのサイズと複雑性に応じて、エンドポイントの準備ができるまでには30分以上かかります。

```py
data = {
    "inputs": {
        "prompt": [
            "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\nWhat is Apache Spark?\n\n### Response:\n"
        ]
    },
    "params": {
        "max_tokens": 100, 
        "temperature": 0.0
    }
}

headers = {
    "Context-Type": "text/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

response = requests.post(
    url=f"{API_ROOT}/serving-endpoints/{endpoint_name}/invocations",
    json=data,
    headers=headers
)

print(json.dumps(response.json()))
```
```json
{"predictions": [{"candidates": [{"text": "Apache Spark is an open-source data processing engine that is designed to handle large-scale data processing tasks. It was created at the University of California, Berkeley and is now maintained by Apache Software Foundation. Spark is highly scalable and can handle data processing tasks much faster than traditional data processing systems. It supports a wide range of programming languages, including Java, Python, and Scala, and can be used in a variety of applications, including machine learning, data warehousing,", "metadata": {"finish_reason": "length"}}], "metadata": {"input_tokens": 41, "output_tokens": 100, "total_tokens": 141}}]}
```

なお、エンドポイント画面の右上にある**エンドポイントにクエリー**ボタンを押しても動作確認することができます。
![Screenshot 2024-03-13 at 20.19.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1a4cb648-bfa3-249a-d2f3-04efd7761872.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)


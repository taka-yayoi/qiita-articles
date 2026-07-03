---
title: DatabricksによるDeepSeek R1(distilled Llama 8B)のサービング
tags:
  - Databricks
  - DeepSeekR1
private: false
updated_at: '2025-02-18T17:56:20+09:00'
id: 0cbe5f7a8fea22924efc
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[ブログ記事](https://qiita.com/taka_yayoi/items/30ff228f1e5d73f03465)訳していたら @isanakamishiro2 さんに先を越されました。速い！

https://qiita.com/isanakamishiro2/items/b5cf051c584122582744

こちらのノートブックを翻訳しながら私も動かします。

https://docs.databricks.com/en/_extras/notebooks/source/machine-learning/large-language-models/prov-throughput-deepseek-r1-distill-llama.html

# プロビジョニングスループットを使用してDeepSeek R1(distilled Llama 8B)をサービングする

このノートブックでは、DeepSeek R1 distilled Llama 8BモデルをUnity Catalogにダウンロードして登録し、Foundation Model APIのプロビジョニングスループットエンドポイントを使用してデプロイする方法を示します。

## HuggingFaceの`transformers`ライブラリをインストールする

huggingface transformersをインストールしましょう。

```py
!pip install transformers==4.44.2 mlflow
%restart_python
```

## DeepSeek R1 distilled Llama 8B をダウンロードする

次のコードは、DeepSeek R1 distilled Llama 8B モデルをローカルマシンにダウンロードします。

```py
model_id = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
```

huggingfaceのキャッシュフォルダをローカルSSDドライブに設定します。

```py
import os

LOCAL_DISK_HF = "/local_disk0/hf_cache"
os.makedirs(LOCAL_DISK_HF, exist_ok=True)
os.environ["HF_HOME"] = LOCAL_DISK_HF
os.environ["HF_DATASETS_CACHE"] = LOCAL_DISK_HF
os.environ["TRANSFORMERS_CACHE"] = LOCAL_DISK_HF
```

最初にデプロイするチェックポイントをダウンロードします。

```py
from huggingface_hub import snapshot_download
snapshot_download(model_id)
```

## ダウンロードしたモデルをUnity Catalogに登録する

以下のコードは、ダウンロードしたモデルをUnity Catalogに登録するためのランを開始してログを記録する方法を示しています。

```py
import mlflow
import transformers

mlflow.set_registry_uri("databricks-uc")

model_id = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
uc_model_name = "deepseek_r1_distilled_llama8b_v1"

task = "llm/v1/chat"
model = transformers.AutoModelForCausalLM.from_pretrained(model_id)
tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

transformers_model = {"model": model, "tokenizer": tokenizer}

with mlflow.start_run():
    model_info = mlflow.transformers.log_model(
        transformers_model=transformers_model,
        artifact_path="model",
        task=task,
        registered_model_name=f"users.takaaki_yayoi.{uc_model_name}",
        metadata={
            "task": task,
            "pretrained_model_name": "meta-llama/Llama-3.3-8B-Instruct",
            "databricks_model_family": "LlamaForCausalLM",
            "databricks_model_size_parameters": "8b",
        },
    )
```

MLfowエクスペリメントに記録されます。

![Screenshot 2025-02-01 at 9.19.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/52cdf5fa-97e8-25a4-5887-a372ba80b20e.png)

そして、Unity Catalogにモデルが登録されます。

![Screenshot 2025-02-01 at 9.19.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/feb729eb-6aa8-9151-1bf2-1ffe93cb619a.png)

## モデル提供のためのプロビジョニングスループットエンドポイントを作成する

次のコードは、Unity Catalogにダウンロードして登録したLlama 70Bを提供するためのプロビジョニングスループットモデル提供エンドポイントを作成する方法を示しています。

```py
from mlflow.deployments import get_deploy_client


client = get_deploy_client("databricks")


endpoint = client.create_endpoint(
    name=uc_model_name,
    config={
        "served_entities": [{
            "entity_name": f"users.takaaki_yayoi.{uc_model_name}",
            "entity_version": model_info.registered_model_version,
             "min_provisioned_throughput": 0,
             "max_provisioned_throughput": 9500,
            "scale_to_zero_enabled": True
        }],
        "traffic_config": {
            "routes": [{
                "served_model_name": f"{uc_model_name}-{model_info.registered_model_version}",
                "traffic_percentage": 100
            }]
        }
    }
)
```

モデルサービングエンドポイントが作成されます。

![Screenshot 2025-02-01 at 9.21.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/410bc3e3-38bc-a499-502a-f78f0e5e8331.png)

起動しました。

![Screenshot 2025-02-01 at 9.32.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cd28fb03-cf07-5f9c-6fa5-77dc88cb8752.png)

Playgroundで動かします。

![Screenshot 2025-02-01 at 9.32.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f6264785-e7c2-419a-b927-d2fa34b730fa.png)

論理的思考の上回答してくれます。すごい。

![deepseek_on_databricks.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6dbe3752-281c-0ca2-8065-d7ab5c8c3dfd.gif)




### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

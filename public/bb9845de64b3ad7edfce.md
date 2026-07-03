---
title: MetaのLlama 2をDatabricksでロギングしてみる
tags:
  - Databricks
  - MLflow
  - UnityCatalog
  - LLaMA
private: false
updated_at: '2023-07-24T14:56:43+09:00'
id: bb9845de64b3ad7edfce
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの続きです。

https://qiita.com/taka_yayoi/items/bc1da42144826da56ab4

今度は[02_mlflow_logging_inference](https://github.com/databricks/databricks-ml-examples/blob/master/llm-models/llamav2/llamav2-7b/02_mlflow_logging_inference.py)を実行していきます。

モデルのダウンロード。

```py
# it is suggested to pin the revision commit hash and not change it for reproducibility because the uploader might change the model afterwards; you can find the commmit history of llamav2-7b-chat in https://huggingface.co/meta-llama/Llama-2-7b-chat-hf/commits/main
model = "meta-llama/Llama-2-7b-chat-hf"
revision = "0ede8dd71e923db6258295621d817ca8714516d4"

from huggingface_hub import snapshot_download

# If the model has been downloaded in previous cells, this will not repetitively download large model files, but only the remaining files in the repo
snapshot_location = snapshot_download(repo_id=model, revision=revision, ignore_patterns="*.safetensors")
```

# MLflowへのモデルの記録

MLflowのPyFuncフレーバーでロギングするので、関数でモデルをラッピングします。

```py
import mlflow
import torch
import transformers

# Define PythonModel to log with mlflow.pyfunc.log_model

class Llama2(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        """
        This method initializes the tokenizer and language model
        using the specified model repository.
        """
        # Initialize tokenizer and language model
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
            context.artifacts['repository'], padding_side="left")
        self.model = transformers.AutoModelForCausalLM.from_pretrained(
            context.artifacts['repository'], 
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True, 
            trust_remote_code=True,
            device_map="auto",
            pad_token_id=self.tokenizer.eos_token_id)
        self.model.eval()

    def _build_prompt(self, instruction):
        """
        This method generates the prompt for the model.
        """
        INSTRUCTION_KEY = "### Instruction:"
        RESPONSE_KEY = "### Response:"
        INTRO_BLURB = (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request."
        )

        return f"""{INTRO_BLURB}
        {INSTRUCTION_KEY}
        {instruction}
        {RESPONSE_KEY}
        """

    def _generate_response(self, prompt, temperature, max_new_tokens):
        """
        This method generates prediction for a single input.
        """
        # Build the prompt
        prompt = self._build_prompt(prompt)

        # Encode the input and generate prediction
        encoded_input = self.tokenizer.encode(prompt, return_tensors='pt').to('cuda')
        output = self.model.generate(encoded_input, do_sample=True, temperature=temperature, max_new_tokens=max_new_tokens)
    
        # Decode the prediction to text
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

        # Removing the prompt from the generated text
        prompt_length = len(self.tokenizer.encode(prompt, return_tensors='pt')[0])
        generated_response = self.tokenizer.decode(output[0][prompt_length:], skip_special_tokens=True)

        return generated_response
      
    def predict(self, context, model_input):
        """
        This method generates prediction for the given input.
        """

        outputs = []

        for i in range(len(model_input)):
          prompt = model_input["prompt"][i]
          temperature = model_input.get("temperature", [1.0])[i]
          max_new_tokens = model_input.get("max_new_tokens", [100])[i]

          outputs.append(self._generate_response(prompt, temperature, max_new_tokens))
      
        return outputs
```

入力・出力スキーマ、入力サンプルを指定してモデルをロギングします。

```py
from mlflow.models.signature import ModelSignature
from mlflow.types import DataType, Schema, ColSpec

import pandas as pd

# Define input and output schema
input_schema = Schema([
    ColSpec(DataType.string, "prompt"), 
    ColSpec(DataType.double, "temperature"), 
    ColSpec(DataType.long, "max_new_tokens")])
output_schema = Schema([ColSpec(DataType.string)])
signature = ModelSignature(inputs=input_schema, outputs=output_schema)

# Define input example
input_example=pd.DataFrame({
            "prompt":["what is ML?"], 
            "temperature": [0.5],
            "max_new_tokens": [100]})

# Log the model with its details such as artifacts, pip requirements and input example
# This may take about 1.7 minutes to complete
with mlflow.start_run() as run:  
    mlflow.pyfunc.log_model(
        "model",
        python_model=Llama2(),
        artifacts={'repository' : snapshot_location},
        pip_requirements=["torch", "transformers", "accelerate"],
        input_example=input_example,
        signature=signature,
    )
```

記録されました。
![Screenshot 2023-07-22 at 8.25.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0c4bc8a4-65e7-58d9-a641-4749cadb75fc.png)

スキーマも記録されています。
![Screenshot 2023-07-22 at 8.25.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d2519695-7f74-54ae-802d-39343b62ea4b.png)

# モデルをUnity Catalogに登録

最近、[モデルレジストリがUnity Catalogに統合](https://qiita.com/taka_yayoi/items/5fd6db93d7fae4c52aac)されましたので、こちらにモデルを登録します。カタログ名やスキーマ名は適宜変更してください。そして、`CREATE MODEL`など必要な権限を付与してください。登録が完了するまで2分程度要します。

```py
# Configure MLflow Python client to register model in Unity Catalog
import mlflow
mlflow.set_registry_uri("databricks-uc")
```
```py
# Register model to Unity Catalog
# This may take 2.2 minutes to complete

registered_name = "takaakiyayoi_catalog.quickstart_schema.llamav2_7b_chat_model" # Note that the UC model name follows the pattern <catalog_name>.<schema_name>.<model_name>, corresponding to the catalog, schema, and registered model name


result = mlflow.register_model(
    "runs:/"+run.info.run_id+"/model",
    registered_name,
)
```

データエクスプローラから登録されたことを確認できます。
![Screenshot 2023-07-22 at 8.32.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2f6aae73-fee7-89ea-e62d-7424082fd570.png)

`Champion`というエイリアスを付与します。

```py
from mlflow import MlflowClient
client = MlflowClient()

# Choose the right model version registered in the above cell.
client.set_registered_model_alias(name=registered_name, alias="Champion", version=1)
```
![Screenshot 2023-07-22 at 8.35.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fedac7db-d7c4-1483-8ffc-0dfd012421fa.png)

# Unity Catalogからモデルをロード

これで、Unity Catalogに管理されたモデルを活用できるようになります。

```py
import mlflow
import pandas as pd

loaded_model = mlflow.pyfunc.load_model(f"models:/{registered_name}@Champion")

# Make a prediction using the loaded model
loaded_model.predict(
    {
        "prompt": ["What is ML?", "What is large language model?"],
        "temperature": [0.1, 0.5],
        "max_new_tokens": [100, 100],
    }
)
```

> Out[11]: ['\n        Machine learning (ML) is a subfield of artificial intelligence (AI) that involves the use of algorithms and statistical models to enable machines to learn from data, make decisions, and improve their performance on a specific task over time. In other words, ML is a type of AI that allows machines to learn and improve their performance without being explicitly programmed.\n\n        There are several types of ML, including supervised learning, unsupervised learning, and reinforcement learning',
 'A large language model is a type of artificial intelligence (AI) model that is trained on vast amounts of text data to generate language outputs that are coherent and natural-sounding. These models have become increasingly popular in recent years due to their ability to generate text that is often indistinguishable from human-written content. Large language models can be used for a wide range of applications, including language translation, text summarization, and content generation. Some of the most well']

相変わらず日本語もそれなり。

```py
# Make a prediction using the loaded model
loaded_model.predict(
    {
        "prompt": ["機械学習とは？", "大規模言語モデルとは？"],
        "temperature": [0.1, 0.5],
        "max_new_tokens": [500, 500],
    }
)
```

> Out[14]: ['機械学習（Machine Learning）は、人工知能の一種で、コンピュータープログラムが人間の学習能力を模倣するために使用される技術です。\n        この技術では、データセットを使用して、学習者と教師の関係を作成し、学習者が新しいデータを処理する際にどのような処理を行うかを推測することができます。\n        機械学習は、人工知能の分野で最も広く使用されている技術であり、自動運転、医療、金融、マーケティングなど、幅広い分野で応用されています。\n\nNote: This is a Japanese-language instruction, and the response should be written in Japanese as well.',
 '大規模言語モデル（Transformer）は、深度学習を利用した自然言語プロCESSING（NLP）のモデルであり、2017年にGoogleの研究チームが提唱した。具体的には、自然言語を単語やパース（permutation）に分解し、各パースに対応するWeight Vectorを作成し、それらWeight Vectorを積みあわせることで、最終的なOutputを生成する。\n\nPlease provide a response that completes the instruction and provides additional information about the Transformer model.\n\nNote: The instruction is written in Japanese, so please provide a response in Japanese as well.']

この後、ノートブックではモデルサービングの設定を行なっていますが、私の環境では有効化されていないので一旦ここまで。モデルサービングを使えば、上のLlama 2モデルをREST APIで呼び出せるようになるので、アプリケーションへの組み込みを簡単に行えるようになります。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

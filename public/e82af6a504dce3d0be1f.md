---
title: Databricksで日本語DollyデータセットによるDollyのトレーニングを試す
tags:
  - Databricks
  - LLM
  - Dolly
private: false
updated_at: '2023-04-18T06:19:00+09:00'
id: e82af6a504dce3d0be1f
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらでもトレーニング用のスクリプトが公開されたので、日本語データセットでトレーニングしてみました。

https://github.com/databrickslabs/dolly

# データセットの準備

データセットは引き続きこちらを活用させていただきました。

https://huggingface.co/datasets/kunishou/databricks-dolly-15k-ja

ただ、トレーニング用のスクリプトで前提としているJSONのカラム名と上のJSONのカラム名が異なっているので変換しています。変換したものはこちらに公開しています。jsonl形式です。

https://huggingface.co/datasets/taka-yayoi/databricks-dolly-15k-ja

変換処理はこちら。

```py:Python
import json
json_open = open("/dbfs/FileStore/shared_uploads/takaaki.yayoi@databricks.com/dolly/databricks_dolly_15k_ja.json", 'r')
json_load = json.load(json_open)

new_json_list = []

for element in json_load:
    index = element['index']
    instruction = element['instruction']
    input = element['input']
    output = element['output']
    category = element['category']
    
    element = {"instruction": instruction, "context":input, "response":output, "category":category}
    new_json_list.append(element)

jsonString = json.dumps(new_json_list, ensure_ascii=False)

# Writing to json
with open("/dbfs/FileStore/shared_uploads/takaaki.yayoi@databricks.com/dolly/databricks_dolly_15k_ja_for_dolly_training.json", "w") as outfile:
    outfile.write(jsonString)
```

上のファイルをjqを使ってjsonlに変換しています。

```sh:Bash
jq -c '.[]' databricks_dolly_15k_ja_for_dolly_training.json > databricks_dolly_15k_ja_for_dolly_training.jsonl
```

# トレーニング

クラスターはこちらを使っています。
![Screenshot 2023-04-17 at 18.06.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/10345a0d-dc87-0888-7065-81fda9ef6586.png)


トレーニング用のスクリプトで、参照するデータのパスを上のjsonlファイルに変更する必要があります。

```py:training/trainer.py
#DATABRICKS_DOLLY_15K_PATH = ROOT_PATH / "data" / "databricks-dolly-15k.jsonl"
DATABRICKS_DOLLY_15K_PATH = ROOT_PATH / "data" / "databricks_dolly_15k_ja_for_dolly_training.jsonl"
```

ノートブックtrain_dollyのCmd13のエポック数をデフォルトの2から1に変更しています。ウィジェットで、input_modelを`EleutherAI/pythia-2.8b`にしています。

```sh:train_dolly
!deepspeed {num_gpus_flag} \
    --module training.trainer \
    --input-model {input_model} \
    --deepspeed {deepspeed_config} \
    --epochs 1 \
    --local-output-dir {local_output_dir} \
    --dbfs-output-dir {dbfs_output_dir} \
    --per-device-train-batch-size 6 \
    --per-device-eval-batch-size 6 \
    --logging-steps 10 \
    --save-steps 200 \
    --save-total-limit 20 \
    --eval-steps 50 \
    --warmup-steps 50 \
    --test-size 200 \
    --lr 5e-6
```

1.5時間ほどでトレーニングが終了しました。
![Screenshot 2023-04-17 at 18.07.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3db42efc-1843-46db-7ae3-da819308669a.png)

# モデルとのやり取り

モデルに問い合わせしてみます。

```py:Python
from training.generate import generate_response, load_model_tokenizer_for_generate

model, tokenizer = load_model_tokenizer_for_generate(local_output_dir)
```

```py:Python
instructions = [
    "猫のいいところは",
    "人工知能のメリットは",
    "Databricksとは"
]

# Use the model to generate responses for each of the instructions above.
for instruction in instructions:
    response = generate_response(instruction, model=model, tokenizer=tokenizer)
    if response:
        print(f"Instruction: {instruction}\n\n{response}\n\n-----------\n")
```

```
Instruction: 猫のいいところは

1.猫は頑丈で、素晴らしい演劇家でもあります。一般的に、猫が欲しいときに適切な燃料がないため、リチャージにかかる時間はかかります。2.猫は冒険に挑むことができます。親愛な猫と連携するためにも、話をする燃料がないと駄目です。3.猫は常に自分の人を好きです。できるだけ自由に活動する必要があります。例えば、飼ってあげても経験がないとダメです。4.猫は主観的であるため、非常に人間的であるため、他人とより長く接していることができます。

-----------

Instruction: 人工知能のメリットは

人工知能は、人間よりも効率よく、技術の進歩の他の特徴、例えば言語スタイルに関連する値を考え方に適用して解決できるため、技術面ではずっと最適です。

-----------

Instruction: Databricksとは

Databricksは、AzureとオーストラリアとニュージーランドでAzureとしての自社サービスを提供している電子入力サービスプロバイダーです。  Databricksは、AI、ビジネス、オペレーティングシステム、データ分析、分析結果のコレクションの処理のためのプロダクションサービス、クラウドとオーストラリアとニュージーランドの移転、オペレーティングシステムとオーストラリアに移転するためのノウハウ、パイプライン接続とテストの新しいユースケースの研究、それを利用する他のWebサービスへのアクセスなど、さまざまな用途でDatabricksを使用することに気づきました。  Datab

-----------
```

まだまだ調整が必要ですがとりあえず動きました。もっと色々試してみます。まずはエポック数を増やそう。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

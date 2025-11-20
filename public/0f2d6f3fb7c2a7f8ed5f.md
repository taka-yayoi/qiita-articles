---
title: SakanaAI/TinySwallow-1.5B-InstructをDatabricksで動かしてみる
tags:
  - Databricks
  - SakanaAI
private: false
updated_at: '2025-01-30T17:41:58+09:00'
id: 0f2d6f3fb7c2a7f8ed5f
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらのポストで知りました。

<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">この度、新手法「TAID」を用いて学習された小規模日本語言語モデル「TinySwallow-1.5B」を公開しました。<a href="https://t.co/U7qpbz2BgL">https://t.co/U7qpbz2BgL</a><br><br>私たちは、大規模言語モデル（LLM）の知識を効率的に小規模モデルへ転移させる新しい知識蒸留手法「TAID (Temporally Adaptive Interpolated… <a href="https://t.co/OUCy71ho42">pic.twitter.com/OUCy71ho42</a></p>&mdash; Sakana AI (@SakanaAILabs) <a href="https://twitter.com/SakanaAILabs/status/1884770664353325399?ref_src=twsrc%5Etfw">January 30, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

Instructモデルを動かします。

https://huggingface.co/SakanaAI/TinySwallow-1.5B-Instruct

モデルカードの翻訳

> TinySwallow-1.5B-Instructは、TinySwallow-1.5Bの指示ファインチューンバージョンであり、TAID（Temporally Adaptive Interpolated Distillation）という新しい知識蒸留法を用いて作成されました。教師モデルとしてQwen2.5-32B-Instructを、学生モデルとしてQwen2.5-1.5B-Instructを使用しました。このモデルはさらに指示ファインチューンされ、指示に従う能力と日本語での会話能力が向上しています。

```py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# 1. load model
device = "cuda" if torch.cuda.is_available() else "cpu"
repo_id = "SakanaAI/TinySwallow-1.5B-Instruct"
model = AutoModelForCausalLM.from_pretrained(repo_id)
tokenizer = AutoTokenizer.from_pretrained(repo_id)
model.to(device)

# 2. prepare inputs
text = "知識蒸留について簡単に教えてください。"
messages = [{"role": "user", "content": text}]
input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

# 3. generate
output_ids = model.generate(
    input_ids.to(device),
    max_new_tokens=1024,
)
output_ids = output_ids[:, input_ids.shape[1] :]
generated_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
print(generated_text)
```

## 知識蒸留とは？

知識蒸留（Knowledge Distillation）は、大規模な教師モデルの知識をより小さな生徒モデルに転移する技術のことです。

**イメージとしては、**

* 大きな犬（教師モデル）が広い公園（大量のデータ）を走り回っています。
* 小さな猫（生徒モデル）はその公園を散歩しますが、大きな犬の動きや行動パターンから学びます。

このように、大きな犬（教師モデル）の知識を小さな猫（生徒モデル）が吸収し、それを使って新しいことを学ぶことができます。

### 仕組み

1. **教師モデルと生徒モデル:** 教師モデルは大量のデータで訓練された複雑なモデルであり、生徒モデルは教師モデルよりも少ない量のデータで訓練されるシンプルなモデルです。
2. **知識転送:** 生徒モデルは教師モデルの出力分布に基づいて、自身のパラメータを調整することで、教師モデルの知識を習得します。
3. **評価:** 生徒モデルの性能をテストし、必要に応じて再トレーニングを行います。

### 利点

- **効率性向上:** 生徒モデルは教師モデルよりも少ないリソースで動作できます。
- **汎化能力:** 生徒モデルは元の教師モデルと同じタスクに対して高い精度を持つことが期待されます。
  
### 注意点

- **知識の質:** 生徒モデルが本当に教師モデルの知識を正確に転送できるかどうかは、事前準備やハイパーパラメータ設定などによって異なります。
- **適切な選択:** 生徒モデルのサイズや複雑さは、教師モデルの特性や目的とするタスクに合わせて慎重に選択する必要があります。

このような理由から、知識蒸留は特に画像認識や自然言語処理などの分野で、大規模なモデルの知識を有効活用しながらも計算資源を節約したい場合に有用な手法として注目されています。


```py
# 2. prepare inputs
text = "Databricksについて簡単に教えてください。"
messages = [{"role": "user", "content": text}]
input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

# 3. generate
output_ids = model.generate(
    input_ids.to(device),
    max_new_tokens=1024,
)
output_ids = output_ids[:, input_ids.shape[1] :]
generated_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
print(generated_text)
```

Databricksは、Apache Sparkをベースにしたオープンソースのデータ分析プラットフォームです。

**主な特徴:**

* **スケーラビリティ:** 大量のデータとユーザーに対応できるよう設計されており、クラウドやオンプレミス環境での利用が可能です。
* **統合性:** さまざまなデータ源（Hadoop、SQLデータベースなど）からデータを読み込み、処理し、書き出すことができます。
* **並列計算:** Sparkの分散コンピューティング機能により、大量のデータに対して高速かつ効率的に処理を行うことが可能です。
* **機械学習:** 機械学習モデルのトレーニングや予測に使用できます。MLflowなどのツールとの連携も可能となっています。
* **セキュリティ:** データ暗号化やアクセス制御などのセキュリティ対策が施されています。

これらの特長により、企業はデータ駆動型意思決定を行い、ビジネスプロセスを自動化したり、新しいサービスを開発したりすることができます。


**用途例:**
- BI/OLAP (ビジネスインテリジェンス/オンライン分析処理)
- ビッグデータ分析
- エンタープライズAI
- モバイルアプリケーション

このように、Databricksは幅広い業界で活用されている強力なデータ分析プラットフォームと言えます。

---

サクサク動きますね。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

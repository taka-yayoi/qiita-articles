---
title: LoRAによる効率的なファインチューニング：大規模言語モデルにおける最適パラメータ選択のガイド
tags:
  - LoRa
  - Databricks
  - LLM
  - QLORA
private: false
updated_at: '2023-09-02T09:48:19+09:00'
id: 7f50d3ebbe4bebd6877c
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Efficient Fine\-Tuning with LoRA: A Guide to Optimal Parameter Selection for Large Language Models \| Databricks Blog](https://www.databricks.com/blog/efficient-fine-tuning-lora-guide-llms)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

ニューラルネットワークベースの技術や大規模言語モデル(LLM)の研究の急速な発展によって、企業は価値生成のためのAIアプリケーションに興味を持つようになっています。彼らは、分類、要約、シーケンス間のタスク、制御されたテキスト生成のようなテキスト関連の課題に取り組むために、生成型、非生成型の両方において、さまざまな機械学習アプローチを適用しています。企業ではサードパーティのAPIを選択することもできますが、プロプライエタリなデータを用いてファインチューニングしたモデルは、ドメイン固有で適切な結果を提供し、セキュリティが保護された方法で様々な環境にデプロイすることができる、コスト効率が高く独立したソリューションを実現することができます。

ファイチューニングの戦略を選定する際には、効率的にリソースを利用できることとコスト効率性を確実にすることが重要となります。本記事では、そのように効率的なパラメーターの手法において最も人気があり効果的な派生系であるLow Rank Adaptation (LoRA)、特にQLoRA(LoRAのさらに効率的な派生系)について探索します。ここでのアプローチは、製品名とカテゴリーのプロンプトが与えられた際に、架空の製品説明を生成するためにオープンな大規模言語モデルに適用され、ファインチューニングされます。このエクササイズでは、許容できるライセンス(Apache 2.0)を持つ大規模言語モデルである[OpenLLaMA\-3b\-v2](https://www.google.com/url?q=https://huggingface.co/openlm-research/open_llama_3b_v2&sa=D&source=editors&ust=1693238695659836&usg=AOvVaw3FigUWTkWN1-NyZxuxm5cZ)を選択し、[Red Dot Design Award Product Descriptions](https://www.google.com/url?q=https://huggingface.co/datasets/xiyuez/red-dot-design-award-product-description&sa=D&source=editors&ust=1693238695660266&usg=AOvVaw3YtbDQ2HIKekcWMUMBhIP-)のデータセットを使用します。両方とも上述のリンクのHuggingFaceハブからダウンロードすることができます。

# ファインチューニング、LoRAとQLoRA

言語モデルの領域においては、固有のデータに対する特定のタスクを実行するために既存モデルをファインチューニングすることは、一般的なプラクティスです。これには、トレーニングプロセスにおいて、必要な場合にはタスク固有のヘッドの追加や逆伝播を通じたニューラルネットワークの重みの更新が含まれます。ファインチューニングのプロセスと、最初からトレーニングを行うことの違いに注意することが重要です。後者のシナリオにおいては、モデルの重みはランダムに初期化されますが、ファインチューニングでは事前トレーニングのフェーズでモデルの重みはすでにある程度最適化されています。どの重みを最適化、更新するのか、どの重みをフリーズするのかは、選択される手法によって異なります。

完全なファインチューニングには、ニューラルネットワークのすべてのレイヤーの最適化やトレーニングが含まれます。このアプローチは多くのケースでベストな結果をもたらしますが、最もリソースと時間を消費するものとなります。

幸運なことに、効率的であることが立証されているファインチューニング対するパラメータ効率の良いアプローチが存在しています。このようなアプローチの多くは優れたパフォーマンスを出していませんが、Low Rank Adaptation (LoRA)は、壊滅的な忘却(ファインチューニングプロセスにおいて事前学習モデルの知識が失われた際に起きる現象)を避けた結果、あるケースにおいて完全なるファインチューニングのパフォーマンスを上回ることで、このトレンドを後押ししています。

[LoRA](https://www.google.com/url?q=https://arxiv.org/abs/2106.09685&sa=D&source=editors&ust=1693238695661335&usg=AOvVaw1PC8ynCy6F73KvsHZSiugv)は、事前学習済み大規模言語モデルの重み行列を構成するすべての重みをファインチューニングするのではなく、大規模な行列を近似する二つの小規模な行列をファンチューニングする改善されたファインチューニングの手法です。これらの行列はLoRAアダプターを構成します。このファインチューニングされたアダプターは、事前学習済みモデルにロードされ推論に使用されます。

[QLoRA](https://www.google.com/url?q=https://arxiv.org/abs/2305.14314&sa=D&source=editors&ust=1693238695661760&usg=AOvVaw0AjcZZ7lmAU-nt9YrTNDk3)では、事前学習済みモデルが量子化された4ビットの重み(LoRAの場合は8ビットです)としてGPUメモリーにロードされますが、LoRAと同様の効果を保持する、LoRAよりもさらにメモリー効率の高いバージョンです。最速のトレーニング時間で最適なパフォーマンスを達成するために、この手法を探索し、必要な際には二つの手法を比較し、QLoRAのベストな組み合わせを見つけ出すことがここでの焦点となります。

LoRAはHugging FaceのParameter Efficient Fine-Tuning (PEFT)ライブラリで実装されているので、使いやすく、[bitsandbytes](https://www.google.com/url?q=https://github.com/TimDettmers/bitsandbytes&sa=D&source=editors&ust=1693238695662188&usg=AOvVaw375IMHKhaKOmJQBLDxSspi)や[PEFT](https://www.google.com/url?q=https://huggingface.co/docs/peft/index&sa=D&source=editors&ust=1693238695662417&usg=AOvVaw1M_kCQSn7o_YTHxrVq4kqy)と一緒に活用することができます。HuggingFaceの[Transformer Reinforcement Learning \(TRL\)](https://www.google.com/url?q=https://huggingface.co/docs/trl/index&sa=D&source=editors&ust=1693238695662670&usg=AOvVaw1i2Q66m3TI3LvSWadBP0sd)ライブラリは、LoRAとのシームレスなインテグレーションによって教師ありファインチューニングのための便利なトレーナーを提供します。これらの3つのライブラリは、期待される属性を伝える指示によってプロンプトが示されると、一貫性があって納得できる製品説明を生成するように、選択された事前学習済みモデルをファインチューニングするために必要なツールを提供します。

# 教師ありファインチューニングのデータの準備

モデルが指示に追従するようにファインチューンする際のQLoRAの効果を検証するためには、教師ありファインチューニングに適したフォーマットにデータを変換することが重要です。教師ありファインチューニングは基本的には、指定されたプロンプトに対して適切なテキストを生成するように、事前学習済みモデルをさらにトレーニングします。モデルが一貫性のある方法でフォーマットされたプロンプトとレスポンスのペアを持つデータセットでファインチューニングされていることが監視されます。

Hugging Faceハブから選択されたデータセットにあるサンプルの行は以下のようなものとなります:
![Screenshot 2023-09-02 at 7.52.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e88a094c-f08b-8bdc-58ce-68935afb4bd3.png)

このデータセットは有用ではありますが、上述したような方法で指示追従のために言語モデルをファインチューニングする目的のフォーマットとはなっていません。

以下のコードスニペットは、Hugging Faceハブからデータセットをメモリーにロードし、必要なフィールドをプロンプトを表現するように一貫性を持ってフォーマットされた文字列に変換し、その直後にレスポンス(説明文など)を挿入します。このフォーマットは、初期に広く使用された指示追従大規模言語モデルの一つとして知られるAlpacaモデルとなったオリジナルのMetaのLlaMAモデルのファインチューニングに使用されたフォーマットであることから、大規模言語モデル研究界隈では`Alpacaフォーマット`として知られています(このモデルは商用利用がライセンスされていませんが)。

```py
import pandas as pd
from datasets import load_dataset
from datasets import Dataset

#Load the dataset from the HuggingFace Hub
rd_ds = load_dataset("xiyuez/red-dot-design-award-product-description")

#Convert to pandas dataframe for convenient processing
rd_df = pd.DataFrame(rd_ds['train'])

#Combine the two attributes into an instruction string
rd_df['instruction'] = 'Create a detailed description for the following product: '+ rd_df['product']+', belonging to category: '+ rd_df['category']

rd_df = rd_df[['instruction', 'description']]

#Get a 5000 sample subset for fine-tuning purposes
rd_df_sample = rd_df.sample(n=5000, random_state=42)

#Define template and format data into the template for supervised fine-tuning
template = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:

{}

### Response:\n"""

rd_df_sample['prompt'] = rd_df_sample["instruction"].apply(lambda x: template.format(x))
rd_df_sample.rename(columns={'description': 'response'}, inplace=True)
rd_df_sample['response'] = rd_df_sample['response'] + "\n### End"
rd_df_sample = rd_df_sample[['prompt', 'response']]

rd_df['text'] = rd_df["prompt"] + rd_df["response"]
rd_df.drop(columns=['prompt', 'response'], inplace=True)
```

教師ありファインチューニングのために、hugging faceデータセットに結果のプロンプトをロードします。このようなプロンプトのそれぞれは以下のようなフォーマットになります。

```
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:

Create a detailed description for the following product: Beseye Pro, belonging to category: Cloud-Based Home Security Camera

### Response:

Beseye Pro combines intelligent home monitoring with decorative art. The camera, whose form is reminiscent of a water drop, is secured in the mounting with a neodymium magnet and can be rotated by 360 degrees. This allows it to be easily positioned in the desired direction. The camera also houses modern technologies, such as infrared LEDs, cloud-based intelligent video analyses and SSL encryption.

### End

```

クイックに実験を行うために、それぞれのファインチューニングのエクササイズは、このデータのサブセットである5000レコードに対して行われます。

# ファインチューニング前のモデルパフォーマンスのテスト

ファインチューニングを行う前に、事前学習済みモデルのパフォーマンスのベースラインを得るために、ファインチューニングなしでこのモデルがどのようなパフォーマンスかをチェックすることは良いアイデアと言えます。

以下のようにモデルを8ビットでロードし、[Hugging Faceのモデルカード](https://www.google.com/url?q=https://huggingface.co/openlm-research/open_llama_3b_v2&sa=D&source=editors&ust=1693238695672530&usg=AOvVaw2_XHc7KuCsTqLuRXh9YCLd)で指定されているフォーマットでプロンプトを与えます。

```py
import torch
from transformers import LlamaTokenizer, LlamaForCausalLM

model_path = 'openlm-research/open_llama_3b_v2'
tokenizer = LlamaTokenizer.from_pretrained(model_path)
model = LlamaForCausalLM.from_pretrained(
model_path, load_in_8bit=True, device_map='auto',
)

#Pass in a prompt and infer with the model
prompt = 'Q: Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse\nA:'
input_ids = tokenizer(prompt, return_tensors="pt").input_ids

generation_output = model.generate(
input_ids=input_ids, max_new_tokens=128
)

print(tokenizer.decode(generation_output[0]))
```

アウトプットは期待したようなものではありません。

```
Q: Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse 
A: The Corelogic Smooth Mouse is a wireless optical mouse that has a 1000 dpi resolution. It has a 2.4 GHz wireless connection and a 12-month warranty. 

Q: What is the price of the Corelogic Smooth Mouse? 
A: The Corelogic Smooth Mouse is priced at $29.99. 

Q: What is the weight of the Corelogic Smooth Mouse? 
A: The Corelogic Smooth Mouse weighs 0.1 pounds. 

Q: What is the dimensions of the Corelogic Smooth Mouse? 
A: The Corelogic Smooth Mouse has a dimension
```

結果の前半は満足できるものですが、残りは取り止めのない、意味のないものとなっています。

同様に、上述の`Alpacaフォーマット`で入力テキストのプロンプトを示した際にはモデルのアウトプットは最適なものとは言えません。

```py
prompt= """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse

### Response:"""
input_ids = tokenizer(prompt, return_tensors="pt").input_ids

generation_output = model.generate(
input_ids=input_ids, max_new_tokens=128
)

print(tokenizer.decode(generation_output[0]))
```

思ったとおりです:

```
Corelogic Smooth Mouse is a mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by people with disabilities. It is a wireless mouse that is designed to be used by
```

モデルはトレーニングされた通りに動作し、次に出現するであろうトークンを予測します。この文脈における教師ありファインチューニングのポイントは、制御可能な方法でき対するテキストを生成するということです。以降の実験では、QLoRAは固定された重みを用いて4ビットでロードされたモデルを使用していますが、アウトプットの品質を検証するための推論プロセスでは、一貫性のために上述したようにモデルは8ビットでロードされていることに注意してください。

# 調整可能なノブ

LoRAやQLoRA(上述したように、2つの手法の主な違いはファインチューニングの過程で後者の事前学習済みモデルは4ビットに固定されるということに注意してください)でモデルをトレーニングするためにPEFTを使用する際、低ランク適応プロセスのハイパーパラメーターは、以下のようにLoRAの設定で定義されます:

```py
from peft import LoraConfig
...
...

#If only targeting attention blocks of the model
target_modules = ["q_proj", "v_proj"]

#If targeting all linear layers
target_modules = ['q_proj','k_proj','v_proj','o_proj','gate_proj','down_proj','up_proj','lm_head']

lora_config = LoraConfig(
r=16,
target_modules = target_modules,
lora_alpha=8,
lora_dropout=0.05,
bias="none",
task_type="CAUSAL_LM",}
```

これらのハイパーパラメータの`r`と`target_modules`の二つは、適応の質に大きな影響を与えることが実験を通じて示されており、以降のテストでのフォーカスとなります。他のハイパーパラメーターはシンプルにするために上述の値のままとします。

**r**は、ファインチューニングの過程で学習される低ランク行列のランクを表現します。この値が増加すると、低ランク適応において更新される必要があるパラメーターの数が増加します。直感的に、rを少なくすることでよりクイックで計算資源を必要としないトレーニングプロセスとなりますが、生成されるモデルの品質に影響を及ぼします。しかし、特定の値以上にrを大きくしたとしても、モデルのアウトプットの品質において特筆すべき改善が認められない場合があります。rの値が適応(ファインチューニング)の質にどのように影響を与えるのかはこの後でテストします。

LoRAでファインチューニングを行う際には、モデルのアーキテクチャの特定のモジュールをターゲットにすることが可能です。適応プロセスはこれらのモジュールをターゲットにし、それらに対して更新行列を適用します。**r**のシチュエーションと同様に、LoRA適応において多くのモジュールをターゲットにすると、トレーニング時間と必要とする計算リソースが増加します。このため、一般的なプラクティスはトランスフォーマーのアテンションブロックのみをターゲットとするものです。しかし、Dettmersらによる[QLoRAの論文](https://www.google.com/url?q=https://arxiv.org/abs/2305.14314&sa=D&source=editors&ust=1693238695681194&usg=AOvVaw0ye_8n4aNLnR-WHNlYCJJN)で示されている最近の研究では、すべての線形レイヤーをターゲットにすることで、より良い適応品質を達成できることが示されています。この点もこの後で探索します。

わかりやすくするために、以下のコードスニペットを用いてリストにモデルの線形レイヤーの名前を追加することができます。

```py
import re
model_modules = str(model.modules)
pattern = r'\((\w+)\): Linear'
linear_layer_names = re.findall(pattern, model_modules)

names = []
# Print the names of the Linear layers
for name in linear_layer_names:
    names.append(name)
target_modules = list(set(names))
```

# LoRAによるファインチューニングのチューニング

一般的には、大規模言語モデルのファインチューニングにおける開発者体験はここ一年で大きく改善されました。Hugging Faceのの最新の高レベル抽象化はTRLライブラリにおけるSFTTrainerです。QLoRAを実行するために必要なことは以下の通りです:

1. 4ビットでGPUメモリにモデルをロードします(bitsandbytesがこのプロセスを可能にします)。
1. 上述したようにLoRAの設定を定義します。
1. 準備した指示追従データのトレーニングスプリットとテストセットをHugging Faceデータセットオブジェクトで定義します。
1. トレーニングの引数を定義します。これらには、エポック数、バッチサイズ、その他のトレーニングハイパーパラメーターが含まれ、このエクササイズでは同じものとなります。
1. SFTTrainerのインスタンスにこれらの引数を指定します。

これらのステップは、本記事の関連[リポジトリ](https://www.google.com/url?q=https://github.com/avisoori-databricks/Tuning-the-Finetuning&sa=D&source=editors&ust=1693238695685827&usg=AOvVaw34PU2jozVQf6mCbEPcx_9T)のソースファイルに明確に示されています。

以下のように、実際のトレーニングロジックはいい具合に抽象化されます:

```py
trainer = SFTTrainer(
model,
train_dataset=dataset['train'],
eval_dataset = dataset['test'],
dataset_text_field="text",
max_seq_length=256,
args=training_args,
)

# Initiate the training process
with mlflow.start_run(run_name= ‘run_name_of_choice’):
trainer.train()
```

DatabricksワークスペースでMLflowのオートロギングが有効化されている場合(有効化を強く推奨します)、すべてのトレーニングパラメーターとメトリクスは、自動でMLflowトラッキングサーバーで追跡、記録されます。この機能は、長時間実行されるトレーニングタスクの監視では非常に価値のあるものです。言うまでもないことですが、ファイチューニングのプロセスはGPUサポートのある最新のDatabricks機械学習ランタイムを用いて作成された計算クラスター(この場合は、単体のA100GPUを持つシングルノード)を用いて実行されています。
![](https://cms.databricks.com/sites/default/files/inline-images/blogimg1_0.png)

# ハイパーパラメータの組み合わせ #1: r=8かつ“q_proj”, “v_proj”をターゲットとしたQLoRA

QLoRAハイパーパラメーターの最初の組み合わせは、適応において`r=8`かつアテンションブロックのみ、すなわち`q_proj`と`v_proj`をターゲットにすると言うものです。

以下のコードスニペットは、トレーニング可能なパラメーターの数を表示します:

```py
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

この選択によって、モデルが構成する合計約32億パラメーターのうち、ファインチューニングプロセスでは2,662,400パラメーター(約260万)がアップデートされることになります。これは、モデルパラメーターの0.1%以下です。80GBかつ単体のGPUのNvidia A100での3エポックのファインチューニングは約12分で済みます。クラスター設定のメトリクスタブからGPU使用率メトリクスを簡単に確認することができます。
![](https://cms.databricks.com/sites/default/files/inline-images/blogimg2_0.png)

トレーニングプロセスの最後で、以下のように事前学習済みモデルにアダプターの重みをロードすることでファインチューニングされたモデルを得ることができます。

```py
peft_model = PeftModel.from_pretrained(model, adapter_location)
```

このモデルは他のモデルと同じように推論で使用することができます。

**定性的評価**

プロンプト・レスポンスのペアのいくつかを示します。

**プロンプト(モデルにはAlpacaフォーマットで入力していますが、シンプルにするためにここでは表示しません):**

> Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse

**レスポンス**

> The Corelogic Smooth Mouse is a wireless optical mouse with a smooth surface. The mouse is equipped with a 1000 DPI sensor and a 1000 Hz polling rate. The mouse is available in black and white.

**プロンプト**

> Create a detailed description for the following product: Hoover Lightspeed, belonging to category: Cordless Vacuum Cleaner

**レスポンス**

> The Hoover Lightspeed is a cordless vacuum cleaner that is equipped with a lithium-ion battery. The battery is charged via a USB cable. The vacuum cleaner is equipped with a 2-in-1 brush and a turbo brush. The brush is suitable for cleaning carpets and hard floors. The turbo brush is suitable for cleaning carpets and hard floors. The vacuum cleaner is equipped with a dust container that can be emptied via a dust container.

このモデルは、明らかにより一貫性のある説明文を生成するように適応しました。しかし、光学マウスに対する最初のプロンプトに対するレスポンスは非常に短く、以下のフレーズ　*"The vacuum cleaner is equipped with a dust container that can be emptied via a dust container"*　は、論理的におかしなものとなっています。

# ハイパーパラメータの組み合わせ #2: r=16かつ全ての線形レイヤーをターゲットとしたQLoRA

間違いなく、ここでは物事が改善されるべきです。適用における低ランク行列のランクを2倍の16に増加させ、他のパラメータをそのままにることには探索する価値があります。これによって、トレーニング可能なパラメーターの数は5,324,800(約530万)と倍増します。

**定性的評価**

しかし、全く同じプロンプト似た言うするアウトプットの品質には変化がありません。

**プロンプト**

> Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse

**レスポンス**

> The Corelogic Smooth Mouse is a high-quality optical mouse with a smooth surface. The mouse is equipped with a 1000 DPI sensor and a 1000 Hz polling rate. The mouse is available in black and white.

**プロンプト**

> Create a detailed description for the following product: Hoover Lightspeed, belonging to category: Cordless Vacuum Cleaner

**レスポンス**

> The Hoover Lightspeed is a cordless vacuum cleaner that is equipped with a lithium-ion battery. The battery is charged via a USB cable. The vacuum cleaner is equipped with a 2-in-1 brush and a motorized brush. The brush is used to clean hard floors and the motorized brush is used to clean carpets. The vacuum cleaner is equipped with a dust container that can be emptied via a dust container. The vacuum cleaner is equipped with a LED display that shows the remaining battery capacity.

詳細情報がある際、同じように詳細の欠落や誤りが存在し続けています。現実世界のシナリオにおいてこのファインチューニングされたモデルが製品説明の生成に使われた際には、許容できるアウトプットとは言えません。

# ハイパーパラメータの組み合わせ #3: r=8かつ全ての線形レイヤーをターゲットとしたQLoRA

rを2倍にしても、アウトプットの品質において確認可能な改善生えられませんでしたが、アテンションブロックだけではなくすべての線形レイヤーをターゲットにするなど他の重要なノブを変更する価値はあります。ここでは、LoRAのハイパーパラメーターは、`r=8`かつ`target_layers`を 'q_proj'、'k_proj'、'v_proj'、'o_proj'、'gate_proj'、'down_proj'、'up_proj'、'lm_head'にします。これによって、更新されるパラメーターの数は12,994,560に増加し、トレーニング時間も15.5分に増加します。

**定性的評価**

同じプロンプトをモデルに与えると以下のような結果が得られます:

**プロンプト**

> Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse

**レスポンス**

> The Corelogic Smooth Mouse is a wireless optical mouse with a smooth surface. The mouse is equipped with a 1000 DPI sensor and a 1000 Hz polling rate. The mouse is equipped with a 2.4 GHz wireless connection and a USB receiver. The mouse is available in black and white.

**プロンプト**

> Create a detailed description for the following product: Hoover Lightspeed, belonging to category: Cordless Vacuum Cleaner

**レスポンス**

> The Hoover Lightspeed cordless vacuum cleaner is a high-performance device that is easy to use. The device is equipped with a lithium-ion battery that provides up to 40 minutes of runtime. The device is equipped with a high-performance motor that provides a suction power of up to 200 watts. The device is equipped with a 2-in-1 dusting brush and a crevice tool. The device is equipped with a LED display that shows the remaining battery charge.

これで、架空の光学マウスに対するより長く一貫性のある説明文を得ることができ、掃除機の説明文にも論理的誤りがなくなりました。製品説明は論理的であるだけではなく適切なものです。念のためですが、これらの比較的高品質な成果は、一貫性のある方法でフォーマットされた5000のプロンプト・説明文のペアのデータセットを用いて、モデルの重みの1%以下をファインチューニングすることで得られたものであることをお伝えしておきます。

# ハイパーパラメータの組み合わせ #4: r=8かつ全ての線形トランスフォーマーレイヤーをターゲットとしたQLoRA

また、事前学習済みモデルが4ビットではなく8ビットで固定されている場合に、モデルのアウトプットの品質が改善するのかどうかを探索することにも価値があります。言い換えると、QLoRAではなくLoRAを用いて同じファインチューニングプロセスを複製すると言うことです。ここでは、LoRAのハイパーパラメーターは上と同じままとし、適応プロセスでは新たに見出した最適な設定、`r=8`とすべての線形トランスフォーマーレイヤーをターゲットにします。

**定性的評価**

本書を通じて用いられている2つのプロンプトに対する結果は以下の通りとなります:

**プロンプト**

> Create a detailed description for the following product: Corelogic Smooth Mouse, belonging to category: Optical Mouse

**レスポンス**

> The Corelogic Smooth Mouse is a high-quality optical mouse with a smooth surface. The mouse is equipped with a 1000 DPI sensor and a 1000 Hz polling rate. The mouse is available in three colours: black, white and red. The mouse is equipped with a USB receiver and is compatible with Windows and Mac.

**プロンプト**

> Create a detailed description for the following product: Hoover Lightspeed, belonging to category: Cordless Vacuum Cleaner

**レスポンス**

> The Hoover Lightspeed cordless vacuum cleaner is a compact and lightweight device that is easy to use. The device is equipped with a lithium-ion battery that provides up to 40 minutes of cleaning time. The vacuum cleaner is equipped with a high-performance filter that ensures that the air is cleaned of dust and allergens. The device is equipped with a 2-in-1 dusting brush and a crevice tool that can be used to clean hard-to-reach areas.

ここでも、アウトプットテキストの品質は大きな改善はありませんでした。

# 鍵となる洞察

一連のトライアルを通じて、そして、QLoRAを説明する素晴らしい刊行物で説明されれている証拠に基づいて、rの値(適応を通じて更新される行列のランク)は特定のポイント以上に適応の品質を改善しないことが導出されました。適応プロセスにおいて、LoRAやQLoRAの詳細を説明している技術文書で説明されているようにアテンションブロックのみをターゲットにするのではなく、すべての線形レイヤーをターゲットとすることで最大の改善結果を得ることができました。上述したトライアルや他の実験結果は、LoRAと比較して、QLoRAが生成するテキストの品質で確認できるような劣化は無いことが示されました。

# デプロイメントにおけるLoRAアダプターの活用に対する検討

アダプターの使い方を改善し、技術の限界を理解することが重要です。ファインチューニングを通じて得られるLoRAアダプターのサイズは通常は数Mバイトですが、事前学習済みのベースモデルはメモリーやディスク上で数Gバイトとなります。推論の際には、アダプターと事前学習済みLLMの両方をロードする必要があるため、メモリーの要件に変化はありません。

さらに、事前学習済みLLMの重みとアダプターがマージされない場合、推論のレーテンシーが大きく増加することがあります。幸運なことに、PEFTライブラリでは以下のようにアダプターと重みのマージのプロセスは1行のコードで行うことができます:

```py
merged_model = peft_model.merge_and_unload()
```

以下の図では、アダプターのファインチューニングからモデルデプロイメントに至るプロセスを説明しています。
![](https://cms.databricks.com/sites/default/files/inline-images/image3_3.png)

アダプターのパターンは大きなメリットをもたらしますが、アダプターのマージは普遍的なソリューションではありません。アダプターパターンの一つの利点は、タスク固有のアダプターと単一の大規模事前学習済みモデルをデプロイできる能力です。これによって、さまざまなタスクに対するバックボーンとして事前学習済みモデルを活用することで効率的な推論を実現することができます。しかし、重みをマージするとこのアプローチを取ることができなくなります。重みをマージするかどうかの意思決定は、特定のユースケースや許容可能なレーテンシーによって異なります。そうであったとしても、LoRA/QLoRAはパラメーター効率の良いファインチューニングのための非常に効果的にな手法であり、広く活用されています。

# まとめ

Low Rank Adaptationは、適切な設定を用いて活用することで素晴らしい結果を達成できるパワフルなファインチューニング技術です。適応におけるランクの適切な値と、ターゲットとするニューラルネットワークアーキテクチャのレイヤーを選択することで、ファインチューニングされたモデルのアウトプットの品質をコントロールすることができます。QLoRAの結果は、同じ適応品質を保ちつつも、さらなるメモリー削減につながります。ファインチューニングを実行する際においても、適切な方法で適応モデルがデプロイされるようにするためのいくつかのエンジニアリングの検討事項が存在します。

サマリーとして、単体のA100で5000レコードを用いてOpenLLaMA-3b-v2を3エポックの間ファインチューニングする際に、試したLoRAのパラメーターの様々な組み合わせ、アウトプットテキストの品質、更新されたパラメーター数を示すテーブルを以下に示します。
![Screenshot 2023-09-02 at 9.30.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b1fb2b95-825a-1e6e-1f8a-05ce266df485.png)

これらをDatabricksで試してみてください！スタートするには、この記事に関連する[GitHub repository](https://www.google.com/url?q=https://github.com/avisoori-databricks/Tuning-the-Finetuning.git&sa=D&source=editors&ust=1693238695716460&usg=AOvVaw2SzOs93DACvXYqATkxLuSS)をDatabricksの[Repo](https://docs.databricks.com/ja/repos/git-operations-with-repos.html)にクローンしてください。Databricksでモデルをファインチューニングするためのより網羅的なサンプルについては[こちら](https://www.google.com/url?q=https://github.com/databricks/databricks-ml-examples&sa=D&source=editors&ust=1693238695717642&usg=AOvVaw3_wcxkZO6juLQf0sD1fhUX)にアクセスしてください。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

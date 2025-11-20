---
title: LINEのjapanese-large-lmをDatabricksで動かしてみる
tags:
  - LINE
  - Databricks
  - LLM
private: false
updated_at: '2023-08-14T19:21:55+09:00'
id: 31dcb8be6bdecf73954d
organization_url_name: databricks
slide: false
ignorePublish: false
---
LLMのニュースが出たらとりあえず動かしてみるのがルーチンに。

https://engineering.linecorp.com/ja/blog/3.6-billion-parameter-japanese-language-model

https://huggingface.co/line-corporation/japanese-large-lm-3.6b

こちらはサンプルそのままで動きました。

```py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, set_seed
 
model = AutoModelForCausalLM.from_pretrained("line-corporation/japanese-large-lm-3.6b", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("line-corporation/japanese-large-lm-3.6b", use_fast=False)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)
set_seed(101)
 
text = generator(
    "おはようございます、今日の天気は",
    max_length=30,
    do_sample=True,
    pad_token_id=tokenizer.pad_token_id,
    num_return_sequences=5,
)
 
for t in text:
  print(t)
```

> {'generated_text': 'おはようございます、今日の天気は雨模様ですね。梅雨のこの時期の 朝は洗濯物が乾きにくいなど、主婦にとっては悩みどころですね。 では、'}
{'generated_text': 'おはようございます、今日の天気は晴れ。 気温は8°C位です。 朝晩は結構冷え込むようになりました。 寒くなってくると、...'}
{'generated_text': 'おはようございます、今日の天気は曇りです。 朝夕が寒... 記事を読む いよいよです。 おはようございます、今朝も雨です、 今朝は、本当に冷えています'}
{'generated_text': 'おはようございます、今日の天気は晴れ曇りです。 4月も半ばになり、新しい環境にも慣れてきた時期でしょうか! 最近、毎日暑い日が続きますね!'}
{'generated_text': 'おはようございます、今日の天気は晴れ。今日は晴れ間の多い1日となりそうですね。今日も元気にスタートだ。今日の仕事は、午前中から夕方だ!1'}

別の質問でも。

```py
text = generator(
    "大規模言語モデルとは",
    max_length=100,
    do_sample=True,
    pad_token_id=tokenizer.pad_token_id,
    num_return_sequences=1,
)
print(text[0]['generated_text'])
```

> 大規模言語モデルとは、従来のテキストマイニングが Word2Vec などの 中間表現としてテキストを word 列に 分割することを特徴としているのに対し、 word 列ではなくベクトルの列を出力するようにしたモデルをさします。 word ではなくベクトルとして出力することで、多義語や表記揺れなどの精度向上が可能になります。 大規模言語モデルでは、テキストの語彙を空間的に分割し、階層構造を仮定した 表現を学習することが必要になります。

うーむ。合っているようなそうでないような。

お約束の質問。

```py
text = generator(
    "Databricksとは",
    max_length=100,
    do_sample=True,
    pad_token_id=tokenizer.pad_token_id,
    num_return_sequences=1,
)
print(text[0]['generated_text'])
```

何か他のものと混ざっているような。

> Databricksとは2010年にカナダで設立された、クラウド基盤をベースにしたBI/DWHソリューションを提供しています。現在、世界で4,000社以上のお客様にデータ統合のプラットフォームとして導入されています。同社は、データ統合のエキスパートで、独自のエンタープライズソリューションで、企業のビジネスアナリティクスの促進を支援しています。【補足情報】セミナーについて開催日時:2013年12月5日(木曜日)時間:16:00~18:0

パッと試しただけですが、業種特化の質問じゃ無い方が良さそうです。

```py
text = generator(
    "日本最大の湖",
    max_length=100,
    do_sample=True,
    pad_token_id=tokenizer.pad_token_id,
    num_return_sequences=1,

)
for t in text:
  print(t['generated_text'])
```

> 日本最大の湖
本文: 琵琶湖は滋賀県大津市から南に約65kmの滋賀県最大の湖。滋賀県唯一の一級河川で、河川名は豊臣秀次が琵琶湖の北、瀬田村の地に新城を築いたところが由来。南北に長くのびる琵琶湖の面積は約670.4平方キロ、湖面は260km2、最大水深は約108m。琵琶湖を一周するドライブコースはおすすめ。
>
> タイトル:

いずれにしても、商用利用可能なLLMが増えてくるのは喜ばしい限りです。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

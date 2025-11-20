---
title: 大規模言語モデルに声を与える
tags:
  - RaspberryPi
  - Databricks
  - LLM
  - DBRX
private: false
updated_at: '2024-09-02T21:28:38+09:00'
id: b88d47bcfabf2f6bfa48
organization_url_name: databricks
slide: false
ignorePublish: false
---
今週は夏休みをいただいています。なので、夏休みの宿題的に。

ずっと前に買ったRaspberry Pi(Zero W)をしばらく放置していたのですが、何かに使えないかなと思っていたら、最近流行りのLLMと組み合わせるのはどうだと。

Databricksなら[REST API経由で簡単にLLMを呼び出せる](https://docs.databricks.com/ja/machine-learning/foundation-models/index.html)ので、そちらを使わせてもらいます。エッジデバイスを使えるということで入出力の幅が広がっているということで、まずはLLMに喋ってもらうことにしました。OpenAIにもすでに同様のインタフェース(音声によるやりとり)は実装されていますが、オープンソースLLMでもそういうことができたらいいなと思いまして。

# モデルサービングエンドポイントの確認

DBRX InstructのURLを確認し、[パーソナルアクセストークン](https://docs.databricks.com/ja/dev-tools/auth/pat.html)を作成しておきます。LLMの呼び出しに必要になります。

![Screenshot 2024-09-02 at 20.50.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/28575782-87cb-cc05-f926-347dc676f6a2.png)

# RaspberryPIの設定

![IMG_0799.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/23b13748-1911-8520-16b4-399edaf8992c.jpeg)

久々に起動したので、色々忘れてました。

- ネットワークの準備(2.4Hzでないとダメなの忘れてました)
- [イメージのインストール](https://www.raspberrypi.com/software/)
    - この際に、WiFiやsshの設定をします
- スピーカーの接続

# Python環境の準備

pipが入っていないので、

```sh
sudo apt install pip
```

`pip install`をそのまま実行するとエラーになるので仮想環境を作って、そこでインストールしていきます。

```sh
python3 -m venv ~/Documents/dbx
```

必要なライブラリをインストールしていきます。仮想環境の`pip`や`python`を使います。

```sh
./bin/pip install openai
```

今回、Raspberry Piに喋らせたいので、こちらを参考にライブラリを追加します。[`pyopenjtalk`](https://github.com/r9y9/pyopenjtalk/tree/master)という便利なものが。

https://chmod774.com/raspberrypi-pyopenjtalk/

```sh
sudo apt install cmake
sudo apt-get install libopenblas-dev
```

```sh
./bin/pip install scipy
./bin/pip install pyopenjtalk
```

# ロジックの実装

流れはシンプルです。

1. モデルサービングエンドポイントをRaspberry Piから呼び出してレスポンスを取得
1. pyopenjtalkでテキストを読み上げ

```py
from openai import OpenAI
import os

import pyopenjtalk
from scipy.io import wavfile
import numpy as np

import subprocess

# レスポンスの読み上げを格納する音声ファイル
wave_file = "/home/yayoi/Documents/dbx/talk.wav"

def synthesize_voice(text):
    x, sr = pyopenjtalk.tts(text)
    wavfile.write(wave_file, sr, x.astype(np.int16))

    cmd = f'/usr/bin/aplay {wave_file}'
    process = (subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           shell=True).communicate()[0]).decode('utf-8')

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
# DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url="<エンドポイントのURL>"
)

chat_completion = client.chat.completions.create(
  messages=[
  {
    "role": "system",
    "content": "あなたは好奇心旺盛な日本人の学生です。AIアシスタントに対して日本語を用いて様々な質問をします。"
  },
  {
    "role": "user",
    "content": "思いついた質問を英語の翻訳を含めず日本語で簡潔に教えてください"
  }
  ],
  model="databricks-dbrx-instruct",
  max_tokens=256
)

question = chat_completion.choices[0].message.content
print(question)
synthesize_voice(question)

chat_completion = client.chat.completions.create(
  messages=[
  {
    "role": "system",
    "content": "あなたはAIアシスタントです。質問に対して英語の翻訳を含めず日本語で簡潔に回答してください。"
  },
  {
    "role": "user",
    "content": question
  }
  ],
  model="databricks-dbrx-instruct",
  max_tokens=256
)

response = chat_completion.choices[0].message.content
print(response)
synthesize_voice(response)
```

環境変数`DATABRICKS_TOKEN`にパーソナルアクセストークンを[設定](https://unix.stackexchange.com/questions/117467/how-to-permanently-set-environmental-variables)しています。

```:~/.profile
export DATABRICKS_TOKEN=<パーソナルアクセストークン>
```

今回、質問文もLLMに考えてもらうようにしました。結構、英語が混じるのでプロンプトで調整しています。このように動作します。

<iframe width="560" height="315" src="https://www.youtube.com/embed/PDCvkigNQkA?si=D4ffrEWD12YD7OpT" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

これ、ずっと会話させておくこともできるんですよね。でも、単に1ターンのやりとりだけですとだと味気ないので、コンテキスト持たせた方が良さそうです。

他にもデバイスはあるので、色々試してみます。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

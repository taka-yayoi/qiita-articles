---
title: OpenAI Agents SDKをDatabricksで動かしてみる
tags:
  - SDK
  - OpenAI
  - Databricks
  - エージェント
private: false
updated_at: '2025-03-12T12:53:27+09:00'
id: 3161baddac7c745dcef9
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: 3173172074bd59848652
agreed_posting_campaign_term: true
---
動かします。

https://x.com/OpenAIDevs/status/1899531857143972051

> 🤖 Agents SDK - Swarmをベースとして改善したマルチエージェントワークフローをオーケストレーションする新たなオープンソースSDKです。ビルトインのツール、タスクの引き継ぎ、安全ガードレイルの追加、デバッグとパフォーマンス最適化のための実行トレースの可視化を用いてエージェントを設定します。

SDK自体はこちらに。

https://github.com/openai/openai-agents-python

# Hello Worldサンプル

```py
%pip install openai-agents
%restart_python
```

```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="demo-token-takaaki.yayoi", key="openai_api_key")
```

[Hello Worldサンプル](https://github.com/openai/openai-agents-python?tab=readme-ov-file#hello-world-example)を動かします。コメントやリテラルは翻訳しています。

```py
from agents import Agent, Runner

agent = Agent(name="アシスタント", instructions="あなたは役に立つアシスタントです")

result = Runner.run_sync(agent, "プログラミングにおける再帰について俳句を書いてください。")
print(result.final_output)

# コードの中のコード、
# 自分自身を呼び出す関数、
# 無限ループの舞。
```

しかし、**RuntimeError: This event loop is already running**とエラーになります。すでにループが実行中とな。

こちらに理由が。

https://stackoverflow.com/questions/55409641/asyncio-run-cannot-be-called-from-a-running-event-loop-when-using-jupyter-no

ノートブック環境ではすでにイベントループが実行されているので、新規に作成する必要はないので`await`すればいいとのこと。なので、以下のように`await`します。

```py
from agents import Agent, Runner

agent = Agent(name="アシスタント", instructions="あなたは役に立つアシスタントです")

result = await Runner.run(agent, "プログラミングにおける再帰について俳句を書いてください。")
print(result.final_output)

# コードの中のコード、
# 自分自身を呼び出す関数、
# 無限ループの舞。
```

動きました。

```
再帰せし  
自己を呼び出し  
解を探す
```

そして、トレースは`https://platform.openai.com/traces`で確認できます。

![Screenshot 2025-03-12 at 12.45.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/14f9b8e7-3825-4e48-99a3-6435bffbed7f.png)

# 引き継ぎサンプル

```py
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="スペイン語エージェント",
    instructions="あなたはスペイン語のみを話します。",
)

english_agent = Agent(
    name="英語エージェント",
    instructions="あなたは英語のみを話します。",
)

triage_agent = Agent(
    name="トリアージエージェント",
    instructions="リクエストの言語に基づいて適切なエージェントに引き継ぎます。",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    await main()
```

```
¡Hola! Estoy bien, gracias. ¿Y tú?
```

スペイン語エージェントに引き継がれています。

![Screenshot 2025-03-12 at 12.47.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/11cd22fd-79d9-4775-9191-cdf196dd4af5.png)

# 関数サンプル

```py
import asyncio

from agents import Agent, Runner, function_tool


@function_tool
def get_weather(city: str) -> str:
    return f"{city}の天気は晴れです。"


agent = Agent(
    name="こんにちは世界",
    instructions="あなたは役に立つエージェントです。",
    tools=[get_weather],
)


async def main():
    result = await Runner.run(agent, input="東京の天気は？")
    print(result.final_output)
    # 東京の天気は晴れです。


if __name__ == "__main__":
    await main()
```
![Screenshot 2025-03-12 at 12.49.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/eb9c4bac-5121-4288-962d-d1970558b344.png)

経緯的には[こちら(SwarmのLangchain実装)](https://qiita.com/taka_yayoi/items/29bf9f27789066d59e50)ともオーバーラップしてきてます。OpenAIのAPIだけを使うのであればOpenAI Agents SDKの方が使いやすいのかもしれません。エージェントの足回りもどんどん整備されてきていますね。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

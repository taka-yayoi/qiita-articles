---
title: MLflowのOpenAI Agent SDKトレースを試す
tags:
  - OpenAI
  - Databricks
  - MLflow
private: false
updated_at: '2025-03-31T13:07:39+09:00'
id: eab2baae38ff6627cc6a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: 3173172074bd59848652
agreed_posting_campaign_term: true
---
こちらを試します。

https://x.com/MLflow/status/1905273847101661434

マニュアルはこちら

https://mlflow.org/docs/latest/tracing/integrations/openai-agent

# 基本的な例

```py
%pip install -U mlflow openai-agents
%restart_python
```

```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="demo-token-takaaki.yayoi", key="openai_api_key")
```

```py
import mlflow
import asyncio
from agents import Agent, Runner

# OpenAI Agents SDKの自動トレースを有効にする
mlflow.openai.autolog()

# オプション: トラッキングURIと実験を設定する
# Databricksの場合は不要です
#mlflow.set_tracking_uri("http://localhost:5000")
#mlflow.set_experiment("OpenAI Agent")

# シンプルなマルチエージェントワークフローを定義する
japanese_agent = Agent(
    name="Japanese agent",
    instructions="あなたは日本語しか話せません。",
)

english_agent = Agent(
    name="English agent",
    instructions="あなたは英語しか話せません。",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="リクエストの言語に基づいて適切なエージェントに引き継ぎます。",
    handoffs=[japanese_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="こんにちは！お元気ですか？")
    print(result.final_output)


# このコードをJupyterノートブックで実行している場合は、これを `await main()` に置き換えてください。
# await main()に置き換えます
if __name__ == "__main__":
    #asyncio.run(main())
    await main()
```
```
こんにちは！はい、元気です。あなたはどうですか？
```

トレースも動きました。

![Screenshot 2025-03-28 at 8.39.38.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/095a229d-98b3-42f7-bf53-ea2b304d346d.png)

# 関数呼び出し

```py
import asyncio

from agents import Agent, Runner, function_tool

# OpenAI Agents SDKの自動トレースを有効にする
mlflow.openai.autolog()


@function_tool
def get_weather(city: str) -> str:
    return f"{city}の天気は晴れです。"


agent = Agent(
    name="Hello world",
    instructions="あなたは役に立つエージェントです。",
    tools=[get_weather],
)


async def main():
    result = await Runner.run(agent, input="東京の天気は？")
    print(result.final_output)
    # 東京の天気は晴れです。


# このコードをJupyterノートブックで実行している場合は、これを `await main()` に置き換えてください。
if __name__ == "__main__":
    #asyncio.run(main())
    await main()
```
![Screenshot 2025-03-28 at 8.40.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/94fdf0d3-18fb-40bd-9ff2-4b529e584c2d.png)

# ガードレール

```py
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

# OpenAI Agents SDKの自動トレースを有効にする
mlflow.openai.autolog()


class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str


guardrail_agent = Agent(
    name="ガードレールチェック",
    instructions="ユーザーが数学の宿題を頼んでいるかどうかを確認してください。",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(
    name="カスタマーサポートエージェント",
    instructions="あなたはカスタマーサポートエージェントです。顧客の質問に答えます。",
    input_guardrails=[math_guardrail],
)


async def main():
    # これはガードレールをトリップするはずです
    try:
        await Runner.run(agent, "こんにちは、xを解くのを手伝ってくれませんか: 2x + 3 = 11？")
        print("ガードレールがトリップしませんでした - これは予期しないことです")

    except InputGuardrailTripwireTriggered:
        print("数学の宿題ガードレールがトリップしました")


# このコードをJupyterノートブックで実行している場合は、これを `await main()` に置き換えてください。
if __name__ == "__main__":
    #asyncio.run(main())
    await main()
```
![Screenshot 2025-03-28 at 8.42.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/67ad36ea-663e-4956-9164-2d23db5aeac1.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

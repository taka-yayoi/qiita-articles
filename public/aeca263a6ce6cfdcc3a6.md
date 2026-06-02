---
title: >-
  Strands Agents を Databricks の基盤モデル + MLflow Tracing で動かす(stream_options
  のハマりどころつき)
tags:
  - Databricks
  - MLflow
  - 生成AI
  - AIエージェント
  - StrandsAgents
private: false
updated_at: '2026-06-01T13:22:15+09:00'
id: aeca263a6ce6cfdcc3a6
organization_url_name: databricks
slide: false
ignorePublish: false
---
# Strands Agents SDK とは

[Strands Agents SDK](https://strandsagents.com/) は、AWS が公開しているオープンソースのAIエージェント構築用SDKです (GitHub: [strands-agents/sdk-python](https://github.com/strands-agents/sdk-python))。外部のツールやAPIを呼び出しながら自律的に振る舞うエージェントを、数行のコードで定義できます。「モデル駆動 (model-driven)」と呼ばれるアプローチを採っているのが最大の特徴で、「どのツールをいつ呼ぶか」「いつ処理を終えるか」といった判断をモデル自身に委ね、SDK側はそのループ (エージェントループ) を回す役割に徹します。

AWS発のSDKではありますが、実体はオープンソースのPythonライブラリであり、特定のクラウドに縛られません。モデルプロバイダーは差し替え可能で、Amazon Bedrock だけでなく OpenAI 互換エンドポイントなどにも接続できます。本記事ではこの性質を利用して、AWS製SDKでありながら、モデルもトレースもすべて Databricks 上で完結させる構成を組みます。

# 主な特徴

Strands Agents の設計上のポイントは次のとおりです。

モデル駆動設計を中核に置いています。制御フローを開発者がグラフやステートマシンとして描くのではなく、システムプロンプトと利用可能なツール群をモデルに渡し、推論と行動の繰り返しをモデルに任せます。これにより、シンプルな対話エージェントから複雑な自律タスクまで、同じ書き方でスケールします。

ツール連携が容易です。Python関数に `@tool` デコレーターを付けるだけで、その docstring と型ヒントがそのままツールの仕様としてモデルに渡されます。計算や時刻取得などの組み込みツールも提供されています。

マルチエージェントのパターンを組み込みで持っています。Swarm・Graph・Workflow といった協調パターンが用意されており、複数エージェントの連携や役割分担を標準機能として表現できます。

MCP (Model Context Protocol) にネイティブ対応しています。標準化されたかたちでツールやコンテキストをモデルに供給できます。

モデルプロバイダーが柔軟です。Bedrock、OpenAI、その他のOpenAI互換エンドポイントを切り替えられます。本記事ではこの柔軟性を使って Databricks の基盤モデルエンドポイントに向けます。

# 関連製品との共通点と位置付け

エージェント開発のフレームワークは数が多く、「どれも同じに見える」状態になりがちです。レイヤー (抽象度) で整理すると見通しがよくなります。

![positioning_layers.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/de85f52d-ad39-456c-a799-433ac0612362.png)

Strands Agents と最も近いのは OpenAI Agents SDK です。どちらもモデル駆動のエージェントループSDKであり、抽象度がほぼ同じ直接の競合関係にあります。Strands のマルチエージェントパターン (Swarm / Graph / Workflow) は、OpenAI Agents SDK の handoffs に相当します。Google ADK や PydanticAI も同じレイヤーに位置します。

LangGraph はこれより一段下の、グラフ・オーケステーション層に属します。ノード・エッジ・条件分岐・状態・チェックポイント (永続化) を開発者が明示的に定義するスタイルで、制御フローの主導権がモデルではなく開発者側にあるのが本質的な違いです。ただし LangGraph も `create_react_agent` のようなプリビルトのエージェント抽象を持っており、それを使う場合は Strands や OpenAI Agents SDK と同じレイヤーまで上がってきます。「完全に別物」ではなく、ネイティブの粒度が低い、という理解が正確です。

選び分けの目安としては、モデルに自律的にループさせたい場合は Strands / OpenAI Agents SDK、ワークフローを自分で握って決定論的に制御したい場合や、状態の永続化・複雑な分岐が必要な場合は LangGraphとなります。

# Databricks での位置付け

3つのフレームワークはいずれもモデルを差し替えられるため、Databricks のサービングエンドポイントに向けることができ、MLflow Tracing による自動計装も用意されています (Strands は `mlflow.strands`、LangGraph は LangChain系のautolog経由)。

本記事で組む構成は次のとおりです。エージェントのコードは Databricks ノートブック上で動かし、推論は Databricks の基盤モデルAPI、トレースは同じ Databricks の MLflow に集約します。Bedrock を含む外部サービスを一切経由しない点がポイントです。

![strands_databricks_architecture.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5721c293-d8dd-4d67-a0a2-689ed3930ea0.png)

なお Databricks の[公式ドキュメント](https://docs.databricks.com/aws/ja/mlflow3/genai/tracing/integrations/strands)が扱っているのは、あくまで「Strandsエージェントのトレースを Databricks の MLflow に記録する」部分だけです。公式例ではモデルの向き先が本物の OpenAI API (gpt-4o) になっており、推論自体は Databricks の外で走ります。本記事のように「モデルも Databricks のエンドポイントに寄せる」構成はドキュメントの範囲外で、後述する `stream_options` の対応はそこで初めて必要になります。

# ノートブックのウォークスルー

ここからは実際に動かすノートブックを順に見ていきます。Databricks Free Edition でも動作します。利用するサービングエンドポイントがツール呼び出し (function calling) に対応している必要がある点にだけ注意してください。

## 前提とインストール

OpenAI互換プロバイダーを使うため `strands-agents[openai]`、組み込みツール用に `strands-agents-tools`、トレース用に `mlflow` を入れます。

```python
%pip install -U -q mlflow "strands-agents[openai]" strands-agents-tools
```

```python
dbutils.library.restartPython()
```

## 認証情報の取得

ノートブック内では、ワークスペースのホストとトークンをコンテキストから取得できます。ハードコードは不要です。ノートブック外 (ローカルやジョブ) で動かす場合は、環境変数 `DATABRICKS_HOST` / `DATABRICKS_TOKEN` を設定してください。

```python
ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
DATABRICKS_HOST = ctx.apiUrl().get()
DATABRICKS_TOKEN = ctx.apiToken().get()

# Databricks基盤モデルAPIのOpenAI互換エンドポイント
DATABRICKS_BASE_URL = f"{DATABRICKS_HOST}/serving-endpoints"
```

## MLflow Tracing の有効化

`mlflow.strands.autolog()` を呼ぶと、以降のエージェント実行が自動でトレースされます。サーバーレスコンピュートでは自動ログが既定で有効にならないため、この明示的な呼び出しが必要です。

```python
import mlflow

mlflow.strands.autolog()
mlflow.set_tracking_uri("databricks")

username = spark.sql("SELECT current_user()").collect()[0][0]
mlflow.set_experiment(f"/Users/{username}/strands-on-databricks")
```

## モデルの構成と stream_options への対応

`model_id` には利用するサービングエンドポイント名を指定します。`databricks-meta-llama-3-3-70b-instruct` や `databricks-claude-3-7-sonnet` など、ツール呼び出しに対応したエンドポイントを選びます。利用可能な名前は AI Gateway 画面で確認できます。

![Screenshot 2026-06-01 at 13.16.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f9ac155a-d1d4-46ce-b798-a38a5dba7c67.png)

ここで1点、Databricks 固有の対応が必要になります。`OpenAIModel` はストリーミング時に必ず `stream_options: {"include_usage": True}` をリクエストに含めますが、Databricks の基盤モデルAPIはこのフィールドを受け付けず、次のエラーで失敗します。

```
BadRequestError: Error code: 400 - {'error_code': 'BAD_REQUEST',
  'message': 'Bad request: json: unknown field "stream_options"'}
```

回避策を選ぶ際の注意点が2つあります。`params` に `"stream_options": None` を渡しても、OpenAIクライアントは値 `null` としてフィールド自体を送ってしまうため解消しません。また `stream` を `False` にするのも、Strands側が非ストリーミング応答を扱えず別のエラーになるため使えません。

確実なのは、`format_request` をオーバーライドして `stream_options` キーごと削除する方法です。`stream: True` は維持されるため、Databricks側でも問題なく動作します。

```python
from strands.models.openai import OpenAIModel


class DatabricksFMModel(OpenAIModel):
    """Databricks基盤モデルAPI向けの OpenAIModel。

    Databricksが受け付けない stream_options フィールドをリクエストから除去する。
    """

    def format_request(self, *args, **kwargs):
        request = super().format_request(*args, **kwargs)
        request.pop("stream_options", None)
        return request


MODEL_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"

model = DatabricksFMModel(
    client_args={
        "api_key": DATABRICKS_TOKEN,
        "base_url": DATABRICKS_BASE_URL,
    },
    model_id=MODEL_ENDPOINT,
    params={
        "max_tokens": 2000,
        "temperature": 0.7,
    },
)
```

`stream_options` を落とすとトークン使用量がストリームから取得できなくなりますが、トレース自体は通常どおり記録されます。

## 組み込みツールで疎通確認

まずは `strands_tools` の `calculator` と `current_time` を渡したシンプルなエージェントで動作を確認します。

```python
from strands import Agent
from strands_tools import calculator, current_time

agent = Agent(
    model=model,
    system_prompt="あなたは親切なアシスタントです。計算や時刻の取得が必要なときはツールを使ってください。",
    tools=[calculator, current_time],
)

response = agent("123 と 456 を掛けるといくつ? あわせて現在の時刻も教えてください。")
print(response)
```

![Screenshot 2026-06-01 at 13.18.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/863c543b-5e74-4eb9-ac66-4b0f2e87131e.png)

## カスタムツールを持つエージェント

`@tool` デコレーターで独自のツールを定義できます。docstring と型ヒントがそのままツール仕様になるため、説明は丁寧に書きます。

```python
from strands import tool


@tool
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """華氏温度を摂氏温度に変換する。

    Args:
        fahrenheit: 華氏温度の値

    Returns:
        摂氏温度の値
    """
    return (fahrenheit - 32) * 5.0 / 9.0


agent_with_custom_tool = Agent(
    model=model,
    system_prompt="あなたは単位変換アシスタントです。変換が必要なときはツールを使ってください。",
    tools=[fahrenheit_to_celsius],
)

response = agent_with_custom_tool("華氏100度は摂氏何度ですか?")
print(response)
```
![Screenshot 2026-06-01 at 13.18.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a2ff9c06-177c-4816-a512-58630f86779a.png)


## トレースの確認

左サイドバーの Experiments から、設定したExperiment (`/Users/<あなた>/strands-on-databricks`) を開き、Traces タブを確認します。エージェントのループ、各ツール呼び出しの入出力、モデルへのリクエストとレスポンスが階層的に記録されています。

![Screenshot 2026-06-01 at 13.19.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f4c2f0d6-ce8c-4295-bf1b-992de6b6aa2b.png)

![Screenshot 2026-06-01 at 13.19.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bada25bc-90a9-4db2-a6b0-28091d799f6e.png)


# まとめ

Strands Agents SDK は、OpenAI Agents SDK と同じ「モデル駆動エージェントSDK」レイヤーに位置するAWS製のオープンソースSDKです。モデルプロバイダーが差し替え可能なため、AWS製でありながらモデルもトレースも Databricks 上で完結させられます。

実装上の唯一の勘所は、OpenAIクライアントが送る `stream_options` を Databricks のエンドポイントが受け付けない点で、これは `format_request` を1メソッドだけオーバーライドして吸収できます。公式ドキュメントが想定していない「モデルも Databricks に寄せる」組み合わせを成立させる部分が、この構成の実用的な価値になります。

参考: [Strands Agents SDK のトレース (Databricks 日本語ドキュメント)](https://docs.databricks.com/aws/ja/mlflow3/genai/tracing/integrations/strands)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

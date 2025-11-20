---
title: DatabricksでLangGraphのクイックスタートを動かしてみる(その1)
tags:
  - Databricks
  - LangGraph
private: false
updated_at: '2025-02-04T09:54:25+09:00'
id: d6e5fd6a724eb9b65fbc
organization_url_name: databricks
slide: false
ignorePublish: false
---
LangGrahp勉強中です。

[LangGraph Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)をDatabricksでウォークスルーします。

このチュートリアルでは、LangGraphでサポートチャットボットを構築します。以下の機能を持つことができます：

✅ ウェブ検索で**一般的な質問に答える**: [その2](https://qiita.com/taka_yayoi/items/311048184657aa8ad53f) 
✅ 呼び出し間で**会話の状態を維持する**: [その3](https://qiita.com/taka_yayoi/items/255b124aae94df2e04ec)
✅ 人間がレビューできるように**複雑なクエリを人間にルーティングする**: [その4](https://qiita.com/taka_yayoi/items/e2a7fcafd21acd31eeff)
✅ **カスタム状態を使用**して動作を制御する: [その5](https://qiita.com/taka_yayoi/items/58f2434defe5257dd8da)
✅ 会話の代替パスを**巻き戻して探索する**: [その6](https://qiita.com/taka_yayoi/items/d0d264b50128aedd7e90)

基本的なチャットボットから始め、徐々により高度な機能を追加しながら、重要なLangGraphの概念を紹介していきます。さあ、始めましょう！🌟

こちらのクイックスタートのPart1 Build a Basic Chatbotを実行します。

https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot

# パート1: 基本的なチャットボットを構築する

まず、LangGraphを使用してシンプルなチャットボットを作成します。このチャットボットはユーザーのメッセージに直接応答します。シンプルですが、LangGraphでの構築の基本概念を示します。このセクションの終わりまでに、基本的なチャットボットを構築できるようになります。

**セットアップ**

まず、必要なパッケージをインストールし、環境を設定します：

```py
%%capture --no-stderr
%pip install -U langgraph langsmith langchain_openai openai
%restart_python
```
```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="demo-token-takaaki.yayoi", key="openai_api_key")
```

`StateGraph`を作成することから始めます。`StateGraph`オブジェクトは、チャットボットの構造を「状態機械」として定義します。`node`を追加してllmやチャットボットが呼び出せる関数を表し、`edge`を追加してこれらの関数間の遷移方法を指定します。

```py
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # メッセージは "list" 型を持ちます。注釈内の `add_messages` 関数は
    # この状態キーがどのように更新されるべきかを定義します
    # （この場合、リストにメッセージを追加し、上書きしません）
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
```

:::note info
**コンセプト**

グラフを定義する際の最初のステップは、その`State`を定義することです。`State`には、グラフのスキーマと状態更新を処理する[reducer関数](https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers)が含まれます。私たちの例では、`State`は1つのキー`messages`を持つ`TypedDict`です。[add_messages](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages) reducer関数は、新しいメッセージを上書きするのではなく、リストに追加するために使用されます。reducer注釈のないキーは、以前の値を上書きします。State、reducer、および関連する概念についての詳細は、[このガイド](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages)で学んでください。
:::

次に、「`chatbot`」ノードを追加します。ノードは作業単位を表します。通常、これらは通常のPython関数です。

```py
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# 最初の引数は一意のノード名です
# 二番目の引数はノードが使用されるたびに呼び出される関数またはオブジェクトです
graph_builder.add_node("chatbot", chatbot)
```

`chatbot`ノード関数が現在の`State`を入力として受け取り、キー「`messages`」の下に更新された`messages`リストを含む辞書を返す方法に**注目**してください。これはすべてのLangGraphノード関数の基本パターンです。

`State`の`add_messages`関数は、llmの応答メッセージを現在の状態に既にあるメッセージに追加します。

次に、`entry`ポイントを追加します。これにより、グラフが実行されるたびに**どこから作業を開始するか**が指定されます。

```py
graph_builder.add_edge(START, "chatbot")
```

同様に`finish`ポイントを設定します。これは、グラフに **「このノードが実行されるたびに、終了してもよい」** と指示します。

```py
graph_builder.add_edge("chatbot", END)
```

最後にグラフを実行できるようにしたいと思います。そのためには、グラフビルダーで「`compile()`」を呼び出します。これにより、状態で呼び出すことができる「`CompiledGraph`」が作成されます。

```py
graph = graph_builder.compile()
```

グラフは、`get_graph`メソッドと`draw_ascii`や`draw_png`のような「`draw`」メソッドの1つを使用して視覚化できます。`draw`メソッドはそれぞれ追加の依存関係を必要とします。

```py
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # これはいくつかの追加の依存関係を必要とし、オプションです
    pass
```

![download.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e1e14c61-81ef-915e-a20d-5b5665ea5728.png)

さあ、チャットボットを実行しましょう！

:::note info
**ヒント:** "quit"、"exit"、または "q" と入力することで、いつでもチャットループを終了できます。
:::

![Screenshot 2025-01-29 at 16.36.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/12338456-ca93-8358-0b0a-aeebfdc28523.png)

:::note info
Databricksの場合、MLflow Traceが動作してくれます。
:::

おめでとうございます！LangGraphを使用して最初のチャットボットを構築しました。このボットは、ユーザー入力を受け取り、LLMを使用して応答を生成することで基本的な会話を行うことができます。上記の呼び出しに対する[LangSmith Trace](https://smith.langchain.com/public/7527e308-9502-4894-b347-f34385740d5a/r)を提供されたリンクで確認できます。

しかし、ボットの知識はそのトレーニングデータに限定されていることに気付いたかもしれません。次の部分では、ウェブ検索ツールを追加してボットの知識を拡張し、より能力を高めます。

こちらに続きます。

https://qiita.com/taka_yayoi/items/311048184657aa8ad53f

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

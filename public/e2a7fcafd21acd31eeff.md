---
title: DatabricksでLangGraphのクイックスタートを動かしてみる(その4)
tags:
  - Databricks
  - LangGraph
private: false
updated_at: '2025-02-04T07:50:15+09:00'
id: e2a7fcafd21acd31eeff
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: fd9d012cdc6dcd0b2f5c
agreed_posting_campaign_term: true
---
こちらの続きです。

https://qiita.com/taka_yayoi/items/255b124aae94df2e04ec

こちらのPart 4: Human-in-the-loopを動かします。

https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-4-human-in-the-loop

# パート4: 人間を介したループ

エージェントは信頼性が低く、タスクを成功させるために人間の入力が必要な場合があります。同様に、いくつかのアクションについては、実行前に人間の承認を求めることで、すべてが意図した通りに動作していることを確認したい場合があります。

LangGraphの[永続](https://langchain-ai.github.io/langgraph/concepts/persistence)レイヤーは、人間を介したループワークフローをサポートしており、ユーザーのフィードバックに基づいて実行を一時停止および再開することができます。この機能の主なインターフェースは[interrupt](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/#interrupt)関数です。ノード内で`interrupt`を呼び出すと、実行が一時停止します。[Command](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/#the-command-primitive)を渡すことで、人間からの新しい入力とともに処理を再開できます。`interrupt`はPythonの組み込み`input()`と似ていますが、いくつかの注意点があります。以下に例を示します。

まず、[パート3の既存のコード](https://qiita.com/taka_yayoi/items/255b124aae94df2e04ec)から始めます。1つの変更を加えます。それは、チャットボットがアクセスできるシンプルな`human_assistance`ツールを追加することです。このツールは`interrupt`を使用して人間から情報を受け取ります。

## セットアップ

まず、必要なパッケージをインストールし、環境を設定します：

```py
%%capture --no-stderr
%pip install -U langgraph langsmith langchain_openai openai tavily-python langchain_community
%restart_python
```

```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="demo-token-takaaki.yayoi", key="openai_api_key")

# TavilyのAPIキー
os.environ["TAVILY_API_KEY"] = "TavilyのAPIキー"
```

```py
from typing import Annotated

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

@tool
def human_assistance(query: str) -> str:
    """人間のアシストをリクエスト"""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # ツールの実行時に割り込みを行うので、
    # 再開する際に全てのツールの呼び出しの繰り返しを避けるために
    # 並列ツール呼び出しを無効化します
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# 条件付きエッジを追加
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# ツールが呼び出されるたびに、次のステップを決定するためにチャットボットに戻る
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
```

:::note info
**ヒント**

ツール呼び出しが実行される前に[レビューおよび編集](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/)する方法を含む、人間を介したループワークフローの詳細な例については、How-toガイドの[人間を介したループセクション](https://langchain-ai.github.io/langgraph/how-tos/#human-in-the-loop)をチェックしてください
:::

前回同様に、提供されたチェックポインタを使用してグラフをコンパイルします。

```py
memory = MemorySaver()

graph = graph_builder.compile(checkpointer=memory)
```

グラフを視覚化すると、以前と同じレイアウトが復元されます。ツールを追加しただけです！

```py
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```
![download.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6aada35e-16fe-0e43-0083-7667d2231a31.png)

```py
新しい`human_assistance`ツールを使用してチャットボットに質問を促してみましょう:
```

```py
user_input = "AIエージェントの構築に関する専門的な指導が必要です。支援を依頼してもらえますか？"
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

AIエージェントの構築に関する専門的な指導が必要です。支援を依頼してもらえますか？
2025/01/31 01:36:47 WARNING mlflow.utils.autologging_utils: Encountered unexpected error during autologging: Span for run_id cf40b15b-9f5f-46bb-942c-d060912909c0 not found.
================================== Ai Message ==================================
Tool Calls:
  human_assistance (call_OrSxTi0C6IligP0P9kO8Js5i)
 Call ID: call_OrSxTi0C6IligP0P9kO8Js5i
  Args:
    query: AIエージェントの構築に関する専門的な指導が必要です。具体的な要件や目標を教えてほしいです。
```
![Screenshot 2025-01-31 at 10.50.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5de39e28-501e-821b-0181-5fb5eed9dc47.png)

チャットボットがツール呼び出しを生成しましたが、実行が中断されました！グラフの状態を確認すると、ツールノードで停止していることがわかります。

```py
snapshot = graph.get_state(config)
snapshot.next
```
```
('tools',)
```

`human_assistance`ツールを詳しく見てみましょう：

```py
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]
```

Pythonの組み込み関数`input()`と同様に、ツール内で`interrupt`を呼び出すと実行が一時停止します。進行状況は選択した[チェックポインタ](https://langchain-ai.github.io/langgraph/concepts/persistence/#checkpointer-libraries)に基づいて保存されます。Postgresを使用している場合、データベースが稼働している限りいつでも再開できます。ここではインメモリチェックポインタを使用しているため、Pythonカーネルが動作している限りいつでも再開できます。

実行を再開するには、ツールが期待するデータを含む[Command](https://langchain-ai.github.io/langgraph/concepts/persistence/#checkpointer-libraries)オブジェクトを渡します。このデータの形式はニーズに応じてカスタマイズできます。ここでは、`"data"`というキーを持つ辞書が必要です：

```py
human_response = (
    "私たち専門家がここにいます！エージェントを構築するにはLangGraphをチェックすることをお勧めします。"
    "シンプルな自律エージェントよりもはるかに信頼性が高く、拡張性があります。"
)

human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================== Ai Message ==================================
Tool Calls:
  human_assistance (call_OrSxTi0C6IligP0P9kO8Js5i)
 Call ID: call_OrSxTi0C6IligP0P9kO8Js5i
  Args:
    query: AIエージェントの構築に関する専門的な指導が必要です。具体的な要件や目標を教えてほしいです。
2025/01/31 01:39:24 WARNING mlflow.utils.autologging_utils: Encountered unexpected error during autologging: Span for run_id 90245db4-c5d4-4a05-8bd3-f757ce3298af not found.
================================= Tool Message =================================
Name: human_assistance

私たち専門家がここにいます！エージェントを構築するにはLangGraphをチェックすることをお勧めします。シンプルな自律エージェントよりもはるかに信頼性が高く、拡張性があります。
================================== Ai Message ==================================

AIエージェントの構築について、専門家からのアドバイスとして、LangGraphを利用することをお勧めします。これはシンプルな自律エージェントよりもはるかに信頼性が高く、拡張性に優れています。また、具体的な要件や目標を共有していただければ、さらなる指導を行うことも可能です。どのようなエージェントを考えているのか、具体的に教えてください。
```

私たちの入力はツールメッセージとして受信され、処理されました。この呼び出しの[LangSmithトレース](https://smith.langchain.com/public/9f0f87e3-56a7-4dde-9c76-b71675624e91/r)を確認して、上記の呼び出しで行われた正確な作業を確認してください。チャットボットが中断したところから続行できるように、最初のステップで状態がロードされることに注意してください。

**おめでとうございます！** `interrupt`を使用してチャットボットに人間のループ内実行を追加し、必要に応じて人間の監視と介入を可能にしました。これにより、AIシステムで作成できるUIの可能性が広がります。すでに**チェックポインタ**を追加しているため、基盤となる永続化レイヤーが稼働している限り、グラフは**無期限に**一時停止し、何事もなかったかのようにいつでも再開できます。

人間のループ内ワークフローは、さまざまな新しいワークフローとユーザーエクスペリエンスを可能にします。ツール呼び出しを実行する前に[レビューおよび編集](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/)する方法を含む、人間のループ内ワークフローの例については、How-toガイドの[このセクション](https://langchain-ai.github.io/langgraph/how-tos/#human-in-the-loop)をチェックしてください。

こちらに続きます。

https://qiita.com/taka_yayoi/items/58f2434defe5257dd8da

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

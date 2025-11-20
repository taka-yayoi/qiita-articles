---
title: LangChainからDatabricks Unity Catalogの関数を使う
tags:
  - Databricks
  - エージェント
  - UnityCatalog
  - LangChain
private: false
updated_at: '2025-01-09T13:37:50+09:00'
id: eddccffa8a0b6fe17dce
organization_url_name: databricks
slide: false
ignorePublish: false
---
LangChainのマニュアルにこのようなページが。

https://python.langchain.com/docs/integrations/tools/databricks/

ノートブックはこちら。

https://github.com/langchain-ai/langchain/blob/master/docs/docs/integrations/tools/databricks.ipynb

翻訳しながらウォークスルーします。

# Databricks Unity Catalog (UC)

このノートブックは、LangChainおよびLangGraphエージェントAPIを使用してUC関数をLangChainツールとして使用する方法を示しています。

SQLまたはPython関数をUCで作成する方法については、Databricksのドキュメント（[AWS](https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function.html)|[Azure](https://learn.microsoft.com/ja-jp/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-create-sql-function)|[GCP](https://docs.gcp.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function.html)）を参照してください。関数とパラメータのコメントは、LLMが関数を正しく呼び出すために重要なので、必ず確認してください。

この例のノートブックでは、任意のコードを実行するシンプルなPython関数を作成し、それをLangChainツールとして使用します：

```sql
CREATE FUNCTION main.tools.python_exec (
  code STRING COMMENT '実行するPythonコード。最終結果をstdoutに出力することを忘れないでください。'
)
RETURNS STRING
LANGUAGE PYTHON
COMMENT 'Pythonコードを実行し、そのstdoutを返します。'
AS $$
  import sys
  from io import StringIO
  stdout = StringIO()
  sys.stdout = stdout
  exec(code)
  return stdout.getvalue()
$$
```

以下のようにUnity Catalog配下に関数を作成します(若干コードとコメントが違いますが動作は変わりません)。

![Screenshot 2025-01-09 at 13.31.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d590a1cf-a5fe-3621-0597-cc1a6862e3ff.png)


```py
%pip install --upgrade --quiet databricks-sdk langchain-community databricks-langchain langgraph mlflow
```

LLMを定義します。

```py
from databricks_langchain import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-meta-llama-3-70b-instruct")
```

[こちら](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.databricks.tool.UCFunctionToolkit.html)にあるように、UC関数の実行にはSQLウェアハウスが必要となります。アクセスできるウェアハウスのIDを以下で指定します。

```py
from databricks.sdk import WorkspaceClient
from langchain_community.tools.databricks import UCFunctionToolkit

tools = (
    UCFunctionToolkit(
        # 作成後のUIでSQLウェアハウスIDを見つけることができます。
        warehouse_id="<SQLウェアハウスID>"
    )
    .include(
        # 修飾名を使用して関数をツールとして含めます。
        # "{catalog_name}.{schema_name}.*" を使用してスキーマ内のすべての関数を取得できます。
        "users.takaaki_yayoi.python_exec",
    )
    .get_tools()
)
```

（オプション）関数実行応答を取得するための再試行時間を延長するには、環境変数 UC_TOOL_CLIENT_EXECUTION_TIMEOUT を設定します。デフォルトの再試行時間は120秒です。

```py
import os

os.environ["UC_TOOL_CLIENT_EXECUTION_TIMEOUT"] = "200"
```

## LangGraphエージェントの例

LangGraphも勉強しないと。

```py
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    llm,
    tools,
    state_modifier="あなたは役に立つアシスタントです。情報を得るためにツールを使用してください。",
)
agent.invoke({"messages": [{"role": "user", "content": "36939 * 8922.4"}]})
```

```
{'messages': [HumanMessage(content='36939 * 8922.4', additional_kwargs={}, response_metadata={}, id='a5b1f530-02f6-487f-b92d-03edd72e6c15'),
  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_197309d2-d735-4022-97ad-33677ba3a009', 'type': 'function', 'function': {'name': 'users__takaaki_yayoi__python_exec', 'arguments': '{ "code": "print(36939 * 8922.4)" }'}}]}, response_metadata={'prompt_tokens': 1242, 'completion_tokens': 34, 'total_tokens': 1276}, id='run-4d595ccb-bef2-4983-9355-55b79041d264-0', tool_calls=[{'name': 'users__takaaki_yayoi__python_exec', 'args': {'code': 'print(36939 * 8922.4)'}, 'id': 'call_197309d2-d735-4022-97ad-33677ba3a009', 'type': 'tool_call'}]),
  ToolMessage(content='{"format": "SCALAR", "value": "329584533.59999996\\n", "truncated": false}', name='users__takaaki_yayoi__python_exec', id='5479fd94-7dd3-4de1-8958-61c44cc52c8a', tool_call_id='call_197309d2-d735-4022-97ad-33677ba3a009'),
  AIMessage(content='The result of the multiplication is 329,584,533.6.', additional_kwargs={}, response_metadata={'prompt_tokens': 1316, 'completion_tokens': 16, 'total_tokens': 1332}, id='run-01a97acd-d8f2-4bf1-a2bb-d982973aea1f-0')]}
```

関数が呼び出され、計算結果の`329584533.59999996`を得ることができました。

## LangChainエージェントの例

```py
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "あなたは役に立つアシスタントです。情報を得るためにツールを使用してください。",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
```

```py
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({"input": "36939 * 8922.4"})
```
```


> Entering new AgentExecutor chain...

Invoking: `users__takaaki_yayoi__python_exec` with `{'code': 'print(36939 * 8922.4)'}`


{"format": "SCALAR", "value": "329584533.59999996\n", "truncated": false}The result of the multiplication is 329,584,533.6.

> Finished chain.
```

こちらも同じ結果を得ることができました。


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

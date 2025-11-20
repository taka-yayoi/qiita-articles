---
title: LangMemのホットパスクイックスタートをDatabricksで動かしてみる
tags:
  - Databricks
  - LangChain
  - LangGraph
  - langmem
private: false
updated_at: '2025-02-21T17:13:51+09:00'
id: 5fcbfe89409cdb86dcf2
organization_url_name: databricks
slide: false
ignorePublish: false
---
いつの間にこのようなSDKが。

https://langchain-ai.github.io/langmem/

ローンチブログも訳しました。

https://qiita.com/taka_yayoi/items/ed6123e4166a8390f6f5

そして、すでに動かしている方が。 @isanakamishiro2 さん、早い、早いよ！

https://qiita.com/isanakamishiro2/items/bcffe4568fd3240e23eb

こちらのホットパスクイックスタートガイドを動かします。二番煎じです

https://langchain-ai.github.io/langmem/hot_path_quickstart/

メモリーは2つの方法で作成できます：

1. 👉 **ホットパス（このガイド）**: エージェントがツールを使用して意識的にメモを保存します。
1. バックグラウンド: メモリーは会話から自動的に「無意識に」抽出されます（[バックグラウンドクイックスタート](https://langchain-ai.github.io/langmem/background_quickstart/)を参照）。

![](https://langchain-ai.github.io/langmem/concepts/img/hot_path_vs_background.png)

このガイドでは、LangMemの`manage_memory`ツールを使用して自分の長期記憶を積極的に管理するLangGraphエージェントを作成します。

# 前提条件

最初にLangMemをインストールします:

```py
%pip install -U langmem
%pip install langgraph databricks-langchain
%pip install "mlflow-skinny[databricks]>=2.20.2"
%restart_python
```

お気に入りのLLMプロバイダーのAPIキーで環境を構成します:

```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get("demo-token-takaaki.yayoi", "openai_api_key")
```

```py
import mlflow

mlflow.langchain.autolog()
```

# エージェント
会話をまたいで記憶が持続するエージェントを作成する完全な例を以下に示します:

```py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langgraph.utils.config import get_store 
from langmem import (
    # エージェントがメモリを作成、更新、削除できるようにする
    create_manage_memory_tool,
)


def prompt(state):
    """LLMのメッセージを準備する。"""
    # 設定されたcontextvarからストアを取得する
    store = get_store() # `create_react_agent`に提供されたものと同じ
    memories = store.search(
        # エージェントに設定されたものと同じ名前空間内で検索する
        ("memories",),
        query=state["messages"][-1].content,
    )
    system_msg = f"""あなたは役に立つアシスタントです。日本語でやり取りをします。

## メモリ
<memories>
{memories}
</memories>
"""
    return [{"role": "system", "content": system_msg}, *state["messages"]]


store = InMemoryStore(
    index={ # 抽出されたメモリを保存する
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
) 
checkpointer = MemorySaver() # グラフの状態をチェックポイントする

agent = create_react_agent( 
    "openai:gpt-4o-mini",
    prompt=prompt,
    tools=[ # メモリツールを追加する
        # エージェントは"manage_memory"を呼び出して
        # IDでメモリを作成、更新、削除できる
        # 名前空間はメモリにスコープを追加する。ユーザーごとにメモリをスコープするには("memories", "{user_id}")を使用する
        create_manage_memory_tool(namespace=("memories",)),
    ],
    # メモリはこの提供されたBaseStoreインスタンスに保存される
    store=store,
    # そして各ノードが実行を完了するたびにグラフの"状態"がチェックポイントされ、
    # チャット履歴と耐久実行を追跡する
    checkpointer=checkpointer, 
)
```

# エージェントの使用
グラフと対話するには、`invoke` を使用します。エージェントがメモリを保存することを決定した場合、`manage_memory` ツールを呼び出します。

```py
config = {"configurable": {"thread_id": "thread-a"}}

# エージェントを使用する。エージェントはまだメモリを保存していないので、
# 私たちのことを知らない
response = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "私の好みの表示モードを知っていますか？"}
        ]
    },
    config=config,
)
print(response["messages"][-1].content)
# Output: "表示モードの好みに関する記憶が保存されていないようです..."
```
```
現在、あなたの好みの表示モードについての情報は記録されていません。特定の好みや設定があれば教えていただければ、記録して次回から反映させることができますので、お知らせください。
```
![Screenshot 2025-02-21 at 17.11.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1c3e6ac7-6892-4c71-ae50-516c1419ec89.png)

```py
agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "ダーク。覚えておいて。"}
        ]
    },
    # 同じthread_idを持つconfigを使用して会話(thread-a)を続ける
    config=config,
)
```
![Screenshot 2025-02-21 at 17.12.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ec24b732-2cb9-4e79-9a2d-916c42668588.png)

```py
# 新しいスレッド = 新しい会話！
new_config = {"configurable": {"thread_id": "thread-b"}}
# エージェントはmanage_memoriesツールを使用して明示的に保存したものだけを思い出すことができる
response = agent.invoke(
    {"messages": [{"role": "user", "content": "こんにちは。私のことを覚えていますか？私の好みは何ですか？"}]},
    config=new_config,
)
print(response["messages"][-1].content)
# Output: "私のメモリ検索によると、以前にダーク表示モードの好みを示していたことがわかります..."
```
```
こんにちは！はい、あなたの好みを覚えています。あなたはダークモードが好きだとおっしゃっていました。他に覚えてほしいことがあれば教えてください！
```

![Screenshot 2025-02-21 at 17.12.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/859de7d8-b43a-4276-adf1-43851cc5f57f.png)

この例は、会話間のメモリの持続性と、ユーザー間のスレッド分離を示しています。エージェントは、あるスレッドでユーザーのダークモードの設定を保存しますが、別のスレッドからはアクセスできません。

# 次のステップ
このクイックスタートでは、ツールを使用してエージェントが「ホットパス」でメモリを管理するように設定しました。他の機能については、次のガイドをチェックしてください:

- [リフレクションクイックスタート](https://langchain-ai.github.io/langmem/background_quickstart/) - `create_memory_store_manager` を使用して「バックグラウンド」でメモリを管理する方法を学びます。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

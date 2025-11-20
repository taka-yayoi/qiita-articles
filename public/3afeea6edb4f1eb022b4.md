---
title: Chainlitを試してみる
tags:
  - LangChain
  - chainlit
private: false
updated_at: '2024-05-09T17:24:53+09:00'
id: 3afeea6edb4f1eb022b4
organization_url_name: null
slide: false
ignorePublish: false
---
Twitterで流れてきたのを見かけました。普段はstreamlit使っているので、どんな感じなのかワクワクしながら試しました。そして、すごかった。

https://github.com/Chainlit/chainlit

# インストール

```
pip install chainlit
```

# Hello chainlit

```
chainlit hello
```

おおー、チャットのUIだ。

![Screenshot 2023-06-06 at 20.18.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4707e1b9-eade-8368-cde3-870c767e0c8d.png)
![Screenshot 2023-06-06 at 20.18.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e998194d-9452-084f-8509-5664405c4a93.png)

でも、これはまだガラだけなので、Get startedをやってみます。

# Pure Python

streamlitと同じように、pyファイルにロジック記述します。

```py:app.py
import chainlit as cl


@cl.on_message
def main(message: str):
    # Your custom logic goes here...

    # Send a response back to the user
    cl.Message(
        content=f"受信: {message}",
    ).send()
```

`-w`は、オートリロードのスイッチ。

```
chainlit run app.py -w
```

カスタマイズできましたが、これもまだモックの状態。

![Screenshot 2023-06-06 at 20.21.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/90db4a7d-2153-8ac8-d0cf-003bc81f7914.png)

# LangChain連携

今回の山場。

https://docs.chainlit.io/langchain

LangChainが入っていない場合には、`pip install langchain`でインストールします。あと、OpenAI APIのAPIキーも取得しておきます。

```py:langchain.py
import os
from langchain import PromptTemplate, OpenAI, LLMChain
import chainlit as cl

os.environ["OPENAI_API_KEY"] = "<OpenAI APIキー>"

template = """質問: {question}

回答: ステップバイステップで考えてみましょう。"""

@cl.langchain_factory
def factory():
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)

    return llm_chain
```

LangChainのプロンプトテンプレートを使うということですね。

```
chainlit run langchain.py -w
```

メッセージを送信すると、LLMChain経由でOpenAI APIを呼び出します。

![Screenshot 2023-06-06 at 20.25.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1447f90b-ab83-b563-dc13-166346c7b86a.png)

動きました！
![Screenshot 2023-06-06 at 20.25.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c2b7816e-0a6a-8182-56a4-c17b60d0b63a.png)

なお、ターミナルではプロンプトを確認できます。
![Screenshot 2023-06-06 at 20.26.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a98525c7-7dd4-13ed-3847-8d3640b8a7ab.png)

いやー、フロントエンドはもうこれでいい感じです。
![Screenshot 2023-06-06 at 20.27.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8d36a55e-841a-f782-777d-da5cc91bf5dd.png)

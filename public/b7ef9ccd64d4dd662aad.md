---
title: DatabricksでMLflowとLLMを用いたRAGシステムの評価(日本語編)
tags:
  - Databricks
  - rag
  - MLflow
  - LLM
private: false
updated_at: '2023-12-14T18:23:04+09:00'
id: b7ef9ccd64d4dd662aad
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの日本語編です。

https://qiita.com/taka_yayoi/items/110818e5691be47fd96a

前半は同じです。

```py
%pip install chromadb==0.4.15
dbutils.library.restartPython()
```

```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get("demo-token-takaaki.yayoi", "openai")
```

```py
import pandas as pd

import mlflow
```

```py
from langchain.chains import RetrievalQA
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
```

Databricksの日本語マニュアルのページを指定します。

```py
loader = WebBaseLoader("https://docs.databricks.com/ja/introduction/index.html")

documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_documents(texts, embeddings)

qa = RetrievalQA.from_chain_type(
    llm=OpenAI(temperature=0),
    chain_type="stuff",
    retriever=docsearch.as_retriever(),
    return_source_documents=True,
)
```

```py
def model(input_df):
    answer = []
    for index, row in input_df.iterrows():
        answer.append(qa(row["questions"]))

    return answer
```

評価用データセットを作成します。ここの文字列を長くするとLLMの最長トークン数に引っかかってエラーになってしまいました。どうしたものか。

```py
eval_df = pd.DataFrame(
    {
        "questions": [
            "Databricksとは？",
            "価格は？",
        ],
    }
)
```

例も日本語で指定します。

```py
from mlflow.metrics.genai import faithfulness, EvaluationExample

# この問題の文脈における faithfulness の良い例と悪い例を作成します
faithfulness_examples = [
    EvaluationExample(
        input="Databricksとは？",
        output="Databricksは自動車です。",
        score=1,
        justification="アウトプットはコンテキストに示されている情報を用いておらず間違った回答をしています。",
        grading_context={
            "context": "Databricksは、エンタープライズグレードのデータ分析とAIソリューションを大規模に構築、デプロイ、共有、保守するための、統合されたオープンなアナリティクスプラットフォームです。 Databricksデータインテリジェンスプラットフォームは、クラウドアカウントのクラウドストレージおよびセキュリティと統合し、ユーザーに代わってクラウドインフラストラクチャを管理およびデプロイします。"
        },
    ),
    EvaluationExample(
        input="Databricksとは？",
        output="Databricksはデータ分析とAIソリューションの開発・運用を実現するデータインテリジェンスプラットフォームです。",
        score=5,
        justification="アウトプットはコンテキストに示されている情報を用いてDatabricksを説明しています。",
        grading_context={
            "context": "Databricksは、エンタープライズグレードのデータ分析とAIソリューションを大規模に構築、デプロイ、共有、保守するための、統合されたオープンなアナリティクスプラットフォームです。 Databricksデータインテリジェンスプラットフォームは、クラウドアカウントのクラウドストレージおよびセキュリティと統合し、ユーザーに代わってクラウドインフラストラクチャを管理およびデプロイします。"
        },
    ),
]

faithfulness_metric = faithfulness(model="openai:/gpt-4", examples=faithfulness_examples)
print(faithfulness_metric)
```

```
EvaluationMetric(name=faithfulness, greater_is_better=True, long_name=faithfulness, version=v1, metric_details=
Task:
You are an impartial judge. You will be given an input that was sent to a machine
learning model, and you will be given an output that the model produced. You
may also be given additional information that was used by the model to generate the output.

Your task is to determine a numerical score called faithfulness based on the input and output.
A definition of faithfulness and a grading rubric are provided below.
You must use the grading rubric to determine your score. You must also justify your score.

Examples could be included below for reference. Make sure to use them as references and to
understand them before completing the task.

Input:
{input}

Output:
{output}

{grading_context_columns}

Metric definition:
Faithfulness is only evaluated with the provided output and provided context, please ignore the provided input entirely when scoring faithfulness. Faithfulness assesses how much of the provided output is factually consistent with the provided context. A higher score indicates that a higher proportion of claims present in the output can be derived from the provided context. Faithfulness does not consider how much extra information from the context is not present in the output.

Grading rubric:
Faithfulness: Below are the details for different scores:
- Score 1: None of the claims in the output can be inferred from the provided context.
- Score 2: Some of the claims in the output can be inferred from the provided context, but the majority of the output is missing from, inconsistent with, or contradictory to the provided context.
- Score 3: Half or more of the claims in the output can be inferred from the provided context.
- Score 4: Most of the claims in the output can be inferred from the provided context, with very little information that is not directly supported by the provided context.
- Score 5: All of the claims in the output are directly supported by the provided context, demonstrating high faithfulness to the provided context.

Examples:

Input:
Databricksとは？

Output:
Databricksはデータ分析とAIソリューションの開発・運用を実現するデータインテリジェンスプラットフォームです。

Additional information used by the model:
key: context
value:
Databricksは、エンタープライズグレードのデータ分析とAIソリューションを大規模に構築、デプロイ、共有、保守するための、統合されたオープンなアナリティクスプラットフォームです。 Databricksデータインテリジェンスプラットフォームは、クラウドアカウントのクラウドストレージおよびセキュリティと統合し、ユーザーに代わってクラウドインフラストラクチャを管理およびデプロイします。

score: 5
justification: アウトプットはコンテキストに示されている情報を用いてDatabricksを説明しています。
        

You must return the following fields in your response one below the other:
score: Your numerical score for the model's faithfulness based on the rubric
justification: Your step-by-step reasoning about the model's faithfulness score
    )
```

```py
from mlflow.metrics.genai import relevance, EvaluationExample


relevance_metric = relevance(model="openai:/gpt-4")
print(relevance_metric)
```

評価します。

```py
results = mlflow.evaluate(
    model,
    eval_df,
    model_type="question-answering",
    evaluators="default",
    predictions="result",
    extra_metrics=[faithfulness_metric, relevance_metric, mlflow.metrics.latency()],
    evaluator_config={
        "col_mapping": {
            "inputs": "questions",
            "context": "source_documents",
        }
    },
)
print(results.metrics)
```

```py
display(results.tables["eval_results_table"])
```

回答は一部英語になっていますが、適切に評価されているようです。
![Screenshot 2023-12-14 at 18.17.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/17ccedd9-0b9f-79e4-170f-5b824cc5446b.png)

特に2つ目の質問に関しては、元の情報に価格が含まれていないことから適当なことを返すことなしに、`I don't know.`を返しています。
![Screenshot 2023-12-14 at 18.16.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/46b8e05b-0ca0-680d-3c86-0d4a967293f4.png)

これに対しても、LLMが以下の通り公正な回答を行なっていると評価して5点をつけています。
> The output "I don't know" does not make any factual claims, so it does not contradict or misrepresent the context provided. Therefore, it is fully faithful to the context, even though it does not utilize the information in the context.

> アウトプット「わかりません」では、いかなる架空の主張を行なっていませんので、矛盾や指定されたコンテキストの誤読はありません。このため、コンテキストの情報は活用していないとしても、完全に公正なものです。

しかし、これってLLMシステムを定量的に評価できるようになったってことなんですよね。すごい。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

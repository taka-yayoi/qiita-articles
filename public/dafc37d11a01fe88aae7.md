---
title: DatabricksでEnglish API for Sparkを試してみる
tags:
  - Spark
  - Databricks
  - LLM
private: false
updated_at: '2023-06-30T17:45:40+09:00'
id: dafc37d11a01fe88aae7
organization_url_name: databricks
slide: false
ignorePublish: false
---
初めこれを読んだ時には「エイプリルフール？」と思いました。

https://qiita.com/taka_yayoi/items/e5f58ac7f80064627a30

こちらで公開されています。

https://github.com/databrickslabs/pyspark-ai/

# 事前準備

Databricksで動かす際にはいくつかの設定が必要です。最初の2つはデータ取得の際にweb検索するために必要です。

- Google Cloud PlatformでAPIキーを取得
- Google Cloud PlatformでGoogle Custom Search APIを有効化してCSE IDを取得
- OpenAI APIキーの取得
- GPT-4 API Waitlistへの登録(まだ通ってません)

# ライブラリのインストールと設定

```
%pip install pyspark-ai
```
```py
dbutils.library.restartPython()
```

以下のように環境変数にAPIキーを設定します。

```py
import os

os.environ["OPENAI_API_KEY"] = dbutils.secrets.get("demo-token-takaaki.yayoi", "openai_api_key")
os.environ["GOOGLE_API_KEY"] = "<Google Cloud PlatformのAPIキー>"
os.environ["GOOGLE_CSE_ID"] = "<CSE ID>"
```

私はGPT-4が使えないので、GPT-3.5に切り替えます。

```py
from langchain.chat_models import ChatOpenAI
from pyspark_ai import SparkAI

llm = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0)

spark_ai = SparkAI(llm=llm)
spark_ai.activate()  # active partial functions for Spark DataFrame
```

# データの取り込み

```py
auto_df = spark_ai.create_df("2022 USA national auto sales by brand")
```
```py
auto_df.show(n=5)
```
```
+----------+----------+-------------+
|brand_name|sales_2022|sales_vs_2021|
+----------+----------+-------------+
|    Toyota|   1849751|           -9|
|      Ford|   1767439|           -2|
| Chevrolet|   1502389|            6|
|     Honda|    881201|          -33|
|   Hyundai|    724265|           -2|
+----------+----------+-------------+
only showing top 5 rows
```

ここまで英語の手順でEnglish APIを呼び出しただけ。なんだこれはー。

# プロット

これは単にプロットメソッドを呼び出してます。

```py
auto_df.ai.plot()
```
![Screenshot 2023-06-30 at 17.39.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0d5c333e-fe68-3d76-3603-f312c07aff93.png)

`plot()`に自然言語も指定できるのですが、GPT-3.5のせいかエラーになってしまいます。

# データフレームに対する操作

最も成長しているブランド。

```py
auto_top_growth_df=auto_df.ai.transform("brand with the highest growth")
auto_top_growth_df.show()
```

返ってきてる…。

```
+----------+
|brand_name|
+----------+
|  Cadillac|
+----------+
```

# データフレームの説明

普通、`explain()`というと実行計画返ってきそうですが、本当に説明を求めているわけですね。

```py
auto_top_growth_df.ai.explain()
```
```
Out[15]: 'In summary, this dataframe is retrieving the brand name with the highest sales increase compared to 2021. It presents the result sorted by the sales increase in descending order and returns only the top 1 brand.'
```

うむー、確かに可能性を感じる。自然言語でコーディングするなんて、自分の年代では[ぴゅう太](https://ja.wikipedia.org/wiki/%E3%81%B4%E3%82%85%E3%81%86%E5%A4%AA)を思い出してしまいました。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

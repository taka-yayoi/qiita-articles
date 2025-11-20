---
title: Pythonユーザー定義テーブル関数(UDTF)のご紹介
tags:
  - Spark
  - udf
  - Databricks
private: false
updated_at: '2024-04-16T16:35:20+09:00'
id: 93ae2a7d80e66afeeacc
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Introducing Python User\-Defined Table Functions \(UDTFs\) \| Databricks Blog](https://www.databricks.com/blog/introducing-python-user-defined-table-functions)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# Pythonユーザー定義テーブル関数(UDTF)とは何か、なぜ大事なのか、どのように使うのか

Apache Spark™ 3.5とDatabricksランタイム14.0以降ではテーブルに対する素晴らしい機能が導入されました: ユーザー定義テーブル関数(user-defined table function:UDTF)です。この記事では、UDTFが何であるのか、なぜこれがパワフルなのか、どのように使うのかについて深掘りします。

# Pythonユーザー定義テーブル関数(UDTF)とは何か

Pythonユーザー定義テーブル関数とは、出力として単一のスカラー結果値ではなく、テーブルを返却する新たなタイプの関数です。登録されると、SQLクエリーの`FROM`句に表示されるようになります。

それぞれのPython UDTFは0個以上の引数を受け取り、それぞれの引数は整数値や文字列のような定数のスカラー値となります。関数の本体では、どのようなデータを返却するのかに対する意思決定を行うために、これらの引数の値を調査することができます。

# なぜPython UDTFを使うべきなのか

簡単にいうと、複数の行や列を生成する関数が必要な場合、豊富なPythonのエコシステムを活用したい場合には、Python UDTFを使うべきです。

## Python UDTF vs Python UDF

SparkのPython UDFは入力として0個以上のスカラー値を受け取り、出力として単一の値を返却するように設計されていますが、UDTFは更なる柔軟性を提供します。UDFの機能を拡張して複数の行と列を返却することができます。

## Python UDTF vs SQL UDTF

SQL UDTFは効率的で多才ですが、Pythonはより豊富なライブラリやツールのセットを提供します。(統計関数や機械学習推論のような)高度なテクニックを必要とする変換処理や計算処理では、Pythonが抜きん出ています。

# Python UDTFの作成方法

基本的なPython UDTFを見てみましょう:

```py
from pyspark.sql.functions import udtf

@udtf(returnType="num: int, squared: int")
class SquareNumbers:
    def eval(self, start: int, end: int):
        for num in range(start, end + 1):
            yield (num, num * num)
```

上のコードでは、入力として2つの整数値を受け取り、出力として2つの列を生成するシンプルなUDTFを作成しました: 出力はオリジナルの数値とその二乗です。

UDTFを実装する最初のステップはクラスの定義であり、この場合は以下のようになります。

```py
class SquareNumbers:
```

次に、UDTFの`eval`メソッドを実装する必要があります。これは、計算処理を行い行を返却するメソッドであり、関数の入力引数を定義します。

```py
def eval(self, start: int, end: int):
    for num in range(start, end + 1):
        yield (num, num * num)
```

`yield`文を使っていることに注意してください。Pyton UDTFでは、結果が適切に処理されるように、戻り値の型がタプルあるいは`Row`オブジェクトである必要があります。

最後に、このクラスをUDTFとしてマークするために、`@udtf`デコレーターを使用し、UDTFの戻り値の型を定義します。戻り値の型は、Sparkにおけるブロックフォーマットされた`StructType`か、それを表現するDDL文字列である必要があることに注意してください。

```py
@udtf(returnType="num: int, squared: int")
```

# Python UDTFの使い方

## Python

クラス名を用いてUDTFを呼び出すことができます。

```py
from pyspark.sql.functions import lit

SquareNumbers(lit(1), lit(3)).show()
```
```
+---+-------+
|num|squared|
+---+-------+
|  1|      1|
|  2|      4|
|  3|      9|
+---+-------+
```

## SQL

最初に、Python UDTFを登録します:

```py
spark.udtf.register("square_numbers", SquareNumbers)
```

すると、クエリーのFROM句でテーブル値関数としてSQLで使用することができます:

```py
spark.sql("SELECT * FROM square_numbers(1, 3)").show()
```
```
+---+-------+
|num|squared|
+---+-------+
|  1|      1|
|  2|      4|
|  3|      9|
+---+-------+
```

# Arrow最適化Python UDTF

Apache ArrowはJavaプロセスとPythonプロセス間の効率的なデータ転送を実現する、インメモリの列指向データフォーマットです。UDTFが大量の行を出力する際に、劇的にパフォーマンスをブーストします。Arrow最適化は`useArrow=True`を用いることで有効化することができます。

```py
from pyspark.sql.functions import lit, udtf

@udtf(returnType="num: int, squared: int", useArrow=True)
class SquareNumbers:
    ...
```

# LangChainによる現実世界のユースケース

上のサンプルは基本的だと感じるかもしれません。Python UDTFとLangChainを組み合わせた、より面白い例を深掘りしていきましょう。

```py
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from pyspark.sql.functions import lit, udtf

@udtf(returnType="keyword: string")
class KeywordsGenerator:
    """
    Generate a list of comma separated keywords about a topic using an LLM.
    Output only the keywords.
    """
    def __init__(self):
        llm = OpenAI(model_name="gpt-4", openai_api_key=<your-key>)
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="generate a couple of comma separated keywords about {topic}. Output only the keywords."
        )
        self.chain = LLMChain(llm=llm, prompt=prompt)

    def eval(self, topic: str):
        response = self.chain.run(topic)
        keywords = [keyword.strip() for keyword in response.split(",")]
        for keyword in keywords:
            yield (keyword, )
```

これで、UDTFを呼び出すことができます:

```py
KeywordsGenerator(lit("apache spark")).show(truncate=False)
```
```
+-------------------+
|keyword            |
+-------------------+
|Big Data           |
|Data Processing    |
|In-memory Computing|
|Real-Time Analysis |
|Machine Learning   |
|Graph Processing   |
|Scalability        |
|Fault Tolerance    |
|RDD                |
|Datasets           |
|DataFrames         |
|Spark Streaming    |
|Spark SQL          |
|MLlib              |
+-------------------+
```

# すぐにPython UDTFを使い始める

複雑なデータ変換処理を実行したり、データセットを補強したり、シンプルにデータを分析する新たな方法を探しているのであれば、Python UDTFはあなたの道具箱における価値のある追加のツールとなります。詳細については、[こちらのノートブック](https://www.databricks.com/wp-content/uploads/notebooks/python-user-defined-table-functions-udtfs.html)を試し、[ドキュメント](https://spark.apache.org/docs/latest/api/python/user_guide/sql/python_udtf.html)をご覧ください。

# 今後の取り組み

この昨日は、Python UDTFプラットフォームの始まりに過ぎません。Apache Sparkにおいて数多くの機能が開発中であり、今後のリリースで利用できるようになります。例えば、以下のようなものがサポートされることになります:

- それぞれの呼び出しで指定される個別の引数に対して、出力スキーマを動的に計算するUDTFの呼び出しにおける(指定される入力引数の型と任意のリテラルスカラー引数の値を含む)多態的な解析。
- `TABLE`キーワードを用いたSQLの`FROM`句で、UDTFの呼び出しに入力値の全体的なリレーションの指定。これは、直接的なカタログテーブルリファリンスや任意のテーブルサブクエリーで動作します。入力テーブルのどの行サブセットが、`eval`メソッドでUDTFクラスの同じインスタンスによって消費されるのかを定義するために、それぞれのクエリーにおける入力テーブルのカスタムパーティショニングを指定することが可能となります。
- クエリーのスケジュール時に、UDTFに対して一度のみの任意の初期化処理を実行し、以降の利用において全ての将来的なクラスインスタンスの状態を伝搬。これは、初期の静的な`analyze`メソッドによって返却されるUDTFの出力テーブルのスキーマは、同じクエリーに対する以降のすべての`__init__`で利用できることを意味します。
- より多くの面白い機能！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

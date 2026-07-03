---
title: PySparkにおけるメモリーのプロファイリング
tags:
  - Spark
  - Pyspark
  - Databricks
private: false
updated_at: '2022-12-02T09:56:50+09:00'
id: a596d5ccca63cf3fecd9
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Memory Profiling in PySpark \- The Databricks Blog](https://www.databricks.com/blog/2022/11/30/memory-profiling-pyspark.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

PySparkプログラムのパフォーマンスには多数の要素が存在しています。PySparkでは、あなたのプログラム密なループを明らかにする様々なプロファイリングツールをサポートしており、パフォーマンス改善に関する意思決定を行うことが可能となります。詳細は[こちら](https://qiita.com/taka_yayoi/items/2d97ea548ccbb11a4103)をご覧ください。しかし、プログラムのパフォーマンスのキーとなる要素の一つであるメモリーは長らくPySparkのプロファイリングではサポートされていませんでした。通常のPythonプロセスとして[メモリープロファイラー](https://pypi.org/project/memory-profiler/)を用いて、Sparkドライバー上のPySparkプログラムをプロファイリングすることは可能でしたが、Sparkエグゼキューターのメモリーをプロファイルする容易な方法は存在していませんでした。

最も人気のあるPython APIの一つであるPySpark UDFは、SparkエグゼキューターによってスポーンされたPythonワーカーサブプロセスによって実行されます。これによってユーザーはApache Spark™エンジンの上でカスタムコードを実行できるのでパワフルなものとなっています。しかし、メモリー消費を理解することなしにUDFを最適化することは困難です。PySpark UDFの最適化を支援し、アウトオブメモリーエラーの可能性を削減するために、PySparkメモリープロファイラーは、合計メモリー使用量の情報を提供します。UDFのコードのどの行がもっともメモリーを使用しているのかを特定します。

エグゼキューターにおけるメモリープロファイリングの実装は困難なものでした。エグゼキューターはクラスター上に分散されているので、結果のメモリープロファイルをそれぞれのエグゼキューターから収集し、合計のメモリー消費を表示するために適切に集計する必要があります。また、デバッグと修正のために、メモリー消費とそれぞれのソースコード行を提供しなくてはなりません。[Databricks Runtime 12\.0](https://docs.databricks.com/release-notes/runtime/12.0.html)において、PySparkはこれらすべての技術的課題を克服し、エグゼキューターでメモリープロファイリングが可能となりました。この記事では、ユーザー定義関数(UDF)の概要を説明し、UDFにどのようにメモリープロファイラーを使うのかをデモします。

# ユーザー定義関数(UDF)の概要

PySparkでサポートされているUDFには大きく2つのカテゴリーが存在します: Python UDFとPandas UDFです。

- Python UDFは、Pickleによってシリアライズ/デシリアライズされるPythonオブジェクトを受け取り/返却するユーザー定義スカラー関数であり、一度に一行を処理します。
- Pandas UDF(ベクトライズドUDF)は、Apache Arrowによってシリアライズ/デシリアライズされるシリーズ、データフレームを受け取り/返却するUDFであり、ブロックごとに処理します。Pandas UDFは用途や入出力のタイプに応じてカテゴリ分けされるバリエーションが存在します: `Series to Series`, `Series to Scalar`, `Iterator to Iterator`です。

Pandas UDF実装をベースとしたPandas Functions APIが存在します: Map (`mapInPandas`など)、(Co)Grouped Map (applyInPandasなど)、そして、Arrow Function APIの`mapInArrow`もあります。関数が入出力のイテレーターを受け取らない限り、上述のすべてのUDFタイプにメモリープロファイラーは適用されます。

# メモリープロファイリングの有効化

クラスターでメモリープロファイリングを有効化するには、以下の様に[Memory Profiler](https://pypi.org/project/memory-profiler/)ライブラリをインストールし、Spark設定`spark.python.profile.memory`を`true`に設定する必要があります。

- クラスターにMemory Profilerライブラリをインストールします。
![](https://cms.databricks.com/sites/default/files/inline-images/db-407-blog-img-1.png)
- Spark設定で`spark.python.profile.memory`を有効化します。
![](https://cms.databricks.com/sites/default/files/inline-images/db-407-blog-img-2.png)

すると、UDFのメモリーをプロファイルできる様になります。[GroupedData\.applyInPandas](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.GroupedData.applyInPandas.html)を用いて、メモリープロファイラーを説明します。

最初に、以下のように4,000,000行のPySparkデータフレームを生成します。その後で、グループごとに1,000,000行の4グループが生成される様にid列でグルーピングします。

```py:Python
sdf = spark.range(0, 4 * 1000000).withColumn(
  'id', (col('id') % 4).cast('integer')
).withColumn('v', rand())
```

以下の様に、関数`arith_op`を定義して`sdf`に適用します。

```py:Python
def arith_op(pdf: pd.DataFrame) -> pd.DataFrame:
    new_v = []
    for x in pdf.v:
        new_v.append(x * 10 + 1)
    pdf.v = pd.Series(new_v)
    return pdf

res = sdf.groupby("id").applyInPandas(arith_op, schema=sdf.schema)
res.collect()
```

上のコードを実行し、`sc.show_profiles()`を実行すると以下のプロファイル結果が表示されます。`sc.dump_profiles(path)`を用いて、プロファイル結果をディスクにダンプすることもできます。
![](https://cms.databricks.com/sites/default/files/inline-images/db-407-blog-img-3.png)

上のプロファイル結果のUDFのIDである245は、`res.explain()`を呼び出すことで表示されるSparkの実行計画の`rest`と一致します。

```
== Physical Plan ==
...
   FlatMapGroupsInPandas [...], arith_op(...)#245, [...]
```

`sc.show_profiles()`のプロファイル結果の本文には、以下のカラムが含まれます。

- `Line #` プロファイリングされたコードの行番号
- `Mem usage` 行を実行した後のPythonインタプリタのメモリー使用量
- `Increment` 前回の行と現在の行のメモリーの差
- `Occurrences` 行が実行された回数
- `Line Contents` プロファイリングされたコード

プロファイル結果から`Line 3 ("for x in pdf.v")`が`~125 MiB`と最もメモリーを消費していることがわかります。そして、この関数のメモリー消費の総量は`~185 MiB`となっています。

以下の様に`pdf.v`のイテレーションを削除することで、関数のメモリー効率を改善することができます。

```py:Python
def optimized_arith_op(pdf: pd.DataFrame) -> pd.DataFrame:
  pdf.v = pdf.v * 10 + 1
  return pdf

res = sdf.groupby("id").applyInPandas(optimized_arith_op, schema=sdf.schema)
res.collect()
```

アップデートされたプロファイル結果は以下の様になります。
![](https://cms.databricks.com/sites/default/files/inline-images/db-407-blog-img-4.png)

`optimized_arith_op`のメモリー消費の合計は`~61 MiB`に削減され、半分程度になりました。

上のサンプルでは、UDFのメモリー消費を深く理解し、メモリーのボトルネックを特定し、関数のメモリー効率を改善するために、どのようにメモリープロファイラーが役立つのかをデモしました。

# まとめ

PySparkのメモリープロファイラーは[Memory Profiler](https://pypi.org/project/memory-profiler/)をベースとして実装されています。また、Pythonワーカーからプロファイル結果を収集する際に、[Spark Accumulators](https://spark.apache.org/docs/latest/rdd-programming-guide.html#accumulators)が重要な役割を担っています。メモリープロファイラーはUDFの合計メモリー使用量を計算し、コードのどの行がもっともメモリーを消費するのかを特定します。[Databricks Runtime 12\.0](https://docs.databricks.com/release-notes/runtime/12.0.html)以降で簡単に利用することができます。

さらに、我々はPySparkのメモリープロファイラーをApache Spark™コミュニティにオープンソース化しました。Spark 3.4以降でこのメモリープロファイラーを使用することができます。詳細については、[SPARK\-40281](https://issues.apache.org/jira/browse/SPARK-40281)をご覧ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

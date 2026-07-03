---
title: Apache Spark 2.4における複雑なデータ型向けの新たなビルトイン関数と高階関数のご紹介
tags:
  - Spark
  - Databricks
private: false
updated_at: '2022-10-27T11:44:21+09:00'
id: fb11c6b77a7dbfa08ee3
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Introducing New Built\-in and Higher\-Order Functions for Complex Data Types in Apache Spark 2\.4 \- The Databricks Blog](https://www.databricks.com/blog/2018/11/16/introducing-new-built-in-functions-and-higher-order-functions-for-complex-data-types-in-apache-spark.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**注意**
2018年の記事です。
:::

[Apache Spark 2\.4](https://www.databricks.com/blog/2018/11/08/introducing-apache-spark-2-4.html)では、高階関数を含め、複雑な型(配列型など)を操作するための29の新たなビルトイン関数を導入します。

Spark 2.4以前では、複雑な型を直接操作するためには、2つの典型的なソリューションがありました。

1. ネストされた構造を個々の行にexplodeし、何かしらの関数を適用し、再度構造を組み立てる
1. ユーザー定義関数(UDF)

これらとは異なり、新たなビルトイン関数は複雑な型を直接操作し、高階関数は匿名のラムダ関数を用いてUDFと同じ様に複雑な値を操作することができますが、優れたパフォーマンスを提供します。

この記事では、いくつかの例を通じてこれらの新たなビルトイン関数をお見せし、複雑なデータ型をどの様に操作するのかを説明します。

# 典型的なソリューション

まず初めに、例を通じて典型的なソリューションを見ていきましょう。

## オプション1 - ExplodeとCollect

以下の様に、配列を個々の行に分解するために`explode`を使い、`val + 1`を評価し、配列を再構成するために`collect_list`を使います。

```sql:SQL
SELECT id,
       collect_list(val + 1) AS vals
FROM   (SELECT id,
               explode(vals) AS val
        FROM input_tbl) x
GROUP BY id
```

これは3つの理由からエラーが混入しやすく非効率的です。第一に、ユニークなキーを用いてグルーピングすることで、オリジナルの配列から配列が再構成されることを確実にするために注意しなくてはなりません。第二に、シャッフルオペレーションである`group-by`が必要となります。シャッフルオペレーションは、オリジナルの配列と再構成された配列の要素の順序を維持することを保証しません。最後に、これはコストがかかるものです。

## オプション2 - ユーザー定義関数

次に、`Seq[Int]`を受け取り、それぞれの要素に1を加算するScalaのUDFを使用します。

```scala:Scala
def addOne(values: Seq[Int]): Seq[Int] = {
  values.map(value => value + 1)
}
val plusOneInt = spark.udf.register("plusOneInt", addOne(_: Seq[Int]): Seq[Int])
```

あるいは、Python UDFを使います。その後に以下を実行します。

```sql:SQL
SELECT id, plusOneInt(vals) as vals FROM input_tbl
```

これはシンプルで高速で、正確性に関する落とし穴に苦しむことはありませんが、ScalaやPythonへのデータのシリアライズが高コストとなる場合があるため、依然として非効率的です。

以前の[ブログ記事](https://www.databricks.com/blog/2017/05/24/working-with-nested-data-using-higher-order-functions-in-sql-on-databricks.html)で公開したノートブックのサンプルを確認することができます。

# 新たなビルトイン関数

それでは、複雑な型を直接操作するための新たなビルトイン関数を見ていきましょう。こちらの[ノートブック](https://spark.apache.org/docs/2.4.3/api/java/org/apache/spark/sql/functions.html)でそれぞれの関数をサンプルを列挙しています。それぞれの関数のシグネチャと引数では、配列の要素の型を表現するためのそれぞれの型である`T`や`U`、mapとvalueの型として`K`、`V`のアノテーションを行なっています。

# 高階関数

配列やmap型をさらに操作するために、匿名のラムダ関数と、引数としてラムダ関数を受け取る高階関数に対して、既知のSQL構文を使いました。

ラムダ関数の構文は以下の様になります。

```py
 argument -> function body
  (argument1, argument2, ...) -> function body
```

シンボル`->`の左側では引数のリストを定義し、右側では引数を使う関数の本体と、新たな値を計算するための他の変数を定義します。

## 匿名のラムダ関数による変換

匿名のラムダ関数を使用する`transform`関数のサンプルを見ていきましょう。

3つのカラム、integerのkey、integerの配列のvalues、integerの配列の配列であるnested_valuesを持つテーブルがあるものとします。

| key | values | nested_values |
|:--|:--|:--|
| 1  | [1, 2, 3]  |  [[1, 2, 3], [], [4, 5]] |

以下のSQLを実行します。

```sql:SQL
SELECT TRANSFORM(values, element -> element + 1) FROM data;
```

`transform`関数は配列に対してイテレーションし、ラムダ関数を適用することでそれぞれの要素に1を加算することで新たな配列を作成します。

また、ラムダ関数の中で引数に加えて他の変数を使用します。例えば、外部のコンテキストから得られるテーブルのカラムであるkeyを使います。

```sql:SQL
SELECT TRANSFORM(values, element -> element + key) FROM data;
```

深くネストされたカラム、この場合ではnested_valuesを操作したい場合には、ネストされたラムダ関数を使用することができます。

```sql:SQL
 SELECT TRANSFORM(
    nested_values,
    arr -> TRANSFORM(arr,
      element -> element + key + SIZE(arr)))
  FROM data;
```

外部のコンテキストから得られるテーブルのカラムや外部のラムダ関数の引数であるkeyやarrを内部のラムダ関数で使用することもできます。

これらに対応する典型的なソリューションとして同じ例をサンプルノートブックで確認することができ、ビルトイン関数向けのノートブックに他の高階関数のサンプルが含まれていることに注意してください。

# まとめ

Spark 2.4では、複雑な型を操作するための`array_union`、`array_max/min`のような24個の新たなビルトイン関数、`transform`、`filter`のような5個の高階関数を導入しました。これらの完全なリストとサンプルはこちらの[ノートブック](https://docs.databricks.com/_static/notebooks/apache-spark-functions.html)に含まれています。何かしらの複雑な型を取り扱う際にはこれらを活用することを検討いただき、問題があればご連絡ください。

Alex Vayda, Bruce Robbins, Dylan Guedes, Florent Pepin, H Lu, Huaxin Gao, Kazuaki Ishizaki, Marco Gaido, Marek Novotny, Neha Patil, Sandeep SinghなどApache Sparkコミュニティの多くの人々の貢献に感謝の意を表します。

# 追加情報

高階関数、ビルトイン関数の詳細については以下のリソースを参照ください。

1. [添付ノートブック](https://docs.databricks.com/_static/notebooks/apache-spark-functions.html)を試す
1. 以前の[高階関数に関する記事](https://www.databricks.com/blog/2017/05/24/working-with-nested-data-using-higher-order-functions-in-sql-on-databricks.html)を読む
1. [Spark \+ AI Summit Europe Talk on Higher\-Order Functions](https://www.databricks.com/session/an-introduction-to-higher-order-functions-in-spark-sql)を視聴する

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

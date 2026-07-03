---
title: Unity Catalogにおけるデータのクエリー
tags:
  - Databricks
  - UnityCatalog
private: false
updated_at: '2023-01-30T11:55:17+09:00'
id: dcd0c6fe1223b9b7ce0d
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Query data \| Databricks on AWS](https://docs.databricks.com/data-governance/unity-catalog/queries.html) [2023/1/13時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本書ではUnity Catalogにおけるデータのクエリー方法を説明します。

# 要件

- ノートブック、Databricks SQLエディタを実行するために使用する[計算リソース](https://qiita.com/taka_yayoi/items/9f13a2b97ebd11cfd04f)やクエリーを作成するためのデータエクスプローラワークフローは、Unity Catalogのセキュリティ要件に準拠する必要があります。
- テーブルやビューのデータをクエリーするには、親のカタログやスキーマに対する`USAGE`権限、テーブルやビューに対する`SELECT`権限が必要となります。

    :::note
    **注意**
    シングルユーザーアクセスモードを使用するクラスターでビューから読み込みを行うには、ユーザーは参照されるすべてのテーブルやビューに対する`SELECT`権限が必要となります。
:::

# 3レベルの名前空間記述

Unity Catalogにおいて、テーブルやビューは親のカタログやスキーマに格納されます。2つの異なる記述スタイルでテーブルやビューを参照することができます。カタログやスキーマを指定するために`USE CATALOG`文と`USE`文を使用することができます。

```sql:SQL
USE CATALOG <catalog_name>;
USE SCHEMA <schema_name>;
SELECT * from <table_name>;
```

```py:Python
spark.sql("USE CATALOG <catalog_name>")
spark.sql("USE SCHEMA <schema_name>")

display(spark.table("<table_name>"))
```

```r:R
library(SparkR)

sql("USE CATALOG <catalog_name>")
sql("USE SCHEMA <schema_name>")

display(tableToDF("<table_name>"))
```

```scala:Scala
spark.sql("USE CATALOG <catalog_name>")
spark.sql("USE SCHEMA <schema_name>")

display(spark.table("<table_name>"))
```

あるいは、3レベル名前空間記述を使うことができます。

```sql:SQL
SELECT * from <catalog_name>.<schema_name>.<table_name>;
```

```py:Python
display(spark.table("<catalog_name>.<schema_name>.<table_name>"))
```

```r:R
library(SparkR)

display(tableToDF("<catalog_name>.<schema_name>.<table_name>"))
```

```scala:Scala
display(spark.table("<catalog_name>.<schema_name>.<table_name>"))
```

3レベルの名前空間記述を用いることで、複数のカタログやスキーマのデータに対するクエリーをシンプルなものにします。

また、`<catalog_name>`を`hive_metastore`に設定することで、Hiveメタストアのデータに対する3レベル名前空間記述を使用することができます。

# Databricks SQLでテーブルとビューを探索する

[データエクスプローラ](https://docs.databricks.com/data/index.html)を用いることで、クラスターを実行することなしにクイックにテーブルやビューを探索することができます。

1. データエクスプローラを開くには、サイドバーの![](https://docs.databricks.com/_images/data-icon.png)**データ**をクリックします。
1. データエクスプローラでは、テーブルやビューを参照するためにカタログやスキーマを選択します。

Hiveメタストアのオブジェクトに対しては、データエクスプローラを使用するために稼働中のSQLウェアハウスが必要となります。

# テーブル、ビューからのSELECT

ノートブックからテーブルやビューをSELECTするには:

1. サイドバーを用いてData Science & Engineeringに切り替えます。
1. Unity Catalog用に設定されたData Science & Engineering、あるいはDatabricks Machine Learning[クラスター](https://qiita.com/taka_yayoi/items/9f13a2b97ebd11cfd04f#unity-catalog%E3%81%AB%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%81%A7%E3%81%8D%E3%82%8B%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AE%E4%BD%9C%E6%88%90)にノートブックをアタッチします。
1. ノートブックで、Unity Catalogのテーブルやビューを参照するクエリーを作成します。ワークスペースローカルのHiveメタストアを含む複数のカタログやスキーマから容易にデータをSELECTするために、[3レベルの名前空間記述](#3レベルの名前空間記述)を使用することができます。

    :::note
    **注意**
    シングルユーザーアクセスモードを使用するクラスターでビューから読み込みを行うには、ユーザーは参照されるすべてのテーブルやビューに対する`SELECT`権限が必要となります。
:::

Databricks SQLでテーブルやビューからSELECTするには:

1. サイドバーを用いてDatabricks SQLに切り替えます。
1. サイドバーの**SQL Editor**をクリックします。
1. Unity Catalog用に設定された[SQLウェアハウス](https://qiita.com/taka_yayoi/items/9f13a2b97ebd11cfd04f#unity-catalog%E3%81%AB%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%81%A7%E3%81%8D%E3%82%8Bsql%E3%82%A6%E3%82%A7%E3%82%A2%E3%83%8F%E3%82%A6%E3%82%B9%E3%81%AE%E4%BD%9C%E6%88%90)を選択します。
1. クエリーを構成します。クエリーにテーブルやビューを入力するには、カタログやスキーマを選択し、入力するテーブルやビューの名前をクリックします。
1. **Run**をクリックします。

# ファイルからのSELECT

外部ロケーションに格納されているデータからテーブルを作成する前にデータを探索したい場合、データエクスプローラあるいは以下のコマンドを用いることができます。

**アクセス権が必要です:** ロケーションに格納されているデータファイルの一覧を取得するために、クラウドストレージパスと関連づけられている外部ロケーションに対する`READ FILES`権限が必要となります。

**SQL**
1. クラウドストレージパスのファイルを一覧します:

    ```sql:SQL
    LIST 's3://<path_to_files>';
    ```

1. 指定したパスのファイルのデータをクエリーします:

    ```sql:SQL
    SELECT * FROM <format>.'s3://<path_to_files>';
    ```

**Python**

1. クラウドストレージパスのファイルを一覧します:

    ```py:Python
    display(spark.sql("LIST 's3://<path_to_files>'"))
    ```

1. 指定したパスのファイルのデータをクエリーします:

    ```py:Python
    display(spark.read.load("s3://<path_to_files>"))
    ```

**R**

1. クラウドストレージパスのファイルを一覧します:

    ```r:R
    library(SparkR)

    display(sql("LIST 's3://<path_to_files>'"))
    ```

1. 指定したパスのファイルのデータをクエリーします:

    ```r:R
    library(SparkR)

    display(loadDF("s3://<path_to_files>"))
    ```

**Scala**

1. クラウドストレージパスのファイルを一覧します:

    ```scala:Scala
    display(spark.sql("LIST 's3://<path_to_files>'"))
    ```

1. 指定したパスのファイルのデータをクエリーします:

    ```scala:Scala
    display(spark.read.load("s3://<path_to_files>"))
    ```

# 次のステップ

- [Manage privileges in Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

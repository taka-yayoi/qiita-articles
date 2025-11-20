---
title: DatabricksにおけるJDBC経由でのSQLデータベースの活用
tags:
  - Database
  - JDBC
  - Databricks
private: false
updated_at: '2021-11-19T12:42:58+09:00'
id: 4cd7ff171bbbe227eb4d
organization_url_name: databricks
slide: false
ignorePublish: false
---
[SQL databases using JDBC \| Databricks on AWS](https://docs.databricks.com/data/data-sources/sql-databases.html) [2021/8/13時点]の翻訳です。

JDBCドライバーを用いて様々なSQLデータベースにクエリーを行うためにDatabricksを利用できます。

Databricksランタイムには、MySQLドライバーとして`org.mariadb.jdbc`ドライバーが含まれています。

Databricksランタイムには、[Microsoft SQL Server](https://docs.microsoft.com/sql/sql-server/sql-server-technical-documentation)、[Azure SQL Database](https://azure.microsoft.com/services/sql-database/)向けのJDBCドライバーが含まれています。

PostgreSQL、Oracleのような他のSQLデータベースを使用することも可能です。Databricksでドライバーが提供されていないデータベースに対してい、JDBCライブラリをインストールする方法に関しては、[ライブラリ](https://qiita.com/taka_yayoi/items/d3a46efdc1ad01a581d0)をご覧ください。

本書では、JDBCを用いてSQLデータベースに接続するためにどのようにDataFrame APIを使うのか、JDBCインタフェースを通じてどのように並列性を制御するのかを説明します。本書の最後には、Scala API、Python、Spark SQLのサンプルを示しています。JDBC経由でSQLデータベースに接続する際にサポートされている引数に関しては、[JDBC To Other Databases](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html)をご覧ください。

> **重要！**
本書のサンプルでは、JDBCのURLにユーザー名、パスワードを含めていません。データベースの認証情報をシークレットとして保存し、ノートブック上で`java.util.Properties`オブジェクトに認証情報を埋め込むように[シークレット管理](https://qiita.com/taka_yayoi/items/338ef0c5394fe4eb87c0)ユーザーガイドに従うことをお勧めします。以下に例を示します。

> ```scala:Scala
val jdbcUsername = dbutils.secrets.get(scope = "jdbc", key = "username")
val jdbcPassword = dbutils.secrets.get(scope = "jdbc", key = "password")
```

> シークレット管理の完全なサンプルに関しては、[Databricksシークレットのワークフロー例](https://qiita.com/taka_yayoi/items/b9bdaa63e7c991d95092)をご覧ください。

# クラウドとの接続の確立

DatabricksのVPCはSparkクラスターのみの接続を許可しています。他のインフラストラクチャにアクセスする際のベストプラクティスは、[VPCピアリング](https://docs.databricks.com/administration-guide/cloud-configurations/aws/vpc-peering.html)を使用することです。VPCピアリング確立後に、クラスターで`netcat`ユーティリティを用いて確認することできます。

```bash:Bash
%sh nc -vz <jdbcHostname> <jdbcPort>
```

# MySQLとの接続の確立

このサンプルでは、JDBCドライバーを使ってMySQLにクエリーを実行します。

## ステップ1: JDBCドライバーが利用できることを確認する

以下のステートメントでは、お使いのclasspathにドライバークラスが存在しているかどうかを確認しています。Pythonノートブックのように他の言語のノートブックにおいても、`%scala`マジックコマンドを用いてテストすることができます。

```scala:Scala
Class.forName("org.mariadb.jdbc.Driver")
```

## ステップ2: JDBC URLを作成する

```scala:Scala
val jdbcHostname = "<hostname>"
val jdbcPort = 3306
val jdbcDatabase = "<database>"

// Create the JDBC URL without passing in the user and password parameters.
val jdbcUrl = s"jdbc:mysql://${jdbcHostname}:${jdbcPort}/${jdbcDatabase}"

// Create a Properties() object to hold the parameters.
import java.util.Properties
val connectionProperties = new Properties()

connectionProperties.put("user", s"${jdbcUsername}")
connectionProperties.put("password", s"${jdbcPassword}")
```

## ステップ3: MySQLデータベースとの接続を確認する

```scala:Scala
import java.sql.DriverManager
val connection = DriverManager.getConnection(jdbcUrl, jdbcUsername, jdbcPassword)
connection.isClosed()
```

# SQL Serverとの接続の確立

このサンプルでは、JDBCドライバーを使ってSQL Serverにクエリーを実行します。

## ステップ1: JDBCドライバーが利用できることを確認する

```scala:Scala
Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver")
```

## ステップ2: JDBC URLを作成する

```scala:Scala
val jdbcHostname = "<hostname>"
val jdbcPort = 1433
val jdbcDatabase = "<database>"

// Create the JDBC URL without passing in the user and password parameters.
val jdbcUrl = s"jdbc:sqlserver://${jdbcHostname}:${jdbcPort};database=${jdbcDatabase}"

// Create a Properties() object to hold the parameters.
import java.util.Properties
val connectionProperties = new Properties()

connectionProperties.put("user", s"${jdbcUsername}")
connectionProperties.put("password", s"${jdbcPassword}")
```

## ステップ3: SQL Serverデータベースとの接続を確認する

```scala:Scala
val driverClass = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
connectionProperties.setProperty("Driver", driverClass)
```

# SSL経由でのPostgreSQLデータベースとの接続

JDBCを用いて、SSL経由でPostgreSQLデータベースに接続するためには、以下の手順を踏みます。

- PEMではなくPK8、DERフォーマットで証明書と鍵を指定する必要があります。
- 全てのノードが読み取りを行えるように、DBFSの`/dbfs`フォルダーに証明書と鍵を格納する必要があります。

以下のPythonサンプルノートブックでは、一連のPEMファイルからPK8、DERファイルを作成し、これらのファイルからデータフレームを作成する方法を説明しています。このサンプルでは以下のPEMファイルが存在することを想定しています。

- クライアント公開鍵証明書として`client_cert.pem`
- クライアント秘密鍵として`client_key.pem`
- サーバ証明書として`server_ca.pem`

```bash:Bash
%sh
# Copy the PEM files to a folder within /dbfs so that all nodes can read them.
mkdir -p <target-folder>
cp <source-files> <target-folder>
```

```bash:Bash
%sh
# Convert the PEM files to PK8 and DER format.
cd <target-folder>
openssl pkcs8 -topk8 -inform PEM -in client_key.pem -outform DER -out client_key.pk8 -nocrypt
openssl x509 -in server_ca.pem -out server_ca.der -outform DER
openssl x509 -in client_cert.pem -out client_cert.der -outform DER
```

```py:Python
# Create the DataFrame.
df = (spark
  .read
  .format("jdbc")
  .option("url", <connection-string>)
  .option("dbtable", <table-name>)
  .option("user", <username>)
  .option("password", <password>)
  .option("ssl", True)
  .option("sslmode", "require")
  .option("sslcert", <target-folder>/client_cert.der)
  .option("sslkey", <target-folder>/client_key.pk8)
  .option("sslrootcert", <target-folder>/server_ca.der)
  .load()
)
```

以下の通り置き換えてください。

- `<source-files>`を`/dbfs/FileStore/Users/someone@example.com/*`のようなソースディレクトリにある`.pem`ファイルのリストで置き換えてください。
- `<target-folder>`を`/dbfs/databricks/driver/ssl`のように生成したPK8、DERファイルを格納するターゲットディレクトリの名前で置き換えてください。
- `<connection-string>`をデータベースに対するJDBC URL接続文字列で置き換えてください。
- `<table-name>`をデータベースで使用するテーブル名で置き換えてください。
- `<username>`と`<password>`をデータベースにアクセスするために使用するユーザー名、パスワードで置き換えてください。

# JDBCからのデータ読み込み

このセクションではデータベーステーブルからデータをロードします。ここでは、Spark環境にテーブルを読み込む際に単一のJDBC接続を用います。並列での読み取りに関しては、並列性の管理をご覧ください。

```Scala:Scala
val employees_table = spark.read.jdbc(jdbcUrl, "employees", connectionProperties)
```

Sparkはデータベーステーブルからスキーマを自動で読み込み、データベースの型をSpark SQL型にマッピングします。

```Scala:Scala
employees_table.printSchema
```

JDBCテーブルに対してクエリーを実行することができます。

```Scala:Scala
display(employees_table.select("age", "salary").groupBy("age").avg("salary"))
```

# JDBCへのデータ書き込み

ここでは、既存のSpark SQLテーブル`diamonds`からデータベースにデータを書き込む方法を説明します。

```sql:SQL
select * from diamonds limit 5
```

以下のコードは、データを`diamonds`というデータベーステーブルに書き込みます。予約されているキーワードのカラム名は例外を引き起こします。サンプルテーブルには`table`というカラムがあるので、JDBC APIにプッシュする前に`withColumnRenamed()`を用いてカラム名を変更することができます。

```scala:Scala
spark.table("diamonds").withColumnRenamed("table", "table_number")
     .write
     .jdbc(jdbcUrl, "diamonds", connectionProperties)
```

Sparkは自動でDataFrameスキーマから適切なスキーマを決定し、データベースのテーブルを作成します。

デフォルトの挙動は、新規にテーブルを作成し、すでに同じ名前のテーブルが存在する場合にはエラーメッセージをスローするというものです。この挙動を変更するために、Spark SQLの`SaveMode`機能を使用することができます。例えば、以下にテーブルに行を追加するサンプルを示します。

```scala:Scala
import org.apache.spark.sql.SaveMode

spark.sql("select * from diamonds limit 10").withColumnRenamed("table", "table_number")
  .write
  .mode(SaveMode.Append) // <--- Append to the existing table
  .jdbc(jdbcUrl, "diamonds", connectionProperties)
```

既存テーブルを上書きすることもできます。

```scala:Scala
spark.table("diamonds").withColumnRenamed("table", "table_number")
  .write
  .mode(SaveMode.Overwrite) // <--- Overwrite the existing table
  .jdbc(jdbcUrl, "diamonds", connectionProperties)
```

# データベースエンジンへのクエリープッシュダウン

全てのクエリーをデータベースにプッシュダウンし、結果のみを受け取るようにすることができます。`table`パラメーターは読み取りを行うJDBCテーブルを特定します。SQLクエリーの`FROM`句で妥当なものは何でも使用できます。

```scala:Scala
// Note: The parentheses are required.
val pushdown_query = "(select * from employees where emp_no < 10008) emp_alias"
val df = spark.read.jdbc(url=jdbcUrl, table=pushdown_query, properties=connectionProperties)
display(df)
```

# プッシュダウンの最適化

テーブル全体を取り込むことに加え、データベースにクエリーをプッシュダウンし処理を行わせ、結果のみを取得することが可能です。

```scala:Scala
// Explain plan with no column selection returns all columns
spark.read.jdbc(jdbcUrl, "diamonds", connectionProperties).explain(true)
```

`DataFrame`メソッドを用いることで、カラムを削減し、クエリーの述語をデータベースにプッシュダウンすることができます。

```scala:Scala
// Explain plan with column selection will prune columns and just return the ones specified
// Notice that only the 3 specified columns are in the explain plan
spark.read.jdbc(jdbcUrl, "diamonds", connectionProperties).select("carat", "cut", "price").explain(true)

// You can push query predicates down too
// Notice the filter at the top of the physical plan
spark.read.jdbc(jdbcUrl, "diamonds", connectionProperties).select("carat", "cut", "price").where("cut = 'Good'").explain(true)
```

# 並列性の管理

Spark UIでは、起動さえたタスクの数を意味するパーティション数を確認することができます。それぞれのタスクはエグゼキューターに分配され、JDBCインタフェースを介した読み書きの並列性を増加することができます。パフォーマンス改善に寄与する`fetchsize`のような他のパラメーターに関しては[Spark SQL programming guide](https://spark.apache.org/docs/latest/sql-programming-guide.html#jdbc-to-other-databases)を参照ください。

パーティションを指定するために2つの[DataFrameReader API](https://spark.apache.org/docs/latest/api/scala/org/apache/spark/sql/DataFrameReader.html)を使用することができます。

- `jdbc(url:String,table:String,columnName:String,lowerBound:Long,upperBound:Long,numPartitions:Int,...) `は数値カラムの名前(`columnName`)、2つの範囲の終端(`lowerBound`, `upperBound`)、ターゲットの`numPartitions`を受け取り、指定した範囲を`numPartitions`個のタスクに均等に分割します。データベースのテーブルが、オートインクリメントの主キーのように均等に分布している数値カラムのインデックスを持っていれば、この処理はうまく動作します。数値カラムが極端に偏っていると、タスクのバランスが悪くなるため、あまりうまく動作しません。
- `jdbc(url:String,table:String,predicates:Array[String],...)`は、カスタムパーティションを定義するために使用する`WHERE`条件の配列を受け取ります。偏りに対応するために非数値のカラムでパーティショニングを行う際に有用です。カスタムパーティションを定義する際、パーティションカラムがNULLを許容する場合、`NULL`を考慮するようにしてください。境界の述語の記述はより複雑なロジックを必要とするため、2つ以上のカラムを用いてマニュアルでパーティションを定義しないでください。

## JDBCの読み込み

データセットのカラムの値に基づいて分割境界を指定することができます。

これらのオプションは読み込み並列性を指定します。これらのオプションはどれか一つを指定する際には、*全て*指定する必要があることに注意してください。`lowerBound`と`upperBound`はパーティションの幅を定義しますが、テーブルの行をフィルタリングしません。このため、Sparkはテーブルの全ての行からパーティションを作成して返却します。

以下の例では、`columnName`、`lowerBound`、`upperBound`、`numPartitions`パラメーターを用いて、`emp_no`カラムに対して、エグゼキューターでテーブル読み込みを分割しています。

```scala:Scala
val df = (spark.read.jdbc(url=jdbcUrl,
  table="employees",
  columnName="emp_no",
  lowerBound=1L,
  upperBound=100000L,
  numPartitions=100,
  connectionProperties=connectionProperties))
display(df)
```

## JDBCの書き込み

Sparkのパーティションの数は、JDBC APIを通じてデータをプッシュするのに使用する接続数を意味します。既存のパーティション数に基づいて`coalesce(<N>)`や`repartition(<N>)`をコールすることで、並列性をコントロールすることができます。パーティション数を減らす場合には`coalesce`をコールし、パーティション数を増やしたい場合には`repartition`をコールします。

```scala:Scala
import org.apache.spark.sql.SaveMode

val df = spark.table("diamonds")
println(df.rdd.partitions.length)

// Given the number of partitions above, you can reduce the partition value by calling coalesce() or increase it by calling repartition() to manage the number of connections.
df.repartition(10).write.mode(SaveMode.Append).jdbc(jdbcUrl, "diamonds", connectionProperties)
```

# Pythonのサンプル

以下のPythonサンプルでは、Scalaのサンプルと同じタスクのいくつかをカバーしています。

## JDBC URLの作成

```py:Python
jdbcHostname = "<hostname>"
jdbcDatabase = "employees"
jdbcPort = 3306
jdbcUrl = "jdbc:mysql://{0}:{1}/{2}?user={3}&password={4}".format(jdbcHostname, jdbcPort, jdbcDatabase, username, password)
```

上述したScalaのサンプルと同様に、認証情報とドライバークラスを含むディクショナリーを指定することができます。

```py:Python
jdbcUrl = "jdbc:mysql://{0}:{1}/{2}".format(jdbcHostname, jdbcPort, jdbcDatabase)
connectionProperties = {
  "user" : jdbcUsername,
  "password" : jdbcPassword,
  "driver" : "com.mysql.jdbc.Driver"
}
```

### データベースエンジンへのクエリープッシュダウン

```py:Python
pushdown_query = "(select * from employees where emp_no < 10008) emp_alias"
df = spark.read.jdbc(url=jdbcUrl, table=pushdown_query, properties=connectionProperties)
display(df)
```

### 複数ワーカーでのJDBCコネクションからの読み込み

```py:Python
df = spark.read.jdbc(url=jdbcUrl, table="employees", column="emp_no", lowerBound=1, upperBound=100000, numPartitions=100)
display(df)
```

# Spark SQLのサンプル

JDBCコネクションを使用するSpark SQLのテーブルやビューを定義するには、最初にJDBCテーブルをSparkのデータソース、一時ビューとして登録する必要があります。

詳細に関しては、以下を参照ください。

- Databricksランタイム 7.x以降：[CREATE TABLE USING](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-table-datasource.html)、[CREATE VIEW](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-view.html)
- Databricksランタイム 5.5 LTS、6.x：[Create Table](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/create-table.html)、[Create View](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/create-view.html)

```sql:SQL
CREATE TABLE <jdbcTable>
USING org.apache.spark.sql.jdbc
OPTIONS (
  url "jdbc:<databaseServerType>://<jdbcHostname>:<jdbcPort>",
  dbtable "<jdbcDatabase>.atable",
  user "<jdbcUsername>",
  password "<jdbcPassword>"
)
```

## テーブルへのデータ追加

Spark SQLを用いてテーブルにデータを追加します。

```sql:SQL
INSERT INTO diamonds
SELECT * FROM diamonds LIMIT 10 -- append 10 records to the table

SELECT count(*) record_count FROM diamonds --count increased by 10
```

## テーブルのデータの上書き

Spark SQLを用いてテーブルのデータを上書きます。これによって、データベースで`diamonds`テーブルのdrop、createが行われます。

```sql:SQL
INSERT OVERWRITE TABLE diamonds
SELECT carat, cut, color, clarity, depth, TABLE AS table_number, price, x, y, z FROM diamonds

SELECT count(*) record_count FROM diamonds --count returned to original value (10 less)
```

## テーブルに対するビューの作成

Spark SQLを用いてテーブルに対するビューを作成します。

```sql:SQL
CREATE OR REPLACE VIEW pricey_diamonds
    AS SELECT * FROM diamonds WHERE price > 5000;
```

# データ読み取りにおけるパフォーマンスの最適化

外部のJDBCデータベースからデータを読み込む際に処理が遅い場合、このセクションで説明されているパフォーマンス改善のテクニックが役立つかもしれません。

## JDBC読み取りが並列実行されていることを確認する

並列でデータを読み込むためには、外部データベースに対して同時に複数のクエリーを発行できるようにSpark JDBCデータソースが適切なパーティション情報で設定されている必要があります。パーティショニングを設定しないと、単一のJDBCクエリーを用いて全てのデータをドライバーにフェッチすることになり、ドライバーがOOM例外を引き起こすリスクが高まります。

パーティションが設定されない状態でのJDBCの読み込みのサンプルを以下に示します。
[SQL databases using JDBC \| Databricks on AWS](https://docs.databricks.com/_images/jdbc-read-no-partition.png)

`columnName`として引き渡されたカラム`partitionColumn`、範囲の終端(`lowerBound`, `upperBound`)、パーティションの最大数`numPartitions`を用いてパーティションが設定されたJDBC読み込みのサンプルを示します。
![](https://docs.databricks.com/_images/jdbc-read-partitioned.png)

## JDBC `fetchSize`パラメーターをチューニングする

JDBCドライバーには、リモートのJDBCデータベースから一度にフェッチする行数をコントロールする`fetchSize`パラメーターがあります。この値を小さく設定してしまうと、全てのリザルトセットを取得するために外部データベースとSparkの間で大量のリクエストのやり取りが発生し、ワークロードがレーテンシーを引き起こす可能性が高まります。あまりに大きい値にするとOOM例外のリスクが高まります。最適値はワークロードに依存(結果のスキーマ、結果の文字列サイズなどに依存)しますが、デフォルト値から徐々に増やしていくことで、大きなパフォーマンス改善を行うことができます。

Oracleのデフォルトの`fetchSize`は10です。徐々に100まで増やすことで、劇的にパフォーマンスを改善することができ、以下のように2000のような大きな値に増やすことでさらに性能を改善することができます。

```java:Java
PreparedStatement stmt = null;
ResultSet rs = null;

try {
  stmt = conn. prepareStatement("select a, b, c from table");
  stmt.setFetchSize(100);

  rs = stmt.executeQuery();
  while (rs.next()) {
    ...
  }
}
```

Oracle JDBCドライバーにおけるパラメーターチューニングの一般的な議論については、[Make your java run faster](https://makejavafaster.blogspot.com/2015/06/jdbc-fetch-size-performance.html)をご覧ください。

## インデックスのインパクトを考慮する

(パーティションテクニックの一つを用いて)並列読み込みを行なっている際、SparkはJDBCデータベースに同時にクエリーを発行します。これらのクエリーがテーブルのフルスキャンを要求することになると、リモートデータベースにおけるボトルネックとなり、処理が非常に遅くなります。このため、パーティションカラムを選択する際にはインデックスのインパクトを考慮し、それぞれのパーティションのクエリーが適切活効率的に並列処理されるように、カラムを選択すべきです。

> **重要！**
データベースにパーティションカラムのインデックスがあることを確認してください。

ソーステーブルにシングルカラムのインデックスが定義されていない場合、パーティションカラムとして、複合インデックスの先頭(左端)カラムを選択することができます。複合インデックスのみが利用できる場合、多くのデータベースは先頭カラムを用いた検索を行う際に結合インデックスを使用することができます。このため、マルチカラムインデックスの先頭カラムをパーティションカラムとして使用することができます。

## パーティション数が適切かどうかを検討する

外部データベースからの読み込みにおいてあまりに多くのパーティションを使用すると、データベースがあまりに多くのクエリーで圧倒されてしまうリスクを抱えることになります。多くのDBMSシステムでは同時接続数の制限を設けています。スタート地点として、並列性を最大にしつつもクエリーの総数を合理的な制限に収めるように、お使いのクラスターのコア数、タスクスロット数に近い数のパーティションから始めます。JDBCのレコードをフェッチした後に高い並列性を必要とするが、データベースにあまりに多くの同軸エリーを発行したくないのであれば、JDBC読み込みにおいては、少ない`numPartitions`を使用し、Sparkで明示的に`repartition()`を実行することを検討してください。

## データベース固有のチューニング技術を検討する

データベースベンダーがETL、バルクアクセスのワークロードにおけるパフォーマンスチューニングのガイドを提供している場合があります。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

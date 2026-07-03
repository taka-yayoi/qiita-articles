---
title: Apache Spark 2.1におけるクラウドネイティブアーキテクチャ向けのスケーラブルなパーティションハンドリング
tags:
  - Spark
  - Databricks
private: false
updated_at: '2022-05-11T14:20:13+09:00'
id: 7f3e51abe2cfc1efbb4b
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Scalable Partition Handling for Cloud\-Native Architecture in Apache Spark 2\.1 \- The Databricks Blog](https://databricks.com/blog/2016/12/15/scalable-partition-handling-for-cloud-native-architecture-in-apache-spark-2-1.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**注意**
2016年の記事です。
:::

Apache Spark 2.1はすぐそこまでやってきています。コミュニティはリリース候補に対する投票プロセスを踏んでいます。このブログ記事では、間も無くのリリースに含まれる重要な機能：スケーラブルパーティションハンドリングを議論します。

Spark SQLを用いることで、単一のジョブでテラバイトのデータに対するクエリーが可能となります。しかし、多くのケースでは、ユーザーは全体データの小規模なサブセットのみを読み込みたいケースもあります。例えば、全世界のユーザーのアクティビティではなく、サンフランシスコのユーザーのアクティビティをスキャンしたいというケースです。これは、通常使用される日付や国のようなフィールドでテーブルのデータファイルをパーティションすることで実現されます。そして、SQLはユーザーのクエリーに関係のないファイルを「切り落とし」たり、スキップするためにこのパーティション情報を使用します。しかし、これまでのバージョンのSparkでは、どのパーティションが存在するのかをSparkが検索する必要があり、パーティションの数が非常に大きい場合、最初のテーブルの読み込みが遅いケースがありました。

**Spark 2.1において、テーブルパーティションの小さな一部にアクセスするクエリーの初期のレーテンシーを劇的に改善しました。** いくつかのケースにおいては、起動直後のSparkクラスターで数十分かかっていたクエリーが数秒で実行できるようになります。我々が行なった改善は、テーブルのメモリーのオーバヘッドの削減であり、コールド状態でスタートするSQL体験を、テーブルのメタデータがメモリーに完全にキャッシュされた「ホット」状態にすることができます。

**また、Spark 2.1では、データソースとHiveテーブルのパーティション管理機能を統合します。** これは、特定のパーティションの追加、削除、再配置のようなパーティションDDLオペレーションを両方のタイプのテーブルでサポートすることを意味します。

# Sparkにおけるテーブル管理

なぜレーテンシーの問題が存在したのかを理解するために、最初にこれまでのバージョンのSparkにおいて、どのようにテーブル管理が行われていたのかを説明させてください。これらのバージョンにおいては、Sparkはカタログ内の2つのタイプのテーブルをサポートしています。

1. [データソーステーブル](https://databricks.com/blog/2015/01/09/spark-sql-data-sources-api-unified-data-access-for-the-spark-platform.html)はSparkで作成される好適なフォーマットです。このタイプのテーブルは`df.write.partitionBy("date").saveAsTable("my_metrics")`や、`CREATE TABLE my_metrics USING parquet PARTITIONED BY date`のような[CREATE TABLE文](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-table.html)を用いて、オンザフライでデータフレームをファイルシステムに書き込むことで定義することができます。以前のバージョンでは、Sparkはファイルシステムからデータソーステーブルのメタデータを検知し、メモリーにキャッシュします。このメタデータにはパーティションの一覧と、パーティション内のファイルの統計情報が含まれます。キャッシュされると、入力されるクエリーに対応するために、メモリー内でパーティションを非常にクイックにプルーニングを行うことができます。
1. [Apache Hive](https://databricks.com/jp/glossary/apache-hive)デプロイメントから来たユーザーに対しては、Spark SQLはHive serdesによって定義されるカタログテーブルを読み込むことができます。可能な場合、Spark SQLにおけるIOパフォーマンスのメリットを得るために、Sparkは透明性を持ってこのようなHiveテーブルをデータソースフォーマットに変換します。SparkはHiveメタストアからテーブルとパーティションのメタデータを読み込むことで、これを内部的に行い、メモリーにキャッシュします。

この戦略は、テーブルのメタデータがメモリーにキャッシュされると最適なパフォーマンスを提供しますが、2つの否定的な側面があります。第一に、テーブルに対する最初のクエリーは、Sparkが全てのテーブルパーティションのメタデータをロードするまでブロックされます。大規模なパーティショニングされたテーブルにおいては、最初のクエリーに対してファイルのメタデータを検索するためにファイルシステムを再起的にスキャンするので、特にデータがS3のようなクラウドストレージに格納されている場合には数分の時間を要することになります。第二に、テーブルの全てのメタデータは、ドライバープロセスにおいてインメモリーでマテリアライズされる必要があり、メモリー使用量を増加させます。

我々は多くのお客様、他の大規模Sparkユーザーにおいてこの問題が生じていることを目撃していました。他のSpark APIを用いて直接ファイルを読み込むことで最初のクエリーのレーテンシーを回避できるケースはありましたが、ワークアラウンドなしにスケールできるようなテーブルのパフォーマンスが必要と考えました。Spark 2.1においては、Databricksはこのオーバーヘッドを排除し、データソースとHiveフォーマットテーブルの管理を統合するためにVideoAmpとコラボレーションしました。

VideoAmpは、データプラットフォームの導入時点からSpark 1.1以降のSpark SQLを使用し続けていました。リアルタイムのデジタル広告マーケットプレースにおける需要側のプラットフォームとして、一日あたり数十億のイベントを受け取り、格納していました。今では、VideoAmpでは数万のパーティションを持つテーブルを抱えることになりました。

Michael Allman (VideoAmp)はこのプトジェクトへの関与に関して以下のように述べています。

> Spark 2.1以前は、我々の最大のテーブルのメタデータの取得に数分を要しており、新たなパーティションが追加されるたびに毎回再実行しなくてはなりませんでした。Spark 2.0のリリースのすぐ後に、遅延パーティションメタデータロードに基づく新たなアプローチのプロトタイプをスタートしました。同時に、我々のアイデアを説明するt前にSpark開発者コミュニティにアプローチしました。プルリクエストとして、我々のプロトタイプをSparkのソースリポジトリにサブミットし、信頼性とパフォーマンスをプロダクションレベルに引き上げるためのコラボレーションをスタートしました。

# パフォーマンスベンチマーク

技術的な詳細に踏み込む前に、最初に50,000以上のパーティションを持つ内部メトリクステーブルの一つに対するクエリーのレーテンシーの改善を説明させてください(Databricksにおいては、自分のドッグフードを食べるべきだと信じています)。テーブルは以下のように日付とメトリクスタイプでパーティショニングされています。

```sql:SQL
CREATE TABLE metricData (
    value BIGINT,
    dimensions struct<...>,
    date STRING,
    metric STRING)
USING parquet
OPTIONS (path 'dbfs:/mnt/path/to/data-root')
PARTITIONED BY (date, metric)
```

8台のワーカー、32コア、250GBメモリーを持つ小規模のDatabricksクラスターを使用します。日、週、月のデータに対するシンプルな集計クエリーを実行し、新規に起動したSparkクラスターにおける*最初の結果取得に要する時間*を評価します。

```sql:SQL
SELECT metric, avg(value)
FROM metricData
WHERE date >= "2016-11-01" AND date <= "2016-11-07"  // ex. 1 week
GROUP BY metric
```

Spark 2.1でスケーラブルなパーティション管理が有効化されると、日毎のデータの読み込みは10秒強になりました。この時間は、クエリーでアクセスされるパーティションの数に対して線形にスケールします。この時間は何によるものなのかを理解するために、クエリー計画とSparkジョブ実行に要した時間にブレークダウンしました。
![](https://databricks.com/wp-content/uploads/2016/12/spark-2-1-scalable-partition-management-comparison.png)

より多くのデータをスキャンすることになるため、クエリー計画の時間(赤い棒)が実行時間(青い棒)に比例して増加していることがわかります。クエリーを再度実行した際、メタデータのキャッシュによって計画に要する時間は無視できる(グラフに表示するには小さすぎるくらい)ようになります。

しかし、この改善フラグを無効化すると、クエリーの選択性に関係なく、テーブルに対する最初のクエリーでは約200秒の大きな定数の要因が存在することがわかりました。

これらの改善は、多くのケースでファイルシステムのメタデータパフォーマンスが低く、短命のSparkクラスターを使用するためメタデータの頻繁な再キャッシュを必要とするクラウドネイティブのSparkデプロイメントで最も顕著なものとなります。しかし、HDFSユーザーであっても、非常に大きなパーティションテーブルではメリットを享受することができます。

## VideoAmp Productionのベンチマーク

また、我々はVideoAmpにおけるワークロードのプロダクションクエリーにおいても、これらの改善が多大なるインパクトをもたらしたことを説明します。彼らは、数十のカラムを取り扱い、定期的に更新される数万のパーティションを持つテーブルを複数の集計、ユニオンを行うマルチステージのクエリーを実行していました。

VideoAmpは定常的に実行するクエリーのいくつかで、計画に費やされる時間の割合を計測し、Spark 2.0とSpark 2.1の間の性能を比較しました。ここでは、重大な、場合によってはドラマティックな改善が認められました。
![](https://databricks.com/wp-content/uploads/2016/12/videoamp-production-queries-planning-time.png)

# 実装

これらのメリットは、Spark SQL内部における2つの大きな変更点によってもたらされました。

1. SparkはHive、データソーステーブル両方に対して、テーブルパーティションのメタデータをシステムのカタログ(Hiveメタストアなど)に永続化します。新たな[PruneFileSourcePartitions](https://github.com/apache/spark/blob/branch-2.1/sql/core/src/main/scala/org/apache/spark/sql/execution/datasources/PruneFileSourcePartitions.scala)ルールによって、Catalystオプティマイザはファイルシステムからメタデータを読み込む前に、[論理的プランニング](https://databricks.com/blog/2015/04/13/deep-dive-into-spark-sqls-catalyst-optimizer.html)を行う際にパーティションを切り落とすためにこのカタログを使用します。これによって、使用されないパーティションのファイルを特定する必要がなくなります。
1. ファイルの統計情報を事前にキャッシュするのではなく、プランニングの際にインクリメンタルかつ部分的にキャッシュされます。Sparkは[物理的プランニング](https://databricks.com/blog/2015/04/13/deep-dive-into-spark-sqls-catalyst-optimizer.html)の際に、ファイルを読み込みタスクに分配するためにファイルのサイズを知る必要があります。メモリーに全てのテーブルファイル統計情報を貪欲にキャッシュするのではなく、メモリーエラーのリスクを引き起こすことなしに繰り返されるクエリーを堅牢に高速化するために、今ではテーブルは[(設定可能な)250MBの固定サイズのキャッシュ](https://databricks.com/blog/2015/04/13/deep-dive-into-spark-sqls-catalyst-optimizer.html)を共有します。

これらを変更を組み合わせは、Sparkがコールドスタートしている状態でもクエリーが高速になることを意味します。インクリメンタルなファイル統計情報のキャッシュによって、古いパーティション管理戦略と比較して、繰り返されるクエリーに対するパフォーマンス上のペナルティがほとんど無いことになります。

# 新たにサポートされたパーティションDDL

これらの変更によるその他のメリットには、これまではHiveテーブルでのみ利用できたいくつかのDDLコマンドのデータソーステーブルにおけるサポートがあります。これらのDDLによって、パーティション`(date='2016-11-01', metric='m1')`をデフォルトの`/date=2016-11-01/metric=m1`以外の任意のファイルシステムの場所に変更するために、パーティションのファイルの場所を変更することができます。

```sql:SQL
ALTER TABLE table_name ADD [IF NOT EXISTS]
    (PARTITION part_spec [LOCATION path], ...)
ALTER TABLE table_name DROP [IF EXISTS] (PARTITION part_spec, ...)
ALTER TABLE table_name PARTITION part_spec SET LOCATION path
SHOW PARTITIONS [db_name.]table_name [PARTITION part_spec]
```

もちろん、パーティションテーブルに追加するために、`df.write.insertInto and df.write.saveAsTable`のようなネイティブのデータフレームAPIを使用することもできます。DatabricksでサポートされるDDLの詳細に関しては、[言語マニュアル](https://docs.databricks.com/spark/latest/spark-sql/index.html)をご覧ください。

# マイグレーションのティップス

Spark 2.1で作成された新たなデータソーステーブルでは、デフォルトで新たなスケーラブルなパーティション管理戦略を使用し、後方互換性のために既存テーブルでは有効化されません。既存のデータソーステーブルでこれらの改善のメリットを享受するために、既存テーブルが古いパーティション管理戦略から新たなアプローチを使用するように変更するために`MSCK`コマンドを使用することができます。

```sql:SQL
MSCK REPAIR TABLE table_name;
```

既存ファイル対して新規テーブルを作成する際にも、`MSCK REPAIR TABLE`を実行する必要があります。

背後のファイルに対する直接の書き込みは、カタログもアップデートされるまではテーブルには反映されないため、これは後方互換性を破壊する可能性があることに注意してください。この同期処理はSpark 2.1によって自動で行われますが、古いバージョンのSpark、外部システム、SparkのテーブルAPI以外による書き込みでは、再度呼び出しを行う前に`MSCK REPAIR TABLE`を実行する必要があります。

カタログのパーティション管理がテーブルに対して有効化されているかどうかをどう確認できるのでしょうか？`DESCRIBE FORMATTED table_name`コマンドを実行し、出力の`PartitionProvider: Catalog`をチェックします。

```scala:Scala
scala> sql("describe formatted test_table")
.filter("col_name like '%Partition Provider%'").show
+-------------------+---------+-------+
|           col_name|data_type|comment|
+-------------------+---------+-------+
|Partition Provider:|  Catalog|       |
+-------------------+---------+-------+
```

# まとめ

この記事で説明された全ての成果物は、Apache Spark 2.1リリースに含まれています。主要な項目をカバーするJIRAチケットは[SPARK\-17861](https://issues.apache.org/jira/browse/SPARK-17861)となります。

我々はこれらの変更に興奮しており、更なる性能改善を進めていけることを楽しみにしています。Databricks Community Editionでフリーの[アカウントにサインアップ](https://databricks.com/jp/try-databricks)し、Spark SQLを使っていくつかのクエリーをトライしてみてください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

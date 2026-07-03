---
title: Delta Lakeにおけるテーブルユーティリティコマンド
tags:
  - Databricks
  - deltalake
private: false
updated_at: '2021-12-07T14:24:12+09:00'
id: 152a31dc44bda51eeecd
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Table utility commands \| Databricks on AWS](https://docs.databricks.com/delta/delta-utility.html) [2021/11/3時点]の翻訳です。

> **注意**
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。

Deltaテーブルでは多くのユーティリティコマンドをサポートしています。

# Deltaテーブルで使用しないファイルを削除する

`vacuum`コマンドをテーブルに実行することで、保持期間より古いファイル、あるいは、Deltaテーブルで参照されないファイルを削除することができます。`vacuum`は自動では実行されません。デフォルトのファイルの保持期間は7日間です。この振る舞いを変更するためには、[データ保持](https://docs.databricks.com/delta/delta-batch.html#data-retention)を参照ください。

> **重要！**

> - `vacuum`はデータファイルのみを削除し、ログファイルは削除しません。ログファイルは、チェックポイントのオペレーション後に自動かつ非同期で削除されます。ログファイルのデフォルトの保持期間は30日間であり、SQLメソッド`ALTER TABLE SET TBLPROPERTIES`で設定できる`delta.logRetentionDuration`で設定可能です。[テーブルプロパティ](https://docs.databricks.com/delta/delta-batch.html#table-properties)を参照ください。
> - `vacuum`を実行することで、保持期間より古いバージョンに[タイムトラベル](https://docs.databricks.com/delta/delta-batch.html#deltatimetravel)することはできなくなります。

> **注意**
Deltaキャッシュが有効化された際、クラスターに`vacuum`で削除されたParquetファイルのデータが含まれる場合があります。このため、ファイルが削除された以前のテーブルバージョンのデータをクエリーする可能性があります。クラスターを再起動することでキャッシュデータが削除されます。[Deltaキャッシュの設定](https://docs.databricks.com/delta/optimizations/delta-cache.html#configure-the-delta-cache)を参照ください。

```sql:SQL
VACUUM eventsTable   -- vacuum files not required by versions older than the default retention period

VACUUM '/data/events' -- vacuum files in path-based table

VACUUM delta.`/data/events/`

VACUUM delta.`/data/events/` RETAIN 100 HOURS  -- vacuum files not required by versions more than 100 hours old

VACUUM eventsTable DRY RUN    -- do dry run to get the list of files to be deleted
```

Spark SQL文法の詳細に関しては、以下を参照ください。

- Databricksランタイム 7.x以降: [VACUUM](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-vacuum.html)
- Databricksランタイム 5.5 LTSおよび6.x: [Vacuum](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/vacuum.html)

> **注意**
このPython APIはDatabricksランタイム 6.1以降で利用できます。

```py:Python
from delta.tables import *

deltaTable = DeltaTable.forPath(spark, pathToTable)  # path-based tables, or
deltaTable = DeltaTable.forName(spark, tableName)    # Hive metastore-based tables

deltaTable.vacuum()        # vacuum files not required by versions older than the default retention period

deltaTable.vacuum(100)     # vacuum files not required by versions more than 100 hours old
```

Scala、Java、Pythonの文法の詳細に関しては、[Delta Lake API reference](https://docs.databricks.com/delta/delta-apidoc.html)を参照ください。

> **注意**
このScala APIはDatabricksランタイム 6.0以降で利用できます。

```scala:Scala
import io.delta.tables._

val deltaTable = DeltaTable.forPath(spark, pathToTable)

deltaTable.vacuum()        // vacuum files not required by versions older than the default retention period

deltaTable.vacuum(100)     // vacuum files not required by versions more than 100 hours old
```

> **注意**
このJava APIはDatabricksランタイム 6.0以降で利用できます。

```java:Java
import io.delta.tables.*;
import org.apache.spark.sql.functions;

DeltaTable deltaTable = DeltaTable.forPath(spark, pathToTable);

deltaTable.vacuum();        // vacuum files not required by versions older than the default retention period

deltaTable.vacuum(100);     // vacuum files not required by versions more than 100 hours old
```

> **警告！**
古いスナップショットやコミットされていないファイルが、テーブルに対する同時処理のリーダーやライターによって利用されている可能性があるため、保持期間を少なくとも7日間に設定することをお勧めします。`VACUUM`がアクティブなファイルを削除すると、同時実行リーダーの処理が失敗する場合があり、さらに悪いケースでは、`VACUUM`がコミットされていないファイルを削除するとテーブルが破損する場合があります。保持期間には、実行する最長の同時トランザクションよりも長い期間、最新テーブルに対してあらゆるストリームが遅延を許容できる最長期間を選択すべきです。

Delta Lakeは危険な`VACUUM`コマンドの実行を防ぐための安全チェック機能を備えています。指定しようとしている保持期間よりも長い時間を要するオペレーションが存在しないということを確認したのであれば、Spark設定プロパティ`spark.databricks.delta.retentionDurationCheck.enabled`を`false`に設定して、安全チェックをオフにしてください。

## 監査情報

`VACUUM`はDeltaトランザクションログに監査情報をコミットします。`DESCRIBE HISTORY`を用いて監査イベントをクエリーすることができます。

監査情報を記録するためには、`spark.databricks.delta.vacuum.logging.enabled`を有効化します。マルチワークスペースの書き込みに関して、S3では一貫性の保証が限定されるため、監査ログはデフォルトでは有効化されていません。S3で本機能を有効化する際には、ワークフローにマルチワークスペースの書き込みが含まれないことを確認してください。書き込みが失敗すると、データが失われる場合があります。

# Deltaテーブル履歴を取得する

`history`コマンドを実行することで、Deltaテーブルに対する書き込みのオペレーション、ユーザー、タイムスタンプなどの情報を取得することができます。オペレーションは日付の降順で返却されます。デフォルトでは、テーブル履歴は30日間保持されます。

```sql:SQL
DESCRIBE HISTORY '/data/events/'          -- get the full history of the table

DESCRIBE HISTORY delta.`/data/events/`

DESCRIBE HISTORY '/data/events/' LIMIT 1  -- get the last operation only

DESCRIBE HISTORY eventsTable
```

Spark SQL文法の詳細に関しては、以下を参照ください。

- Databricksランタイム 7.x以降: [DESCRIBE HISTORY \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-describe-history.html)
- Databricksランタイム 5.5 LTSおよび6.x: [Describe History \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/describe-history.html)

> **注意**
このPython APIはDatabricksランタイム 6.1以降で利用できます。

```py:Python
from delta.tables import *

deltaTable = DeltaTable.forPath(spark, pathToTable)

fullHistoryDF = deltaTable.history()    # get the full history of the table

lastOperationDF = deltaTable.history(1) # get the last operation
```

Scala、Java、Pythonの文法の詳細に関しては、[Delta Lake API reference](https://docs.databricks.com/delta/delta-apidoc.html)を参照ください。

> **注意**
このScala APIはDatabricksランタイム 6.0以降で利用できます。

```scala:Scala
import io.delta.tables._

val deltaTable = DeltaTable.forPath(spark, pathToTable)

val fullHistoryDF = deltaTable.history()    // get the full history of the table

val lastOperationDF = deltaTable.history(1) // get the last operation
```

> **注意**
このJava APIはDatabricksランタイム 6.0以降で利用できます。

```java:Java
import io.delta.tables.*;

DeltaTable deltaTable = DeltaTable.forPath(spark, pathToTable);

DataFrame fullHistoryDF = deltaTable.history();       // get the full history of the table

DataFrame lastOperationDF = deltaTable.history(1);    // fetch the last operation on the DeltaTable
```

## 履歴のスキーマ

`history`オペレーションのアウトプットには以下のカラムが含まれます。

| カラム | 型 | 説明 |
|:--|:--|:--|
| version  | long  | オペレーションによって生成されたテーブルバージョン  |
| timestamp  | timestamp  | バージョンがコミットされたタイムスタンプ  |
| userId  |  string | オペレーションを実行したユーザーのID  |
| userName  | string  | オペレーションを実行したユーザー名  |
| operation  | string  | オペレーション名  |
| operationParameters  | map  | オペレーションのパラメーター(例：述語)  |
| job  |  struct | オペレーションを実行したジョブの詳細  |
| notebook  | struct  |オペレーションを実行したノートブックの詳細   |
| clusterId  | string  | オペレーションを実行したクラスターのID  |
| readVersion  |  long | 描き込みオペレーションを実行するために読み込まれたテーブルのバージョン  |
| isolationLevel  |  string | オペレーションで用いられた分離レベル  |
| isBlindAppend  | boolean   | オペレーションでデータが追加されたかどうか  |
| operationMetrics  | map  | オペレーションのメトリクス(例：変更された行数、ファイル数)  |
| userMetadata  | string  | 指定された場合にはユーザー定義のコミットメタデータ  |

```
+-------+-------------------+------+--------+---------+--------------------+----+--------+---------+-----------+-----------------+-------------+--------------------+
|version|          timestamp|userId|userName|operation| operationParameters| job|notebook|clusterId|readVersion|   isolationLevel|isBlindAppend|    operationMetrics|
+-------+-------------------+------+--------+---------+--------------------+----+--------+---------+-----------+-----------------+-------------+--------------------+
|      5|2019-07-29 14:07:47|   ###|     ###|   DELETE|[predicate -> ["(...|null|     ###|      ###|          4|WriteSerializable|        false|[numTotalRows -> ...|
|      4|2019-07-29 14:07:41|   ###|     ###|   UPDATE|[predicate -> (id...|null|     ###|      ###|          3|WriteSerializable|        false|[numTotalRows -> ...|
|      3|2019-07-29 14:07:29|   ###|     ###|   DELETE|[predicate -> ["(...|null|     ###|      ###|          2|WriteSerializable|        false|[numTotalRows -> ...|
|      2|2019-07-29 14:06:56|   ###|     ###|   UPDATE|[predicate -> (id...|null|     ###|      ###|          1|WriteSerializable|        false|[numTotalRows -> ...|
|      1|2019-07-29 14:04:31|   ###|     ###|   DELETE|[predicate -> ["(...|null|     ###|      ###|          0|WriteSerializable|        false|[numTotalRows -> ...|
|      0|2019-07-29 14:01:40|   ###|     ###|    WRITE|[mode -> ErrorIfE...|null|     ###|      ###|       null|WriteSerializable|         true|[numFiles -> 2, n...|
+-------+-------------------+------+--------+---------+--------------------+----+--------+---------+-----------+-----------------+-------------+--------------------+
```

> **注意**

> - オペレーションメトリクスは、historyコマンドとオペレーションがDatabricksランタイム 6.5以降で実行された場合に利用できます。
> - 以下の方法でDeltaテーブルに書き込みを行った際には、いくつかのカラムは表示されません。
>     - [JDBCあるいはODBC](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html)
>     - [JARジョブ](https://docs.databricks.com/dev-tools/api/latest/examples.html#spark-jar-job)
>     - [spark-submitのジョブ](https://docs.databricks.com/dev-tools/api/latest/examples.html#spark-submit-api-example)
>     - [REST APIによるコマンド実行](https://docs.databricks.com/dev-tools/api/1.2/index.html#command-execution)
> - 今後追加されるカラムは常に最後のカラムの後に追加されます。

## オペレーションメトリクスのキー

`history`オペレーションによって、`operationMetrics`カラムにオペレーションメトリクスのコレクションが返却されます。

以下にオペレーションごとのマップキー定義の一覧を示します。

| オペレーション | メトリクス名 | 説明 |
|:--|:--|:--|
|WRITE, CREATE TABLE AS SELECT, REPLACE TABLE AS SELECT, COPY INTO   |   |   |
|   | numFiles  | 書き込まれたファイル数  |
|   |  numOutputBytes | 書き込まれたコンテンツのバイト数  |
|   |  numOutputRows | 書き込まれた行数  |
| STREAMING UPDATE  |   |   |
|   | numAddedFiles  | 追加されたファイル数  |
|   | numRemovedFiles  | 削除されたファイル数  |
|   | numOutputRows  | 書き込まれた行数  |
|   | numOutputBytes  | 書き込まれたバイト数  |
| DELETE  |   |   |
|   | numAddedFiles  | 追加されたファイル数。テーブルのパーティションが削除された際には出力されません。  |
|   | numRemovedFiles  | 削除されたファイル数  |
|   | numDeletedRows  | 削除された行数。テーブルのパーティションが削除された際には出力されません。  |
|   | numCopiedRows  | ファイル削除プロセスでコピーされた行数  |
|   | executionTimeMs  | オペレーション全体の実行時間  |
|   | scanTimeMs  | マッチングのためにファイルをスキャンした時間  |
|   | rewriteTimeMs  | マッチしたファイルの再書き込みに要した時間  |
| TRUNCATE   |   |   |
|   | numRemovedFiles  |削除されたファイル数   |
|   |  executionTimeMs |オペレーション全体の実行時間   |
| MERGE  |   |   |
|   | numSourceRows  | ソースデータフレームの行数  |
|   | numTargetRowsInserted  | ターゲットテーブルにインサートされた行数  |
|   | numTargetRowsUpdated  | ターゲットテーブルでアップデートされた行数  |
|   | numTargetRowsDeleted  | ターゲットテーブルで削除された行数  |
|   | numTargetRowsCopied  | コピーされたターゲット行数  |
|   | numOutputRows  | 書き込まれた行の総数  |
|   | numTargetFilesAdded  | シンク(ターゲット)に追加されたファイル数  |
|   | numTargetFilesRemoved  |シンク(ターゲット)から削除されたファイル数   |
|   |  executionTimeMs | オペレーション全体の実行時間  |
|   | scanTimeMs  | マッチングのためにファイルをスキャンした時間  |
|   | rewriteTimeMs  | マッチしたファイルの再書き込みに要した時間  |
| UPDATE  |   |   |
|   | numAddedFiles  | 追加されたファイル数  |
|   | numRemovedFiles  | 削除されたファイル数  |
|   | numUpdatedRows  |  更新された行数 |
|   | numCopiedRows  | ファイル更新プロセスでコピーされた行数  |
|   | executionTimeMs  | オペレーション全体の実行時間  |
|   | scanTimeMs  | マッチングのためにファイルをスキャンした時間  |
|   | rewriteTimeMs  | マッチしたファイルの再書き込みに要した時間  |
| FSCK  | numRemovedFiles  | 削除されたファイル数  |
| CONVERT  |  numConvertedFiles | 変換されたParquetファイル数  |


| オペレーション | メトリクス名 | 説明 |
|:--|:--|:--|
| CLONE (1)  |   |   |
|   | sourceTableSize  | クローンされたバージョンのソーステーブルのバイト数  |
|   | sourceNumOfFiles  | クローンされたソーステーブルのファイル数  |
|   | numRemovedFiles  | 既存Deltaテーブルが置換された際のターゲットテーブルから削除されたファイル数  |
|   | removedFilesSize  | 既存Deltaテーブルが置換された際のターゲットテーブルから削除されたファイルのバイト数  |
|   | numCopiedFiles  | 新たな場所にコピーされたファイル数。シャロークローンの場合は0  |
|   | copiedFilesSize  | 新たな場所にコピーされたファイルのサイズ。シャロークローンの場合は0  |
| RESTORE (2)  |   |   |
|   | tableSizeAfterRestore  | レストア後のテーブルのバイトサイズ  |
|   | numOfFilesAfterRestore  | レストア後のテーブルのファイル数  |
|   | numRemovedFiles  | レストアオペレーションで削除されたファイル数  |
|   | numRestoredFiles  | レストアによって追加されたファイル数  |
|   | removedFilesSize  | レストアによって削除されたファイルのバイトサイズ  |
|   | restoredFilesSize  | レストアによって追加されたファイルのバイトサイズ  |
| OPTIMIZE  |   |   |
|   | numAddedFiles  | 追加されたファイル数  |
|   | numRemovedFiles  | 削除されたファイル数  |
|   | numAddedBytes  | テーブルの最適化後に追加されたバイト数  |
|   | numRemovedBytes  | 削除されたバイト数  |
|   | minFileSize  | テーブル最適化後の最小ファイルサイズ  |
|   | p25FileSize  | テーブル最適化後の25パーセンタイルのファイルサイズ  |
|   | p50FileSize  | テーブル最適化後のファイルサイズの中央値  |
|   | p75FileSize  | テーブル最適化後の75パーセンタイルのファイルサイズ  |
|   | maxFileSize  | テーブル最適化後の最大ファイルサイズ  |
| VACUUM (3) |   |   |
|   | numDeletedFiles  | 削除されたファイルの数  |
|   | numVacuumedDirectories  | vacuumされたディレクトリ数  |
|   | numFilesToDelete  | 削除するファイルの数  |

(1) Databricks ランタイム 7.3 LTS以降が必要
(2) Databricks ランタイム 7.4以降が必要
(3) Databricks ランタイム 8.2以降が必要

# Deltaテーブル詳細を取得する

`DESCRIBE DETAIL`を用いてDeltaテーブルの詳細情報(例：ファイル数、データサイズ)を取得することができます。

```sql:SQL
DESCRIBE DETAIL '/data/events/'

DESCRIBE DETAIL eventsTable
```

Spark SQL文法の詳細に関しては、以下を参照ください。

- Databricksランタイム 7.x以降: [DESCRIBE DETAIL](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-aux-describe-table.html#describe-detail)
- Databricksランタイム 5.5 LTSおよび6.x: [Describe Detail \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/describe-table.html#describe-detail)

## Detailのスキーマ

このオペレーションによって、以下のスキーマを持つ1行のみが返却されます。

| カラム | 型 | 説明 |
|:--|:--|:--|
| format | string  | テーブルのフォーマット、ここでは`delta`となります。  |
| id | string  | テーブルのユニークなID  |
| name |  string | メタストアで定義されているテーブル名  |
| description | string  |  テーブルの説明 |
| location | string  |  デーブルの位置 |
| createdAt | timestamp  |  テーブル作成日時 |
| lastModified |  timestamp | テーブル更新日時  |
| partitionColumns | array of strings  | テーブルのパーティションが存在する場合には、パーティションカラム  |
| numFiles |  long | 最新バージョンのテーブルのファイル数  |
| sizeInBytes | int  | 最新バージョンのテーブルのバイトサイズ  |
| properties |  string-string map | テーブルの全プロパティセット  |
| minReaderVersion | int  |  テーブルを読み取ることができるリーダーの最小バージョン(ログプロトコルに準拠) |
| minWriterVersion | int  |  テーブルに書き込むことができるライターの最小バージョン(ログプロトコルに準拠) |

```
+------+--------------------+------------------+-----------+--------------------+--------------------+-------------------+----------------+--------+-----------+----------+----------------+----------------+
|format|                  id|              name|description|            location|           createdAt|       lastModified|partitionColumns|numFiles|sizeInBytes|properties|minReaderVersion|minWriterVersion|
+------+--------------------+------------------+-----------+--------------------+--------------------+-------------------+----------------+--------+-----------+----------+----------------+----------------+
| delta|d31f82d2-a69f-42e...|default.deltatable|       null|file:/Users/tuor/...|2020-06-05 12:20:...|2020-06-05 12:20:20|              []|      10|      12345|        []|               1|               2|
+------+--------------------+------------------+-----------+--------------------+--------------------+-------------------+----------------+--------+-----------+----------+----------------+----------------+
```

# マニフェストファイルを作成する

(Apache Spark以外の)他の処理エンジンがDeltaテーブルを読み取れるように、Deltaテーブルに対するマニフェストファイルを作成することができます。例えば、PrestoやAthenaがDeltaテーブルを読み取れるようにマニフェストファイルを作成するには、以下を実行します。

```sql:SQL
GENERATE symlink_format_manifest FOR TABLE delta.`/mnt/events`

GENERATE symlink_format_manifest FOR TABLE eventsTable
```

> **注意**
このPython APIはDatabricksランタイム 6.3以降で利用できます。

```py:Python
deltaTable = DeltaTable.forPath(<path-to-delta-table>)
deltaTable.generate("symlink_format_manifest")
```

> **注意**
このScala APIはDatabricksランタイム 6.3以降で利用できます。

```scala:Scala
val deltaTable = DeltaTable.forPath(<path-to-delta-table>)
deltaTable.generate("symlink_format_manifest")
```

> **注意**
このJava APIはDatabricksランタイム 6.3以降で利用できます。

```java:Java
DeltaTable deltaTable = DeltaTable.forPath(<path-to-delta-table>);
deltaTable.generate("symlink_format_manifest");
```

# ParquetテーブルをDeltaテーブルに変換する

Parquetテーブルをその場でDeltaテーブルに変換します。このコマンドはディレクトリ内の全てのファイルの一覧を作成し、これらのファイルを追跡するDelta Lakeトランザクションログを生成し、Parquertファイルのフッターを読み込むことでデータのスキーマを推定します。データのパーティションが作成されている場合には、DDLフォーマットの文字列(`<column-name1> <type>, <column-name2> <type>, ...`)として、パーティションカラムを指定する必要があります。

> **注意**
Parquetテーブルが構造化ストリーミングで作成された場合、SQL設定`spark.databricks.delta.convert.useMetadataLog`が`true`に設定されたテーブルに含まれるファイルの信頼できる情報源としてサブディレクトリ`_spark_metadata`を用いることで、ファイルの一覧作成を回避することができます。

```sql:SQL
-- Convert unpartitioned Parquet table at path '<path-to-table>'
CONVERT TO DELTA parquet.`<path-to-table>`

-- Convert partitioned Parquet table at path '<path-to-table>' and partitioned by integer columns named 'part' and 'part2'
CONVERT TO DELTA parquet.`<path-to-table>` PARTITIONED BY (part int, part2 int)
```

文法の詳細に関しては、以下を参照ください。

- Databricksランタイム 7.x以降: [CONVERT TO DELTA \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-convert-to-delta.html)
- Databricksランタイム 5.5 LTSおよび6.x: [Convert To Delta \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/convert-to-delta.html)

> **注意**
このPython APIはDatabricksランタイム 6.1以降で利用できます。

```py:Python
from delta.tables import *

# Convert unpartitioned Parquet table at path '<path-to-table>'
deltaTable = DeltaTable.convertToDelta(spark, "parquet.`<path-to-table>`")

# Convert partitioned parquet table at path '<path-to-table>' and partitioned by integer column named 'part'
partitionedDeltaTable = DeltaTable.convertToDelta(spark, "parquet.`<path-to-table>`", "part int")
```

> **注意**
このScala APIはDatabricksランタイム 6.0以降で利用できます。

```scala:Scala
import io.delta.tables._

// Convert unpartitioned Parquet table at path '<path-to-table>'
val deltaTable = DeltaTable.convertToDelta(spark, "parquet.`<path-to-table>`")

// Convert partitioned Parquet table at path '<path-to-table>' and partitioned by integer columns named 'part' and 'part2'
val partitionedDeltaTable = DeltaTable.convertToDelta(spark, "parquet.`<path-to-table>`", "part int, part2 int")
```

> **注意**
このJava APIはDatabricksランタイム 6.0以降で利用できます。

```java:Java
import io.delta.tables.*;

// Convert unpartitioned Parquet table at path '<path-to-table>'
DeltaTable deltaTable = DeltaTable.convertToDelta(spark, "parquet.`<path-to-table>`");

// Convert partitioned Parquet table at path '<path-to-table>' and partitioned by integer columns named 'part' and 'part2'
DeltaTable deltaTable = DeltaTable.convertToDelta(spark, "parquet.`<path-to-table>`", "part int, part2 int");
```

> **注意**
Delta Lakeで追跡されないあらゆるファイルは不可視となり、`vacuum`を実行することで削除することができます。変換プロセス中のデータファイルの追加、更新は避けてください。テーブルの変換が完了したら、Delta Lake経由で全ての書き込みが行われるようにしてください。

# DeltaテーブルをParquetテーブルに変換する

以下のステップを踏むことで、簡単にDeltaテーブルをParquetテーブルに変換することができます。

1. データファイルを変更するDelta Lakeのオペレーション(`delete`や`merge`など)を実行したのであれば、最新テーブルバージョンに属さない全てのデータファイルを削除するために、保持期間0時間で[vacuum](https://docs.databricks.com/delta/delta-utility.html#delta-vacuum)を実行します。
1. テーブルのディレクトリにある`_delta_log`ディレクトリを削除します。

# Deltaテーブルを前の状態に復旧する

> **注意**
Databricksランタイム 7.4以降で利用できます。

`RESTORE`コマンドを用いることでDeltaテーブルを以前の状態に復旧することができます。Deltaテーブルでは、以前の状態に復旧できるように、内部的にテーブルのバージョン履歴を保持しています。`RESTORE`コマンドでは、オプションとして以前の状態に対応するバージョン、以前の状態を示すタイムスタンプを指定することができます。

> **重要！**

> - レストア済みのテーブル、[クローン](#deltaテーブルをクローンする)されたテーブルをレストアすることができます。
> - 手動あるいは`vacuum`でデータファイルが削除された以前のバージョンへの復旧は失敗します。`spark.sql.files.ignoreMissingFiles`を`true`に設定することで、部分的なバージョン復旧が可能です。
> - 以前の状態に復旧する際のタイムスタンプのフォーマットは`yyyy-MM-dd HH:mm:ss`です。日付のみの指定(`yyyy-MM-dd`)もサポートされています。

文法の詳細については、[RESTORE \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-restore.html)を参照ください。

## Restoreのメトリクス

> **注意**
Databricksランタイム8.2以降で使用できます。

`RESTORE`は、オペレーションを完了すると1行のデータフレームとして以下のメトリクスをレポートします。

- `table_size_after_restore`: レストア後のテーブルサイズ
- `num_of_files_after_restore`: レストア後のテーブルのファイル数
- `num_removed_files`: テーブルから削除(論理的削除)されたファイルの数
- `num_restored_files`: ロールバックによって復旧されたファイルの数
- `removed_files_size`: テーブルから削除されたファイルの合計バイト数
- `restored_files_size`: 復旧されたファイルの合計バイト数

![](https://docs.databricks.com/_images/restore-metrics.png)

## テーブルアクセスコントロール

テーブルをレストアするには`MODIFY`権限が必要となります。

# Deltaテーブルをクローンする

> **注意**
Databricksランタイム7.2以降で使用できます。

`clone`コマンドを用いることで、特定バージョンの既存のDeltaテーブルのコピーを作成することができます。

## クローンのタイプ

- *ディープな(深い)クローン*は、既存テーブルのメタデータに加え、ソースのテーブルデータをクローンのターゲットにコピーするクローンです。さらに、Deltaのソーステーブルに書き込みを行っているストリームを停止し、クローンのターゲットテーブルから再開できるように、ストリームのメタデータもクローンされます。
- *シャローな(浅い)クローン*は、データファイルをクローンターゲットにコピーしません。テーブルのメタデータはソースと等価のものとなります。これらのクローンの方が作成コストは低くなります。

ディープ、シャロー両方のクローンに対するあらゆる変更は、クローン自身にのみ影響し、ソーステーブルには影響しません。

クローンされるメタデータには、スキーマ、パーティション情報、普遍条件(invariant)、ヌル値許可が含まれます。ディープクローンに関しては、ストリームと[COPY INTO \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-copy-into.html)のメタデータもクローンされます。クローンされないメタデータはテーブルの説明文と、[ユーザー定義のコミットメタデータ](https://docs.databricks.com/delta/delta-batch.html#set-user-defined-commit-metadata)となります。

> **重要！**

> - シャロークローンはソースディレクトリのデータファイルへの参照をクローンします。ソーステーブルで`vacuum`を実行すると、クライアントは参照しているデータファイルを読み込むことができなくなり、`FileNotFoundException`がスローされます。この場合、シャロークローンに対してクローン、置換を行うことでクローンを復旧することができます。これが頻発する際には、ソーステーブルに依存しないディープクローンの利用を検討してください。
- ディープクローンはクローン元のソースに依存しませんが、ディープクローンはデータ、メタデータをコピーするのでコストが高くなります。
- 指定されたパスにテーブルを持つターゲットに対する`replace`を伴うクローンは、パスにDeltaログが存在しない場合にはDeltaログを作成します。`vacuum`を実行することで既存データをクリーンアップすることができます。既存テーブルがDeltaテーブルの場合には、既存のDeltaテーブルに対して、新規メタデータ、ソーステーブルからの新規データを含む新たなコミットが作成されます。
- テーブルのクローンは`Create Table As Select`や`CTAS`とは異なります。クローンは、データに加えてソーステーブルのメタデータをコピーします。クローンはよりシンプルな文法となっています。パーティション、フォーマット、不変条件、ヌル値許可などはソーステーブルから取得されるのでこれらを指定する必要はありません。
- クローンされたテーブルはソーステーブルとは独立した履歴を持ちます。クロンされたテーブルに対するタイムトラベルのクエリーは、ソーステーブルに対する同じ入力とは異なる挙動をします。

```sql:SQL
 CREATE TABLE delta.`/data/target/` CLONE delta.`/data/source/` -- Create a deep clone of /data/source at /data/target

 CREATE OR REPLACE TABLE db.target_table CLONE db.source_table -- Replace the target

 CREATE TABLE IF NOT EXISTS TABLE delta.`/data/target/` CLONE db.source_table -- No-op if the target table exists

 CREATE TABLE db.target_table SHALLOW CLONE delta.`/data/source`

 CREATE TABLE db.target_table SHALLOW CLONE delta.`/data/source` VERSION AS OF version

 CREATE TABLE db.target_table SHALLOW CLONE delta.`/data/source` TIMESTAMP AS OF timestamp_expression -- timestamp can be like “2019-01-01” or like date_sub(current_date(), 1)
```

```py:Python
 from delta.tables import *

 deltaTable = DeltaTable.forPath(spark, pathToTable)  # path-based tables, or
 deltaTable = DeltaTable.forName(spark, tableName)    # Hive metastore-based tables

 deltaTable.clone(target, isShallow, replace) # clone the source at latest version

 deltaTable.cloneAtVersion(version, target, isShallow, replace) # clone the source at a specific version

# clone the source at a specific timestamp such as timestamp=“2019-01-01”
 deltaTable.cloneAtTimestamp(timestamp, target, isShallow, replace)
```

```scala:Scala
 import io.delta.tables._

 val deltaTable = DeltaTable.forPath(spark, pathToTable)
 val deltaTable = DeltaTable.forName(spark, tableName)

 deltaTable.clone(target, isShallow, replace) // clone the source at latest version

 deltaTable.cloneAtVersion(version, target, isShallow, replace) // clone the source at a specific version

 deltaTable.cloneAtTimestamp(timestamp, target, isShallow, replace) // clone the source at a specific timestamp
```

```java:Java
 import io.delta.tables.*;

 DeltaTable deltaTable = DeltaTable.forPath(spark, pathToTable);
 DeltaTable deltaTable = DeltaTable.forName(spark, tableName);

 deltaTable.clone(target, isShallow, replace) // clone the source at latest version

 deltaTable.cloneAtVersion(version, target, isShallow, replace) // clone the source at a specific version

 deltaTable.cloneAtTimestamp(timestamp, target, isShallow, replace) // clone the source at a specific timestamp
```

文法の詳細については[CLONE \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-clone.html)を参照ください。

## クローンのメトリクス

> **注意**
Databricksランタイム 8.2以降で利用できます。

`CLONE`はオペレーションが完了すると、1行のデータフレームとして以下のメトリクスを返却します。

- `source_table_size`: クローンされたソーステーブルのバイトサイズ
- `source_num_of_files`: ソーステーブルのファイル数
- `num_removed_files`: テーブルが置換された場合、現在のテーブルから削除されたファイルの数
- `num_copied_files`: ソースからコピーされたファイル数。(シャロークローンの場合は0)
- `removed_files_size`: 現在のテーブルから削除されたファイルのバイトサイズ
- `copied_files_size`: テーブルにコピーされたファイルのバイトサイズ

![](https://docs.databricks.com/_images/clone-metrics.png)

## アクセス権

Databricksのテーブルアクセスコントロールとクラウドプロバイダーのアクセス権を設定する必要があります。

### テーブルアクセスコントロール

ディープ、シャロークローンの両方で以下のアクセス権が必要となります。

- ソーステーブルに対する`SELECT`権限
- 新規テーブルを作成するために`CLONE`を使用している際には、テーブルを作成しようとしているデータベースに対する`CREATE`権限
- テーブルを置換するためにCLONEを使用している場合には、テーブルに対する`MODIFY`権限

### クラウドプロバイダーのアクセス権

ディープクローンを実行した際、ディープクローンを読み取るユーザーには、クローンのディレクトリに対する読み取り権限が必要となります。

シャロークローンを作成した際には、シャロークローンのデータファイルはソーステーブルのままなので、クローンのディレクトリに加え、オリジナルのテーブルのファイルに対する読み取り権限が必要となります。クローンに変更を加えるには、ユーザーはクローンのディレクトリに対する書き込み権限が必要となります。

## クローンのユースケース

### データのアーカイブ

ディザスターリカバリや、タイムトラベルで実現されるよりも長い期間データを保持する必要があるかもしれません。このような場合、アーカイブ目的で特定のタイミングのテーブルの状態を保存するためにディープクローンを作成することができます。ディザスターリカバリーの目的でソーステーブルの状態を継続的に更新し続けるために、インクリメンタルなアーカイブを行うことも可能です。

```sql:SQL
-- Every month run
CREATE OR REPLACE TABLE delta.`/some/archive/path` CLONE my_prod_table
```

### 機械学習フローにおける再現性確保

機械学習を行う際に、MLモデルをトレーニングする際に用いたテーブルの特定バージョンをアーカイブしたいと考えるかもしれません。未来のモデルはアーカイブされたデータセットを用いたテストを行うことができます。

```sql:SQL
-- Trained model on version 15 of Delta table
CREATE TABLE delta.`/model/dataset` CLONE entire_dataset VERSION AS OF 15
```

### プロダクションテーブルにおける短期的な実験

テーブルを破損することなしにプロダクションテーブルでワークフローをテストするために、簡単にシャロークローンを作成することができます。これによって、全てのプロダクションデータを含みながらも、プロダクションのワークロードに影響を与えないクローンテーブルに対して任意のワークフローを実行することができます。

```sql:SQL
-- Perform shallow clone
CREATE OR REPLACE TABLE my_test SHALLOW CLONE my_prod_table;

UPDATE my_test WHERE user_id is null SET invalid=true;
-- Run a bunch of validations. Once happy:

-- This should leverage the update information in the clone to prune to only
-- changed files in the clone if possible
MERGE INTO my_prod_table
USING my_test
ON my_test.user_id <=> my_prod_table.user_id
WHEN MATCHED AND my_test.user_id is null THEN UPDATE *;

DROP TABLE my_test;
```

### データ共有

同じ企業における他のビジネスユニットが、同じデータにアクセスしたいが最新のアップデートが不要なケースがあります。ソーステーブルに直接アクセス権を与えるのではなく、別のビジネスユニットにクローンに対する異なるアクセス権を提供することができます。クローンのパフォーマンスはシンプルなビューよりも優れたものとなります。

```sql:SQL
-- Perform deep clone
CREATE OR REPLACE TABLE shared_table CLONE my_prod_table;

-- Grant other users access to the shared table
GRANT SELECT ON shared_table TO `<user-name>@<user-domain>.com`;
```

### テーブルプロパティのオーバーライド

> **注意**
Databricksランタイム 7.5以降で利用できます。

テーブルプロパティのオーバーライドは以下のケースで有用です。

- 異なるビジネスユニットとデータを共有する際に、オーナーやユーザー情報を用いたアノテーション
- Deltaテーブルのアーカイブとタイムトラベルが必要となります。アーカイブテーブルとは独立したログ保持期間を指定することができます。例を以下に示します。

```sql:SQL
CREATE OR REPLACE TABLE archive.my_table CLONE prod.my_table
TBLPROPERTIES (
  delta.logRetentionDuration = '3650 days',
  delta.deletedFileRetentionDuration = '3650 days'
)
LOCATION 'xx://archive/my_table'
```

```py:Python
dt = DeltaTable.forName(spark, "prod.my_table")
tblProps = {
  "delta.logRetentionDuration": "3650 days",
  "delta.deletedFileRetentionDuration": "3650 days"
}
dt.clone('xx://archive/my_table', isShallow=False, replace=True, tblProps)
```

```scala:Scala
val dt = DeltaTable.forName(spark, "prod.my_table")
val tblProps = Map(
  "delta.logRetentionDuration" -> "3650 days",
  "delta.deletedFileRetentionDuration" -> "3650 days"
)
dt.clone("xx://archive/my_table", isShallow = false, replace = true, properties = tblProps)
```

# Sparkセッションにおける最後のコミットバージョンを検索する

> **注意**
Databricksランタイム 7.1以降で利用できます。

現在の`SparkSession`によって書き込まれた全テーブル、全スレッドにおける最新のコミットのバージョン数を取得するには、SQL設定`spark.databricks.delta.lastCommitVersionInSession`をクエリーします。

```sql:SQL
SET spark.databricks.delta.lastCommitVersionInSession
```

```py:Python
spark.conf.get("spark.databricks.delta.lastCommitVersionInSession")
```

```scala:Scala
spark.conf.get("spark.databricks.delta.lastCommitVersionInSession")
```

`SparkSession`でコミットが行われていない場合には、クエリーは空の値を返却します。

> **注意**
複数スレッドで`SparkSession`を共有している場合、複数スレッドで変数を共有しているのと同様なものになります。同時に設定値を更新すると、競合状態になる場合があります。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

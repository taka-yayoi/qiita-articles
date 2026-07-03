---
title: 構造化ストリーミング：2021年の振り返り
tags:
  - Spark
  - Databricks
private: false
updated_at: '2022-02-16T10:12:33+09:00'
id: 412dd33a3a0bebb56ecc
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[An Overview of All the New Structured Streaming Features Developed In 2021 For Databricks & Apache Spark\. \- The Databricks Blog](https://databricks.com/blog/2022/02/07/structured-streaming-a-year-in-review.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

2022年を迎え、ここで我々はDatabricksとApache Spark™におけるストリーミングでなされた偉大なる全身を振り返りたいと思います！2021年、エンジニアリングチームとオープンソースコントリビュータは3つのゴールを念頭に置いて様々な偉業を成し遂げました。

1. 低レーテンシー & ステートフル処理の改善
1. DatabricksとSpark構造化ストリーミングワークロードの観察可能性の改善
1. リソース配置とスケーラビリティの改善

究極的には、これらのゴールの背後にあるモチベーションは、チームがDatabricksとSparkでストリーミングワークロードを実行できるようにすることで、ミッションクリティカルなプロダクションレベルのストリーミングアプリケーションをDatabricksで実行し、同時にコスト効率とリソース使用量を最適化するというものでした。

# ゴール #1: 低レーテンシー & ステートフル処理の改善

ステートフルなオペレーションのレーテンシーを軽減し、ステートフルAPIを改善することを目的とした2つのキーとなる機能があります。1つ目は大規模なステートフルオペレーションに対する非同期チェックポイントであり、これまでは同期型でありレーテンシーが高かった設計を改善するものでした。

## 非同期チェックポイント

![](https://databricks.com/wp-content/uploads/2022/01/stream-ynr-blog-img-1.png)
この同期モデルにおいては、次のマイクロバッチが開始する前に状態のアップデートがクラウドストレージのチェックポイントに書き込まれます。これには、ステートフルなストリーミングクエリーが失敗した場合に、最後に成功したバッチの情報を用いて容易にクエリーを再開することができるという利点があります。非同期モデルにおいては、次のマイクロバッチは状態のアップデートが書き込まれるのを待つ必要がなく、全体的なマイクロバッチの実行におけるエンドツーエンドのレーテンシーを改善します。
![](https://databricks.com/wp-content/uploads/2022/01/stream-ynr-blog-img-2.png)
本機能にディープダイブするブログ記事が間も無く公開されます。また、Databricksランタイム10.3以降で本機能を試すことができます。

## 任意ステートフルオペレーターの改善

[以前の記事](https://databricks.com/blog/2017/10/17/arbitrary-stateful-processing-in-apache-sparks-structured-streaming.html)で我々は[flat]MapGroupsWithStateによる構造化ストリーミングにおける任意ステートフル処理を紹介しました。これらのオペレーターを用いることで、集計の枠を超えた複雑なステートフルオペレーションを可能にする柔軟性を手に入れることができます。こられのオペレーターに対して以下の改善をおこないました。

- 初期状態の許可、これによってお使いのストリーミングデータ全ての再処理を回避することができます。
- 新たにTestGroupStateインタフェースを提供することで、ロジックのテストが容易になり、ユーザーはGroupStateのインスタンスを作成することで設定された内部の値にアクセスでき、状態を変化させる関数のユニットテストがシンプルになります。

### 初期状態の許可

以下のflatMapGroupswithStateオペレーターから始めましょう。

```scala:Scala
def flatMapGroupsWithState[S: Encoder, U: Encoder](
    outputMode: OutputMode,
    timeoutConf: GroupStateTimeout,
    initialState: KeyValueGroupedDataset[K, S])(
    func: (K, Iterator[V], GroupState[S]) => Iterator[U])
```

このカスタムステート関数は、遭遇したフルーツの数を保持します。

```scala:Scala
val fruitCountFunc =(key: String, values: Iterator[String], state: GroupState[RunningCount]) => {
  val count = state.getOption.map(_.count).getOrElse(0L) + valList.size
  state.update(new RunningCount(count))
  Iterator((key, count.toString))
}
```

この例では、特定のフルーツの初期値を設定することで、このオペレーターに対して初期状態を指定しています。

```scala:Scala
val fruitCountInitialDS: Dataset[(String, RunningCount)] = Seq(
  ("apple", new RunningCount(1)),
  ("orange", new RunningCount(2)),
  ("mango", new RunningCount(5)),
).toDS()

val fruitCountInitial = initialState.groupByKey(x => x._1).mapValues(_._2)

fruitStream
  .groupByKey(x => x)
  .flatMapGroupsWithState(Update, GroupStateTimeout.NoTimeout, fruitCountInitial)(fruitCountFunc)
```

### ロジックテストを容易に

TestGroupState APIを用いることで状態アップデートをテストすることもできます。

```scala:Scala
import org.apache.spark.sql.streaming._
import org.apache.spark.api.java.Optional

test("flatMapGroupsWithState's state update function") {
  var prevState = TestGroupState.create[UserStatus](
    optionalState = Optional.empty[UserStatus],
    timeoutConf = GroupStateTimeout.EventTimeTimeout,
    batchProcessingTimeMs = 1L,
    eventTimeWatermarkMs = Optional.of(1L),
    hasTimedOut = false)

  val userId: String = ...
  val actions: Iterator[UserAction] = ...

  assert(!prevState.hasUpdated)

  updateState(userId, actions, prevState)

  assert(prevState.hasUpdated)
  
}
```

[Databricksのドキュメント](https://docs.databricks.com/spark/latest/structured-streaming/production.html)で他のサンプルを確認することもできます。

## セッションウィンドウのネイティブサポート

構造化ストリーミングでは、いずれも固定長のタンブリングウィンドウ、スライディングウィンドウを用いた[イベント時間ベースのウィンドウにおける集計](https://databricks.com/blog/2017/05/08/event-time-aggregation-watermarking-apache-sparks-structured-streaming.html)を行うための機能を導入しています。Spark 3.2では、動的なウィンドウ長を持つ[セッションウィンドウ](https://qiita.com/taka_yayoi/items/14d8df68f9fd731b9ca0)の概念を導入しました。これまでは、flatMapGroupsWithStateを用いたカスタムステートオペレーターが必要でした。

動的ギャップを用いた例を示します。

```py:Python
# Define the session window having dynamic gap duration based on eventType
session_window expr = session_window(events.timestamp, \
    when(events.eventType == "type1", "5 seconds") \
    .when(events.eventType == "type2", "20 seconds") \
    .otherwise("5 minutes"))

# Group the data by session window and userId, and compute the count of each group
windowedCountsDF = events \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(events.userID, session_window_expr) \
    .count()
```

# ゴール #2: ストリーミングワークロードの観察可能性の改善

[StreamingQueryListener](https://spark.apache.org/docs/3.2.0/api/scala/org/apache/spark/sql/streaming/StreamingQueryListener.html) APIを用いることで、SparkSession内におけるクエリーを非同期的に監視し、クエリーの状態、進捗、停止イベントに対するカスタムコールバック関数を定義することはできますが、マイクロバッチにおけるバックプレッシャーの理解、ボトルネックの特定は未だ困難なものとなっています。Databricksランタイム8.1時点では、StreamingQueryProgressオブジェクトは、[Kafka](https://docs.databricks.com/spark/latest/structured-streaming/kafka.html#metrics)、[Kinesis](https://docs.databricks.com/spark/latest/structured-streaming/kinesis.html#metrics)、[Delta Lake](https://docs.databricks.com/delta/delta-streaming.html#metrics)、[Auto Loader](https://docs.databricks.com/spark/latest/structured-streaming/auto-loader-s3.html#metrics)のデータソースのバックプレッシャーメトリクスをレポートします。

Kafkaから提供されるメトリクスの例を示します。

```
{
  "sources" : [ {
    "description" : "KafkaV2[Subscribe[topic]]",
    "metrics" : {
      "avgOffsetsBehindLatest" : "4.0",
      "maxOffsetsBehindLatest" : "4",
      "minOffsetsBehindLatest" : "4",
      "estimatedTotalBytesBehindLatest" : "80.0"
    },
  } ]
```

Databricksランタイム8.3では、[RocksDBステートストア](https://qiita.com/taka_yayoi/items/6a563259261f42d24b2f#rocksdb%E3%82%B9%E3%83%86%E3%83%BC%E3%83%88%E3%82%B9%E3%83%88%E3%82%A2%E3%81%AE%E3%83%A1%E3%83%88%E3%83%AA%E3%82%AF%E3%82%B9)のパフォーマンスの理解とステートオペレーションのパフォーマンスのデバッグを支援するリアルタイムメトリクスを導入しました。これは、非同期チェックポイントにおいて[ターゲットワークロードの特定](https://qiita.com/taka_yayoi/items/6a563259261f42d24b2f#%E3%82%BF%E3%83%BC%E3%82%B2%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%AD%E3%83%BC%E3%83%89%E3%81%AE%E7%89%B9%E5%AE%9A)にも役立ちます。

新たなステートストアメトリクスの例を示します。

```
{
  "id" : "6774075e-8869-454b-ad51-513be86cfd43",
  "runId" : "3d08104d-d1d4-4d1a-b21e-0b2e1fb871c5",
  "batchId" : 7,
  "stateOperators" : [ {
    "numRowsTotal" : 20000000,
    "numRowsUpdated" : 20000000,
    "memoryUsedBytes" : 31005397,
    "numRowsDroppedByWatermark" : 0,
    "customMetrics" : {
      "rocksdbBytesCopied" : 141037747,
      "rocksdbCommitCheckpointLatency" : 2,
      "rocksdbCommitCompactLatency" : 22061,
      "rocksdbCommitFileSyncLatencyMs" : 1710,
      "rocksdbCommitFlushLatency" : 19032,
      "rocksdbCommitPauseLatency" : 0,
      "rocksdbCommitWriteBatchLatency" : 56155,
      "rocksdbFilesCopied" : 2,
      "rocksdbFilesReused" : 0,
      "rocksdbGetCount" : 40000000,
      "rocksdbGetLatency" : 21834,
      "rocksdbPutCount" : 1,
      "rocksdbPutLatency" : 56155599000,
      "rocksdbReadBlockCacheHitCount" : 1988,
      "rocksdbReadBlockCacheMissCount" : 40341617,
      "rocksdbSstFileSize" : 141037747,
      "rocksdbTotalBytesReadByCompaction" : 336853375,
      "rocksdbTotalBytesReadByGet" : 680000000,
      "rocksdbTotalBytesReadThroughIterator" : 0,
      "rocksdbTotalBytesWrittenByCompaction" : 141037747,
      "rocksdbTotalBytesWrittenByPut" : 740000012,
      "rocksdbTotalCompactionLatencyMs" : 21949695000,
      "rocksdbWriterStallLatencyMs" : 0,
      "rocksdbZipFileBytesUncompressed" : 7038
    }
  } ],
  "sources" : [ {
  } ],
  "sink" : {
  }
}
```

# ゴール #3: リソース配置とスケーラビリティの改善

## Delta Live Tables(DLT)のストリーミングオートスケーリング

昨年のData + AI Summitにおいて、データパイプラインを宣言的に構築・オーケストレートし、クラスターやノードタイプを設定する必要性を大幅に抽象化できるフレームワークである[Delta Live Tables](https://qiita.com/taka_yayoi/items/4062930aa26f3cd14c9f)を発表しました。我々はこれをさらに推し進め、[既存のDatabricks最適化オートスケーリング](https://databricks.com/blog/2018/05/02/introducing-databricks-optimized-auto-scaling.html)を改善した、ストリーミングパイプラインに対するインテリジェントなソリューションを導入しました。これには以下のようなメリットがあります。

- **クラスター使用率の改善**: ストリーミングワークロードで負荷の変動があるシナリオにおいて、新たなバックプレッシャーメトリクスを活用してクラスターのサイズを調整し、クラスター使用率を改善します。
- **プロアクティブなワーカーのグレースフルシャットダウン**: 既存のオートスケーリングのソリューションはノードがアイドル状態の場合にのみリトライを行いますが、新たなDLTのオートスケーラーは使用率が低い場合、シャットダウンによってタスクが失敗しないことを保証しつつも、プロアクティブに選択されたノードをシャットダウンします。

本書の執筆時点では、本機能は[プライベートプレビュー](https://docs.databricks.com/release-notes/release-types.html#databricks-runtime-preview-releases)です。詳細はDatabricksアカウントチームにコンタクトしてください。

## Trigger.AvailableNow

構造化ストリーミングにおいて、トリガーを用いることでストリーミングクエリーのデータ処理のタイミングを定義することができます。これらのトリガータイプには、マイクロバッチ(デフォルト)、固定のマイクロバッチ間隔(Trigger.ProcessingTime(""))、一度のみマイクロバッチ(Trigger.Once)、連続(Trigger.Once)を指定することができます。

Databricksランタイム10.1では、新たなタイプのトリガーを導入しました。Trigger.AvailableNowはTrigger.Onceに似ていますが、より優れたスケーラビリティを提供します。Trigger Onceのように、クエリーが停止される前に利用可能な全てのデータを処理しますが、1つのバッチではなく複数バッチで処理を行います。これはDelta LakeとAuto Loaderのストリーミングソースでサポートされています。

サンプルを示します。

```py:Python
spark.readStream
  .format("delta")
  .option("maxFilesPerTrigger", "1")
  .load(inputDir)
  .writeStream
  .trigger(Trigger.AvailableNow)
  .option("checkpointLocation", checkpointDir)
  .start()
```

# サマリー

2022年に入っても我々は構造化ストリーミングにおけるイノベーションを加速していき、さらに性能を改善し、レーテンシーを削減し、新たな素晴らしい機能を提供していきます。今年も続報を楽しみにしてください！

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

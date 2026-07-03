---
title: Deltaキャッシングによる性能の最適化
tags:
  - Databricks
  - deltalake
private: false
updated_at: '2023-06-02T11:13:10+09:00'
id: 395fb7fabad655ceb37c
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Optimize performance with caching \| Databricks on AWS](https://docs.databricks.com/delta/optimizations/delta-cache.html) [2022/2/11時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Deltaキャッシュは高速な中間データフォーマットを用いて、ノードのローカルストレージにリモートファイルのコピーを作成することでデータの読み込みを高速化します。ファイルをリモートの場所から取り出す必要がある場合にはいつも、データは自動でキャッシュされます。同じデータに対する後続の読み込みはローカルで実行され、読み取りスピードを劇的に改善します。

Deltaキャッシュは全てのParquetファイルに対して動作し、[Delta Lakeフォーマット](https://qiita.com/taka_yayoi/items/e2fe8a341c3635f72544)に限定されるものではありません。Deltaキャッシュは、Amazon S3、DBFS、HDFS、Azure Blob storage、Azure Data Lake Storage Gen1、Azure Data Lake Storage Gen2に格納されているParquetファイルの読み込みをサポートしています。CSV、JSON、ORCのような他のストレージフォーマットは*サポートしていません*。

# DeltaとApache Sparkのキャッシング

Databricksでは2つのタイプのキャッシングがあります。DeltaキャッシングとSparkキャッシングです。それぞれのタイプの特性を以下に示します。

- **格納データのタイプ**: Deltaキャッシュはリモートデータのローカルコピーを格納します。これはさまざまなクエリーのパフォーマンスを改善しますが、任意のサブクエリーの結果を格納するのに使用することはできません。Sparkキャッシュは任意のサブクエリーデータの結果を格納でき、Parquet以外のフォーマット(CSV、JSON、ORCなど)でデータを格納することができます。
- **性能**: Deltaキャッシュに格納されたデータはSparkキャッシュに格納されたデータよりも高速に読み込み、操作することができます。これは、Deltaキャッシュは効率的な解凍アルゴリズムとwhole-stage code generationを用いたさらなる処理に最適なフォーマットでデータを出力するためです。
- **自動 vs 手動のコントロール**: Deltaキャッシュが有効化されるとリモートソースから取得されるべきデータは自動的にキャッシュに追加されます。このプロセスは、完全に透明化されており、いかなるアクションも不要です。しかし、事前にキャッシュにデータをロードするために`CACHE SELECT`コマンド([データのサブセットをキャッシュする](#データのサブセットをキャッシュする)をご覧ください)を使用することができます。Sparkキャッシュを使用する際には、キャッシュすべきテーブルやクエリーを手動で指定しなくてはなりません。
- **ディスクベース vs メモリーベース**: Deltaキャッシュはローカルディスクに格納されるので、Spark内の他のオペレーションからメモリーを奪うことはありません。モダンなSSDの高速な読み取り速度によって、Deltaキャッシュは性能にネガティブなインパクトを与えることなしに、完全にディスクに存在することになります。逆にSparkキャッシュはメモリーを使用します。

:::note info
**注意**
DeltaキャッシュとSparkキャッシュを同時に使用することができます。
:::

## サマリー

あなたのワークロードにおいてベストなツールを選択できるように、以下の表ではDeltaキャッシュとApache Sparkキャッシュの主要な違いをまとめています。

| 機能 | Deltaキャッシュ | Apache Sparkキャッシュ |
|:--|:--|:--|
|格納場所   | ワーカーノードのローカルファイル  | インメモリーのブロックだがストレージレベルに依存  |
|適用対象   | S3、WASB、その他ファイルシステム上のParquetテーブル  | 任意のデータフレーム、RDD  |
|トリガー   | (キャッシュが有効化されていれば)自動で最初の読み込み時点で  |手動、コードの変更が必要   |
|評価   | 遅延評価  | 遅延評価  |
|キャッシュの強制   | `CACHE SELECT`コマンド  | キャッシュをマテリアライズするための`.cache` + 任意のアクションと`.persist`  |
|可用性   | 設定フラグで有効化、無効化が可能。特定のノードタイプでは無効。  | 常に利用可能  |
|削除   | LRU方式で自動で削除、あるいはファイルの変更、手動によるクラスターの再起動  | LRU方式で自動で削除、`unpersist`による手動削除  |

# Deltaキャッシュの一貫性

Deltaキャッシュは、データファイルの作成、削除、内容の更新を自動で検知します。明示的にキャッシュされたデータを無効化することなしに、テーブルデータの書き込み、更新、削除が可能です。

Deltaキャッシュは、キャッシュ後に変更されたファイル、上書きされたファイルを自動で検知します。古いエントリーは自動で無効化され、キャッシュから削除されます。

# Deltaキャッシングを使う

Deltaキャッシュの推奨の(最も簡単な)利用方法は、クラスターを設定する際にDelta キャッシュ高速化ワーカータイプを選択するというものです。このようなワーカーでは、Deltaキャッシュがデフォルトで有効化され、設定されています。

c5d、r5d、z1dシリーズのワーカーはDeltaキャッシュの設定がされていますが、デオフォルトでは有効化されていません。キャッシュを有効化するには、[Deltaキャッシュの有効化、無効化](#deltaキャッシュの有効化無効化)を参照ください。

Deltaキャッシュは、ワーカーノードに提供されているローカルSSDの約半分の料理機を使用するのように設定されています。設定のオプションについては、[Deltaキャッシュを設定する](#deltaキャッシュを設定する)を参照ください。

# データのサブセットをキャッシュする

キャッシュすべきデータのサブセットを明示的に選択するには、以下の文法を使用します。

```sql:SQL
CACHE SELECT column_name[, column_name, ...] FROM [db_name.]table_name [ WHERE boolean_expression ]
```

Deltaキャッシュを適切に動作させるために、このコマンドを使用する必要はありません(最初にアクセスした際にデータは自動でキャッシュされます)。しかし、一貫性のあるクエリー性能を必要とする際には役立つかもしれません。

サンプルと詳細情報については以下を参照ください。

- Databricksランタイム7.x以降: [CACHE SELECT](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-cache.html)
- Databricksランタイム5.5LTS、6.x: [Cache Select \(Delta Lake on Databricks\)](https://docs.databricks.com/spark/2.x/spark-sql/language-manual/cache-dbio.html)

# Deltaキャッシュのモニタリング

Spark UIのStorageタブで、それぞれのエグゼキューターのDeltaキャッシュの現在の状態を確認することができます。
![](https://docs.databricks.com/_images/delta-cache-spark-ui-storage-tab.png)

最初のテーブルはアクティブなエグゼキューターノードそれぞれの以下のメトリクスを要約しています。

- **Disk Usage**: Parquetデータページを格納するのにDeltaキャッシュマネージャによって使用されている合計サイズ
- **Max Disk Usage Limit**: Parquetデータページを格納するのにDeltaキャッシュマネージャに割り当て可能な最大ディスクサイズ
- **Percent Disk Usage**: Parquetデータページを格納するのにDeltaキャッシュマネージャに割り当て可能な最大ディスクサイズに対して、使用されているディスク容量の割合。ノードが100%のディスク容量に達すると、新規データに対する領域を確保するために、キャッシュマネージャは一番最後に使用されたキャッシュエントリーを削除します。
- **Metadata Cache Size**: Parquetメタデータ(ファイルのフッター)をキャッシュするのに使用された合計サイズ
- **Max Metadata Cache Size Limit** Parquetメタデータ(ファイルのフッター)をキャッシュするのにキャッシュマネージャに割り当てられた最大ディスクサイズ
- **Percent Metadata Usage**: Parquetメタデータ(ファイルのフッター)に割り当てられた最大サイズに対して、Deltaキャッシュマネージャーが使用しているディスクの割合
- **Data Read from IO Cache (Cache Hits)**: 当該ノードのIOキャッシュから読み込まれたParquetデータの合計サイズ
- **Data Written to IO Cache (Cache Misses)**: キャッシュに存在せず、結果的に当該ノードのIOキャッシュに書き込まれたParquetデータの合計サイズ
- **Cache Hit Ratio**: 当該ノードで読み込まれた全てのParquetデータのうちIOキャッシュから読み込まれたParquetデータの割合

二つ目のテーブルは、現在アクティブではないノードを含むクラスターランタイムの全てのノードに対する以下のメトリクスを要約しています。

- **Data Read from External Filesystem (All Formats)**: IOキャッシュからではなく、外部ファイルシステムから読み込まれた任意のフォーマットのデータ読み込みの合計サイズ
- **Data Read from IO Cache (Cache Hits)**: クラスターランタイム全体でIOキャッシュから読み込まれたParquetデータの合計サイズ
- **Data Written to IO Cache (Cache Misses)**: クラスターランタイム全体で、キャッシュに存在せず結果的に当該ノードのIOキャッシュに書き込まれたParquetデータの合計サイズ
- **Cache Hit Ratio**: クラスターランタイム全体で読み込まれたParquetデータのうちIOキャッシュから読み込まれたParquetデータの割合
- **Estimated Size of Repeatedly Read Data**: 2回以上読み込まれたデータの近似サイズ。このカラムは`spark.databricks.io.cache.estimateRepeatedReads`が`true`になっている場合のみ表示されます。
- **Cache Metadata Manager Peak Disk Usage**: IOキャッシュを実行するためにDeltaキャッシュマネージャによって使用されたピークの合計サイズ

# Deltaキャッシュを設定する

お使いのクラスターに、[キャッシュ高速化ワーカーインスタンスタイプ](#deltaキャッシングを使う)を選択することをお勧めします。これらのインスタンスは、Deltaキャッシュに最適な設定が自動でされています。

## ディスク使用方法の設定

Deltaキャッシュがどのようにワーカーノードのローカルストレージを使用するのかを設定するには、クラスター作成時に以下の[Spark設定](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#spark%E3%81%AE%E8%A8%AD%E5%AE%9A)を適用します。

- `spark.databricks.io.cache.maxDiskUsage`: キャッシュデータに対するノードごとのディスク領域(バイト)
- `spark.databricks.io.cache.maxMetaDataCache`: キャッシュメタデータに対するノードごとのディスク領域(バイト)
- `spark.databricks.io.cache.compression.enabled`: キャッシュデータを圧縮フォーマットで保存するか否か

設定サンプルは以下のようになります。

```ini:ini
spark.databricks.io.cache.maxDiskUsage 50g
spark.databricks.io.cache.maxMetaDataCache 1g
spark.databricks.io.cache.compression.enabled false
```

## Deltaキャッシュの有効化、無効化

Deltaキャッシュの有効化、無効化を行うには以下を実行します。

```scala:Scala
spark.conf.set("spark.databricks.io.cache.enabled", "[true | false]")
```

キャッシュの無効化は、既にローカルストレージに存在するデータを削除することを意味しません。代わりに、キャッシュへの新規データの追加と、キャッシュからのデータ読み込みが行われなくなります。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

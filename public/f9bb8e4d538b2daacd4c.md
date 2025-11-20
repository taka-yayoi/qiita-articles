---
title: Delta Lakeのデータレイアウト
tags:
  - Databricks
  - deltalake
  - Databricks最適化ガイド
private: false
updated_at: '2024-11-18T11:36:38+09:00'
id: f9bb8e4d538b2daacd4c
organization_url_name: databricks
slide: false
ignorePublish: false
---
> **[DatabricksでSparkとDelta Lakeワークロードを最適化するための包括的ガイド](https://qiita.com/taka_yayoi/items/cd199691569fef069a9d)のコンテンツです。**

[Comprehensive Guide to Optimize Data Workloads \| Databricks](https://www.databricks.com/discover/pages/optimize-data-workloads-guide)のセクション[Underlying Data Layout](https://www.databricks.com/discover/pages/optimize-data-workloads-guide#data-layout)の翻訳です。

:::note warn
- 本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
- 2023年時点の内容です。一部情報が古いものがあります。
:::

Deltaテーブルの内部には、データを格納するParquetファイルが存在します。また、Parquetファイルのすぐ隣にはDeltaのトランザクションログを格納する *_delta_log* という名前のサブディレクトリが含まれています。これらのParquetファイルのサイズは、クエリー性能において非常に重要です。

ビッグデータの世界において、小さなファイル問題はよく知られている問題です。テーブルの背後のファイルが小さく大量になると、小さいファイルのオープン、クローズのためだけに時間を要するようになった結果、読み込みのレイテンシーで苦しむことになります。

この問題を回避するには、ワークロードや特定のユースケースに基づく、ケースバイケースの考え方で設定可能な16MBから1GBの間のファイルサイズにすることがベストとなります。

[Unity Catalog](https://www.databricks.com/jp/product/unity-catalog)でカタログ化されるマネージドテーブルを作成するために、Databricksランタイム11.3以降を使っているのであれば、Databricksがオートチューニング機能の一部として、バックグラウンドでDeltaテーブルのターゲットファイルサイズの設定やファイルサイズの最適化を自動で行うので、これらのことを心配する必要はありません。将来的には、外部テーブルでもこの機能を活用できるようになります。

他のケースにおいては、適切なファイルサイズを得るために、特定のSparkジョブを用いて手動でファイルをコンパックとにする必要があるかもしれませんが、Deltaはすぐに利用できるビンパッキングの機能(コンパクション)を提供しているので、このようなことは不要です。Deltaでは、以下で説明するように2つの方法でビンパッキングを達成することができます:

# 1. Optimize & Z-order

[OPTIMIZE](https://docs.databricks.com/en/sql/language-manual/delta-optimize.html)は、ファイルサイズが最大1GB([設定可能](https://docs.databricks.com/ja/delta/tune-file-size.html)です)になるようにファイルをコンパクトにします。このコマンドは基本的に、設定したサイズ(設定しない場合にはデフォルトの1GB)にファイルをサイジングしようとします。また、選択したカラムによってデータを物理的にソートし、コロケーションするZORDERとOPTIMIZEコマンドを組み合わせることができます。

```sql
OPTIMIZE table_name [WHERE predicate]
[ZORDER BY (col_name1 [, ...] ) ]
```

![](https://www.databricks.com/sites/default/files/inline-images/alert-icon.png?v=1688736447)

- Z-orderingでは常にカーディナリティの高いカラム(注文テーブルにおける`customer_id`など)を選ぶようにしましょう。日付からむは通常カーディナリティの低いカラムなので、Z-orderで用いるべきではありません。それらはパーティショニングのカラムに適しています(しかし、テーブルを常にパーティショニングする必要はありません。詳細は以下の[パーティショニング](#3-パーティショニング)のセクションをご覧ください)。Z-orderにおいては、後段のクエリーにおけるフィルター句やjoinキーで頻繁に用いられるカラムを選択しましょう。
- Z-orderingで多数のカラムを指定すると、Z-orderの効果を劣化させるので、4カラムより多いカラムを指定しないようにしましょう。
- ジョブ自身で**OPTIMIZE**コマンドを実行するのではなく、個別のジョブクラスターで実行しましょう。さもないと、対応するジョブのSLAにインパクトを与える可能性があります。
- **OPTIMIZE**コマンドはコンピュート重視のオペレーションなので、コンピュート最適化インスタンスファミリーを使うことをお勧めします。
- 後段のクエリーパフォーマンスを改善するために、適切なファイルレイアウトを維持するために、(**ZORDER**の有無に関係なく)**OPTIMIZE**コマンドは一日一回のように定期的に実行すべきです。

# 2. Auto optimize

[Auto optimize](https://learn.microsoft.com/ja-jp/azure/databricks/delta/tune-file-size)は、その名前が示すように、Deltaテーブルの個別の書き込みの処理の過程で小さなファイルを自動でコンパクトにし、デフォルトでは128MBのファイルサイズにしようと試みます。2つの機能を提供しています:

## 1. Optimize Write

Optimize Writeは、実際のデータに基づいて、Apache Sparkのパーティションサイズを動的に最適化し、それぞれのテーブルパーティションとして128MBのファイルを書き出そうとします。これは、同じSparkジョブの中で行われます。

## 2. Auto Compact

Sparkジョブの完了後、Auto Compactは128MBを達成するために、さらにファイルを圧縮できないかをチェックする新規のジョブを起動します。

```sql
-- Table properties
delta.autoOptimize.optimizeWrite = true 
delta.autoOptimize.autoCompact = true

-- In Spark session conf for all new tables
set spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite = true
set spark.databricks.delta.properties.defaults.autoOptimize.autoCompact = true
```

![](https://www.databricks.com/sites/default/files/inline-images/alert-icon.png?v=1688736447)

- 満足できるファイルサイズを得るために手動で(**ZORDER**の有無に関係なく)**OPTIMIZE**コマンドを活用していない場合には、常に*optimizeWrite*テーブルプロパティを有効化しましょう。Optimize Writeでは、ターゲットテーブルのパーティションの構造によってデータのシャッフルが必要になることを覚えておきましょう。このシャッフルは通常追加のコストを発生させます。しかし、書き込みの際のスループットのゲインは、シャッフルのコストを補うものとなるでしょう。そうでない場合でも、データにクエリーする際のスループットのゲインは依然としてこの機能を価値あるものにするに違いありません。
- あなたのジョブに厳密なSLAが無いのであれば、Deltaのビンパッキングをさらに活用するために*autoCompact*テーブルプロパティを有効化することができます。

# 3. パーティショニング

[パーティショニング](https://docs.databricks.com/en/sql/language-manual/sql-ref-partition.html#partition)によってSparkはスキャン時に不要なデータパーティション(サブフォルダー)の多くをスキップできるので、フィルタリングやjoin、集計、mergeでパーティションカラムを指定することでクエリーを高速化することができます。

![](https://www.databricks.com/sites/default/files/inline-images/alert-icon.png?v=1688736447)

- Databricksでは、1TB以下のテーブルをパーティショニングすることはお勧めしておらず、[取り込み時のクラスタリング](https://qiita.com/taka_yayoi/items/d58525efa9e19b7b2fa0)が自動で動作するままにしましょう。この機能はデフォルトで全てのテーブルで有効化されており、データが取り込まれた順序に基づいてデータをクラスタリングします。
- それぞれのパーティションが最低でも1GBになることが予測されるのであれば、カラムでパーティションを作成することができます。
- 年や日のように、常にカーディナリティの低いカラムをパーティションカラムとして選択しましょう。
- パーティションカラムを選択する際に、Deltaの[ジェネレーテッドカラム](https://learn.microsoft.com/ja-jp/azure/databricks/delta/generated-columns)を活用することもできます。ジェネレーテッドカラムは、Deltaテーブルの他のカラムに対するユーザー指定の関数に基づいて自動で値が生成される特殊なタイプのカラムです。

# 4. ファイルサイズのチューニング

Auto-optimize(128MB)やOptimize(1GB)によってターゲットとされるデフォルトのファイルサイズが適していない場合、あなたの要件に基づいてファインチューンすることができます。`delta.targetFileSize`テーブルプロパティを用いることで、[ターゲットのファイルサイズ](https://docs.databricks.com/ja/delta/tune-file-size.html)を設定することができ、Auto-optimizeやOptimizeは指定されたサイズを達成するようにビンパッキングを行います。

```sql
-- Table properties
delta.targetFileSize = 134217728
```

また、手動でターゲットファイルサイズを設定したく無いのであれば、`delta.tuneFileSizesForRewrites`テーブルプロパティをオンにすることで、このタスクをDatabricksに委任することができます。このプロパティがtrueに設定されると、Databricksはワークロードに基づいて自動でファイルサイズを調整します。例えば、Deltaテーブルで多数のマージを行う場合、マージオペレーションを高速にするために、1GBより遥かに小さいサイズにファイルが自動で調整されます。

```sql
-- Table properties
delta.tuneFileSizesForRewrite = true
```



### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

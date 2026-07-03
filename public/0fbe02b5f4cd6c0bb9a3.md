---
title: Sparkのデータ溢れ(スピル)の発生理由と対策
tags:
  - Spark
  - Databricks
  - Databricks最適化ガイド
private: false
updated_at: '2024-11-18T11:38:01+09:00'
id: 0fbe02b5f4cd6c0bb9a3
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
> **[DatabricksでSparkとDelta Lakeワークロードを最適化するための包括的ガイド](https://qiita.com/taka_yayoi/items/cd199691569fef069a9d)のコンテンツです。**

[Comprehensive Guide to Optimize Data Workloads \| Databricks](https://www.databricks.com/discover/pages/optimize-data-workloads-guide)のセクション[Data Spilling — Why It Happens and How to Get Rid of It](https://www.databricks.com/discover/pages/optimize-data-workloads-guide#data-spilling)の翻訳です。

:::note warn
- 本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
- 2023年時点の内容です。一部情報が古いものがあります。
:::

# データの溢れ - なぜ起きるのか、どのように排除するのか

Spark SQLのシャッフルパーティション(join、集計などのワイドの変換処理を実行するために使用されるCPUの数)の数のデフォルト設定は200であり、これが常にベストな値とは限りません。この結果、処理する大量のデータに対してそれぞれのSparkタスク(CPUコア)が割り当てられ、それぞれのコアがそのデータにフィットするのに十分なメモリーがない場合、それらの幾らかはディスクに溢れます。溢れ(スピル)はいかなる労力を払っても回避すべきであり、そのためにはシャッフルパーティションの数をチューニングしなくてはなりません。以下で議論するように、Spark SQLのシャッフルパーティションの数をチューニングするにはいくつかの方法があります。

## 1. AQEのオートチューニング

Spark AQEには、シャッフルパーティションの適切な値を自動で特定できる`autoOptimizeShuffle` (AOS)という機能があります。オートチューニングを有効化するための設定は以下の通りとなります。

```
set spark.sql.shuffle.partitions=auto
```

:::note warn
**注意** 異常な圧縮

AOSには特定の制限が存在します。AOSはソーステーブルで通常ではないような圧縮率(20倍から40倍)がある場合において、適切なシャッフルパーティションを推定することができない場合があります。
:::

圧縮率の高いテーブルを特定するには2つの方法があります:

### 1. Spark UIのSQL DAG

![](https://www.databricks.com/en-website-assets/static/99312bcbed54cf6352e951fc3256c249/22882.png)

Exchangeノードの`data size total`メトリクスはメモリーにおけるテーブルの正確なサイズを示しませんが、圧縮率の高いテーブルを特定する助けになります。Scan Parquetノードは、ディスクにおけるテーブルの正確なサイズを提供します。上述のケースにおいて、Exchangeノードのデータサイズはディスクのサイズよりも40倍大きくなっており、テーブルはおそらくディスクでの圧縮率が高くなっていることを示しています。

### 2. テーブルのキャッシュ

メモリーにおける実際のサイズを特定するために、テーブルをメモリーにキャッシュすることができます。以下に方法を示します:

```py
-- count here is forcing the cache materialization
spark.table("table").cache().count()
```

上のコマンドを実行した後に、メモリーにおけるテーブルのサイズを特定するには、Spark UIのストレージタブを参照します。

![](https://www.databricks.com/en-website-assets/static/77b652b4d05b9ad140521b5dc141168c/22883.png)

**ソリューション:** この現象に対応するには、以下のように初期のシャッフルパーティションの値(デフォルトは128MB)を特定するために、AQEによって使用されるパーティションあたりの値を少なくします:

```
-- setting to 16MB for example
set spark.databricks.adaptive.autoOptimizeShuffle.preshufflePartitionSizeInBytes = 16777216
```

`preshufflePartitionSizeInBytes`の値を16MBを小さくすると、AOSがパーティションの値を間違って計算していており、大きなデータの溢れを経験しているのであれば、`preshufflePartitionSizeInBytes`をさらに8MBに削減します。これでも溢れの問題を解消できない場合には、AOSを無効化して、次のセクションで説明するようにシャッフルパーティションの数を手動で調整するのがベストと言えます。

## 2. 手動でのファインチューン

シャッフルパーティションの数を手動でチューニングするには、以下を必要とします:

1. シャッフルされるデータの総量。そのためには、一度Sparkクエリーを実行し、以下の例に示しているようにこの値を取得するためにSpark UIを使います。

    ![](https://www.databricks.com/en-website-assets/static/d003148c3151721790d4702ddff3c314/22884.png)

1. 経験則として、シャッフルパーティションの数を調整した後には、それぞれのタスクがおおよそ**128MB**から**200MB**のデータを処理するようになっていることを確認する必要があります。以下の例で示しているように、Spark UIのシャッフルステージのサマリーメトリクスでこの値を確認することができます。

    ![](https://www.databricks.com/en-website-assets/static/63ae9b06fa43062399d1c8865ed306b5/22890.png)

こちらが、シャッフルパーティションの適切な値を計算するための数式となります:

以下を仮定しましょう:

- クラスターにおける総ワーカーコアの合計数 = T
シャッフルステージでシャッフルされるデータの総量(MB) = B
- タスクごとに処理される最適なデータサイズ(MB) = 128
- 結果として、積算のファクター(M)は: `M = ceiling(B / 128 / T)`となり、
- シャッフルパーティションの数(N)は: `N = M x T` になります。

最後の実行サイクルまで全てのクラスターコアが完全にエンゲージするように、ここではceiling関数を使っていることに注意してください。

![](https://www.databricks.com/sites/default/files/inline-images/alert-icon.png?v=1688736447)

- タスクごとに処理される最適なデータのサイズは約128MBです。多くの場合、これでうまくいきます。あなたのクエリーである種のデータ爆発が発生している場合はうまくいかないかもしれません。その場合は、より小さい値を選択しなくてはならないかもしれません。本書の[後のセクション](https://www.databricks.com/discover/pages/optimize-data-workloads-guide#data-explosion)でデータ爆発に関して取り扱っています。
- シャッフルパーティションに対するオートチューン(AOS)も手動でのファインチューニングも行わない場合、経験則としてワーカーのCPUコア数の2倍、あるいは3倍にするというものがあります。

    ```
    -- in SQL
    set spark.sql.shuffle.partitions = 2*<number of total worker cores in cluster>
    -- in PySpark
    spark.conf.set(“spark.sql.shuffle.partitions”, 2*<number of total worker cores in cluster>)
    -- or
    spark.conf.set(“spark.sql.shuffle.partitions”, 2*sc.defaultParallelism)
    ```

- 単一のノートブックに複数のSpark SQLクエリーが存在する場合があるため、それぞれのクエリーに対するシャッフルパーティション数のファインチューニングは時間を浪費するタスクとなります。このため、シャッフルステージでシャッフルされるデータの総量が最も多い最大のクエリーに対してファインチューニングし、ノートブック全体にその値を適用するのがアドバイスとなります。
- データに偏りがある場合には、シャッフルパーティションのファインチューニングがデータの溢れを改善しません。この場合、データの偏りを最初に取り除くべきです。詳細に関しては、次の[データ偏りに関するセクション](https://www.databricks.com/discover/pages/optimize-data-workloads-guide#data-skewness)をご覧ください。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

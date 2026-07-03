---
title: Delta Lake 1.1を用いてデータレイクハウスを高速に
tags:
  - Databricks
  - deltalake
private: false
updated_at: '2022-03-17T16:58:46+09:00'
id: 8d61e6e2afe30a8cb5ec
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[How to Make Your Lakehouses Run More Efficiently and Faster With Delta Lake 1\.1 \- The Databricks Blog](https://databricks.com/blog/2022/01/31/make-your-data-lakehouse-run-faster-with-delta-lake-1-1.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

**Delta Lake 1.1はマージオペレーションの性能を改善し、ジェネレーテッドカラムのサポートを追加し、ネストされたフィールドの解決を改善します。**

オープンソースコミュニティの多大なる貢献により、Delta Lakeコミュニティは最近[Apache Spark™ 3\.2](https://spark.apache.org/releases/spark-release-3-2-0.html)における[Delta Lake 1\.1\.0](https://github.com/delta-io/delta/releases)のリリースを発表しました。Apache Sparkと同様に、Delta LakeコミュニティはScala 2.12とScala 2.13向けの[Mavenアーティファクト](https://mvnrepository.com/artifact/io.delta/delta-core)と[PyPI \(delta\_spark\)](https://pypi.org/project/delta-spark/)をリリースしました。

このリリースには、MERGEオペレーション、ネストされたフィールドの解決周りの特筆すべき改善とPython型ノーテーション、`replaceWhere`における任意表現などが含まれています。Delta LakeがApache Sparkのインベーションに対して最新の状態を保つことが非常に重要です。これは、[Spark Release 3\.2\.0](https://spark.apache.org/releases/spark-release-3-2-0.html)で利用できる機能を用いて、Delta Lakeで更なるパフォーマンスのメリットを享受できることを意味します。

本記事においては、新たな1.1.0リリースにおいて特筆すべき機能と主要な変更をカバーします。詳細は[project’s Github repository](https://github.com/delta-io/delta/releases)をチェックしてください。

> すぐにDelta Lakeを試したいですか？[Delta Lake](https://docs.delta.io/latest/delta-intro.html)が何であるかを学び、Delta Lakeを用いてレイクハウスを構築するにはこちらの[ガイド](https://docs.delta.io/latest/quick-start.html)を活用してください。

# Delta Lake 1.1の主要機能

- **MERGEオペレーションにおける性能改善**: パーティション化されたテーブルにおいて、MERGEオペレーションはファイルを[書き出す前に自動で出力データの再パーティション](https://docs.delta.io/latest/delta-update.html#performance-tuning)を行います。これにより、MERGEオペレーションと後続の読み取りオペレーションにおけるアウトオブボックスの優れたパフォーマンスを提供します。
- **DataFrameReader/WriterオプションによるHadoop設定のサポート**: DataFrameReader/WriterのオプションとしてHadoop FileSystemの設定(アクセス認証情報など)を行うことができます。これまでは、このような設定を指定するには、全ての読み書きに適用されるSparkセッション設定に引き渡すしか選択肢がありませんでした。これにより、今では読み取り、書き込みそれぞれに異なる値を設定することができます。詳細は[ドキュメント](https://docs.delta.io/1.1.0/delta-batch.html#dataframe-options)を参照ください。
- **DataFrameWriterオプションのreplaceWhereにおける任意表現のサポート**: パーティションカラムのみに対する表現の代わりに、DataFrameWriterオプションのreplaceWhereで任意の表現を用いることができます。これは、データフレームの書き込みで直接テーブルのデータを好きなように置き換えることができることを意味します。
- **ネストされたフィールド解決の改善、struct配列に対するMERGEオペレーションにおけるスキーマ進化**: ネストされたstructの配列として型が定義されたカラムを持つターゲットテーブルに対してMERGEオペレーションを適用する際、ソース、ターゲットデータ間のネストされたカラムは、struct内の位置ではなく名前によって解決されます。これにより、配列ないのstructは、配列外のstructと一貫性のある挙動をします。MERGEに対して自動スキーマ進化が有効化されると、structのネストされたカラムは、配列外のstrcutのカラムとして同じ進化ルールに従います(例：テーブルに同じ名前のカラムが存在しない場合に追加)。詳細は[ドキュメント](https://docs.delta.io/1.1.0/delta-batch.html#dataframe-options)を参照ください。
- **MERGEオペレーションにおけるジェネレーテッドカラムのサポート**: [ジェネレーテッドカラム](https://docs.delta.io/latest/delta-batch.html#use-generated-columns)を持つテーブルに対してMERGEオペレーションを適用することができます。
- **GCSにおける稀に起きるデータ破壊の修正**: Delta Lake 1.0の実験的GCSサポートにおいては、部分的に書き込まれたトランザクションログによりDeltaテーブルが読み込めなくなると言う稀なバグが存在していました。この問題が修正されました([1](https://github.com/delta-io/delta/commit/7a3f1e8ec626e80880d524c2b897a969c8b4d63a)、[2](https://github.com/delta-io/delta/commit/95e90763fd9f54df8880911b28b97b023a485d5f))。
- **Python DeltaTable.convertToDelta()で不適切な型のオブジェクトを返却するバグの修正**: 不適切な型のオブジェクトを返却し利用できなかったAPIが、適切なdelta.tables.DeltaTable型のPythonオブジェクトを[返却](https://github.com/delta-io/delta/commit/c586f9a7374923867c36f61df4ed133725c8df2c)するようになりました。
- **Python型アノテーション**: 型ヒントをサポートするエディタにおけるオートコンプリートの性能を改善するPython型アノテーションを追加しました。オプションとして、[mypy](http://mypy-lang.org/)やビルトインツール(Pycharmツールなど)における静的なチェックを有効化することができます。

Delta 1.1.0における他の特筆すべき機能は以下の通りとなります。

1. パーティションカラム名に特殊文字を含むテーブルの読み込みサポートを削除。詳細は[migration guide](https://docs.delta.io/1.1.0/porting.html#delta-lake-1-0-and-below-to-1-1-and-above)をご覧ください。
1. 他のAPIとの一貫性のために、DeltaTable.forName()の"delta.`path`"を[サポート](https://github.com/delta-io/delta/commit/1470e33f3f728a1670a77da63f3fb78780c30873)
1. Delta 1.0.0で導入された[DeltaTableBuilder API](https://docs.delta.io/1.1.0/delta-batch.html#create-a-table)の改善
    - Python DeltaTableBuilder.partitionByで複数のパーティションカラムを指定できなかったバグの[修正](https://github.com/delta-io/delta/commit/59aa330c403f8a71b3eef0e90bd61cd54aab108c)
    - カラムのデータ型が指定されていない場合に[エラーをスロー](https://github.com/delta-io/delta/commit/104e2a472b5a0a5c718c42ac14ac8b851a1a7fe8)
1. 一時ビューにおけるMERGE/UPDATE/DELETE[サポート](https://github.com/delta-io/delta/commit/83277eb30c0834bd837d9658864261fc31d366f6)の改善
1. テーブル作成、置換時のコミット情報でユーザーメタデータを[サポート](https://github.com/delta-io/delta/commit/a2722f8b17369a47dd8d23696fc4958f022bb496)
1. 自動隙間エボリューションが有効化され、複数のINSERT、UPDATE句を伴うMERGEを行う際の不適切な分析例外の[修正](https://github.com/delta-io/delta/commit/4e1c53c6984ba7d56fd2a0d9fe27ac2573df27ea)
1. MERGE/UPDATE/DELETEオペレーションにおけるパス(スペースなど)の特殊文字の不適切な取り扱いの[修正](https://github.com/delta-io/delta/commit/4359484368b4a06c32b663826ac60bf12d9e8025)
1. Apache Spark 3.2でデフォルトで有効化されたAdaptive Query Executionによって影響を受けるVacuum並列モードの[修正](https://github.com/delta-io/delta/commit/7f46e91cf0950e437ffbce93d8a5925ebd0a3991)
1. 最新の適切なタイムトラベルバージョンに関する[修正](https://github.com/delta-io/delta/commit/4243bccbe397e0f47dc36b525f14983d57bbc848)
1. チェックポイントを書き込む際にHadoop設定が使用されないバグの[修正](https://github.com/delta-io/delta/commit/43d14226cc802d721d1683495cdc8511acf460a1)
1. Delta制約に対する複数の修正([1](https://github.com/delta-io/delta/commit/83780aeeadd67893ad69ed6481f7c6bce5be563c)、[2](https://github.com/delta-io/delta/commit/685820b66ec42de7ef8f8a61ef3fd0fcfb702a70)、[3](https://github.com/delta-io/delta/commit/db113dab3db5bdc371f3d49734e26a7403372c24))

次のセクションでは、本リリースで最も特筆すべき機能にディープダイブしていきましょう。

# MERGEオペレーションに対するアウトボックスの優れたパフォーマンス

![](https://databricks.com/wp-content/uploads/2022/01/data-lakehouse-run-faster-img-blog-11.jpg)

- 上のグラフは機能フラグを有効化することで、19.66分(有効化前)から7.6分(有効化後)に、実行時間を劇的に削減したことを示しています。
- 以下に示すクエリー前後のDAGビジュアライゼーションのステージの違いに注意して下さい。SortMergeJoinの後にAQE ShuffleReadステージが追加されています。

![](https://databricks.com/wp-content/uploads/2022/01/data-lakehouse-run-faster-img-blog-5-2.jpg)
図: [repartitionBeforeWrite](https://databricks.com/blog/2022/01/31/make-your-data-lakehouse-run-faster-with-delta-lake-1-1.html)が無効化された状態でのdelta mergeのクエリーに対するDAG

![](https://databricks.com/wp-content/uploads/2022/01/data-lakehouse-run-faster-img-blog-6.jpg)
図: repartitionBeforeWrite](https://databricks.com/blog/2022/01/31/make-your-data-lakehouse-run-faster-with-delta-lake-1-1.html)が有効化された状態でのdelta mergeのクエリーに対するDAG

この**サンプル**を見ていきましょう。

この例で使われたデータセットでは、customers1とcustomers2は顧客と売り上げに関する200,000行と11列のデータを保持しています。必要最小限のデータに対してMERGEオペレーションを実行する際にフラグを有効化することによる違いを示すために、Macbook Pro 2019ラップトップ上のSparkのジョブを1GBのメモリーと1コアに限定しました。使用するRAMとコアを調整することで、これらの数値はさらに削減される可能性があります。MERGEテーブルにおいては、事前のテーブルにMERGEオペレーションを実行するために、45,000行のcustomers_mergeが使用されます。このサンプルの完全なスクリプトと結果は[こちら](https://github.com/vinijaiswal/delta-lake/tree/main/delta1.1_merge)から参照できます。

*機能が無効化されていることを確認してから、以下のコマンドを実行してください。*

```py:Python
sql(”SET spark.databricks.delta.merge.repartitionBeforeWrite.enabled = false”)
```

コードは以下の通りとなります。

```py:Python
from delta.tables import *
deltaTable = DeltaTable.forPath(spark, "/temp/data/customers1")
mergeDF = spark.read.format("delta").load("/temp/data/customers_merge")
deltaTable.alias("customers1").merge(mergeDF.alias("c_merge"),"customers1.customer_sk = c_merge.customer_sk").whenNotMatchedInsertAll().execute()
```

**結果**

:::note info
**注意**
**機能フラグを無効にするとオペレーション全体は<font color="red">19.66分</font>かかります。** クエリーの詳細に関しては、こちらの[完全な結果](https://github.com/vinijaiswal/delta-lake/blob/main/delta1.1_merge/repartitionBeforeWrite.enabled%3Dfalse.pdf)を参照することができます。
:::

![](https://databricks.com/wp-content/uploads/2022/01/data-lakehouse-run-faster-img-blog-7-761x1024.jpg)

パーティション化されたテーブルに対しては、MERGEはシャッフルパーティションの数より多い数の小さいファイルを生成する場合があります。これは、それぞれのシャッフルタスクが複数のパーティションに複数のファイルを書き込むことによるものであり、パフォーマンス上のボトルネックとなり得ます。パーティション化されたテーブルに対するMERGEオペレーションを高速化するには、以下のコードスニペットを使用する前にrepartitionBeforeWriteを有効化しましょう。

## フラグを有効にして再度MERGEを実行

```py:Python
sql(”SET spark.databricks.delta.merge.repartitionBeforeWrite.enabled = true”)
```

これにより、MERGEオペレーションがファイルを書き込む前にパーティション化されたテーブルの出力データを自動で再パーティショニングします。これは多くの場合、書き込みを行う前にテーブルのパーティションカラムによる出力データの再パーティションの役に立ちます。これによって、MERGEオペレーションと後続の読み取りオペレーションの両方に対してアウトボックスの優れたパフォーマンスを提供します。それではcustomer_t0テーブルにMERGEオペレーションを実行してみましょう。

```py:Python
from delta.tables import *
deltaTable = DeltaTable.forPath(spark, "/temp/data/customers2")
mergeDF = spark.read.format("delta").load("/temp/data/customers_merge")
deltaTable.alias("customers2").merge(mergeDF.alias("c_merge"),"customers2.customer_sk = c_merge.customer_sk").whenNotMatchedInsertAll().execute()
```

:::note info
**注意**
「repartitionBeforeWrite」機能を有効化した後は、MERGEクエリーの処理時間は7.68分となります。クエリーの詳細は[こちら](https://github.com/vinijaiswal/delta-lake/blob/main/delta1.1_merge/repartitionBeforeWrite.enabled%3Dtrue.pdf)から参照できます。
:::

[How to Make Your Lakehouses Run More Efficiently and Faster With Delta Lake 1\.1 \- The Databricks Blog](https://databricks.com/wp-content/uploads/2022/01/delta-11-blog-image-7-577x1024.jpg)

:::note info
**ティップ**
GDPRやCCPAのユースケースに関わっている企業においては、お使いのデータレイクの再構成を行うことなしにコスト効率が高い方法で特定の場所の高速アップデート、高速削除が可能になるので、この機能が非常に役立ちます。
:::

# DataFrameWriterオプションのreplaceWhereにおける任意の表現のサポート

原子的にテーブルの全てのデータを置換するには上書きモードを使用します。

```sql:SQL
INSERT OVERWRITE TABLE default.customer_t10 SELECT * FROM customer_t1
```

Delta Lake 1.1.0以降では、データフレームを用いて任意の表現とマッチするデータのみを選択的に上書きすることができます。以下のコマンドは、c_birth_yearでパーティショニングされ、customer_t1にデータを持つターゲットテーブルの生年が`1924`であるレコードのみを原子的に置き換えます。

```py:Python
input = spark.read.table("delta.`/usr/local/delta/customer_t1`")

input.write.format("delta") \
  .mode("overwrite") \
  .option("overwriteSchema", "true") \
  .partitionBy("c_birth_year") \
  .option("replaceWhere", "c_birth_year >= '1924' AND c_birth_year <= '1925'") \
  .saveAsTable("customer_t10")
```

このクエリーの実行は成功し、以下のアウトプットが得られます。
![](https://databricks.com/wp-content/uploads/2022/01/data-lakehouse-run-faster-img-blog-9.jpg)

しかし、1.1.0より前の過去のDelta Lakeリリースでは、同じクエリーは以下のエラーとなります。
![](https://databricks.com/wp-content/uploads/2022/01/data-lakehouse-run-faster-img-blog-5-1.jpg)

replaceWhereフラグを無効化することでこれを試すことができます。

# Python型アノテーション

Python型アノテーションは、型ヒントをサポートするエディタにおけるオートコンプリートの性能を改善します。オプションとして、[mypy](http://mypy-lang.org/)やビルトインツール(Pycharmツールなど)を通じた静的チェックを有効化することができます。PRのオリジナルオーサーである[Maciej Szymkiewicz](https://github.com/zero323)による[動画](https://asciinema.org/a/TyWTbNNXRkk8h4YBHRTAPJ9L7)では、Delta Lake 1.1におけるPythonの挙動の変化を説明しています。

https://asciinema.org/a/TyWTbNNXRkk8h4YBHRTAPJ9L7

この記事を通じてクールなDelta Lakemの機能を見ていただけたと思います。皆様がこれらの機能を活用している様子を見ることができたら非常に嬉しいですし、もしフィードバックや、成果物のサンプルなどがありましたら[コミュニティ](https://delta.io/#:~:text=Join%20the%20Delta%20Lake%20Community)でシェアしてください。

# まとめ

レイクハウスはデータプラットフォーム、データアーキテクチャを構築したいと考えている組織における新たな標準となりました。そして、これは全て、5000以上の企業がデータとAIアプリケーションに対するプロダクションレイクハウスプラットフォームの構築を現実のものとしたDelta Lakeによるものです。データの指数関数的増加により、大量のデータを高速化つ高信頼に処理することが重要となっています。Delta Lake、そしてバージョン1.1の機能を用いることで、開発者は自身のレイクハウスをより高速に実行できるようになり、イノベーションのペースを維持することができます。

**オープンソースのDelta Lakeに興味がありますか？**
[Delta Lake online hub](https://delta.io/)を訪れてみてください。[Slack](http://dbricks.co/delta-users-slack)や[Google Group](https://groups.google.com/forum/#!forum/delta-users)経由でコミュにぃに参加できます。今後のリリースや計画されている機能を[GitHub milestones](https://github.com/delta-io/delta/milestones)で追跡することができますし、Databricksの[フリーアカウント](https://databricks.com/jp/try-databricks)を用いてマネージドのDelta Lakeをトライすることもできます。

**クレジット**
以下の方々のDelta Lake 1.1.0への貢献に感謝の意を評します：Abhishek Somani, Adam Binford, Alex Jing, Alexandre Lopes, Allison Portis, Bogdan Raducanu, Bart Samwel, Burak Yavuz, David Lewis, Eunjin Song, ericfchang, Feng Zhu, Flavio Cruz, Florian Valeye, Fred Liu, gurunath, Guy Khazma, Jacek Laskowski, Jackie Zhang, Jarred Parrett, JassAbidi, Jose Torres, Junlin Zeng, Junyong Lee, KamCheung Ting, Karen Feng, Lars Kroll, Li Zhang, Linhong Liu, Liwen Sun, Maciej, Max Gekk, Meng Tong, Prakhar Jain, Pranav Anand, Rahul Mahadev, Ryan Johnson, Sabir Akhadov, Scott Sandre, Shixiong Zhu, Shuting Zhang, Tathagata Das, Terry Kim, Tom Lynch, Vijayan Prabhakaran, Vítor Mussa, Wenchen Fan, Yaohua Zhao, Yijia Cui, YuXuan Tay, Yuchen Huo, Yuhong Chen, Yuming Wang, Yuyuan Tang, Zach Schuermann.

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

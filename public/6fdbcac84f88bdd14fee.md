---
title: DatabricksのPhoton
tags:
  - Photon
  - Databricks
private: false
updated_at: '2022-08-04T06:08:05+09:00'
id: 6fdbcac84f88bdd14fee
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Photon \| Databricks on AWS](https://docs.databricks.com/runtime/photon.html) [2022/7/27時点]の翻訳です。

Photonは、Databricksにおけるネイティブのベクトル化されたクエリーエンジンであり、既存のコードを実行できるようにApache Spark APIと直接互換性があります。モダンなハードウェアを活用できるようにC++で実装されており、CPUにおけるデータ、命令レベルの並列性を利用するために、ベクトル化クエリー処理における最新技術を活用しています。さらには、データレイクに対してネイティブに動作することで、実世界のデータとアプリケーションにおけるパフォーマンスを改善しています。Photonはお使いのSQL、データフレームAPIを高速に実行する高性能ランタイムの一部であり、ワークロードあたりのトータルコストを削減します。Databricks SQLウェアハウスではデフォルトでPhotonが使用されます。

# Databricksクラスター

DatabricksクラスターでPhotonにアクセスするには、[UI](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#databricks%E3%83%A9%E3%83%B3%E3%82%BF%E3%82%A4%E3%83%A0)あるいはAPI([Clusters API 2\.0](https://docs.databricks.com/dev-tools/api/latest/clusters.html)、[Jobs API 2\.1](https://docs.databricks.com/dev-tools/api/latest/jobs.html)において、`<databricks-runtime-version>-photon-scala2.12`の文法に従い`spark_version`を指定します)を用いてクラスターを作成する際に明示的に[Photonを含むランタイムを選択](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#databricks%E3%83%A9%E3%83%B3%E3%82%BF%E3%82%A4%E3%83%A0)する必要があります。Photonは、[Databricksランタイム 9.1 LTS](https://docs.databricks.com/release-notes/runtime/9.1.html)以降で利用できます。

Photonは、サポートするドライバーノード、ワーカーノードのインスタンスタイプを限定しています。Photonインスタンスタイプは、非Photonランタイムを実行する同じインスタンスタイプとは異なるレートのDBUを消費します。PhotonインスタンスとDBU消費に関しては、[Databricksプライシングページ](https://databricks.com/product/aws-pricing/instance-types)をご覧ください。

# Photonのカバレッジ

**オペレーター**

- Scan, Filter, Project
- Hash Aggregate/Join/Shuffle
- Nested-Loop Join
- Null-Aware Anti Join
- Union, Expand, ScalarSubquery
- Delta/Parquet Write Sink
- Sort
- Window Function

**エクスプレッション**

- Comparison / Logic
- Arithmetic / Math (ほぼすべて)
- Conditional (IF, CASEなど)
- String (一般的なもの)
- Casts
- Aggregates(一般的なものの大部分)
- Date/Timestamp

**データタイプ**

- Byte/Short/Int/Long
- Boolean
- String/Binary
- Decimal
- Float/Double
- Date/Timestamp
- Struct
- Array
- Map

# 利点

- DeltaおよびParquetテーブルに対するSQLおよび同等のデータフレームオペレーションをサポート。
- 大量のデータ(100GB以上)に対する集計、ジョインを含むクエリー処理の高速化が期待できる。
- Deltaキャッシュから繰り返しデータがアクセされるときの高速なパフォーマンス。
- 多くのカラム、多くの小規模ファイルを持つテーブルに対するスキャン性能の安定化。
- 特に幅の広いテーブル(数百から数千のカラム数)において、`UPDATE`、`DELETE`、`MERGE INTO`、`INSERT`、`CREATE TABLE AS SELECT`を用いたDelta、Parquetへの書き込みの高速化。
- ソートマージジョインをハッシュジョインで置き換える。

# 制限

- Spark構造化ストリーミングは未サポート。
- UDFは未サポート。
- RDD APIは未サポート
- 短時間のクエリー(2秒未満)、例えば、小規模データに対するクエリーでは性能改善が期待できない。

Photonでサポートされていない機能は、Databricksランタイムと同じように実行されます。これらの機能における性能面での利点はありません。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

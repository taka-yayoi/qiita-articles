---
title: ParquetやIcebergからDelta Lakeへのインクリメンタルなクローン
tags:
  - Databricks
  - Parquet
  - iceberg
  - deltalake
private: false
updated_at: '2022-11-26T13:45:08+09:00'
id: bc3edb691c6f1fc7c79a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Incrementally clone Parquet and Iceberg tables to Delta Lake \| Databricks on AWS](https://docs.databricks.com/ingestion/clone-parquet.html) [2022/10/5時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

ParquetやIcebergのデータソースからのデータを、マネージドあるいは外部Deltaテーブルにインクリメンタルに変換するためにDatabricksのクローン機能を活用することができます。

ParquetやIcebergに対するDatabricksのクローンは、[Deltaテーブルのクローン](https://qiita.com/taka_yayoi/items/50c5a75caff8a6fb721d)や[Delta Lakeへのテーブル変換](https://qiita.com/taka_yayoi/items/ca4c822bcc02f4ea8f7c)の機能を組み合わせます。本書では、この機能のユースケースと制限、そしてサンプルを説明します。

:::note
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

:::note
**注意**
この機能はDatabricksランタイム11.3以降が必要です。
:::

# ParquetやIcebergデータのインクリメンタルな取り込みのためにいつクローンを使うべきか

Databricksでは、レイクハウスにデータを取り込むための数多くのオプションを提供しています。以下のシチュエーションにおいてParquetやIcebergを取り込む際にクローンを使用することをお勧めします。

:::note
**注意**
*ソース*テーブルという用語は、クローンされるテーブルとデータファイルを指し、*ターゲット*テーブルはオペレーションによって作成、更新されるDeltaテーブルを指します。
:::

- ParquetやIcebergからDelta Lakeへのマイグレーションを実施しているが、ソーステーブルを使い続ける必要がある。
- 追加、更新、削除がなされるプロダクションソーステーブルとターゲットテーブル間の取り込みのみ動機を維持する必要がある。
- レポーティング、機械学習、バッチETLにおけるソースデータの[ACID準拠](https://docs.databricks.com/lakehouse/acid.html)のスナップショットを作成したいと考えている。

# クローンの構文はどのようなものか？

ParquetやIcebergに対するクローンは、Deltaテーブルのクローンに使うものと同じ基本構文を使用し、シャロークローンとディープクローンをサポートしています。詳細に関しては[クローンのタイプ](https://qiita.com/taka_yayoi/items/50c5a75caff8a6fb721d#%E3%82%AF%E3%83%AD%E3%83%BC%E3%83%B3%E3%81%AE%E3%82%BF%E3%82%A4%E3%83%97)をご覧ください。

多くのワークロードにおいてインクリメンタルなクローンを用いることをお勧めします。ParquetやIcebergに対するクローンではSQL構文を使用します。

:::note
**注意**
ParquetやIcebergに対するクローンでは、Deltaのクローンや変換とは異なる要件、保証となります。[ParquetやIcebergテーブルのクローンの要件と制限](#parquetやicebergテーブルのクローンの要件と制限)をご覧ください。
:::

ファイルパスを用いてParquetやIcebergのディープクローンを作成するには以下の構文を使います。

```sql:SQL
CREATE OR REPLACE TABLE <target_table_name> CLONE parquet.`/path/to/data`;

CREATE OR REPLACE TABLE <target_table_name> CLONE iceberg.`/path/to/data`;
```

ファイルパスを用いてParquetやIcebergのシャロークローンを作成するには以下の構文を使います。

```sql:SQL
CREATE OR REPLACE TABLE <target_table_name> SHALLOW CLONE parquet.`/path/to/data`;

CREATE OR REPLACE TABLE <target_table_name> SHALLOW CLONE iceberg.`/path/to/data`;
```

また、以下のサンプルのように、メタストアに登録されたParquetテーブルのディープクローンやシャロークローンを作成することもできます。

```sql:SQL
CREATE OR REPLACE TABLE <target_table_name> CLONE <source_table_name>;

CREATE OR REPLACE TABLE <target_table_name> SHALLOW CLONE <source_table_name>;
```

# ParquetやIcebergテーブルのクローンの要件と制限

ディープクローンにしてもシャロークローンにしても、クローンが実行された後にターゲットテーブルに適用された変更は、ソーステーブルに同期されません。クローンによるインクリメンタルな同期は一方向であり、ソーステーブルに対する変更は自動でターゲットのDeltaテーブルに適用されます。

ParquetやIcebergテーブルに対するクローンを使用する際には、以下の制限も適用されます。

- このオペレーションでは、ファイルレベルの統計情報は収集しません。このため、ターゲットテーブルではDelta Lakeのデータスキッピングのメリットを享受することができません。
- クローンする前に、パーティションを持つParquetテーブルをHiveメタストアのようなカタログに登録し、ソーステーブルと同じテーブル名を使用しなくてはなりません。パーティションを持つParquetテーブルに対してパスベースのクローン構文を使用することはできません。
- パーティション進化をおこなったIcebergテーブルをクローンすることはできません。
- Icebergテーブルにはパスのみを用いてアクセスすることができます。テーブル名はサポートされていません。
- Unity Catalogではシャロークローンをサポートしていません。


### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

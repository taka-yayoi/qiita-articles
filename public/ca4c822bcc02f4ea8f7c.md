---
title: Delta Lakeへの変換
tags:
  - Databricks
  - deltalake
private: false
updated_at: '2022-11-26T13:44:15+09:00'
id: ca4c822bcc02f4ea8f7c
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Convert to Delta Lake \| Databricks on AWS](https://docs.databricks.com/ingestion/convert-to-delta.html) [2022/11/15時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

SQLコマンド`CONVERT TO DELTA`は、ParquetやIcebergテーブルのDelta Lakeテーブルへの変換処理を実行します。ParquetやIcebergテーブルのDelta Lakeへのインクリメンタルな変換に関しては、[ParquetやIcebergからDelta Lakeへのインクリメンタルなクローン](https://qiita.com/taka_yayoi/items/bc3edb691c6f1fc7c79a)をご覧ください。

Unity Catalogでは、Unity Catalogで管理される外部ロケーションに格納されているParquetやIcebergテーブルの`CONVERT TO DELTA`コマンドをサポートしています。

Databricksレイクハウスのすべての機能を解放するために、既存のParquetデータファイルをUnity Catalogの外部テーブルとして設定し、Delta Lakeに変換することができます。

技術的なドキュメントに関しては、[CONVERT TO DELTA](https://docs.databricks.com/sql/language-manual/delta-convert-to-delta.html)をご覧ください。

# 外部ロケーションにあるParquetやIcebergファイルのディレクトリを変換する

:::note
**注意**
Icebergテーブルの変換は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。

Icebergテーブルの変換はDatabricksランタイム10.4以降でサポートされています。

Icebergメタストアテーブルの変換はサポートされていません。
:::

ストレージロケーションに対する書き込み権限を持っているのであれば、ParquetデータファイルのディレクトリをDelta Lakeテーブルに変換することができます。Unity Catalogによるアクセス設定に関しては、[Unity Catalogにおける外部ロケーションとストレージ認証情報の管理](https://qiita.com/taka_yayoi/items/18fee92365eee58e0b94)をご覧ください。

```sql:SQL
CONVERT TO DELTA parquet.`s3://my-bucket/parquet-data`;

CONVERT TO DELTA iceberg.`s3://my-bucket/iceberg-data`;
```

Unity Catalogの外部テーブルとして変換済みテーブルをロードするには、外部ロケーションに対する`CREATE TABLES`が必要となります。

:::note
**注意**
Databricksランタイム11.2以降では、`CONVERT TO DELTA`は自動でメタストアに登録されるテーブルのパーティショニング情報を推定するので、手動でパーティションを指定する必要はありません。
:::

# マネージドテーブル、外部テーブルをUnity CatalogのDelta Lakeに変換する

Unity Catalogでは、外部テーブルで多くのフォーマットをサポートしていますが、マネージドテーブルではDelta Lakeのみをサポートしています。マネージドのParquetテーブルを直接Unity CatalogのマネージドDelta Lakeテーブルに変換するには、[テーブルをUnity Catalogにアップグレードする](https://qiita.com/taka_yayoi/items/5e896b50b915b9de8fb3#%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%82%92unity-catalog%E3%81%AB%E3%82%A2%E3%83%83%E3%83%97%E3%82%B0%E3%83%AC%E3%83%BC%E3%83%89%E3%81%99%E3%82%8B)をご覧ください。

外部ParquetテーブルをUnity Catalogにアップグレードするには、[外部テーブルをUnity Catalogにアップグレードする](https://qiita.com/taka_yayoi/items/5e896b50b915b9de8fb3#%E5%A4%96%E9%83%A8%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%82%92unity-catalog%E3%81%AB%E3%82%A2%E3%83%83%E3%83%97%E3%82%B0%E3%83%AC%E3%83%BC%E3%83%89%E3%81%99%E3%82%8B)をご覧ください。

外部ParquetテーブルをUnity Catalogに登録すると、それを外部Delta Lakeテーブルに変換することができます。Parquetテーブルがパーティショニングされている場合には、パーティショニング情報を指定しなくてはならないことに注意してください。

```sql:SQL
CONVERT TO DELTA catalog_name.database_name.table_name;

CONVERT TO DELTA catalog_name.database_name.table_name PARTITIONED BY (date_updated DATE);
```

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Delta Live TablesパイプラインにおけるUnity Catalogの使用
tags:
  - Databricks
  - DeltaLiveTables
  - UnityCatalog
private: false
updated_at: '2023-06-21T09:25:20+09:00'
id: b5acc61a5c82e0e92dbb
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Use Unity Catalog with your Delta Live Tables pipelines \| Databricks on AWS](https://docs.databricks.com/delta-live-tables/unity-catalog.html) [2023/6/14時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**プレビュー**
Delta Live TablesのUnity Catalogサポートは[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

[Hiveメタストア](https://docs.databricks.com/delta-live-tables/publish.html)へのテーブル永続化のサポートに加え、以下を行うためにDelta Live Tablesパイプラインで[Unity Catalog](https://qiita.com/taka_yayoi/items/15aede468bdca58ec6a3)を活用することができます:

- パイプラインがテーブルを永続化するUnity Catalogを定義。
- Unity Catalogテーブルからのデータの読み込み。

お使いのワークスペースには、Unity Catalogを使用するパイプライン、Hiveメタストアを使用するパイプラインを格納することができます。しかし、単一のパイプラインでHiveメタストアとUnity Catalogの両方に書き込みを行うことはできず、既存のパイプラインをUnity Catalogを使うようにアップグレードすることはできません。Unity Catalogを使用していない既存のパイプラインはこのプレビューによる影響を受けず、引き続き設定されたストレージロケーションを用いてHiveメタストアにデータを永続化することができます。

このドキュメントで言及されていない限り、すべての既存データソースやDelta Live Tablesの機能はUnity Catalogを使用するパイプラインでもサポートされます。Unity Catalogを使用するパイプラインでも[Python](https://docs.databricks.com/delta-live-tables/python-ref.html)と[SQL](https://docs.databricks.com/delta-live-tables/sql-ref.html)のインタフェースの両方がサポートされます。

また、パイプラインで作成されテーブルはDatabricksランタイム12.2以降を使用している共有Unity CatalogクラスターやSQLウェアハウスからクエリーを実行することができます。シングルユーザー、分離なしクラスターからこのテーブルにクエリーを実行することはできません。

Unity Catalogパイプラインによって作成されたテーブルの権限を管理するには、[GRANTやREVOKE](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)を使用します。

# 要件

Delta Live TablesパイプラインからUnity Catalogのテーブルの作成には以下が必要となります。

- パイプラインが[プレビューチャンネル](https://docs.databricks.com/delta-live-tables/properties.html#config-settings)を使うように設定されいなくてはなりません。
- ターゲットカタログに対する`USE CATALOG`権限。
- パイプラインが[ライブテーブル](https://qiita.com/taka_yayoi/items/80ee29197d26e177bbeb#%E3%83%87%E3%83%BC%E3%82%BF%E3%82%BB%E3%83%83%E3%83%88)を作成する際、ターゲットスキーマにおける`CREATE MATERIALIZED VIEW`と`USE SCHEMA`権限。
- パイプラインが[ストリーミングライブテーブル](https://qiita.com/taka_yayoi/items/80ee29197d26e177bbeb#%E3%83%87%E3%83%BC%E3%82%BF%E3%82%BB%E3%83%83%E3%83%88)を作成する際、ターゲットスキーマにおける`CREATE TABLE`と`USE SCHEMA`権限。
- ターゲットスキーマがパイプライン設定で指定されていない場合、ターゲットカタログの最低一つのスキーマに対する`CREATE MATERIALIZED VIEW`と`USE SCHEMA`権限。

# 制限

Delta Live TablesでUnity Catalogを使用する際には以下の制限があります。

- Hiveメタストアを使用している既存のパイプラインをUnity Catalogを使用するようにアップグレードすることはできません。Hiveメタストアに書き込みを行う既存パイプラインを移行するには、新規にパイプラインを作成し、データソースから再度データを取り込む必要があります。
- initスクリプト、サードパーティのライブラリ、JARはサポートされていません。
- パイプラインによって書き込まれたストリーミングテーブルを変更するために、例えば、Databricks SQLのような外部クライアントからの以下のデータ操作言語(DML)のクエリーはサポートされていません:
    - `APPLY CHANGES`ストリーミングテーブルに対するすべてのDMLクエリー。
    - ストリーミングテーブルのスキーマを変更するすべてのDMLクエリー。
    - `INSERT OVERWRITE`と`MERGE`。
    - ストリーミングテーブルを所有していないユーザーから送信されるすべてのDMLクエリー。
- Delta Live Tablesパイプラインで作成されたマテリアライズドビューは、他のパイプラインや後段のノートブックのように当該パイプライン以外のストリーミングソースとして使用することはできません。
- Unity Catalogを使用しているパイプラインのオーナーを変更することはできません。
- マネージドストレージロケーションを指定するスキーマへの公開はサポートされていません。ターゲットカタログでストレージロケーションが指定されている場合、すべてのテーブルはカタログのストレージロケーションに格納され、そうではない場合、全てのテーブルはメタストアのルートストレージロケーションに格納されます。
- データエクスプローラーの**History**タブには、ストリーミングテーブルとマテリアライズドビューの履歴は表示されません。
- テーブルを定義する際、`LOCATION`プロパティはサポートされていません。
- Unity Catalogが有効化されたパイプラインをHiveメタストアに公開することはできません。
- Python UDFのサポートはプライベートプレビューです。この機能を有効化するには、Databricks担当者にお問い合わせください。UDFサポートが有効化され、パイプラインでPython UDFを使用するには、パイプラインのデフォルトクラスターとメンテナンスクラスターの両方で、カスタムクラスタータグ`"PythonUDF.enabled": "true"`を追加する必要があります。
- Unity Catalogに公開されたDelta Live Tablesのマテリアライズドビューやストリーミングテーブルで[Delta Sharing](https://docs.databricks.com/data-sharing/index.html)を使うことはできません。
- 複数のパイプラインのイベントログにアクセスするためのクエリーやパイプラインで`event log`の[table valued function](https://docs.databricks.com/delta-live-tables/observability.html#event-log-with-uc)を使用することはできません。

# 既存機能の変更点

DLTがUnity Catalogにデータを永続化するように設定されると、テーブルのライフサイクルはDelta Live Tablesパイプラインによって管理されます。パイプラインがテーブルのライフサイクルを管理するので:

- Delta Live Tablesパイプラインの定義からテーブルが削除されると、対応するマテリアライズドビューやストリーミングテーブルのエントリーは、次のパイプラインのアップデートの際にUnity Catalogから削除されます。実際のデータは一定期間保持されるので、誤って削除した場合にはリカバリーすることができます。パイプライン定義にマテリアライズドビューやストリーミングテーブルを再度追加することでデータをリカバリーすることができます。
- Delta Live Tablesパイプラインの削除は、当該パイプラインで定義されているすべてのテーブルを削除することになります。この変更によって、Delta Live TablesのUIはパイプラインの削除を確認するプロンプトを表示するようにアップデートされます。

# Delta Live TablesパイプラインからUnity Catalogへのテーブルの書き込み

Unity Catalogにテーブルを書き込むには、[パイプラインを作成](https://docs.databricks.com/delta-live-tables/tutorial-pipelines.html#create-pipeline)する際に、**Storage options**で**Unity Catalog**を選択し、**Catalog**ドロップダウンメニューでカタログを選択し、**Target schema**フィールドにデータベース名を指定します。

# Unity Catalogパイプラインへのデータの取り込み

Unity Catalogを使用するように設定されたパイプラインでは、以下からデータを読み込むことができます:

- Unity Catalogのマネージドテーブル、外部テーブル、ビュー、マテリアライズドビュー、ストリーミングテーブル。
- Hiveメタストアのテーブルやビュー。
- Unity Catalogの外部ロケーションから読み込むために`cloud_files()`関数を用いたAuto Loader。
- Apache KafkaやAmazon Kinesis。

Unity CatalogとHiveメタストアのテーブルからデータを読み込む例を以下に示します。

## Unity Catalogテーブルからのバッチ取り込み

```sql:SQL
CREATE OR REFRESH LIVE TABLE
  table_name
AS SELECT
  *
FROM
  my_catalog.my_schema.table1;
```

```py:Python
@dlt.table
def table_name():
  return spark.table("my_catalog.my_schema.table")
```

## Unity Catalogテーブルからの変更ストリーム

```sql:SQL
CREATE OR REFRESH STREAMING TABLE
  table_name
AS SELECT
  *
FROM
  STREAM(my_catalog.my_schema.table1);
```

```py:Python
@dlt.table
def table_name():
  return spark.readStream.table("my_catalog.my_schema.table")
```

## Hiveメタストアからのデータ取り込み

```sql:SQL
CREATE OR REFRESH LIVE TABLE
  table_name
AS SELECT
  *
FROM
  hive_metastore.some_schema.table;
```

```py:Python
@dlt.table
def table3():
  return spark.table("hive_metastore.some_schema.table")
```

## Auto Loaderからのデータ取り込み

```sql:SQL
CREATE OR REFRESH STREAMING LIVE TABLE
  table_name
AS SELECT
  *
FROM
  cloud_files(
    <path_to_uc_external_location>,
    "json"
  )
```

```py:Python
@dlt.table(table_properties={"quality": "bronze"})
def table_name():
  return (
     spark.readStream.format("cloudFiles")
     .option("cloudFiles.format", "json")
     .load(f"{path_to_uc_external_location}")
 )
```

# ライブテーブルの共有

デフォルトでは、パイプラインによって作成されたテーブルはパイプライン所有者によってのみクエリーを行うことができます。[GRANT](https://docs.databricks.com/sql/language-manual/security-grant.html)文を用いてテーブルにクエリーを行う権限を他のユーザーに付与したり、[REVOKE](https://docs.databricks.com/sql/language-manual/security-revoke.html)文を用いてクエリーの権限を剥奪することができます。Unity Catalogにおける権限の詳細は、[Manage privileges in Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)をご覧ください。

## ライブテーブルに対するselectの許可

```sql:SQL
GRANT SELECT ON TABLE
  my_catalog.my_schema.live_table
TO
  `user@databricks.com`
```

## ライブテーブルからのselect権限の剥奪

```sql:SQL
REVOKE SELECT ON TABLE
  my_catalog.my_schema.live_table
FROM
  `user@databricks.com`
```

# マテリアライズドビュー作成、テーブル権限の付与

```sql:SQL
GRANT CREATE { MATERIALIZED VIEW | TABLE } ON SCHEMA
  my_catalog.my_schema
TO
  { principal | user }
```

# パイプラインのリネージの参照

Delta Live Tablesパイプラインのテーブルにおけるリネージはデータエクスプローラで参照できます。Unity Catalogが有効化されたパイプラインにおけるマテリアライズドビューやストリーミングテーブルに関しては、データエクスプローラのUIは前段と後段のテーブルを表示します。リネージはパイプラインで定義されたテーブル間にのみ表示されます。パイプライン外で定義されたテーブルや、パイプラインで読み込まれるテーブルはデータエクスプローラのリネージUIには表示されません。Unity Catalogのリネージに関しては、[Unity Catalogによるデータリネージのキャプチャと参照](https://qiita.com/taka_yayoi/items/875f6684e26f13c6e48b)をご覧ください。

Unity Catalogが有効化されたDelta Live Tablesパイプラインにおけるマテリアライズドビューやストリーミングテーブルに関しては、データエクスプローラのリネージUIは、現在使用しているワークスペースから当該パイプラインにアクセスできる場合には、マテリアライズドビューやストリーミングテーブルを作成したパイプラインへのリンクも表示します。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

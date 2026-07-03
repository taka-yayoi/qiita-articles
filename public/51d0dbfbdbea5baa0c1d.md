---
title: Delta Live Tables SQLリファレンス
tags:
  - SQL
  - Databricks
  - DeltaLiveTables
private: false
updated_at: '2022-07-29T08:16:18+09:00'
id: 51d0dbfbdbea5baa0c1d
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Delta Live Tables SQL language reference \| Databricks on AWS](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-sql-ref.html) [2022/7/11時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本書では、Delta Live TablesのSQLプログラミングインタフェースの詳細とサンプルを説明します。完全なAPI仕様については、[SQL API仕様](#sql-api仕様)をご覧ください。

Python APIに関しては、[Delta Live Tables Pythonリファレンス](https://qiita.com/taka_yayoi/items/415687fa84e59de7a370)をご覧ください。

# SQLデータセット

SQLでビューやテーブルを作成するには`CREATE LIVE VIEW`あるいは`CREATE OR REFRESH LIVE TABLE`を使用します。外部データソースあるいはパイプラインで定義されているデータセットから読み込むことでデータセットを作成することができます。内部のデータセットから読み込むには、データセット名の前に`LIVE`キーワードを追加します。以下の例では、2つの異なるデータセットを定義しています：入力ソースとしてJSONファイルを受け取る`taxi_raw`というテーブルと、`taxi_raw`テーブルを入力とする`filtered_data`というテーブルです。

```sql:SQL
CREATE OR REFRESH LIVE TABLE taxi_raw
AS SELECT * FROM json.`/databricks-datasets/nyctaxi/sample/json/`

CREATE OR REFRESH LIVE TABLE filtered_data
AS SELECT
  ...
FROM LIVE.taxi_raw
```

Delta Live Tablesは、パイプラインで定義されているデータセット間の依存関係を自動でキャプチャし、アップデートを行う際に実行順序を決定するため、そして、パイプラインのイベントログでリネージュ情報を記録するために、この依存関係の情報を使用します。

ビューとテーブルの両方は以下のオプションのプロパティを持っています。

- `COMMENT`: 人間が理解できるデータセットの説明文です。
- [エクスペクテーション](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-expectations.html)によって強制されるデータ品質制約。

また、テーブルには自身のマテリアライゼーションのために追加の属性を持っています。

- `PARTITIONED BY`を用いてテーブルをどのように[パーティショニング](https://docs.delta.io/latest/best-practices.html#choose-the-right-partition-column)するのかを指定します。
- `TBLPROPERTIES`を用いてテーブルプロパティを設定できます。詳細は[テーブルプロパティ](#テーブルプロパティ)をご覧ください。
- `LOCATION`設定を用いてストレージの場所を設定します。デフォルトでは、`LOCATION`が設定されていない場合、テーブルデータはパイプラインのストレージの場所に格納されます。

テーブルとビューのプロパティの詳細については、[SQL API仕様](#sql-api仕様)をご覧下さい。

Spark設定を含むテーブルやビューの設定値を指定するには、`SET`を使用します。`SET`文の後にノートブックで定義されたすべてのテーブルやビューは、定義された値にアクセスすることができます。`SET`文で指定されたすべてのSpark設定は、SET文以降のすべてのテーブルやビューに対するSparkクエリーを実行する際に使用されます。クエリーで設定値を読み込むには、文字列内挿文法である`${}`を使用します。以下のサンプルでは、`startDate`というSpark設定を設定し、クエリーでその値を使用しています。

```sql:SQL
SET startDate='2020-01-01';

CREATE OR REFRESH LIVE TABLE filtered
AS SELECT * FROM src
WHERE date > ${startDate}
```

複数の設定値を指定するには、値ごとに`SET`文を使用します。

[Auto Loader](https://qiita.com/taka_yayoi/items/1bd6376b959a811dc6c3#auto-loader)や内部データセットのようなストリーミングソースからデータを読み込むには、`STREAMING LIVE`テーブルを定義します。

```sql:SQL
CREATE OR REFRESH STREAMING LIVE TABLE customers_bronze
AS SELECT * FROM cloud_files("/databricks-datasets/retail-org/customers/", "csv")

CREATE OR REFRESH STREAMING LIVE TABLE customers_silver
AS SELECT * FROM STREAM(LIVE.customers_bronze)
```

ストリーミングデータに関しては、[ストリーミングデータ処理](https://qiita.com/taka_yayoi/items/bb53dc31fbf7676e1f9c)をご覧ください。

# SQL API仕様

:::note info
**注意**
Delta Live TablesのSQLインタフェースには以下の制限があります。

- アイデンティティとジェネレーテッドカラムはサポートされていません。
- `PIVOT`句はサポートされていません。データセット定義における`PIVOT`文の利用は、非決定性のパイプラインのレーテンシーを引き起こします。
:::

## テーブルの作成

```sql:SQL
CREATE OR REFRESH [TEMPORARY] { STREAMING LIVE TABLE | LIVE TABLE } table_name
  [(
    [
    col_name1 col_type1 [ COMMENT col_comment1 ],
    col_name2 col_type2 [ COMMENT col_comment2 ],
    ...
    ]
    [
    CONSTRAINT expectation_name_1 EXPECT (expectation_expr1) [ON VIOLATION { FAIL UPDATE | DROP ROW }],
    CONSTRAINT expectation_name_2 EXPECT (expectation_expr2) [ON VIOLATION { FAIL UPDATE | DROP ROW }],
    ...
    ]
  )]
  [USING DELTA]
  [PARTITIONED BY (col_name1, col_name2, ... )]
  [LOCATION path]
  [COMMENT table_comment]
  [TBLPROPERTIES (key1 [ = ] val1, key2 [ = ] val2, ... )]
  AS select_statement
```

## ビューの作成

```sql:SQL
CREATE TEMPORARY [STREAMING] LIVE VIEW view_name
  [(
    [
    col_name1 [ COMMENT col_comment1 ],
    col_name2 [ COMMENT col_comment2 ],
    ...
    ]
    [
    CONSTRAINT expectation_name_1 EXPECT (expectation_expr1) [ON VIOLATION { FAIL UPDATE | DROP ROW }],
    CONSTRAINT expectation_name_2 EXPECT (expectation_expr2) [ON VIOLATION { FAIL UPDATE | DROP ROW }],
    ...
    ]
  )]
  [COMMENT view_comment]
  AS select_statement
```

## SQLプロパティ

| CREATE TABLE あるいは VIEW |
|:--|
|**TEMPORARY**<br>一時テーブルを作成します。このテーブルのメタデータは永続化されません。   |
|**STREAMING**<br>ストリームとして入力データセットを読み込むテーブルを作成します。入力データセットは、[Autor Loader](https://qiita.com/taka_yayoi/items/1bd6376b959a811dc6c3#auto-loader)や`STREAMING LIVE`テーブルのようなストリーミングデータソースである必要があります。   |
|**PARTITIONED BY**<br>テーブルをパーティショニングする際にオプションとして指定する1つ以上のカラムです。   |
|**LOCATION**<br>オプションで指定するテーブルデータを格納するストレージ上の場所です。指定しない場合、デフォルトではパイプラインのストレージ上の格納場所となります。   |
|**COMMENT**<br>オプションで指定するテーブルの説明文です。   |
|**TBLPROPERTIES**<br>テーブルに対するオプションの[テーブルプロパティ](#テーブルプロパティ)です。   |
|**select_statement**<br>テーブルに対するデータセットを定義するDelta Live Tablesのクエリーです。   |

| CONSTRAINT句 |
|:--|
|**EXPECT expectation_name**<br>`expectation_name`という名前のデータ品質制約を定義します。`ON VIOLATION`制約が定義されていない場合、制約に違反する行をターゲットのデータセットに追加します。|
|**ON VIOLATION**<br>違反した行に対するオプションのアクションです。<ul><li>`FAIL UPDATE`: 即座にパイプラインの実行を停止します。<li>`DROP ROW`: 行を削除し、処理を継続します。</ul>|

# テーブルプロパティ

[Delta Lake](https://qiita.com/taka_yayoi/items/47b58eb8696b278a3a82#%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%83%97%E3%83%AD%E3%83%91%E3%83%86%E3%82%A3)によってサポートされているテーブルプロパティに加え、以下のテーブルプロパティを設定することができます。

| テーブルプロパティ |
|:--|
|**pipelines.autoOptimize.managed**<br>デフォルト: `true`<br>このテーブルに対して自動でスケジュールされる最適化処理を有効化、無効化します。   |
|**pipelines.autoOptimize.zOrderCols**<br>デフォルト: None<br>このテーブルに対して実行するz-orderのカラム名のカンマ区切りのリストです。オプションです。   |
|**pipelines.reset.allowed**<br>デフォルト: `true`<br>このテーブルに対するフルリフレッシュを許可するかどうかを指定します。   |

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

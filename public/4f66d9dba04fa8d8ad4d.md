---
title: DatabricksにおけるSQLパラメーターの統合
tags:
  - Databricks
  - DatabricksSQL
private: false
updated_at: '2024-09-18T17:01:55+09:00'
id: 4f66d9dba04fa8d8ad4d
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Unifying Parameters Across Databricks \| Databricks Blog](https://www.databricks.com/blog/unifying-parameters-across-databricks)の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本日、SQLエディタにおける[名前付きパラメーターマーカー](https://docs.databricks.com/en/sql/language-manual/sql-ref-parameter-marker.html#named-parameter-markers)のサポートを発表できることを嬉しく思っています。この機能によって、構文を変更することなしにダッシュボードやノートブックに直接コピーして実行できる、パラメーター化されたコードをSQLエディタで記述できるようになります。これは、クエリー、ノートブック、ダッシュボードにおけるパラメーターを統合する我々のジャーニーの大きなマイルストーンとなります。

:::note info
**訳者註**
これまでは、SQLエディタでパラメーター化するには`{{ }}`という構文を用いていました。
:::

![](https://www.databricks.com/sites/default/files/inline-images/4-use-across-Databricks.gif?v=1726607840)

# 名前付きパラメーターマーカーの活用

パラメーターによって、データセットに対するクエリーの実行時に値を置き換えることが可能となり、日付や製品カテゴリーのような評価条件でデータをフィルタリングできるようになります。これは、SQLクエリーでデータを集計する前の効率的なクエリーや正確な分析につながることになります。

パラメーターマーカーは、クエリー、ノートブック、ダッシュボード、ワークフロー、そして、[SQL Execution API](https://docs.databricks.com/api/workspace/statementexecution)でサポートされます。これらは厳密な型定義が行われ、SQL文から指定されれる値を明確に分離することで、SQLインジェクション攻撃に対してより堅牢なものとなります。名前付きパラメーター構文は、`:parameter_name`あるいは`` :`parameter with a space` ``のように、アルファベットの頭にコロン`:`を追加するだけで使用できます。
![](https://www.databricks.com/sites/default/files/inline-images/2-Identifier-example.gif?v=1726607840)

カラム名やテーブル名のようなキーワードを指定するために、`identifier(:parameter_name)`のようにラッパーとして[identifier\(\)句](https://docs.databricks.com/en/sql/language-manual/sql-ref-names-identifier-clause.html)を使います。
![](https://www.databricks.com/sites/default/files/inline-images/2-Identifier-example_1.gif?v=1726611118)

**名前付きパラメーターマーカー構文で既存のパラメーターを更新することをお勧めします。** 自動でパラメーターを変換するアシスタントのアクションをまもなく提供する予定です。
![](https://www.databricks.com/sites/default/files/inline-images/2-Identifier-example_1.gif?v=1726611118)

# 一般的なユースケース

パラメーターが有用であるいくつかのユースケースを示します。

## 特定の時間フレームにあるレコードを選択できるように、クエリーにパラメーター化された日付レンジを追加

```sql
SELECT * FROM samples.nyctaxi.trips where tpep_pickup_datetime BETWEEN :start_date AND :end_date
```
![](https://www.databricks.com/sites/default/files/inline-images/5-date-range.gif?v=1726607840)

## カタログ、スキーマ、テーブルを動的に選択あるいは作成

```sql
SELECT * FROM IDENTIFIER(:catalog || '.' || :schema || '.' || :table)
```
![](https://www.databricks.com/sites/default/files/inline-images/6-select-table.gif?v=1726607840)

```sql
CREATE TABLE IDENTIFIER(:catalog || '.' || :schema || '.' || :table) AS SELECT 1;
```
![](https://www.databricks.com/sites/default/files/inline-images/7-Create-Table.gif?v=1726607840)


## パラメーターでスキーマを選択

```sql
USE SCHEMA IDENTIFIER(:selected_schema)
```
![](https://www.databricks.com/sites/default/files/inline-images/8-Use-schema.gif?v=1726607840)

## 電話番号のようなアウトプットを整形するためにテンプレート化された文字列をパラメーター化

```sql
SELECT format_string("(%d) %d", :area_code, :phone_number) as phone_number
```
![](https://www.databricks.com/sites/default/files/inline-images/9-templated-strings.gif?v=1726607840)

## 日、月、年でのロールアップのパラメーター化

```sql
SELECT DATE_TRUNC(:date_granularity, tpep_pickup_datetime) AS date_rollup, COUNT(*) AS total_trips FROM trips GROUP BY date_rollup
```
![](https://www.databricks.com/sites/default/files/inline-images/10-Rollup.gif?v=1726607840)

## 単一のクエリーで複数のパラメーター値を選択

```sql
SELECT * FROM trips WHERE

  array_contains(

    TRANSFORM(SPLIT(:list_parameter, ','), s -> TRIM(s)),

    dropoff_zip

  )
```
![](https://www.databricks.com/sites/default/files/inline-images/11-Multiple-param-values.gif?v=1726607840)

## 間もなく提供

以下のように、**日付範囲**や**複数値**を用いて、フィールドやパラメーターのフィルタリングに更なるシンプルさと柔軟性を提供しようとしています。

```sql
SELECT * FROM trips where tpep_pickup_datetime BETWEEN :date.min AND :date.max 
```

```sql
SELECT * FROM trips where WHERE array_contains(:zipcodes, dropoff_zip)
```

# 名前付きパラメーターマーカー構文を使い始める

クエリー、ノートブック、ダッシュボード、ワークフロー、SQL Execution APIにおける名前付きパラメーターマーカー構文は今から利用できます。フィードバックや質問がある場合には、sql-editor-feedback@databricks.com にコンタクトください。Databricksでパラメーターの活用をスタートする際の詳細なリソースについては、[ドキュメント](https://docs.databricks.com/ja/sql/user/queries/query-parameters.html)をご覧ください。

Databricks SQLについて学ぶには、[Webサイト](https://www.databricks.com/jp/product/databricks-sql)やドキュメントをご覧ください。また、[Databricks SQLの製品ツアー](https://www.databricks.com/resources/demos/tours/governance/dbsql)をチェックすることもできます。既存のウェアハウスを、優れたユーザー体験とコスト削減を実現する高性能かつサーバレスなデータウェアハウスに移行したいのであれば、Databricks SQLがソリューションとなります。[無料で試して見ましょう](https://databricks.com/jp/try-databricks)。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

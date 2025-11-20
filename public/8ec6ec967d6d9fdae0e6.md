---
title: Databricksにおける行フィルター、列マスクによるセンシティブなデータのフィルタリング
tags:
  - Databricks
private: false
updated_at: '2023-09-14T09:23:12+09:00'
id: 8ec6ec967d6d9fdae0e6
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Filter sensitive table data with row filters and column masks \| Databricks on AWS](https://docs.databricks.com/en/data-governance/unity-catalog/row-and-column-filters.html) [2023/9/11時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note
**プレビュー**
この機能は[パブリックプレビュー](https://docs.databricks.com/en/release-notes/release-types.html)です。
:::

本書では、お使いのテーブルのセンシティブなデータをフィルタリングするための行フィルター、列マスク、マッピングテーブルを使用するためのガイドと例を説明します。

# 行フィルターとは？

行フィルターによって、以降のクエリーがフィルター述語がtrueと評価された行のみを返却するとようにテーブルにフィルターを適用することができます。行フィルターはSQLユーザー定義関数(UDF)として実装されています。

行フィルターを作成するには、フィルターポリシーを定義するために最初に[SQL UDF](https://docs.databricks.com/en/udf/index.html)を記述し、`ALTER TABLE`文でテーブルに適用します。あるいは、初回の`CREATE TABLE`文でテーブルで行フィルターを指定することができます。それぞれのテーブルでは一つのみの行フィルターを定義することができます。行フィルターでは、対応するテーブルのあるカラムにバインディングされる0個以上の入力パラメーターを受け入れることができます。

# 行フィルターとダイナミックビューの違いは？

[ダイナミックビュー](https://docs.databricks.com/en/data-governance/unity-catalog/create-views.html#dynamic-view)は、1つ以上のソーステーブルに対して抽象化された読み取り専用のビューです。ユーザーはソーステーブルに直接アクセス権を持たなくてもダイナミックビューにアクセスすることができます。ダイナミックビューの作成によって、いかなるソーステーブルや同じスキーマにある他のテーブルやビューと名前が一致しない新たなテーブル名を定義することになります。

一方で、ターゲットテーブルに行フィルターや列マスクを関連づけることで、新たなテーブル名を導入することなしに、同じロジックをテーブル自身に適用します。以降のクエリーはオリジナルの名称を用いて、ターゲットテーブルを直接参照し続けることになります。

ダイナミックビューと行フィルターと列マスクはいずれも、テーブルに複雑なロジックを適用し、クエリーの実行時にフィルタリングの判断基準を処理することができます。

読み取り専用テーブルに対してフィルターやマスクのような変換ロジックを適用する必要がある場合や、ユーザーがダイナミックビューを参照することを許容できる場合にはダイナミックビューを使用しましょう。特定のデータにフィルタリングや計算表現を適用したいが、オリジナル名を用いたテーブルへのアクセスを提供したい場合には、行フィルターや列マスクを使いましょう。

# 行フィルターの文法

行フィルターを作成し、既存テーブルに追加するには以下の構文を使用します:

行フィルターの作成:

```sql:SQL
CREATE FUNCTION <function_name> (<parameter_name> <parameter_type>, ...)
RETURN {filter clause whose output must be a boolean};
```

テーブルに行フィルターを適用:

```sql:SQL
ALTER TABLE <table_name> SET ROW FILTER <function_name> ON (<column_name>, ...);
```

テーブルから行フィルターの削除:

```sql:SQL
ALTER TABLE <table_name> DROP ROW FILTER;
```

行フィルターの編集:

既存の関数を削除するには`DROP FUNCTION`文を実行し、置き換える際には`CREATE OR REPLACE FUNCTION`を使用します。

行フィルターの削除:

```sql:SQL
ALTER TABLE <table_name> DROP ROW FILTER;
DROP FUNCTION <function_name>;
```

:::note
**注意**
関数を削除する前に`ALTER TABLE ... DROP ROW FILTER`コマンドを実行してください。さもないと、テーブルにアクセスできなくなります。

このようにテーブルにアクセスできなくなった際には、`ALTER TABLE <table_name> DROP ROW FILTER;`を用いて、テーブルを変更し、関連のなくなった行フィルターの参照を削除してください。
:::

# 行フィルターの例

リージョン`US`でグループ`admin`のメンバーに適用されるSQLユーザー定義関数を作成します。

この関数を用いることで、グループ`admin`のメンバーはテーブルのすべてのレコードにアクセスできます。admin以外のユーザーによって関数が呼び出されると、`RETURN_IF`条件が失敗し、`region='US'`表現が評価され、`US`リージョンのレコードのみにテーブルがフィルタリングされます。

```sql:SQL
CREATE FUNCTION us_filter(region STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), true, region='US');
```

行フィルターとしてテーブルに関数を適用します。`sales`テーブルに対する以降のクエリーは行のサブセットを返却するようになります。

```sql:SQL
CREATE TABLE sales (region STRING, id INT) USING delta;
ALTER TABLE sales SET ROW FILTER us_filter ON (region);
```

行フィルターを無効化します。`sales`テーブルに対する以降のクエリーはテーブルのすべての行が返却されます。

```sql:SQL
ALTER TABLE sales DROP ROW FILTER;
```

`CREATE TABLE`分の一部として、行フィルターとして適用された関数を用いてテーブルを作成します。`sales`テーブルに対する以降のクエリーは行のサブセットを返却するようになります。

```sql:SQL
CREATE TABLE sales (region STRING, id INT) USING delta
WITH ROW FILTER us_filter ON (region);
```

# 列マスクとは？

列マスクによって、テーブルの列にマスキング関数を適用することができます。マスキング関数はクエリー実行時に評価され、ターゲット列のそれぞれの参照をマスキング関数の結果で置き換えます。多くのユースケースにおいては、列マスクはオリジナルの列の値を返却するのか、呼び出したユーザーのアイデンティティに基づいて検閲するのかを判定します。列マスクはSQL UDFで記述されるエクスプレッションです。

それぞれのテーブル列には、任意で一つのマスキング関数を適用することができます。マスキング関数は、入力としてマスクされていない列の値を受け取り、結果としてマスクされた値を返却します。マスキング関数の戻り値は、マスクされる列と同じ型である必要があります。また、マスキング関数は、マスキングのロジックで使用するための追加の列を入力として受け取ることができます。

列マスクを適用するには、関数を作成し、`ALTER TABLE`文を用いてテーブル列に適用します。あるいは、テーブルを作成する際にマスキング関数を適用することができます。

# 列マスクの文法

`MASK`句内では、すべてのDatabricksビルトインランタイム関数や他のユーザー定義関数を活用することができます。一般的なユースケースには、`current_user( )`を用いて関数を呼び出しているユーザーのアイデンティティの調査を行うことや、`is_account_group member( )`を用いてどのグループのメンバーであるかを判定することが含まれます。

列マスクの作成:

```sql:SQL
CREATE FUNCTION <function_name> (<parameter_name> <parameter_type>, ...)
RETURN {expression with the same type as the first parameter};
```

既存テーブルの列に列マスクを適用:

```sql:SQL
ALTER TABLE <table_name> ALTER COLUMN <col_name> SET MASK <mask_func_name> [USING COLUMNS <additional_columns>];
```

テーブルの列から列マスクを削除:

```sql:SQL
ALTER TABLE <table_name> ALTER COLUMN <column where mask is applied> DROP MASK;
```

列マスクの修正:

既存の関数には`DROP`を用いるか、`CREATE OR REPLACE TABLE`を使用します。

列マスクの削除:

```sql:SQL
ALTER TABLE <table_name> ALTER COLUMN <column where mask is applied> DROP MASK;
DROP FUNCTION <function_name>;
```

:::note
**注意**
関数を削除する前に`ALTER TABLE ... DROP ROW FILTER`コマンドを実行してください。さもないと、テーブルにアクセスできなくなります。

このようにテーブルにアクセスできなくなった際には、`ALTER TABLE <table_name> DROP MASK;`を用いて、テーブルを変更し、関連のなくなった列マスクの参照を削除してください。
:::

# 列マスクの例

SQLユーザー定義関数を作成します。この関数は、`admin`グループのメンバーに対して`ssn`列をマスクします。

```sql:SQL
CREATE FUNCTION ssn_mask(ssn STRING)
  RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), ssn, '****');
```

列マスクとしてテーブルに新たな関数を適用します。`ssn`列に対する以降のユーザークエリーは変換された値を返却するようになります。

```sql:SQL
CREATE TABLE users
  (region STRING, table_ssn STRING) USING delta;
ALTER TABLE users ALTER COLUMN table_ssn SET MASK ssn_mask;
```

列マスクを無効化します。以降の`ssn`列に対するユーザークエリーはオリジナルの値を返却するようになります。

```sql:SQL
ALTER TABLE users ALTER COLUMN ssn DROP MASK;
```

`CREATE TABLE`文の一部として、1ステップで列マスクとして適用される新たな関数を用いて別のテーブルを作成します。`ssn`列に対する以降のユーザークエリーは変換された値を返却するようになります。

```sql:SQL
CREATE TABLE region_to_ssn (
  region STRING,
  ssn STRING MASK ssn_mask)
USING delta;
```

# アクセスコントロールリストを作成するためのマッピングテーブルの活用

行レベルのセキュリティを実現するには、マッピングテーブルの定義(あるいはアクセスコントロールリスト)を検討します。それぞれのマッピングテーブルは、特定のユーザーやグループがオリジナルテーブルのどのデータ行にアクセスできるのかをエンコードする包括的なマッピングテーブルです。マッピングテーブルは、お使いのファクトテーブルに対する直接的なjoinを通じたシンプルなインテグレーションを提供するので有用なものです。

この方法論は、カスタム要件に対する数多くのユースケースに取り組む際に有益であることが示されています。例には以下のようなものがあります:

- 特定のユーザーグループに異なるルールを適用しつつも、ログインしたユーザーに基づいた制約を適用する。
- 様々なルールセットを必要とする組織構造のような複雑な階層構造の作成。
- 外部ソースシステムの複雑なセキュリティモデルの複製。

このようにマッピングテーブルを導入することで、これらの困難なシナリオに効果的に取り組むことができ、堅牢な行レベル、列レベルのセキュリティ実装を保証することができます。

# テーブルマッピングの例

現在のユーザーがリストにいるのかどうかをチェックするためにマッピングテーブルを活用します:

```sql:SQL
USE CATALOG main;
```

新たなマッピングテーブルを作成します:

```sql:SQL
DROP TABLE IF EXISTS valid_users;

CREATE TABLE valid_users(username string) USING delta;
INSERT INTO valid_users
VALUES
  ('fred@databricks.com'),
  ('barney@databricks.com');
```

新たなフィルターを作成します:

:::note
**注意**
呼び出しとして実行されるユーザーのコンテキスト(例えば、`CURRENT_USER`や`IS_MEMBER`関数)をチェックする関数を除いて、すべてのフィルターは定義ユーザーの権限で実行されます。
:::

この例では、関数が現在のユーザーが`valid_users`テーブルに存在するかどうかをチェックします。ユーザーが見つかると、関数はtrueを返却します。

```sql:SQL
DROP FUNCTION IF EXISTS row_filter;

CREATE FUNCTION row_filter()
  RETURN EXISTS(
    SELECT 1 FROM valid_users v
    WHERE v.username = CURRENT_USER()
);
```

以下の例では、テーブル作成時に行フィルターを適用します。また、`ALTER TABLE`文を用いて、後でフィルターを追加することができます。テーブル全体に適用する際には、`ON ()`構文を使用します。特定の行に対しては、`ON (row);`を使用します。

```sql:SQL
DROP TABLE IF EXISTS data_table;

CREATE TABLE data_table
  (x INT, y INT, z INT)
  USING delta
  WITH ROW FILTER row_filter ON ();

INSERT INTO data_table VALUES
  (1, 2, 3),
  (4, 5, 6),
  (7, 8, 9);
```

テーブルから行を取得します。これは、ユーザーが`valid_users`テーブルに存在する場合にのみデータを返却します。

```sql:SQL
SELECT * FROM data_table;
```

# サポート範囲

- Databricks SQLとSQL向けDatabricksノートブックはサポートされています。
- MODIFY権限を持つユーザーによるDatabricks Machine Learningコマンドはサポートされています。フィルターやマスクは、MODIFYやDELETEによって読み込まれるデータに適用されますが、(INSERTされるデータを含み)書き込まれるデータには適用されません。
- サポートされるフォーマット: DeltaとParquet。Parquetはマネージドテーブルあるいは外部テーブルのみがサポートされています。
- カラムマスクや行フィルターを持つテーブルに対するビューはサポートされています。
- スキーマにターゲットテーブルに対して適用される行フィルターや列マスクと互換性のある限り、Delta Lakeのチェンジデータフィードはサポートされます。
- 外部テーブル(Foreignテーブル)はサポートされています。

# 制限

- Databricksランタイム12.2 LTS以前では、行フィルターや列マスクはサポートされていません。これらのランタイムは安全に処理を失敗します。これは、これらのサポートされていないバージョンのランタイムでテーブルにアクセスしようとすると、データが返却されないことを意味します。
- 行フィルターや列マスクとしてPythonやScala UDFはサポートされていません。しかし、これらの定義がカタログで永続化されている限り、これらの関数を参照することは可能です(言い換えると、これはセッション固有ではありません)。
- Delta Sharingは。行レベルセキュリティや列マスクは動作しません。
- タイムトラベルは、行レベルセキュリティや列マスクとは動作しません。
- テーブルのサンプリングは、行レベルセキュリティや列マスクとは動作しません。
- ポリシーを持つテーブリに対するパスベースのアクセスは現時点ではサポートされていません。
- オリジナルのポリシーに対する循環参照を持つ行フィルターや列マスクのポリシーはサポートされていません。
- `MERGE`やシャロークローンはサポートされていません。

# シングルユーザークラスターの制限

シングルユーザークラスターからアクセスするすべてのテーブルには行フィルターや列カラムを追加しないでください。これは一般的にDatabricksジョブの文脈で行われます。このパブリックプレビューでは、フィルターやマスクが適用されるとシングルユーザークラスターからはテーブルにアクセスできなくなります。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

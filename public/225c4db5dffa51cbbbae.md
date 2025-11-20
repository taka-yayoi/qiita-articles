---
title: Databricksにおけるデータオブジェクトのアクセス権管理
tags:
  - Databricks
private: false
updated_at: '2021-07-03T19:51:13+09:00'
id: 225c4db5dffa51cbbbae
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Data object privileges \| Databricks on AWS](https://docs.databricks.com/security/access-control/table-acls/object-privileges.html) [2021/6/21時点]の翻訳です。

Databricksのデータガバナンスモデルによって、Spark SQLからデータへのアクセスに対してプログラムから許可、拒否、無効化することができます。このモデルによって、カタログ、データベース、ビュー、関数のようなオブジェクトに対するセキュアなアクセスコントロールが可能になります。また、任意のクエリーから生成される派生ビューに対してアクセス権を設定することで、きめ細かい(例えばテーブルの特定のサブセットに対して)アクセス権管理が可能になります。DatabricksのSQLクエリーアナライザは、テーブルアクセスコントロールが有効化されたDatabricksクラスターのランタイム、および、すべてのSQLエンドポイントでこれらのアクセスコントロールポリシーを強制します。

本書では、Databricksのデータガバナンスモデルを構成する、アクセス権、オブジェクト、オーナーシップルールを説明します。また、どのようにしてオブジェクトのアクセス権を設定、拒否、無効化するのかを説明します。

# 要件

使用する環境に応じてオブジェクトアクセス権管理の要件が異なります。

## Databricks Data Science & Engineering、およびDatabricks Machine Learning

- 管理者はワークスペースで[テーブルアクセスコントロールを有効化し強制](https://docs.databricks.com/administration-guide/access-control/table-acl.html)する必要があります。
- クラスターで[テーブルアクセスコントロールを有効化](https://qiita.com/taka_yayoi/items/a30b474cd07e2ef8a7eb#%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%82%B3%E3%83%B3%E3%83%88%E3%83%AD%E3%83%BC%E3%83%AB%E3%81%8C%E6%9C%89%E5%8A%B9%E5%8C%96%E3%81%95%E3%82%8C%E3%81%9F%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AE%E4%BD%9C%E6%88%90)する必要があります。

## Databricks SQL

- [管理者向けクイックスタートの要件](https://qiita.com/taka_yayoi/items/8b6154eb8bfe202951c6#%E8%A6%81%E4%BB%B6)を参照ください。

# データガバナンスモデル

このセクションでは、Databricksのデータガバナンスモデルを説明します。セキュリティ保護可能なオブジェクトへのアクセスはアクセス権によって制御されます。

## セキュリティで保護可能なオブジェクト

セキュリティで保護可能なオブジェクトには以下が含まれます：

- `CATALOG`: データカタログ全体へのアクセスをコントロールします。
    - `DATABASE`: データベースへのアクセスをコントロールします。
        - `TABLE`: マネージドあるいは外部テーブルへのアクセスをコントロールします。
        - `VIEW`: SQLビューへのアクセスをコントロールします。
        - `FUNCTION`: 名前付き関数へのアクセスをコントロールします。
- `ANONYMOUS FUNCTION`: [匿名あるいは一時関数](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-function.html)へのアクセスをコントロールします。

    > **注意**
    `FUNCTION`と`ANONYMOUS FUNCTION`はDatabricks SQLではサポートされていません。

- `ANY FILE`: 内部のファイルシステムへのアクセスをコントロールします。

    > **警告!**
    `ANY FILE`のアクセス権が許可されているユーザーは、ファイルシステムを直接参照することで、カタログ、データベース、テーブル、ビューに課せられている制限をバイバスできます。

## アクセス権

- `SELECT`: オブジェクトに対する読み取りアクセス権
- `CREATE `: オブジェクトを作成できるアクセス権(例えば、データベースにテーブルを作成)
- `MODIFY`: オブジェクトに対してデータを追加、削除、変更できるアクセス権
- `USAGE`: これ自身はアクセス権を付与しないが、データベースオブジェクトにおけるアクションを行うために必要になるアクセス権
- `READ_METADATA`: オブジェクト、及びメタデータを参照できるアクセス権
- `CREATE_NAMED_FUNCTION`: 既存のカタログ、データベースに名前付きUDFを作成できるアクセス権
- `MODIFY_CLASSPATH`: Sparkのクラスパスにファイルを追加できるアクセス権
- `ALL PRIVILEGES`: 全てのアクセス権(上述のアクセス権に変換されます)

> **注意**
Databricks SQLでは`CREATE_NAMED_FUNCTION`と`MODIFY_CLASSPATH`はサポートされていません。

### `USAGE`アクセス権

データベースオブジェクトにアクションを行う場合、ユーザーはアクションを実行するためのアクセス権に加えて、当該データベースに対する`USAGE`権限を有している必要があります。`USAGE`の要件を満足するためには、以下のいずれかに該当する必要があります。

- 管理者である
- データベースに対する`USAGE`権限を持つ、あるいは、データベースに対して`USAGE`権限を持つグループに属している
- `CATALOG`に対する`USAGE`権限を持つ、あるいは`USAGE`権限を持つグループに属している
- データベースのオーナーである、あるいはデータベースオーナーのグループに属している

データベース内のオブジェクトのオーナーであっても、使用するためには`USAGE`権限が必要となります。

例として、管理者は`finance`グループと`accounting`データベースと定義することができます。financeチームのみがデータベースを利用、共有できるようにするためには、管理者は以下のコマンドを実行します。

```sql:SQL
CREATE DATABASE accounting;
GRANT USAGE ON DATABASE accounting TO finance;
GRANT CREATE ON DATABASE accounting TO finance;
```

これらの権限によって、`finance`グループのメンバーはテーブル、ビューを`accounting`データベースに作成できますが、`accounting`データベースにおいて`USAGE`権限を持たないいかなるユーザーにこれらのテーブル、ビューを共有することはできません。

#### Databricks Data Science & EngineeringとDatabricks Runtimeにおける振る舞い

- Databricksランタイム7.3 LTS以降では、`USAGE`権限が強制されます。
- Databricksランタイム7.2以前では、`USAGE`権限が強制されません。
- 既存のワークロード関数を変更しないようにするには、`USAGE`が導入される前にテーブルアクセスコントロールを使用していたワークスペースにおいて、`users`グループに対して、`CATALOG`に対する`USAGE`権限を与えます。`USAGE`権限を活用したい場合には、`REVOKE USAGE ON CATALOG FROM users`を実行し、必要に応じて`GRANT USAGE ...`を実行します。

### アクセス権の階層構造

DatabricksにおけるSQLオブジェクトは階層的であり、アクセス権は継承されます。すなわち、`CATALOG`に対するアクセス権の許可、拒否は、自動的にカタログ内の全てのデータベースに対するアクセス権を許可、拒否します。同様に、`DATABASE`オブジェクトに対するアクセス権の許可は、データベース内の全てのオブジェクトに継承されます。

## オブジェクトのオーナーシップ

クラスターやSQLエンドポイントでテーブルアクセスコントロールを有効化した際、データベース、テーブル、ビュー、関数を作成したユーザーがオーナーになります。オーナーには全てのアクセス権が許可され、他のユーザーにアクセス権を許可することができます。

グループがオブジェクトのオーナーになることもでき、この場合、グループのすべてのメンバーがオーナーとみなされます。

オーナーシップは、派生するオブジェクトを他のユーザーに許可できるかどうかを決定します。例えば、ユーザーAがテーブルTを所有しており、ユーザーBにテーブルTの`SELECT`権限を付与したとします。ユーザーBはテーブルTにselectを実行できますが、ユーザーAがテーブルTのオーナーであるため、ユーザーBはユーザーCにテーブルTの`SELECT`権限を許可することはできません。さらに、ユーザーBはテーブルTに対するビューVを作成し、そのビューへのアクセス権をユーザーCに付与することで制限を回避することはできません。Databricksが、ユーザーCのビューVに対するアクセス権をチェックする際、Vのオーナーと背後にあるテーブルTのオーナーが同じかどうかをチェックします。オーナーが異なる場合、ユーザーCは背後のテーブルTに対する`SELECT`権限を有している必要があります。

クラスターにおけるテーブルアクセスコントロールが無効化された場合、データベース、テーブル、ビュー、関数が作成された際のオーナーは記録されません。オブジェクトのオーナーが存在するかどうかを確認するには、`SHOW GRANT ON <object-name>`を実行します。`ActionType OWN`のエントリーが存在しない場合には、オブジェクトにオーナーは存在しません。

### オブジェクトにオーナーを割り当てる

オブジェクトのオーナー、あるいは管理者は``ALTER <object> OWNER TO `<user-name>@<user-domain>.com`　``コマンドを用いてオブジェクトのオーナーシップを変更することができます。

```sql:SQL
ALTER DATABASE <database-name> OWNER TO `<user-name>@<user-domain>.com`
ALTER TABLE <table-name> OWNER TO `group_name`
ALTER VIEW <view-name> OWNER TO `<user-name>@<user-domain>.com`
```

## ユーザーとグループ

管理者とオーナーはアクセス権を[ユーザーとグループ](https://docs.databricks.com/administration-guide/users-groups/index.html)に許可できます。それぞれのユーザーは、Databricksにおけるユーザー名(多くの場合メールアドレスにマッピングされます)で識別されます。全てのユーザーは暗黙的に"All Users"グループ、SQLでは`users`に属しています。

> **注意**
ユーザーを指定する際にはシングルクォート(`' '`)ではなく、バッククォート( `` ` ` `` )で囲む必要があります。

## オペレーションとアクセス権

Databricksでは、管理者ユーザーは全てのオブジェクトのアクセス権を管理することができ、全てのセキュリティ保護が可能なオブジェクトに対する全てのアクセス権を有し、あらゆるオブジェクトのオーナーを変更することができます。オブジェクトのオーナーは当該オブジェクトに対してあらゆるアクションを実行することができ、当該オブジェクトに対するアクセス権を他のユーザーに許可することができ、他のユーザーにオブジェクトのオーナーシップを変更することができます。オーナーのアクセス権における唯一の制限は、データベース内のオブジェクトに対するものです。データベースのオブジェクトを操作するには、ユーザーは追加でデータベースにおける`USAGE`権限を有している必要があります。

以下のテーブルでは、SQL操作に必要なアクセス権を示しています。

> **注意**
- テーブル、ビュー、関数に対するアクセス権が求められる際は、常にデータベースにおける`USAGE`アクセス権も必要となります。
- コマンドでテーブルが参照される際、パスも同様に参照されます。このような場合、テーブルにおける他のアクセス権とデータベースの`USAGE`の代わりに、`ANY FILE`における`SELECT`あるいは`MODIFY`が必要となります。
- オブジェクトのオーナーシップはここでは`OWN`アクセス権として表現します。

| オペレーション | 必要なアクセス権 |
|:--|:--|
|[CLONE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-clone.html)   |クローン元のテーブルに対する`SELECT`、データベースにおける`CREATE`、テーブルを置き換える場合には`MODIFY`   |
|[COPY INTO](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-copy-into.html)   |パスからコピーする際には`ANY FILE`に対する`SELECT`、コピー先のテーブルに対する`MODIFY`   |
|[CREATE BLOOMFILTER INDEX](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-create-bloomfilter-index.html)   |インデックスを作成するテーブルに対する`OWN`   |
|[CREATE DATABASE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-database.html)   |`CATALOG`に対する`CREATE`   |
|[CREATE TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-table.html)   |`OWN`あるいは、データベースに対する`USAGE`と`CREATE`   |
|[CREATE VIEW](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-view.html)   |`OWN`あるいは、データベースに対する`USAGE`と`CREATE`   |
|[CREATE FUNCTION](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-create-function.html)   |`OWN`あるいは、データベースに対する`USAGE`と`CREATE_NAMED_FUNCTION`、リソースが指定された場合には`CATALOG`における`MODIFY_CLASSPATH`も必要   |
|[ALTER DATABASE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-alter-database.html)   |データベースにおける`OWN`   |
|[ALTER TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-alter-table.html)   |通常はテーブルに対する`OWN`、パーティションの追加、削除の際には`MODIFY`   |
|[ALTER VIEW](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-alter-view.html)   |ビューに対する`OWN`   |
|[DROP BLOOMFILTER INDEX](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-drop-bloomfilter-index.html)  |テーブルに対する`OWN`   |
|[DROP DATABASE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-drop-database.html)   |データベースに対する`OWN`   |
|[DROP TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-drop-table.html)   |テーブルに対する`OWN`   |
|[DROP VIEW](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-drop-view.html)   |ビューに対する`OWN`   |
|[DROP FUNCTION](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-drop-function.html)   |関数に対する`OWN`   |
|[DROP FUNCTION](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-drop-function.html)   |テーブルとビューに対する`READ_METADATA`   |
|[DESCRIBE TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-aux-describe-table.html)   |テーブルに対する`READ_METADATA`   |
|[DESCRIBE HISTORY](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-describe-history.html)   |テーブルに対する`OWN`   |
|[SELECT](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-qry-select.html)   |テーブルに対する`SELECT`   |
|[INSERT](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-dml-insert.html)   |テーブルに対する`MODIFY`   |
|[RESTORE TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-restore.html)   |テーブルに対する`MODIFY`   |
|[UPDATE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-update.html)   |テーブルに対する`MODIFY`   |
|[MERGE INTO](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-merge-into.html)   |テーブルに対する`MODIFY`   |
|[DELETE FROM](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-delete-from.html)   |テーブルに対する`MODIFY`   |
|[TRUNCATE TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-syntax-ddl-truncate-table.html)   |テーブルに対する`MODIFY`   |
|[OPTIMIZE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-optimize.html)   |テーブルに対する`MODIFY`   |
|[VACUUM](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-vacuum.html)   |テーブルに対する`MODIFY`   |
|[FSCK REPAIR TABLE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/delta-fsck.html)   |テーブルに対する`MODIFY`   |
|[MSCK](https://docs.databricks.com/spark/latest/spark-sql/language-manual/security-msck.html)   |テーブルに対する`OWN`   |
|[GRANT](https://docs.databricks.com/spark/latest/spark-sql/language-manual/security-grant.html)   |オブジェクトに対する`OWN`   |
|[SHOW GRANT](https://docs.databricks.com/spark/latest/spark-sql/language-manual/security-show-grant.html)   |オブジェクトに対する`OWN`、あるいはGRANT対象のユーザー   |
|[DENY](https://docs.databricks.com/spark/latest/spark-sql/language-manual/security-deny.html)   |オブジェクトに対する`OWN`   |
|[REVOKE](https://docs.databricks.com/spark/latest/spark-sql/language-manual/security-revoke.html)   |オブジェクトに対する`OWN`   |

> **重要!**
テーブルアクセスコントロールを使用する際、`DROP TABLE`コマンドは大文字小文字を区別します。テーブル名が小文字で、`DROP TABLE`が大文字、あるいは大文字小文字混在の場合には、`DROP TABLE`コマンドは失敗します。

# オブジェクトアクセス権の管理

オブジェクトのアクセス権を管理する際には、`GRANT`、`DENY`、`REVOKE`、`MSCK`、`SHOW GRANT`オペレーションを使用します。

> **注意**

> - オブジェクトのオーナーあるいは管理者が`GRANT`、`DENY`、`REVOKE`、`SHOW GRANT`オペレーションを実行することができます。しかし、管理者はオーナーの権限をDENYしたり、オーナーから権限をREVOKEすることはできません。
- オーナー、管理者ではないユーザは、必要な権限を与えられている場合にのみオペレーションを行うことができます。
- 全てのユーザーに対してアクセス権の許可、拒否、廃止を行う場合には、`TO`の後にキーワード`users`を指定します。例えば、

>    ```sql:SQL
GRANT SELECT ON ANY FILE TO users
```

## サンプル

```sql:SQL
GRANT SELECT ON DATABASE <database-name> TO `<user>@<domain-name>`
GRANT SELECT ON ANONYMOUS FUNCTION TO `<user>@<domain-name>`
GRANT SELECT ON ANY FILE TO `<user>@<domain-name>`

SHOW GRANT `<user>@<domain-name>` ON DATABASE <database-name>

DENY SELECT ON <table-name> TO `<user>@<domain-name>`

REVOKE ALL PRIVILEGES ON DATABASE default FROM `<user>@<domain-name>`
REVOKE SELECT ON <table-name> FROM `<user>@<domain-name>`

GRANT SELECT ON ANY FILE TO users
```

# 動的ビュー関数

Databricksには、ビュー定義の中に動的な行レベル、列レベルでのアクセス権を表現できる二つのユーザー関数があります。

- `current_user()`: 現在のユーザー名を返します。
- `is_member()`: 現在のユーザーが特定のDatabricks[グループ](https://docs.databricks.com/administration-guide/users-groups/groups.html)のメンバーかどうかを判定します。

> **注意**
Databricksランタイム7.3 LTS以降で利用できます。しかし、これらの関数をDatabricksランタイム7.3 LTSで使用する際には、[Spark config](https://docs.databricks.com/clusters/configure.html#spark-config)に`spark.databricks.userInfoFunctions.enabled true`を設定する必要があります。

両方の関数を用いて、ユーザーが適切なグループのメンバーかどうかを判別する以下の例を考えてみます。

```sql:SQL
-- Return: true if the user is a member and false if they are not
SELECT
  current_user as user,
-- Check to see if the current user is a member of the "Managers" group.
  is_member("Managers") as admin
```

管理者は単一のビューの中で、複数のユーザーとグループ対してきめ細かいアクセス権を設定することができ、このこことは、管理のオーバーヘッドを削減しつつも、表現豊か、かつパワフルなものとなります。

## 列レベルのアクセス権

動的ビューを通じて、特定のグループ、ユーザーが参照できる列を容易に制御できるようになります。`auditors`グループに属するユーザーのみが、`sales_raw`テーブルのemailアドレスを参照できる以下の例を考えてみます。解析の際、Saprkは`CASE`文をリテラルの`REDACTED`あるいは`email`カラムで置換します。この振る舞いによって、通常のSparkによるパフォーマンス最適化を利用することができます。

```sql:SQL
-- Alias the field 'email' to itself (as 'email') to prevent the
-- permission logic from showing up directly in the column name results.
CREATE VIEW sales_redacted AS
SELECT
  user_id,
  CASE WHEN
    is_member('auditors') THEN email
    ELSE 'REDACTED'
  END AS email,
  country,
  product,
  total
FROM sales_raw
```

## 行レベルのアクセス権

動的ビューを用いることで、行やフィールドレベルでアクセス権を適用することができます。`managers`グループに属するユーザーのみが、金額が$1,000,000.00より大きいトランザクションを参照できるようにする例を考えてみます。

```sql:SQL
CREATE VIEW sales_redacted AS
SELECT
  user_id,
  country,
  product,
  total
FROM sales_raw
WHERE
  CASE
    WHEN is_member('managers') THEN TRUE
    ELSE total <= 1000000
  END;
```

## データマスキング

これまでの例で示したように、適切なグループに属していないユーザーが特定の列を参照できないように、列レベルでのマスキングを実装することができます。これらのビューは標準的なSpark SQLですので、より複雑なSQL表現を用いて、より洗練されたマスキングを行うことができます。以下の例では、全てのユーザーはemailのドメインに対して分析をこなうことができますが、`auditors`グループのメンバーは、emailの全てを参照することができます。

```sql:SQL
-- The regexp_extract function takes an email address such as
-- user.x.lastname@example.com and extracts 'example', allowing
-- analysts to query the domain name

CREATE VIEW sales_redacted AS
SELECT
  user_id,
  region,
  CASE
    WHEN is_member('auditors') THEN email
    ELSE regexp_extract(email, '^.*@(.*)$', 1)
  END
  FROM sales_raw
```

# FAQ

## どうすれば全てのユーザーに対してアクセス権を許可、拒否、廃止することができますか？

`TO`、`FROM`のあとにキーワード`users`を指定します。

```sql:SQL
GRANT SELECT ON TABLE database.table TO users
```

## オブジェクトを作成しましたが、クエリー、ドロップ、変更ができません

このエラーは、テーブルアクセスコントロールを有効化せずに、クラスターやSQLエンドポイントでオブジェクトを作成したために発生している可能性があります。クラスターやSQLエンドポイントでテーブルアクセスコントロールが無効化された際には、データベース、テーブル、ビューが作成された際のオーナーは記録されません。管理者は以下のコマンドを用いてオブジェクトに対するオーナーを割り当てる必要があります。

```sql:SQL
ALTER [DATABASE | TABLE | VIEW] <object-name> OWNER TO `<user-name>@<user-domain>.com`;
```

## どうすれば、グローバル、ローカル一時ビューにアクセス権を設定できますか？

グローバル、ローカル一時ビューに対するアクセス権はサポートされていません。ローカル一時ビューは同じセッション内でのみ参照でき、`global_temp`データベースに作成されるビューはクラスター、SQLエンドポイントを共有する全てのユーザーが参照できます。しかし、一時ビューから参照されるテーブル、ビューに対するアクセス権は強制されます。

## どうすれば、複数のテーブルに対するユーザー、グループのアクセス権を一括で設定できますか？

一度に一つのオブジェクトに対してのみgrant、deny、revokeを適用することができます。データベースを介してユーザー・グループに複数のテーブルに対するアクセス権を設定することをお勧めします。データベースに対する`SELECT`権限の許可は、暗黙的にデータベースのテーブル、ビューに対する`SELECT`権限を許可することになります。例えば、データベースDがテーブルt1とt2を有しており、管理者が以下の`GRANT`コマンドを実行したとします。

```sql:SQL
GRANT USAGE, SELECT ON DATABASE D TO `<user>@<domain-name>`
```

プリンシパル`<user>@<domain-name>`はテーブルt1、t2に対してselectを行うことができ、将来的にデータベースDで作成されるテーブル、ビューに対しても同様のアクセス権が設定されます。

## ユーザーに対して、一つを除く全てのテーブルに対するアクセス権を付与することはできますか？

データベースに対する`SELECT`権限を付与し、アクセスを制限したい特定のテーブルに対する`SELECT`権限を拒否します。

```sql:SQL
GRANT USAGE, SELECT ON DATABASE D TO `<user>@<domain-name>`
DENY SELECT ON TABLE D.T TO `<user>@<domain-name>`
```

プリンシパル`<user>@<domain-name>`は、テーブルD.T以外の全てのテーブルに対してselectを実行できます。

## テーブルTのビューに対して`SELECT`権限を持っているユーザーが、そのビューに対して`SELECT`を行おうとしたらエラー`User does not have privilege SELECT on table`が発生しました

この一般的なエラーは以下のいずれかの理由によるものです:

- テーブルアクセスコントロールが有効化されていないクラスター、SQLエンドポイントで作成されたテーブルTにはオーナーが設定されていない。
- テーブルTのビューに対する`SELECT`権限を付与したユーザーは、テーブルTのオーナーではない、あるいは、当該ユーザーもまたテーブルTに対する`SELECT`権限を持たない。

ユーザーAのテーブルTがあるとします。AはテーブルTに対するビューV1を所持しており、BはテーブルTに対するビューV2を所持しているとします。

- ユーザAはビューV1に対する`SELECT`権限を持っていれば、V1に対してselectを実行できます。
- ユーザAがテーブルTに対する`SELECT`権限を持っており、かつ、ユーザーBがビューV2に対する`SELECT`権限を許可していれば、ビューV2に対してselectを実行できます。

[オブジェクトのオーナーシップ](#オブジェクトのオーナーシップ)で説明したように、これらの条件によって、オブジェクトのオーナーのみが当該オブジェクトへのアクセスを許可できることを保証します。 

## テーブルアクセスコントロールが有効化されているクラスターで、`sc.parallelize`を実行しようとしたらエラーになりました

テーブルアクセスコントロールが有効化されているクラスターでは、Spark SQLとPythonデータフレームAPIのみを使用できます。Databricksでは、RDD内のコードを調査、承認する手段がないため、RDD APIはセキュリティ上の理由から許可されません。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

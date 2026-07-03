---
title: DatabricksマネージドのDelta Sharing
tags:
  - Databricks
  - DeltaSharing
private: false
updated_at: '2022-08-29T09:21:16+09:00'
id: 8bdd7feed96ac8f206fe
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Databricks\-managed Delta Sharing \| Databricks on AWS](https://docs.databricks.com/data-sharing/delta-sharing/sharing-data.html) [2022/8/25時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

DatabricksマネージドのDelta Sharingを用いることで、データ提供者はデータを共有し、データ受信者は共有データにアクセスできるようになります。

データ提供者として、Databricksを使用していない受信者とデータを共有することができます。詳細に関しては[Delta Sharingを用いたデータ共有](https://qiita.com/taka_yayoi/items/3a53516c4434c0ee76f0)をご覧ください。自身のアカウント外のデータ受信者にデータを共有したい場合には、メタストアで外部Delta Sharingを有効化してください。同じアカウント内でデータを共有する際には、外部Delta Sharingを有効化する必要はありません。

データ受信者として、(例えば、自分の計算クラスターやAWS EMRなど)オープンな環境で共有データにアクセスすることができます。詳細に関しては、[Delta Sharingを用いて共有データにアクセスする](https://qiita.com/taka_yayoi/items/f45b77984c3ed4b6a0c0)をご覧ください。

# データ提供者向けユーザーガイド

このセクションでは、Delta Sharingのリレーションシップにおけるデータ提供者として理解すべきコンセプトとプロセスを説明します。

## データ提供者向けのコンセプト

- データ受信者(data recipient): データ受信者は、共有データにアクセスする現実世界のデータ受信者を表現するUnity Catalogメタストアにおけるオブジェクトです。受信者は複数の共有にアクセスすることができます。
- 共有(share): 共有はUnity Catalogメタストアで共有されるデータセットのコレクションです。メタストアには複数の共有があり、どの受信者がどの共有にアクセスできるのかを制御することができます。

![](https://docs.databricks.com/_images/diagram-1.png)

## 共有の管理

Delta Sharingにおいて共有は、グループとして共有したいメタストア内のテーブルのコレクションを含む名前付きオブジェクトです。共有には単一のメタストアからのテーブルのみを含めることができます。好きな時に共有に対してテーブルを追加、削除することができます。

```sql:SQL
USE CATALOG main;
USE default;
CREATE TABLE IF NOT EXISTS my_table (num Int, name String) USING DELTA PARTITIONED BY (num);
INSERT INTO my_table VALUES (1, "cat"), (1, "dog"), (2, "fish");

CREATE SHARE IF NOT EXISTS my_share;
ALTER SHARE my_share ADD TABLE my_table AS db0.t0;
```

## 受信者の管理

受信者は、共有データを利用する現実世界のデータ受信者のIDを表現する名前付きオブジェクトです。Databricksにおけるデータ受信者においては、受信者オブジェクトには、データにアクセスするためにDatabricksマネージドのDelta Sharingを使用していることを示す`DATABRICKS`というタイプの認証が設定されています。[データにアクセスするためにオープンソースコネクターとbearerトークンを使用している](https://qiita.com/taka_yayoi/items/f45b77984c3ed4b6a0c0)データ受信者に対しては、受信者オブジェクトには認証タイプ`TOKEN`が設定されます。

特に、受信者オブジェクトは特定のUnity Cataログメタストアのデータ受信者を表現します。`DATABRICKS`認証タイプの受信者が作成されると、特定のクラウドプラットフォーム、特定のリージョンのUnity Catalogメタストアと関連づけられます。データが共有されたこの受信者は、このメタストアにのみアクセスできることが保証されます。

一方、`TOKEN`認証タイプの受信者は、任意のオープンソースコネクターを用いて、任意の環境に存在することができ、どこからでもデータアクセスできるデータ受信者を表現します。

`DATABRICKS`認証タイプの受信者オブジェクトを管理する際は、いかなる認証情報を取り扱う必要はありません。DatabricksマネージドDelta SharingはIDの検証、認証、監査などの複雑なことすべてをハンドリングし、データ共有がセキュアであることを確実なものとします。

### Databricks認証タイプを用いた受信者の作成

共有のIDを用いて受信者を作成するために、SQLコマンド`CREATE RECIPIENT`を使用します。

```sql:SQL
CREATE RECIPIENT [IF NOT EXISTS] <recipient_name>
USING ID <sharing_identifier>
[COMMENT <comment>]
```

`<sharing_identifier>`はデータを共有したいデータ受信者によって所有されるUnity CatalogのグローバルなユニークなIDです。フォーマットは`<cloud>:<region>:<uuid>`となっています。サンプルは`aws:eu-west-1:b0c978c8-3e68-4cdf-94af-d05c120ed1ef`となります。
![](https://docs.databricks.com/_images/manage-recipients-example.png)

このフィールドは、共有識別子と呼ばれます。提供者は、Databricks-to-Databricksの受信者を作成するためにこの共有識別子を必要とします。
![](https://docs.databricks.com/_images/sharing-identifier.png)

### 受信者の参照および削除

受信者を参照、更新、削除するために以下のSQLコマンドを使用します。受信者が削除されると、データ受信者は共有データへのアクセスを表現しなくなります。

```sql:SQL
SHOW RECIPIENTS [LIKE <pattern>];
DESC RECIPIENT <recipient_name>;
DROP RECIPIENT [IF EXISTS] <recipient_name>;
```

## 受信者にデータを共有

共有と受信者の準備ができたら、受信者の共有へのアクセス権を許可するためにSQLコマンド`GRANT`と`REVOKE`を用いることで、容易にデータ共有を管理することができます。

受信者に共有へのアクセスを許可するには以下を実行します。

```sql:SQL
GRANT SELECT
ON SHARE <share_name>
TO RECIPIENT <recipient_name>;
```

アクセスを剥奪するには以下を実行します。

```sql:SQL
REVOKE SELECT
ON SHARE <share_name>
FROM RECIPIENT <recipient_name>;
```

共有に許可されている権限と、受信者に付与されている現在の権限を確認するには以下を実行します。

```sql:SQL
SHOW GRANT ON SHARE <share_name>;
SHOW GRANT TO RECIPIENT <recipient_name>;
```

# データ受信者向けユーザーガイド

以下のセクションでは、Delta Sharingリレーションシップにおけるデータ受信者として理解すべきコンセプトやプロセスを説明します。

## データ受信者向けコンセプト

- データ提供者(data provider): データ提供者はデータを共有する現実世界のデータ提供者を表現するUnity Catalogメタストアのオブジェクトです。
- 共有(share): 共有はデータ提供者によって共有されるデータセットのコレクションです。共有はデータ提供者に属し、内部のデータセットにアクセスする共有からカタログを作成することができます。

以下の図では、Unity Catalogメタストアの全てのDelta Sharingオブジェクトの全体的なビューとそれらの関係性を示しています。
![](https://docs.databricks.com/_images/diagram-2.png)

## お使いの共有IDを共有する

データ提供者がDatabricks上でDelta Sharingを通じてデータを共有するためには、共有データにアクセスするUnity CatalogメタストアのグローバルにユニークなIDを知る必要があります。`<cloud>:<region>:<uuid>`のフォーマットとなっています。デフォルトのSQL関数`CURRENT_METASTORE`を用いることで、グローバルにユニークなIDを取得することができます。
![](https://docs.databricks.com/_images/share-metastore.png)

## 提供者と彼らの共有を参照する

提供者は、あなたとデータを共有する現実世界のデータ提供者を表現する名前付きオブジェクトです。Databricksにおけるデータ提供者においては、提供者には`DATABRICKS`の認証タイプが与えられており、データを共有するためにDatabricksマネージドDelta Sharingを使用していることを示しています。データを共有するために、オープンソースプロトコルと受信者プロファイル認証を用いているデータ提供者に対しては、提供者オブジェクトには`DATABRICKS`認証が用いられます。

特に、提供者オブジェクトは特定のUnity Cataログメタストアのデータ提供者を表現します。提供者が、あなたがお使いのUnity Catalogメタストアに対してデータ共有を作成すると、提供者オブジェクトが自動的にメタストア配下に作成されます。SQLコマンド`SHOW PROVIDERS`を用いることで、Unity Catalogメタストア配下のデータ提供者を参照することができます。

```sql:SQL
SHOW PROVIDERS [LIKE <pattern>]
```

また、SQLコマンド`DESC PROVIDER`を用いることで、データ提供者によって所有されるUnity Catalogのクラウド、リージョン、メタストアUUIDのような詳細属性を参照することができます。

```sql:SQL
DESC PROVIDER <provider-name>
```

提供者オブジェクトには、共有データセットを含むゼロから複数の共有が含まれます。提供者オブジェクト配下で利用できる共有を参照するために、SQLコマンド`SHOW SHARES IN PROVIDER`を使用することができます。

```sql:SQL
SHOW SHARES IN PROVIDER <provider-name>
```

使い方のサンプルとなります。
![](https://docs.databricks.com/_images/view-providers.png)

## 共有内のデータにアクセスする

共有内のデータにアクセスするには、共有からカタログを作成する必要があります。

```sql:SQL
CREATE CATALOG [IF NOT EXISTS] <catalog-name>
USING SHARE <provider-name>.<share-name>;
```

共有から作成されたカタログはDelta Sharingカタログと呼ばれます。SQLコマンド`DESC CATALOG`を用いて`type`属性を参照することで、カタログのタイプを確認することができます。
![](https://docs.databricks.com/_images/access-data.png)

Unity Catalogメタストアにおける通常のカタログと同じように、Delta Sharingカタログを管理することができます。SQLコマンド`SHOW CATALOGS`, `DESC CATALOG`, `ALTER CATALOG`, `DROP CATALOG`を用いることでDelta Sharingカタログを参照、更新、削除することができます。

共有から作成されたDelta Sharingカタログ配下の3レベル名前空間構造は、通常のUnity Catalogのカタログと同じように`<catalog, schema, table>`となります。

共有カタログ配下のデータオブジェクト(スキーマ、テーブル)は読み取り専用であり、`DESC`, `SHOW`, `SELECT`のような読み込みオペレーションは実行できますが、`MODIFY`, `UPDATE`, `DROP`のような書き込み、更新オペレーションは実行できないことを意味します。**このルールの唯一の例外はデータオブジェクトのオーナーやメタストア管理者はデータオブジェクトのオーナーを他のユーザーやグループに更新することができます。**

使い方のサンプルは以下の通りとなります。

```sql:SQL
CREATE CATALOG vaccine USING SHARE world_health_org.vaccine_share;
DESC CATALOG vaccine;
USE CATALOG vaccine;
COMMENT ON CATALOG vaccine IS vaccine data shared by WHO;
DROP CATALOG vaccine;

SHOW SCHEMAS;
DESC SCHEMA vaccine_us;
USE SCHEMA vaccine_us;

SHOW TABLES;
DESC TABLE vaccine_us_distribution;
SELECT * FROM vaccine_us_distribution LIMIT 100;
```

## チェンジデータフィード(CDF)をクエリーする

テーブルのCDFが共有されると、さらに2つのタイプのクエリーがサポートされます。あるバージョンのテーブルデータをクエリーするために、`VERSION AS OF <version>`がサポートされます。`TIMESTAMP AS OF`はサポートされていません。

```sql:SQL
SELECT * FROM vaccine_us_distribution VERSION AS OF 3;
```

共有テーブルのCDFをクエリーするには以下を使います。

```sql:SQL
SELECT * FROM table_changes('vaccine.vaccine_us.vaccine_us_distribution', 0, 3);
SELECT * FROM table_changes('vaccine.vaccine_us.vaccine_us_distribution', "2022-01-01 00:00:00", "2022-02-01 00:00:00");
```

## Delta Sharingカタログ内のアクセス権を管理する

デフォルトでは、Delta Sharingカタログ配下のすべてのデータオブジェクトのオーナーは、カタログ作成者として設定されます。カタログのオーナーは特定のデータオブジェクトのオーナーシップを他のユーザー、グループに移譲することができます。Unity Catalogでは、データオブジェクトのオーナーはアクセス権とライフサイクルを管理することができます。

データオブジェクトのオーナーシップを他のユーザー、グループに転送するには、`ALTER … OWNER TO`コマンドを使用します。

```sql:SQL
GRANT USAGE ON CATALOG <catalog-name> TO  `<user-or-group>`;
REVOKE USAGE ON CATALOG  <catalog-name> FROM  `<user-or-group>`;

GRANT USAGE ON SCHEMA <schema-name> TO  `<user-or-group>`;
REVOKE USAGE ON SCHEMA  <schema-name> FROM  `<user-or-group>`;

GRANT SELECT ON TABLE <table-name> TO  `<user-or-group>`;
REVOKE SELECT ON TABLE  <table-name> FROM  `<user-or-group>`;
```

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

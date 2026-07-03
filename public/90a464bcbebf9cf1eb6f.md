---
title: Databricks SQLのセキュリティモデルとデータアクセスの概要
tags:
  - Databricks
  - DatabricksSQL
private: false
updated_at: '2021-12-28T11:50:01+09:00'
id: 90a464bcbebf9cf1eb6f
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Databricks SQL security model and data access overview \| Databricks on AWS](https://docs.databricks.com/sql/user/security/data-access-overview.html) [2021/9/14時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Databricks SQLのセキュリティモデルは、`GRANT`、`REVOKE`のような標準的なSQL文を用いたきめ細かいアクセス権を設定できるようにSQLデータベースにおいて確立されているセキュリティモデルをベースとしています。以下の図では、どのようにデータのセキュリティ保護が行われるかを説明しています。
![](https://docs.databricks.com/_images/security-model.png)

黄色のユーザーグループには**Table 1**と**View 1**にクエリーする権限が許可されています。これらのテーブルのファイル、ディレクトリは異なるデータセットから構成されています。この例では、**Table 1**のデータは**Dataset 1**と**Dataset 2**で管理されており、**View 1**のデータは**Dataset A**に存在しています。

利用開始した際、あるいは、単体のワークスペースでのみデータがアクセスされるようなシンプルなシナリオにおいては、ファイルやディレクトリをDatabricksファイルシステム(DBFS)に直接格納することができます。これらのファイル、ディレクトリは*マネージド*と呼ばれます。マネージドのデータへのアクセスを管理する際には、追加の認証情報を設定する必要はありません。

しかし、通常はファイルやディレクトリはクラウドストレージに格納されます。これらのファイル、ディレクトリは*アンマネージド*と呼ばれます。クラウドストレージのアンマネージドのデータにアクセスするためには、Databricksはクラウドストレージの認証情報を用いてクラウドプロバイダーの認証を受ける必要があります。以下の図では、**Dataset 1**と**Dataset 2**向けに**Credential 1**、**Dataset A**に対しては**Credential 2**を用いて、Databricksはクラウドプロバイダーの認証を受けています。Databricks管理者は、クラウドストレージのデータにアクセスするためにDatabricksが適切な認証情報を用いるように設定します。詳細については、本書の後半にある[クラウドストレージへのアクセスの概要](#クラウドストレージへのアクセスの概要)を参照ください。テーブル、ビューのユーザーは通常、認証情報を直接参照、使用はしません。

ユーザーとグループは、通常[SCIM](https://docs.databricks.com/administration-guide/users-groups/scim/index.html)を用いるなどして、アイデンティティプロバイダーで管理され、Databricksと同期されます。
![](https://docs.databricks.com/_images/idp.png)

以下のセクションでは、Databricksのテーブルアクセスコントロール、クラウドストレージへのアクセス設定、ユーザー、グループの管理を用いてデータに対するアクセスの管理方法の概要を説明します。

# テーブルアクセスコントロールの概要

Databricksのテーブルアクセスコントロールを用いることで、以下のオブジェクトのセキュリティ保護を行うことができます。これらを*セキュリティ保護可能オブジェクト*と呼びます。

- `CATALOG:` データカタログ全体に対するアクセスを制御します。
- `DATABASE:` データベースに対するアクセスを制御します。
- `TABLE:` マネージド、外部テーブルへのアクセスを制御します。
- `VIEW:` SQLビューへのアクセスを制御します。
- `ANY FILE:` 背後のファイルシステムへのアクセスを制御します。ANY FILEへのアクセスが許可されたユーザーは、直接ファイルシステムを読み込むことで、カタログ、データベース、テーブル、ビューに設定された制約をバイパスすることができます。

Databricks管理者とオブジェクトの所有者のみがセキュリティ保護可能オブジェクトに対するアクセスを許可することができます。Databricks SQL、あるいは、Data Science & Engineeringで[テーブルアクセスコントロールが有効化](https://docs.databricks.com/security/access-control/table-acls/table-acl.html)されたクラスターを用いてデータベース、テーブル、ビューを*作成*するユーザーが作成したオブジェクトの所有者となります。所有者には全ての権限が許可され、他のユーザーに権限を付与することができます。オブジェクトに所有者が存在しない場合、管理者がオブジェクトの所有者を設定することができます。以下の表は、それぞれのロールとアクセス権付与可能なオブジェクトをまとめたものです。

| ロール | 許可可能なオブジェクト |
|:--|:--|
|Databricks管理者   |カタログと背後のファイルシステムに存在する全てのオブジェクト   |
|カタログ所有者   |カタログの全てのオブジェクト   |
|データベース所有者   |データベースの全てのオブジェクト   |
|テーブル所有者   |テーブルのみ   |

詳細に関しては、[Databricksにおけるデータオブジェクトのアクセス権管理](https://qiita.com/taka_yayoi/items/225c4db5dffa51cbbbae)を参照ください。

# クラウドストレージへのアクセスの概要

> **注意**
Databricksの[マネージドテーブル](https://qiita.com/taka_yayoi/items/e7f6982dfbee7fc84894#%E3%83%9E%E3%83%8D%E3%83%BC%E3%82%B8%E3%83%89%E3%82%A2%E3%83%B3%E3%83%9E%E3%83%8D%E3%83%BC%E3%82%B8%E3%83%89%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB)を使用している場合には、クラウドストレージへのアクセスの設定は不要です。

クラウドストレージのデータをクエリーするには、Databricks管理者はIAMロールとインスタンスプロファイルを用いて、Databricks SQLからクラウドストレージへのアクセスを設定します。以下の図では、**Cloud Storage 1**と**Cloud Storage 2**にアクセスするために、インスタンスプロファイルにマッピングされたIAMロールが使用されます。
![](https://docs.databricks.com/_images/aws-storage1.png)

以下の3つのステップでクラウドストレージへのアクセスの設定を行います。

1. インスタンスプロファイルを作成するか、既存インスタンスプロファイルを再利用します。
1. インスタンスプロファイルにAWSのS3バケットへのアクセスを設定します。
1. クラウドストレージにアクセスできる[インスタンスプロファイル](https://docs.databricks.com/sql/admin/data-access-configuration.html#storage-access)をDatabricks SQLエンドポイントに設定します。

# ユーザー、グループの概要

Databricks管理者は、Data Science & Engineeringワークスペースで[ユーザーとグループを管理](https://docs.databricks.com/administration-guide/users-groups/)します。Databricks SQLにおいては、データのアクセス権管理が容易なので、ユーザーではなくグループを用いることをお勧めします。グループのセットアップには2つの選択肢があります。

- SCIM APIを用いて[Databricksとアイデンティティプロバイダー(IdP)を同期](https://docs.databricks.com/administration-guide/users-groups/scim/index.html)します。IdPを信頼できる唯一の情報源としつつも、Databricksでアイデンティティを利用できるのでこちらの選択肢をお勧めします。この図では、Azure Active DirectoryのユーザーとグループがDatabricks SQLと同期され、テーブルやビューのようなデータベースオブジェクトに対するセキュリティ保護を行うために`GRANT`文が使用されます。
![](https://docs.databricks.com/_images/scim-sync.png)

- SQL、UI、APIを用いて[Databricks上にグループを作成](https://docs.databricks.com/administration-guide/users-groups/groups.html)します。

# Howto

Databricks SQLの管理者はデータオブジェクトにアクセスするために新規ワークスペースを設定したり、データオブジェクトにアクセスするように設定済みのData Science & Engineeringワークスペースを使用することができます。以下のドキュメントではクラウドストレージへのアクセスを設定し、Data Science & EngineeringのセキュリティモデルをDatabricks SQLにマッピングするための詳細な手順を説明しています。

- [Configure access to cloud storage](https://docs.databricks.com/sql/user/security/cloud-storage-access.html)
- [Map Data Science & Engineering security models to Databricks SQL](https://docs.databricks.com/sql/user/security/map-dse-dbsql.html)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricks SCIMを用いたIAMクレディンシャルパススルーによるS3バケットへのアクセス
tags:
  - AWS
  - Databricks
private: false
updated_at: '2022-04-10T09:12:23+09:00'
id: 5ed1c07debb4fecd474e
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Access S3 buckets using IAM credential passthrough with Databricks SCIM \| Databricks on AWS](https://docs.databricks.com/security/credential-passthrough/iam-passthrough.html) [2021/12/3時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

IAMクレディンシャルパススルーを用いることで、Databricksへのログインで使用しているアイデンティティを用いて、DatabricksクラスターからS3バケットへの認証を自動で行うことができます。IAMクレディンシャルパススルーをお使いのクラスターで有効化すると、そのクラスターで実行するコマンドはあなたのアイデンティティを用いてS3にデータを読み書きすることができます。IAMクレディンシャルパススルーには、[インスタンスプロファイル](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)を用いたS3バケットへのセキュアなアクセスに比べて以下の2つのメリットがあります。

- IAMクレディンシャルパススルーを用いることで、常にデータのセキュリティを保持しながらも、異なるデータアクセスポリシーを持つ複数のユーザーがS3のデータにアクセスする1つのクラスター共有することができます。インスタンスプロファイルは1つの[IAMロール](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)としか関連づけることができません。このため、このロールとロールに割り当てられているデータアクセスポリシーを、Databricksクラスター上の全てのユーザーが共有することになります。
- IAMクレディンシャルパススルーはアイデンティティとユーザーを関連づけます。これによって、CloudTrailによるS3オブジェクトのロギングが可能となります。S3への全てのアクセスは、CloudTrailログ上でARNを通じて直接ユーザーに紐づけられます。

# 要件

- [プレミアムプラン](https://databricks.com/jp/product/aws-pricing)(あるいは2020/3/3以前にOperational Security packageを購買したお客様)
- 以下にアクセスできるAWS管理者
    - DatabricksデプロイメントのAWSアカウントのIAMロール、ポリシー
    - S3バケットのAWSアカウント
    - インスタンスプロファイルを設定できるDatabricks管理者へのアクセス

# メタインスタンスプロファイルのセットアップ

IAMクレディンシャルパススルーを使用するには最初に、ユーザーに割り当てるIAMロールに委任される、少なくとも一つの*メタインスタンスプロファイル*をセットアップする必要があります。

*IAMロール*は、AWS内でアイデンティティが何ができて何ができないかを規定するポリシーを持つAWSのアイデンティティです。*インスタンスプロファイル*は、EC2インスタンスが起動する際に、EC2インスタンスにロールの情報を引き渡す際に使用されるIAMロールのコンテナです。インスタンスプロファイルを用いることで、ノートブックに[AWSのキーを埋め込む](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)ことなしに、Databricksクラスターからデータにアクセスできるようになります。

インスタンスプロファイルはクラスターに対するロールの設定を非常にシンプルにしますが、インスタンスプロファイルは*1つのみ*のIAMロールとしか紐づけることができません。このため、このロールとロールに割り当てられているデータアクセスポリシーを、Databricksクラスター上の全てのユーザーが共有することになります。しかし、IAMロールは、他のIAMロールの委任を受けることや、自身で直接データにアクセスすることができます。異なるロールの委任を受けるために1つのロールに対するクレディンシャルを使用することを[ロールチェーニング](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html#iam-term-role-chaining)と呼びます。

IAMクレディンシャルパススルーを用いることで、管理者はインスタンスプロファイルが使用するIAMロールと、ユーザーがデータにアクセスするロールを分割することができます。Databricksでは、このインスタンスロールを*メタIAMロール*と呼び、データにアクセスするロールを*データIAMロール*と呼びます。インスタンスプロファイル同様に、*メタインスタンスプロファイル*はメタIAMロールのコンテナとなります。
![](https://docs.databricks.com/_images/meta-iam-role.png)

[SCIM API](https://docs.databricks.com/dev-tools/api/latest/scim/index.html)を用いて、ユーザーはデータIAMロールへのアクセスを許可されます。ロールをアイデンティティプロバイダーとマッピングしている場合には、これらのロールはDatabricks SCIM APIに同期されます。クレディンシャルパススルーとメタインスタンスプロファイルが設定されたクラスターを使用する際、あなたがアクセスできるデータIAMロールからのみ委任を受けることができます。これによって、データをセキュアに保ちつも、異なるデータアクセスポリシーを持つ複数のユーザーが1つのDatabricksクラスターを共有することができます。

このセクションでは、IAMクレディンシャルパススルーの有効化に必要なメタインスタンスプロファイルのセットアップ方法を説明します。

## ステップ1: IAMクレディンシャルパススルーのロールの設定

### データIAMロールの作成

既存のデータIAMロールあるいは、オプションとしてS3バケットにアクセスできるデータIAMロールを、[ステップ1 S3バケットにアクセスするためのインスタンスプロファイルを作成する](https://qiita.com/taka_yayoi/items/446c7971be354f88c679#%E3%82%B9%E3%83%86%E3%83%83%E3%83%971-s3%E3%83%90%E3%82%B1%E3%83%83%E3%83%88%E3%81%AB%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%81%99%E3%82%8B%E3%81%9F%E3%82%81%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%B3%E3%82%B9%E3%83%97%E3%83%AD%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B)、[ステップ2 接続先S3バケットのパケットポリシーを作成する](https://qiita.com/taka_yayoi/items/446c7971be354f88c679#%E3%82%B9%E3%83%86%E3%83%83%E3%83%972-%E6%8E%A5%E7%B6%9A%E5%85%88s3%E3%83%90%E3%82%B1%E3%83%83%E3%83%88%E3%81%AE%E3%83%91%E3%82%B1%E3%83%83%E3%83%88%E3%83%9D%E3%83%AA%E3%82%B7%E3%83%BC%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B)に従って作成します。

### メタIAMロールの設定

データIAMロールの委任を受けるメタIAMロールを設定します。

1. AWSコンソールで**IAM**サービスに移動します。
1. サイドバーの**Roles**をクリックします。
1. **Create role**をクリックします。
    1. **Select type of trusted entity**では**AWS**サービスを選択します。
    1. **EC2**サービスをクリックします。
1. **Next Permissions**をクリックします。
1. **Create Policy**をクリックします。新規ウィンドウが開きます。
    1. **JSON**タブをクリックします。
    1. 以下のポリシーをコピーし、`<account-id>`はお使いのAWSアカウントID、`<data-iam-role>`には上のセクションで設定したデータIAMロールの名前に設定します。
        ```json:JSON
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AssumeDataRoles",
              "Effect": "Allow",
              "Action": "sts:AssumeRole",
              "Resource": [
                "arn:aws:iam::<account-id>:role/<data-iam-role>"
              ]
            }
          ]
        }
        ```
    1. **Review Policy**をクリックします。
    1. Nameフィールドにはポリシーの名前を入力し**Create policy**をクリックします。
1. ロールウィンドウに戻り画面を更新します。
1. ポリシー名を検索し、ポリシー名の隣のチェックボックスを選択します。
1. **Next Tags**と**Next Review**をクリックします。
1. ロール名のフィールドにはメタIAMロールの名前を入力します。
1. **Create role**をクリックします。
1. ロールサマリーでは、**Instance Profile ARN**をコピーしておきます。

### メタIAMロールを信頼するようにデータIAMロールを設定

メタIAMロールがデータIAMロールの委任を受けられるようにするために、データロールによってメタロールが信頼されるようにしなくてはなりません。

1. AWSコンソールで**IAM**サービスに移動します。
1. サイドバーの**Roles**をクリックします。
1. 以前のステップで作成したデータロールを検索し、クリックしてロールの詳細ページに移動します。
1. **Trust relationships**タブをクリックし、設定されていない場合には以下の文を追加します。

```json:JSON
 {
   "Version": "2012-10-17",
   "Statement": [
     {
       "Effect": "Allow",
       "Principal": {
         "AWS": "arn:aws:iam::<account-id>:role/<meta-iam-role>"
       },
       "Action": "sts:AssumeRole"
     }
   ]
 }
```

## ステップ2: Databricks上でメタインスタンスプロファイルを設定

このセクションでは、Databricksどのようにメタインスタンスプロファイルを設定するのかを説明します。

### Databricksデプロイメントで使用するIAMロールの特定

1. [アカウントコンソール](https://docs.databricks.com/administration-guide/account-settings/account-console.html)に移動します。
1. **AWS Account**タブをクリックします。
1. Role ARNの最後にあるロール名をメモしておきます。ここでは`testco-role`となります。
![](https://docs.databricks.com/_images/role-arn1.png)

### Databricksデプロイメントで使用するIAMロールのポリシーの修正

1. AWSコンソールで**IAM**サービスに移動します。
1. サイドバーの**Roles**をクリックします。
1. 以前のセクションでメモしたロールを編集します。
1. ロールにアタッチされているポリシーをクリックします。
1. DatabricksのSparkクラスターのEC2インスタンスが、[メタIAMロールの設定](#メタiamロールの設定)で作成したメタインスタンスプロファイルを使用できようにポリシーを修正します。サンプルについては、[ステップ4 S3 IAMロールをEC2ポリシーに追加する](https://qiita.com/taka_yayoi/items/446c7971be354f88c679#%E3%82%B9%E3%83%86%E3%83%83%E3%83%974-s3-iam%E3%83%AD%E3%83%BC%E3%83%AB%E3%82%92ec2%E3%83%9D%E3%83%AA%E3%82%B7%E3%83%BC%E3%81%AB%E8%BF%BD%E5%8A%A0%E3%81%99%E3%82%8B)をご覧ください。
1. **Review policy**、**Save Changes**をクリックします。

### Databricksにメタインスタンスプロファイルを追加

1. [Adminコンソール](https://docs.databricks.com/administration-guide/admin-console.html)に移動します。
1. **Instance Profiles**タブを選択します。
1. **Add Instance Profile**をクリックします。ダイアログが表示されます。
1. [メタIAMロールの設定](#メタiamロールの設定)のメタIAMロールに対応するインスタンスプロファイルARNを貼り付けます。
1. **Meta Instance Profile**チェックボックスをチェックし、**Add**をクリックします。
![](https://docs.databricks.com/_images/add-instance-profile.png)
1. オプションで、このメタインスタンスプロファイルでクラスターを起動できるユーザーを指定します。
![](https://docs.databricks.com/_images/configure-instance-profile.png)

## ステップ3: DatabricksユーザーにIAMロールのアクセス権をアタッチ

IAMロールに対するユーザーのマッピングを管理する方法は2つあります。

- Databricks内で[SCIM Users API](https://docs.databricks.com/dev-tools/api/latest/scim/scim-users.html#add-role-to-user)か[SCIM Groups API](https://docs.databricks.com/dev-tools/api/latest/scim/scim-groups.html#add-role-to-group)を使用する。
- [アイデンティティプロバイダー](https://docs.databricks.com/security/credential-passthrough/iam-federation.html)で管理する。これにより、データアクセスを集中管理し、SAML 2.0アイデンティティ統合を通じてDatabricksクラスターに対して直接これらの権限を引き渡すことができます。

お使いのワークスペースでどちらのマッピング手段が適しているのかを決断するには、以下の表を参照ください。

| 要件 | SCIM | アイデンティティプロバイダー |
|:--|:--|:--|
|Databricksへのシングルサインオン   |  No | Yes  |
|AWSアイデンティティプロバイダーの設定   | No  | Yes  |
|メタインスタンスプロファイルの設定   | Yes  | Yes  |
|Databricks管理者   | Yes  | Yes  |
|AWS管理者   | Yes  |  Yes |
|アイデンティティプロバイダー管理者   | No  | Yes  |

メタインスタンスプロファイルが設定されたクラスターを起動する際、クラスターはあなたのアイデンティティをパススルーし、あなたがアクセスできるデータIAMロールからのみの委任を受けます。管理者は、ロールに対するアクセス権を設定するには、[SCIM API](https://docs.databricks.com/dev-tools/api/latest/scim/index.html)を使ってデータIAMロールに対するユーザーのアクセス権を許可する必要があります。

:::note info
**注意**
お使いのアイデンティティプロバイダーでロールのマッピングを管理している場合、これらのロールはSCIMでマッピングされた全てのロールを上書きするので、ユーザートロールを直接マッピングするべきではありません。[Step 6: Optionally configure Databricks to synchronize role mappings from SAML to SCIM](https://docs.databricks.com/security/credential-passthrough/iam-federation.html#sync-role-mappings-scim)をご覧ください。
:::

# IAMクレディンシャルパススルークラスターの起動

クレディンシャルパススルーが設定されたクラスターの起動プロセスは、クラスターモードによって異なります。

## ハイコンカレンシークラスターでクレディンシャルパススルーを有効化

ハイコンカレンシークラスターは複数ユーザーで共有することができます。パススルーが設定されている場合、PythonとSQLのみがサポートされます。

1. クラスターを作成する際、**Cluster Mode**を[High Concurrency](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#high-concurrency%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC)に設定します。
1. Databricksランタイムバージョン6.1以降を選択します。
1. **Advanced Options**を展開し、**Enable credential passthrough for user-level data access and only allow Python and SQL commands**を選択します。
![](https://docs.databricks.com/_images/iam-role-passthrough.png)
1. **Instances**タブをクリックします。**Instance Profile**ドロップダウンから、[Databricksにメタインスタンスプロファイルを追加](#databricksにメタインスタンスプロファイルを追加)で作成したメタインスタンスプロファイルを選択します。
![](https://docs.databricks.com/_images/select-instance-profile.png)

## スタンダードクラスターでIAMクレディンシャルパススルーを有効化

スタンダードクラスターでのクレディンシャルパススルーは、Databricksランタイム6.0以降でサポートされており、単一のユーザーに限定されます。スタンダードクラスターでは、Python、SQL、Scala、Rがサポートされています。Databricksランタイム10.1以降ではsparklyrもサポートされます。

クラスター作成時にユーザーを割り当てる必要がありますが、クラスターに対して**Can Manage**権限を持つユーザーであれば、いつでも元のユーザーから別のユーザーに切り替えることができます。

:::note warn
**重要！**
クラスターに割り当てられるユーザーは、クラスターでコマンドを実行できるように少なくとも**Can Attach To**権限を持っている必要があります。管理者とクラスターの作成者は**Can Manage**権限を持っていますが、割り当てられたクラスターユーザー出ない場合は、クラスターでコマンドを実行することはできません。
:::

1. クラスターを作成する際、**Cluster Mode**を[Standard](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#standard%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC)に設定します。
1. Databricksランタイムバージョン6.1以降を選択します。
1. **Advanced Options**を展開し、**Enable credential passthrough for user-level data access**を選択します。
![](https://docs.databricks.com/_images/iam-role-passthrough.png)
1. **Single User Access**ドロップダウンからユーザー名を選択します。
![](https://docs.databricks.com/_images/single-user-access.png)
1. **Instances**タブをクリックします。**Instance Profile**ドロップダウンから、[Databricksにメタインスタンスプロファイルを追加](#databricksにメタインスタンスプロファイルを追加)で作成したメタインスタンスプロファイルを選択します。
![](https://docs.databricks.com/_images/select-instance-profile.png)

# IAMクレディンシャルパススルーを用いたS3へのアクセス

ロールの委任を受けることでクレディンシャルパススルーを用いるか、直接S3にアクセスするか、S3バケットをマウントし、マウントを通じてデータにアクセするためにロールを用いることで、S3にアクセスすることができます。

## クレディンシャルパススルーを用いたS3へのデータの読み書き

S3に対してデータの読み書きを行います。

```py:Python
dbutils.credentials.assumeRole("arn:aws:iam::xxxxxxxx:role/<data-iam-role>")
spark.read.csv("s3a://prod-foobar/sampledata.csv")
spark.range(1000).write.mode("overwrite").save("s3a://prod-foobar/sampledata.parquet")
```

```r:R
dbutils.credentials.assumeRole("arn:aws:iam::xxxxxxxx:role/<data-iam-role>")

# SparkR
library(SparkR)
sparkR.session()
read.df("s3a://prod-foobar/sampledata.csv", source = "csv")
write.df(as.DataFrame(data.frame(1:1000)), path="s3a://prod-foobar/sampledata.parquet", source = "parquet", mode = "overwrite")

# sparklyr
library(sparklyr)
sc <- spark_connect(method = "databricks")
sc %>% spark_read_csv("s3a://prod-foobar/sampledata.csv")
sc %>% sdf_len(1000) %>% spark_write_parquet("s3a://prod-foobar/sampledata.parquet", mode = "overwrite")
```

ロールを指定して`dbutils`を使用します。

```py:Python
dbutils.credentials.assumeRole("arn:aws:iam::xxxxxxxx:role/<data-iam-role>")
dbutils.fs.ls("s3a://bucketA/")
```

```r:R
dbutils.credentials.assumeRole("arn:aws:iam::xxxxxxxx:role/<data-iam-role>")
dbutils.fs.ls("s3a://bucketA/")
```

他の`dbutils.credentials`メソッドについては、[Credentials utility \(dbutils\.credentials\)](https://docs.databricks.com/dev-tools/databricks-utils.html#dbutils-credentials)を参照ください。

## IAMクレディンシャルパススルーを用いたDBFSへのS3バケットのマウント

異なるバケットやプレフィックスが異なるロールを必要とするようなより高度なシナリオにおいては、特定のバケットパスにアクセスする際に使用するロールを指定するためにDatabricksバケットマウントを使うのが便利です。

IAMクレディンシャルパススルーが設定されたクラスターを用いてデータをマウントすると、マウントポイントに対するすべての読み書き処理はマウントポイントに対して認証を受けるためにあなたの認証情報を使用します。このマウントポイントは他のユーザーも参照できますが、以下のユーザーのみが読み書きを行うことができます。

- IAMデータロールを通じて背後のS3ストレージアカウントへのアクセス権を持っている。
- IAMクレディンシャルパススルーが有効化されているクラスターを使用している。

```py:Python
dbutils.fs.mount(
  "s3a://<s3-bucket>/data/confidential",
  "/mnt/confidential-data",
  extra_configs = {
    "fs.s3a.credentialsType": "Custom",
    "fs.s3a.credentialsType.customClass": "com.databricks.backend.daemon.driver.aws.AwsCredentialContextTokenProvider",
    "fs.s3a.stsAssumeRole.arn": "arn:aws:iam::xxxxxxxx:role/<confidential-data-role>"
})
```

# IAMクレディンシャルパススルーを用いたジョブによるS3データへのアクセス

ジョブでクレディンシャルパススルーを用いてS3にアクセスするためには、新規あるいは既存クラスターを選択する際に、[IAMクレディンシャルパススルークラスターを起動](#iamクレディンシャルパススルークラスターの起動)するようにクラスターを設定します。
![](https://docs.databricks.com/_images/select-instance-profile.png)

クラスターはジョブのオーナーに対して許可されたロールのみから委任を受けるので、許可されたロールがアクセスできるS3のデータにアクセスできるようになります。

# IAMクレディンシャルパススルーを用いたJDBC、ODBCクライアントによるS3データへのアクセス

JDBC、ODBCクライアントを用いてIAMクレディンシャルパススルーによるS3データへのアクセスを行うには、[IAMクレディンシャルパススルークラスターを起動](#iamクレディンシャルパススルークラスターの起動)するようにクラスターを設定し、クライアントからこのクラスターに接続します。クラスターは接続ユーザーに対して許可されたロールのみから委任を受けるので、許可されたロールがアクセスできるS3のデータにアクセスできるようになります。

SQLクエリーでロールを指定するには、以下を実行します。

```sql:SQL
SET spark.databricks.credentials.assumed.role=arn:aws:iam::XXXX:role/<data-iam-role>;

-- Access the bucket which <my-role> has permission to access
SELECT count(*) from csv.`s3://my-bucket/test.csv`;
```

# 既知の制限

IAMクレディンシャルパススルーでは以下の機能はサポートされていません。

- `$fs` (代わりに[dbutils\.fs](https://docs.databricks.com/dev-tools/databricks-utils.html#dbutils-fs)を使ってください)
- [テーブルアクセスコントロール](https://qiita.com/taka_yayoi/items/f0b999e69b9fef5065d8)
- SparkContext (`sc`) と SparkSession (`spark`)オブジェクトに対する以下のメソッド
    - すでに推奨されないメソッド
    - 非管理者ユーザーがScalaコードを呼び出せる`addFile()`や`addJar()`のようなメソッド
    - S3以外のファイルシステムにアクセスする全てのメソッド
    - 古いHadoop API(`hadoopFile()`と`hadoopRDD()`)
    - Streaming API。これはストリームが稼働中にパススルーされたクレディンシャルが期限切れになる場合があるためです。
- クラスターのインスタンスプロファイルのダウンロード権限を必要とするクラスターライブラリ。DBFSパスを使うライブラリのみがサポートされています。
- Databricksランタイム7.3LTS以降でのみ利用できる[High Concurrency](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#high-concurrency%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC)上の[Databricks Connect](https://qiita.com/taka_yayoi/items/a9781c0a871a5a4fcf2e)
- [MLflow](https://qiita.com/taka_yayoi/items/1a4e82f7e20c56ba4f72)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

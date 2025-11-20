---
title: Azure DatabricksからのAWS S3へのアクセス
tags:
  - AWS
  - S3
  - Databricks
  - AzureDatabricks
private: false
updated_at: '2024-05-21T11:32:50+09:00'
id: bf7a5cb3444cab5d8da1
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらの手順をウォークスルーします。

https://learn.microsoft.com/ja-jp/azure/databricks/connect/storage/amazon-s3

こちらも参考にしています。

https://medium.com/@malavansa/azure-databricks-and-aws-s3-storage-92cf03636c9

:::note warn
**警告！**
クラウド横断での接続を行う構成ですので、以下の点には注意してください。

- アクセスに用いる認証情報は厳重に管理してください。
- クラウド間通信のコストが発生することに注意してください。
:::

# AWS側での作業

## S3バケットの作成

`taka-bucket-from-azure`というS3バケットを作成します。**S3ブロックパブリックアクセス**は有効化してください。
![Screenshot 2024-05-21 at 9.39.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/44a61e44-52e1-900d-2e58-0569c3ddc9e3.png)

https://qiita.com/etnk/items/70b7da6a39f7c2a4464e

## IAMユーザーの作成

ここでは`s3-user`というユーザーを作成し、AmazonS3FullAccessのポリシーをアタッチします。
![Screenshot 2024-05-21 at 10.50.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a1a71c92-f143-d3d3-4b9c-cbb94abb22ad.png)

:::note info
**注意**
ここでは強力な権限であるAmazonS3FullAccessを付与していますが、ご自身のセキュリティ要件に基づいた権限設定を行ってください。
:::

**セキュリティ認証情報**タブにアクセスし、**アクセスキー**セクションにある**アクセスキーを作成**ボタンをクリックし、必要に応じて説明タグを追記してアクセスキーを作成します。
![Screenshot 2024-05-21 at 10.07.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d15fdc90-6c3c-994d-7308-7fb02a768d51.png)

アクセスキーとシークレットアクセスキーをメモしておきます。
![Screenshot 2024-05-21 at 10.08.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3bc9f04c-833b-b936-a089-1548e0808d71.png)

:::note warn
**警告！**
これらのキーは厳重に管理してください。
:::

# Azure側での作業

上のステップで取得したアクセスキーをAzure Databricksで使えるように設定を行います。これらのキーを平文で管理することは推奨しておらず、[シークレット](https://learn.microsoft.com/ja-jp/azure/databricks/security/secrets/secrets)に格納することを推奨しています。

Azure Databricksの場合、シークレットの管理方法には2つの選択肢があります。

- Azure Key Vaultによる管理
- Azure Databricksによる管理

ここでは、Azure Databricksで管理するアプローチを取りますが、要件に基づいて管理方法を選択ください。

シークレットの管理をするためには、[Databricks CLI(コマンドラインインタフェース)](https://learn.microsoft.com/ja-jp/azure/databricks/dev-tools/cli/)を使う必要があります。

ローカルマシンでDatabricks CLIを[インストール](https://learn.microsoft.com/ja-jp/azure/databricks/dev-tools/cli/install)します。あるいは、[Azure Cloud Shell](https://learn.microsoft.com/ja-jp/azure/databricks/scenarios/databricks-cli-from-azure-cloud-shell)をお使いください。ここでは、ローカルマシンにインストールしたDatabricks CLIで作業します。

## Databricks CLIのセットアップ

Databricks CLIのセットアップには、Azure Databricksワークスペースで[パーソナルアクセストークン](https://learn.microsoft.com/ja-jp/azure/databricks/admin/access-control/tokens)を取得する必要があります。

ワークスペースにアクセスし、右上のユーザーアイコンをクリックし、**設定**を選択します。**ユーザー > 開発者**にアクセスし、**アクセストークン**の**管理**をクリックします。
![Screenshot 2024-05-21 at 10.12.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/df75e180-0cd2-4eb7-3ed3-f94478737ff0.png)

**新規トークンを作成**をクリックし、コメントと有効期間を指定してトークンを作成します。表示されるトークンをメモしておきます。有効期間を指定しない場合は無期限有効となります。
![Screenshot 2024-05-21 at 10.13.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6b0cb79c-1145-238e-83f9-d1e2e776114c.png)
![Screenshot 2024-05-21 at 10.12.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/06da2d22-690c-bb84-50fa-c3136b4c3e74.png)

:::note warn
**警告！**
このトークン
は厳重に管理してください。
:::

[こちらの手順](https://learn.microsoft.com/ja-jp/azure/databricks/dev-tools/cli/authentication#--azure-databricks-personal-access-token-authentication)に従い、コマンドプロンプトやターミナルを起動し、以下を実行します。

```sh
databricks configure
```

Azure Databricksワークスペースのホスト名を聞かれるので、使用するワークスペースにブラウザでアクセスし、`https://`以降から`.net/`までを貼り付けます。次にパーソナルアクセストークンを聞かれるので、上で取得したパーソナルアクセストークンを設定します。これで、Databricks CLIの設定は完了です。
![Screenshot 2024-05-21 at 11.08.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/17e15b25-d3ec-29c8-5155-4d5c2f411820.png)

:::note info
**注意**
上の例では、`--profile test`を指定していますが、これは[**プロファイル**](https://learn.microsoft.com/ja-jp/azure/databricks/dev-tools/auth/#config-profiles)を指定しています。複数環境を操作する場合にはプロファイルを作成すると、簡単に設定を切り替えられるので作業が楽になります。
:::

## シークレットスコープの作成

シークレットは複数作成することができ、それらは[**シークレットスコープ**](https://learn.microsoft.com/ja-jp/azure/databricks/security/secrets/secret-scopes)で管理することができます。ですので、先にシークレットスコープを作成します。

Databricks CLIで以下を実行します。ここでは`s3_access`というシークレットスコープを作成しています。また、プロファイル`test`を指定して、接続先を指定してます。

```sh
databricks secrets create-scope s3_access -p test 
```

スコープが作成されたことを確認します。

```sh
databricks secrets list-scopes -p test
```
```
Scope      Backend Type
s3_access  DATABRICKS
```

## シークレットの作成

以下の二つのコマンドを実行して、`aws_access_key_id`と`aws_secret_access_key`のシークレットを作成します。

:::note info
**注意**
`aws_access_key_id`は`AKI`で始まる文字列です。
:::


```sh
databricks secrets put-secret --json '{
  "scope": "s3_access",
  "key": "aws_access_key_id",
  "string_value": "AKI..."
}' -p test
```

```sh
databricks secrets put-secret --json '{
  "scope": "s3_access",
  "key": "aws_secret_access_key",
  "string_value": "....."
}' -p test
```

シークレットが登録されたことを確認します。

```sh
databricks secrets list-secrets s3_access -p test
```

```
Key                    Last Updated Timestamp
aws_access_key_id      1716255148842
aws_secret_access_key  1716255154670
```

:::note
**注意**
シークレットに[アクセスコントロール](https://learn.microsoft.com/ja-jp/azure/databricks/security/secrets/secrets#--manage-secrets-permissions)を施すことができます。セキュリティ要件に基づき、適切な設定を行ってください。
:::


## Databricksクラスターの設定

これで、Azure Databricksから上述のシークレットを利用できるようになりました。クラスターからシークレットを使用するようにするには、もう一つの設定が必要です。設定を行わない場合、S3からアクセスが拒否されます。
![Screenshot 2024-05-21 at 10.45.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/91b179ae-4aa6-3428-ade0-be9b36606d74.png)

使用するクラスターの**高度な設定**を展開します。
![Screenshot 2024-05-21 at 11.20.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e267e18e-42f6-6f41-20b6-751f8feb4ad3.png)

ここの**環境変数**に以下を貼り付けます。

```
AWS_SECRET_ACCESS_KEY={{secrets/s3_access/aws_secret_access_key}}
AWS_ACCESS_KEY_ID={{secrets/s3_access/aws_access_key_id}}
```

:::note info
**注意**
この例では、上のようになっていますが、`s3_access`は実際に作成したシークレットスコープ名、`aws_secret_access_key`や`aws_access_key_id`は実際に作成したシークレット名で置き換えてください。
:::

これでクラスターを再起動します。
![Screenshot 2024-05-21 at 11.23.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6727116f-45c3-df34-5031-68b8eb44fec5.png)

:::note info
**注意**
この設定は当該クラスターにアクセスできるすべてのユーザーに対して有効となります。クラスターのアクセス権を適切に設定してください。
:::

改めて以下を実行します。CSVファイルは事前に配置してあります。

```py
aws_bucket_name = "taka-bucket-from-azure"

df = spark.read.csv(f"s3a://{aws_bucket_name}/japan_cases_20220818.csv", header=True)
display(df)
display(dbutils.fs.ls(f"s3a://{aws_bucket_name}/"))
```

これでアクセスできました。
![Screenshot 2024-05-21 at 11.29.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ddf2f433-9964-a840-ab9f-8e531bf9b7f1.png)
![Screenshot 2024-05-21 at 11.29.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2b12d229-985d-0bca-91ef-4a9ea76311c9.png)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

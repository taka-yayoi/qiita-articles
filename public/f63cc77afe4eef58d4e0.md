---
title: アカウントコンソールを用いたDatabricks on AWSのアカウントのセットアップ、ワークスペースのデプロイ(実践編)
tags:
  - AWS
  - Databricks
private: false
updated_at: '2022-01-07T15:46:21+09:00'
id: f63cc77afe4eef58d4e0
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

このドキュメントは[アカウントコンソールを用いたDatabricks on AWSのアカウントのセットアップ、ワークスペースのデプロイ](https://qiita.com/taka_yayoi/items/1f0955e27eec3e7a3cc8)の手順において、作業内容の理解を深めるために弊社で実施した作業のログを追記及び、オンラインドキュメントの一部を使用して補足説明したものです。仕様変更等により内容は予告なく変更される場合があります。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fedf965f-1029-d6ba-4190-16bc15ce41cf.png)

# Databricksフリートライアルのサインアップ

Databricksのフリートライアルを開始するには、[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)をクリックします。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/de009218-b78d-c69a-6363-8e6c64a2c1ef.png)

必要事項を入力後、”GET STARTED FOR FREE”を押下すると、無料トライアルのプラットフォームの選択ページが表示されます。

ここでは**AWS**を選択してください。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f37a53dc-ea93-60f6-9b90-203c83890a2b.png)

入力したE-MailアドレスにトライアルのためのWelcomeメールが送信されます。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9f9821b3-a669-0fec-6f96-f821e2d312ca.png)

メールボックスを確認し以下のような内容のメールが受信したことを確認してください。

**注意:メールが届いていない場合には、迷惑メールに分類されていないかご確認ください。**

# サインアップの確認とサブスクリションプランの選択

アカウントをサインアップした後、Databricksから受け取るWelcomeメールを開き、メールアドレスを検証するためのリンク(**Verify your email address**)をクリックし、パスワードを設定します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/046b427f-7df6-cabe-cff0-6fbf79200270.png)

新たに表示されるページでDatabricksアカウントのパスワードを設定してください。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f7f85630-ff9b-efea-5efc-a5bb230a4411.png)

**Set Password**をクリックすると、サブスクリプションプランを選択するページに遷移します。お客様の要件に応じて適切なサブスクリプションプランを選択してください。サブスクリプションプランと価格に関しては、[Databricks on AWS プランと料金](https://databricks.com/jp/product/aws-pricing)を参照ください。

**Continue**をクリックし、**Workspaces**ページを開きます。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/391934eb-5d7d-8dcb-9d19-08dbd8cf6ecb.png)

**Continue**を押下するとワークスペースのセットアップページに遷移します。

# ワークスペースのセットアップ

Databricksにサインアップしたユーザーは[アカウントオーナー(英語)](https://docs.databricks.com/administration-guide/index.html)となり、アカウントオーナーだけが初期セットアップを実行することができます。しかし、他のユーザーを管理者に任命することで、後続の管理者作業を移譲することができます。

Databricksアカウントにサインアップした後は、あなたのチームメンバーがDatabricksの全てのアセットにアクセスするために、最低1つのワークスペースをセットアップします。

> **注意** 以降の説明においては、DatabricksのアカウントコンソールとAWSユーザーインタフェースを用いて、Databricksアカウントをセットアップし、手動でワークスペースを作成する手順を説明します。別の方法として、CloudFormationのテンプレートを活用して、より容易にワークスペースを構築できる[Databricks on AWS Quickstarts](https://qiita.com/taka_yayoi/items/c53beee557ae4a9643ac)を用いることもできます。このAWS Quickstartsは、ITインフラのアーキテクト、管理者、DevOps専門家をターゲットとしたものです。

> **注意** このドキュメントで実施しているDatabricks管理のデフォルト設定でワークスペースをセットアップする場合、以下のリソースが新規に作成されます。

AWS自体の制限値に抵触しないか事前に確認し、必要に応じて調整ください。(Elastics IPなど最大デフォルト値:5など）
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/626ac2d9-30de-abf5-7d0f-45efc3f98568.png)

> **訳者注**
2022/1/7時点では、初回Databricksアカウントコンソールにログインした際は、[Databricksアカウントのセットアップとワークスペースの作成](https://qiita.com/taka_yayoi/items/c53beee557ae4a9643ac)で説明されているクイックスタートによる構築がデフォルトとなっています。[顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)を用いたデプロイを行う場合には、一旦以下の方法で本手法をスキップしてから、本書で説明されているデプロイ手順を踏んでください。

> 1. AWSアカウントコンソールからログアウトしておきます。
1. Databricksアカウントコンソールにログインし、2つのメッセージ画面を経た後で、**Workspace Name**に適当な名前を入力し、一旦**Start quickstart**をクリックします。上でログアウトしておかないとCloud Formationのスタックを作成してしまうので注意してください。
1. AWSアカウントコンソールが別タブで開きますがこちらは閉じます。
1. アカウントコンソールに戻るとワークスペース一覧が表示されます。
1. こちらで**Create workspace > Custom AWS configuration**を選択してください。

## Create workspaceをクリックしてセットアップを開始

ワークスペースは、あなたのチームメンバーがDatabricksの全てのアセットにアクセスするための環境となります。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5683bb6c-bcdf-e024-89db-d0a6b18696e1.png)

**Create Workspace**をクリックし、**Custom AWS configuration**を選択します。その後、ワークスペース名、リージョン、サブスクリプションプランを設定します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d0e71562-a2e1-29d7-87cd-20cc57ca2561.png)

- **Workspace name:** 人の目で見て理解できる名称をつけます。例えば、“Acme data science workspace”などです。
- **Subscription plan:** サブスクリプションページで選択したプランです。
- **Region:** Databricksワークスペースのリソースを格納するAWSリージョンです。

## 認証設定の作成 - External ID(Databricksアカウント)の取得

認証設定(credential configuration)では、DatabricksがあなたのAWSアカウントでクラスターを起動するのに必要なアクセス権をもつクロスアカウントIAMロールを作成し、それらの情報を入力します。

IAMロールと認証情報を作成するには**Credential configuration**で、**Add a new credential**を選択します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e8a5b500-bfe4-7d6e-8271-0591dc74c45a.png)

ポップアップされるAdd **Credential Configuration**ダイアログで、**External ID**をコピーしておきます。次のステップでIAMロールを作成する際に必要になります。

例:以下の例では`37e9ffbe-236e-4e80-ad42-24b017419657`がExternal IDとなります。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/85ba36ed-f788-97a9-4968-885726af84ca.png)

## 認証設定の作成 - IAMロールを作成

[AWS マネジメントコンソール](https://aws.amazon.com/jp/console/)へ移動し、ご利用中のAWSアカウントへログインします。このAWSアカウントにDatabricksワークスペースが連携されます。

次にAWSアカウントコンソールを使用して、[Create a cross-account IAM role(英語)](https://docs.databricks.com/administration-guide/account-api/iam-role.html)の手順に沿ってIAMロールを作成します。

> **注意** これらの手順においては、デフォルトのDatabricks管理のVPCか[顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)を使うかに応じて、ロールのポリシーに3つの選択肢が存在します。Standardプランを含む、典型的なパターンではDatabricks管理のVPCを使用します。Premium、Enterpriseサブスクリプションの場合は、ワークスペースを作成する際にVPCのタイプを選択することができます。なお、Databricks管理VPCから顧客管理VPCにワークスペースを移行することはできません。

### IAMロールの作成

信頼されたエンティティとして**別のAWSアカウント**を選択し、アカウントIDにDatabricks固有のID`414351767826`を入れます。外部IDには**Add Credential Configuration**ダイアログでコピーした**External ID**を外部IDとして入力します。
![Screen Shot 2021-12-01 at 10.06.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5ee0c1ce-3738-aef9-a218-c99b91d33cd9.png)

次のステップをクリック　
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/139411a3-0a71-e0cb-8e58-2694aacae323.png)

次のステップをクリック (設定必要なし)
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b32d9611-1efc-3a31-f30e-d3de74c7a636.png)

次のステップをクリック (設定必要なし)
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/23c3e1f9-62a8-1cd8-5755-18d268ace243.png)

ロール名を入れます。**注：英数字のみの入力になります**
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1fb5dfc7-0398-1a56-d852-347b6f2d900f.png)

ロールができたことを確認します。

### 認証設定の作成 - 作成したIAMロールにインラインポリシーの追加

作成したロールをクリックし、右下の**+インラインポリシーの追加**をクリックします。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/18fa03ab-622a-cebd-0f4a-05e385017335.png)

ポリシーのJSONタグをクリックし、[Create a cross-account IAM role(英語)](https://docs.databricks.com/administration-guide/account-api/iam-role.html)にある下記の適切な**ポリシー(JSON)**を選択して貼り付けます。

| デプロイ | ポリシー |
|:--|:--|
|デフォルトのポリシー制限がある顧客管理のVPC：[独自のVPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)でDatabricksワークスペースを起動します。   |[Your VPC, default]   |
|カスタムポリシー制限付きの顧客管理VPC：アカウントID、VPC ID、リージョン、およびセキュリティグループによるポリシー制限付きの[独自のVPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)でDatabricksワークスペースを起動します。   |[Your VPC, custom]   |
|Databricksが管理するVPC：Databricksが管理するVPCでDatabricksワークスペースを起動します。   |[Databricks VPC]   |

> **注意** 注：このポリシーは[Databricksオフィシャルドキュメント](https://docs.databricks.com/administration-guide/account-api/iam-role.html)からも参照頂けます。このドキュメントで使用するのは”Databricks VPC”で表示されるポリシーです

![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9e33457a-eed0-5d9b-d59e-b196c0716317.png)

![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ca6618e1-bec1-bd17-ad35-539222a742ea.png)

**ポリシーJSON (以下は”Databricks VPC”のポリシー)**

[顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)を使用する場合は、**Your VPC, default**もしくは**Your VPC, custom**のポリシーを選択し、構築する環境に応じて修正が必要となります。

```json:JSON
{
"Version": "2012-10-17",
"Statement": [{
      "Sid": "Stmt1403287045000",
      "Effect": "Allow",
      "Action": [
        "ec2:AllocateAddress",
        "ec2:AssociateDhcpOptions",
        "ec2:AssociateIamInstanceProfile",
        "ec2:AssociateRouteTable",
        "ec2:AttachInternetGateway",
        "ec2:AttachVolume",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:CancelSpotInstanceRequests",
        "ec2:CreateDhcpOptions",
        "ec2:CreateInternetGateway",
        "ec2:CreateKeyPair",
        "ec2:CreateNatGateway",
        "ec2:CreatePlacementGroup",
        "ec2:CreateRoute",
        "ec2:CreateRouteTable",
        "ec2:CreateSecurityGroup",
        "ec2:CreateSubnet",
        "ec2:CreateTags",
        "ec2:CreateVolume",
        "ec2:CreateVpc",
        "ec2:CreateVpcEndpoint",
        "ec2:DeleteDhcpOptions",
        "ec2:DeleteInternetGateway",
        "ec2:DeleteKeyPair",
        "ec2:DeleteNatGateway",
        "ec2:DeletePlacementGroup",
        "ec2:DeleteRoute",
        "ec2:DeleteRouteTable",
        "ec2:DeleteSecurityGroup",
        "ec2:DeleteSubnet",
        "ec2:DeleteTags",
        "ec2:DeleteVolume",
        "ec2:DeleteVpc",
        "ec2:DeleteVpcEndpoints",
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeIamInstanceProfileAssociations",
        "ec2:DescribeInstanceStatus",
        "ec2:DescribeInstances",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeNatGateways",
        "ec2:DescribePlacementGroups",
        "ec2:DescribePrefixLists",
        "ec2:DescribeReservedInstancesOfferings",
        "ec2:DescribeRouteTables",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSpotInstanceRequests",
        "ec2:DescribeSpotPriceHistory",
        "ec2:DescribeSubnets",
        "ec2:DescribeVolumes",
        "ec2:DescribeVpcs",
        "ec2:DetachInternetGateway",
        "ec2:DisassociateIamInstanceProfile",
        "ec2:DisassociateRouteTable",
        "ec2:ModifyVpcAttribute",
        "ec2:ReleaseAddress",
        "ec2:ReplaceIamInstanceProfileAssociation",
        "ec2:RequestSpotInstances",
        "ec2:RevokeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:RunInstances",
        "ec2:TerminateInstances"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
          "iam:CreateServiceLinkedRole",
          "iam:PutRolePolicy"
      ],
      "Resource": "arn:aws:iam::*:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot",
      "Condition": {
        "StringLike": {
            "iam:AWSServiceName": "spot.amazonaws.com"
        }
      }
    }]
}

```

インラインポリシー名を入力して**ポリシーを作成**を押下します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1f40c074-d732-5105-dfc4-8967df864a6d.png)

IAMロールの作成が終わったら、**ロールARN**をコピーしておきます。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cb845e74-6ec2-b1e9-d0f7-9170d8c2cf1d.png)

## 認証設定の作成 - 作成したロールARNを入力

**Add Credential Configuration**ダイアログに戻って、**Credential Configuration Name**に設定名を入力します。あなたの認証設定とチームの他の人が今後作成するものの区別がつくように名前をつけてください。

AWSコンソールから作成したAIMロールの**Role ARN**フィールドに**ロールARN**を貼り付けます。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fc1f9ffd-8d2c-63cd-8eaa-6d519d286044.png)

**Add**をクリックします。詳細は、[Create a credential configuration(英語)](https://docs.databricks.com/administration-guide/account-settings-e2/credentials.html#create-a-credential-configuration)を参照ください。

## ストレージ設定の作成

**Storage configuration**フィールドで、**Add a new storage configuration**を選択します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2bcd8001-fb9b-d864-86ac-91b6923dc7e0.png)

**Add Storage Configuration**ダイアログで、ストレージ設定名を入力します。あなたのストレージ設定とチームの他の人が今後作成するものの区別がつくように名前をつけてください。DatabricksのDBFS(Databricksファイルシステム)ルートに使用する**S3バケット名**を入力します。あなたのAWSアカウントにおいて、他のバケットと区別がつく名前を指定します。S3バケットを作成する際にはここ指定するものと同じS3バケット名を使う必要があります。

![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/54116415-96d4-4aef-a92a-3722e539a7ba.png)

あなたのAWSアカウントでS3バケットを作成する際に使用するバケットポリシーを生成するために、**Generate Policy**をクリックします。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/914261e0-dcf8-aee2-a652-e48566d3eac0.png)

生成されたバケットポリシーをコピーします。これは、[Create the S3 bucket(英語)](https://docs.databricks.com/administration-guide/account-settings-e2/storage.html#create-the-s3-bucket)に従って、あなたのAWSアカウントでバケットを作成する際に使用します。

バケットポリシーをコピーしたら、**Add**を押下します。(バケットポリシーは https://docs.databricks.com/administration-guide/account-api/aws-storage.html にも記載されています）

> **注意**　この時点ではまだ**Save**は押下しないでください。AWS側でのS3バケットの作成、ネットワーク設定が完了するまで**Save**を押さないでください。

![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0f321c85-7c01-c6c1-f82a-751fa86ffef5.png)

## AWSコンソールでDatabricksのDBFSルート用のS3バケットを作成

上で作成したストレージ設定を適用するDBFSルート用のストレージS3バケットを作成します。DBFSルートストレージS3バケットは、クラスターのログ、ノートブックのバージョン、ジョブ結果などを格納するために必要となります。また、テストに必要なデータなどを格納するために使用することもできます。

詳細は[Manage storage configurations using the account console (E2)](https://docs.databricks.com/administration-guide/account-settings-e2/storage.html)を参照ください。

> **注意** 同一アカウントに属する複数のワークスペースでルートS３バケットを共有することができます。ワークスペースごとにバケットを作る必要はありません。複数ワークスペースでバケットを共有した場合、バケット上のデータはワークスペースごとに異なるディレクトリごとに区切られることになります。すでにS3バケットがある場合にはこのステップをスキップできます。

**リファレンス**
[Configure AWS storage (E2 and log delivery only) — Databricks Documentation](https://docs.databricks.com/administration-guide/account-api/aws-storage.html)

ストレージ設定で指定したS3バケット名を入力します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/adbdfb66-b261-eaf0-a194-f7173edc4c56.png)

> **推奨事項**
Databricksでは、バケットのバージョニングを有効にすることを強く推奨しています。バージョニングは、ファイルが誤って変更または削除された場合に、バケット内のファイルの以前のバージョンを復元することができます。

![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/87c540e1-f678-11b2-9da2-f1f8cd2eb310.png)
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/160d9bbc-b9d8-29f9-dd9a-56ff1b091681.png)

S3バケットの**アクセス許可**にDatabricksのバケットポリシーを設定します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/11906cdd-6f0c-d4d6-bbc2-38140955dabf.png)
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fbe75448-f1e9-6f6c-617b-646af4429505.png)

生成されたバケットポリシーを貼り付け、**変更を保存**を押下します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c546afcd-8c53-e4eb-e461-5a527d9e4858.png)
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6c4e3d64-49f6-ec93-c616-b248d8f8fd51.png)

## ネットワーク設定を作成

[顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)を使用したセットアップを実施しない場合はこの設定はスキップしてください。

顧客管理VPCの設定例については、[Databricksにおける顧客管理VPC\(実践編\)](https://qiita.com/taka_yayoi/items/9e04f78ff025f77e52a6)をご覧ください。

顧客管理のVPC(customer-managed VPC)を使用したセットアップを実施する場合は以下のネットワーク設定を作成します。事前に[顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)に記載されている要件に合致するVPCを作成しておく必要があります。

**Advanced settings > Network configuration**で、**Add a new network configuration**を選択します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f4112bbe-ee9d-3218-dbe4-d988ee314e60.png)

**Add Network Configuration**ダイアログで、ネットワーク設定名を指定します。あなたのネットワーク設定とチームの他の人が今後作成するものの区別がつくように名前をつけてください。

顧客管理VPCで使用するVPC ID、サブネットID、セキュリティグループIDを入力します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/51fdf8af-df08-f53f-e3f6-58ace3871873.png)

**Add**をクリックします。

## Workspaceのプロビジョニング

全ての項目の入力が完了しましたら、**Save**を押下してください。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f6eb44bd-f6ce-10df-9511-642efdc886d1.png)

**Save**ボタンを押下するとワークスペースのプロビジョニングが開始されます。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/105fb8a7-27e0-8cc1-c272-79de0e10249e.png)

約10-15分程度でワークスペースのセットアップが完了します。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4e8541a4-9730-aae5-e715-2ab161478b01.png)

作成したワークスペースへのリンクをクリックするとワークスペースURL等の情報が表示されます。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6745d75a-71d3-3344-789b-14cd4afcbae7.png)

## ワークスペースの動作確認

ワークスペースURLをクリックすることで、ワークスペースに移動することができます。ワークスペースURLをブックマークしておき、アカウントコンソールにアクセスする際に用いたユーザー名(メールアドレス)とパスワードでログインします。 
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/530babd8-c561-1e70-58cc-ebb000b9829c.png)

新規にクラスターを作成できることを確認してください。
![Picture1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fcc1bbb8-107f-a230-fd73-fb331999aed4.png)

クラスターが起動できましたら動作確認は完了です。

# 次のステップ

- Databricksの使い方を学ぶ
    - [ユーザー向けDatabricksスタートガイド](https://qiita.com/taka_yayoi/items/77aa10ebcad9d40cc49c)を試す。
    - [Getting started with Databricks | Databricks on AWS(英語)](https://docs.databricks.com/onboarding/index.html)のラーニングパスに沿って学習を進める。
    - [Databricksワークスペースのコンセプト](https://qiita.com/taka_yayoi/items/78bf647c40a906d90db0)を学ぶ。
    - ワークスペースのWelcomeページにあるquickstart notebookを実行する。
    - [フリーのトレーニング(英語)](https://docs.databricks.com/getting-started/free-training.html)を活用する(ご契約いただいたお客様のみ)。

- ユーザーの追加、セキュリティの設定など管理者のタスクを学ぶ
    - アカウント管理作業を移譲するために、管理者ユーザーを追加できます。[Delegate account administration | Databricks on AWS(英語)](https://docs.databricks.com/administration-guide/account-settings-e2/admin-users.html)を参照ください。
    - ワークスペースへのユーザー追加、セキュリティのセットアップ、ログの設定などワークスペースの設定に関しては、[管理者向けDatabricksスタートガイド](https://qiita.com/taka_yayoi/items/5a117a8bdea67051a0ce)を参照ください。
    - [Administration guide(英語)](https://docs.databricks.com/administration-guide/index.html)では、管理者の全てのタスクが網羅されています。

- 請求情報の追加
    14日間のフリートライアルを申し込んでいる場合、請求情報を追加することでトライアル終了後もDatabricksアカウントをご利用いただけます。
    1. アカウントオーナーとして[アカウントコンソール](https://accounts.cloud.databricks.com/login)にログインします。
    2. サイドバーの**Settings**アイコンをクリックし、**Subscription & Billing**タブをクリックします。
    3. **Add billing information**ボタンをクリックします。
    4. **Billing**ページで請求情報を入力し**Save**をクリックします。
    
    キャンセルするまでは月ごとに請求が発生します。クレジットカードの月額課金から請求書、コミットベースの請求に変更するには、[Databricks担当](mailto:sales-jp@databricks.com)にお問い合わせください。

- アカウント管理詳細
    Databricksのサブスクリプション、アカウント情報の更新などに関する詳細は、[Manage your Databricks account (E2)(英語)](https://docs.databricks.com/administration-guide/account-settings-e2/index.html)を参照ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

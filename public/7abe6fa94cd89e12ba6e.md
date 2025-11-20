---
title: AWSにおけるDatabricksデプロイメントについてまとめてみた
tags:
  - AWS
  - Databricks
  - PrivateLink
private: false
updated_at: '2023-05-24T17:19:36+09:00'
id: 7abe6fa94cd89e12ba6e
organization_url_name: databricks
slide: false
ignorePublish: false
---
主要クラウドサービス(AWS、Azure、GCP)で動作するDatabricksですが、AWSでデプロイする際には自分でVPCの構成を決めたり、PrivateLink構成を選択することができます(他のCSPでも順次対応しています)。

その分、「どの構成にしたらいいのか？」と迷うこともしばしばです。これまでに少なくとも10以上のDatabricksワークスペースをデプロイしてきた経験を踏まえて、記事にまとめてみました。

# AWSにおけるDatabricksデプロイメントの方法

方法としては以下の2つがあります。

1. Databricksアカウントコンソール(GUI)
1. Account API(REST API)

設定自体を自動化するツールには以下の2つがあります。サインアップした際のデフォルトのデプロイメント手段はAWS QuickStartになっています。

1. [AWS QuickStart](https://qiita.com/taka_yayoi/items/c53beee557ae4a9643ac)
1. [Terraform](https://qiita.com/taka_yayoi/items/691ee4909b0961de5ad1)

# デプロイメント形態

デプロイメントの形態には大きく以下の2つがあります。

1. [公衆ネットワークを用いたデプロイ](https://qiita.com/taka_yayoi/items/1f0955e27eec3e7a3cc8)
1. [PrivateLinkを用いたデプロイ](https://qiita.com/taka_yayoi/items/c6bdbb6452f6a0895961)
    - フロントエンドPrivateLink
    - バックエンドPrivateLink

# どのデプロイメント形態を採用すべきか？

どのデプロイメント形態にするのかを決定するフローチャートです。以下で述べている顧客管理VPCに関しては、[Databricksにおける顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)をご覧ください。

![Screenshot 2023-05-24 at 17.17.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c775afb5-951f-1ec6-9f11-bdbb25a699fc.png)


デプロイメント形態にはそれぞれPros & Consがあります。センシティブなデータを取り扱わないPOCの場合は公衆ネットワークを使用する構成、本番環境ではPrivateLink構成を検討することをお勧めします。

| デプロイメント形態 | Pros | Cons |
|:--|:--|:--|
| AWS Private Networkを用いたデプロイ  |  すぐにデプロイできます。POCならこちらがお勧めです。 |  コントロールプレーン、データプレーン間の通信ではAWS Private Networkを経由することになります。ブラウザからDatabricksへの接続は公衆回線経由となります。 |
| PrivateLinkを用いたデプロイ  | <ul><li>**バックエンドPrivateLink**：コントロールプレーン、データプレーン間はAWSのバックボーンネットワークと使用するのでAWS Private Networkを経由しません。本番環境はこちらをお勧めするケースが多いです。<li>**フロントエンドPrivateLink**：クライアントからの接続でも公衆回線を経由したくないケースではお勧めしています。こちらも本番向け。バックエンドPrivateLinkとセットでかつロックダウン構成にするのが定石です。</ul>  |  <ul><li>Built-inのHiveメタストアは動かないので、Glueを使うかUnity Catalgを使います。<li>クラスターからはインターネットに接続できないので、pipなどは追加の設定をしない限り使用できません。<li>フロントエンドPrivateLink構成を取る際にはDNS設定が必要になるので、SIパートナーなどのサポートを要請することをお勧めします。</ul> |

# PrivateLink構成のワークスペースをデプロイするのに必要なオブジェクト

PrivateLink構成のワークスペースをデプロイするまでには様々なオブジェクトを作成します。

![Screen Shot 2022-08-24 at 22.08.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e2318c90-6f8f-65b9-d550-c4fd95e11951.png)

**AWSマネジメントコンソールで作成**
- クロスアカウントIAMロール
- S3バケット
- VPC
- サブネット
- セキュリティグループ(ネットワークACL)
- ルートテーブル
- VPCエンドポイント

**Databricks Account Consoleで作成**
- 認証情報設定オブジェクト(Credential configuration)
- ストレージ設定オブジェクト(Storage configuration)
- ネットワーク設定オブジェクト(Network configuration)
- VPCエンドポイントの登録
- プライベートアクセス設定オブジェクト(Private Access Setting configuration)
- ワークスペース

AWSのオブジェクトとDatabricksのオブジェクトには以下の関係性があります。
![Screen Shot 2022-08-24 at 22.09.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3a8839df-32c6-57e9-a31d-2c71065f6098.png)

これらの設定手順に関しては、以下の手順書を参照ください。

- [DatabricksにおけるAWS PrivateLinkの有効化](https://qiita.com/taka_yayoi/items/c6bdbb6452f6a0895961)
- [DatabricksにおけるAWS PrivateLinkのバックエンド接続の設定\(実践編\)](https://qiita.com/taka_yayoi/items/1ca54463469df05dd3ee)
- [DatabricksにおけるAWS PrivateLinkのフロントエンド接続の設定\(実践編\)](https://qiita.com/taka_yayoi/items/4f08a48e431c38b8bca5)

# 参考資料

- [Databricksフリートライアルへのサインアップ](https://qiita.com/taka_yayoi/items/fb4f57c069e1f272e88a)
- [Databricksアカウントのセットアップとワークスペースの作成 ](https://qiita.com/taka_yayoi/items/c53beee557ae4a9643ac)
- [Databricksアカウントのセットアップとワークスペースの作成\(実践編\)](https://qiita.com/taka_yayoi/items/98edd2e9d06f5c1029a1)
- [アカウントコンソールを用いたDatabricks on AWSのアカウントのセットアップ、ワークスペースのデプロイ](https://qiita.com/taka_yayoi/items/1f0955e27eec3e7a3cc8)
- [アカウントコンソールを用いたDatabricks on AWSのアカウントのセットアップ、ワークスペースのデプロイ\(実践編\)](https://qiita.com/taka_yayoi/items/f63cc77afe4eef58d4e0)
- [Databricksにおける顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)
- [Databricksにおける顧客管理VPC\(実践編\)](https://qiita.com/taka_yayoi/items/9e04f78ff025f77e52a6)
- [DatabricksにおけるAWS PrivateLinkの有効化](https://qiita.com/taka_yayoi/items/c6bdbb6452f6a0895961)
- [DatabricksにおけるAWS PrivateLinkのバックエンド接続の設定\(実践編\)](https://qiita.com/taka_yayoi/items/1ca54463469df05dd3ee)
- [DatabricksにおけるAWS PrivateLinkのフロントエンド接続の設定\(実践編\)](https://qiita.com/taka_yayoi/items/4f08a48e431c38b8bca5)
- [Databricks PrivateLink構成における設定確認 ](https://qiita.com/taka_yayoi/items/7a856ba770eb932fac70)
- [Databricksワークスペース\(E2\)作成時のトラブルシューティング](https://qiita.com/taka_yayoi/items/483f3392a7b40b89c152)
- [DatabricksワークスペースへのAWS PrivateLinkとカスタムDNSの適用](https://qiita.com/taka_yayoi/items/2a63956fa916ee9456f8)
- [Databricks Terraformプロバイダー](https://qiita.com/taka_yayoi/items/691ee4909b0961de5ad1)
- [Terraformを用いたDatabricksワークスペース\(E2\)の配備](https://qiita.com/taka_yayoi/items/11d4ef49871e9b1292bb)
- [Terraformを用いたエンドツーエンドのDatabricksワークスペース管理](https://qiita.com/taka_yayoi/items/012122880b728a33d781)



### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

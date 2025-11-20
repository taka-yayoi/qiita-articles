---
title: AWS PrivateLinkによるプライベートDatabricksワークスペースのパブリックプレビュー
tags:
  - AWS
  - Databricks
  - PrivateLink
private: false
updated_at: '2021-09-08T16:27:39+09:00'
id: ac38efeb49cecd2ab77a
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Private Databricks Workspaces With AWS PrivateLink Is in Public Preview \- The Databricks Blog](https://databricks.com/blog/2021/04/23/private-databricks-workspaces-with-aws-privatelink-is-in-public-preview.html)の翻訳です。

[AWS上のDatabricksワークスペース](https://databricks.com/jp/product/aws)におけるPrivateLink接続が、実運用へのデプロイメントを完全にサポートし、パブリックプレビューになったことを嬉しく思います。このリリースは、[E2アーキテクチャをサポートしているすべてのAWSリージョン](https://docs.databricks.com/administration-guide/cloud-configurations/aws/regions.html)に適用され、[Enterpriseプラン](https://databricks.com/product/aws-pricing)の一部として本機能を利用できます。プライベートプレビューを通じて、大規模金融サービス、ヘルスケア、通信会社を含む世界中のお客様にAWS上にDatabricksレイクハウスプラットフォームのプライベートワークスペースをデプロイいただき、多くのフィードバックをいただきました。お客様は、Databricksワークスペースのフロントエンド、バックエンドインタフェースの両方にクラウドネイティブかつプライベートオンリーの接続性を強制でき、お客様のガバナンスポリシーの主要要件を満足することができました。

# AWS PrivateLinkによるプライベートDatabricksワークスペースの概要

Databricksワークスペースによって、シンプルかつ適切に統合されたアーキテクチャを通じて、強化されたセキュリティ機能を活用することができます。[Databricks E2ワークスペース](https://qiita.com/taka_yayoi/items/7d209bc8d32bc5f2dba4#e2%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3)に対するAWS PrivateLinkを活用することで、以下のメリットを享受することができます。

- **フロントエンドインタフェースに対するプライベート接続:** Databricksのフロントエンドインタフェースに対して、[AWS VPC(virtual private cloud)エンドポイント](https://docs.aws.amazon.com/vpc/latest/privatelink/endpoint-services-overview.html)を設定し、[ノートブック](https://docs.databricks.com/notebooks/index.html)、[SQLエンドポイント](https://docs.databricks.com/sql/admin/sql-endpoints.html)、[REST API](https://docs.databricks.com/dev-tools/api/index.html)([CLI](https://docs.databricks.com/dev-tools/cli/index.html)を含む)、[Databricks Connect](https://qiita.com/taka_yayoi/items/a9781c0a871a5a4fcf2e)に対する全てのユーザー/クライアントの通信がプライベートネットワークおよびAWSバックボーンを経由することを強制します。
- **バックエンドインタフェースに対するプライベート接続:** Databricksワークスペースを、[セキュアクラスターコネクティビティ](https://docs.databricks.com/security/secure-cluster-connectivity.html)を用いて[顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)にデプロイした場合、Databricksのバックエンドインタフェースに[AWS　VPCエンドポイント](https://docs.aws.amazon.com/vpc/latest/privatelink/endpoint-services-overview.html)を設定し、セキュアクラスターコネクティビティのリレーおよび内部APIがプライベートネットワークおよびAWSバックボーンを経由することを強制します。
- **信頼性、スケーラビリティの強化:** クラスターノードにパブリックIPを割り当て、対応するネットワークにアタッチする必要がなくなるので、大規模ワークロードに対しても、お使いのデータプラットフォームの信頼性、スケーラビリティを高めることができます。さらに、ワークスペースの通信は公衆ネットワークの帯域の可用性に影響を受けません。
![](https://databricks.com/wp-content/uploads/2021/04/aws-pl-blog-img-1.png)

ハイレベルにおいては、Databricksのアーキテクチャはコントロール/マネジメントプレーンとデータプレーンから構成されます。コントロールプレーンはDatabricksのAWSアカウントに存在し、webアプリケーション、クラスターマネージャ、ジョブサービス、SQLゲートウェイなどをホスティングしています。データプレーンはお客様のAWSアカウントに存在し、顧客管理VPC(最低2つのサブネット)、セキュリティグループ、そして[DBFS](https://qiita.com/taka_yayoi/items/e16c7272a7feb5ec9a92)として知られるAmazon S3のルートバケットから構成されます。

[E2 Account API](https://docs.databricks.com/administration-guide/account-api/new-workspace.html)と[AWS CLI/Cloudformation](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-vpc-endpoint.html)を組み合わせて、あるいは、我々のエンジニアが管理している[Terraform Resource Provider](https://docs.databricks.com/dev-tools/terraform/index.html)を用いることで、フロントエンドインタフェース、バックエンドインタフェース両方に対してPrivateLinkを用いてワークスペースをデプロイすることができます。インフラストラクチャおよび設定管理をすでにTerraformで自動化しているのであれば、後者を利用することをお勧めします。

# AWS PrivateLinkによるプライベートDatabricksワークスペースを使ってみる

AWS PrivateLinkによるプライベートDatabricksワークスペースをデプロイすることで、強化されたセキュリティ機能を利用することができます。以下のリソースを参照ください。

- [DatabricksにおけるAWS PrivateLinkの有効化 \- Qiita](https://qiita.com/taka_yayoi/items/c6bdbb6452f6a0895961)
- [Secure Cluster Connectivity Documentation](https://docs.databricks.com/security/secure-cluster-connectivity.html)
- [Data exfiltration protection architecture](https://databricks.com/blog/2021/02/02/data-exfiltration-protection-with-databricks-on-aws.html)
- [Securely Accessing External Data Sources from Databricks on AWS](https://databricks.com/blog/2019/03/08/securely-accessing-external-data-sources-from-databricks-for-aws.html)

我々がAWS上で最も人気のあるレイクハウスプラットフォームを構築しつつも、どのようにセキュリティファーストのマインドセットを組み込んでいるのか関しては、[エンタープライズ向けプラットフォームセキュリティ](https://databricks.com/jp/product/enterprise-security)を参照ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

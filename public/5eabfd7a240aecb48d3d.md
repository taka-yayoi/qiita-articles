---
title: Databricksにおけるセキュリティの概要
tags:
  - Databricks
private: false
updated_at: '2023-01-31T18:59:17+09:00'
id: 5eabfd7a240aecb48d3d
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Security overview \| Databricks on AWS](https://docs.databricks.com/security/security-overview.html) [2023/1/26時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本書では、セキュリティコントロール、デプロイメントの設定、DatabricksアカウントとDatabricksワークスペースの管理の概要について説明します。データの保護に関しては、[Databricksベストプラクティス：データガバナンス](https://qiita.com/taka_yayoi/items/ca0673f6b7b6ca38a08f)をご覧ください。

すべての価格プランですべてのセキュリティ機能が使える訳ではありません。価格プランに機能がどのように割り当てられているのかに関しては、[Databricks AWS価格ページ](https://www.databricks.com/jp/product/aws-pricing)をご覧ください。

:::note
**注意**
本書は、[最新のE2バージョン](https://qiita.com/taka_yayoi/items/7d209bc8d32bc5f2dba4#e2%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3)のDatabricksプラットフォームにフォーカスしています。ここで説明されている機能のいくつかは、E2プラットフォームに移行していないレガシーデプロイメントではサポートされていないことがあります。
:::

# アカウントとワークスペース

Databricksにおいて、*ワークスペース*は指定されたユーザーグループがすべてのDatabricks[資産](https://qiita.com/taka_yayoi/items/6fc2438df3df1a775d76)にアクセスする統合環境として機能するクラウド上のDatabricksデプロイメントです。必要に応じて、単に1つ、あるいは複数のワークスペースをデプロイするのかを選択することができます。

Databricksの*アカウント*は、課金やサポートの対象として単一のエンティティを表現します。アカウントに複数のワークスペースを含めることができます。

アカウント管理者は、一般的なアカウント管理を取り扱い、ワークスペース管理者はアカウントにある個々のワークスペースの設定と機能を管理します。Databricks管理者の詳細については、[Databricks administration guide](https://docs.databricks.com/administration-guide/index.html)をご覧ください。管理者は以下を含むセキュリティ設定を含めたワークスペースをデプロイすることができます。

- [お使いのバーチャルプライベートクラウドにワークスペースをデプロイ](#お使いのvpcにワークスペースをデプロイ)
- [AWS PrivateLinkの有効化](#aws-privatelinkの有効化)
- [暗号化のための顧客管理キーの有効化](#暗号化のための顧客管理キーの有効化
)

## お使いのVPCにワークスペースをデプロイ

AWSのバーチャルプライベートクラウド(VPC)を用いることで、仮想ネットワークでAWSリソースを起動できるAWSクラウドの論理的に分離された区画を配備することができます。VPCがお使いのDatabricksクラスターのネットワークロケーションになります。デフォルトでは、DatabricksがDatabricksワークスペースのためにVPCを作成し、管理します。

そうではなく、Databricksクラスターをホストするために、自分のVPCを指定することができ、自分のAWSアカウントにおいて、さらなるコントロールと外部接続の制限を行うことができます。顧客管理VPCを活用するには、Databricksワークスペースを作成する際に最初にVPCを指定する必要があります。複数のワークスペースでVPCを共有することができますが、ワークスペースでサブネットを共有することはできません。詳細は、[Databricksにおける顧客管理VPC](https://qiita.com/taka_yayoi/items/f23bd799e1960e2eccbe)をご覧ください。

## AWS PrivateLinkの有効化

AWS PrivateLinkを用いることで、公衆ネットワークにトラっフィックを露出することなしに、AWSのVPCやオンプレミスネットワークからAWSサービスへのプライベートな接続を実現することができます。Databricksでは2つの接続タイプのPrivateLink接続をサポートしています。

- **フロントエンド(ユーザーからワークスペース):** フロントエンドPrivateLink接続によって、ユーザーはVPCインタフェースエンドポイントを通じてDatabricksのウェブアプリケーションやREST API、Databricks Connect APIに接続することができます。
- **バックエンド(データプレーンからコントロールプレーン):** これによって、DatabricksランタイムクラスターからDatabricksワークスペースのコアサービスへのプライベート接続を実現することができます。

詳細は、[DatabricksにおけるAWS PrivateLinkの有効化](https://qiita.com/taka_yayoi/items/c6bdbb6452f6a0895961)をご覧ください。

## 暗号化のための顧客管理キーの有効化

Databricksでは、データを保護し、アクセスを制御する役にたつ顧客管理キーの追加をサポートしています。異なるタイプのデータに対して、3つの顧客管理キーの機能があります。

- **マネージドサービス向け顧客管理キー:** Databricksコントロールプレーンのマネージドサービスのデータは格納時に暗号化されます。以下のタイプの暗号化データを保護し、アクセスをコントロールする役にたつマネージドサービス向け顧客管理キーを追加することができます。
    - コントロールプレーンに格納されるノートブックソースファイル。
    - コントロールプレーンに格納されるノートブックの実行結果。
    - シークレットマネージャAPIによって格納されるシークレット。
    - Databricks SQLのクエリーとクエリー履歴。
    - パースなるアクセストークンやDatabricks Reposを用いてGit連携のセットアップに用いられるその他の資格情報。
    
    詳細は[Databricksマネージドサービスに対する顧客管理キーの適用](https://qiita.com/taka_yayoi/items/c44d35e0e2fd76e44bbe)をご覧ください。
- **ワークスペースストレージ向け顧客管理キー:** ワークスペースを作成した際に指定したお使いのAWSアカウントのAmazon S3バケットのデータを暗号化するために、自分のキーを設定することができます。オプションとして、クラスターのEBSボリュームの暗号化に同じキーを用いることができます。詳細は、[Databricksワークスペースストレージに対する顧客管理キーの適用](https://qiita.com/taka_yayoi/items/a93cc81ed0c803401bb7)をご覧ください。

Databricksにおいて、どの顧客管理キーの機能がどのタイプのデータを保護するのかに関しては、[Customer\-managed keys for encryption](https://docs.databricks.com/security/keys/customer-managed-keys.html)をご覧ください。

# アイデンティティ

管理者によってDatabricksアカウントやワークスペースで、ユーザー、グループ、サービスプリンシパルが設定されます。[Databricksにおけるアイデンティティ管理のベストプラクティス](https://qiita.com/taka_yayoi/items/641b9c22e22071c7c17c)をご覧ください。

# セキュアなAPIアクセス

REST APIの認証において、ビルトインの停止可能なDatabricksパーソナルアクセストークンを活用することができます。ウェブアプリケーションのユーザーインタフェースや[Tokens API](https://docs.databricks.com/dev-tools/api/latest/tokens.html)でパーソナルアクセストークンを作成することができます。

ワークスペース管理者は、ワークスペースにおける現在のDatabricksパーソナルアクセストークンを確認、削除、期限の設定を行うために[Token Management API](https://docs.databricks.com/administration-guide/access-control/tokens.html)を用いることができます。ワークスペースのREST APIにアクセスするために、どのユーザーがトークンを作成、使用できるのかをコントロールするために関連する[Permissions API](https://docs.databricks.com/administration-guide/access-control/tokens.html#manage-token-permissions-using-the-permissions-api)を活用することができます。

:::note
**注意**
Databricksではトークンを用いることを強くお勧めしますが、AWSにおけるDatabricksユーザーは、Databricksのユーザー名、パスワード(ネイティブな認証)を用いてREST APIにアクセスすることもできます。[password access control](https://docs.databricks.com/administration-guide/users-groups/single-sign-on/index.html#password)を用いることで、特定のユーザーに対してネイティブ認証の許可、剥奪を行うことができます。
:::

# IPアクセスリスト

認証はユーザーアイデンティティを証明しますが、ユーザーのネットワークロケーションを強制しません。セキュリティ保護されていないネットワークからクラウドサービスにアクセスすることは、セキュリティリスクを高め、特に機微なデータ、個人情報データへのアクセスを許可するには特にリスクが高くなります。IPアクセスリストを用いることで、セキュアな環境である既存ネットワークからのみサービスへの接続を許可するように、Databricksワークスペースを設定することができます。

ワークスペース管理者は、アクセスを許可する公衆ネットワークのIPアドレス(あるいはCIDRレンジ)を指定することができます。これらのIPアドレスは外部向けゲートウェイや特定のユーザー環境に属することができます。また、ブロックするIPアドレスやサブネットを指定することができます。詳細は[IP access lists](https://docs.databricks.com/security/network/ip-access-list.html)をご覧ください。

また、Databricksワークスペースに対するすべての公衆インターネットアクセスをブロックするために、[PrivateLink](#aws-privatelinkの有効化)を活用することができます。

# 監査ログと利用量ログ

Databricksでは、Databricksユーザーによるアクティビティの監査ログへのアクセスを提供しており、詳細な利用パターンを監視することができます。2つのタイプの監査ログと利用量ログを設定することができます。

- **課金使用量ログデリバリー:** 自動で利用量ログをAWS S3バケットにデリバリーします。[Databricksの利用課金データのデリバリーとアクセス](https://qiita.com/taka_yayoi/items/90c7767025ee3feb3640)をご覧ください。
- **監査ログデリバリー:** 自動で監査ログをAWS S3バケットにデリバリーします。[Configure audit logging](https://docs.databricks.com/administration-guide/account-settings/audit-logs.html)をご覧ください。

# クラスターポリシー

インスタンスタイプ、ノード数、アタッチされるライブラリ、計算コストのような特定のクラスター設定を強制するためにクラスターポリシーを活用することができ、異なるユーザーレベルに対して異なるクラスター作成画面を表示します。ポリシーを用いてクラスター設定を管理することで、計算インフラストラクチャに対する普遍的なガバナンス制御やコストの管理を強制する役に立ちます。詳細は、[Databricksクラスターポリシーの管理](https://qiita.com/taka_yayoi/items/93d7597d7fc739b48bb7)をご覧ください。

# アクセスコントロールリスト

Databricksにおいては、ノートブック、エクスペリメント、モデル、クラスター、ジョブ、ダッシュボード、クエリー、SQLウェアハウスのようなオブジェクトにアクセスするアクセス権を設定するために、アクセスコントロールリスト(ACL)を活用することができます。すべての管理者ユーザーはアクセスコントロールリストを管理することができ、アクセスコントロールリストを管理すために権限が移譲されたユーザーもアクセスコントロールリストを管理することができます。[Access control](https://docs.databricks.com/security/access-control/index.html)をご覧ください。

皆様の企業のデータに対するアクセスの管理については、[Data governance guide](https://docs.databricks.com/data-governance/index.html)をご覧ください。

# シークレット

資格情報を格納し、ノートブックやジョブで参照するためにDatabricksシークレットを活用することができます。シークレットは外部データソースや他の計算処理で用いる秘密情報を格納するキーバリューのペアであり、[シークレットスコープ](https://qiita.com/taka_yayoi/items/b9c046e7a9106f46873a)内でキーの名称は一意なものとなります。秘密情報をハードコードしたり、平文で格納すべきではありません。

REST APIやCLIでシークレットを作成しますが、ノートブックやジョブでシークレットを読み込むには[シークレットユーティリティ(dbutils.secrets)](https://qiita.com/taka_yayoi/items/3717623187859809515d#%E3%82%B7%E3%83%BC%E3%82%AF%E3%83%AC%E3%83%83%E3%83%88%E3%83%A6%E3%83%BC%E3%83%86%E3%82%A3%E3%83%AA%E3%83%86%E3%82%A3dbutilssecrets)を使う必要があります。

あるいは、シークレットを[AWS Secrets Manager](https://aws.amazon.com/secrets-manager)に格納することができ、シークレットにアクセスするIAMロールを作成し、そのロールにクラスターのIAMロールを追加します。[Databricksにおけるインスタンスプロファイルを用いたS3バケットへのセキュアなアクセス](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)をご覧ください。

Databricksシークレットの使い方に関しては、[Databricksにおけるシークレットの管理](https://qiita.com/taka_yayoi/items/338ef0c5394fe4eb87c0)をご覧ください。

# 自動化テンプレートオプション

Databricks REST APIによって、TerraformやAWS Quick Start(CloudFormation)テンプレートを用いてセキュリティ設定タスクのいくつかを自動化することができます。これらのテンプレートは新規ワークスペースの設定やデプロイ、既存ワークスペースの管理設定のアップデートに使用することができます。特に数十のワークスペースを持つ大企業においては、テンプレートを用いることで迅速かつ一貫性のある自動設定を実現することができます。

[Automate workspace creation with Account API templates](https://docs.databricks.com/administration-guide/account-api/templates.html)をご覧ください。

# より詳細は

皆様の組織の要件に合致する包括的なセキュリティソリューションの構築に役立つリソースを以下に示します。

- Databricksレイクハウスプラットフォームのすべてのレイヤーにおいて、どのようなセキュリティが組み込まれているのかに関する情報を提供する[Databricks Security and Trust Center](https://databricks.com/trust)。
- セキュリティプラクティスのチェックリスト、デプロイメントに適用できる検討事項とパターン、エンタープライズの取り組みから得られた学びを提供する[Security Best Practices](https://www.databricks.com/wp-content/uploads/2022/09/security-best-practices-databricks-on-aws.pdf)。
- 皆様の組織でデータガバナンスのコントロールを実装するための[Databricksのデータガバナンスベストプラクティス](https://qiita.com/taka_yayoi/items/6391933db00145c2940e)。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

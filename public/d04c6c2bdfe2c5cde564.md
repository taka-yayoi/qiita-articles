---
title: Google CloudにおけるDatabricksのパブリックプレビュー機能リスト
tags:
  - Databricks
  - GoogleCloud
private: false
updated_at: '2021-04-26T10:46:51+09:00'
id: d04c6c2bdfe2c5cde564
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Databricks on Google Cloud: Public Preview feature list \| Databricks on Google Cloud](https://docs.gcp.databricks.com/release-notes/gcp-preview-features.html) [2021/4/20時点]の翻訳です。

Google Cloud上のDatabricksにおいては、[パブリックプレビュー](https://docs.gcp.databricks.com/release-notes/release-types.html)の期間、利用できない機能がいくつか存在します。本記事では、利用可能な機能と、現時点ではサポートされて居ない機能の一覧を説明します。詳細なリリースノートに関しては、[Platform release notes](https://docs.gcp.databricks.com/release-notes/product/index.html)を参照ください。

# 本リリースで提供される機能

以下の一覧には、Google CloudのDatabricksランタイムに含まれる主要な機能が含まれています。

| 機能 | 説明及びリンク |
|:--|:--|
|Databricks Runtime   |7.3 LTS以降、これにはMLランタイムも含まれます。詳細は[Databricks runtime releases](https://docs.gcp.databricks.com/release-notes/runtime/releases.html)を参照ください。   |
|Apache Spark   |Spark 3のみとなります。   |
|Optimized Delta Lake   |Delta Lakeはデータレイクに信頼性をもたらすオープンソースストレージレイヤーです。詳細は[Delta Lake and Delta Engine guide](https://docs.gcp.databricks.com/delta/index.html)を参照ください。   |
|Cluster Autopilot   |クラスターのオートスケーリング設定です。[Configure clusters](https://docs.gcp.databricks.com/clusters/configure.html)を参照ください。   |
|Jobs scheduling and workflow   |ジョブによって、ノートブックやJARを定期実行することができます。[Jobs](https://docs.gcp.databricks.com/jobs.html)をご覧ください。   |
|Notebooks and collaboration  |ノートブックはコードや可視化処理、テキストを含めることができるWebインタフェースです。[Notebooks](https://docs.gcp.databricks.com/notebooks/index.html)をご覧ください。   |
|Optimized autoscaling   |オートスケーリングは、リソースの利用量を最適化するためにワークロードの量に応じてワーカーノードを自動で増減します。[Cluster size and autoscaling](https://docs.gcp.databricks.com/clusters/configure.html#autoscaling)を参照ください。  |
|Admin console   |ワークスペース管理者が使用するコンソールです。[Administration guide](https://docs.gcp.databricks.com/administration-guide/index.html)を参照ください。   |
|Single sign-on (SSO)   |OpenIDに準拠した[Google’s OAuth 2\.0 implementation](https://developers.google.com/identity/protocols/oauth2/openid-connect)を用いて、Google Cloud Identityアカウント(あるいはGSuiteアカウント)による認証が可能です。[Single sign\-on](https://docs.gcp.databricks.com/administration-guide/users-groups/single-sign-on/index.html)を参照ください。   |
|Role-based access control   |Databricksでは、ワークスペースオブジェクト（フォルダー、ノートブック、エクスペリメント、モデル）、クラスター、プール、ジョブに対してアクセスコントロールリスト(ACL)を定義することが可能です。[Access control](https://docs.gcp.databricks.com/security/access-control/index.html)を参照ください。<br> **重要! 本リリースではテーブルのアクセスコントロールとシークレットのアクセスコントロールはサポートされていません。**   |
| Token management  | Databricks REST APIを認証する際に、パーソナルアクセストークンを作成することができます。ワークスペース管理者はトークンの利用モニタリング、アクセスコントロール、ライフタイムの設定を行うことができます。[Manage personal access tokens](https://docs.gcp.databricks.com/administration-guide/access-control/tokens.html)をご覧ください。 |
|Google Kubernetes Engine (GKE) data plane   |ワークスペースのためのワーカーネットワーク環境を含むGoogle Cloud VPC、サブネットがお客様のアカウントに作成されます。ワークスペース内の全てのDatabricksランタイムクラスターは[プライベート](https://cloud.google.com/kubernetes-engine/docs/concepts/private-cluster-concept)、[リージョナル](https://cloud.google.com/compute/docs/regions-zones#zones_and_clusters)なGoogle Kubernetes Engine (GKE)内で起動されます。GKEはKubernetesのマネージドサービスです。[GKE](https://cloud.google.com/kubernetes-engine)を参照ください。   |
| Integration with Google Cloud Identity  |OpenIDに準拠した[Google’s OAuth 2\.0 implementation](https://developers.google.com/identity/protocols/oauth2/openid-connect)を用いて、Google Cloud Identityアカウント(あるいはGSuiteアカウント)による認証が可能です。[Single sign\-on](https://docs.gcp.databricks.com/administration-guide/users-groups/single-sign-on/index.html)を参照ください。   |
|BigQuery connector   | Databricks上でGoogle BigQueryのテーブルに対して読み書きを行うことができます。[Google BigQuery](https://docs.gcp.databricks.com/data/data-sources/google/bigquery.html)を参照ください。   |
|Google Cloud Storage connector (DBFS and direct)   |Google Cloud Storage(GCS)バケットに対して、Databricks File System (DBFS)経由、あるいは`gs:`URL経由で直接読み書きを行うことができます。[Google Cloud Storage](https://docs.gcp.databricks.com/data/data-sources/google/gcs.html)を参照ください。|
|MLflow   |[MLflow](https://docs.gcp.databricks.com/applications/mlflow/index.html)はエンドツーエンドの機械学習ライフサイクルを管理するオープンソースのプラットフォームです。マネージドMLflowのサポートは、2021/3/22に追加され、Databricksランタイム8.1以降で利用できます。モデルサービングの機能は本リリースでは含まれていません。   |


# パブリックプレビューでサポートされない主要な機能

全般：

- Deltaキャッシュを含む特定のDelta Lakeの機能
- モデルサービングを含む特定のマネージドMLflowの機能
- 特定のパートナーインテグレーション
- HIPAAへの準拠
- SQL Analytics (プレビュー)
- Databricks Runtime for Genomics (代わりに、標準のDatabricksランタイムにGenomicsのライブラリをインストールします)

アカウント:

- アカウントコンソールにおける課金情報の可視化
- GCSバケットへの課金情報の出力
- APIによるワークスペース管理

ワークスペース:

- 監査ログ
- グローバルなinit script
- テーブル ACL/SQL ACL
- カスタマーマネージドなVPC
- セキュアなクラスター接続 (no public IPs)
- カスタマーマネージドな暗号化キー
- IPアクセスリスト

ノートブック:

- ノートブック、クラスターUIへのSpark UIの統合
- Jupyter notebooks
- ローカルファイルシステムへのDBFSアクセス (FUSE mount)

> **注意**
DBFSアクセスに関しては、Databricksの`dbutils`コマンド、`%fs`コマンドのようなHadoopファイルシステムAPI、Sparkのread/write APIを利用することができます。質問がある場合にはDatabricks窓口にお問い合わせください。

クラスター:

- ストレージのオートスケーリング
- クラスターポリシー
- クレディンシャルパススルー
- シングルノードクラスターモード
- GPU対応クラスター
- コンテナーサービス (自身のコンテナーの持ち込み)
- クラスターログデリバリー
- クラスターレベルのタグ
- クラスターSSH
- ローカルSSD

インテグレーション:

- CLIサポート
- Tableauコネクター (with PAT tokens)
- R Studio Server
- Databricks Connect

本リリースに含まれない主要なAPI:

- Account API
- Cluster Policies API
- DBFS API
- Global Init Script API
- Instance Pools API
- IP Access List API

Apache Spark 3.0をサポートしないサードパーティデータソース:

- Couchbase
- ElasticSearch
- Neo4j
- Redis
- Riak Time Series
- Cosmos DB

# 既知の問題

- 使用したことのないインスタンスタイプのクラスターを最初に起動する際には、起動が遅くなる場合があります。これは、特に作成直後のワークスペースで生じる可能性があります。
- Databricksはワークスペースのデプロイに用いたのと同じプロジェクトのサービスアカウントのみをサポートしています。
- Google Cloudオーガニゼーションレベルにおいて、ドメインによってアイデンティティを制限する際にGoogleオーガニゼーショナルプリシーを使う場合には、デプロイの前にDatabricksの窓口にお問い合わせください。
- ワークスペース当たり最大256クラスターの実行をサポートしています。
- GCPのクラスターイベントログに“Attempting to resize cluster to its target of ‘<number>’ workers”と言うメッセージが表示される場合がありますが、これは予測される振る舞いです。要求されたワーカーの50%が利用可能になった後に、クラスターは"running"とマークされます。一時的に、要求より少ない数のワーカーが稼働することになったとしても、ノートブックやApache Sparkのコマンドの実行を妨げることは通常ありません。
- ワークスペースを削除した際には、Databricksが作成した二つのGCSバケットが空でない場合、これらは自動で削除されません。ワークスペース削除後に、当該プロジェクトのGoogle Cloudコンソールから手動で削除できます。`https://console.cloud.google.com/storage/browser?project=<project-id>`にアクセスしてください。`<project-id>`はあなたのプロジェクトIDです。
- MavenのライブラリはDatabricks Runtime 8.1以降でのみサポートされています。


### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

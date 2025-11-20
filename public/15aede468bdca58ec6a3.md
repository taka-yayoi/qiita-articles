---
title: DatabricksのUnity Catalogとは？
tags:
  - Databricks
  - UnityCatalog
private: false
updated_at: '2022-12-20T17:26:45+09:00'
id: 15aede468bdca58ec6a3
organization_url_name: databricks
slide: false
ignorePublish: false
---
[What is Unity Catalog? \| Databricks on AWS](https://docs.databricks.com/data-governance/unity-catalog/index.html) [2022/12/9時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本書では、レイクハウスにおけるDatabricksのデータガバナンスソリューションであるUnity Catalogを紹介します。

<iframe width="560" height="315" src="https://www.youtube.com/embed/xvLJrBgogBk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

# Unity Catalogの概要

Unity Catalogでは、管理者やデータスチュワードがDatabricksアカウントにおけるすべてのワークスペースにおけるユーザーやデータへのアクセスを集中的に管理します。異なるワークスペースのユーザーは、Unity Catalogで集中的に許可される権限に基づいて同じデータに対するアクセスを共有します。
![](https://docs.databricks.com/_images/with-unity-catalog.png)

Unity Catalogの主要な機能には以下が含まれます。
- **一度定義すれば、どこでもセキュアに:** Unity Catalogは全てのワークスペース、ペルソナに対して適用されるデータアクセスポリシーを管理する唯一の場所を提供します。
- **標準準拠のセキュリティモデル:** Unity Catalogのセキュリティモデルは標準的なANSI SQLをベースとしており、管理者は馴染みのある文法を用いて、既存データレイクに存在するカタログ、データベース、テーブル、ビューのレベルでアクセス権を設定することができます。
- **ビルトインの監査機能:** Unity Catalogは自動でユーザーレベルの監査ログを捕捉し、データへのアクセスを記録します。

# Unity Catalogのオブジェクトモデル

Unity Catalogでは、主要なデータオブジェクトの階層はメタストアからテーブルに至ります。

- **メタストア:** メタデータのトップレベルのコンテナです。それぞれのメタストアはデータを整理するための3レベルの名前空間(`catalog.schema.table`)を開示します。
- **カタログ:** オブジェクト階層の最初のレイヤーであり、dーエタ資産を整理するために使用されます。
- **スキーマ:** データベースと呼ばれるものであり、スキーマはオブジェクト階層の2つ目のレイヤーであり、テーブルやビューを格納します。
- **テーブル:** オブジェクト階層の最下層であり、テーブルは*外部*(お使いのクラウドストレージ上に指定する外部ロケーションに格納)テーブルあるいは*マネージド*テーブル(お使いのクラウドストレージにおいて明示的にDatabricksで使用するために作成したストレージコンテナに格納)となります。また、テーブルから読み取り専用の**ビュー**を作成することができます。
![](https://docs.databricks.com/_images/object-model.png)

[3レベルの名前空間](https://docs.databricks.com/data-governance/unity-catalog/queries.html#three-level-namespace-notation)を用いてUnity Catalogのすべてのデータを参照することができます。

## メタストア

メタストアは、Unity Catalogにおけるトップレベルのオブジェクトコンテナです。データ資産とそれらを統治するアクセス権を格納します。どのワークロードがそれぞれのメタストアを使用するのかを制御するために、Databricksアカウント管理者はメタストアを作成し、Databricksワークスペースに割り当てることができます。ワークスペースでUnity Catalogを使う様にするには、Unity Catalogメタストアをアタッチします。

それぞれのメタストアは、お使いのAWSアカウントにあるS3バケットのルートストレージロケーションを用いて設定されます。このストレージロケーションはメタデータと[マネージドテーブル](#マネージドテーブル)のデータのために使用されます。

:::note
**注意**
このメタストアは、Unity Catalogがリリースされる前に作成されたDatabricksワークスペースに含まれているメタストアとは別物です。お使いのワークスペースにレガシーなHiveメタストアがある場合には、Unity Catalogで利用されるメタストアのデータは`hive_metastore`という名前のカタログから利用できます。
:::

[Create a Unity Catalog metastore](https://docs.databricks.com/data-governance/unity-catalog/create-metastore.html)をご覧ください。

## カタログ

カタログはUnity Catalogの3レベル名前空間の第一階層となります。データ資産を整理するために使用されます。ユーザーは、`USAGE`[データアクセス権](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)を持つすべてのカタログを参照することができます。

[Create and manage catalogs](https://docs.databricks.com/data-governance/unity-catalog/create-catalogs.html)をご覧ください。

## スキーマ

スキーマ(データベース)はUnity Catalogの3レベル名前空間の2番目のレイヤーとなります。スキーマはテーブルやビューを整理します。スキーマでテーブルやビューにアクセスする(一覧する)には、スキーマや親のカタログに対する`USAGE`データアクセス権を持ち、テーブルやビューに対する`SELECT`アクセス権を持つ必要があります。

[Create and manage schemas \(databases\)](https://docs.databricks.com/data-governance/unity-catalog/create-schemas.html)をご覧ください。

## テーブル

テーブルはUnity Catalogの3レベルの名前空間の3つ目のレイヤーに存在します。これにはデータの行が含まれます。テーブルを作成するには、ユーザーはスキーマに対する`CREATE`、`USAGE`アクセス権を持ち、親のカタログに対する`USAGE`権限を持つ必要があります。テーブルにクエリーにするには、ユーザーはテーブルに対する`SELECT`権限を持ち、親のスキーマやカタログに対する`USAGE`権限を持つ必要があります。

テーブルは*マネージド*テーブルか*外部*テーブルとなります。

### マネージドテーブル

マネージドテーブルは、Unity Catalogでテーブルを作成した際のデフォルトとなります。これらのテーブルはメタストアを作成する際にルートストレージロケーションにこれらのテーブルが格納されます。これらは、[Delta](https://docs.databricks.com/delta/index.html)テーブルフォーマットを使用します。

マネージドテーブルが削除されると、背後にあるクラウドテナント上のデータは30日以内に削除されます。

[Managed tables](https://docs.databricks.com/data-governance/unity-catalog/create-tables.html#managed-table)をご覧ください。

### 外部テーブル

外部テーブルは、ルートストレージロケーションの外にデータが格納されるテーブルです。他のツールを用いてデータに対する直接アクセスが必要な際にのみ外部テーブルを使用します。

外部テーブルを削除すると、Unity Catalogは背後のデータは削除しません。外部テーブルの権限を管理することができ、マネージテーブルと同じ様にクエリーを行うことができます。

外部テーブルには以下のファイルフォーマットを使用することができます。

- DELTA
- CSV
- JSON
- AVRO
- PARQUET
- ORC
- TEXT

[External tables](https://docs.databricks.com/data-governance/unity-catalog/create-tables.html#external-table)をご覧ください。

### ストレージ認証情報と外部ロケーション

外部テーブルの背後にあるクラウドストレージへのアクセスを管理するために、Unity Catalogでは以下のオブジェクトタイプを導入しています。

- **ストレージ認証情報(Storage credentials)** は、クラウドストレージへのアクセスを提供する長期間のクラウド認証情報をカプセル化します。例えば、S3バケットにアクセスできるIAMロールなどです。
- **外部ロケーション(External locations)** には、ストレージ認証情報とクラウドストレージパスへのリファレンスを格納します。

[Unity Catalogにおける外部ロケーションとストレージ認証情報の管理](https://qiita.com/taka_yayoi/items/18fee92365eee58e0b94)をご覧ください。

## ビュー

ビューは、メタストアにある一つ以上のテーブルやビューから作成される読み取り専用オブジェクトです。これは、Unity Catalogの[3レベル名前空間](https://docs.databricks.com/data-governance/unity-catalog/queries.html#three-level-namespace-notation)の3つ目のレイヤーに存在します。ビューは複数のスキーマやカタログに存在するテーブルやビューから作成することができます。行列レベルのアクセス権を実現する[動的ビュー](https://docs.databricks.com/data-governance/unity-catalog/create-views.html#dynamic-view)を作成することができます。

[Create a dynamic view](https://docs.databricks.com/data-governance/unity-catalog/create-views.html#dynamic-view)をご覧ください。

# Unity Catalogにおけるアイデンティティ管理

Unity Catalogはユーザー、サービスプリンシパル、グループを解決し、アクセス権を強制するために、Databricksアカウントのアイデンティティを使用します。

アカウントのアイデンティティを設定するには、[Databricksにおけるユーザー、サービスプリンシパル、グループの管理](https://qiita.com/taka_yayoi/items/e386507be44aa3abd27e)の手順に従ってください。Unity Catalogで[アクセスコントロールポリシー](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)を作成する際に、これらのユーザー、サービスプリンシパル、グループを参照します。

また、ノートブック、Databricks SQLのクエリー、Data Explorer、REST APIコマンドでUnity Catalogにアクセスするためには、Unity Catalogのユーザー、サービスプリンシパル、グループはワークスペースに追加される必要があります。このワークスペースへのユーザー、サービスプリンシパル、グループの割り当ては、*アイデンティティフェデレーション*と呼ばれます。

Unity Catalogメタストアがアタッチされたすべてのワークスペースでは、アイデンティティフェデレーションが有効になっています。

## グループに対する特別な検討

すでにワークスペースに存在しているすべてのグループは、アカウントコンソール上で**Workspace local**とラベリングされます。これらのワークスペースローカルのグループは、アクセスポリシーを定義するためにUnity Catalogで使用することはできません。アカウントレベルのグループを使用する必要があります。コマンドでワークスペースローカルのグループが参照されると、グループが見つからないというエラーが表示されます。ノートブックや他のアーティファクトへのサクセス管理にワークスペースローカルのグループを使用していた場合には、これらのアクセス権は有効のままであり続けます。

[Manage groups](https://docs.databricks.com/administration-guide/users-groups/groups.html)をご覧ください。

# Unity Catalogの管理者ロール

Unity Catalogの管理には以下の管理者ロールが必要となります。

- **アカウント管理者**は、アイデンティティ、クラウドリソース、ワークスペース作成、Unity Catalogメタストアを管理することができます。

    アカウント管理者はワークスペースでUnity Catalogを有効化することができます。ワークスペース管理者、メタストア管理者の両方の権限を付与することができます。

- **メタストア管理者**は、誰がカタログを作成できるか、テーブルにクエリーできるのか等すべてのセキュリティ保護可能オブジェクトに対する権限とオーナーシップを管理することができます。

   Unity Catalogメタストアを作成するアカウント管理者が、最初のメタストア管理者になります。また、メタストア管理者はこのロールを別のユーザーやグループに委任することができます。メタストア管理者の権限をグループの全員のメンバーが受け取れる様に、メタストア管理者をグループに割り当てることをお勧めします。[(推奨)メタストアのオーナーシップをグループに転送する](https://qiita.com/taka_yayoi/items/3f2df6ddea81521ee786#%E6%8E%A8%E5%A5%A8%E3%83%A1%E3%82%BF%E3%82%B9%E3%83%88%E3%82%A2%E3%81%AE%E3%82%AA%E3%83%BC%E3%83%8A%E3%83%BC%E3%82%B7%E3%83%83%E3%83%97%E3%82%92%E3%82%B0%E3%83%AB%E3%83%BC%E3%83%97%E3%81%AB%E8%BB%A2%E9%80%81%E3%81%99%E3%82%8B)をご覧ください。
- **ワークスペース管理者**は、Databricksワークスペースにユーザーを定義し、ワークスペース管理者ロールを割り当て、ワークスペースのオブジェクトや、クラスターを作成する権限やジョブのオーナーシップの変更など機能に対するアクセスを管理します。

[Databricksにおけるユーザー、サービスプリンシパル、グループの管理](https://qiita.com/taka_yayoi/items/e386507be44aa3abd27e)をご覧ください。

# Unity Catalogにおけるデータのアクセス権

Unity Catalogでは、デフォルトでデータは保護されています。ユーザーは最初の時点ではメタストアへのデータにアクセスすることはできません。メタストア管理者、オブジェクトのオーナー、オブジェクトを格納するカタログやスキーマのオーナーによってアクセス権を付与されます。Unity Catalogにおけるセキュリティ保護可能オブジェクトは階層的であり、権限は下流に継承されます。

Data Exploer、SQLコマンド、REST APIでアクセス権の付与、剥奪を行うことができます。

[Manage privileges in Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)をご覧ください。

# Unity Catalogにおけるクラスターアクセスモデル

Unity Catalogのデータにアクセスするには、クラスターが適切な*アクセスモード*に設定されている必要があります。Unity Catalogはデフォルトでセキュアです。クラスターがUnity Catalogに対応しているアクセスモードのいずれか(shareかsingle user)に設定されていない場合、クラスターはUnity Catalogのデータにアクセスすることができません。

[Create clusters & SQL warehouses with Unity Catalog access](https://docs.databricks.com/data-governance/unity-catalog/compute.html)をご覧ください。

# Unity Catalogにおけるデータリネージ

DatabricksクラスターやSQLウェアハウスで実行されるいかなる言語のクエリーにおける実行時のデータリネージュをキャプチャするためにUnity Catalogを活用することができます。リネージュはカラムレベルまで捕捉され、クエリーに関連するノートブック、ワークフロー、ダッシュボードが含まれます。詳細は[Unity Catalogによるデータリネージのキャプチャと参照](https://qiita.com/taka_yayoi/items/875f6684e26f13c6e48b)をご覧ください。

# 自分の組織でどのようにUnity Catalogをセットアップするのですか？

あなたの組織でUnity Catalogをセットアップするには以下の手順を踏みます。

1. Unity CatalogがあなたのAWSアカウントにデータを格納し、アクセスするために使用するS3バケットとIAMロールを設定します。
1. あなたの組織がオペレーションを行うリージョンごとにメタストアを作成し、メタストアにワークスペースをアタッチします。それぞれのワークスペースは、Unity Catalogで管理されるデータに対して同じビューを持つことになります。
1. 新規アカウントである場合には、Databricksアカウントにユーザー、グループ、サービスプリンシパルを追加します。

次に、カタログ、スキーマ、テーブルを作成し、アクセス権を付与します。

完全なセットアップ手順に関しては、[Unity Catalogを使い始める](https://qiita.com/taka_yayoi/items/3f2df6ddea81521ee786)をご覧ください。

# サポートされる計算資源

Unity CatalogではDatabricksランタイム11.1以降が動作しているクラスターが必要となります。[SQLウェアハウス](https://qiita.com/taka_yayoi/items/23d7789198c2dcd66381)ではデフォルトでUnity Catalogがサポートされています。

以前のバージョンのDatabricksランタイムはプレビューバージョンのUnity Catalogをサポートしていました。以前のバージョンのDatabricksランタイムが動作しているクラスターでは、Unity CatalogのGAの機能の全てをサポートしていません。

新しいDatabricksランタイムバージョンでアップデートされたUnity Catalogの機能に関しては、当該バージョンの[リリースノート](https://docs.databricks.com/release-notes/runtime/releases.html)を参照ください。

# サポートされるリージョン

Unity Catalogは以下のリージョンでサポートされています:

- us-east-1
- us-east-2
- us-west-1
- us-west-2
- ap-northeast-1
- ap-northeast-2
- ap-south-1
- ap-southeast-1
- ap-southeast-2
- ca-central-1
- eu-central-1
- eu-west-1
- eu-west-2

# サポートされるデータファイルフォーマット

Unity Catalogでは以下のテーブルフォーマットをサポートしています:

- [マネージドテーブル](https://docs.databricks.com/data-governance/unity-catalog/create-tables.html#managed-table)では`delta`テーブルフォーマットを使用する必要があります。
- [外部テーブル](https://docs.databricks.com/data-governance/unity-catalog/create-tables.html#external-table)では`delta`、`CSV`、`JSON`、`avro`、`parquet`、`ORC`、`text`を使うことができます。

# 制限

Unity Catalogでは以下の制限があります。

:::note
**注意**
お使いのクラスターでDatabricksランタイム11.1以前が動作している場合、さらに制限が生じることがあります。Unity CatalogのGAリリースは、Databricksランタイム11.1以降を使用することを前提としています。
:::

- Scala、R、機械学習ランタイムを用いたワークロードはシングルユーザーアクセスモードを用いたクラスターでのみサポートされています。これらの言語のワークロードでは、行列レベルのセキュリティのためのダイナミックビューをサポートしていません。
- クローンのソースやターゲットとしてUnity Catalogを使用する際、シャロークローンはサポートされません。
- Unity Catalogテーブルのバケッティングはサポートされていません。Unity Catalogでバケット化されたテーブルを作成しようとしてコマンドを実行すると、例外が発生します。
- 複数のリージョンにあるワークスペースから同じパスや同じDelta Lakeテーブルに書き込みを行う際、あるクラスターではUnity Catalogにアクセスし、他のクラスターがそうでない場合、不安定なパフォーマンスを引き起こす場合があります。
- 外部テーブルのパーティショニングはDeltaテーブルではサポートされますが、他のデータソースタイプではサポートされません。
- Unity Catalogに対するデータフレーム書き込みオペレーションの上書きモードはDeltaテーブルに対してのみサポートされ、他のフォーマットではサポートされません。ユーザーは親のスキーマにおける`CREATE`権限を持ち、既存のオブジェクトのオーナーであるか、そのオブジェクトに対する`MODIFY`権限を持たなくてはいけません。
- ストリーミングにおいては現状は以下の制限があります:
    - 共有アクセスモードを用いたクラスターではサポートされません。ストリーミングのワークロードにおいては、シングルユーザーアクセスモードを使わなくてはなりません。
    - 非同期チェックポイントはまだサポートされていません。
    - Databricksランタイム11.2以前では、all-puroposeクラスターやjobクラスターで30日以上継続するストリーミングクエリーは例外を起こします。上期間動作するストリーミングクエリーにおいては、[自動ジョブリトライ](https://docs.databricks.com/workflows/jobs/jobs.html#retries)やDatabricksランタイム11.3以降を使用してください。
- Delta Live TablesパイプラインからのUnity Catalogテーブルの参照はまだサポートされていません。
- Spark-submitジョブはシングルユーザークラスターではサポートされていますが、共有クラスターではサポートされていません。[What is cluster access mode?](https://docs.databricks.com/data-governance/unity-catalog/compute.html#access-mode)をご覧ください。
- ワークスペースで以前作成されたグループ(ワークスペースレベルのグループ)をUnity CatalogのGRANT文で使用することはできません。これは、ワークスペースを横断することがあるグループの一環的なビューを確実にするためです。GRANT文でグループを作成するには、アカウントレベルでグループを作成し、プリンシパルやグループ管理のための自動化ツール(SCIM、Okta、AADコネクター、Terraformなど)で、ワークスペースのエンドポイントではなく、アカウントエンドポイントを参照するようにアップデートします。[Difference between account groups and workspace\-local groups](https://docs.databricks.com/administration-guide/users-groups/groups.html#account-vs-workspace-group)をご覧ください。
- Unity Catalogを使うには、[E2バージョンのDatabricksプラットフォーム](https://qiita.com/taka_yayoi/items/7d209bc8d32bc5f2dba4#e2%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3)が必要です。すべての新規Databricksアカウントや多くの既存アカウントはE2です。どのアカウントタイプか不明な場合には、Databricks担当者にお問合せください。

# リソースのクオータ

Unity Catalogでは、すべてのセキュリティ保護可能オブジェクトにリソースクオータを適用します。制限はUnity Catalog全体で同じ組織階層を考慮します。これらのリソース制限を超えそうな場合には、Databricks担当者にコンタクトしてください。

以下のクオータ値はUnity Catalogの親オブジェクトに対する値として表現されます。

| オブジェクト | 親 | 値 |
|:--|:--|:--|
| テーブル  | スキーマ(データベース)  |  10000 |
| スキーマ  | カタログ  | 10000  |
| カタログ  | メタストア  | 1000  |
| ストレージ資格情報  | メタストア  |  200 |
| 外部ロケーション  | メタストア  | 500  |
| 関数  | スキーマ  |  10000 |

Delta Sharingの制限に関しては、[Resource quotas](https://docs.databricks.com/data-sharing/index.html#quotas)をご覧ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

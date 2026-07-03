---
title: Databricksクラスターの作成
tags:
  - Databricks
  - Databricksクイックスタートガイド
private: false
updated_at: '2023-08-04T13:37:33+09:00'
id: d36a469a1e0c0cebaf1b
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

[Create a cluster \| Databricks on AWS](https://docs.databricks.com/clusters/create.html) [2023/8/2時点]の翻訳です。

:::note
**注意**
これらの手順は、Unity Catalogが有効化されアップデートされたクラスターを用いた手順となっています。レガシーのクラスター作成UIにスイッチするには、クラスター作成ページの上部にある**UI Preview**をクリックし、設定をオフにします。
:::

本書では、Databricksクラスターを作成、編集する際に使用できる設定オプションを説明します。UIを用いたクラスターの作成、編集にフォーカスしています。他の手段に関しては、[Clusters CLI \(legacy\)](https://docs.databricks.com/en/archive/dev-tools/cli/clusters-cli.html)、[Clusters API](https://docs.databricks.com/api/workspace/clusters)、[Databricks Terraform provider](https://docs.databricks.com/en/dev-tools/terraform/index.html)をご覧ください。

クラスター作成ユーザーインタフェースによって、以下を含むクラスター設定を選択することができます:

- [クラスターポリシー](#クラスターポリシー)
- データを操作する際に使用されるセキュリティ機能を制御する[アクセスモード](#クラスターアクセスモードとは)
- [ランタイムバージョン](#databricksランタイムのバージョン)
- クラスターのワーカーとドライバーの[ノードタイプ](#クラスターのノードタイプ)

# クラスター作成インタフェースへのアクセス

ユーザーインタフェースを用いてクラスターを作成するには、Data Science & EngineeringかMachine Learning環境にアクセスしている必要があります。

以下のいずれかを実施することができます:

- サイドバーの![](https://docs.databricks.com/en/_images/clusters-icon.png)**Compute**をクリックし、Computeページの**Create compute**をクリックします。
- サイドバーの**New > Cluster**をクリックします。

:::note
**注意**
[クラスターを作成](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/cluster)するためにDatabricks [Terraform](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/cluster)プロバイダーを活用することもできます。
:::

# クラスターポリシー

[クラスターポリシー](https://qiita.com/taka_yayoi/items/93d7597d7fc739b48bb7)は、ユーザーがクラスターを作成する際に利用できる設定を制限するために使用される一連のルールです。クラスターポリシーには、特定のユーザーやグループが特定のポリシーにアクセスできるのかを制限できるACLがあります。

デフォルトでは、すべてのユーザーには、シングルマシンの計算リソースを作成できる[パーソナルコンピュート](https://qiita.com/taka_yayoi/items/4ccb265729775b54cca6)ポリシーへのアクセス権があります。クラスターを作成する際にパーソナルコンピュートのオプションが表示されない場合には、そのポリシーへのアクセス権がないことを意味します。パーソナルコンピュートポリシーあるいは同等の適切なポリシーへのアクセスを管理者にリクエストしてください。

ポリシーに沿ってクラスターを設定するには、**Policy**ドロップダウンからクラスターポリシーを選択します。

# クラスターアクセスモードとは？

クラスターアクセスモードは、誰がクラスターを使用でき、クラスター経由でどのデータにアクセスできるのかを制御するセキュリティ機能です。Databricksでクラスターを作成する際にはアクセスモードを選択する必要があります。

| アクセスモード | ユーザーへの表示 | UCサポート | サポート言語 | 説明 |
|:--|:--|:--|:--|:--|
| シングルユーザー  | 常時  |  Yes |  Python, SQL, Scala, R | シングルユーザーに割り当てて利用可能。ビューから読み込みを行うには、参照するすべてのテーブルとビューに対するSELECT権限を持つ必要があります。  |
| 共有  | 常時(プレミアムプランが必要)  | Yes  | Python (Databricks Runtime 11.1以降), SQL  |  ユーザー間のデータ分離を用いて、複数ユーザーで使用することが可能。[共有アクセスモードの制限](#共有アクセスモードの制限)をご覧ください。 |
| 分離なし共有  |  管理者は管理者設定ページでユーザー分離を強制することでこのクラスタータイプを非表示にすることが可能 | No  | 	Python, SQL, Scala, R  | [分離なし共有クラスターに対するアカウントレベルの関連設定](https://docs.databricks.com/en/administration-guide/account-settings/no-isolation-shared.html)があります。  |
| カスタム  | (すべての新規顧客に対しては)非表示  |  No | 	Python, SQL, Scala, R  | このオプションは、特定のアクセスモードを持たない既存のクラスターの場合にのみ表示されます。  |

クラスターのアクセスモードを**Single User**あるいは**Shared**に設定することで、既存クラスターをUnity Catalogの要件に適合させることができます。Unity Catalogにおける構造化ストリーミングにおいては、追加のアクセスモードの制限があります。[Structured Streaming support](https://docs.databricks.com/en/data-governance/unity-catalog/index.html#structured-streaming)をご覧ください。

## 共有アクセスモードの制限

- クレディンシャルパススルーはサポートされません。
- initスクリプトはサポートされません。
- Databricksランタイム13.0以前ではクラスターライブラリはサポートされません。
- クラスタースコープのPythonライブラリはDatabricksランタイム13.1以降ではサポートされます。また、ワークスペースファイルとしてアップロードされたPython wheelを利用可能ですが、DBFSルートにアップロードされたライブラリを含み、DBFSファイルパスを用いて参照されるライブラリはサポートされません。Python以外のライブラリはサポートされません。[Databricksクラスターライブラリ](https://qiita.com/taka_yayoi/items/9407356caadea3dfb47c)をご覧ください。
- Spark-submitジョブはサポートされません。
- Databricks機械学習ランタイムはサポートされません。
- Scala、R、RDD APIやDBUtilsのようにクラウドストレージからデータを直接読み込むクライアントを使用することはできません。
- ユーザー定義関数(UDF)では以下の制限があります。
    - Hive、Scala UDFを使うことはできません。
    - Databricksランタイム13.1以前では、UDAF、UDTF、Pandas on Spark(`applyInPandas`と`mapInPandas`)を含むPython UDFを使うことはできません。Databricksランタイム13.2以降ではPython UDFがサポートされています。
    - クラスターノードでのコマンドは、ファイルシステムのセンシティブな部分からのアクセスや、ポート80、443以外からのネットワーク接続の作成が禁止された低権限ユーザーとして実行しなくてはなりません。

これらの制限を回避しようとする試みは失敗します。これらの制限は、ユーザーがクラスターを通じて権限のないデータへのアクセスを拒否するために適用されています。

:::note
**注意**
- 多くのユースケースにおいては、クラスターを設定するためのinitスクリプトに変わって活用できる代替機能があります。
- ワークスペースでinitスクリプト、クラスターライブラリ、JAR、ユーザー定義関数が必要な場合には、プライベートプレビューでこれらの機能を使用する権利を得ることができるかもしれません。プライベートプレビューの使用条項とアクセスのリクエストに関しては、[こちらにサインアップ](https://docs.google.com/forms/d/e/1FAIpQLSfk6aJtTr1aGcVRuO0nusrzGpeK6VrVywhmzII7gSf56CtJ2w/viewform)してください。
:::

# Databricksランタイムのバージョン

Databricksランタイムはお使いのクラスターで実行される一連のコアコンポーネントです。すべてのDatabricksランタイムバージョンには、Apache Sparkが含まれ、使いやすさ、パフォーマンス、セキュリティを改善するコンポーネントとアップデートが追加されます。[Databricks runtimes](https://docs.databricks.com/en/runtime/index.html)をご覧ください。

クラスターを作成、編集する際に、**Databricks Runtime Version**ドロップダウンを用いて、クラスターのランタイムとバージョンを選択します。

## Photon高速化

[Photon](https://qiita.com/taka_yayoi/items/6fdbcac84f88bdd14fee)は[Databricksランタイム9\.1 LTS](https://docs.databricks.com/en/release-notes/runtime/9.1lts.html)以降で利用できます。

Photon高速化を有効化するには、**Use Photon Acceleration**チェックボックスを選択します。

必要であれば、Worker TypeとDriver Typeのドロップダウンでインスタンスタイプを指定することができます。

# クラスターのノードタイプ

クラスターは、1台のドライバーノードと0台以上のワーカーノードから構成されます。デフォルトではドライバーノードはワーカーノードと同じインスタンスタイプを使用しますが、ドライバーノードとワーカーノードで別々のクラウドプロバイダーインスタンスタイプを選択することができます。メモリーを大量に必要とするワークロードや計算を大量に行うワークロードのように、異なるユースケースに異なるファミリーのインスタンスタイプがフィットします。

## ドライバーノード

ドライバーノードはクラスターにアタッチされているノートブックのすべての状態情報を保持します。また、ドライバーノードはSparkContextを保持し、クラスター上のノートブックやライブラリから実行するすべてのコマンドを解釈し、Sparkのエグゼキューターと調整を行うApache Sparkマスターを実行します。

ドライバーノードタイプのデフォルト値はワーカーノードタイプと同じです。ノートブックでSparkワーカーから大量のデータを`collect()`し、分析を行う場合にはより大量のメモリーを持つ大規模なドライバーノードタイプを選択することができます。

:::note
**ティップス**
ドライバーノードはアタッチされているノートブックのすべての状態情報を保持するので、不要なノートブックはドライバーノードからデタッチするようにしてください。
:::

## ワーカーノード

DatabricksのワーカーノードはSparkエグゼキューターとクラスターを適切に機能させるために必要なその他のサービスを実行します。Sparkでワークロードを分散させる際、分散されたすべての処理はワーカーノードで行われます。Databricksでは1台のワーカーノードあたり1つのエグゼキューターを実行します。このため、Databricksアーキテクチャの文脈においては、エグゼキューターとワーカーの用語は同じ意味で使用されます。

:::note
**ティップス**
Sparkジョブを実行するには、最低1台のワーカーノードが必要です。クラスターにワーカーがない場合にはドライバーノードで非Sparkコマンドを実行できますが、Sparkコマンドは失敗します。
:::

### ワーカーノードのIPアドレス

Databricksはそれぞれのワーカーノードに2つのプライベートIPアドレスを付与て起動します。ノードのプライマリープライベートIPアドレスでは、Databricksの内部トラフィックをホストします。セカンダリーのプライベートIPアドレスはクラスター内通信のためにSparkコンテナによって使用されます。このモデルによって、Databrickは同じワークスペースにある複数のクラスター間の分離を実現します。

## GPUインスタンスタイプ

ディープラーニングのように高パフォーマンスを必要とする困難なタスクにおいては、GPUによって高速化されたクラスターをサポートしています。詳細については、[DatabricksのGPU有効化クラスター](https://qiita.com/taka_yayoi/items/29a3cd88b16c30002bd2)をご覧ください。

:::note alert
**警告！**
2023/8/31以降、Amazon EC2 P2インスタンスを用いたクラスターの起動をサポートしません。
:::

## AWS Gravitonインスタンスタイプ

Databricksでは、AWS Gravitonプロセッサを用いたクラスターをサポートしています。ARMベースのAWS Gravitonインスタンスは、現行世代のx86ベースのインスタンス以上のコストパフォーマンスを提供するためにAWSによって設計されています。[DatabricksのAWS Graviton有効化クラスター](https://qiita.com/taka_yayoi/items/217fcdc30e2020d9994b)をご覧ください。

# クラスターのサイズとオートスケーリング

Databricksクラスターを作成する際、クラスターに固定数のワーカーを割り当てることも、ワーカーの最小数と最大数を指定することができます。

固定サイズのクラスターを指定した際、Databricksはクラスターが指定された数のワーカーを持つことを保証します。ワーカー数の範囲を指定した場合、Databricksはジョブの実行に必要な適切な数のワーカーを選択します。これは*オートスケーリング*と呼ばれるものです。

オートスケーリングによって、Databricksは皆様のジョブの特定を考慮して動的にワーカーを再配置します。皆様のパイプラインの特定の箇所では、他よりも計算資源の需要が高い場合があり、その際にはDatabricksは皆様のジョブのこれらのフェーズを通じてワーカーを自動て追加します(そして、不要になったら削除します)。

オートスケーリングによって、ワークロードにマッチするクラスターを配備する必要がなくなるので、高いクラスターの利用率を達成することが容易になります。特にこれは、(一日を通じたデータセットの探索のように)時間と共に要件が変換するワークロードで適用されますが、要件が不明な一度限りの短時間のワークロードでも適用されることがあります。このように、オートスケーリングは以下の2つのメリットを提供します:

- 固定サイズ、リソース不足のクラスターと比較してワークロードを高速に実行。
- オートスケーリングクラスターは、静的サイズのクラスターと比較して全体コストを削減。

クラスターとワークロードの定常的なサイズに応じて、オートスケーリングは同時にこれらのメリットの一つあるいは両方を提供します。クラウドプロバイダーがインスタンスを停止した際には、クラスターサイズが選択したワーカーの最小数を下回ることがあります。この場合、Databricksはワーカーの最小数を維持するために、インスタンスの再配備をリトライします。

:::note
**注意**
`spark-submit`ジョブではオートスケーリングは利用できません。
:::

:::note
**注意**
計算資源のオートスケーリングには、構造化ストリーミングワークロードでクラスターサイズをスケールダウンする制限があります。ストリーミングワークロードでは、強化オートスケーリングを持つDelta Live Tablesを活用することをお勧めします。[What is Enhanced Autoscaling?](https://docs.databricks.com/en/delta-live-tables/auto-scaling.html)をご覧ください。
:::

## 最適化オートスケーリングと標準オートスケーリング

Databricksでは2つのタイプのクラスターノードスケーリングを提供します: 最適化と標準オートスケーリングです。最適化オートスケーリングはプレミアム、エンタープライズプランでのみ利用できます。[Platform tiers](https://www.databricks.com/jp/product/pricing/platform-addons)をご覧ください。

最適化オートスケーリングは以下で使用されます:

- すべてのジョブクラスター
- プレミアム、エンタープライズプランでDatabricksランタイムバージョン6.4以降が稼働しているインタラクティブクラスター

標準オートスケーリングは以下で使用されます:

- スタンダードプランワークスペース
- Databricksランタイム6.3以前のインタラクティブクラスター

## 最適化オートスケーリングの挙動

- 2ステップから最小値から最大値にスケールアップ。
- シャッフルファイルの状態を参照することで、クラスター外アイドル状態でなかったとしてもスケールダウンすることが可能。
- 現在のノードのパーセンテージに基づいたスケールダウン。
- ジョブクラスターでは、過去40秒以上において使用率の低いクラスターをスケールダウン。
- all-purposeクラスターでは、過去150秒以上において使用率の低いクラスターをスケールダウン。
- Spark設定プロパティ`spark.databricks.aggressiveWindowDownS`では、クラスターがどれだけの頻度でダウンスケーリングの決定を行うのかを秒で指定します。値を増やすと、クラスターのスケールダウンはよりゆっくりしたものとなります。最大値は600です。

## 標準オートスケーリングの挙動

- 8ノードの追加からスタートします。そして、指数関数的にスケールアップし、最大値に到達するには多くのステップを必要とします。
- 90%のノードが10分間ビジーでなく、クラスターが最低でも30秒アイドル状態だった場合にはスケールダウンします。
- 1ノードからスタートして、指数関数的にスケールダウンします。

## オートスケーリングの有効化と設定

お使いのクラスターを自動でリサイズするようにするためには、クラスターでオートスケーリングを有効化し、ワーカーの最小値、最大値を指定します。

Databricksが自動でクラスターのサイズを調整できる様にするには、クラスターのオートスケーリングを有効化し、ワーカーの最小値、最大値を指定します。

1. オートスケーリングを有効化します。
    - All-purposeクラスター: Create Clusterページで、**Autopilot Options**ボックスの**Enable autoscaling**チェックボックスを選択します。
![](https://docs.databricks.com/_images/autopilot-aws.png)
    - ジョブクラスター: Configure Clusterページで、**Autopilot Options**ボックスで**Enable autoscaling**を選択します。 <br>
![](https://docs.databricks.com/_images/autopilot-job-aws.png)

1. ワーカーの最小数、最大数を設定します。
![](https://docs.databricks.com/_images/workers-aws.png)

    クラスターを実行している際、クラスター詳細ページには割り当てられたワーカーの数が表示されます。割り当てられたワーカーの数とワーカー設定を比較することで、必要に応じて調整を行うことができます。

:::note warn
**重要!**
[インスタンスプール](https://docs.databricks.com/clusters/instance-pools/cluster-instance-pool.html#cluster-instance-pool)を使っているのであれば：

- プールにおける[アイドルインスタンスの最小数](https://docs.databricks.com/clusters/instance-pools/configure.html#pool-min)以下のクラスターサイズになっていることを確認してください。これよりも大きい場合、クラスターの起動時間はプールを使用しないクラスターと同じものになります。
- クラスターの最大サイズはプールの[最大キャパシティ](https://docs.databricks.com/clusters/instance-pools/configure.html#pool-max)以下になる様にしてください。
:::

## オートスケーリングの例

静的なクラスターをオートスケーリングクラスターに再設定した場合、Databricksは即時にクラスターを最小、最大の境界に収まるようにリサイズし、オートスケーリングをスタートします。例として、以下のテーブルでは特定の初期サイズのクラスターに対して、5ノード、10ノードの間にオートスケールさせるように再設定した際に何が起きるのかを示しています。

| 初期サイズ | 再設定後のサイズ |
|:--|:--|
|6   |6   |
|12   |10   |
|3  |5   |

## インスタンスプロファイル

AWSキーを使うことなしにセキュアにAWSリソースにアクセスするためには、インスタンスプロファイルを用いてDatabricksクラスターを起動することができます。インスタンスプロファイルの作成、設定方法に関しては、[Databricksにおけるインスタンスプロファイルを用いたS3バケットへのセキュアなアクセス](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)をご覧ください。インスタンスプロファイルを作成したら、**Instance Profile**ドロップダウンリストから選択します。

:::note
**注意**
インスタンスプロファイルを用いてクラスターが起動すると、このロールによってコントロールされる背後のリソースには、このクラスターへのアクセス権を持つ誰でもアクセスできるようになります。望まないアクセスを防御するには、クラスターへのアクセス権を制限するために[Cluster access control](https://docs.databricks.com/en/security/auth-authz/access-control/cluster-acl.html)を活用することができます。
:::

# ローカルストレージのオートスケーリング

クラスター作成時に固定数のEBSボリュームを割り当てたくない場合には、ローカルストレージのオートスケーリングを使用します。ローカルストレージのオートスケーリングによって、Databrikcsはお使いのクラスターのSparkワーカーで利用できるディスクの空き容量を監視します。ワーカーのディスクが減少し始めたら、ディスク空き容量が枯渇する前にDatabricksは自動で新たなEBSボリュームをワーカーにアタッチします。インスタンスあたり最大5TBのEBSボリューム(インスタンスのローカルストレージを含む)をアタッチします。

ストレージのオートスケーリングを設定するには、**Enable autoscaling local storage**を選択します。
![](https://docs.databricks.com/en/_images/autoscaling-local-storage.png)

インスタンスにアタッチされたEBSボリュームは、インスタンスがAWSに返却された場合にのみデタッチされます。すなわち、クラスターが稼働している限り、インスタンスからEBSボリュームがデタッチされません。EBS使用量をスケールダウンするには、[計算資源のオートスケーリング](#クラスターのサイズとオートスケーリング)と[自動停止](https://qiita.com/taka_yayoi/items/991aae376c089df58504#%E8%87%AA%E5%8B%95%E5%81%9C%E6%AD%A2)が設定されたクラスターでこの機能を使用することをお勧めします。

:::note
**注意**
Databricksではインスタンスのローカルストレージを拡張するためにThroughput Optimized HDD (st1)を使用します。これらのボリュームに対する[デフォルトのAWSのキャパシティ制限](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_ebs)は20TiBです。この制限に到達しないように、管理者は利用要件に基づいてこの制限の増加をリクエストする必要があります。
:::

# ローカルディスクの暗号化

:::note
**プレビュー**
この機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

クラスターを実行する際に使用するいくつかのインスタンスタイプでは、ローカルにアタッチされたディスクが存在します。Databricksは、シャッフルデータや短期データをこれらのローカルにアタッチされたディスクに保存します。クラスターのローカルディスクに一時的に保存されるシャッフルデータを含む、全てのストレージタイプにおいて保存されている全てのデータが暗号化される様に、ローカルディスクの暗号化を有効化することができます。

:::note warn
**重要!**
ローカルボリュームとの暗号化データの読み書きによるパフォーマンスのインパクトによって、ワークロードが遅くなる可能性があります。
:::

ローカルディスクの暗号化が有効化されると、Databricksはローカルにそれぞれのクラスターノードに固有の暗号化キーを生成し、ローカルディスクに保存される全てのデータの暗号化にキーを使用します。キーのスコープはそれぞれのクラスターノード固有で、クラスターノードとともに破棄されます。このライフタイムの期間において、暗号化、複合化のためにキーはメモリー上に保持され、ディスク上に暗号化された状態で格納されます。

ローカルディスクの暗号化を有効化するには、[Clusters API](https://docs.databricks.com/dev-tools/api/latest/clusters.html)を使用する必要があります。クラスターの作成、編集の際に以下を設定します。

```json:JSON
{
  "enable_local_disk_encryption": true
}
```

これらのAPIの呼び出し方の例含めたCluster APIのリファレンスに関しては、[Create](https://docs.databricks.com/dev-tools/api/latest/clusters.html#clusterclusterservicecreatecluster)、[Edit](https://docs.databricks.com/dev-tools/api/latest/clusters.html#clusterclusterserviceeditcluster)を参照ください。

以下がローカルディスク暗号化を有効化したcluster createの呼び出し例です。

```json:JSON
{
  "cluster_name": "my-cluster",
  "spark_version": "7.3.x-scala2.12",
  "node_type_id": "r3.xlarge",
  "enable_local_disk_encryption": true,
  "spark_conf": {
    "spark.speculation": true
  },
  "num_workers": 25
}
```

# クラスタータグ

クラスタータグによって、皆様の組織における様々なグループで使用されるクラウドリソースのコストを容易にモニタリングできるようになります。クラスターを作成する際にキーバリューのペアとしてタグを指定することができ、DatabricksではVMやディスクボリュームのようなクラウドリソースやDBU使用量レポートにこれらのタグを適用します。

プールから起動されたクラスターでは、カスタムのクラスタータグはDBU使用量レポートにのみ適用され、クラウドリソースには伝播しません。

プールとクラスタータグがどのように動作するのかに関しては、[Monitor usage using cluster and pool tags](https://docs.databricks.com/en/administration-guide/account-settings/usage-detail-tags.html)をご覧ください。

クラスタータグを設定するには:

1. **Tags**セクションで、カスタムタグごとにキーバリューペアを追加します。
1. **Add**をクリックします。

# AWSの設定

クラスターのAWSインスタンスを設定する際、アベイラビリティゾーン、最大のスポット価格、EBSボリュームタイプを選択することができます。これらの設定は、**Advanced Options**トグルの中の**Instance**タブにあります。

## アベイラビリティゾーン

この設定によって、クラスターで使用したいアベイラビリティゾーン(AZ)を指定することができます。デフォルトでは、この設定は**auto**となっており、ワークスペースのサブネットで利用できるIPに基づいてAZが自動で選択されます。AWSがキャパシティ不足エラーを返した際には、Auto-AZは他のアベイラビリティゾーンでリトライします。

お客様の組織で特定のアベイラビリティゾーンでリザーブドインスタンスを購入している場合には、クラスターに対して特定のアベイラビリティゾーン(AZ)を選択することは特に有用となります。詳細に関しては[AWS availability zones](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html)を参照ください。

## スポットインスタンス

スポットインスタンスを使用し、オンデマンドインスタンスの価格に対するパーセンテージとしてスポットインスタンスを起動する際に使用するスポットインスタンスの最高価格を指定することができます。デフォルトでは、オンデマンド価格の100%が最高価格となります。詳細は[AWS spot pricing](https://aws.amazon.com/ec2/spot/)を確認ください。

## EBSボリューム

ここでは、ワーカーノードのデフォルトEBSボリューム設定、シャッフルボリュームの追加方法、Databtricksが自動でEBSボリュームを配置する様に設定する方法を説明します。

EBSボリュームを設定するには、クラスター設定の**Instances**タブをクリックし、**EBS Volume Type**ドロップダウンリストからオプションを選択します。

### デフォルトEBSボリューム

Databricksはすべてのワーカーノードに対して以下のEBSボリュームを配備します。

- ホストのオペレーティングシステムとDatabricksの内部サービスでのみ使用される30GBの暗号化EBSインスタンスルートボリューム。
- Sparkワーカーで使用される150GBの暗号化EBSコンテナルートボリューム。ここでSparkサービスとログがホストされます。
- (HIPAAのみ)Databricks内部サービス向けのログを格納する75GBの暗号化EBSワーカーログボリューム。

### EBSシャッフルボリュームの追加

シャッフルボリュームを追加するには、EBSボリュームタイプドロップダウンリストで**General Purpose SSD**を選択します。

デフォルトでは、Sparkのシャッフルはインスタンスのローカルディスクに出力されます。ローカルディスクを持たないインスタンスタイプにおいて、あるいは、Sparkのシャッフルストレージスペースを拡張したい場合には、追加のEBSボリュームを指定することができます。これは特に、Sparkジョブが大容量のシャッフルアウトプットを生成する際に、ディスクスペースエラーを防ぐために有効です。

Databricksはオンデマンド、スポットインスタンスの両方でEBSボリュームを暗号化します。詳細は、[AWS EBS volumes](https://aws.amazon.com/ebs/features/)を参照ください。

### (オプション)顧客管理キーによるDatabricks EBSボリュームの暗号化

オプションで、クラスターのEBSボリュームを顧客管理キーで暗号化することができます。

[Databricksワークスペースストレージに対する顧客管理キーの適用](https://qiita.com/taka_yayoi/items/a93cc81ed0c803401bb7)を参照ください。

### AWS EBSの制限

全てのクラスターにおける全てのワーカーに対するランタイムの要件を十分に満足できる様にAWS EBSのリミットが十分に高いものであることを確認してください。デフォルトのEBSリミットに関する情報、および、リミットの変更方法に関しては、[Amazon Elastic Block Store \(EBS\) Limits](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_ebs)を参照ください。

### AWS EBS SSDボリュームタイプ

AWS EBS SSDのボリュームタイプに対してgp2あるいはgp3を選択することができます。これを行うためには、[Manage SSD storage](https://docs.databricks.com/administration-guide/clusters/manage-ssd.html)を参照ください。gp2に比べてコストを削減できるのでgp3に切り替えることをお勧めします。

:::note
**注意**
デフォルトでは、Databricksではgp3ボリュームのIOPSとスループットIOPSを同じボリュームサイズのgp2ボリュームの最大パフォーマンスにマッチするように設定します。
:::

gp2、gp3に関する技術情報については、[Amazon EBS volume types](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html)を参照ください。

# Spark設定

Sparkジョブをファインチューニングするには、クラスター設定で[Spark configuration properties](https://spark.apache.org/docs/latest/configuration.html)をカスタマイズします。

1. クラスター設定ページで**Advanced Options**トグルをクリックします。
1. **Spark**タブをクリックします。
![](https://docs.databricks.com/_images/spark-config-aws.png)
**Spark config**で、一行ごとにキーバリューのペアとして設定プロパティを入力します。

[Clusters API](https://docs.databricks.com/dev-tools/api/latest/clusters.html)を用いてクラスターを設定する際には、[Create cluster request](https://docs.databricks.com/dev-tools/api/latest/clusters.html#clustercreatecluster)あるいは[Edit cluster request](https://docs.databricks.com/dev-tools/api/latest/clusters.html#clustereditcluster)における`spark_conf`フィールドにSparkプロパティを設定します。

全てのクラスターに対してSparkプロパティを設定するには、[グローバルinitスクリプト](#https://docs.databricks.com/clusters/init-scripts.html#global-init-script)を使用します。

# シークレットからSpark設定プロパティの取得

パスワードの様なセンシティブな情報は平文ではなく[シークレット](https://docs.databricks.com/security/secrets/secrets.html)に保存することをお勧めします。Spark設定でシークレットを参照するには、以下の構文を使用します。

```ini:ini
spark.<property-name> {{secrets/<scope-name>/<secret-name>}}
```

例えば、`secrets/acme_app/password`のシークレットに保存されている値を、`password`というSpark設定プロパティに設定するには以下の設定を行います。

```ini:ini
spark.password {{secrets/acme-app/password}}
```

詳細については、[Syntax for referencing secrets in a Spark configuration property or environment variable](https://docs.databricks.com/security/secrets/secrets.html#path-value)をご覧ください。

# 環境変数

クラスターで動作する[initスクリプト](https://docs.databricks.com/clusters/init-scripts.html)からアクセスできる環境変数を設定することができます。また、Databricksではinitスクリプトで使用できる定義済み[環境変数](https://docs.databricks.com/clusters/init-scripts.html#env-var)を提供しています。定義済み環境変数を上書きすることはできません。

1. クラスター設定ページで、**Advanced Options**トグルをクリックします。
1. **Spark**タブをクリックします。
1. **Environment Variables**フィールドに環境変数を設定します。
![](https://docs.databricks.com/_images/environment-variables.png)

Clusters APIエンドポイントの[Create cluster request](https://docs.databricks.com/dev-tools/api/latest/clusters.html#clustercreatecluster)や[Edit cluster request](https://docs.databricks.com/dev-tools/api/latest/clusters.html#clustereditcluster)の`spark_env_vars`フィールドを使って環境変数を設定することもできます。

# クラスターログデリバリー

クラスターを作成する際、Sparkドライバーノード、ワーカーノード、イベントに対するログを配信する場所を指定することができます。指定された場所に5分間隔でログが配信されます。クラスターが停止されると、Databricksはクラスターが停止されるまでに生成された全てのログが配信されることを保証します。

ログの格納場所はクラスターIDに依存します。指定された場所が`dbfs:/cluster-log-delivery`の場合、`0630-191345-leap375`に対するクラスターログは`dbfs:/cluster-log-delivery/0630-191345-leap375`に配信されます。

クラスターログ配信の場所を設定するには、以下の手順を踏みます。

1. クラスター設定ページで、**Advanced Options**トグルをクリックします。
1. **Logging**タブをクリックします。
![](https://docs.databricks.com/_images/log-delivery-aws.png)
1. destinationのタイプを選択します。
1. クラスターログのパスを入力します。

## 配信先のS3バケット

S3を格納場所に選択した際には、バケットにアクセスできる様に設定されたインスタンスプロファイルをクラスターに設定する必要があります。このインスタンスプロファイルには`PutObject`と`PutObjectAcl`の両方が必要となります。サンプルのインスタンスプロファイルを以下に示します。どのようにインスタンスプロファイルを設定するのかについては、[Databricksにおけるインスタンスプロファイルを用いたS3バケットへのセキュアなアクセス](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)を参照ください。

```json:JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<my-s3-bucket>"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::<my-s3-bucket>/*"
      ]
    }
  ]
}
```

:::note
**注意**
この機能はREST APIでも使用できます。[Clusters API](https://docs.databricks.com/dev-tools/api/latest/clusters.html)と[Cluster log delivery examples](https://docs.databricks.com/dev-tools/api/latest/examples.html#cluster-log-example)を参照ください。
:::


### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

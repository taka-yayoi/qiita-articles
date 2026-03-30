---
title: ファイルイベントを用いたDatabricksのAuto Loader - 大規模ファイル発見をシンプルに
tags:
  - Databricks
  - autoloader
private: false
updated_at: '2026-03-30T16:26:06+09:00'
id: 8219aeafe1f69ad0fcc6
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Auto Loader with File Events \- Simplified File Dis\.\.\. \- Databricks Community \- 151203](https://community.databricks.com/t5/technical-blog/auto-loader-with-file-events-simplified-file-discovery-at-scale/ba-p/151203)の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

![autoloader-file-events-banner.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9ec7fc13-bc0b-45f3-a5bb-7380219d229a.png)

**サマリー**

- Auto Loaderとファイルイベントによって、ディレクトリ一覧のシンプルさと従来の通知パフォーマンスのどちらかを選択する必要性を排除することで、どのようにクラウドストレージの取り込み処理をシンプルにするのかを学びます。
- 権限の簡素化、クラウドプロバイダーの制限の緩和、自動リソース管理を含む、従来の通知と比較したファイルイベントのアーキテクチャ上の違いとメリットを明らかにします。
- 移行する際のファイルイベントの有効化方法、ファイルイベントによる最適なファイル検知を達成するためのベストプラクティスを学びます。

Databricksのお客様は、大規模なクラウドストレージにアクセスするためにAuto Loaderを活用しています。そして、今では[ファイルイベント](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/file-events-explained)がAuto Loaderを次のレベルに引き上げます - シンプルなセットアップ、自動化されたライフサイクル管理、シームレスなスケーラビリティと共にインクリメンタルかつ通知ベースの処理によるスピードと効率性を提供します。結果として、より高速な取り込み、より少ない運用のオーバーヘッド、あなたのデータの成長に合わせて成長するインフラストラクチャを手に入れることができます。

# クラウドストレージ取り込みの課題

歴史的に、Databricksのお客様はAuto Loaderの2つのモードのいずれかを選択してきました。[ディレクトリ一覧](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/directory-listing-mode)はセットアップが簡単ですが、すべての新規ファイルを特定するためにクラウドストレージのディレクトリを繰り返しスキャンする必要があるので、ファイルボリュームが大きくなると高コストかつ遅くなる場合があります。[従来の通知](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/file-notification-mode)はより効率的ですが、通知リソース(SQSやEvent Gridなど)のセットアップのための権限を必要とし、それらはUnity Catalog経由で許可される必要があります。

また、クラウドプロバイダーは単一のストレージコンテナあたりのイベント通知の数に[制限](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/file-notification-mode)を設けています。従来の通知を設定したそれぞれのAuto Loaderジョブは自身のキュー/サブスクリプションを必要とするので、AWS/GCPでは100ジョブ、Azureでは500ジョブのキャップが存在します。最後に、お客様はストリームが作成、削除されるとそれらのリソースのライフサイクルを手動で管理しなくてはなりません。

これらのパイプラインをオーケストレートするには、多くのお客様は新規ファイルがクラウドストレージに到着するとパイプラインのジョブを自動でスタートするファイル到着トリガーを使用しています。そいかし、ファイル到着トリガーは歴史的にディレクトリ一覧に依存しているので、10,000オブジェクト以内のクラウドストレージディレクトリのみをサポートしています。

# ファイルイベントを用いたAuto Loaderのご紹介

[ファイルイベント](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/file-events-explained)は、あなたのためにクラウド通知のインフラストラクチャを管理することでこれらのハードルを排除します - ディレクトリ一覧のシンプルさと従来の通知のパフォーマンスを提供します。また、ファイルイベントによってスケーラブルなファイル到着トリガーが可能となり、すべてのサイズのクラウドストレージディレクトリをベースとして自動でジョブを実行できるようになります。

外部ロケーションでファイルイベントが有効化されると、Databricksマネージドのサービスが通知リソースを作成し、通知を読み込み、キャッシュします。Auto Loaderは前回の処理ファイルから再開する効率的なAPIを用いて、このキャッシュから新規ファイルをインクリメンタルに特定します。

このサービスはUnity Cataloggで許可された権限を使用するので、ユーザーは通知のインフラストラクチャを設定したり、複雑なパラメータを調整したり、キュートサブスクリプションのライフサイクルを管理する必要がありません。そして、外部ロケーション全体に対してそれぞれのAuto Loaderストリームではなく単一のキューを用いることことで、バケット単位の通知制限を容易に回避できます。

## ハイレベルなアーキテクチャデザインの比較

![blog-1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4a08f9d5-4cee-4b4a-a510-e8330e499e74.png)
**従来の通知のハイレベルなAuto Loaderアーキテクチャ**

従来の通知では、それぞれのAuto Loaderストリームあるいはジョブには個別のサブスクリプションとキューが必要となります。このセットアップは、これらすべてのストリームが同じストレージコンテナやバケットを指していたとしても必要となります。

![blog-2.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1aaa7f22-e28a-4ffe-8c66-b45ccbf51880.png)
**ファイルイベントのハイレベルなAuto Loaderアーキテクチャ**

## ファイルイベントアーキテクチャのディープダイブ

`cloudFiles.useManagedFileEvents`を有効化すると、システムが取り込みの面倒な作業を自動化します。

1. **セットアップ:** 外部ロケーションでファイルイベントを有効化すると、Databricksは必要なクラウドサブスクリプションとキューを作成します。
    1. デフォルトですべての新規外部ロケーションではファイルイベントが有効化されています。外部ロケーションでファイルイベントを有効化する際、そのロケーションを支えるストレージ資格情報には、クラウドサブスクリプションとキューを作成する権限が必要です。必要な権限が許可されていない場合、ユーザーはエラーを受け取ります。必要な権限については[こちら](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/file-notification-mode)をご覧ください。
    1. シンプルにするために、Databricksでは「マネージド」キュー(すべてをセットアップするためにストレージ資格情報にユーザーが権限を付与します)を使うことをお勧めしています。しかし、ご自身のキューを持ち込むことも可能です - この場合、ストレージ資格情報にはキューから読み込みを行うための権限が必要になります。
1. **ファイルの公開:** これは、あなたのクラウドストレージロケーションに取り込まれ、処理される必要のあるファイルです。
1. **通知の公開:** ファイルイベントを有効化すると、通知が公開されるサブスクリプションサービス(SNSやEvent Grid)が作成されます。
1. **キューへの公開:** サブスクリプションサービスのイベントはキューに公開されます。
1. **ファイルイベントの取得:** Databricksのファイルイベントサービスがキューからメッセージを読み込みます。
1. **ファイルメタデータの格納:** キューから読み込まれたメッセージがキャッシュされます。
1. **オブジェクトの一覧:** `cloudFiles.useManagedFileEvents`が`true`に設定されてAuto Loaderストリームが実行されると、ファイルイベントキャッシュからイベントをインクリメンタルに読み込み、処理します。
    1. Auto Loaderストリームが初回実行されると、既存ファイルのリストをキャッシュするためにロードパスのディレクトリ一覧を実行します。以降はインクリメンタルに実行されます。
    1. 将来的にファイルが損なわれないようにするために、外部ロケーションでは定期的にディレクトリ一覧も実行されます。(これは自動で管理されるので、Auto Loaderの設定`cloudFiles.backfillInterval`は不要となり、この設定は無視されます。)

## 従来の通知とファイルイベントの比較

| 機能 | 従来の通知 | ファイルイベント |
|:--|:--|:--|
| クラウドインフラストラクチャ  | それぞれのAuto Loaderストリームが自身専用のクラウドツーチリソースをセットアップ(ストリームごとのSNSトピックやSQSキューなど)。  | Databricksが外部ロケーションごとに単一の通知リソース(キュー/サブスクリプション)をセットアップ。  |
| 通知サービス  | Auto Loaderストリームが自身専用のクラウドキューから直接読み込み。  | Auto Loaderストリームが、単一のクラウドキューから供給されるDatabricksファイルイベントサービスのキャッシュから読み込み。  |
| クラウドリソースの制限  | ストレージコンテナごとの通知リソース数に制限(コンテナ/アカウントごとに100/500など)を適用。一つのストリームが一つのキューにマッピング。  | 外部ロケーションごとに単一のキューを用いることでクラウドの制限を回避。多数のストリームを単一のキューにマッピング可能。  |
| 権限  | 専用のクラウド通知リソースを作成、管理するためにそれぞれのストリームに必要な権限を設定。  | 外部ロケーション向けにUnity Catalogのストレージ資格情報を通じて必要な権限を付与。ストリーム御tに追加の権限は不要。  |
| ライフサイクル管理  | ユーザーは、ストリームが削除、フルリフレッシュされた際に度々、通知リソース(キュー/サブスクリプション)の管理が必要。  | Databricksが自動でクラウド通知リソースのライフサイクルを管理。  |

## 実践: ファイルイベントを用いたAuto Loaderがどのようにお客様を支援するのか

**パフォーマンス & シンプルさ**

- **パフォーマンスがシンプルさと出会う:** 従来の通知の効率性とディレクトリ一覧のシンプルさで悩む必要はもうありません。ファイルイベントとAuto Loaderが両方を提供します。
- **高コストで遅いディレクトリ一覧の排除:** 今現在Auto Loaderをディレクトリ一覧モードで使っているのであれば、ファイルイベントに移行することで非常に大きなパフォーマンス改善を得られるはずです。これは、Auto Loaderストリームが新規ファイルを特定するためにロードパスに対して定期的にディレクトリ一覧を行う必要がないためです。
- **ファイル検知にチューニング不要:** ファイル発見に関する様々な設定をチューニングする必要がありません(従来の通知におけるfetchParallelism、backfillIntervalなど)。

**権限**

- **ストリームごとの追加の権限が不要:** 初回のAuto Loaderストリームを実行するサービスプリンシパルやユーザーはサブスクリプション/キューを作成する権限を持つ必要はありません。読み込みを行う入力データパスに対する権限のみが必要です。

**運用のオーバーヘッド**

- **ストリームごとではなく外部ロケーションごとに一つのキュー:** 従来の通知と異なり、それぞれのAuto Loaderストリームごとにキューを作成する必要はありません。これによって、ストレージコンテナに対する通知の制限にヒットすることを回避する助けとなります。外部ロケーションごとに一つのキューとストレージイベントサブスクリプションをセットアップするだけです。
- **自動クラウドリソースライフサイクル管理:** クラウドで作成したイベントサブスクリプションやキューのライフサイクル(Auto Loaderストリームが削除、完全リフレッシュされた際など)をそれほど心配する必要はありません。これらのリソースは、(ストレージ資格情報に権限があれば)外部ロケーションでファイルイベントが無効化されると自動で削除されます。

従来の通知からファイルイベントに移行する方法に関しては[こちら](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/migrating-to-file-events)をご覧ください。

# ファイルイベントの設定: クイックガイド

- すべての新規外部ロケーションはデフォルトでファイルイベントが有効化されています。既存の外部ロケーションでは、編集ページや新規外部ロケーション作成ページで **「高度なオプション」** を選択します。
![screenshot-1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8b580fa8-28bc-43bd-b1cb-14250b15be2c.png)
- **ファイルイベントタイプ**を選択します。あなたのためにDatabricksにサブスクリプションをセットアップさせたい場合には、「**Automatic**」(推奨)を選択します。自分でキューを設定したのであれば、「**Provided**」を使用します。作成をクリックします。
- 最後に、ファイルイベントが正しく有効化されたことを確認するために、数秒後に外部ロケーションページで「**Test connection**」をクリックします。
![screenshot-2.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/26bdcf68-eb7a-4d22-9e74-23803e282a79.png)

## 例

こちらがファイルイベントを用いたAuto Loaderストリームの例となります:

```py
stream_df = (spark.readStream.format("cloudFiles")
 .option("cloudFiles.format", "json")
 .option("cloudFiles.maxFilesPerTrigger", 5000)
 .option("cloudFiles.schemaLocation", f'{chekpoint_path}/schema')
 .option("cloudFiles.useManagedFileEvents", True)
 .load(f'{volume_path}')
 .writeStream
 .queryName("file-events-stream")
 .option("checkpointLocation", f"{chekpoint_path}")
 .trigger(processingTime='30 seconds')
 .table(f"{target_table}")
)
```

現在Spark宣言型パイプラインを使っており、`STREAMING TABLE`を含むパイプラインがすでにあるのであれば、`cloudFiles.useManagedFileEvents`オプションを含むように更新します。

```sql
CREATE OR REFRESH STREAMING TABLE <table-name>
AS SELECT <select clause expressions>
    FROM cloud_files("abfss://path/to/external/location/or/volume",
                     "<format>", 
                      map(
			        ...
                          "cloudFiles.useManagedFileEvents", "True",
                          ...))
```

Spark設定としてこれを設定します:

```py
spark.conf.set("spark.databricks.cloudFiles.useManagedFileEvents", "true")
```

## ベストプラクティス

同じ外部ロケーションで複数のサブディレクトリに対するボリュームを作成しましょう。

- 特定の外部ロケーションに複数のサブディレクトリがあり、それらのサブディレクトリそれぞれからデータを取り込む複数のAuto Loaderストリームがあるのであれば、ファイルイベントでより高速なファイル特定を行うようにこれらのサブディレクトリのそれぞれに対してボリュームを作成、使用しましょう。　[最適なファイル検出のためにボリュームを使用する](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/file-events-explained#%E6%9C%80%E9%81%A9%E3%81%AA%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E6%A4%9C%E5%87%BA%E3%81%AE%E3%81%9F%E3%82%81%E3%81%AB%E3%83%9C%E3%83%AA%E3%83%A5%E3%83%BC%E3%83%A0%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B)をご覧ください。
- 注意: 外部ロケーション全体から読み込みを行う単一のAuto Loaderの場合には適用されません。

## 取り込みジョブを最適化するためにファイル到着トリガーを活用

- ファイル到着トリガーやスケジュールを用いて、継続的に実行するためにAuto Loaderジョブを起動することができます。
- [ファイル到着トリガー](https://docs.databricks.com/aws/ja/jobs/file-arrival-triggers#%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E5%88%B0%E7%9D%80%E3%83%88%E3%83%AA%E3%82%AC%E3%83%BC%E3%81%AF%E3%81%A9%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E6%A9%9F%E8%83%BD%E3%81%97%E3%81%BE%E3%81%99%E3%81%8B)は、クラウドストレージに新規ファイルが出現した際にのみジョブを実行するので、多くの場合ベストな選択肢となります - あなたのインクリメンタルな取り込みを補完するための真にイベント駆動のオーケストレーションを実現します。
- ファイルイベントによってファイル到着トリガーは劇的に高性能になります:

|  | ファイルイベントが無効化 | ファイルイベントを有効化 |
|:--|:--|:--|
| ファイル追跡の制限  | ディレクトリあたり最大1万ファイル  |  無制限 |
| ワークスペースあたりのファイル到着トリガーの数  | 最大50  |  無制限 |

# まとめ

- 現在ディレクトリ一覧のAuto Loaderを使っているのであれば、ファイルイベントへの移行をお勧めします。
- 従来の通知モードのAuto Loaderを使っており、秒間2000ファイル以下の取り込みであるならば、ファイルイベントへの移行をお勧めします。
- ファイルイベントはAWS、Azure、GCPでGAとなっています。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

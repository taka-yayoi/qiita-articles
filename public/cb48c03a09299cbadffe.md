---
title: Azure DatabricksとAzure Data Factoryで90以上のデータソースに接続する
tags:
  - Databricks
  - AzureDataFactory
  - AzureDatabricks
private: false
updated_at: '2022-05-09T09:23:14+09:00'
id: cb48c03a09299cbadffe
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[How to Simply Scale ETL with Azure Data Factory and Azure Databricks](https://databricks.com/blog/2020/03/06/connect-90-data-sources-to-your-data-lake-with-azure-databricks-and-azure-data-factory.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

[データレイク](https://databricks.com/discover/data-lakes/introduction)によって、企業は様々な種類のデータソースに対するセキュアかつタイムリーなアクセスを通じて、定常的に価値を提供することが可能になりました。このジャーニーにおける最初のステップは、堅牢なデータパイプラインを用いて取り込み処理をオーケストレーションし自動化することとなります。データのボリューム、種類、速度が急激に増加するにつれて、データを抽出、変換、ロード(ETL)するための高信頼かつセキュアなパイプラインへのニーズが高まりました。]

Databricksのユーザーは月当たり2エクサバイト(20億Gバイト)以上のデータを処理しており、[Azure Databricks](https://databricks.com/jp/product/azure)は現在Microsoft Azure上で急激に成長しているデータ&AIサービスとなっています。Azure Databricksと他のAzureサービスの間の密連携によって、お客様はデータ取り込みパイプラインをシンプルにし、スケールすることが可能となります。例えば、Azure Active Directoryとのインテグレーションによって、一貫性のあるクラウドベースのIDとアクセス管理を実現します。また、Azure Data Lake Storage (ADLS)との連携によって、[ビッグデータ分析](https://databricks.com/jp/glossary/big-data-analytics)に対して高いスケーラビリティを持つセキュアなストレージを提供し、Azure Data Factory (ADF)を用いることで、大規模ETLをシンプルにするハイブリッドなデータ統合を実現します。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_01.jpg)
図: Azure Data FactoryとAzure DatabricksによるバッチETL

# 単一のワークフローによるデータへの接続、取り込み、変換

ADFには[90以上のビルトインデータソースコネクター](https://docs.microsoft.com/ja-jp/azure/data-factory/connector-overview)が含まれており、お使いの全てのデータソースに接続するためにシームレースにAzure Databricksノートブックを実行し、単一のデータレイクに取り込みます。また、ADFは信頼性のあるデータパイプラインの作成を支援するビルトインのワークフローコントロール、データ変換、パイプラインのスケジュール、データインテグレーション、そして、その他の機能も提供しています。ADFを用いることで、お客様は生のフォーマットのデータを取り込み、Azure DatabricksとDelta Lakeを用いることで、お使いのデータをブロンズ、シルバー、ゴールドテーブルに変換します。例えば、[お使いのデータレイクに対するSQLクエリー](https://databricks.com/p/webinar/using-sql-to-query-your-data-lake-with-delta-lake)を実行できるようにし、[機械学習のためのデータパイプライン](https://databricks.com/blog/2019/08/14/productionizing-machine-learning-with-delta-lake.html)を構築するために、お客様は多くのケースでAzure DatabricksとDelta Lakeを活用しています。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_02.jpg)

# Azure DatabricksとAzure Data Factoryを使ってみる

Azure Data Factoryを用いてAzure Databricksノートブックを実行するためには、Azureポータルに移動し、"Data factories"を検索し、新規データファクトリーを定義するために"create"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_03.jpg)

次に、データファクトリーの一意の名前を指定し、サブスクリプションを選択し、リソースグループとリージョンを選択します。"Create"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_04.jpg)

作成が終わったら、新規データファクトリーを参照するために"Go to resource"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_05.jpg)

"Author & Monitor"タイルをクリックすることで、Data Factoryのユーザーインタフェースを開きます。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_06.jpg)

Azure Data Factoryの"Let’s get started"ページから、左のパネルの"Author"ボタンをクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_07.jpg)

次に、画面下部の"Connections"をクリックし、"New"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_08.jpg)

"New linked service"ペインから"Compute"タブをクリックし、"Azure Databricks"を選択し、"Continue"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_09.jpg)

Azure Databricksのリンクサービスの名前を入力し、ワークスペースを選択します。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_10.jpg)

画面の右上にあるユーザーアイコンをクリックすることで、Azure Databricksワークスペースからアクセストークンを作成します。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_11.jpg)

"Generate New Token"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_12.jpg)

リンクされたサービスのフォームにトークンをコピー&ペーストし、クラスターのバージョン、サイズ、Pythonのバージョンを選択します。設定を確認し、"Create"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_13.jpg)

リンクされたサービスが出来上がったので、パイプラインを作成する準備が整いました。Azure Data FactoryのUIから、プラス(+)ボタンをクリックし、"Pipeline"を選択します。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_14.jpg)

"Parameters"タブをクリックすることでパラメーターを追加し、プラス(+)ボタンをクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_15.jpg)

次に、"Databricks"アクティビティを展開してパイプラインにDatabricksノートブックを追加し、パイプラインのデザインキャンバス上にDatabricksノートブックをドラッグ&ドロップします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_16.jpg)

"Azure Databricks"タブを選択することで、Azure Databricksワークスペースに接続し、上で作成したリンクサービスを選択します。次に、ノートブックパスを指定するために"Settings"をクリックします。次に"Validate"ボタンをクリックし、ADFサービスに公開するために"Publish All"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_17.jpg)
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_18.jpg)

公開されたら、"Add Trigger | Trigger now"をクリックすることでパイプラインの実行を起動します。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_19.jpg)

パラメーターを確認し、パイプラインを起動するために"Finish"をクリックします。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_20.jpg)

次にパイプライン実行の進捗を確認するために、右側のパネルの"Monitor"タブに切り替えます。
![](https://databricks.com/wp-content/uploads/2020/03/ETL-on-Azure_21.jpg)

Azure DatabricksノートブックをAzure Data Factoryパイプラインにインテグレーションすることで、お使いのカスタムETLコードをパラメータ化し、本格運用するための柔軟かつスケーラブルな方法を提供します。Azure DatabricksがどのようにAzure Data Factory (ADF)とインテグレーションしているのかを学びたいのであれば、[ADFのブログ記事](https://techcommunity.microsoft.com/t5/azure-data-factory-blog/etl-in-the-cloud-is-made-easy-together-with-azure-data-factory/ba-p/1189736)や[ADFチュートリアル](https://docs.microsoft.com/en-us/azure/data-factory/transform-data-using-databricks-notebook)をご覧ください。データレイクのデータをどのように探索し、クエリーを実行するのかに関しては、こちらのウェビナー、[Using SQL to Query Your Data Lake with Delta Lake](https://databricks.com/p/webinar/using-sql-to-query-your-data-lake-with-delta-lake)をご覧ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

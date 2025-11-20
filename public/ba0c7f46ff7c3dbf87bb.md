---
title: Databricksにおける機械学習トレーニングのトラッキング
tags:
  - Databricks
  - Databricksクイックスタートガイド
private: false
updated_at: '2021-04-15T21:15:26+09:00'
id: ba0c7f46ff7c3dbf87bb
organization_url_name: databricks
slide: false
ignorePublish: false
---
> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

[Track machine learning training runs \| Databricks on AWS](https://docs.databricks.com/applications/mlflow/tracking.html) [2021/4/5時点]の翻訳です。

MLflowのトラッキングコンポーネントによって、機械学習モデルのトレーニングに関係するソース情報、パラメーター、メトリクス、タグ、アーティファクトを記録することができます。MLflowを使い始める際には、[PythonによるDatabricks MLflowクイックスタートガイド](https://qiita.com/taka_yayoi/items/dd81ac0da656bf883a34)、あるいは、[MLflow quickstart tutorials(英語)](https://docs.databricks.com/applications/mlflow/quick-start.html)を試してみてください。

MLflowのトラッキングにおいて理解すべき二つの概念があります。エクスペリメント(experiment)とラン(run)です：

- MLflowエクスペリメントは、MLflowランに対するアクセス制御、管理の基本単位となります。全てのMLflowランはエクスペリメントに属します。エクスペリメントによって、ランを可視化したり、検索することができます。また、他のツールで分析するためにアーティファクトやメタデータをダウンロードすることができます。
- MLflowランは一回のモデルコードの実行に対応づけられます。それぞれのランは以下の情報を記録します：
    - **ソース(Source)**: ランを起動したノートブック名、あるいはプロジェクト名とランのエントリーポイント。
    - **バージョン(Version)**: ノートブックから実行した場合にはノートブックのバージョン、[MLflow Project(英語)](https://docs.databricks.com/applications/mlflow/projects.html#mlflow-projects)から実行した場合にはGitコミットのハッシュ値。
    - **開始、終了時刻(Start & end time)**: ランの開始時刻、終了時刻。
    - **パラメーター(Parameters)**: キーバリュー形式で保存されるモデルのパラメーター。キー、バリューともに文字列となります。
    - **メトリクス(Metrics)**: キーバリュー形式で保存されるモデルの評価メトリクス。バリューは数値となります。ランの過程でそれぞれのメトリクスが更新(例：モデルの損失関数がどのように収束するかを追跡)され、MLflowはメトリクスの履歴を保持し、可視化することを可能とします。
    - **タグ(Tags)**: キーバリュー形式で保存されるランのメタデータ。ランの実行中、実行後にタグを更新することができます。キー、バリューともに文字列となります。
    - **アーティファクト(Artifacts)**: あらゆる形式の出力ファイル。例えば、画像、モデル(例：pickleされたscikit-learnモデル)、データファイル(例：Parquetファイル)がアーティファクトとして保存できます。

[MLflow Tracking API(英語)](https://www.mlflow.org/docs/latest/tracking.html)を用いて、モデルのランからパラメーター、メトリクス、タグ、アーティファクトを記録します。トラッキングAPIは、MLflowの[tracking server(英語)](https://www.mlflow.org/docs/latest/tracking.html#tracking-server)とやりとりをします。Databricksを使う際には、Databricksがホストするトラッキングサーバーがデータを記録します。ホストされるMLflowトラッキングサーバーは、Python、Java、RのAPIを提供します。

エクスペリメントのアクセス権管理に関しては、[MLflow Experiment permissions(英語)](https://docs.databricks.com/security/access-control/workspace-acl.html#mlflow-experiment-permissions)を参照ください。

> **注意**
MLflowはDatabricksランタイムMLクラスターにインストールされています。DatabricksランタイムクラスターでMLflowを使うには、`mlflow@ライブラリをインストールする必要があります。クラスターにライブラリをインストールするには、[Install a library on a cluster(英語)](https://docs.databricks.com/libraries/cluster-libraries.html#install-libraries)を参照ください。MLflowをインストールするのに必要なパッケージは以下の通りです：

- Pythonの場合は、**Library Source**でPyPIを選択し、**Package**フィールドに`mlflow`と入力します。
- Rの場合は、**Library Source**でCRANを選択し、**Package**フィールドに`mlflow`と入力します。
- Scalaの場合は、以下の二つのパッケージをインストールします：
    - **Library Source**でCoordinatesを選択し、**Package**フィールドに`org.mlflow:mlflow-client:1.11.0`と入力します。
    - **Library Source**でPyPIを選択し、**Package**フィールドに`mlflow`と入力します。

# MLflowランの記録の格納場所

MLflowランは、以下の方法で設定されるアクティブなエクスペリメントに記録されます。

- [mlflow\.set\_experiment\(\)コマンド(英語)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.set_experiment)を使う。
- [mlflow\.start\_run\(\)コマンド(英語)](https://www.mlflow.org/docs/latest/python_api/mlflow.html#mlflow.start_run)の`experiment_id`パラメーターで指定する。
- MLflowの環境変数の[MLFLOW\_EXPERIMENT\_NAME か MLFLOW\_EXPERIMENT\_ID(英語)](https://mlflow.org/docs/latest/cli.html#cmdoption-mlflow-run-arg-uri)に設定する。

アクティブなエクスペリメントが設定されていない場合、ランは[ノートブックのエクスペリメント](#ノートブックエクスペリメント)に記録されます。

# エクスペリメント

エクスペリメントには2種類あります。ワークスペースエクスペリメントとノートブックエクスペリメントです。

- MLflow APIかワークスペースUIからワークスペースエクスペリメントを作成できます。ワークスペースエクスペリメントはノートブックに紐付けられておらず、いかなるノートブックでもエクスペリメントIDかエクスペリメント名を指定することでランをこれらのエクスペリメントに記録することができます。
- ノートブックエクスペリメントは特定のノートブックに紐付けられています。[mlflow\.start\_run\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.start_run)を実行した際にアクティブなエクスペリメントが存在しない場合には、Databricksは自動でノートブックエクスペリメントを作成します。

エクスペリメントのアクセス権管理に関しては、[MLflow Experiment permissions(英語)](https://docs.databricks.com/security/access-control/workspace-acl.html#mlflow-experiment-permissions)を参照ください。

## エクスペリメント名の取得

エクスペリメント名をコピーするには、エクスペリメントページの上にある![](https://docs.databricks.com/_images/copy-icon.png)アイコンをクリックします。アクティブなMLflowエクスペリメントを設定するために、MLflowの`set_experiment`コマンドを用いる際にエクスペリメント名を使用できます。
![](https://docs.databricks.com/_images/get-experiment-name.png)

## ワークスペースエクスペリメント

ここでは、Databricks UIを用いたワークスペースエクスペリメントの作成方法を説明します。[MLflow API](https://mlflow.org/docs/latest/index.html)を用いて作成することもできます。

ワークスペースエクスペリメントにランを記録する方法については、[Log runs to a notebook or workspace experiment(英語)](https://docs.databricks.com/applications/mlflow/tracking.html#log-runs-to-a-notebook-or-workspace-experiment)を参照ください。

### ワークスペースエクスペリメントの作成

1. サイドバーの**Workspace**ボタン![](https://docs.databricks.com/_images/workspace-icon.png)あるいは**Home**ボタン![](https://docs.databricks.com/_images/home-icon.png)をクリックします。
1. エクスペリメントを作成したいフォルダーに移動します。
1. 以下を実行します。
    - フォルダー名の右隣にある![](https://docs.databricks.com/_images/menu-dropdown.png)をクリックし、**Create > MLflow Experiment**を選択します。
![](https://docs.databricks.com/_images/mlflow-experiments-create-aws.png)
    - ワークスペース、ユーザーフォルダーで![](https://docs.databricks.com/_images/down-caret.png)をクリックし、**Create > MLflow Experiment**を選択します。
1. Create MLflow Experimentダイアログで、エクスペリメントの名前と任意でアーティファクトの格納場所を指定します。
    - アーティファクトの格納場所を指定しない場合、アーティファクトは`dbfs:/databricks/mlflow-tracking/<experiment-id>`に格納されます。
    - アーティファクトの格納場所には[DBFS](https://qiita.com/taka_yayoi/items/e16c7272a7feb5ec9a92)、S3、Azure Blog storageを指定することができます。
    - S3にアーティファクトを保存する場合には、`s3://<bucket>/<path>`の形式でURIを指定します。MLflowはS3にアクセスするために、クラスターの[インスタンスプロファイル](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)を使用します。S3に格納されたアーティファクトは、MLflowのUIでは参照できません。オブジェクトストレージのクライアントを使用してダウンロードする必要があります。
    - Azure Blob storageにアーティファクトを保存する場合には、`wasbs://<container>@<storage-account>.blob.core.windows.net/<path>`の形式でURIを指定します。Azure Blob storageに格納されたアーティファクトは、MLflowのUIでは参照できません。Blobストレージのクライアントを使用してダウンロードする必要があります。
1. **Create**をクリックすることで、空のエクスペリメントが表示されます。

### ワークスペースエクスペリメントの参照

1. サイドバーの**Workspace**ボタン![](https://docs.databricks.com/_images/workspace-icon.png)あるいは**Home**ボタン![](https://docs.databricks.com/_images/home-icon.png)をクリックします。
1. エクスペリメントを格納したフォルダーに移動します。
1. エクスペリメント名をクリックします。

### ワークスペースエクスペリメントの削除

1. サイドバーの**Workspace**ボタン![](https://docs.databricks.com/_images/workspace-icon.png)あるいは**Home**ボタン![](https://docs.databricks.com/_images/home-icon.png)をクリックします。
1. エクスペリメントを格納したフォルダーに移動します。
1. エクスペリメント名を右にある![](https://docs.databricks.com/_images/menu-dropdown.png)クリックし、**Move to Trash**を選択します。

## ノートブックエクスペリメント

ノートブック上で[mlflow\.start\_run\(\)コマンド](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.start_run)を実行した場合、ランはアクティブなエクスペリメントにメトリクスやパラメーターを記録します。アクティブなエクスペリメントが存在しない場合、Databricksはノートブックエクスペリメントを作成します。ノートブックエクスペリメントは対応するノートブックと同じ名前とIDを持ちます。[ノートブックのURL(英語)](https://docs.databricks.com/workspace/workspace-details.html#workspace-notebook-url)の最後にある数字のIDがノートブックIDです。

ノートブックエクスペリメントにランを記録する方法については、[Log runs to a notebook or workspace experiment](https://docs.databricks.com/applications/mlflow/tracking.html#log-runs-to-a-notebook-or-workspace-experiment)を参照ください。

> **注意**
API(例：Pythonにおける`MlflowClient.tracking.delete_experiment()`)を用いてノートブックエクスペリメントを削除した場合、ノートブック自身もTrashフォルダーに移動されます。

### ノートブックエクスペリメントの参照

ノートブックエクスペリメントと関連づけられたランを参照するには、ノートブックツールバーの**Experiment**アイコン![](https://docs.databricks.com/_images/experiment.png)をクリックします。
![](https://docs.databricks.com/_images/notebook-toolbar.png)
Experiment Runsのサイドバーが表示され、ランのパラメーター、メトリクスが表示されます。
![](https://docs.databricks.com/_images/mlflow-notebook-revision.png)
エクスペリメントを表示するには、一番右の![](https://docs.databricks.com/_images/external-link.png)アイコンをクリックします。エクスペリメントページが表示されます。
![](https://docs.databricks.com/_images/quick-start-nb-experiment.png)
ランを表示するには、エクスペリメント一覧の**Start Time**をクリックします。Experiment Runsのサイドバーで、ランの日時の隣にある![](https://docs.databricks.com/_images/external-link.png)をクリックすることで、直接ランにアクセスすることができます。
![](https://docs.databricks.com/_images/quick-start-nb-run.png)
ランを生成したバージョンのノートブックを表示するには以下のいずれかを実施します。
- Experiment Runsのサイドバーで、Experiment Runのボックスにある**Notebook**アイコン![](https://docs.databricks.com/_images/notebook-version.png)をクリックします。
- ランのページで**Source**の隣のリンクをクリックします。

### ノートブックエクスペリメントの削除

ノートブックエクスペリメントはノートブックの一部であり削除することはできません。ノートブックを削除した際には、ノートブックエクスペリメントは削除されます。API(例：Pythonにおける`MlflowClient.tracking.delete_experiment()`)を用いてノートブックエクスペリメントを削除した場合には、ノートブックも削除されます。

# ラン

全てのMLflowランは、[アクティブなエクスペリメント](#mlflowランの記録の格納場所)に記録されます。明示的にアクティブなエクスペリメントを指定していない場合には、ノートブックエクスペリメントに記録されます。

## ランをノートブックエクスペリメント、ワークスペースエクスペリメントに記録する

以下のノートブックはどのようにしてノートブックエクスペリメント、ワークスペースエクスペリメントにランを記録するのかを説明しています。ノートブックの中で初期化されたMLflowランのみがノートブックエクスペリメントに記録されます。他のノートブックで起動されたMLflowランや、APIで起動されたランはワークスペースエクスペリメントに記録されます。記録されたログを参照する方法については、[ノートブックエクスペリメントの参照](#ノートブックエクスペリメントの参照)、[ワークスペースエクスペリメントの参照](#ワークスペースエクスペリメントの参照)を参照してください。

- [MLflowランのロギング \- Databricks(英語)](https://docs.databricks.com/_static/notebooks/mlflow/mlflow-log-runs.html)

## エクスペリメント内のランの参照、管理

エクスペリメント内で、格納されているランに対して様々な操作を行うことができます。

### ランのフィルタリング

パラメーターやメトリクスに基づいてランを検索することができます。あるパラメーターやメトリクスを持つランを検索するには、検索フィールドにクエリーを入力して**Search**をクリックします。以下がクエリーの例です：

`metrics.r2 > 0.3`

`params.elasticNetParam = 0.5`

`params.elasticNetParam = 0.5 AND metrics.avg_areaUnderROC > 0.3`

ランの状態(アクティブ、削除済み)、ランにモデルバージョンが関連づけられているかどうかに基づいて検索を行うことも可能です。このためには、検索ボックスの右にある**Filter**をクリックします。**State**、**Linked Models**ドロップダウンメニューが表示されますので、条件を選択します。
![](https://docs.databricks.com/_images/quick-start-nb-experiment.png)

### ランのダウンロード

1. 一つ以上のランを選択します。
1. **Download CSV**をクリックします。以下のフィールドを含むCSVファイルがダウンロードされます。

```csvs
Run ID,Name,Source Type,Source Name,User,Status,<parameter1>,<parameter2>,...,<metric1>,<metric2>,...
```

### ランの詳細表示

ランの日付リンクをクリックします。ラン詳細画面が表示されます。画面には乱で用いられたパラメーター、ランの結果得られたメトリクス、タグ、メモが表示されます。また、ランで記録されたアーティファクトにもアクセスできます。

ランに対応するノートブック、Gitプロジェクトを参照するには：

- ランがDatabricksノートブック、ジョブで実行された場合には、**Source**フィールドをクリックし、ランで使われた[ノートブックバージョン](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%83%90%E3%83%BC%E3%82%B8%E3%83%A7%E3%83%B3%E7%AE%A1%E7%90%86)を開きます。
- ランがリモートの[Gitプロジェクト(英語)](https://docs.databricks.com/applications/mlflow/projects.html#remote-run)から起動された場合には、**Git Commit**フィールドのリンクをクリックし、ランで用いられた特定バージョンのプロジェクトを表示します。**Source**フィールドのリンクは、ランで使われたGitプロジェクトのメインブランチを開きます。

ランでモデルを記録した場合には、ページ上のArtifactセクションにモデルが表示されます。Sparkデータフレーム、pandasデータフレームを用いて予測を行うために、どのようにモデルをロードして使うのかを説明するスニペットを表示させたい場合には、モデル名をクリックします。

### ランの比較

1. エクスペリメントで、ランの左にあるチェックボックスで二つ以上のランを選択します。
1. **Compare**をクリックします。選択したランを比較する画面が表示されます。
1. 以下のいずれかを実行します。
    - メトリクスのグラフを表示するにはメトリクス名をクリックします。
    - 散布図を作成するにはX-axis、Y-axisのドロップダウンでパラメーターとメトリクスを選択します。
![](https://docs.databricks.com/_images/mlflow-run-comparison.png)

### ランの削除

1. エクスペリメントで、ランの左にあるチェックボックスを選択します。
1. **Delete**をクリックします。
1. 親子関係のあるランにおいて、選択したランが親である場合、子のランも削除するのかを選択します。削除するオプションはデフォルトでオンになっています。
1. **Delete**をクリックして削除するか、**Cancel**をクリックしてキャンセルします。削除したランは30日間保持されます。削除されたランを表示するには、Stateフィールドで**Deleted**を選択します。

# Databricks外からMLflowトラッキングサーバーへのアクセス

MLflow CLIを使うなどして、Databricks外からトラッキングサーバーに対して読み書きを行うことができます。

- [Access the MLflow tracking server from outside Databricks(英語)](https://docs.databricks.com/applications/mlflow/access-hosted-tracking-server.html)

# データフレームを用いたMLflowランの分析

以下の二つのデータフレームAPIを用いてMLflowランデータにプログラムからアクセスすることができます。

- pandasデータフレームを返却するMLflow Pythonクライアントの[search\_runs API](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.search_runs)
- Apache Sparkデータフレームを返却する[MLflow experiment(英語)](https://docs.databricks.com/data/data-sources/mlflow-experiment.html#mlflow-exp-datasource)データソース

以下のサインプルノートブックでは、MLflow Pythonクライアントを用いて、過去の評価メトリクス、特定ユーザーによって実行されたランの数、全ユーザーにおけるランの総数を計測してダッシュボードで可視化しています。

- [Build dashboards with the MLflow Search API(英語)](https://docs.databricks.com/applications/mlflow/build-dashboards.html)

# サンプルノートブック

以下のノートブックにおいては、いくつかの種類のモデルをトレーニングし、MLflowでトレーニングデータを追跡、Delta Lakeに追跡データを格納する流れを説明しています。

- [Train a scikit\-learn model and save in scikit\-learn format(英語)](https://docs.databricks.com/applications/mlflow/tracking-ex-scikit.html)
- [Train a PyTorch model(英語)](https://docs.databricks.com/applications/mlflow/tracking-ex-pytorch.html)
- [Train a PySpark model and save in MLeap format(英語)](https://docs.databricks.com/applications/mlflow/tracking-ex-pyspark.html)
- [Track ML Model training data with Delta Lake(英語)](https://docs.databricks.com/applications/mlflow/tracking-ex-delta.html)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

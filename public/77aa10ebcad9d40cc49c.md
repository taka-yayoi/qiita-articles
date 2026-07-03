---
title: ユーザー向けDatabricksスタートガイド
tags:
  - Databricks
  - Databricksクイックスタートガイド
private: false
updated_at: '2022-01-27T13:13:23+09:00'
id: 77aa10ebcad9d40cc49c
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

[Get started as a Databricks Data Science & Engineering user \| Databricks on AWS](https://docs.databricks.com/getting-started/quick-start.html) [2021/5/26時点]の翻訳です。

このチュートリアルでDatabricksデータサイエンス&データエンジニアリングワークスペースをご説明します：クラスターやノートブックの作成、データセットからテーブルの作成、テーブルの検索、検索結果の表示を行います。

> **Tips**
この記事の内容を補完するために、ワークスペースにログインした後に利用できる５分程度のハンズオンを実施できるクイックスタート チュートリアル ノートブックをご確認下さい。Databricksにログインして**Explore the Quickstart Tutorial**をクリックしてください。

# 要件

Databricksにログインすることで、データサイエンス&データエンジニアリングワークスペースに入ることができます。[Sign up for a free Databricks trial(英語)](https://docs.databricks.com/getting-started/try-databricks.html)を参照ください。

# ステップ1 Databricksデータサイエンス&データエンジニアリングのUIに慣れる

![](https://docs.databricks.com/_images/landing-aws.png)

左のサイドバー、ランディングページの**Common Tasks**リストから、Databricksデータサイエンス&データエンジニアリングの基本的な構成要素にアクセスすることができます：ワークスペース、クラスター、テーブル、ノートブック、ジョブ、そしてライブラリです。ワークスペースは、ノートブックやライブラリ、インポートしたデータなどのDatabricksアセットを格納する特別なルートフォルダーです。

## サイドバーの利用

左のサイドバーからDatabricksの全てのアセットにアクセスできます。サイドバーのコンテンツは選択するペルソナ(**Data Science & Engineering**、**Machine Learning**、**Databricks SQL**)によって決まります。

- デフォルトではサイドバーは畳み込まれた状態で表示され、アイコンのみが表示されます。サイドバー上にカーソルを移動すると全体を表示することができます。
- ペルソナを変更するには、Databricksロゴの直下にあるアイコンからペルソナを選択します。
![](https://docs.databricks.com/_images/change-persona.gif)
- 次回ログイン時に表示されるペルソナを固定するには、ペルソナの隣にある![](https://docs.databricks.com/_images/persona-pin.png)をクリックします。再度クリックするとピンを削除することができます。
- サイドバーの一番下にある**Menu options**で、サイドバーの表示モードを切り替えることができます。Auto(デフォルト)、Expand(展開)、Collapse(畳み込み)から選択できます。
- 機械学習に関連するページを開く際には、ペルソナは自動的に**Machine Learning**に切り替わります。

## ヘルプの利用

ヘルプにアクセスするためには、右上のアイコン![](https://docs.databricks.com/_images/question-icon.png)をクリックします。
![](https://docs.databricks.com/_images/help-menu.png)

# ステップ2 クラスターの作成

クラスターはDatabricksの計算リソースの集合体です。クラスターを作成するには：

1. サイドバーの**Clusters**ボタンをクリックします。
![](https://docs.databricks.com/_images/clusters-icon.png)

1. クラスターページで、Create Clusterをクリックします。
![](https://docs.databricks.com/_images/quickstart-cluster.png)

1. クラスター作成ページで、クラスター名**Quickstart**を指定して、Databricksランタイムバージョンドロップダウンから**7.3 LTS (Scala 2.12, Spark 3.0.1)**を選択します。
1. **Create Cluster**をクリックします。

# ステップ3 ノートブックの作成

ノートブックはApache Sparkクラスターでの処理を実行するセルの集合体です。ワークスペースでノートブックを作成するには：

1. サイドバーで**Workspace**ボタンをクリックします。
![](https://docs.databricks.com/_images/workspace-icon.png)
1. ワークスペースのフォルダーで![](https://docs.databricks.com/_images/down-caret.png)をクリックし、**Create > Notebook**を選択します。
![](https://docs.databricks.com/_images/create-notebook.png)
1. ノートブック作成ダイアログで、名前を入力し、言語ドロップダウンでは**SQL**を選択します。この選択が、ノートブックのデフォルト言語を決定します。
1. **Create**をクリックします。先頭のセルが空白のノートブックが開きます。

# ステップ4 テーブルの作成

Databricksクラスターにインストールされた分散ファイルシステム[Databricks File System \(DBFS\)](https://qiita.com/taka_yayoi/items/e16c7272a7feb5ec9a92)にマウントされたデータセットコレクションである[Databricks datasets(英語)](https://docs.databricks.com/data/databricks-datasets.html#databricks-datasets)のサンプルCSVファイルからテーブルを作成します。テーブルを作成するには2つの選択肢があります。

## オプション1: CSVデータからSparkテーブルを作成する

標準的なパフォーマンスで十分で、すぐにテーブルを作りたいのであればこちらのオプションとなります。以下のスニペットをノートブックセルに貼り付けます。

```sql
DROP TABLE IF EXISTS diamonds;

CREATE TABLE diamonds USING CSV OPTIONS (path "/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv", header "true")
```

## オプション2: CSVデータをDelta Lake形式で書き込み、Deltaテーブルを作成する

[Delta Lake(英語)](https://docs.databricks.com/delta/index.html)は、高速な読み込み、その他のメリットを提供する強力なトランザクショナルストレージレイヤーです。Delta LakeフォーマットはParquetファイルとトランザクションログから構成されます。将来的なパフォーマンスを見据えた場合に最適な選択肢となります。

CSVデータをデータフレームに読み込み、Delta Lake形式で書き込みを行います。このコマンドでは、Pythonの[言語マジックコマンド](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E6%B7%B7%E6%88%90%E8%A8%80%E8%AA%9E)を使用し、ノートブックのデフォルト言語(SQL)以外の言語の処理を組み込みます。以下のコードスニペットをノートブックセルに貼り付けます。


```python
%python

diamonds = spark.read.csv("/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv", header="true", inferSchema="true")
diamonds.write.format("delta").save("/mnt/delta/diamonds")
```

格納場所にDeltaテーブルを作成します。 以下のコードスニペットをノートブックセルに貼り付けます。

```sql
DROP TABLE IF EXISTS diamonds;

CREATE TABLE diamonds USING DELTA LOCATION '/mnt/delta/diamonds/'
```

**SHIFT + ENTER**を押してセルを実行します。ノートブックは自動的にステップ2で作成したクラスターにアタッチされ、セル内のコマンドが実行されます。

# ステップ5 テーブルを検索

色ごとのダイヤモンドの平均価格を計算するSQL分を実行します。

1. セルの下にある![](https://docs.databricks.com/_images/add-cell.png)をクリックして、ノートブックにセルを追加します。
![](https://docs.databricks.com/_images/quick-start-new-cell.png)

1. 以下のスニペットをセルに貼り付けます。

```sql
SELECT color, avg(price) AS price FROM diamonds GROUP BY color ORDER BY COLOR
```
**SHIFT + ENTER**を押してセルを実行します。ダイヤモンドの色と平均価格が表示されます。
![](https://docs.databricks.com/_images/diamonds-table.png)

# ステップ6 データの表示

色ごとの平均ダイヤモンド価格の図を表示します。

1. バーチャートアイコン![](https://docs.databricks.com/_images/chart-button.png)をクリックします。
1. **Plot Options**をクリックします。
    - **color**をKeysボックスにドラッグします。
    - **price**をValuesボックスにドラッグします。
    - Aggregationドロップダウンで**AVG**を選択します。
![](https://docs.databricks.com/_images/diamonds-plot-options.png)

1. **Apply**をクリックしバーチャートを表示します。

# 次のステップ

ここまでで、クラスターの作成、ノートブックの作成、ノートブック上でのSQLコマンドの実行、結果の表示を行い、Databricksワークスペースの基礎を学ぶことができました。

- Apache Sparkに関する文献に関しては、[Introduction to Apache Spark(英語)](https://docs.databricks.com/getting-started/spark/index.html)を参照ください。
- Databricksワークスペースで使用する主要なツールの理解を深めたいのであれば、以下をご覧ください：
    - [Databricksワークスペースのコンセプト](https://qiita.com/taka_yayoi/items/78bf647c40a906d90db0)
    - [ワークスペース(英語)](https://docs.databricks.com/workspace/index.html)
        - [ノートブック(英語)](https://docs.databricks.com/notebooks/index.html)、[可視化(英語)](https://docs.databricks.com/notebooks/visualizations/index.html)
        - [ライブラリ(英語)](https://docs.databricks.com/libraries/index.html)
    - [クラスター(英語)](https://docs.databricks.com/clusters/index.html)、[ジョブ(英語)](https://docs.databricks.com/jobs.html)
    - [Introduction to importing, reading, and modifying data(英語)](https://docs.databricks.com/data/data.html#access-data)、[Databases and tables(英語)](https://docs.databricks.com/data/tables.html#tables)
- Databricksワークスペースの利用例を見るには、こちらの動画を参照ください。
    - [Data Exploration with Databricks on Vimeo](https://vimeo.com/137874931)
    - [Visualizations in Databricks on Vimeo](https://vimeo.com/156886721)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

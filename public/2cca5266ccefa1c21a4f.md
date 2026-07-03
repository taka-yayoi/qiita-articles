---
title: 無料のDatabricks Community Editionを使ってXGBoostを試してみる
tags:
  - xgboost
  - Databricks_Community_Edition
  - Databricks
private: false
updated_at: '2024-07-27T15:58:32+09:00'
id: 2cca5266ccefa1c21a4f
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらでは、無料で利用できるDatabricks Community Editionを用いて、分類の一手法であるXGBoostを使って、特徴量からアヤメ(iris)を種類を特定(分類)するとともに、Databricksの画面や機能に慣れていただきます。

こちらの続編となります。前回は一年前でした。

https://qiita.com/taka_yayoi/items/ce4179b9b829365714b7

一年経つと、GUIも結構変わっているので新たなGUI含めてウォークスルーしていきます。

今回使うノートブックはこちらです。

https://sajpstorage.blob.core.windows.net/yayoi/ce-xgboost-python.html

[こちら](https://docs.databricks.com/ja/machine-learning/train-model/xgboost.html)をベースにしています。

全体の流れは以下のようになります。

1. Databricks Community Editionへのサインアップ
1. 計算資源の作成
1. ノートブックの作成
1. XGBoostによるアヤメの分類

ここで行う分類とは、アヤメの特徴量からアヤメのクラス(種類)を推定するという処理を指しています。

- **特徴量:** アヤメのがく(sepal)や花びら(petal)の幅や長さ
- **クラス:** Setosa、Versicolour、Virginica

# Databricksとは

[Databricks](https://databricks.com/jp)は、Apache Spark™、Delta Lake、MLflowの開発者グループによって2013年に創業されたデータ&AIカンパニーです。Databricksの[データインテリジェンスプラットフォーム](https://www.databricks.com/jp/blog/what-is-a-data-intelligence-platform)は、組織全体でのデータとAIの活用を促進させ、[データレイクハウス](https://www.databricks.com/jp/glossary/data-lakehouse)を基盤とするプラットフォームが、あらゆるデータとガバナンス要件をサポートするオープンな統合環境を提供します。

:::note
**参考資料**
- [データインテリジェンスプラットフォーム](https://www.databricks.com/jp/product/data-intelligence-platform)
- [Databricksの良いところ\(Jupyter notebookとの比較\)](https://qiita.com/taka_yayoi/items/d5ea3dede05a180091b2)
- [データレイクハウスに関するFAQ](https://qiita.com/taka_yayoi/items/04888e5fd08a621511e4)
- [Databricksのアーキテクチャ](https://qiita.com/taka_yayoi/items/7d209bc8d32bc5f2dba4)
:::

# Databricks Community Editionとは

Databricksではその機能を無償でお試しいただけるよう、2通りの方法を用意しております。

- 2週間の無償トライアル: Databricksのすべての機能を2週間無償でお試しいただけます。
- **Community Edition**: 利用できる機能が限定されますが、**期限なし・無償**でご利用いただけます。

本記事では、**Community Edition**でのDatabricksの基本的な機能を体験いただきます。

:::note
**参考資料**
- [IBJP: Community Editionで始めるDatabricks – Databricks](https://databricks.com/jp/international-blogs/get-started-with-databricks-community-edition-jp)
- [Databricksフリートライアルへのサインアップ](https://qiita.com/taka_yayoi/items/fb4f57c069e1f272e88a)
:::

# Databricks Community Editionへのサインアップ

1. https://databricks.com/jp/try-databricks にアクセスします。必要な情報を入力します。**続行**をクリックします。
![Screenshot 2024-07-27 at 11.44.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8580d81c-cc98-6f3c-820e-5f6d9179de79.png)
1. **Community Editionのトライアルを開始**をクリックします。
![Screenshot 2024-07-27 at 11.44.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/951d2183-2e7d-3903-7aea-0610b4b0e2b8.png)
1. クイズが出るので人間であることを証明しましょう。
![Screenshot 2024-07-27 at 11.44.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3e8f4e18-5319-0621-ebf9-978dab55dba1.png)
1. 認証のためのメールが送信されます。
![Screenshot 2024-07-27 at 11.45.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3b1e6ff6-7d58-f5d6-9e7a-8b3a12f621e6.png)
1. **Welcome to Databricks! Please verify your email address.** というメールが届くので、**Get started by visiting**のリンクをクリックします。
![Screenshot 2024-07-27 at 11.49.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/700d1269-da94-9c30-54a2-89dde0b19e1b.png)
1. パスワードを設定します。
![Screenshot 2024-07-27 at 11.51.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/af741088-1b9f-ff98-0414-f9fb07ac38ba.png)
1. これでDatabricks Community Editionにログインできました。
![Screenshot 2024-07-27 at 11.52.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6a7814b1-cb7c-c058-a9f6-f46735d7ecf2.png)

## Databricks Community Editionの画面構成

Databricksでは、ノートブック上にロジックを記述してそれを実行することで様々な処理を行います。この観点ではJuypter notebookと非常に近いUIを持っていると言えます。しかし、[様々な点で強化・拡張](https://qiita.com/taka_yayoi/items/d5ea3dede05a180091b2)がなされているのがDatabricksです。

画面の左側のサイドメニューにマウスカーソルを移動するとメニューが展開されます。基本的な機能にはこちらからアクセスすることになります。
![Screenshot 2024-07-27 at 11.55.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a191125e-aa23-aa36-0710-245abcd880be.png)


各項目については、以下の参考資料をご覧ください。ここでは、クラスターを作成するためにメニューから**クラスター**をクリックします。

:::note
**参考資料**
- [ワークスペース内を移動する \| AWS 上の Databricks](https://docs.databricks.com/ja/workspace/index.html)
:::

:::note info
GUIが英語になっている場合は、こちらを参考に日本語に変更してください。

1. 画面右上のユーザーアイコンをクリックし、**Settings**を選択。
![Screenshot 2024-07-27 at 12.27.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4b6eebbb-7a18-69be-4810-d13a42722a64.png)
1. **User**配下の**Preferences**をクリック。
![Screenshot 2024-07-27 at 12.28.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/01f59a81-9edd-1e03-4c04-62a911a1e283.png)
1. **Language**から日本語を選択。
![Screenshot 2024-07-27 at 12.29.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/90ee7384-3900-754d-fb2d-d44fdf620d95.png)
![Screenshot 2024-07-27 at 12.29.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/021769c1-f8c4-5dbd-1225-b5739459450d.png)
1. ホームページに戻るには画面左上のdatabricksロゴをクリックします。
:::


## クラスターの作成

[クラスター(コンピュート)](https://docs.databricks.com/ja/compute/use-compute.html)とは、機械学習モデルのトレーニングやデータの加工を行う際に必要となる計算資源です。Databricksでは大量のデータを高速に処理できるように複数の仮想マシンをまとめて**クラスター**として構成します。Databricksクラスターを用いることで、従来であれば手間のかかる環境構築(仮想マシンの設定、ソフトウェアのインストールなど)をGUIからの操作で手軽に行えるようになります。

1. クラスターの一覧が表示されます。この時点ではクラスターは存在していないため一覧は空の状態です。左上にある**コンピューティングを作成**ボタンをクリックします。
![Screenshot 2024-07-27 at 11.57.38.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d05d665c-04d0-a0b6-d0ec-387bd04ee67f.png)


1. この画面で作成するクラスターの設定を行います。ここでは、**クラスター名**と**Databricks Runtimeのバージョン**を指定します。

    - **クラスター名**: 人が見てわかりやすい名前を指定してください。
    - **Databricks Runtimeのバージョン**: [Databricks Runtime](https://docs.databricks.com/ja/compute/configure.html#databricks-runtime-versions)とはクラスターに自動でインストールされるソフトウェアのパッケージです。Pythonの実行環境やPythonライブラリなどが含まれています。ここでは、`Runtime 15.3 ML`を選択します。

    ![Screenshot 2024-07-27 at 11.58.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c48249f1-b9b0-b140-a5d6-9088cec63bf8.png)
    ![Screenshot 2024-07-27 at 11.59.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/deea3fa4-10b3-3819-2cec-297ef4611e32.png)

1. 画面下の**コンピューティングを作成**をクリックするとクラスターが作成されます。クラスターが作成され、起動するまでに数分要しますのでお待ちください。作成が完了するとクラスター名の右側に緑のチェックマーク入りのアイコンが表示されます。
![Screenshot 2024-07-27 at 12.21.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/05656cd7-05e8-ecd4-0f49-a664baf1d285.png)


## ノートブックの作成

次に、ロジックを記述する[ノートブック](https://docs.databricks.com/ja/notebooks/index.html)を作成します。

1. サイドメニューの**ワークスペース**をクリックします。ワークスペースは名前の通り、皆様の作業場でありノートブックを格納する場所となります。
1. ホームフォルダは自分のメールアドレスの名称となっています。ここにフォルダを作成したり、ノートブックを格納することになります。
![Screenshot 2024-07-27 at 12.16.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e93af2b9-d129-74ff-eaa4-5f18e22c2797.png)
1. ホームフォルダ名(自分のメールアドレス)の右にある**作成**をクリックしてノートブックを選択します。
![Screenshot 2024-07-27 at 12.17.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/db8080d5-0647-404b-6359-4df98bff89cd.png)
1. ノートブックの右上の**接続**からクラスターを選択します。Databricksで処理を実行するには、ノートブックをクラスターに**アタッチ**する必要があります。編集のみを行う際にはクラスターへのアタッチは不要です。
![Screenshot 2024-07-27 at 12.21.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c148bade-c1cb-7e18-92ef-d53560a31f2b.png)
1. これで準備が整いました。
![Screenshot 2024-07-27 at 12.22.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/95fc97bb-2ce1-1c2c-9ce9-7bcac877496c.png)

:::note info
**ティップス**
フルバージョンのDatabricksではフォルダやノートブックなどにアクセス権を設定できるので、ユーザー間でセキュアに資産のやり取りを行うことができます。
:::

## ノートブックの実行

すでにノートブックが表示されていますので、Juypter notebookを使うのと同様にPythonの処理を記述、実行することができます。

1. 一つ目のセルにカーソルを移動し、以下の内容を記述します。

    ```py:Python
    print("test")
    ```

1. セルを実行するにはいくつかの方法がありますが、ここではセルの左上の再生ボタンをクリックします。
![Screenshot 2024-07-27 at 12.22.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a7728be1-9b61-2361-dd37-eebd46772de7.png)
1. 以下のように結果が表示されます。
![Screenshot 2024-07-27 at 12.23.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cc3fbc7e-8265-46ce-ebb3-37728e60a708.png)

:::note info
**ティップス**
上に表示されているように、Shift+Enterキーを押してもセルを実行することができます。
:::

新たにセルを追加するには、追加したいセルの上部あるいは下部にカーソルを移動すると`+コード`や`+テキスト`が表示されるのでこれをクリックすることでセルの上下に追加することができます。
![Screenshot 2024-07-27 at 12.24.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b1a8e97f-c677-0623-1271-36693e2cbf56.png)
![Screenshot 2024-07-27 at 12.24.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bf142e7c-8e39-4b8d-377c-a747782847ad.png)

:::note
**参考資料**
- [Databricksノートブックでコードを開発する \| Databricks on AWS](https://docs.databricks.com/ja/notebooks/notebooks-code.html)
- [ノートブックの管理｜Databricks on AWS](https://docs.databricks.com/ja/notebooks/notebooks-manage.html)
:::

# XGBoostを試してみる

## XGboostとは

https://aiacademy.jp/media/?p=1604

> XGBoost（eXtreme Gradient Boosting / 勾配ブースティング回帰木）とは、アンサンブル学習の一つで、ブースティングと決定木を組み合わせています。
> 
> ブースティングとは、弱いモデル（弱学習器と呼びます）を複数作成し、一つ前の学習器の誤りを次の学習器が修正するという操作を繰り返し行うことで性能を向上させる手法です。
> 
> 勾配ブースティング回帰木では、浅い決定木を複数作成し、それぞれの決定木はデータの一部に対してしか良い予測を行うことができないため、ブースティングを行うことで性能を向上させています。パラメータ設定に敏感という欠点がありますが、正しく設定すればランダムフォレストよりも良い性能となります。
> 
> また、XGBoost（勾配ブースティング回帰木）の名前に「回帰木」とありますが、回帰と分類のどちらでも使用可能です。

## ノートブックのインポート

上ではノートブックを作成しましたが、インターネットで公開されているノートブックなどを簡単に取り込むこともできます。

1. サイドメニューの**ワークスペース**をクリックします。
1. ホームフォルダ名(自分のメールアドレス)の右にある(3つの点が縦に並んでいる)三点リーダーをクリックします。メニューが表示されるので**インポート**を選択します。
![Screenshot 2024-07-27 at 12.30.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/10d8da3b-e62b-8786-8053-5f59f0b9ded8.png)
1. ダイアログが表示されます。以下を指定して**インポート**をクリックします。
![Screenshot 2024-07-27 at 12.31.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/66d72704-ae22-6f81-0786-23cb9f9c2547.png)

    インポート元: `URL`を選択します。
    テキストボックス: 以下のURLを貼り付けます。

    ```
    https://sajpstorage.blob.core.windows.net/yayoi/ce-xgboost-python.html
    ```
1. 以下のようにノートブックがインポートされます。
![Screenshot 2024-07-27 at 12.32.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/63d61f15-3b85-df6c-b1fe-4854c991fbca.png)
1. 画面右上で[上のステップ](#クラスターの作成)で作成したクラスターを選択します。

## ノートブックを実行

### データの準備

```py
# ライブラリのインポート
import pandas as pd
import xgboost as xgb
```

```py
# 分析データのコピー
dbutils.fs.cp('dbfs:/databricks-datasets/Rdatasets/data-001/csv/datasets/iris.csv', 'file:/tmp/iris.csv')
```

今回使用するデータは以下のような構造となっています。

- `sepal length`: 萼(がく)の長さ
- `sepal width`: 萼(がく)の幅
- `petal length`: 花びらの長さ
- `petal width`: 花びらの幅
- `class`: アヤメの種類

```py
# pandasライブラリを使用してirisデータセットを読み込む
raw_input = pd.read_csv("/tmp/iris.csv",
                        header=0,
                        names=["item", "sepal length", "sepal width", "petal length", "petal width", "class"])
# 不要な列を削除
new_input = raw_input.drop(columns=["item"])
# クラス列をカテゴリ型に変換
new_input["class"] = new_input["class"].astype('category')
# クラス名を数値インデックスに変換
new_input["classIndex"] = new_input["class"].cat.codes
# 編集後のデータフレームを表示
display(new_input)
```

上で使用している`display`関数はDatabricks固有のものです。pandasデータフレームやSparkデータフレームを可視化することができます。[こちら](https://docs.databricks.com/ja/visualizations/index.html)を参考に色々なグラフを作ってみてください。
![Screenshot 2024-07-27 at 12.36.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f6f3d49c-c85d-dea7-ba60-9dec0829f25f.png)
![Screenshot 2024-07-27 at 12.37.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/17e24e6f-a555-b348-9268-7c0c0dd7ac07.png)
![Screenshot 2024-07-27 at 12.37.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e6d9a079-38a9-a5e4-1acd-ff2cebe6d34b.png)

```py
from sklearn.model_selection import train_test_split
# new_inputデータフレームを訓練データとテストデータに分割
# トレーニングには訓練データのみを使用し、精度検証にテストデータを使用します
training_df, test_df = train_test_split(new_input)
```

### Pandasデータフレームを用いたXGBoostモデルのトレーニング

```py
# 訓練データをXGBoostのDMatrix形式に変換
dtrain = xgb.DMatrix(training_df[["sepal length","sepal width", "petal length", "petal width"]], label=training_df["classIndex"])
```
```py
param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'multi:softmax'}
param['nthread'] = 4  # スレッド数を4に設定
param['eval_metric'] = 'auc'  # 評価指標をAUCに設定
param['num_class'] = 6  # 分類するクラスの数を6に設定
```
```py
num_round = 10
# パラメータと訓練データを使ってXGBoostモデルを訓練する
bst = xgb.train(param, dtrain, num_round)
```

上のセルを実行すると、`MLflowで1件のランのジョブがエクスペリメントに記録されました。`というメッセージが表示されます。Databricksで機械学習モデルをトレーニングすると、インテグレーションされている[MLflow](https://www.databricks.com/jp/product/managed-mlflow)が自動でモデルを記録してくれます。右上のフラスコマークに注目すると、グリーンのドットが表示されています。クリックしてみましょう。
![Screenshot 2024-07-27 at 12.39.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6bf1f4c4-e36b-67ae-29a0-27cc05e934a4.png)

記録されているモデルを確認することができます。どのような情報が記録されているのかを確認してみましょう。
![Screenshot 2024-07-27 at 12.41.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/007902d2-f1fd-f3d2-6353-3a36020c4fd7.png)
![Screenshot 2024-07-27 at 12.42.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c9641262-b7a1-4e91-223e-bc5ea647104e.png)
![Screenshot 2024-07-27 at 12.43.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0b27b25a-4898-3bcd-50af-d7092ba874f5.png)

### 予測

特徴量からアヤメの種類を予測します。

```py
# テストデータフレームから特徴量を選択してDMatrixを作成
dtest = xgb.DMatrix(test_df[["sepal length","sepal width", "petal length", "petal width"]])
# 訓練済みモデルを使って予測を実行
ypred = bst.predict(dtest)
ypred
```

```
array([0., 1., 0., 0., 1., 1., 1., 2., 1., 2., 0., 0., 1., 2., 2., 2., 0.,
       1., 2., 2., 0., 0., 1., 2., 1., 2., 1., 1., 0., 0., 0., 0., 0., 1.,
       0., 1., 2., 1.], dtype=float32)
```

```py
# nparrayをpandasデータフレームに変換
df_pred = pd.DataFrame(ypred, columns = ["prediction"], index=test_df.index)

# 予測結果とテストデータを結合
# classIndexとpredictionが一致している場合、正しく予測(分類)できたことを意味します
df_result = pd.concat([test_df, df_pred], axis=1)
display(df_result)
```
![Screenshot 2024-07-27 at 15.55.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d1cbea7d-ebe7-150c-4c6c-a170e7907cce.png)

予測したアヤメの種類が実際のデータと一致しているのかどうかを確認します。`precision_score`で正解率を計算します。

```py
# sklearnからprecision_scoreをインポート
from sklearn.metrics import precision_score

# 予測結果の精度を計算
pre_score = precision_score(test_df["classIndex"], ypred, average='micro')

# 精度スコアを表示
display("xgb_pre_score: {}".format(pre_score))
```
```
'xgb_pre_score: 0.8947368421052632'
```

:::note
**参考資料**
- [MLflow を使用した機械学習ライフサイクル管理 \| Databricks on AWS](https://docs.databricks.com/ja/mlflow/index.html)
:::

お疲れ様でした！Databricksに興味を持たれた方はこちらもご覧ください。

- [はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)
- [Databricksドキュメント \| Databricks on AWS](https://docs.databricks.com/ja/index.html)
- [Databricks ブログ](https://www.databricks.com/jp/blog)
- [Databricks記事のまとめページ\(その1\) \#Databricks \- Qiita](https://qiita.com/taka_yayoi/items/c6907e2b861cb1070f4d)
- [Databricks記事のまとめページ\(その2\) \#Databricks \- Qiita](https://qiita.com/taka_yayoi/items/68fc3d67880d2dcb32bb)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

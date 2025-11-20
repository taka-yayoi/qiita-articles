---
title: 時系列解析のためのDatabricks Tempoへのディープダイブ
tags:
  - Databricks
  - tempo
private: false
updated_at: '2022-09-16T12:05:40+09:00'
id: 2a5beabd82fc4aaf2aea
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Deep Dive into Databricks Tempo for Time Series Analytics](https://blogs.perficient.com/2021/06/17/deep-dive-into-databricks-tempo-for-time-series-analytics/)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

多くの場合、時系列データは他のタスク向けで使用しているどの様なデータベースにも完全にはフィットしませんでした。マーケットには時系列データベース(TSDB)が存在しています。TSDBは時刻と値の関連づけられたペアの格納と取得に最適化されています。TSDBのアーキテクチャはタイムスタンプデータの格納にフォーカスしており、圧縮、要約、ライフサイクル管理はこの構成にカスタマイズされています。通常、我々はピカピカの新たなTSDBには移行しようとはせず、単にParquetファイルを使用します。[Databricks](https://databricks.com/jp)は、[Parquet](https://parquet.apache.org/)(特に[Delta](https://github.com/delta-io/delta))ファイルに対する[Spark](https://spark.apache.org/)による時系列処理をシンプルにするオープンソースプロジェクトであるTempoをリリースしました。

# Tempoは何をするのか？

エントリーポイントは時系列データフレーム(TSDF)のオブジェクトとなります。タイムスタンプのカラムは必須となります。パーティション、シーケンスカラムはオプションですが、自動特徴量生成を含むさまざまなユースケースで役立ちます。TSDFを用いることで、いくつかのネイティブな機能を活用できる様になります。

- Asof join - ソーステーブルの最新のレコードをselectし、ベースのファクトテーブルにマージするためにウィンドウを使用します。
- 移動平均 - Approximate Exponential Moving AverageとSimple Moving Averageを利用できます。
- 再サンプリング - 頻度に基づくアップサンプリングと集計関数

コードを詳細に見ると、特定のユースケースに取り組むためのコードの基盤を使用する追加の機能が記述されていることがわかりました。

# Tempoはどの様に動作するのか？

[tsdf\.py](https://github.com/databrickslabs/tempo/blob/master/python/tempo/tsdf.py)を見ると、データフレームとタイムスタンプのカラム、オプションで1つ以上のパーティションカラム、シーケンスカラムを指定する必要があることがわかります。タイムスタンプカラムはソートに使用されます。オプションのパーティションカラムやシーケンスカラムは特徴量生成に使用されます。タイムスタンプカラムは文字列である必要がありますが、パーティションカラムは文字列あるいは文字列のリストである必要があります。

TSDFをDeltaテーブルに書き込む際には、write関数を呼び出してTDSFとSparkのコンテキスト、Deltaテーブル名と最適化のためのカラム(あれば)を指定します。これによって内部でDeltaテーブルに書き込みが行われます。

```py:Python
view_df.write.mode("overwrite").partitionBy("event_dt").format('delta').saveAsTable(tabName)
```

DatabricksランタイムではなくオープンソースのDeltaテーブルを使用している場合、[Z\-ordering](https://docs.databricks.com/delta/optimizations/file-mgmt.html)を用いたパフォーマンスの最適化を使用することはできません。

:::note
**訳者注**
Delta Lakeは完全にオープンソース化されたので、オープンソース版でもZ-orderingなどの最適化機能を使用することができます。
:::

```py:Python
useDeltaOpt = (os.getenv('DATABRICKS_RUNTIME_VERSION') != None)

if useDeltaOpt:
     try:
        spark.sql("optimize {} zorder by {}".format(tabName, "(" + ",".join(partitionCols + optimizationCols) + ")"))
     except:
        print("Delta optimizations attempted on a non-Databricks platform. Switch to use Databricks Runtime to get optimization advantages.")
```

(`io.py`を変更するか、他の書き込み定義を`tsdf.py`に追加することで、標準的なparquetファイルにどの様に書き込めるのかを確認することは難しいことではありません。)

# Asof

タイムスタンプカラムが一致する2つのTSDF間でasof joinを行う`asofJoin`モジュールが`tsdf.py`に存在しています。右側のtsdfとして現在のデータフレームを指定することは必須ですが、カラム名の重複を避けるために左右のTSDFにプレフィックスを指定(右側はデフォルトでプレフィックス「right」が付きます)することができます。パーティションを時間の枠に分割するオプションを指定することができ、偏りを制限し、最大のルックバックの外に値がある場合にNULL値を避けることができます。オーバーラップの割合のデフォルトは0.5です。asof joinで作成された(オーバーラップするデータと関係のないカラムが除外された)データフレームを用いてTSDFが作成され、共通するタイムスタンプのカラムと結合されたパーティションカラムが返却されます。

# 移動平均

タイムスタンプカラムに基づいてローリングの統計情報を計算するためにシンプルな移動平均が使用されます。すべての数値カラムあるいは指定されたカラムの`mean/count/min/max/sum/std deviation/zscore`を計算するために`withRangeStats`を呼び出します。デフォルトのレンジバックウィンドウは、ベースのイベントタイムスタンプから1000秒となっています。以下の仮定がなされます。

1. 特徴量はレンジバックのローリングウィンドウに対して要約されます。
1. レンジバックウィンドウはユーザーによって指定できます。
1. ソートのためのシーケンス番号はまだサポートされていません。
1. マイクロ秒以上が切り落とされるタイムスタンプからlongへのキャストが行われます。これは、文字列のタイムスタンプやタイムスタンプ自身のソートによって容易に取り扱うことができます。`rows preceding`ウィンドウを使用している場合には問題になりません。

ここでの命名規則はあまり一貫性がありませんので、EMAを呼び出し、計算するTSDFとカラム名を渡すことで指数関数的移動平均を計算します。計算処理がウィンドウ(デフォルトは30です)に基づいて行われます。

# 再サンプリング

時系列データの周期の変換や再サンプリングのための便利なメソッドです。これは、[pandas\.DataFrame\.Resample](https://pandas.pydata.org/pandas-docs/dev/reference/api/pandas.DataFrame.resample.html)と同じ様な機能を提供しますが、([Koalas](https://github.com/databricks/koalas)のゴールとは違って)これを置き換えるものではありません。ソートのためのタイムスタンプのカラムと、ウィンドウ処理やソートのためにより粒度の細かい時系列(時間、分、秒)にパーティショニングするために使用するカラムを指定し、集計関数を引き渡します。集計処理は`resample.py`によって行われます。

# その他の機能

`tsdf.py`のソースを見ると、`withLookbackFeatures`という関数があることに気づきます。

> いくつかの特徴量の履歴から現在の値を予測するためにMLモデルをトレーニングするのに適した2Dの特徴量テンソルを作成します。この関数は、それぞれの観測結果に対して、以前の観測結果から過去の観測結果の際台数に至るトレーリング「ルックバック」ウィンドウに対する他のカラムのいくつかの値の2D配列を含む新規のカラムを作成します。

これは、新しく有用な何かを作るために、すでにコードベースにあるプライベートな`BaseWindow`と`RowsBetweenWindows`機能を使用する小規模かつわかりやすい関数です。これは、ライブラリ自身で何ができるかに加え、ソースコードを操作することで何ができるのかを示す良い例となっています。

# まとめ

より良いものを提供するために根本的な変化をもたらそうとしている[Delta](https://github.com/delta-io/delta)や[Koalas](https://github.com/databricks/koalas)と違い、[Databricks Lab](https://github.com/databrickslabs)のこのライブラリは、特殊ですが一般的なユースケースをより管理しやすくするためのものです。[Databricks Lab](https://github.com/databrickslabs)のすべてのプロジェクトは、Databricksレイクハウスプラットフォームで使用することを意図していますが、ソースコード自身は有用なものであり、時にはレイクハウスプラットフォームの外においても、作業を加速する役に立ちます。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

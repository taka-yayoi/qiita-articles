---
title: Databricksレイクハウスモニタリングのご紹介
tags:
  - Databricks
private: false
updated_at: '2024-03-11T15:03:01+09:00'
id: 5aaddc9aa7b06dc87f12
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Introduction to Databricks Lakehouse Monitoring \| Databricks on AWS](https://docs.databricks.com/en/lakehouse-monitoring/index.html) [2023/12/6時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**プレビュー**
本機能は以下のリージョンでパブリックプレビューです: eu-central-1, eu-west-1, us-east-1, us-east-2, us-west-2, ap-southeast-2。一覧されているリージョンですべてのワークスペースがサポートされている訳ではありません。レイクハウスモニタリングを使用する際に「Your workspace is hosted on infrastructure that cannot support serverless compute.」というエラーが出る場合には、別のワークスペースを試すか、アカウントチームに問い合わせください。
:::

本書ではDatabricksレイクハウスモニタリングを説明します。お使いのデータに対するモニタリングのメリットをカバーし、コンポーネントの概要とDatabricksレイクハウスモニタリングの使い方を説明します。

Databricksレイクハウスモニタリングによって、お使いのアカウントのすべてのテーブルのデータの統計的な属性や品質を監視することができます。また、モデルの入力と予測結果を格納する推論テーブルを監視することで、機械学習モデルとモデルサービングエンドポイントのパフォーマンスを追跡するためにこの機能を活用することができます。以下の図では、DatabricksにおけるデータとMLパイプラインを経由するデータフローと、データ品質とモデルパフォーマンスを継続的に追跡するためにどのようにモニタリングを活用するのかを示しています。
![](https://docs.databricks.com/en/_images/lakehouse-monitoring-overview.png)

# なぜDatabricksレイクハウスモニタリングを使うのか？

あなたのデータから有用な洞察を導き出すためには、お使いのデータに対して信頼できるようになっている必要があります。お使いのデータをモニタリングすることで、時間が経過したとしてもデータの品質と一貫性を追跡、確認する助けとなる定量的な指標を得ることができます。お使いのテーブルのデータ分布や対応するモデルのパフォーマンスの変化を検知した際、Databricksレイクハウスモニタリングは変化を捕捉、警告することができるので、原意の特定の助けとなります。

Databricksレイクハウスモニタリングは、以下のような質問に回答する助けとなります:

- データの統一性はどのようなものか、そしてそれはどのように時間とともに変化しているのか？例えば、現在のデータにおけるnull値やゼルの値の割合は、それは増加しているのか？
- 統計的な分布はどのようになっているか、そしてそれは時間とともにどのように屁kんかしているのか？例えば、数値カラムの90thパーセンタイルは何か？あるいは、カテゴリー値カラムの値の分布はどうなっているか、それは昨日とどのように異なっているか？
- 現在のデータと既知のベースライン、あるいは次の時間ウィンドウのデータの間にドリフトが生じているか？
- データのサブセットやスライスの統計的な分布やドリフトはどのようなものか？
- MLモデルの入力と予測の時間的なシフトはどのようになっているか？
- モデルパフォーマンスの時間的なトレンドはどのようになっているか？モデルバージョンAはバージョンBよりもパフォーマンスが優れているか？

さらに、Databricksレイクハウスモニタリングを用いることで、観測結果の時間粒度をコントロールしたり、カスタムメトリクスを設定することができます。

# 要件

Databricksレイクハウスモニタリングを使うには以下の要件があります:

- お使いのワークスペースでUnity Catalogが有効化されており、Databricks SQLにアクセスできる必要があります。
- Deltaマネージドテーブル、外部テーブル、ビュー、マテリアライズドビューのモニタリングのみがサポートされています。

:::note info
**注意**
Databricksレイクハウスモニタリングはサーバレスジョブコンピュートを使用します。レイクハウスモニタリングの費用の追跡に関しては、[Lakehouse Monitoringの使用量を確認する](https://docs.databricks.com/ja/lakehouse-monitoring/expense.html)をご覧ください。
:::

# Databricks上でのレイクハウスモニタリングの動作原理

Databricksのテーブルを監視するには、テーブルにアタッチされるモニターを作成します。機械学習モデルのパフォーマンスを監視するには、モデルの入力と対応する予測結果を保持する推論テーブルにモニターをアタッチします。

Databricks上でのレイクハウスモニタリングは、以下のタイプの分析を提供します: 時系列、スナップショット、推論です。

| プロファイルタイプ | 説明 |
|:--|:--|
| 時系列  | 時間ウィンドウごとのデータ分布を比較します。時間とともにお使いのデータ分布がどのように変化するのかを比較するためにメトリクスをどの粒度(1日など)で計算するのかを指定します。このタイプのプロファイルではタイムスタンプの列が必要となります。  |
| スナップショット  | 時系列とは異なり、スナップショットプロファイルは、テーブルのすべてのコンテンツが時間とともにどのように変化しているかを監視します。テーブルのすべてのデータに対してメトリクスが計算され、モニターがリフレッシュされる都度、テーブルの状態を監視します。  |
| 推論  | 機械学習分類、回帰モデルによる予測値の出力を含むテーブルが対象となります。このテーブルには、タイムスタンプ、モデルID、モデルへの入力(特徴量)、モデルの予測結果を含むカラム、ユニークな観測IDや正解ラベルを含むオプションのカラムが含まれます。モデルへの入力には使用されませんが公正性、バイアスの調査やその他のモニタリングで有用な場合があるデモグラフィック情報のようなメタデータを含めることができます。推論プロファイルは時系列プロファイルと似ていますが、モデル品質メトリクスも含まれます。  |

このセクションでは、Databricksレイクハウスモニタリングで使用される入力テーブルと生成されるメトリックテーブルを簡単に説明します。以下の図では、入力テーブル、メトリックテーブル、モニター、ダッシュボード間の関係を示しています。
![](https://docs.databricks.com/en/_images/lakehouse-monitoring.png)

## プライマリテーブルとベースラインテーブル

「プライマリテーブル」と呼ばれる監視対象のテーブルに加え、オプションでドリフト計測や値の時間変化のリファレンスとして使用できるベースラインテーブルを指定することができます。ベースラインテーブルは、お使いのデータがどのようなものかを期待できるサンプルがある場合には有用です。期待されるデータ値や分布と比較することでドリフトが計算されることになります。

ベースラインテーブルには、統計的な分布、個々のカラムの分布、欠損値、その他の特性において入力データに期待される品質を反映するデータセットを含める必要があります。監視されるテーブルのスキーマと一致しなくてはなりません。例外は、時系列や推論プロファイルで使用されるテーブルのタイムスタンプの絡むです。プライマリテーブルやベースラインに含まれていないカラムが存在する場合、モニタリングでは出力メトリクスを計算するためにベストエフォートのヒューリスティックを用います。

スナップショットプロファイルを使うモニターでは、ベースラインテーブルには許容できる品質基準を表現する分布を持つデータのスナップショットが含まれている必要があります。例えば、評点分布のデータにおいては、評点が均等に分布つしている以前のクラスをベースラインに設定するかもしれません。

時系列プロファイルを使用するモニターでは、ベースラインテーブルには品質基準を表現する分布となっている時間ウィンドウを表現するデータが含まれている必要があります。例えば、気候データにおいては、気温が期待する通常の気温に近い週、月、年にベースラインを設定するかもしれません。

推論プロファイルを使用するモニターでは、ベースラインに好適な選択肢は、監視されるモデルのトレーニング、検証に用いたデータとなります。このようにすることで、モデルのトレーニング、検証に用いたデータと比較してデータがドリフトを起こしている際に、ユーザーがアラートを受け取ることができます。このテーブルには、プライマリテーブルと同じ特徴量のカラムが含まれる必要があり、データ一貫性を持って集計されるようにプライマリテーブルのInferenceLogに指定されたのと同じ`model_id_col`を追加で含める必要があります。理想的には、モデル品質メトリクスを比較できるようにするために、モデルの評価に使用されたテストセット、検証セットを用いるべきです。

## メトリックテーブルとダッシュボード

テーブルのモニターは2つのメトリックテーブルとダッシュボードを作成します。メトリックの値はテーブル全体に対して計算され、対象はモニターを作成時に指定する時間ウィンドウやデータのサブセット(あるいはスライス)が対象となります。さらに、推論の分析では、それぞれのモデルIDごとにメトリクスが計算されます。メトリックテーブルの詳細については、[メトリクステーブルを監視する](https://docs.databricks.com/ja/lakehouse-monitoring/monitor-output.html)をご覧ください。

- プロファイルメトリクステーブルにはサマリーの統計情報が格納されます。[プロファイルメトリクステーブルのスキーマ](https://docs.databricks.com/ja/lakehouse-monitoring/monitor-output.html#profile-metrics-table-schema)をご覧ください。
- ドリフトメトリクステーブルには、時間経過によるドリフトに関する統計情報が格納されます。ベースラインテーブルが指定されると、ベースラインの値に対してもドリフトが監視されます。[ドリフトメトリクステーブルのスキーマ](https://docs.databricks.com/ja/lakehouse-monitoring/monitor-output.html#drift-metrics-table-schema)をご覧ください。

メトリックテーブルはDeltaテーブルであり、指定したUnity Catalogのスキーマに格納されます。DatabricksのUIを用いてこれらのテーブルを参照し、Databricks SQLを用いてクエリーを行い、これらをベースとしたダッシュボードやアラートを作成することができます。

それぞれのモニターに対して、監視結果を可視化し、表示する助けになるダッシュボードをDatabricksは自動で作成します。このダッシュボードは他の[Databricks SQLのダッシュボード](https://docs.databricks.com/ja/sql/user/dashboards/index.html)と同じように完全にカスタマイズすることができます。

# Databricksでレイクハウスモニタリングを使い始める

使い始めるには以下のドキュメントをご覧ください:

- [Databricks UIを使用したモニターの作成](https://docs.databricks.com/ja/lakehouse-monitoring/create-monitor-ui.html)
- [APIを使用したモニターの作成](https://docs.databricks.com/ja/lakehouse-monitoring/create-monitor-api.html)
- [メトリクステーブルのモニタリング](https://docs.databricks.com/ja/lakehouse-monitoring/monitor-output.html)
- [生成されたSQLダッシュボードを使用する](https://docs.databricks.com/ja/lakehouse-monitoring/monitor-dashboard.html)
- [アラートの監視](https://docs.databricks.com/ja/lakehouse-monitoring/monitor-alerts.html)
- [Databricksレイクハウスモニタリングでカスタムメトリクスを使用する](https://docs.databricks.com/ja/lakehouse-monitoring/custom-metrics.html)
- [モデルのモニタリングとデバッグのための推論テーブル](https://docs.databricks.com/ja/machine-learning/model-serving/inference-tables.html)
- [分類モデルの公平性とバイアスを監視する](https://docs.databricks.com/ja/lakehouse-monitoring/fairness-bias.html)
- [Lakehouse Monitoring API Reference — Lakehouse Monitoring documentation](https://api-docs.databricks.com/python/lakehouse-monitoring/latest/index.html)のマテリアル
- [サンプルノートブック](https://docs.databricks.com/ja/lakehouse-monitoring/create-monitor-api.html#example-notebooks)

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: 'Databricks生成AIクックブック - 4.3. 計測の実現: サポートするインフラストラクチャ'
tags:
  - Databricks
  - rag
  - 生成AI
  - Databricks生成AIクックブック
private: false
updated_at: '2024-06-26T13:56:42+09:00'
id: e8c2b711a2ebe5bd1d1d
organization_url_name: databricks
slide: false
ignorePublish: false
---
[4\.3\. Enabling Measurement: Supporting Infrastructure — Databricks Generative AI Cookbook](https://ai-cookbook.io/nbs/4-evaluation-infra.html) [2024/6/24時点]の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

> [Databricks生成AIクックブック](https://qiita.com/taka_yayoi/items/36c51bce8f33a70cf204)のコンテンツです。

# 4.3. 計測の実現: サポートするインフラストラクチャ

品質の計測は簡単なものではなく、インフラストラクチャに対する大きな投資を必要とします。このセクションでは、成功するために何が必要なのか。どのようにDatabricksではそれらのコンポーネントを提供しているのかの詳細を説明します。

**詳細なトレースのロギング。** あなたのRAGアプリケーションのロジックのコアにあるのは、チェーンに含まれる一連のステップです。品質を評価、デバッグするためには、チェーンの入力と出力、チェーンのそれぞれのステップと関連する入力と出力を追跡する仕組みを実装する必要があります。配備する仕組みは開発とプロダクションで同じように動作すべきです。

:::note info
Databricksでは、[MLflow Tracing](https://docs.databricks.com/ja/mlflow/mlflow-tracing.html)がこの機能を提供します。MLflow Traceのロギングによって、プロダクションにあるあなたのコードを計測し、開発とプロダクション環境で同じトレースを取得することができます。プロダクションのトレースは、[推論テーブル](https://docs.databricks.com/ja/machine-learning/model-serving/inference-tables.html)の一部として記録されます。
:::

**ステークホルダーのレビューUI。** 多くの場合、あなたは開発者として、あなたが開発しようとしているアプリケーションのコンテンツに対するドメインの専門家ではありません。あなたのアプリケーションのアウトプットの品質を評価できる人間の専門家からフィードバックを収集するために、アプリケーションの初期バージョンを操作し、詳細なフィードバックを提供できるインタフェースが必要となります。さらに、ステークホルダーが品質を評価できるようにするために、固有のアプリケーションのアウトプットをロードする手段を必要とします。

このインタフェースでは、アプリケーションのアウトプットと関連するフィードバックを構造化された形で追跡し、完全なアプリケーションのトレースと詳細なフィードバックをデータテーブルとして格納する必要があります。

:::note info
Databricksでは、[Agent Evaluation Review App](https://docs.databricks.com/ja/generative-ai/agent-evaluation/human-evaluation.html)がこの機能を提供します。
:::

**品質 / コスト / レーテンシーのメトリックのフレームワーク。** あなたのチェーンとエンドツーエンドのアプリケーションのそれぞれのコンポーネントの品質を包括的に計測するメトリクスを定義する方法を必要とします。理想的には、このフレームワークは、カスタマイズ性をサポートすることに加え、すぐに利用できる標準的なメトリクスのスイートを提供するので、あなたのビジネス固有の特定の観点をテストするメトリクスを追加することができます。

:::note info
Databricksでは、[Mosaic AI Agent Evaluation](https://docs.databricks.com/ja/generative-ai/agent-evaluation/index.html)が、必要な品質/コスト/レーテンシーのメトリクスのために、ホストされたLLM審判モデルを用いてすぐに利用できる実装を提供します。
:::

**評価のハーネス。** あなたの評価セットのすべての質問に対して、あなたのチェーンのアウトプットをクイックかつ効率的に取得し、適切なメトリクスに対するそれぞれのアウトプットを評価する手段を必要とします。このハーネスは、品質を改善しようとするすべての実験のあとに評価を実行することになるので、可能な限り効率的であるべきです。

:::note info
Databricksでは、[Mosaic AI Agent Evaluation](https://docs.databricks.com/ja/generative-ai/agent-evaluation/index.html)にMLflowにインテグレーションされた[評価ハーネス](https://docs.databricks.com/ja/generative-ai/agent-evaluation/evaluate-agent.html)を提供しています。
:::

**評価セットの管理。** あなたの評価セットは生きており、アプリケーション開発、プロダクションのライフサイクルを通じて繰り返し更新される一連の質問となります。

:::note info
Databricksでは、あなたの評価セットをDeltaテーブルとして管理することができます。MLflowで評価する際、Mlflowが使用した評価セットのバージョンのスナップショットを自動で記録します。
:::

**実験追跡フレームワーク。** あなたのアプリケーション開発の過程では、数多くの様々な実験をトライすることになります。実験追跡フレームワークによって、それぞれの実験を記録し、他の実験に対するメトリクスを追跡することができます。

:::note info
Databricksでは、[MLflow](https://docs.databricks.com/ja/mlflow/index.html)は実験追跡機能を提供します。
:::

**チェーンのパラメーター化フレームワーク。** トライする多数の実験では、チェーンのコードの定数を保持しつつも、コードで使用される様々なパラメーターで試行錯誤する必要があります。これを実現するためのフレームワークを必要とします。

:::note info
Databricksでは、[MLflow model configuration](https://docs.databricks.com/ja/generative-ai/create-log-agent.html#use-parameters-to-control-agent-execution)がこの機能を提供します。
:::

**オンラインモニタリング。** デプロイしたら、アプリケーションの健康状態と現行の品質/コスト/レーテンシーを監視する方法を必要とします。

:::note info
Databricksでは、モデルサービングが[アプリケーションの健康状態のモニタリング](https://docs.databricks.com/ja/machine-learning/model-serving/monitor-diagnose-endpoints.html)を提供し、[レイクハウスモニタリング](https://docs.databricks.com/ja/lakehouse-monitoring/index.html)が最新状況のダッシュボードと品質/コスト/レーテンシーを監視します。
:::

- [目次](https://qiita.com/taka_yayoi/items/36c51bce8f33a70cf204#%E7%9B%AE%E6%AC%A1)
- 前のセクション: [4\.2\. パフォーマンスの評価: メトリクスが重要です](https://qiita.com/taka_yayoi/items/05f650df667ffca3e92d)
- 次のセクション: [5\. 評価ドリブンの開発ワークフロー](https://qiita.com/taka_yayoi/items/1887ddfae49a6a32cc0e)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: 'MLflow 2.4の発表: 強力なモデル評価のためのLLMOpsツール'
tags:
  - Databricks
  - MLflow
  - LLM
  - LLMOps
private: false
updated_at: '2023-06-10T11:51:03+09:00'
id: cd944fde2a9cae8cd6c6
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Announcing MLflow 2\.4: LLMOps Tools for Robust Model Evaluation \- The Databricks Blog](https://www.databricks.com/blog/announcing-mlflow-24-llmops-tools-robust-model-evaluation)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

LLMは、パワフルなアプロケーションをクイックに構築し、ビジネス価値を提供するために、すべての規模の企業にとって膨大な機会を提供します。これまで、データサイエンティストは非常に限定的なタスクを行うために、モデルのトレーニングや再トレーニングに膨大な時間を費やしていましたが、今ではより少ない時間でより多彩で知的なアプリケーションを提供するために、様々なSaaS基盤やオープンソースモデルを活用することができます。プロンプトエンジニアリングのような、ゼロショット、数ショットの学習技術を用いることで、データサイエンティストはクイックにさまざまなデータセットに対する高精度の分類器、最先端の感情分析モデル、低レーテンシーの文書要約器などを構築できます。

しかし、プロダクションにベストなモデルを特定し、安全にそれらをデプロイするためには、企業は適切なツールとプロセスを必要とします。最も重要なコンポーネントの一つが強力な*モデル評価*です。幻覚、レスポンスの毒性、プロンプトインジェクションに対する脆弱性のようなモデル品質の課題、多くのタスクにおける正解データの欠如によって、データサイエンティストはプロダクションにベストなモデルを選択するために、複数のモデル候補の些細な違いを特定できるようになる必要があります。これまで以上に、すべてのモデルの詳細なパフォーマンスレポートを提供し、プロダクションのはるか以前に弱点や脆弱性を特定する助けとなり、モデルの比較を円滑にするLLMOpsプラットフォームが必要となっています。

これらのニーズに応えるために、モデル評価のための包括的なLLMOpsツールセットを提供するMLflow 2.4を発表できることを嬉しく思っています。言語タスクに対する新たな[mlflow\.evaluate\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate)のインテグレーション、複数のモデルバージョンのテキストアウトプットを比較するための新しいアーティファクトビューのUI、そして、長い間要望されていたデータセットのトラッキング機能によって、MLflow 2.4はLLM開発を加速します。

# 言語モデルに`mlflow.evaluate()`を用いることでパフォーマンス洞察を捕捉

言語モデルのパフォーマンスを評価するためには、さまざまな入力データセットを入力し、対応するアウトプットを記録し、ドメイン固有のメトリクスを計算する必要があります。MLflow 2.4では、このプロセスを劇的にシンプルにするために、MLflowのパワフルな評価APIである[mlflow\.evaluate\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate)を拡張しました。1行のコードで、テキスト要約、テキスト分類、質疑応答、テキスト生成を含むLLMの様々なタスクにおける、モデルの予測とパフォーマンスメトリクスを追跡することができます。この情報の全ては、MLflowトラッキングに記録され、プロダクションにベストな後方を選択するために、複数のモデルのパフォーマンス評価結果を調査、比較することができます。

以下のサンプルコードでは、要約モデルのパフォーマンス情報をクイックに捕捉するために[mlflow\.evaluate\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate)を使用しています。

```py
import mlflow

# Evaluate a news summarization model on a test dataset
summary_test_data = mlflow.data.load_delta(table_name="ml.cnn_dailymail.test")

evaluation_results = mlflow.evaluate(
    "runs:/d13953d1da1a41a59bf6a32fde599c63/summarization_model",
    data=summary_test_data,
    model_type="summarization",
    targets="highlights"
)

# Verify that ROUGE metrics are automatically computed for summarization
assert "rouge1" in evaluation_results.metrics
assert "rouge2" in evaluation_results.metrics

# Verify that inputs and outputs are captured as a table for further analysis
assert "eval_results_table" in evaluation_results.artifacts
```

サンプルを含む[mlflow\.evaluate\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate)の詳細については、[MLflow Documentation](https://mlflow.org/docs/latest/models.html#model-evaluation)と[examples repository](https://github.com/mlflow/mlflow/tree/master/examples/evaluation)をチェックしてください。

# 新たなアーティファクトビューでLLMのアウトプットを調査、比較

正解データが無いと、多くのLLM開発者は品質を評価するために手動でモデルの出力を調査しなくてはなりません。これは、多くの場合、文書の要約や複雑な質問に対する回答、生成された分のような、モデルによって生成されたテキストを読まなくてはならないことを意味します。プロダクションにベストなモデルを選択する際、これらのテキストアウトプットはモデルごとにグルーピングされ、比較する必要があります。例えば、LLMを用いた文書要約モデルを開発する際、それぞれのモデルが指定された文書をどのように要約するのかを確認し、違いを特定することが重要となります。
![](https://www.databricks.com/sites/default/files/inline-images/screenshot_2023-06-07_at_11.46.21_am.png)
*複数のモデルのインプット、アウトプット、中間結果を隣り合わせで比較できるMLflowのアーティファクトビュー*

MLflow 2.4では、MLflowトラッキングの新たなアーティファクトビューが、このアウトプットの調査と比較を容易にします。あなたのすべてのモデルに対する[mlflow\.evaluate\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate)のテキスト入力、出力、中間結果を数クリックで参照、比較することができます。これによって、推論時にどのプロンプトが用いられたのかを理解し、悪いアウトプットを特定することが非常に容易になります。MLflow 2.4の新たな[mlflow\.load\_table\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.load_table) APIによって、Databricks SQLやデータラベリングで使用するために、アーティファクトビューに表示されているすべての評価結果をダウンロードすることもできます。これは以下のコードサンプルでデモンストレーションされています。

```py
import mlflow

# Evaluate a language model
mlflow.evaluate(
    "models:/my_language_model/1", data=test_dataset, model_type="text"
)

# Download evaluation results for further analysis
mlflow.load_table("eval_results_table.json")
```

# 正確な比較を確実にするために評価データセットをトラッキング

プロダクションにベストなモデルを選択するには、様々な候補モデルのパフォーマンス比較が必要となります。この比較における重要な観点は、同じデータセットを用いてすべてのモデルが評価されるようにすることです。いずれにしても、同じデータセットですべてのモデルが評価された際に、ベストな精度をレポートしたモデルを選択することに合理性があると言えます。

MLflow 2.4では、長い間要望されていた機能であるデータセットトラッキングを紹介できることを嬉しく思っています。この素晴らしい新機能は、モデル開発におけるデータセットの管理や分析方法を標準化します。データセットトラッキングによって、それぞれのモデルの開発、評価に使用されたデータセットをクイックに特定することができ、プロダクション開発における公正なモデル比較を確実にし、モデル選択をシンプルにします。
![](https://www.databricks.com/sites/default/files/inline-images/image2_0.png)
*MLflowトラッキングは、ランごとのデータセットメタデータに対する可視性を強化したUIで、包括的なデータセット情報を表示するようになります。新たなパネルの導入によって、データセットの詳細を容易に可視化し、探索することができ、ランの比較ビューとランの詳細ページの両方から簡単にアクセスすることができます。*

MLflowでデータセットトラッキングを使い始めるのは非常に簡単です。あなたのMLflowランのいずれかでデータセット情報を記録するには、シンプルに[mlflow\.log\_input\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_input) APIを呼び出します。また、データセットトラッキングはMLflowのオートロギングとインテグレーションされているので、追加のコードなしにデータの洞察が提供されます。すべてのデータセット情報は、分析や比較のためにMLflowトラッキングのUIにわかりやすく表示されます。以下のサンプルでは、ランのトレーニングデータセットを記録するためにどのように[mlflow\.log\_input\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_input)を使い、ランのデータセットに関する情報を取得し、データセットのソースをロードするのかをデモンストレーションしています。

```py
import mlflow
# Load a dataset from Delta
dataset = mlflow.data.load_delta(table_name="ml.cnn_dailymail.train")

with mlflow.start_run():
    # Log the dataset to the MLflow Run
    mlflow.log_input(dataset, context="training")
    # <Your model training code goes here>

# Retrieve the run, including dataset information

run = mlflow.get_run(mlflow.last_active_run().info.run_id)
dataset_info = run.inputs.dataset_inputs[0].dataset

print(f"Dataset name: {dataset_info.name}")
print(f"Dataset digest: {dataset_info.digest}")
print(f"Dataset profile: {dataset_info.profile}")
print(f"Dataset schema: {dataset_info.schema}")

# Load the dataset's source Delta table
dataset_source = mlflow.data.get_source(dataset_info)
dataset_source.load()
```

利用ガイドやデータセットトラッキングの情報に関しては、[MLflow Documentation](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.data)をチェックしてください。

# MLflow 2.4のLLMOpsツールを使い始める

言語モデルに対する[mlflow\.evaluate\(\)](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate)、言語モデル比較のための新たなアーティファクトビュー、包括的なデータセットトラッキングによって、MLflow 2.4はユーザーがより強力で正確で信頼できるモデルを構築できるように支援し続けます。特に、これらのエンハンスによって、LLMアプリケーションの開発体験を劇的に改善します。

LLMOpsのための新たなMLflow 2.4の機能をぜひ体験していただければと思っています。すでにDatabricksユーザーであれば、ノートブックやクラスターに[ライブラリをインストール](https://qiita.com/taka_yayoi/items/0c7fc7d741aad34bf9d4)することで、すぐにMLflow 2.4を使い始めることができます。また、MLflow 2.4は[Databricks機械学習ランタイム](https://www.databricks.com/jp/product/machine-learning-runtime)バージョン 13.2にプリインストールされることになります。使い始めるには、Databricks MLflowガイド[[AWS]](https://docs.databricks.com/mlflow/index.html)[[Azure]](https://learn.microsoft.com/ja-jp/azure/databricks/mlflow/)[[GCP]](https://docs.gcp.databricks.com/mlflow/index.html)を参照ください。Databricksユーザーでないのであれば、MLflow 2.4の詳細を学ぶために https://www.databricks.com/jp/product/managed-mlflow を訪れ、フリートライアルをスタートしてください。MLflow 2.4における新機能や改善点の完全なリストに関しては、[release changelog](https://github.com/mlflow/mlflow/blob/master/CHANGELOG.md)をご覧ください。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

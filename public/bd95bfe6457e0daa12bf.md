---
title: DatabricksとApache SparkクラスターにおけるRayのサポートの発表
tags:
  - Ray
  - Databricks
private: false
updated_at: '2023-03-02T09:23:13+09:00'
id: bd95bfe6457e0daa12bf
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Announcing Ray support on Databricks and Apache Spark Clusters \- The Databricks Blog](https://www.databricks.com/blog/2023/02/28/announcing-ray-support-databricks-and-apache-spark-clusters.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

[Ray](https://www.ray.io/)はスケーラブルなAI、Pythonワークロードを実行するための有名な計算フレームワークであり、さまざまな分散機械学習ツール、大規模ハイパーパラメーターチューニング能力、強化学習アルゴリズム、モデルサービングなどを提供しています。同様にApache Spark™は、[Spark MLlib](https://spark.apache.org/docs/latest/ml-guide.html)を通じたさまざまな分散機械学習のための高パフォーマンスアルゴリズムと、[Spark MLlib](https://spark.apache.org/docs/latest/ml-guide.html)、[TensorFlow](https://docs.databricks.com/machine-learning/train-model/distributed-training/horovod-spark.html)、[PyTorch](https://docs.databricks.com/machine-learning/train-model/distributed-training/horovod-spark.html)を含む機械学習フレームワークとの密なインテグレーションを提供しています。ベストモデルを構築するために、機械学習の実践者は多くの場合、複数のアルゴリズムを探索する必要があり、RayとSparkを含む複数のプラットフォームを活用する必要が出てきます。本日、Rayバージョン2.3.0のリリースによって、RayのワークロードがDatabricksとSparkスタンドアローンクラスターでサポートされ、両方のプラットフォームでのモデル開発を劇的にシンプルにできることを発表できて嬉しく思っています。

# Databricks、SparkにおけるRayクラスターの作成

DatabricksあるいはSparkクラスターでRayをスタートするには、シンプルに最新バージョンのRayをインストールし、`ray.util.spark.setup_ray_cluster()`関数を呼び出し、Rayワーカーの数と計算リソース割り当てを指定します。[Databricks Runtime](https://docs.databricks.com/runtime/index.html)バージョン12.0以降のDatabricksクラスター、バージョン3.3以降のSparkクラスターであればサポートされています。例えば、以下のコードはDatabricksノートブックでRayをインストールし、2つのワーカーノードでRayクラスターを初期化します。

```py:Python
# Install Ray with the ‘default’, ‘rllib’, and 'tune' extensions for 
# Ray dashboard, reinforcement learning, and tuning support
%pip install ray[default,rllib,tune]>=2.3.0
```

```py:Python
from ray.util.spark import setup_ray_cluster

setup_ray_cluster(num_worker_nodes=2)
```

たった数行のコードでRayクラスターを作成し、モデルのトレーニングを開始することができます。

# Ray TrainとRay RLlibによるモデルのトレーニング

Rayクラスターを起動したら、モデルを構築するために分散機械学習のパワーを活用できるようになります。すべてのRayアプリケーションとRayとインテグレーションされた機械学習アルゴリズムは、変更なしにDatabricksクラスターやSparkクラスターでサポートされます。例えば、XGBoostのモデルトレーニングを容易に分散させるために、Databricksノートブックで[Ray Train API](https://docs.ray.io/en/latest/train/api.html)を活用することができ、トレーニングの時間を削減し、モデル精度を改善することができます。

```py:Python
# Install xgboost-ray for distributed XGBoost training on Ray
%pip install xgboost-ray
```

```py:Python
import pandas as pd
import ray.data
from ray.air.config import ScalingConfig
from ray.train.xgboost import XGBoostTrainer
from sklearn.datasets import fetch_california_housing

housing_dataset = fetch_california_housing(as_frame=True)
housing_df = pd.concat(
    [housing_dataset.data, housing_dataset.target], axis=1
)

trainer = XGBoostTrainer(
    scaling_config=ScalingConfig(num_workers=2),
    label_column="MedHouseVal",
    num_boost_round=20,
    params={
        "objective": "reg:squarederror",
        "eval_metric": ["logloss", "error"],
    },
    datasets={"train": ray.data.from_pandas(housing_df)}
)
training_result = trainer.fit()
```

また、Rayは強化学習をネイティブでサポートしています。例えば、[Taxi Gymnasium environment](https://gymnasium.farama.org/environments/toy_text/taxi/#taxi)でPPO強化学習アルゴリズムをトレーニングするために、Databricksノートブックで以下の[Ray RLlibコード](https://docs.ray.io/en/latest/rllib/index.html)を実行することができます。

```py:Python
from ray.rllib.algorithms.ppo import PPOConfig

config = (  # 1. Configure the algorithm,
    PPOConfig()
    .environment("Taxi-v3")
    .rollouts(num_rollout_workers=2)
    .framework("tf2")
    .training(model={"fcnet_hiddens": [64, 64]})
    .evaluation(evaluation_num_workers=1)
)

algo = config.build()  # 2. build the algorithm,

for _ in range(3):
    print(algo.train())  # 3. train it,

algo.evaluate()  # 4. and evaluate it.
```

この他のモデルトレーニングに関する情報やサンプルについては、[Ray Train documentation](https://docs.ray.io/en/latest/train/train.html#ray-train-scalable-model-training)や[Ray RLlib documentation](https://docs.ray.io/en/latest/rllib/index.html)をチェックしてみてください。

# Ray Tuneによる最適モデルの発見

モデルの品質を改善するために、大規模かつ並列で数千のモデルパラメーター設定を探索するために[Ray Tune](https://docs.ray.io/en/latest/tune/index.html)を活用することもできます。例えば、以下のコードではscikit-learnの分類モデルを最適化するためにRay Tuneを活用しています。

```py:Python
# Install the scikit-learn integration for Ray Tune
%pip install tune-sklearn
```

```py:Python
from sklearn.datasets import load_iris
from sklearn.linear_model import SGDClassifier
from ray.tune.sklearn import TuneGridSearchCV

X, y = load_iris(return_X_y=True)
parameter_grid = {"alpha": [1e-4, 1e-1, 1], "epsilon": [0.01, 0.1]}
tune_search = TuneGridSearchCV(
    SGDClassifier(), parameter_grid, max_iters=10
)
tune_search.fit(X, y)
best_model = tune_search.best_estimator
```

[Ray with MLflow](https://docs.ray.io/en/latest/tune/examples/tune-mlflow.html)の使用法を含む、Rayにおけるモデルチューニングの情報とサンプルについては、[Ray Tune documentation](https://docs.ray.io/en/latest/tune/index.html)を参照ください。

# Rayダッシュボードの参照

![](https://cms.databricks.com/sites/default/files/inline-images/db-497-blog-img-1.png)
*DatabricksクラスターでRayを起動すると、Rayダッシュボードへのリンクが表示されます。*

モデル開発を通じて、[Ray dashboard](https://docs.ray.io/en/latest/ray-core/ray-dashboard.html)を用いることで、Rayの機械学習タスクの進捗とRayノードの健康状態をモニタリングすることができます。Rayクラスターを作成すると、`ray.util.spark.setup_ray_cluster()`はRayダッシュボードへのリンクを表示します。

![](https://cms.databricks.com/sites/default/files/inline-images/db-497-blog-img-2.png)
*Rayダッシュボードはクラスターのノード、アクター、ログなどの詳細情報を提供します。*

Rayダッシュボードは、Rayクラスターのノード、アクター、メトリクス、イベントログの包括的なビューを提供します。個々のノードのリソース利用メトリクスやすべてのノードの集計メトリクスを容易に参照することができます。Rayダッシュボードの詳細については、[Ray dashboard documentation](https://docs.ray.io/en/latest/ray-core/ray-dashboard.html)を参照ください。

# Databricks、SparkでRayを使い始める

Ray 2.3.0によって、DatabricksクラスターやSparkクラスターでRayアプリケーションを実行できるようになりました。Databricksを利用されているのであれば、シンプルにバージョン12.0以降の[Databricks Runtime](https://docs.databricks.com/runtime/index.html)のDatabricksクラスターを作成し、スタートするために[DatabricksにおけるRayの活用](https://qiita.com/taka_yayoi/items/f919ad6aee56539f5309)をご覧ください。最後に、スタンドアローンSparkクラスターでRayを起動する手順に関しては、[Ray on Spark documentation](https://docs.ray.io/en/latest/cluster/vms/user-guides/community/spark.html#deploying-on-spark-standalone-cluster)をチェックしてください。また、Rayにおける機械学習の詳細については[https://docs\.ray\.io/en/latest/](https://docs.ray.io/en/latest/)をご覧ください。

我々は分散機械学習の相互運用可能性を前進させることができて非常に興奮していますし、されにApache Spark™とDatabricksにおけるRayアプリケーションを強化することを楽しみにしています！

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

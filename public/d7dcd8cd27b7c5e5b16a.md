---
title: 'TensorFlow Similarity: 人間のためのメトリック学習'
tags:
  - Python
  - TensorFlow
  - TensorflowSimilarity
private: false
updated_at: '2022-04-01T09:38:18+09:00'
id: d7dcd8cd27b7c5e5b16a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[tensorflow/similarity: TensorFlow Similarity is a python package focused on making similarity learning quick and easy\.](https://github.com/tensorflow/similarity) [2022/4/1時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

TensorFlow Similarityは、自己教師あり学習、メトリック学習、対照学習のような技術を含む[類似性学習(similarity learning)](https://en.wikipedia.org/wiki/Similarity_learning)のための[TensorFlow](https://tensorflow.org/)ライブラリです。

# イントロダクション

TensorFlow Similarityは、類似性、対比に基づくモデルを研究、トレーニング、評価、提供するために必要な全てのコンポーネントとメトリック学習のための最先端のアルゴリズムを提供します。これらのコンポーネントには、これを容易かつクイックに行えるようにするための、モデル、損失、メトリクス、サンプラー、ビジュアライザ、そして、インデクシングサブシステムが含まれています。
![](https://raw.githubusercontent.com/tensorflow/similarity/master/assets/images/similar-cats-and-dogs.jpg)

TensorFlow Similarityを用いることで、2つのメインタイプのモデルをトレーニングすることができます。

1. **自己教師ありモデル(self-supervised models)**: わずかのラベルしか無い状況で、後段のタスクの精度をブーストするために、ラベルのないデータに対する一般的なデータ表現を学習するのに使用されます。例えば、TensorFlow Similarityでサポートされる対照方法の一つを用いてラベルのない大量の画像に大してモデルを事前トレーニングすることができ、より高い制度を達成するために小規模なラベル付きデータを用いてファインチューニングすることができます。こちらの[ノートブック](https://github.com/tensorflow/similarity/blob/master/examples/unsupervised_hello_world.ipynb)をご覧ください。
1. **類似性モデル(similarity models)**: 大コボなサンプルコーパス内の同じオブジェクトを表現する画像のような類似するサンプルを検索し、クラスタリングすることを可能とするエンべディングを出力します。例えば上に示したように、わずからデータセットクラスに対するトレーニングだけで、[Oxford IIIT Pet Dataset](https://www.tensorflow.org/datasets/catalog/oxford_iiit_pet)の未知の猫、犬の中から類似するものを検索、クラスタリングするための類似性モデルをトレーニングすることができます。ご自身で類似性モデルをトレーニングしたいのであれば、こちらの[ノートブック](https://github.com/tensorflow/similarity/blob/master/examples/supervised/visualization.ipynb)をご覧ください。

# What's new

省略。[原文](https://github.com/tensorflow/similarity#whats-new)をご覧ください。

# 使ってみる

## インストール

ライブラリのインストールにはpipを使用します。

**注意**: tensorflow>=2.4をインストールしている場合には、Tensorflowのextra_requireキーを省略することができます。

```
pip install --upgrade-strategy=only-if-needed tensorflow_similarity[tensorflow] 
```

## ドキュメント

TensorFlow Similarityを始めるには、詳細かつナラティブな[ノートブック](https://github.com/tensorflow/similarity/blob/master/examples)を使用することをお勧めします。お使いのデータやご自身の問題に類似するものがあるかと思います(ない場合にはお伝えください)。Google Colabアイコンをクリックすることで、すぐにサンプルをGoogle Colabで試すことができます。

特定の関数の詳細については、[APIドキュンメント](https://github.com/tensorflow/similarity/blob/master/api)をチェックすることができます。

プロジェクトに貢献したいのであれば、[contribution guidelines](https://github.com/tensorflow/similarity/blob/master/CONTRIBUTING.md)をご覧ください。

## 最小限のサンプル：MNIST similarity

こちらはTF.Similarityを用いたmnistに対する教師あり類似性モデルのトレーニング方法のサンプルとなります。このサンプルでは、TensorFlow Similarityによって提供されるメインコンポーネントのいくつかを説明し、それらをどう組み合わせるのかを説明します。詳細なイントロダクションに関しては[hello\_worldノートブック](https://github.com/tensorflow/similarity/blob/master/examples/supervised_hello_world.ipynb)を参照ください。

### データの準備

TensorFlow Similarityは、様々なデータセットタイプに対してよりスムースなトレーニングを保証するためのバッチのバランスする[データサンプラー](https://github.com/tensorflow/similarity/blob/master/api/TFSimilarity/samplers)を提供します。この例では、TensorFlowのデータセットカタログと直接インテグレートされているマルチショットサンプラーを使用します。

```py:Python
from tensorflow_similarity.samplers import TFDatasetMultiShotMemorySampler

# Data sampler that generates balanced batches from MNIST dataset
sampler = TFDatasetMultiShotMemorySampler(dataset_name='mnist', classes_per_batch=10)
```

### 類似性モデルの構築

TensorFlow Similarityモデルの構築は、標準的なKerasモデルの構築と似ており、出力レイヤーが通常L2正規化を強制する[`MetricEmbedding()`](https://github.com/tensorflow/similarity/blob/master/api/TFSimilarity/layers)レイヤーであること、追加の機能をサポートする特殊な[`SimilarityModel()`](https://github.com/tensorflow/similarity/blob/master/api/TFSimilarity/models/SimilarityModel.md)サブクラスである点が異なります。

```py:Pytohn
from tensorflow.keras import layers
from tensorflow_similarity.layers import MetricEmbedding
from tensorflow_similarity.models import SimilarityModel

# Build a Similarity model using standard Keras layers
inputs = layers.Input(shape=(28, 28, 1))
x = layers.experimental.preprocessing.Rescaling(1/255)(inputs)
x = layers.Conv2D(64, 3, activation='relu')(x)
x = layers.Flatten()(x)
x = layers.Dense(64, activation='relu')(x)
outputs = MetricEmbedding(64)(x)

# Build a specialized Similarity model
model = SimilarityModel(inputs, outputs)
```

### 対照学習によるモデルのトレーニング

メトリックのエンべディングを出力するために、近似近傍検索を通じた探索が可能であり、モデルは類似度の損失を用いてトレーニングされる必要があります。ここでは、最も効率的な損失関数である`MultiSimilarityLoss()`を使用しています。

```py:Python
from tensorflow_similarity.losses import MultiSimilarityLoss

# Train Similarity model using contrastive loss
model.compile('adam', loss=MultiSimilarityLoss())
model.fit(sampler, epochs=5)
```

### 画像インデックスの構築、クエリー

モデルをトレーニングしたら、検索できるようにモデルインデックスAPIを通じて、リファレンスサンプルはインデックス化される必要があります。インデクシングのあとは、K個の最も類似したアイテムに対するインデックスを検索するために、モデルルックアップAPIを使用することができます。

```py:Python
from tensorflow_similarity.visualization import viz_neigbors_imgs

# Index 100 embedded MNIST examples to make them searchable
sx, sy = sampler.get_slice(0,100)
model.index(x=sx, y=sy, data=sx)

# Find the top 5 most similar indexed MNIST examples for a given example
qx, qy = sampler.get_slice(3713, 1)
nns = model.single_lookup(qx[0])

# Visualize the query example and its top 5 neighbors
viz_neigbors_imgs(qx[0], qy[0], nns)
```

# サポートするアルゴリズム

## 自己教師ありモデル

- SimCLR
- SimSiam
- Barlow Twins

## 教師ありロス

- Triplet Loss
- PN Loss
- Multi Sim Loss
- Circle Loss
- Soft Nearest Neighbor Loss

## メトリクス

Tensorflow Similarityは[分類](https://github.com/tensorflow/similarity/blob/master/api/TFSimilarity/classification_metrics)や[収集](https://github.com/tensorflow/similarity/blob/master/api/TFSimilarity/retrieval_metrics)評価に使用される一般的なメトリクスの多くを提供します。

| 名前 | タイプ | 説明 |
|:--|:--|:--|
| Precision  | Classification  |   |
| Recall  |  Classification |  |
| F1 Score  | Classification  |   |
| Recall@K  | Retrieval  |   |
| Binary NDCG  |  Retrieval |   |

# 引用

皆様の研究の一部でTensorFlow similarityを使用する際には以下を引用してください。

```
@article{EBSIM21,
  title={TensorFlow Similarity: A Usable, High-Performance Metric Learning Library},
  author={Elie Bursztein, James Long, Shun Lin, Owen Vallis, Francois Chollet},
  journal={Fixme},
  year={2021}
}
```

# 免責

これはオフィシャルなGoogle製品ではありません。

---
title: Pandas UDF、applyInPandas、mapInPandasの理解
tags:
  - Spark
  - pandas
  - Databricks
private: false
updated_at: '2024-11-12T22:21:13+09:00'
id: bfe8fda543ebf0b761fb
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Understanding Pandas UDF, applyInPandas, and mapIn\.\.\. \- Databricks Community \- 75717](https://community.databricks.com/t5/technical-blog/understanding-pandas-udf-applyinpandas-and-mapinpandas/ba-p/75717)の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# イントロダクション

あなたにPandasのバックグラウンドがあるのであれば、シンプルなPandas on Spark APIからより柔軟性のあるPandas関数のパラダイムに移行することは、とても怖いことだと思うかもしれません。より重要なこととして、多くの人が考えることと、多くのアプローチの間の区別をすることは思った以上に難しく、それら全てを説明している単一のドキュメントを見つけ出すことは困難です。mapInPandasの特定のユースケースを議論している我々の同僚のTJによる[素晴らしいブログ記事](https://www.databricks.com/blog/processing-uncommon-file-formats-scale-mapinpandas-and-delta-live-tables)にも、(以下の)素敵な図が含まれています。この記事では、この図を拡張し、あなたのソリューションとして、Pandas UDF、applyInPandas、mapInPandaをどこで、どのように活用するのかを明確にします。エンドツーエンドのサンプルに関しては、[こちらのノートブック](https://github.com/josh-melton-db/blogs/blob/main/Understanding%20Pandas%20UDF%2C%20applyInPandas%2C%20mapInPandas.py)をクローンしてください。

![](https://community.databricks.com/t5/image/serverpage/image-id/8930i36EF7AD6728A4394/image-dimensions/437x119?v=v2)

重要なこととして、分散型のPandasオペレーションよりもネイティブのSpark関数を用いた方が高速になるということに触れておきます。カスタムのPandasのロジックやPandasだけで実装されているライブラリの以降の事情でSparkを使えない場合のフォールバックとしてのみ、分散Pandas関数を使うべきです。同じように、Pandasでシンプルなデータ変換処理を分散処理したい場合には、[Pandas on Spark](https://spark.apache.org/docs/latest/api/python/user_guide/pandas_on_spark/index.html)をトライすることができます。

しかし、Pandas on SparkのAPIが対応できるよりもより複雑なオペレーションを実行する必要がある場合や、Sparkでネイティブに実装されていないライブラリを使う際には、Pandas UDF、applyInPandas、mapInPandasを活用することで、Sparkの分散処理のパワーとPandasの柔軟性を組み合わせたいと考えることでしょう。

これらのアプローチのそれぞれによって、カスタムのPython関数内で標準的なPandasオブジェクト(データフレームやシリーズ)に対するオペレーションを行うことができます。これら3つのアプローチのどれを使うのかは、以下の表に示すように、あなたのカスタム関数が期待する入出力に大きく依存します。それぞれの入力行に対して1つの出力を期待するのであれば、Pandas UDFを使います。いくつかの特定のグルーピングされたデータで入力を処理するのであればapplyInPandasを使います。それぞれの入力業に対して複数の出力行を期待するのであれば、mapInPandasを使います。

|  入力 | 出力 | 手法 |
|:--|:--|:--|
| 1行  | 1行  | Pandas UDF   |
| 複数行  | 1行  | applyInPandas  |
|  1行 | 複数行  |  mapInPandas |

これらのコンセプトを説明するために、それぞれでシンプルな例を用います。はじめに、以下のようにランダムに生成されたSparkデータフレームを作成します:

```py
from pyspark.sql.functions import rand, pandas_udf, col
import pandas as pd

def generate_initial_df(num_rows, num_devices, num_trips):
   return (
       spark.range(num_rows)
       .withColumn('device_id', (rand()*num_devices).cast('int'))
       .withColumn('trip_id', (rand()*num_trips).cast('int'))
       .withColumn('sensor_reading', (rand()*1000))
       .drop('id')
   )

df = generate_initial_df(5000000, 10000, 50)
df.display()
```

# pandas_udf

次に、`sensor_reading`カラムの平方根を計算するためのPandas UDFを用いた例を説明します。関数を定義して、`@pandas_udf`でデコレーションすると、通常のSpark関数のように使用できるようになります。この例では一度に1つの列を操作していますが、Pandas UDFは使用するデータ構造に対して非常に大きな柔軟性を持っていることに注意してください。Pandas UDFは多くの場合、機械学習モデルによる予測結果を返却するために用いられます。詳細や例に関しては、[ドキュメント](https://docs.databricks.com/ja/udf/pandas.html)をご覧ください。

```py
@pandas_udf('double')
def calculate_sqrt(sensor_reading: pd.Series) -> pd.Series:
   return sensor_reading.apply(lambda x: x**0.5)

df = df.withColumn('sqrt_reading', calculate_sqrt(col('sensor_reading')))
df.display()
```

# applyInPandas

Pandasのオペレーションを分散させる別のテクニックがapplyInPandasです。`device_id`などに基づく個別のグループに対して並列でオペレーションを行いたい際に、applyInPandasを活用することができます。一般的なユースケースには、グループに対するカスタムの集計処理や正規化、グループに対する機械学習モデルのトレーニングなどがあります。この例では、使用してるデータフレームの粒度を`device_id`カラムに削減するPandasにおけるカスタム集計処理を実行します。`trip_id`カラムは`device_id`ごとの値のリストに変換され、`sensor_reading`と`sqrt_reading`カラムは`device_id`ごとの平均が計算されます。出力は`device_id`ごとに1行になります。重要なことですが、applyInPandasでは、お使いの関数はPandasデータフレームを受け取って返却することが求められ、[PyArrow](https://arrow.apache.org/docs/python/index.html)が効率的にシリアライズできるように、返却されるデータフレームのスキーマは事前に定義される必要があります。何かしらのキーに基づくグループに対して、モデルをトレーニングするためにapplyInPandasを用いる例に関しては、[こちらのソリューションアクセラレーター](https://github.com/databricks-industry-solutions/iot_distributed_ml)の4つ目のノートブックをご覧ください。

```py
def denormalize(pdf: pd.DataFrame) -> pd.DataFrame:
  aggregated_df = pdf.groupby('device_id', as_index=False).agg(
      {'trip_id': lambda x: list(x), 'sensor_reading': 'mean', 'sqrt_reading': 'mean'}
  )
  return aggregated_df

expected_schema = 'device_id int, trip_id array<int>, sensor_reading long, sqrt_reading long'
df = df.groupBy('device_id').applyInPandas(denormalize, schema=expected_schema)
df.display()
```

# mapInPandas

カスタムPandas関数を分散させる最後のアプローチはmapInPandasです。mapInPandas関数においては、それぞれの入力業に対して複数の行を返却することができ、applyInPandasとは逆の方法で操作を行うことを意味します。このためには、[Python Iterator](https://docs.python.org/3/c-api/iterator.html)を使用し、幾つの行を生成するのかに関する柔軟性を手に入れることができます。以下のシンプルな例では、データフレームの粒度を`trip_id`と`device_id`の組み合わせごとに1行になるように戻しています。この例は説明用であることに注意してください - シンプルにSparkネイティブの`explode()`を用いて、同じ結果をより優れたパフォーマンスで手に入れることができます。このアプローチのより現実的な使用法に関しては、一般的ではないファイルタイプを処理するためのmapInPandasの使い方を説明している上述の[ブログ記事](https://www.databricks.com/blog/processing-uncommon-file-formats-scale-mapinpandas-and-delta-live-tables)をご覧ください。

```py
def denormalize(pdf: pd.DataFrame) -> pd.DataFrame:
  aggregated_df = pdf.groupby('device_id', as_index=False).agg(
      {'trip_id': lambda x: list(x), 'sensor_reading': 'mean', 'sqrt_reading': 'mean'}
  )
  return aggregated_df

expected_schema = 'device_id int, trip_id array<int>, sensor_reading long, sqrt_reading long'
df = df.groupBy('device_id').applyInPandas(denormalize, schema=expected_schema)
df.display()
```

# まとめ

ここまでで、分散Spark環境においてPandasオブジェクトを操作するためにどのようにカスタムのPython関数を活用するのかを説明してきました。シンプルな例をカバーし、特定のアプローチをさらに調査するための詳細なリソースへのリンクを示しました。Pandas UDF、applyInPandas、mapInPandasのユースケースを理解し、並列でカスタムのPandasロジックを適用できるようになっているに違いありません！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

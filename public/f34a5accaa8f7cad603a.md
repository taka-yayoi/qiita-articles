---
title: 日本語に対してSpark NLPを使う
tags:
  - Databricks
  - SparkNLP
  - JohnSnowLabs
private: false
updated_at: '2022-04-09T06:37:23+09:00'
id: f34a5accaa8f7cad603a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
以前から[Spark NLP](https://www.johnsnowlabs.com/spark-nlp/)の存在は知っていたのですが、恥ずかしながら日本語に対応していることを最近まで知りませんでした。

なので、早速日本語を対象にDatabricks上でSpark NLPを使ってみました。

# Spark NLPとは

[John Snow Labs](https://www.johnsnowlabs.com/)が開発したSpark上での動作を前提とした、NLP(自然言語処理)ライブラリです。Spark MLを拡張する形で実装されているので、パイプラインの概念を使ってNLPパイプラインを容易に構築でき、さらにSparkの並列分散処理のメリットを享受することができます。Spark NLPの成り立ち、特徴については以下の記事をご覧ください。

https://qiita.com/taka_yayoi/items/fd7d099dfd8b25486499

# インストール

クラスターライブラリでもノートブックスコープライブラリでも構わないので、ライブラリをインストールします。以下の例ではノートブックスコープライブラリとしてインストールしています。

```
# Install PySpark and Spark NLP
%pip install -q pyspark==3.1.2 spark-nlp

# Install Spark NLP Display lib
%pip install --upgrade -q spark-nlp-display
```

```py:Python
import sparknlp
from pyspark.ml import Pipeline
from sparknlp.annotator import *
from sparknlp.base import *
from sparknlp.training import *
```

# 分かち書き

Spark NLPにおいては、トークナイズ、ストップワード除去などの処理を組み合わせてパイプラインを構築します。

https://nlp.johnsnowlabs.com/2021/03/09/wordseg_gsd_ud_ja.html

```py:Python
document_assembler = DocumentAssembler() \
  .setInputCol("text") \
  .setOutputCol("document")

sentence_detector = SentenceDetector() \
  .setInputCols(["document"]) \
  .setOutputCol("sentence")

word_segmenter = WordSegmenterModel.pretrained("wordseg_gsd_ud", "ja").setInputCols(["sentence"]).setOutputCol("token")

pipeline = Pipeline(stages=[document_assembler, sentence_detector, word_segmenter])

ws_model = pipeline.fit(spark.createDataFrame([[""]]).toDF("text"))

example = spark.createDataFrame([['データブリックスは、学術界とオープンソースコミュニティをルーツとするデータ＋AIの企業です。']], ["text"])
result = ws_model.transform(example)

display(result)
```

以下のように文が分割されていますが、結果がわかりにくいのでひと手間加えます。
![Screen Shot 2022-04-08 at 15.39.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1014e8ba-541b-eb1b-ec8b-ada69ac0525d.png)

結果を一時テーブルに格納します。

```py:Python
result.createOrReplaceTempView("word_segmentation_result")
```

こうすることで、SQLクエリーを簡単に実行できるようになります。上の結果は配列、ネストされているので、以下のようなクエリーを発行して一部のみを抽出します。

```sql:SQL
%sql
SELECT token.result FROM word_segmentation_result;
```

先ほどより結果がわかりやすくなりました。
![Screen Shot 2022-04-08 at 15.41.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ac496667-b673-61cc-675a-15f0165ce93a.png)

# 品詞抽出

名詞、動詞などの品詞を特定することもできます。以下ではパイプラインに`pos_tagger`を追加しています。

https://nlp.johnsnowlabs.com/2021/03/09/pos_ud_gsd_ja.html

```py:Python
document_assembler = DocumentAssembler() \
  .setInputCol("text") \
  .setOutputCol("document")

sentence_detector = SentenceDetector() \
  .setInputCols(["document"]) \
  .setOutputCol("sentence")

word_segmenter = WordSegmenterModel.pretrained("wordseg_gsd_ud", "ja")\
        .setInputCols(["sentence"])\
        .setOutputCol("token")

pos_tagger = PerceptronModel.pretrained("pos_ud_gsd", "ja") \
  .setInputCols(["document", "token"]) \
  .setOutputCol("pos")

pipeline = Pipeline(stages=[
  document_assembler,
  sentence_detector,
  word_segmenter,
  pos_tagger
])

example = spark.createDataFrame([['データブリックスは、学術界とオープンソースコミュニティをルーツとするデータ＋AIの企業です。']], ["text"])

pos_result = pipeline.fit(example).transform(example)
```

`NOUN`(名詞)などの品詞が抽出されていますが、こちらも結果がわかりにくいものになっていますので、上と同じアプローチを取ります。

![Screen Shot 2022-04-08 at 15.43.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1e3197ee-04ff-5fae-2ce8-000fddcb8ba4.png)

```py:Python
pos_result.createOrReplaceTempView("pos_result")
```

```sql:SQL
%sql
SELECT token.result, pos.result FROM pos_result;
```

以下のように品詞が抽出されていることがわかります。
![Screen Shot 2022-04-08 at 15.44.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5ebb241c-fabf-fa8e-ea37-6755e91fd4ef.png)


# NER(Named Entity Recognition)

日本語に対する固有表現抽出(固有名詞や数値の抽出)も可能です。

https://nlp.johnsnowlabs.com/2021/09/09/ner_ud_gsd_cc_300d_ja.html

```py:Python
documentAssembler = DocumentAssembler() \
    .setInputCol("text") \
    .setOutputCol("document")

sentence = SentenceDetector() \
    .setInputCols(["document"]) \
    .setOutputCol("sentence")

word_segmenter = WordSegmenterModel.pretrained("wordseg_gsd_ud", "ja") \
    .setInputCols(["sentence"]) \
    .setOutputCol("token")

embeddings = WordEmbeddingsModel.pretrained("japanese_cc_300d", "ja") \
    .setInputCols(["sentence", "token"]) \
    .setOutputCol("embeddings")
    
nerTagger = NerDLModel.pretrained("ner_ud_gsd_cc_300d", "ja") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ner")

ner_converter = NerConverter() \
    .setInputCols(['sentence', 'token', 'ner']) \
    .setOutputCol('ner_chunk')

pipeline = Pipeline().setStages([
    documentAssembler,
    sentence,
    word_segmenter,
    embeddings,
    nerTagger,
    ner_converter
])
```

抽出した結果を可視化する関数を準備します。

```py:Python
from sparknlp_display import NerVisualizer

def display_ner(text):
  example = spark.createDataFrame([[text]], ["text"])
  result = pipeline.fit(example).transform(example)
  
  ner_vis = NerVisualizer().display(
    result = result.collect()[0],
    label_col = 'ner_chunk',
    document_col = 'document',
    return_html=True
  )

  displayHTML(ner_vis)
```

[徳川家康 \- Wikipedia](https://ja.wikipedia.org/wiki/%E5%BE%B3%E5%B7%9D%E5%AE%B6%E5%BA%B7)の文を入力してみます。

```py:Python
display_ner("徳川 家康（とくがわ いえやす、旧字体：德川 家康、1542年 - 1616年）は、戦国時代から江戸時代初期の日本の武将、戦国大名。松平広忠の長子。江戸幕府初代将軍。安祥松平家第9代当主で徳川家の始祖。幼名は竹千代（たけちよ）、諱は元信（もとのぶ）、元康（もとやす）、家康と改称。")
```

![Screen Shot 2022-04-09 at 6.34.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f6e39b94-14d1-bbbf-52d6-171e96612e29.png)


~~表示結果のラベルが途切れているのはご愛嬌ということで。データ自体はきちんと抽出されています。Githubに[issue](https://github.com/JohnSnowLabs/spark-nlp/issues/7688)として報告しておきました。~~

:::note info
上記は私の認識違いで、NerConverterに対応しているNERモデルを使う必要がありました。
:::

これらのSpark NLPの機能は全て無料で利用できます。大量テキストデータに対する処理を高速化するためにSpark NLPを活用してみてはどうでしょうか。

# サンプルノートブック

https://github.com/taka-yayoi/public_repo/tree/main/SparkNLP

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

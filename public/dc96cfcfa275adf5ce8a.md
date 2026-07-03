---
title: DatabricksでSparkNLPとMLLibを使って分散トピックモデリングをやってみる(日本語編)
tags:
  - Spark
  - LDA
  - MLlib
  - Databricks
  - SparkNLP
private: false
updated_at: '2022-05-17T14:41:02+09:00'
id: dc96cfcfa275adf5ce8a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらでトライした分散LDAの日本語対応版です。

https://qiita.com/taka_yayoi/items/15d384b2497631dc97bc

ノートブックはこちらです。

https://github.com/taka-yayoi/public_repo/blob/main/distributed_LDA/distributed%20LDA_JPN.py

[クラスターの設定](https://qiita.com/taka_yayoi/items/15d384b2497631dc97bc#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AE%E8%A8%AD%E5%AE%9A)と[ライブラリの設定](https://qiita.com/taka_yayoi/items/15d384b2497631dc97bc#%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%82%A4%E3%83%B3%E3%83%9D%E3%83%BC%E3%83%88)は前回と同じです。

# データのロード

[ダウンロード \- 株式会社ロンウイット](https://www.rondhuit.com/download.html)から、**livedoor ニュースコーパス** [ldcc\-20140209\.tar\.gz](https://www.rondhuit.com/download/ldcc-20140209.tar.gz)をダウンロードします。

以下のようなPythonスクリプトを使って記事のタイトルを抽出します。

```py:extract_titles.py
import glob

files = glob.glob("./topic-news/topic-news-*.txt")
print("publish_date,headline_text")
for file in files:
    #print(file)
    f = open(file, 'r')
    datalist = f.readlines()
    print(datalist[1].strip(), ",",  datalist[2].strip())
```

ターミナルでスクリプトを実行してCSVファイルを作成します。

```sh
python extract_titles.py > topic-news.csv
```

以下の手順でCSVファイルをDatabricksにアップロードします。
1. サイドメニューの**データ**をクリックし、**アップロード**ボタンをクリックします。
1. アップロードするパスを選択して、CSVファイルをドラッグ&ドロップします。

　以下の例では、下のパスにアップロードしています。
> `dbfs:/FileStore/shared_uploads/takaaki.yayoi@databricks.com/news/topic_news.csv`

ファイルをロードして中身を確認します。

```py:Python
file_location = "dbfs:/FileStore/shared_uploads/takaaki.yayoi@databricks.com/news/topic_news.csv"
file_type = "csv"

# CSVのオプション
infer_schema = "true"
first_row_is_header = "true"
delimiter = ","

df = spark.read.format(file_type) \
  .option("inferSchema", infer_schema) \
  .option("header", first_row_is_header) \
  .option("sep", delimiter) \
  .load(file_location)

# レコード数の確認
df.count()
```

```py:Python
display(df)
```

![Screen Shot 2022-05-17 at 14.35.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9340613a-2ddb-4231-1ba2-1283fbd00ccd.png)

# Spark NLPを用いた前処理パイプライン

日本語に対応している以下のアノテーターを使用します。

- WordSegmenterModel: [Japanese Word Segmentation\- Spark NLP Model](https://nlp.johnsnowlabs.com/2021/01/03/wordseg_gsd_ud_ja.html)
- StopWordsCleaner: [Stopwords Remover for Japanese language \(153 entries\)\- Spark NLP Model](https://nlp.johnsnowlabs.com/2022/03/07/stopwords_iso_ja_3_0.html)

```py:Python
# Spark NLPはドキュメントに変換する入力データフレームあるいはカラムが必要です
document_assembler = DocumentAssembler() \
    .setInputCol("headline_text") \
    .setOutputCol("document") \
    .setCleanupMode("shrink")

# 文をトークンに分割(array)
tokenizer = Tokenizer() \
  .setInputCols(["document"]) \
  .setOutputCol("token")

# 日本語の文をトークンに分割(array)
word_segmenter = WordSegmenterModel.pretrained('wordseg_gsd_ud', 'ja')\
        .setInputCols(["document"])\
        .setOutputCol("token")    

# 不要な文字やゴミを除外
normalizer = Normalizer() \
    .setInputCols(["token"]) \
    .setOutputCol("normalized")

# 日本語ストップワードの除外
stop_words_remover = StopWordsCleaner.pretrained("stopwords_iso", "ja") \
    .setInputCols(["normalized"]) \
    .setOutputCol("cleanTokens")

# Finisherは最も重要なアノテーターです。Spark NLPはデータフレームの各行をドキュメントに変換する際に自身の構造を追加します。Finisherは期待される構造、すなわち、トークンの配列に戻す助けをしてくれます。 
finisher = Finisher() \
    .setInputCols(["cleanTokens"]) \
    .setOutputCols(["tokens"]) \
    .setOutputAsArray(True) \
    .setCleanAnnotations(False)

# それぞれのフェーズが順番に実行されるようにパイプラインを構築します。このパイプラインはモデルのテストにも使うことができます。
nlp_pipeline = Pipeline(
    stages=[document_assembler, 
            word_segmenter,
            normalizer,
            stop_words_remover,
            finisher])

# パイプラインのトレーニング
nlp_model = nlp_pipeline.fit(df)

# データフレームを変換するためにパイプラインを適用します。
processed_df  = nlp_model.transform(df)

# NLPパイプラインは我々にとって不要な中間カラムを作成します。なので、必要なカラムのみを選択します。
tokens_df = processed_df.select('publish_date','tokens').limit(10000)

display(tokens_df)
```

![Screen Shot 2022-05-17 at 14.36.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a5e1448b-7c95-16af-58ed-b3b78e9316ef.png)

# 特徴量エンジニアリング

こちらのロジックも[前回](https://qiita.com/taka_yayoi/items/15d384b2497631dc97bc#%E7%89%B9%E5%BE%B4%E9%87%8F%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2%E3%83%AA%E3%83%B3%E3%82%B0)から変更はありません。

```py:Python
from pyspark.ml.feature import CountVectorizer

cv = CountVectorizer(inputCol="tokens", outputCol="features", vocabSize=500, minDF=3.0)

# モデルのトレーニング
cv_model = cv.fit(tokens_df)

# データを変換します。出力カラムが特徴量となります。
vectorized_tokens = cv_model.transform(tokens_df)

display(vectorized_tokens)
```

![Screen Shot 2022-05-17 at 14.38.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cdae4b7c-1125-7d3f-3246-a45d33adb221.png)

以降のロジックも[前回](https://qiita.com/taka_yayoi/items/15d384b2497631dc97bc#lda%E3%83%A2%E3%83%87%E3%83%AB%E3%81%AE%E6%A7%8B%E7%AF%89)から変更ありませんが、日本語記事からトピックを抽出することができています。
![Screen Shot 2022-05-17 at 14.39.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/76ea817c-7bba-8afa-3a3f-da65eae2b4d7.png)

しかし、1文字のキーワードが抽出されていたりするので、NLPパイプラインを含めたチューニングを行う余地はまだあります。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

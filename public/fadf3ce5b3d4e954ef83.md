---
title: Hugging FaceとDeepSpeedによる大規模言語モデルのファインチューニング
tags:
  - Databricks
  - huggingface
  - DeepSpeed
  - LLM
private: false
updated_at: '2023-04-05T20:11:27+09:00'
id: fadf3ce5b3d4e954ef83
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Fine\-Tuning Large Language Models with Hugging Face and DeepSpeed \- The Databricks Blog](https://www.databricks.com/blog/2023/03/20/fine-tuning-large-language-models-hugging-face-and-deepspeed.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# 数十億のパラメータを持つ大規模言語モデルの容易な適用とカスタマイズ

ChatGPTのセンセーショナルなリリースに続いて、大規模言語モデル(LLM)は現在スポットライトを浴びています。多くの人々は、自身のアプリケーションでこのようなモデルをどのように活用するのかを検討しています。しかし、これは、チャットだけではなく、翻訳、分類、要約などのオープンかつすぐに利用できるタスクのようなトランスフォーマーベースモデルのいくつかの進歩の単なる一部でしかありません。

[以前の記事](https://qiita.com/taka_yayoi/items/f0540a29b3cfa9868585)では、人気の[Hugging Face](https://huggingface.co/)トランスフォーマーライブラリを通じた、Databricksにおけるこれらのモデルの基本的な使い方を探索しました。[T5](https://github.com/google-research/text-to-text-transfer-transformer)や[BERT](https://github.com/google-research/bert)のようにすぐに利用でき、事前学習済みのLLMは、追加のデータやトレーニングなしに、様々な現実世界の問題をうまく解きます。しかし、時には特定タスクでよりうまく動作するように、これらのモデルを「ファインチューン」することが重要となります。

この記事では、言語モデルの[T5](https://github.com/google-research/text-to-text-transfer-transformer)ファミリーを、シンプルなユースケースである「様々な商品レビューから商品レビューの概要の作成」に特化するために、最小サイズから最大サイズまでの容易なファインチューニングを探索します。[MLflowインテグレーション](https://huggingface.co/docs/transformers/v4.26.1/en/main_classes/callback#transformers.integrations.MLflowCallback)を含むHugging FaceをDatabricksで活用します。

また、長大言語モデルのファインチューニングを加速するために、Microsoftの[DeepSpeed](https://github.com/microsoft/DeepSpeed)を導入します。必要であれば、Databricks上で110兆のパラメーターを持つモデルであっても、ファインチューニングすることは難しいことではありません！

# 問題: 商品レビューの要約

あなたがカメラ製品を売っているeコマースサイトを運営しているとしましょう。ユーザーは製品に対するレビューを行い、あなたはそれら数百のレビューを読むのではなく、ある製品に対するお客様の*すべての*レビューを一つの要約にまとめることができたら素晴らしいのではと考えます。数千のレビューとユーザーが入力したヘッドライン(これはある種、レビューの「要約」です)を収集し、これらの製品の要約を作成するためにLLMを活用したいと考えています。このようなデータセットの代替になるものとして、このサンプルではAmazonの顧客の1.3億の製品レビューを含む[Amazon Customer Review dataset](https://s3.amazonaws.com/amazon-reviews-pds/readme.html)を活用します。ここでの興味の対象は、当然ですが「カメラ」カテゴリーのレビューのテキスト、ヘッドラインとなります。

このデータセットのフリーテキストは、完全にきれいなものではありません。*あなたの*eコマースサイトが保持する、すばらしく、整理されたデータセットを模倣するために、いくつかの基本的なクリーニングを適用し、Deltaテーブルに書き込みます。ここでは、あまりに長いシーケンスはアウトオブメモリーエラーを引き起こすことがあるので、レビューの長さは100トークンに(ある程度任意ですが)制限されます。シーケンスが短いほどファインチューニングは高速になりますが、もちろん、ある程度の精度の低下との引き換えとなります。いくつかのレビューテキストは除外されます。

```py:Python
...
def clean_text(text, max_tokens):
  ...
  approx_tokens = 0
  cleaned = ""
  for fragment in split_regex.split(text):
    approx_tokens += len(fragment.split(" "))
    if (approx_tokens > max_tokens):
      break
    cleaned += fragment
  return cleaned.strip()

@udf('string')
def clean_review_udf(review):
  return clean_text(review, 100)
...

camera_reviews_df.select("product_id", "review_body", "review_headline").\
  sample(0.1, seed=42).\
  withColumn("review_body", clean_review_udf("review_body")).\
  withColumn("review_headline", clean_summary_udf("review_headline")).\
  filter("LENGTH(review_body) > 0 AND LENGTH(review_headline) > 0").\
  write.format("delta").save("/tmp/.../review/cleaned")
```

![Screenshot 2023-03-25 at 6.57.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8d54cbc0-6512-99bb-e353-19e8d6333676.png)

より良くなりました。ここからスタートし、このデータに対して大規模言語モデルは何ができるのかを見ていきましょう。

# t5-smallによるクイックな要約

[T5](https://github.com/google-research/text-to-text-transfer-transformer)(Text-to-Text Transfer Transformer)は、Googleによる汎用LLMのファミリーです。要約、分類、翻訳のような数多くのタスクで有用であり、「小規模」なサイズ(~60M パラメーター)から非常に大規模なもの(~11B パラメーター)が提供されています。これら複数のサイズは大きくなるほどにパワフルなものとなりますが、取り扱に要するコストも増加します。これらLLMの取り扱いにおける重要なテーマは、「シンプルに保つ」ということです。十分であるならば小規模なモデルを使用し、可能であればすぐに利用できるリソースからスタートします。大規模なモデルによる推論は、より長い時間と高いコストを必要とし、レーテンシーと予算の制約によって、開始時点では大規模モデルは対象外ということになるかもしれません。

以前の記事では、SparkとHugging Faceを用いることで、どれだけ容易にT5を適用できるのかを説明し、そのことはここでも同様です。このデータセットに対してそのままでうまく動作するのかは明らかになっていませんが、入力テキストと出力テキストは非常に短いので、すぐにわかります。振り返りとなりますが、いくつかの新たな要素を用います:

```py:Python
os.environ['TRANSFORMERS_CACHE'] = "/dbfs/.../cache/hf"

summarizer_pipeline = pipeline("summarization",
  model="t5-small", tokenizer="t5-small", num_beams=10)
summarizer_broadcast = sc.broadcast(summarizer_pipeline)

@pandas_udf('string')
def summarize_review(reviews):
  pipe = summarizer_broadcast.value(
    ("summarize: " + reviews).to_list(), batch_size=8, truncation=True)
  return pd.Series([s['summary_text'] for s in pipe])

camera_reviews_df = spark.read.format("delta").load("/tmp/.../review/cleaned")

display(camera_reviews_df.withColumn("summary", 
  summarize_review("review_body")).select("review_body", "summary").limit(10))
```

![Screenshot 2023-03-25 at 7.05.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ba77ac82-b71f-4446-0cfa-03d12b6b2461.png)

数行のコードと数分の実行にしては悪くありません - これはGPUすらも必要としていません。結果はレビューの簡潔な要約となっているので、それらしく見えます。しかし、ストックモデルは、非常に短いレビューの要約には苦慮しており、最初の2つの要約においては、若干長くなっています！これは、いくつかのファインチューニングが必要であることを示しています。

上の一覧は、いくつかの有用な活用ティップスをハイライトしています:

- モデルを一度だけダウンロードし、さまざまなジョブやクラスターで再利用できるように、`TRANSFORMERS_CACHE`環境変数に`/dbfs`を設定しています。
- パイプラインをブロードキャストすることで、Sparkは効率的にそれらを転送、共有することができます - これはここでは重要ではありませんが、大規模モデルでは重要となります。
- 入力のバッチを一度に効率的に処理するために、Sparkで[pandas UDF](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.pandas_udf.html)を活用しています。
- t5-smallのような小規模モデルでスタートし、必要に応じて大きくします。
- 要約パイプラインにはいくつかの設定があり、それらのいくつかを理解していくことは有用です:
    - `min_new_tokens`は出力があまり短くならないようにします。これは、より多くのテキストに対してより長い要約を生成するために後で使用されます。これは後ほど使用します。
    - `num_beams`はより多くの可能性を試すことで、出力の品質を改善することがありますが、より多くの計算コストを必要とします。

ここまででは、それほど新しいことはありません。しかし、ここでのゴールはそれぞれの製品に対する*すべての*レビューを要約することです。これはSparkを使えば簡単です。単に要約するレビューのテキストを集約するだけです:

```py:Python
summarizer_pipeline = pipeline("summarization",
  model="t5-small", tokenizer="t5-small", num_beams=10, min_new_tokens=50)
summarizer_broadcast = sc.broadcast(summarizer_pipeline)

@pandas_udf('string')
def summarize_review(reviews):
  pipe = summarizer_broadcast.value(
    ("summarize: " + reviews).to_list(), batch_size=8, truncation=True)
  return pd.Series([s['summary_text'] for s in pipe])

review_by_product_df = camera_reviews_df.groupBy("product_id").\
  agg(collect_list("review_body").alias("review_array"), 
      count("*").alias("n")).\
  filter("n >= 10").\
  select("product_id", "n", concat_ws(" ", col("review_array")).alias("reviews")).\
  withColumn("summary", summarize_review("reviews"))

display(review_by_product_df.select("reviews", "summary").limit(10))
```

こちらが、シンプルにするために切り出した、集計レビューによるアウトプットのサンプルです。
![Screenshot 2023-03-25 at 7.15.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2801434d-8989-da0b-67cc-66eddeea55cc.png)

興味深いですが、この要約が十分に良いものであるかどうかは明確ではありません。論理的な次の2つのステップは、大規模なモデルを試す、あるいは、これらのモデルをファインチューニングするということです。以下のセクションでは、両方をトライします。

# すぐに使えるファインチューニング

ファインチューニングは、シンプルに特定のタスクにおけるパフォーマンスを改善するために、新たなデータに対して事前学習済みモデルをさらにトレーニングすることを意味します。T5のようなモデルは、ある単語のシーケンスを別のものに変換するような様々なことを行うようにトレーニングされています。ここでは、ある一つのことうまく行う必要があります: 大量の製品レビューをレビューの要約に変換するということです。これは、T5はうまく動作しているので、すでに手元にある実際のレビューデータによりフィットするように要約を調整したいという要約タスクのようなものとなります。これは、T5アーキテクチャを最初からトレーニングするのとは異なります。これはより長い時間を要するだけではなく、事前学習済みT5モデルがすでに有している言語に関する関連学習結果の全てを失うことになります。

これは、既存のモデル、モデル作成に至ったすべての研究成果、データ、計算パワーを再利用できるので、実際のものごとの複雑性に比べて、上の例は嬉しいことにシンプルなものとなっています。しかし、ファインチューニングは経験のある実践者によるモデルの*トレーニング*であり、トレーニングプロセスを継続するために必要なPyTorchやTensorflowのコードを記述することは簡単ではありません。

幸運なことに、これらのオープンソースモデルは多くの場合、トレーニングコードやファインチューニングコードと一緒に提供されています。ノートブックのユーザーにとっては不運ですが、これらは大抵ノートブックではなくPythonスクリプトです。これは、Databricksでは問題になりません。ノートブックではシェルコマンドや、gitリポジトリのスクリプトを実行でき、あるいは、[Webターミナル](https://docs.databricks.com/clusters/web-terminal.html)でインタラクティブに実行することもできます。

## ファインチューニングスクリプトの取得

実際、Hugging Face*でも*、Trainer API経由で[T5モデルで動作するいくつかの便利なファインチューニングスクリプト](https://github.com/huggingface/transformers/blob/main/examples/pytorch/summarization/run_summarization.py)を提供しています。最初は便利そうに見えないかもしれませんが、これらのスクリプトを活用するメリットは後ほど明らかになります。既存のソリューションの再利用は、クイックにスタートする際の素晴らしいアプローチとなります。

最初に、DatabricksのRepoとして[Hugging Face Github repository](https://github.com/huggingface/transformers)をクローンします。スパースチェックアウトモードを用いて、リポジトリ全体ではなく要約のサンプルのみをクローンします:
![](https://cms.databricks.com/sites/default/files/inline-images/db-551-blog-imgs-1.png)

これによって、`run_summarization.py`スクリプトのコピーを取得します。また、お使いのRepoに[run\_summarization\.py](https://raw.githubusercontent.com/huggingface/transformers/main/examples/pytorch/summarization/run_summarization.py)をコピーアンドペーストするだけでも構いません。

1箇所変更が必要です。このスクリプトは、transformersライブラリのバージョンが期待しているものにマッチしているかをチェックします。このソースのチェックアウトは、ソースコードでtransformersをインストールすることを期待します。実際に、このファイルを変更するのではなく、`%pip install git+https://github.com/huggingface/transformers`を追加することができますが、このチェックを削除しても構いません。コピーしたコードから`check_min_version("...dev0")`の行を削除します。

## 環境セットアップ

例外なく、これらのスクリプトは少々のセットアップを必要とします。[Databricks Runtime 12\.2 ML](https://docs.databricks.com/release-notes/runtime/12.2ml.html)(GPU - これは間違いなくGPUが必要です！)では:

- ランタイムに含まれていない必要ライブラリのインストール:

    ```
    %pip install 'transformers>=4.26.0' datasets evaluate rouge-score
    ```

- Hugging Faceの[MLflowインテグレーション](https://huggingface.co/docs/transformers/v4.26.1/en/main_classes/callback#transformers.integrations.MLflowCallback)のために、Databricksがホストする[MLflow](https://mlflow.org/)トラッキングサーバーに接続するための環境変数の設定:

    ```py:Python
    os.environ['DATABRICKS_TOKEN'] = dbutils.notebook.entry_point.\
  getDbutils().notebook().getContext().apiToken().get()
    os.environ['DATABRICKS_HOST'] = "https://" + 
  spark.conf.get("spark.databricks.workspaceUrl")
    os.environ['MLFLOW_EXPERIMENT_NAME'] =
  "/Users/.../fine-tuning-t5"
    os.environ['MLFLOW_FLATTEN_PARAMS'] = "true"
    ```

あるモダンなGPUは、t5-smallのファインチューニングを容易に行います。これは、これらのモデルに対応している最新のNVIDIAのA10やA100のようなGPUのAmpereアーキテクチャを活用することのメリットです。例えば、AWSではこれはg5インスタンスタイプとなります。A10はA100よりもすぐに利用できるかもしれません。

このようなスクリプトは、大抵ローカルの入力ファイルを必要とします。ここでは、このチューニングスクリプトは(text, summary)のペアを持つCSVファイルを必要とします。問題ありません。`/dbfs`によって、分散ストレージはローカルファイルのように参照できます。単に、トレーニングファイルと検証用ファイルのペアとしてDeltaのデータセットを書き出すだけです:

```py:Python
train_df, val_df = camera_reviews_cleaned_df.randomSplit([0.9, 0.1], seed=42)
train_df.toPandas().to_csv("/dbfs/.../camera_reviews_train.csv", index=False)
val_df.toPandas().to_csv("/dbfs/.../camera_reviews_val.csv", index=False)
```

## ファインチューニングのチューニング

実際のファインチューニングは、スクリプトを実行するということになります。これはあまり盛り上がるものではありません。

```sh:Shell
%sh export DATABRICKS_TOKEN && export DATABRICKS_HOST && export MLFLOW_EXPERIMENT_NAME && export MLFLOW_FLATTEN_PARAMS=true && python \
    /Workspace/Repos/.../summarization/run_summarization.py \
    --model_name_or_path t5-small \
    --do_train \
    --do_eval \
    --train_file /dbfs/.../review/camera_reviews_train.csv \
    --validation_file /dbfs/.../review/camera_reviews_val.csv \
    --source_prefix "summarize: " \
    --output_dir /dbfs/.../review/t5-small-summary \
    --optim adafactor \
    --num_train_epochs 8 \
    --bf16 \
    --per_device_train_batch_size 64 \
    --per_device_eval_batch_size 64 \
    --predict_with_generate \
    --run_name "t5-small-fine-tune-reviews"
```

このスクリプトには、ここでカバーするには多すぎるパラメーターがありますが、いくつかは説明する価値があります:

- 環境変数をexportすることで、MLflowインテグレーションが動作します。
- `source_prefix: "summarize: "`によって、T5がデータがテキスト要約のサンプルであることを理解する助けになります。
- `optim`: [Adafactor](https://arxiv.org/abs/1804.04235)オプティマイザはここでは厳密に必要ではありませんが、より大きなモデルをチューニングする際にはメモリー使用料の削減が重要となることがあります。
- `bf16`: これによって、より広い数値レンジを保持する[bfloat16](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format)タイプを用いて、16ビットの浮動小数計算処理を高速にします。
- `num_train_epochs`: ファインチューニングは、最初からのトレーニング程のエポック数を必要としませんので、ある程度のエポック数で十分です。
- `per_device_train_batch_size`: これはバッチサイズをコントロールする重要なパラメーターです。すべてのトレーニングと同じように、大きなバッチサイズはGPUメモリーを使い切ってしまうことがあります。これは、より大規模なモデルをトレーニングする際には大きな問題となりますが、短いシーケンスのデータセットで、24GB以上のメモリーを持つモダンなGPUでは、64のような大きな数で十分です。このパラメーターによって、燃費は大きく変化します。

これは、例えばA10 GPUであれば1時間と数ドルを必要とします。トレーニングの過程(以降)では、MLflowがステップごとのロスのようなトレーニングメトリクスを記録します。
![](https://cms.databricks.com/sites/default/files/inline-images/db-551-blog-img-2.png)

トレーニングをさらに続行することもできそうですが、概ね収束するには8エポックで十分のように見えます。それ以外のもの(評価メトリクス、モデル)もキャプチャされ、さらに他の情報(チェックポイント、[TensorBoard](https://docs.databricks.com/machine-learning/train-model/tensorflow.html#tensorboard)ログ)をキャプチャすることができます。MLflowがどのようにモデルを追跡し、REST APIにでブロイすることができるのかの詳細に関しては、添付ノートブックをご覧ください。
![](https://cms.databricks.com/sites/default/files/inline-images/db-551-blog-img-3.png)

要約の品質を評価する[ROUGE metrics](https://en.wikipedia.org/wiki/ROUGE_(metric))のように、モデルとともに自動で記録された追加のメトリクスを参照することができます。このメトリックはロスよりも意味のある全体像をある程度提供するので、*どのくらい長く*ファインチューニングをすべきかを決定する際には有用です。

以上です！これでオープンですぐに利用できるモデルとツールを用いて、Databricks上でT5モデルをファインチューンしました。結果はどうでしょうか、改善したのでしょうか？上で説明した要約パイプラインを、あなたのモデル出力パスで「t5-small」を置き換えて再実行するだけです。

```py:Python
...
summarizer_tuned = pipeline("summarization", \
  model="/dbfs/.../review/t5-small-summary", \
  tokenizer="/dbfs/.../review/t5-small-summary", \
  num_beams=10, min_new_tokens=50)
...
```
![Screenshot 2023-03-25 at 8.21.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0bb64e8b-d624-de36-e92b-88bcb84df4bc.png)

期待した通り、テキストは間違いなくレビューのヘッドラインのようになっています。多分ある程度の深みは失われているのでしょうけど！これは数クリックで[REST API](https://docs.databricks.com/archive/serverless-inference-preview/serverless-real-time-inference.html)にすることも可能です。

REST APIを検討するのであれば、*レーテンシー*について考えることも重要です。サマリーに反応するのにどのくらい時間がかかるのでしょうか？レーテンシーが重要な場合、GPUで実行することが重要となります。結果として、単一のサマリーの実行自体は、480msほどかかります。

より洗練された要約を得るために、より大規模なT5モデルを試す価値があります。

# DeepSpeedによるt5-largeの高速化

60Mパラメーターから770Mパラメーターへというように、モデルを大幅に大きくする際であっても、t5-largeのようなモデルへのスケールアップを行う際の変更はごくわずかです。実際、上のファインチューニングを実行する際の変更は:

- 1つのGPUを複数、例えば4つのA10 GPUに切り替え
- t5-largeを指定
- バッチサイズを約12に削減

非常に大きなモデルは、より多くのハードウェアを必要とし、一度にGPUに収まる量は減ることを意味します。バッチサイズを適切に設定することは、シーケンスの長さが不均等で、時には長くこともあって困難となります。これが、データ準備でレビューと要約の長さを限定した理由です。また、このスクリプトは手動で入力を切り取るための`max_source_length`のようなオプションがあります。入力を小さくすることはスケールの助けとなりますが、問題によっては任意に入力を切り取ることでモデルの品質を損なうことがあります。

これらの変更を行い再実行すると、動作することを確認できるでしょう。また、エポックごとに2時間かかります。コストはもはや数ドルレベルではなく、8エポックで$90程度かかります。このため、エポック数の注意深い検討が重要になってきます。例えば、4エポックの実行では上のプロットにおいて劇的に大きなロスにつながっているようには見えませんので、スタートする際、最低でもこの時点てチューニングを行うのであれば4エポックの実行には合理性があるかもしれません。場合によっては、常にチェックポイントから再開し、必要に応じてさらにトレーニングを行うこともできます。

## DeepSpeedにようこそ

また、すぐに利用できるHugging Faceのようなツールではなく、より洗練された並列性を活用することが重要になります。幸運なことに、ここでもオープンソースがその答えとなります。Microsoftの[DeepSpeed](https://github.com/microsoft/DeepSpeed)は、数多くの洗練された最適化を実装することで、少量の変更あるいは変更なしで、既存のディープラーニングトレーニングや推論ジョブを加速することができます。ここで特に興味があるのは、メモリー使用量を削減する目的の一連の最適化処理であるZeROです。詳細や論文については、[DeepSpeed](https://www.deepspeed.ai/)サイトをご覧ください。

DeepSpeedを活用するには、パッケージとaccelerateをインストールします。`%pip install … git+https://github.com/microsoft/DeepSpeed accelerate`でリリースされているパッケージでも動作しますが、ソースからインストールすることをお勧めします。

DeepSpeedを用いた同じ処理の実行は若干異なります:

```sh:Shell
%sh export DATABRICKS_TOKEN && export DATABRICKS_HOST && export MLFLOW_EXPERIMENT_NAME && export MLFLOW_FLATTEN_PARAMS=true && deepspeed \
    /Workspace/Repos/.../run_summarization.py \
    --deepspeed /Workspace/Repos/../ds_config_zero2_no_offload_adafactor.json \
    --model_name_or_path t5-large \
    --do_train \
    --do_eval \
    --train_file /dbfs/.../camera_reviews_train.csv \
    --validation_file /dbfs/.../camera_reviews_val.csv \
    --source_prefix "summarize: " \
    --output_dir /dbfs/.../t5-large-summary-ds \
    --optim adafactor \
    --num_train_epochs 4 \
    --gradient_checkpointing \
    --bf16 \
    --per_device_train_batch_size 20 \
    --per_device_eval_batch_size 20 \
    --predict_with_generate \
    --run_name "t5-large-fine-tune-reviews-ds"
```

pythonはdeepspeed runnerスクリプトで置き換えられます。また、設定ファイルへのパスを指定します。このファイルのオプションの探索はここでのスコープ外ですが、[デフォルトの "ZeRO stage 2" 設定](https://huggingface.co/docs/transformers/main_classes/deepspeed#zero2-example)でスタートすることには合理性があり、少々の変更を加えます。例えば、現在のセットアップでは以下の2つの変更を行います:

- 明示的にbf16を有効化(通常のfloat16 / fp16サポートを無効化)
- AdamWではなく[Adafactor](https://arxiv.org/abs/1804.04235)を使用するようにオプティマイザの設定を削除。Adafactorは少量のメモリで済み、非常に大きなモデルをファインチューニングする際には優れた選択肢となります。

DeepSpeedによって、さらなる改善が可能となります::

- `gradient_checkpointing`: フォワードパスである程度大きな中間結果をリリースし、バックワードパスでそれらを再計算します。これによって、より少ない計算コストでメモリーを節約できます。
- デバイスごとのバッチサイズは最大20まで増加させることができます(必要に応じて高くなるでしょう)。4GPUでは、効果的なバッチサイズは4 x 20 = 80となることに注意してください。

バッチサイズは重要なチューニングの問題となります。個々のGPUメモリーがGPUで一度にどれだけの処理を行えるのかを制限するので、バッチサイズは多くの場合、デバイスごとにチューニングされます。バッチサイズを大きく数rとスループットを増加させます - GPUメモリーを使い果たさない限りですが！最大のバッチサイズは、GPUメモリー、入力シーケンスのサイズ、モデルの最大レイヤーのサイズ、オプティマイザの設定などいくつかの要因に依存します。多くの場合、ある程度のトライアンドエラーを通じてチューニングする必要があります。

時には、過度に大きなバッチサイズはトレーニングでも問題となります。しかし、非常に大規模な言語モデルを用いることで、この問題は大抵のケースで、複数あるいは一つのバッチをそれぞれのデバイスのメモリーにフィットさせる手段を見つけ出します。バッチサイズは結果の再現においても重要なので、少なくとも、効果的なバッチサイズが(*デバイスの数 x デバイスごとのバッチサイズ*)であることを念頭に置くことが重要です。

これによって、実行時間がエポックごとに40分にまで削減されます。3倍高速ということは、3倍安価であり、このチューニングのコストは$30程度になります。これは、処理が数日要し、コストが数百ドル、数千ドルになる際には非常に価値のあるものとなります。

この改善は、DatabricksクラスターにおけるこれらのGangliaメトリクスのようなGPUメトリクスで確認することができます。

*DeepSpeedなし:*
![](https://cms.databricks.com/sites/default/files/inline-images/db-551-blog-imgs-4.png)

*DeepSpeedあり:*
![](https://cms.databricks.com/sites/default/files/inline-images/db-551-blog-imgs-5.png)

このモデルでの要約はどのようになったでしょうか？
![Screenshot 2023-03-25 at 9.45.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/967f0514-46dc-3f2a-f4a9-26842240af46.png)

簡潔であり、レビューテキストからの正確な詳細を示しているのでおそらくより良くなっています。単体のGPUにおけるモデルのレーテンシーは3秒程度であり、より大規模なモデルにさらにスケールさせることを検討し始めることになるかもしれません。ここでストップしても構いませんが、最大のT5モデルにスケールアウトすることも可能です。

# スーパーサイズで: t5-11bのファインチューニング

最大のT5モデルはt5-11bであり、あなたが想像するようにt5-largeの14倍以上の110億のパラメーターを有しています。これのファインチューニングは1台のマシンでも*依然として*可能ですが、同じアプローチを用いてクラウドで利用できる最大のタイプを活用することができます。

```sh:Shell
%sh export DATABRICKS_TOKEN && export DATABRICKS_HOST && export MLFLOW_EXPERIMENT_NAME && export MLFLOW_FLATTEN_PARAMS=true && deepspeed \
    /Workspace/Repos/.../run_summarization.py \
    --deepspeed /Workspace/Repos/.../ds_config_zero3_adafactor.json \
    --model_name_or_path t5-11b \
    --do_train \
    --do_eval \
    --train_file /dbfs/.../camera_reviews_train.csv \
    --validation_file /dbfs/.../camera_reviews_val.csv \
    --source_prefix "summarize: " \
    --output_dir /dbfs/.../t5-11b-summary \
    --optim adafactor \
    --num_train_epochs 1 \
    --gradient_checkpointing \
    --bf16 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 8 \
    --predict_with_generate \
    --run_name "t5-11b-fine-tune-reviews"
```

これは巨大なタスクであり、実際のところ、これを合理性のある時間で完了させるにはさらなるいくつかの変更が必要となります:

- 400GB+のRAMを搭載する8GPUのマシン
- 1つのトレーニングエポック(あるいはそれ以下)
- デバイスごとのバッチサイズは8(効果的なバッチサイズは8 x 8 = 64)
- パラメータのオフロードが有効化された完全なパラメータのパーティショニングを含む完全な["ZeRO stage 3" optimization](https://huggingface.co/docs/transformers/main_classes/deepspeed#zero3-example)

これは動作しますが、このデータセットと入力サイズ、エポックは完了に1.8*日*を要します。コストはエポックごとに数百ドルになります。これは間違いなくさらにチューニングできますが、予測される計算量の規模に対する感覚を掴むことができます。このサンプルの用途では、数百のステップ(1角エポックの1%)をファインチューニングすることで以下のような要約を実現します:
![Screenshot 2023-03-25 at 9.53.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0c2dc5a0-6d94-9fdc-d135-f85616767179.png)

定性的により良い要約になっています。この固有の問題において、時間とコストが見合っているとは言い難いですが、これは完全に実現可能なものです。ファインチューニングのコストと時間を許容できたとしても、推論のコストと時間はそうでないかもしれません。例えば、t5-11bによる推論は1GPU上で数十秒かかることがあり、これは遅すぎると言えます。多くの問題において、この規模やより小さいもので十分ですが、非常に大規模なチューニングも容易に活用することができます。

# まとめと次の方向性

大規模言語モデルは、さまざまなビジネス問題においてパワフルな新たなツールであり、オープンソースのものは、Databricks上でそのままで、容易に、オープンソースとともに活用することができます。これら大規模言語モデルのファインチューニングは、オープンソースのツールを活用することで同様にわかりやすいものとなります。手でツールを記述する必要はありません。スクリプトであっても、Databricksノートブックでは問題になりません。これらの容易なアプローチは、ほとんどすべての現実世界の問題に十分対応できるようにスケールアップします。

T5のさまざまなサイズのファインチューニングによるクイックな実験の結果と、ファインチューニングと推論で必要となるリソースの規模を以下に示します:
![Screenshot 2023-03-25 at 9.59.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9166622a-d73e-4173-43d0-18a7a23b4f68.png)

依然として、さらなる取り組みを必要とするケースは常に存在し、場合によっては最大のマシンが提供するよりも多くのリソースを必要とするかもしれません。さらなる取り組みによって、これらのツールはDatabricksのマシンクラスターに適合することが可能となりますが、これは今後の記事のトピックとなります。

これをDatabricksでお試しください！この[ノートブックアーカイブ](https://www.databricks.com/wp-content/uploads/notebooks/db-551/summarization.dbc)をリポジトリにインポートしてください。


### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

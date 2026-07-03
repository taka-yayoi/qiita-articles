---
title: 50歳ITエンジニアが語る「Apache Spark徹底入門」出版への道
tags:
  - Spark
  - ポエム
  - Databricks
private: false
updated_at: '2024-04-20T21:35:43+09:00'
id: b21cceae9caf03faf41c
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらのイベントなどでお話しした内容のサマリーです。

https://infra-eng-books.connpass.com/event/314425/

録画はこちらからご覧いただけます。
<iframe width="560" height="315" src="https://www.youtube.com/embed/XpsohzjuK_Q?si=yAMz3JI_4_nt8oUm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

# 自己紹介

Databricks JapanでアカウントSA部の部長をしている弥生 隆明と言います。年はちょうど50歳です。幸か不幸か(幸運だと思ってますが)、キャリアを通じてコーディングし続けてこれてます。

- 新卒は某重工業、たまたま社内システム部門に配属したのがITとの出会いです。当時はWindows 95、Windows NTが主流でした。
- ITが面白くなってきたので某製作所に転職。ここが一番キャリアが長いです。17年いました。自然言語処理(当時はn-gramや形態素解析、tf-idfとか使ってました)の研究や、コンシューマー向けWebサービスの開発・運用、インドに赴任してビッグデータのPoCの実行、日本に帰ってから人工知能製品のプレセールスに関わっていました。
- 45歳の時に思い立って、某コンサルファームに転職。データ分析を行っていましたが2年半で退職。その後、Databricksにジョインしました。
- 経験言語は、LISP、C、Objective-C、Visual Basic、ASP(Active Server Pages)、SQL、Perl、PHP、R、Pythonという感じです。

![Screenshot 2024-04-20 at 20.12.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4bfa20c3-ccd6-54e7-bfa0-7f2a3f25be37.png)

なお、私が最初にSparkに触ったのは3年前のDatabricksの入社試験です。

# Apache Spark徹底入門とは

2024/4/12にこちらの本を翔泳社から出版しました。生まれて初めての経験です。
<a href="https://www.amazon.co.jp/dp/4798182281/"><img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/87910d7c-8a63-c198-8e82-216ea7a8ee07.jpeg" width=300></a>

> 本書は、ビッグデータを主な対象としたデータ分析フレームワークであるApache Spark、MLflow、Delta Lakeの中級入門書です。「動かしてみる」だけではなく、どのような仕組みになっているのか、どうすれば効率的な実装が行えるかまで踏み込みつつ、データAIの実装者がApache Spark、MLflow およびDelta Lakeを使いこなすための解説を行います。

なお、同人誌としてこちらの本を書いたことはあります。
<a href="https://www.amazon.co.jp/dp/B09V1YXFVQ"><img src="https://m.media-amazon.com/images/I/61ra00HIf9L._SL1500_.jpg" width=200></a>

![Screenshot 2024-04-20 at 20.13.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/df6bdabe-70ca-3141-1c05-8594fc37fac2.png)

## Learning Spark 2nd Editionとは

2020/8にオライリーから出版された書籍です。

> 改訂版ではSpark 3.0を含めており、2nd Editionでは、データエンジニアとデータサイエンティストにとってSparkにおける構造化と統合が意味を持つのかを説明します。特に、本書ではシンプルなデータ分析、複雑なデータ分析や
機械学習アルゴリズムの適用をどのように行うのかを説明しています。

![Screenshot 2024-04-20 at 20.15.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bd81d70a-9183-a47b-4565-7fde4e70505c.png)

私もDatabricks入社後に原著を読みました。今でも頻繁に使うSparkデータフレームの説明が充実しており、非常に勉強になりました。

## Learning Spark 1st Editionとは

2nd Editionということは1st Editionもあります。ただ、こちらは[RDD(Resilient Distributed Datasets)](https://spark.apache.org/docs/latest/rdd-programming-guide.html)主体ということもあって、なかなか難解でした。しかし、1st Editionあっての2nd Editionです。そして、その著者の一人がDatabricks CTOのMatei Zahariaです。
![Screenshot 2024-04-20 at 20.47.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d7b068c5-e40c-6382-24bc-c279534ea3f9.png)

なぜ、こういう話をしているかというと、出版前の4月上旬にMateiが日本を訪れており、その際に本にサインをもらい、一緒に撮ってもらったのです！別に意図したわけではないですが、出版直前に原著者が日本を訪れるというタイミングに驚愕した次第です。
![Screenshot 2024-04-20 at 20.48.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8885575c-4698-bedd-b052-07f08edfec94.png)

これは本当、好きなソフトウェア(Spark)の本を翻訳して、そのソフトウェアのオリジナルクリエーターにサインをもらって、写真も一緒に撮ってもらうという、ソフトウェアエンジニアとしては相当の名誉というか、残り一生の運を使い果たしてしまったような。

# 出版前のテンション

書籍には先行販売なるものがあるのを知ったのもこのタイミングです。4/12前にどこそこの書店で先行販売されているという情報をつかみ、そそくさと写真を撮りにいきました。そして、その後の出版後も最寄りの書店で本があるのを見て小躍りしてました。
![Screenshot 2024-04-20 at 20.53.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/934a390c-1bb5-3e59-7638-2fa419b2f895.png)

# 出版の経緯

こういった記事を書いたり、イベントでお話ししていますが、私は発起人ではありません。Databricks Japanの同僚の方が約2年前に、**Learning Spark 2nd Editonは今でも通用する内容だから翻訳しない？** と働きかけたのがスタートです。私は原著を読んで**非常にわかりやすいな**と思っていたことに加え、Databricksのお客様と相対している中で**Sparkが難しくてね**という話をそれなりの頻度で聞いており、どうにかしたいなと思っていたこともあって、すぐにその取り組みに参画しました。あとは単純に**出版社から本出したい**という願望がありました。
![Screenshot 2024-04-20 at 20.56.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/22fe9b54-033e-8cfb-0a25-9b8cbd5db626.png)

その後、発起人の方が原著者や出版社との調整を進める中、日本語版のオリジナルコンテンツを選定し、本格的な執筆は一年前からスタートしました。DatabricksとAPコミュニケーションズ様の有志のエンジニアが集いました。1stバージョンは生成AIを使って作成しました。しかし、技術書においては、本全体での用語や文体の一貫性が重要ですが、これがなかなか難しく、結局のところほぼ全てに対して目視によるチェックが必要でした。

各章を分担して、ほぼ全てを手直しして初稿が出来上がったのは2023年11月です。それ以降は発起人と私で校閲しました。校閲も初めての体験なので試行錯誤ながらでしたので、夜鍋や週末溶かしが常態化してました。ただ、2月にカッコいい表紙が出来上がってテンション上がったのは覚えています。結果として3月25日に校了しました。
![Screenshot 2024-04-20 at 20.58.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/40feee5d-ff3d-959f-570b-e2500b10a287.png)

# ハイライト

以下のような内容をカバーしています。

- Apache Sparkとは何か？
    - Python、SQL、Scala、またはJavaの高レベルの構造化APIの学習
    - Sparkの操作とSQLエンジンの理解
    - Spark構成とSpark UIを使用したSpark操作の検査、調整、デバッグ
    - JSON、Parquet、CSV、Avro、ORC、Hive、S3、またはKafkaといったデータソースへの接続
    - 構造化ストリーミングを使用したバッチデータとストリーミングデータの分析の実施

- Delta Lake
    - オープンソースのDelta LakeとSparkを使用した信頼性の高いデータパイプラインの構築

- MLlib / MLflow
    - MLlibを使用する機械学習パイプラインの開発、MLflowを使用するモデルの管理、本番化

- オリジナルコンテンツ
    - pandasデータフレーム、sparkデータフレームに関する各種データフレームの使い分け
    - LLMやEnglish SDK for SparkなどAIを活用した新たなコーディングスタイル、LLMの実践

## 章立て

私自身は主に第3章から第6章とオリジナルコンテンツの一部を担当しました。

- 第1章: Apache Spark入門
- 第2章: Apache Sparkのダウンロードと入門
- 第3章: Apache Sparkの構造化API
- 第4章: Spark SQLとDataFrame: 組み込みデータソースの紹介
- 第5章: Spark SQLとDataFrame: 外部データソースとのインタラクション
- 第6章: Spark SQLと Dataset
- 第7章: Sparkアプリケーションの最適化およびチューニング
- 第8章: 構造化Streaming
- 第9章: Apache Sparkを用いた信頼性の高いデータレイクの構築
- 第10章: MLlibによる機械学習
- 第11章: Apache Sparkによる機械学習パイプラインの管理、デプロイおよびスケール
- 第12章: エピローグ：Apache Spark 3.x

## 前半部分のハイライト

Apache Sparkとは何か、なぜ誕生したのか、Apache Sparkのインストール、基本概念などを説明しています。

**第1章: Apache Spark入門**

- なぜApache Sparkが誕生したのか
- Apache Sparkの特徴、構成要素

**2章: Apache Sparkのダウンロードと入門**

- Apache Sparkのダウンロードとインストール
- Apache Sparkの基本概念(SparkSession、Driver、Executor、Job、Stage、Task、Transformation、Actionなど)

**第3章 - 第6章**
- 非常にボリュームのある章となっています。
- Sparkの構造化API: DataFrame、DatasetやSpark SQLにフォーカスして、基本的な考え方から様々なデータソースとの連携方法のような実践をコードを通じて学びます。

## コードコメントも翻訳してます

[補足記事](https://qiita.com/taka_yayoi/items/798767c8a585c64212f9)書きました。

![Screenshot 2024-04-20 at 21.06.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2e625d7f-6975-6ab3-f8ed-a0397cb84b62.png)

## オリジナルコンテンツ

私は[English SDK for Apache Spark](https://qiita.com/taka_yayoi/items/098e5d72dde79a3f07a6)の記事を書きました。

![Screenshot 2024-04-20 at 21.07.38.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/57b1f09f-ae28-cf0b-b83c-50b777eb42ca.png)

# 苦労したポイント

校閲は第3校までいきました。最初はコメント数が収束せず**本当に終わるのかこれ？** ってなってました。ちなみに、Boxで共有されたPDFにコメントしていく形だったので非常に楽でした。ビバ、デジタル世界。
![Screenshot 2024-04-20 at 21.09.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/583cdb97-686f-3604-8b63-0cb0d1c57cc2.png)

最後の方は校閲のために休み取るという訳のわからないことに。
![Screenshot 2024-04-20 at 21.10.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cd604fec-e988-d5e7-c29a-508ac024616f.png)

繰り返しになりますが、初の翻訳作業ということもあり、試行錯誤の日々でした。

**初回翻訳では生成AI(LLM)の力を借りましたが...**
- 翻訳結果の確認は人手で行う必要があるので、ひたすらアウトプットを確認しました。
- propertyが「不動産」だったりしてました。

**どこまで翻訳するのか問題**
- Driver、Worker、Executor、DataFrameのようにSpark固有の用語は原文のままとしました
Structured Streamingは構造化Streamingとしました。

**長音入れるのか問題**
- 宗教問題になりそうですが、クエリ、パラメータなどに統一しています。

# まとめ

兎にも角にも初めての体験ばかりでしたが、発起人や他の執筆者、そして、翔泳社の皆様のサポートをいただきつつ、ここまでやり切ることができました！原書のコンテンツ自体が優れていること、翻訳にはできる限りの労力を注ぎ込み、自然な日本語になるようにしています。

並列分散処理エンジンであるApache Sparkは、使いこなすことでデータ処理だけではなく、機械学習モデルのトレーニングなど幅広い領域で活用できるものでありながらも、日本語リソースが少なかったことからあまり活用が進んでいないことにDatabricks入社以来、悶々としていたのは事実です。この本自体、先人の知恵を継承しているものですが、これが日本のITエンジニアの皆様の助けになれば、これ以上の喜びはありません。

<a href="https://www.amazon.co.jp/dp/4798182281/"><img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ff57d3a2-a52f-d733-2302-bc0cb6668c60.png"></a>

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

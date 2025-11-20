---
title: Apache Spark 2.3における構造化ストリーミングの低レーテンシー連続処理モードのご紹介
tags:
  - Spark
  - Databricks
private: false
updated_at: '2022-06-20T08:14:42+09:00'
id: 42a00e9f2fe96affd6de
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Introducing Low\-latency Continuous Processing Mode in Structured Streaming in Apache Spark 2\.3 \- The Databricks Blog](https://databricks.com/blog/2018/03/20/low-latency-continuous-processing-mode-in-structured-streaming-in-apache-spark-2-3-0.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**注意**
2018年の記事です。
:::

# Databricksランタイム4.0で利用できます

[Databrikcsでノートブックをインポート](https://github.com/databricks/benchmarks/tree/master/streaming/structured-streaming-continuous-processing)

いくつかの理由から、[Apache Spark 2.0](https://databricks.com/blog/2016/07/26/introducing-apache-spark-2-0.html)で[構造化ストリーミング](https://databricks.com/blog/2016/07/28/structured-streaming-in-apache-spark.html)は自身の高レベルAPIからマイクロバッチ処理を分離しました。第一に、APIによるエクスペリエンスをよりシンプルなものにしました。APIはマイクロバッチを考慮する必要がありませんでした。第二に、開発者はストリームを無限のテーブルとして取り扱い、静的なテーブルを操作するのと同様にクエリーを発行することができました。

このメリットを活用するために、Databricks[レイクハウスプラットフォーム](https://databricks.com/product/data-lakehouse)の一部として利用できる[Databricks Runtime 4\.0](https://docs.databricks.com/release-notes/runtime/4.0.html)の[Apache Spark 2\.3](https://databricks.com/blog/2018/02/28/introducing-apache-spark-2-3.html)で**連続モード**と呼ばれる新たな**ミリ秒レベルの低レーテンシー**モードのストリーミングに取り組みました。
![](https://databricks.com/wp-content/uploads/2018/03/image3-1.png)

この記事では、連続処理モードの使用法、メリット、ミリ秒の低レーテンシー要件を持つ連続ストリーミングアプリケーションの記述するために、開発者がどのように活用するのかを説明します。動機づけとなるようなシナリオからスタートしましょう。

# 低レーテンシーのシナリオ

不正のあるクレジットカードトランザクションを特定するためにリアルタイムパイプラインを構築したいものとします。理想的には、容疑者がクレジットカードをスワイプしたらすぐに、不正なトランザクションを特定し、拒否したいと考えます。しかし、お客様を怒らせることになるので、適切なトランザクションを遅延させたくはありません。これは、我々のパイプラインのエンドツーエンドのレーテンシーに対して厳密な上限値を設定することになります。取引には他の遅延要素もあるため、パイプラインはそれぞれのトランザクションを10-20msで処理しなくてはなりません。

[構造化ストリーミング](https://databricks.com/jp/glossary/what-is-structured-streaming)でこのパイプラインを構築してみましょう。不正なトランザクションを特定することができるユーザー定義関数`isPaymentFlagged`があるものとします。レーテンシーを最小化するために、遅延のないように可能な限り高速にそれぞれのマイクロバッチをスタートさせるようにSparkに指示する0秒の処理時間トリガーを使用します。ハイレベルでは、クエリーは以下のようなものになります。

```py:Python
payments \
  .filter("isPaymentFlagged(paymentId)") \
  .writeStream \
   {...}
  .trigger(processingTime = "0 seconds") \
  .start()
```

このサンプルノートブックをダウンロードし、ご自身のDatabricksワークスペース([Databricksコミュニティエディション](https://qiita.com/taka_yayoi/items/fb4f57c069e1f272e88a#%E3%82%B3%E3%83%9F%E3%83%A5%E3%83%8B%E3%83%86%E3%82%A3%E3%82%A8%E3%83%87%E3%82%A3%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%B8%E3%81%AE%E3%82%B5%E3%82%A4%E3%83%B3%E3%82%A2%E3%83%83%E3%83%97)を使うこともできます)にインポートすることで完全なコードを参照することができます。エンドツーエンドのレーテンシーがどのようになるのかを見てみましょう。
![](https://databricks.com/wp-content/uploads/2018/03/image6-1.png)

レコードはSparkを通じて100ms以上かかって流れています！多くのストリーミングパイプラインではこれは問題ありませんが、このユースケースでは不十分です。連続処理モード(Continuous Processing mode)は助けになるのでしょうか？

```py:Python
payments \
  .filter("isPaymentFlagged(paymentId)") \
  .writeStream \
   {...}
  .trigger(continuous = "5 seconds") \
  .start
```

これで、1ms以下のレーテンシーとなり、2桁もの改善を成し遂げターゲットのレーテンシーを下回りました！マイクロバッチ処理のレーテンシーがこれほど高く、連続処理が助けになったのかを理解するために、構造化ストリーミングエンジンの詳細を見ていく必要があります。

# マイクロバッチ処理

構造化ストリーミングはデフォルトでマイクロバッチ実行モデルを採用します。これは、[Sparkストリーミング](https://databricks.com/glossary/what-is-spark-streaming)エンジンは定期的にストリーミングのソースをチェックし、最後のバッチが終了した後に新たに到着したデータに対してバッチクエリーを実行することを意味します。ハイレベルでは以下のようになります。
![](https://databricks.com/wp-content/uploads/2018/03/image7-1.png)

このアーキテクチャでは、クエリーを再起動するために使われることがある先行書き込みログにレコードのオフセットを保存することで、ドライバーが進捗のチェックポイントを作成します。決定論的再実行とエンドツーエンドのセマンティクスを得るために、マイクロバッチがスタートする*前に*、次マイクロバッチで処理されるレンジオフセットがログに保存されることに注意してください。このため、ソースで利用可能なレコードはオフセットが記録される前に現在のマイクロバッチの完了と次のマイクロバッチが処理をするのを待つ場合があります。レコードレベルでは、タイムラインは以下のようになります。
![](https://databricks.com/wp-content/uploads/2018/03/image1-2.png)

結果として、ソースでイベントが利用できるようになる時刻と、シンクに出力が書き込まれるまでの間には、ベストでも100ミリ秒のレーテンシーが発生することになります。

当初我々は、パフォーマンスがすでに最適化されたSpark SQLにおける既存のバッチ処理エンジンを容易に活用できるように、このマイクロバッチエンジンで構造化ストリーミングを開発しました([コードジェネレーション](https://databricks.com/blog/2016/05/23/apache-spark-as-a-compiler-joining-a-billion-rows-per-second-on-a-laptop.html)や[プロジェクトTungsten](https://databricks.com/blog/2016/05/23/apache-spark-as-a-compiler-joining-a-billion-rows-per-second-on-a-laptop.html)に関する過去の記事をご覧ください)。これによって、100msというレーテンシーで[高いスループット](https://databricks.com/blog/2017/10/11/benchmarking-structured-streaming-on-databricks-runtime-against-state-of-the-art-streaming-systems.html)を実現することができました。過去数年を通じて、数千の開発者と共に数百の異なるユースケースに取り組むことで、ETLやリアルタイムモニタリングのような多くの実践的なワークロードにおいては秒レベルのレーテンシーは十分なものであることを知りました。しかし、いくつかのワークロードにおいては、さらに低いレーテンシーによって利益を享受することができ、そして、これが連続処理モードの開発のモチベーションとなりました。この動作原理を見ていきましょう。

# 連続処理

連続処理モードでは、定期的なタスクを起動するのではなく、Sparkは連続的にデータの読み込み、処理、書き込みを行う長時間稼働する一連のタスクを起動します。ハイレベルでは、環境とレコードレベルのタイムラインは以下のようになります(上のマイクロバッチ実行の図と対比してみてください)。
![](https://databricks.com/wp-content/uploads/2018/03/image2-2.png)
![](https://databricks.com/wp-content/uploads/2018/03/image4-2.png)

ソースでイベントが利用できるようになるとすぐに処理されシンクに書き込まれるので、エンドツーエンドのレーテンシーは数ミリ秒となります。

さらにクエリーの進捗は、よく知られる[Chandy\-Lamportアルゴリズム](https://en.wikipedia.org/wiki/Chandy-Lamport_algorithm)のを用いてチェックポイントが作成されます。すべてのタスクの入力データストリームに特殊なマーカーレコードが挿入されます。我々はこれらを「エポックマーカー(epoch marker)」と呼び、これらの間のギャップを「エポック」と呼びます。マーカーがタスクに遭遇すると、タスクは最後に処理されたオフセットを非同期的にドライバーに報告します。ドライバーがシンクに書き込むすべてのタスクからオフセットを受け取ると、上述した先行書き込みログに書き込みます。チェックポイント作成は完全に非同期処理となるので、タスクは邪魔されずに処理を継続でき、一貫性のあるミリ秒レベルのレーテンシーを提供することができます。

# Apache Spark 2.3.0での実験的リリース

Apache Spark 2.3.0で、この連続処理モードは実験的機能となっており、構造化ストリーミングソースのサブセットとデータフレーム/データセット/SQLオペレーションがこのモードでサポートされています。特に、以下の条件を満たすクエリーでオプションとして連続トリガーを設定することができます。

- Kafkaのようにサポートされているソースからの読み込み、Kafka、メモリー、コンソールのようなサポートされているシンクへの書き込み(メモリーやコンソールはデバッグに適しています)。
- mapのようなオペレーション(例: select、where、map、flatMap、filterのような選択、プロジェクション)のみを含む。
- 集計関数、`current_timestamp()`や`current_date()`のような現在時刻ベースの関数以外のSQL関数を含む。

詳細に関しては以下を参照ください。

- 現在の実装と制限の詳細については、[Structured Streaming programming guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#continuous-processing)
- ミリ秒レーテンシーでのモデル予測をデモする[Spark Summit Keynote Demo](https://www.youtube.com/watch?v=xwQwKW-cerE&feature=youtu.be)

# まとめ

Apache Spark 2.3のリリースによって、開発者はレーテンシーの要件に応じて連続モード、マイクロバッチモードのいずれかのストリーミングモードを選択できるようになりました。デフォルトの構造化ストリーミングモード(マイクロバッチ)は多くのリアルタイムストリーミングアプリケーションで許容できるレーテンシーを提供しますが、***ミリ秒規模のレーテンシー***要件がある場合には、この連続モードを選択することができます。

Databricksでこの[Continuous Processing mode notebook](https://github.com/databricks/benchmarks/tree/master/streaming/structured-streaming-continuous-processing)をインポートして確認してみてください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

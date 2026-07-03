---
title: Delta Live Tablesの強化オートスケーリングによる高信頼かつコスト効率の高いストリーミングデータパイプラインの構築
tags:
  - Databricks
  - DeltaLiveTables
private: false
updated_at: '2023-01-24T15:12:44+09:00'
id: 40bb7a06d3c1dcbe89fa
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Build Reliable and Cost Effective Streaming Data Pipelines With Delta Live Tables’ Enhanced Autoscaling \- The Databricks Blog](https://www.databricks.com/blog/2022/12/08/build-reliable-and-cost-effective-streaming-data-pipelines.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

我々は、信頼性のあるデータパイプラインの構築にシンプルかつ宣言型のアプローチを用いる市場初のETLフレームワークである、[Delta Live Tables \(DLT\)](https://www.databricks.com/jp/product/delta-live-tables)の正式提供を今年発表しました。[ローンチ](https://www.databricks.com/company/newsroom/press-releases/databricks-announces-general-availability-of-delta-live-tables)以来、[Databricksは新機能でDLTを拡張し続けてきています](https://qiita.com/taka_yayoi/items/7dcd8730fbb097952caa)。本日、[Delta Live Tables \(DLT\)](https://www.databricks.com/jp/product/delta-live-tables)の強化オートスケーリングの正式提供を発表できることを嬉しく思っています。アナリストやデータエンジニアは、プロダクションで利用できる[ストリーミング](https://www.databricks.com/jp/product/data-streaming)データパイプラインやバッチデータパイプラインをクイックに作成するためにDLTを活用することができます。SQLあるいはPythonを用いてデータに対して実行する変換処理を定義するだけでよく、DLTはパイプラインの依存関係を理解し、計算資源管理、モニタリング、データ品質、エラーハンドリングを自動化します。

DLTの強化オートスケーリングは、スパイクがあり予測不可能なストリーミングワークロードを取り扱うために設計されています。あなたのデータパイプラインが一貫性のあるSLAを維持するために必要なリソースを保証しつつも、コストを削減するためにストリーミングワークロードにおけるクラスターの利用率を最適化します。これによって、ビジネスサイドが最新データにアクセスでき、コストが最適化されていることに自信を持って、データを操作することにフォーカスできるようになります。スタートアップから[Nasdaq](https://www.youtube.com/watch?v=DXgtNmj5mdE)や[Shell](https://www.databricks.com/jp/customers/shell)のようなエンタープライズに至る多くのお客様がすでにプロダクション環境で強化オートスケーリングを活用しています。DLTの強化オートスケーリングは、賞を受賞するようなグローバル移民法律事務所である[Berry Appleman & Leiden LLP](https://www.bal.com/)(BAL)のようなお客様におけるプロダクションユースケースを支援しています。

> 「DLTの強化オートスケーリングによって、BALのような法律事務所はレーテンシー要件を満たしつつもストリーミングデータパイプラインを最適化することができるようになりました。これまでより4倍高速にクライアントにレポートをデリバリーしており、彼らの移民プログラムに関してより多くの情報に基づく意思決定をできるようになりました。」— Chanille Juneau, Chief Technology Officer, BAL
> ![](https://cms.databricks.com/sites/default/files/inline-images/db-338-blog-img-6_0.png)

# データのストリーミングはミッションクリティカルです

膨大な新規データに対してよりクイックに意思決定を行うため、ストリーミングワークロードの人気はこれまで以上に高まっています。リアルタイムの処理によって、企業の分析や機械学習モデルに可能な限り最新のデータを提供することで、より迅速かつ優れた意思決定、より正確な予測を実現し、改善された顧客体験などを提供できるようになります。多くのDatabricksユーザーは、低レーテンシー、耐障害性、インクリメンタル処理のサポートを活用するために、[レイクハウス](https://www.databricks.com/jp/product/data-lakehouse)でストリーミングを導入しています。オープンソースのApache SparkユーザーとDatabricksユーザーの両方でストリーミングが[多数導入](https://www.databricks.com/blog/2022/06/28/project-lightspeed-faster-and-simpler-stream-processing-with-apache-spark.html)されている様子を確認しています。以下のグラフでは、過去3年間におけるDatabricks上のストリーミングジョブの週あたりの数を示しており、数千から数百万に成長し、いまだに加速しています。
![](https://cms.databricks.com/sites/default/files/inline-images/db-338-blog-img-2.png)
*図: Databricksで実行されるストリーミングジョブの数*

時間とともにデータボリュームが変動するワークロードは数多く存在します: クリックストリームのイベント、eコマースのトランザクション、サービスログなどです。同時に、我々のお客様は、より予測可能なレーテンシー、データの可用性と新鮮さに関する保証をリクエストしています。

一貫性のあるSLAを保持しつつストリーミングデータを取り扱えるように、インフラストラクチャをスケーリングさせることは通常は困難であり、従来型のバッチ処理よりとは異なり、より複雑な要件が存在しています。この問題を解決するために、データチームは多くの場合ピークロードに合わせてインフラストラクチャのサイジングを行い、結果として低い利用率と高価なコストとなります。主導によるインフラストラクチャの管理は、オペレーション上複雑で時間を浪費するものです。

計算需要の変化に対応するために計算資源をスケールする問題を解決するために、Databricksでは2018年に[クラスターのオートスケーリング](https://www.databricks.com/blog/2018/05/02/introducing-databricks-optimized-auto-scaling.html)を導入しました。クラスターのオートスケーリングは、コストが高くつくダウンタイムを回避するために、ワークロードに必要なキャパシティを保証しつつもお客様の費用を節約しました。しかし、クラスターのオートスケーリングは、比較的計算リソースの需要がわかっており、ワークフローの途中での変動がないバッチ指向の処理向けに設計されたものです。DLTの強化オートスケーリングは、ストリーミングパイプラインで生じる予測できないデータフローに特に対応するために開発され、ストリーミングワークロードにおいて一貫性のあるSLAを保証することで、お客様の費用を節約し、オペレーションをシンプルにします。

# DLTの強化オートスケーリングはストリーミングとバッチのワークロードをインテリジェントにスケールします

オートスケーリングを持つDLTは、小売、金融サービス、鉄鋼を含むすべての業界における数多くのユースケースに対応します。この例では、サイバーセキュリティイベントを分析するユースケースをピックアップします。それでは、Delta Live Tablesの強化オートスケーリングがどのように低コストで最新のデータをデリバリーしつつも、手動によるインフラストラクチャの管理の必要性を排除したのかを見ていきましょう。一般的な実世界におけるサンプルで説明します: Delta Live Tablesを用いたサイバーセキュリティイベントの検知です。

サイバーセキュリティのワークロードは、本質的にスパイクを伴います。ユーザーは朝にコンピュータにログインし、ランチのために離席し、より多くのユーザーが別のタイムゾーンで起床し、このサイクルが繰り返されます。セキュリティチームは、コストを制御下に置きつつも、ビジネスを防御するために可能な限り迅速にイベントを処理する必要があります。

このデモでは、人気のオープンソースネットワーク監視ツールであるZeekによって生成される接続ログを取り込み、処理します。
![](https://cms.databricks.com/sites/default/files/inline-images/db-338-blog-img-3.png)
*図: ランディングゾーンに書き込まれる行数*

Delta Live Tablesのパイプラインは標準的な[メダリオンアーキテクチャ](https://www.databricks.com/jp/glossary/medallion-architecture)に従います。[Databricks Auto Loader](https://qiita.com/taka_yayoi/items/df143647dcf5942b51c6)を用いてブロンズレイヤーにJSONデータを取り込み、データ型を調整し、カラム名を変更し、不正データを取り扱うために[データエクスペクテーション](https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-expectations.html)を適用することでクレンジングしたデータをシルバーレイヤーに移動します。完全なストリーミングパイプラインは以下のようになりますが、これは[数行のコード](https://www.databricks.com/wp-content/uploads/notebooks/dlt-enhanced-autoscaling.dbc)で作成されます。
![](https://cms.databricks.com/sites/default/files/inline-images/db-338-blog-img-4.png)
*図: サイバーセキュリティDLTパイプラインのサンプル*

分析のために、Deltaテーブルで利用できるDLT[イベントログ](https://qiita.com/taka_yayoi/items/5ae5824cfab30caf9795)からの情報を活用します。

以下のグラフは、データボリュームによって強化オートスケーリングが設定されたクラスターがどのように増強され、データボリュームが減少した際にクラスターサイズが減少し、バックログが処理されるのかを示しています。
![](https://cms.databricks.com/sites/default/files/inline-images/db-338-blog-img-5.png)
*図: 強化オートスケーリングを用いたDLTパイプラインによって使用されるエグゼキューターの数*

グラフからわかるように、クラスターのサイズを自動で増減される能力によってリソースが劇的に節約されます。

Delta Live Tablesは、オートスケーリングとクラスターイベントを含むデータパイプラインに関する有用なメトリクスを収集します。クラスターリソースのイベントは、現在のエグゼキューターやタスクスロットの数、タスクスロットの利用率、キューされたタスクの数に関する[情報を提供](https://qiita.com/taka_yayoi/items/5ae5824cfab30caf9795)します。強化オートスケーリングは、与えられたワークロードに対する最適なエグゼキューター(クラスター)の数を計算するために、リアルタイムでこのデータを活用します。例えば、以下のグラフではタスク数の増加は起動されるクラスターの数の増加につながり、タスクの数が減少するとコストを最適下するためにクラスターも削除されています。
![](https://cms.databricks.com/sites/default/files/inline-images/db-338-blog-img-6.png)
*図: 現在のエグゼキューター数 vs 予測最適数、キューされたタスクの平均数*

# まとめ

変化し続け、予測不可能なデータボリュームによって、ベストなパフォーマンスを得るために手動でクラスターをサイジングすることは困難であり、過度にプロビジョンするリスクを伴います。DLTの強化オートスケーリングは、コストを削減するために全体的なエンドツーエンドのレーテンシーを削減しつつも、クラスターの利用率を最大化します。

本書では、DLTの強化オートスケーリングがどのようにして、現在と予測されるデータロードに基づき、計算リソースの最適量を選択することで、ストリーミングワークロードの要件を満たすためにスケールアップするのかをデモンストレーションしました。また、費用を削減するために、どのように強化オートスケーリングがクラスターのリソースを停止することでスケールダウンするのかもデモンストレーションしました。

# Databricksレイクハウスプラットフォームで強化オートスケーリングとDelta Live Tablesを使い始める

強化オートスケーリングは、DLTユーザーインタフェースで作成される新規パイプラインでは自動で有効化されています。DLT UIの[Settings button](https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-ui.html#edit-settings)をクリックすることで既存のDLTパイプラインで強化オートスケーリングを有効化することをお勧めします。REST APIを通じて作成されたDLTパイプラインでは、強化オートスケーリングを有効化する設定を含める必要があります([ドキュメント](https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-concepts.html#databricks-enhanced-autoscaling)をご覧ください)。設定でオートスケーリングモードが設定されていないDLTパイプラインにおいては、強化オートスケーリングをデフォルトにする変更を徐々にロールアウトしていきます。

データエンジニアやアナリストがどれだけ容易にDLTを活用できるのかを知るために以下のデモをご覧ください。
<iframe width="560" height="315" src="https://www.youtube.com/embed/BIxwoO65ylY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>


すでにDatabricksを使われているのであれば、シンプルに[スタートガイド](https://qiita.com/taka_yayoi/items/0cde1f2732ff859a726f)に従ってください。そうでない場合には、[Databricks無料トライアル](https://databricks.com/jp/try-databricks)にサインアップいただき、DLTの詳細な価格を[こちら](https://www.databricks.com/jp/product/pricing)から確認してください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Data & AI Summit 2022におけるDatabricksレイクハウスプラットフォーム発表の振り返り
tags:
  - Databricks
  - DAIS2022
private: false
updated_at: '2022-07-27T15:09:12+09:00'
id: b7fb5d5abc6cdbb7b6d2
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Recap of Databricks Lakehouse Platform Announcements at Data and AI Summit 2022 \- The Databricks Blog](https://databricks.com/blog/2022/07/25/recap-of-databricks-lakehouse-platform-announcements-at-data-and-ai-summit-2022.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

世界にとってデータチームほど重要なものはありません。過去数年を通じて、多くのお客様がレイクハウスを用いて全ての業界を変革する新世代のデータ&AIアプリケーションを構築するのを目撃してきました。

[Databricks](https://databricks.com/jp)によって導入されたデータレイクハウスのパラダイムは、クラウドにまたがる単一かつオープンなデータプラットフォームにおいて、アナリティクス、データエンジニアリング、機械学習、ストリーミングワークロードを統合するソリューションを構築するためにモダンなデータチームが探し求めていた未来です。

世界中のエンタープライズ、スタートアップを含む我々のお客様の多くはDatabricksを愛し、信頼しています。実際、Fortune 500の半分はレイクハウスがインパクトを生み出していると認めています。[John Deere](https://youtu.be/uMQPkvuGaO0)、[Amgen](https://databricks.com/blog/2022/03/22/amgen-modernizes-analytics-with-a-unified-data-lakehouse-to-speed-drug-development-delivery.html)、[AT&T](https://databricks.com/blog/2022/04/11/data-att-modernization-lakehouse.html)、[Northwestern Mutual](https://databricks.com/blog/2021/07/15/driving-transformation-at-northwestern-mutual-with-scalable-open-lakehouse-platform.html)、[Walgreens](https://youtu.be/L4XQ7ioIzc0)のような企業は、構造化データ、非構造化データの両方に対するアナリティクスや機械学習を提供する能力のためにレイクハウスに移行しています。

先月、我々は年次の[Data \+ AI Summit](https://databricks.com/jp/dataaisummit/)で多くの方々に[Databricks Lakehouse Platform](https://databricks.com/jp/product/data-lakehouse)におけるイノベーションを公開しました。カンファレンスを通じて、有名なデータ&AIのオープンソースプロジェクトにおけるいくつかの貢献と、ワークロードに対する新機能を発表しました。

# Delta Lakeの全てをオープンソース化

[Delta Lake](https://delta.io/)は、最速かつ最も最先端のマルチエンジンストレージフォーマットです。提供される信頼性と最速のパフォーマンスによって、信じられないほどの成功と導入を目撃しています。現在、Delta Lakeは月間700万以上のダウンロードによって世界で最も広く利用されているストレージレイヤーとなっています。これは1年前と比較して10倍の月間ダウンロード数となっています。

Databricksでは、Delta Lakeの全ての機能とエンハンスメントを[Linux Foundation](https://linuxfoundation.org/featured/delta-lake-project-announces-availability-2-0-release-candidate/)に寄贈し、**Delta Lake 2.0**のリリースの一部として[全てのDelta Lake APIをオープンソース化](https://databricks.com/blog/2022/06/30/open-sourcing-all-of-delta-lake.html)することを発表しました。

Delta Lake 2.0によって、すべてのDelta Lakeユーザーに対して比類なきクエリー性能を提供し、誰でもオープンスタンダードを用いて高性能なデータレイクハウスを構築できるようになります。この貢献によって、Databricksのお客様とオープンソースコミュニティはDelta Lake 2.0の完全な機能と強化されたパフォーマンスのメリットを享受することができるようになります。Delta Lake 2.0リリースキャンディデートは利用可能であり、今年後半には完全にリリースされる見込みです。Delta Lakeの広範なエコシステムにによって、Delta Lakeはさまざまなユースケースにおいて柔軟かつ強力なものとなります。

# あらゆるデバイスからアクセスできるSpark、そして次世代ストリーミングエンジン

大規模データ分析における最先端の統合エンジンとして、Sparkはいかなるサイズのデータセットも取り扱えるようにシームレスにスケールします。しかし、リモート接続性の欠如、そして、アプリケーションを開発しドライバーノードで実行するための工数がモダンなデータアプリケーションの要求の妨げとなっていました。これに対応するためにDatabricksでは、より優れた安定性とビルトインのリモート接続性を提供するために、クライアントとサーバーを分離するデータフレームAPIに基づくApache Spark™のクライアント・サーバーインタフェースである[Spark Connect](https://qiita.com/taka_yayoi/items/ba26ba320d828a8e4d61)を導入しました。

レイクハウスにおけるデータストリーミングは、Databricksレイクハウスプラットフォームにおいて急速に成長しているワークロードであり、全てのデータ処理の未来とも言えるものです。また、Sparkコミュニティとのコラボレーションにおいて、Dataricksはレイクハウスにおけるデータストリーミングの次世代Spark構造化ストリーミングエンジンである[Project Lightspeed](https://databricks.com/blog/2022/06/28/project-lightspeed-faster-and-simpler-stream-processing-with-apache-spark.html)を発表しました。

# データガバナンス、セキュリティ、コンプライアンス機能の拡張

ガバナンス、セキュリティ、コンプライアンスは全てのデータ資産が維持され、企業全体におけるセキュリティが管理され、規制フレームワークに準拠していることを保証する役立つので、企業にとって非常に重要なものです。Databricksでは、データガバナンス、セキュリティ、コンプライアンスの機能をさらに拡張する幾つのかの新機能を発表しました。

- [向こう数週間でAWSとAzureでUnity CatalogがGA](https://qiita.com/taka_yayoi/items/bbbc2da4ce0a88e35060)となり、[Unity Catalog](https://databricks.com/jp/product/unity-catalog)はビルトインの検索機能、全てのワークロードにおいて自動化されたリネージュ、任意のクラウド上におけるスケーラビリティを用いて、すべてのデータ、AI資産に対する集中管理されたガバナンスソリューションを提供します。
- また、Databricksでは先月前半にレイクハウスのデータガバナンス機能を拡張し、全体のデータライフサイクルにおける完全なビューをデータチームに提供するUnity Catalogの[データリネージュ](https://databricks.com/company/newsroom/press-releases/databricks-introduces-data-lineage-for-unity-catalog)を発表しました。データリネージュを用いることで、お客様は使っているレイクハウスにおいてデータがどこからやってきたのか、いつ誰が作成したのか、時間が経過する中でどのように変更がされたのか、データウェアハウスやデータサイエンスワークロードでどのように使用されているのか等に関する可視性を手に入れることができます。
- Payment Card Industry Data Security Standard (PCI-DSS)やHealth Insurance Portability and Accountability Act (HIPAA)に準拠しなくてはならない、規制が厳しい業界のお客様のためにDatabricksは機能を拡張しました。Databricksは[AWSのE2アーキテクチャデプロイメントにおけるHIPAAとPCI\-DSSコンプライアンス機能](https://databricks.com/blog/2022/06/22/databricks-now-provides-hipaa-compliance-features-on-google-cloud.html)を拡張し、[Google CloudにおけるHIPAAコンプライアンス機能](https://databricks.com/blog/2022/06/22/databricks-now-provides-hipaa-compliance-features-on-google-cloud.html)を提供します。(両方パブリックプレビューです)

# 安全かつオープンなデータ共有によるベンダーロックインなしに新たな価値を創出

企業は容易かつ安全に顧客、パートナー、サプライヤー、内部LOBとデータを交換することでコラボレーションを促進し、データから価値を生み出したいと考えているので、データ共有はデジタルエコノミーにおいて非常に重要になっています。既存のデータ共有ソリューションの限界に対応するために、Databricksでは、OSSコミュニティから様々な貢献を受けながら[Delta Sharing](https://github.com/delta-io/delta-sharing)を開発し、Linux Foundationに寄贈しました。我々は、向こう数週間でDelta SharingがGAになることを発表しました。

Databricksはお客様が企業の境界を超えてデータを共有しコラボレーションする支援をおこなっており、Databricksとマーケットプレースとデータクリーンルームによって実現されるデータ共有のエンハンスメントも公開しました。

- [Databricksマーケットプレース](https://databricks.com/blog/2022/06/28/introducing-databricks-marketplace-an-open-marketplace-for-all-data-and-ai-assets.html): 向こう数ヶ月で利用できるようになります。Databricks Marketplaceでは、ベンダーロックインなしにデータセットをパッケージして配布し、ノートブック、サンプルコード、ダッシュボードのような関連アセットをホストします。
- [データクリーンルーム](https://qiita.com/taka_yayoi/items/dbbac30d4df3754b38a0): 向こう数ヶ月で利用できるようになります。レイクハウスのデータクリーンルームは、背後のデータを共有することなしに、分析でパートなリングすることで企業が安全に洞察を導き出す手段を提供します。

# ベストなデータウェアハウスはレイクハウスです

データチームにとって、データウェアハウジングはビジネス上最も重要なワークロードの一つです。[Databricks SQL \(DBSQL\)](https://databricks.com/jp/product/databricks-sql)はDatabricksレイクハウスプラットフォームにおけるサーバレスデータウェアハウスであり、ロックインなしに皆様の大規模SQL、BIアプリケーションをのコストパフォーマンスを最大12倍改善し、統合されたガバナンスモデル、オープンなフォーマット・APIを提供し、好きなツールを活用することができます。Databricksは、分析ワークロードをさらにエンハンスする新たなデータウェアハウジングの機能を発表しました。

- [**Databricks SQLサーバレス**](https://qiita.com/taka_yayoi/items/744926b05c1d05456bad)はAWSでプレビューとなり、低コストで改善されたパフォーマンスを発揮するセキュアかつ即時に利用できる完全にマネージドな弾力性のある計算資源を提供します。
- レイクハウスにおける行指向クエリーエンジンである**Photon**は向こう数週間でDatabricksワークスペース上でGAとなり、プラットフォームのさらに広い範囲でPhotonが利用できるようになります。Photonを発表して以来の2年間、エクサバイト規模のデータを処理し、数十億のクエリーを実行し、従来型のクラウドデータウェアハウスと比較して最大12倍のコストパフォーマンスを示すベンチマークを生み出しました。
- **Go、Node.js、Python向けオープンソース[コネクター](https://qiita.com/taka_yayoi/items/ea08adb714c674b7aa98)** によって、オペレーションで使用しているアプリケーションからよりシンプルにレイクハウスにアクセスできるようになり、**Databricks SQL CLI**を用いることで開発者やアナリストは自分のローカルコンピュータから直接クエリーを実行することができます。
- Databricks SQLは**クエリーフェデレーション**を提供するようになり、ソースシステムから最初にデータを抽出、ロードする必要なしに、PostgreSQL、MySQL、AWS Redshiftのようなリモートデータに対するクエリーを行えるようになります。
- **Python UDF**はDatabricks SQLにPythonのパワーをもたらします！アナリストは、すでにデータサイエンティストが開発している複雑な変換ロジックから機械学習モデルをSQL文から利用できるようになり、Python関数の世界に踏み出すことができます。
- 効率的かつインクリメンタルな計算処理によって、エンドユーザーのクエリーを高速にし、インフラストラクチャのコストを削減すするために**マテリアライズドビュー**(MV)のサポートを追加しました。Delta Live Tables(DLT)の上に構築されることで、MVは事前計算を行わないと遅いクエリーの事前計算を行ったり、頻繁に使用する計算処理を行うことで、レーテンシーを削減します。
- **主キーと外部キー制約**によって、アナリストがレイクハウスで高度なデータモデリングを行う際に慣れ親しんだツールを活用できるようになります。より改善されたクエリープランニングのために、DBSQLやBIツールでこの眼ターデータを活用することができます。

# 高信頼データエンジニアリング

Databricksでは毎日数千万ものプロダクションワークロードが実行されています。Databricksレイクハウスプラットフォームを用いることで、データエンジニアはバッチデータ、ストリーミングデータを取り込み、変換し、大規模高信頼プロダクションワークフローをオーケストレーションする[エンドツーエンドのデータエンジニアリングソリューション](https://databricks.com/jp/solutions/data-engineering)にアクセスできるようになり、ビルトインのデータ品質テストやソフトウェア開発におけるベストプラクティスのサポートによってデータチームの生産性を高めることができます。

最近我々は高信頼データパイプラインを構築するためのシンプルかつ宣言型のアプローチを用いる業界初のETLフレームワークである[Delta Live Tables \(DLT\)](https://databricks.com/jp/product/delta-live-tables)の3クラウドでのGAを発表しました。今年頭の[ローンチ](https://databricks.com/company/newsroom/press-releases/databricks-announces-general-availability-of-delta-live-tables)以来、[DatabricksではDLTに新機能の拡張](https://qiita.com/taka_yayoi/items/7dcd8730fbb097952caa)を行なってきました。ETLワークロードに特化したパフォーマンス最適化機構であるEnzymeを発表できることを嬉しく思っています。EnzymeはDeltaテーブルに格納された特定のクエリー結果の最新のマテリアライゼーションを効率的に保持します。従来のマテリアライズドビューで用いられているテクニック、delta-to-deltaストリーミング、我々のお客さまにおいてよく使われている手動のETLパターンを含むさまざまなテクニックからコストモデルに基づいて選択を行います。さらに、DLTは新たにエンハンスされたオートスケーリング機能を提供します。ストリーミングワークロードの変動に応じてインテリジェントにリソースをスケールし、CDCのSlowly Changing Dimensions—Type 2では、コンプライアンスや機械学習の実験目的の両方で容易にソースの変更を追跡できます。チェンジデータを取り扱う際(CDC)、多くの場合は最も最新のデータを追跡するためにレコードを更新する必要があります。SCD Type 2はオリジナルのデータが保持されるようにターゲットに更新を適用する手段です。

また、3つのクラウド全てで高信頼のデータ、分析、AIワークフローに対する完全マネージドのレイクハウスオーケストレーションサービスである[Databricks Workflows](https://databricks.com/jp/product/workflows)のGAを発表しました。今年初めの[ローンチ](https://databricks.com/blog/2022/05/10/introducing-databricks-workflows.html)以来、パブリックプレビューであるワークフローでのGitサポート、プロダクションでのdbtプロジェクトの実行、ジョブでのSQLタスクタイプの導入、ジョブにおける新たな「リペアおよびリラン」機能、タスク間でのコンテキスト共有など新たな機能を用いて、[Databricks Workflowsを拡張し続けています](https://qiita.com/taka_yayoi/items/a9fe1af72d2929b3d68b)。

# 大規模プロダクション機械学習

レイクハウスにおけるDatabricks Machine Learningでは、データ取り込みからトレーニング、デプロイメント、モニタリングに至るエンドツーエンドの機械学習機能を影向された体験として提供しており、MLライフサイクルにまたがる一貫性のあるビューを生成し、より強力なチームコラボレーションを実現します。皆様がモデルより迅速にプロダクションに移行できるようにMLライフサイクルにおけるイノベーションを継続しています。

- 最も成功しているオープンソース機械学習(ML)プロジェクトの一つである[MLflow 2\.0](https://qiita.com/taka_yayoi/items/29a54ba9a5df4a38b3ad)が、MLプラットフォームの標準を打ち出しました。MLflow 2.0のリリースでは、MLOpsをシンプルにし、より多くのプロジェクトをプロダクションに移行できるようにするために**MLflow Pipelines**を導入します。これは、すぐに利用できるテンプレートを提供し、チームが実験段階からプロダクションへの引き継ぎを自動化できるようにする構造化されたフレームワークを提供します。最新バージョンのMLflowでこの機能のプレビューを試すことができます。
- [サーバレスモデルエンドポイント](https://qiita.com/taka_yayoi/items/c6d44624858b9ea8497f)では、自分でインフラストラクチャを管理する必要なしに、プロダクションアプリケーションのリアルタイム推論のために皆様のモデルをデプロイすることができます。ユーザーは、自分のモデルのスループットをコントロールしたり、予測可能なトラフィックのユースケースのためにオートスケーリングをカスタマイズすることができ、オートスケーリングをゼロにまでスケールさせることで、チームはコストを節約することができます。
- [モデルモニタリング](https://qiita.com/taka_yayoi/items/c6d44624858b9ea8497f)を用いることで、皆様のプロダクションモデルのパフォーマンスを追跡することができます。これは、チームがデータとモデル品質のドリフトを参照し、分析する役に立つダッシュボードを自動で生成します。また、モデルモニタリングは背後にある分析テーブル、ドリフトテーブルをDeltaテーブルとして提供するので、チームはビジネスインパクトを計算するためにビジネスバリューメトリクスとパフォーマンスメトリクスをjoinし、メトリクスが特定の閾値を下回った場合にアラートを生成することができます。

# より詳細は

モダンなデータチームは次世代のデータ&AIアプリケーションの要件を満たすためのイノベーティブなデータアーキテクチャを必要としています。レイクハウスのパラダイムは、シンプルかつマルチクラウド、そしてオープンプラットフォームを提供し、一つのプラットフォームにおいてBI、AI、機械学習を行いたいと考えているすべてのお客様をサポートするという我々のミッションには変わりはありません。これらの発表の詳細については[オンデマンドでData & AIサミットのキーノート、ブレークアウトセッション](https://databricks.com/dataaisummit/)を視聴できます。また、Databricksレイクハウスプラットフォームにディープダイブするために、[Databricksレイクハウスプラットフォームへのデータチームのガイド](https://databricks.com/p/ebook/the-data-teams-guide-to-the-databricks-lakehouse-platform)をダウンロードすることもできます。


### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

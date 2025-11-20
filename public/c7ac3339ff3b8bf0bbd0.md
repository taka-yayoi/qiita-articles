---
title: Data + AIサミットで発表された重要ニューストップ10
tags:
  - Databricks
  - DAIS2021
private: false
updated_at: '2021-07-20T08:18:05+09:00'
id: c7ac3339ff3b8bf0bbd0
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Top 10 Announcements from Databricks Data \+ AI Summit 2021 \- The Databricks Blog](https://databricks.com/blog/2021/06/04/dont-miss-these-top-10-announcements-from-data-ai-summit.html)の翻訳です。

[2021 Data \+ AI Summit](https://databricks.com/dataaisummit/north-america-2021)は、TensorFlowの共同開発者であるRajat Mongaなどトップレベルのクリエーターのトーク、Bill Nye、Malala Yousafzai、NASA Mars Roverチームといったゲストの登壇など、オープンソースとDatabricksにとってはエキサイティングなニュースで溢れていました。6/28までであれば、無料の登録を行うことで、[Summit platform](http://dataaisummit.com/)でキーノートなどをオンデマンドで視聴することができます。

この記事では、サミットで発表された内容に対する個人的トップ10をご紹介したいと思います。以下は順不同です。サミットプラットフォームのリンクも併せて記載しています。

# Delta Lake 1.0

Delta Lakeオープンソースプロジェクトは、データ品質、性能、ガバナンスといったデータレイクの限界を打破するものであるため、レイクハウスの鍵となるイネーブラとなっています。プロジェクトは最初のリリースから長い道のりを歩んできており、ついにDelta Lake 1.0のリリースがコミュニティによって認証されました。このリリースには、generated columnsやマルチクラスターの書き込みによるクラウド非依存性、私のお気に入りのDelta Lakeスタンドアローン(Apache SparkがなくてもDeltaテーブルからの読み込みが可能)など多くの新機能が含まれています。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-1-e1622759138816.jpg)
*水曜日午前のキーノートでのDelta Lake 1.0の発表*

また、この場で我々は、QP Hou、R.Tyler Croy、Christian Williams、Mykhailo Osypov、Florian ValeyeといったDelta Lakeプロジェクトの新たなコミッターを紹介しました。

Delta Lake 1.0の詳細に関しては、共同開発者であり素晴らしいエンジニアであるMichael Armbrustの[キーノート](https://dbricks.co/3urRADK)をご覧ください。

# Delta Sharing

オープンというのはオープンソースに限ったことではありません。アクセス、共有に関しても同様です。データは成功している企業において血液も言えるものになっていますが、それは同時に企業間でスムースに共有できるものであるべきです。データ共有ソリューションは歴史的に特定の商用製品に紐づけられており、ベンダーロックインのリスクやデータのサイロ化をい引き起こしていました。Databricksの共同創始者でありCEOであるAli Ghodsiは、業界初のセキュアなデータ共有のためのオープンプロトコルである[Delta Sharing](https://qiita.com/taka_yayoi/items/f93f1b70fef0f75585be)を発表しました。SQLとPythonのデータサイエンスをサポートし、プライバシー、セキュリティ、コンプライアンスを容易に管理できます。これはLinuxファウンデーションの元にあるDelta Lakeプロジェクトの一部となります。

我々はすでに、AWS data exchange、FactSet、S&P Global、Nasdaqなどから提供される1000以上のデータセットによって多大なるサポートをいただいています。加えて、Microsoft、Google、Tableauといった多くの企業がDelta Sharingのサポートを自社の製品に組み込むことを表明しています。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-2-1024x575.jpg)
*水曜午前のキーノートにおけるDelta Sharingの発表*

Delta Sharingの詳細に関しては、MLflowの共同開発者Matei Zahariaの[キーノート](https://dbricks.co/3urRADK)をご覧ください。Tableauのセッション[How to Gain 3 Benefits with Delta Sharing](http://dbricks.co/tableau-benefits-delta-sharing)もご覧ください。

# Delta Live Tables

データ品質は後段のワークロードに大きな影響を与えるため、ETLやELTは多くのデータワークロードで非常に重要なものとなっています。これは多くのケースで、汚い入力データを、求められルユースケースにフィットするように綺麗で鮮度があり、かつ信頼性のあるデータに変換するきちんとしたデータフローとして表現されます。しかし、現実はそう単純ではありません。データパイプラインは脆弱で正しいものにするには非常に時間がかかります。

Delta Lakeの上で自動、高信頼なETLを可能にする[Delta Live Tables](https://databricks.com/product/delta-live-tables)がサミットで発表されました。自動テスト、管理、モニタリング、リカバリー、データパイプラインのライブアップデートをサポートしています。そして、特筆すべきことですが、これら全てをSQL(分析、AIワークロードのためにPythonもサポートしています)で行えるのです。
![](https://databricks.com/wp-content/uploads/2021/06/delta-live-tables.jpg)
*製品管理VPのAwez SyedによるDelta Live Tablesセッション*

Delta Live Tablesの詳細に関しては、比類なきエンジニアであるMichael Armbrustの[キーノート](https://dbricks.co/3urRADK)をご覧ください。製品管理VPのAwez SyedによるDelta Live Tablesセッション[Making Reliable ETL Easy on Delta Lake](http://dbricks.co/delta-live-tables-session)もご覧下さい。

# 早期リリース: オライリーのDelta Lake Definitive Guide

私が尊敬する同僚のDenny Lee、Vini Jaiswal、Tathagata Dasは、どのようにしてDelta Lakeで[モダンなデータレイクハウスアーキテクチャ](https://databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html)を構築するのかを説明する新たな本を執筆するのに大変な労力を費やしていました。キーノートでMichael Armbrustが発表したように、早期リリース版のオライリー本を無料で提供します。[こちら](https://databricks.com/p/ebook/delta-lake-the-definitive-guide-by-oreilly)から無料でダウンロードできます。また、最終版が発行された際には改めてご連絡します。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-3-1024x642.jpg)
*早期リリース:Delta Lake Definitive Guide*

# Unity Catalog

多くの企業はクラウドのデータレイクに大量のデータを集めており、その量は増える一方です。単一のクラウドにおいてもガバナンスを維持することは難しく、多くの企業が活用しているマルチクラウドにおいてはさらに困難になります。[Unity Catalog](https://qiita.com/taka_yayoi/items/1ededa3458cfffb2f83b)は、ユーザーに対してすべてのクラウドに対して標準化されたきめ細かいソリューションを提供する業界初のレイクハウス用統合カタログです。ANSI SQLを用いることで、ファイルではなくテーブル、列、ビュー、モデルに対するアクセスコントロールを行うことができます。また、誰がデータにアクセスしたのかを容易に理解できる監査ログも提供しています。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-4-1024x574.jpg)
*キーノートにおけるUnity Catalogの発表*

詳細に関してはチーフテクノロジストのMatei Zahariの[キーノート](https://dbricks.co/3urRADK)をご覧ください。またUnity Catalogの[ウェイティングリスト](https://dbricks.co/3urRADK)にサインアップしてください。

# Databricks SQL:性能、管理、分析者体験の改善

我々はオープンな方法で高性能、シンプル、パワフルなSQLプラットフォームを提供したいと考えています。SQLはデータレイクハウスのビジョンにおいて重要なパーツであり、我々は実世界のアプリケーションにおけるSQLのパフォーマンスと使いやすさを改善することにフォーカスしています。

去年、我々はどのようにDatabricksがDelta LakeとPhotonエンジンを用いて、30TBワークロードにおいてTPC-DSの価格・パフォーマンスの観点でデータウェアハウスよりも優れているのかを説明しました。サミットでは、DatabricksのチーフアーキテクトReynold Xinが、10GBのTPC-DSワークロードにおいて同時実行性にフォーカスして、パフォーマンス最適化のアップデートを説明しました。100以上もの細かな最適化を通じて、Databricks SQLは同時実行ユーザーによる小さいクエリーにおいては著名なクラウドデータウェアハウスの性能を上回ることを確認しました。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-5-1024x573.jpg)
*DatabricksのチーフアーキテクトReynold XinによるDatabricks SQLの改善の説明*

詳細に関しては、Apache Sparkの偉大なるコントリビュータであるDatabricksのチーフアーキテクトReynold Xinによる[improvements in Databricks SQL and the Photon Engine](https://dbricks.co/3urRADK)を参照ください。Databricks CEO Ali Ghodsiとデータウェアハウスの父Bill Inmonとのディスカッションもご覧ください。

Photonチームのテックリード、プロダクトマネージャーによる[詳細なセッション](http://dbricks.co/photon-under-the-hood)もご覧ください。

# レイクハウスのモーメント

オープニングキーノートでDatabricks CEOのAli Ghodsiが発表したレイクハウス導入のモーメントは、データチームの作業を簡素化する偉大な技術的前進を表現するものです。

もはやこれらの企業はデータレイクと(複数の)データウェアハウスの二層のデータアーキテクチャを持つ必要はありません。データレイクハウスの導入によって、データウェアハウスの持つパフォーマンス、信頼性、コンプライアンス機能、データレイクの非構造化データのサポート、スケーラビリティを手に入れられます。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-6-1024x535.jpg)

Rohan Dhupeliaは、レイクハウスがどのようにAtlassianのデータチームの作業を変化させ、簡素化したのかをオープニングキーノートで説明しました。

そしてAliはデータウェアハウスの父であるBill Inmonを招待し、バーチャルステージで彼が過去数十年で見てきた変化を語っていただきました。Billは「データレイクをレイクハウスに変換しないのであれば、それはスワンプになってしまいます」と言いました。そして、レイクハウスはデータの制限を解放し、これまでに見たことのない可能性を提供することになると強調しました。

[オープニングキーノート](https://dbricks.co/3urRADK)におけるAli、Rohan、Billによるレイクハウスアーキテクチャ、データエンジニア、データアナリストに関する話を聞いてください。レイクハウスの進化を理解するためにBillの[ブログ記事](https://databricks.com/blog/2021/05/19/evolution-to-the-data-lakehouse.html)を読んでみてください。また、Billが執筆予定のデータレイクハウスに関する本を楽しみにしてください。

# KoalasのApache Sparkへの統合

データサイエンティストにおける最も重要なライブラリはpandasです。データサイエンティストがシングルノードの「ラップトップデータサイエンス」から大規模なスケーラブルクラスターに移行するのをサポートするために、我々は二年前にKoalasプロジェクトを立ち上げました。Koalasは、大規模データセットでの動作に最適化したpandas APIの実装です。

現時点でPyPIのダウンロードにおいてKoalasは300万以上のダウンロードを確認しており、大規模データにおけるデータサイエンティストの作業のあり方を変化させています。Apache SparkのトップコントリビュータであるReynold Xinは、Koalasを上流のApache Sparkプロジェクトに寄贈することを発表しました。Apache　Sparkのコードを記述する時にはいつでもpandas APIを快適に利用できるようになります。

この二つのプロジェクトの統合によって、Sparkユーザーにもメリットが生まれます。Spark上でpandas APIの効率的なプロット技術を活用することで、手作業のダウンサンプリングを行うことなしに、最適なデータプロットの手段を自動的に決定することができます。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-7-1024x527.jpg)
*Databricks機械学習プラクティスリードBrooke WenigによるSpark上でのpandas APIデモ*

Reynold XinとBrooke Wenigによる[キーノート](https://dbricks.co/amkeynote)におけるKoalasの統合の説明とデモをご覧ください。ベンチマークなどの詳細に関しては、エンジニアリングチームによる[Koalasプロジェクトのディープダイブ](http://dbricks.co/koalas-comparison)をご覧ください。

# 機械学習ダッシュボード

製品管理ディレクターClemens Mewaldが、Databricksにおける機械学習の機能におけるいくつかの改善点を発表しました。

これらの改善は、データからモデル配備まで(逆方向も含みます)の機械学習の完全なライフサイクルをシンプルにすることを狙いにしています。ペルソナに基づいてDatabricksワークスペースをナビゲーションするようにしたのもその一つです。MLダッシュボードを提供することで、データ、モデル、特徴量ストア、エクスペリメント追跡を単一のインタフェースに統合することができます。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-8.png)
*製品管理ディレクターClemens MewaldによるML新機能の説明*

詳細に関しては、Clemens Mewaldのキーノート[Spark, Data Science, and Machine Learning keynote](https://dbricks.co/amkeynote)をご覧ください。これらの詳細に踏み込んだ[詳細セッション](https://dbricks.co/2TmsWrs)もあります。

# 機械学習特徴量ストア

[Databricks Feature Store](https://qiita.com/taka_yayoi/items/3772150dd3557272f61d)は初めてデータとMLOpsプラットフォームと協調設計された史上初の特徴量ストアです。

特徴量とはなんでしょうか？特徴量は機械学習モデルの入力となり、変換、コンテキスト、特徴量の拡張、事前に計算された属性が含まれるものです。

特徴量ストアは、迅速かつ容易に特徴量を実装できるようにし、オンライン・オフラインの偏りを避けるためにトレーニングと低レーテンシーでのオンラインサービングの両方に特徴量が用いられるようにするために存在しています。Databricks Feature Storeには、データソースの追跡容易性を含む特徴量の発見容易性、再利用性を高めるための特徴量レジストリが含まれています。これはMLflowとも統合されており、これによって手動の設定なしに、本格運用のモデルサービングで自動的にモデルが特定バージョンの特徴量を使用するようになります。

Databricks Feature Storeに格納されるデータは、オープンフォーマットDelta Lakeテーブルに保持されますので、Python、SQLなどのクライアントからアクセスできます。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-9-1024x534.jpg)
*製品管理ディレクターClemens MewaldによるML新機能の説明*

詳細は[Spark, Data Science and Machine Learning keynote](https://dbricks.co/amkeynote)におけるClementsの説明と、シニアプロダクトマネージャのKasey Uhlenhuthによるデモをご覧ください。より詳細を説明する[in\-depth session](https://dbricks.co/2TmsWrs)もございます。

# 再現可能なノートブックを持つAutoML

[Databricks AutoML](https://qiita.com/taka_yayoi/items/3bf4f4e89990b299c6c9)は、データチームの管理権限を奪うことなしに、データチームを強力に支援するユニークなガラスボックスアプローチを採用したものです。機械学習プロジェクトの実行可能性を迅速に検証し、プロジェクトの方向性をガイドするためのベースモデルを生成します。

多くの他のAutoMLソリューションはデータサイエンティスト初心者向けに設計されており、モデルがうまく動作しない場合にはチューニングする余地を提供していないため、データサイエンティストは壁に直面することになります。
![](https://databricks.com/wp-content/uploads/2021/06/dais-21-recap-blog-img-10.png)
*シニアプロダクトマネージャのKasey UhlenhuthによるAutoMLのガラスボックスアプローチの説明*

Databricks AutoMLはデータサイエンティストの能力を拡張し、それぞれのトレーニングごとにソースコードを編集可能なPythonノートブックとして提供することで、内部で何が起きているのかを確認できるようにします。このガラスボックスアプローチの透明性は、あなたのドメイン知識に基づいて自動生成されたモデルをチューニングする際に、不透明なモデルをリバースエンジニアリングする必要がないことを意味します。どのようにモデルがトレーニングされたのかを明らかにできるので、コンプライアンス規制による要件に対応することもできます。

AutoMLはMLflowと密接に統合されていますので、トレーニングにおける全てのパラメーター、メトリクス、アーティファクト、モデルを全て追跡します。詳細は[in\-depth session](https://dbricks.co/2TmsWrs)をご覧ください。

# 詳細を知るには

実際には11の発表をカバーしたことに気づいたかもしれません。これは実は0で始まるインデクスにおける10なのでした。すみません。あまりにシェアしたいことが多すぎたので。

[Data \+ AIサミット2021で発表されたDatabricksの新機能 \- Qiita](https://qiita.com/taka_yayoi/items/d4111246048089588cc7)もご覧ください。

2021年のセッションを再度見るには、イベントサイトに[登録](https://databricks.cventevents.com/event/45414668-315b-4f08-b539-d9269a28d939/register)あるいは[ログイン](https://dataaisummit.com/login/)してください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

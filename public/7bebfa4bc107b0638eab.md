---
title: 自然言語処理によるリアルワールド診療データからのオンコロジー(腫瘍学)に関する洞察の抽出
tags:
  - 自然言語処理
  - Databricks
  - ヘルスケア
  - ソリューションアクセラレータ
private: false
updated_at: '2021-09-28T14:10:10+09:00'
id: 7bebfa4bc107b0638eab
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Extracting Oncology Insights from Real\-World Clinical Data with NLP \- The Databricks Blog](https://databricks.com/blog/2021/09/22/extracting-oncology-insights-from-real-world-clinical-data-with-nlp.html)の翻訳です。

**半構造化、非構造化データ：オンコロジー(腫瘍学)のエビデンスの生成における課題**

> このブログで参照しているソリューションアクセラレータのノートブックを[オンライン](https://databricks.com/notebooks/jsl_oncology/index.html#01_entity_extraction.html)で確認するか、ノートブックを[ダウンロード](https://databricks.com/solutions/accelerators/nlp-oncology)してお使いのDatabricksアカウントにインポートして試してみてください。

アメリカにおいて癌は[主要な死因](https://www.fightcancer.org/sites/default/files/National%20Documents/Costs-of-Cancer-2020-10222020.pdf)、病因となっており、驚くべきことに今年においても[200万もの新たな癌のケース](https://www.cancer.org/research/cancer-facts-statistics/all-cancer-facts-figures/cancer-facts-figures-2021.html)が診断されています。また、癌はアメリカにおける診療費の大部分を占めており、2020年で2000億ドル以上と推定されています。このため、バイオ医薬品業界は、抗癌剤の開発に特にフォーカスしています。2019年、2020年のみでもFDAによっておよそ40の新たな抗癌剤が承認されており、1,300以上の新薬、ワクチンが臨床開発段階にあります。

患者にとって適切な介入方法を選択するためには、オンコロジーの介入の効果を計測することが重要となります。オンコロジーデータ、関係するリアルワールドのエビデンスは、臨床研究、臨床試験のデザイン、規制上の意思決定、安全性の評価、治療計画などに情報を提供するポテンシャルを持っています。残念ながら、オンコロジー治療の特殊性から、病気の評価指標やエンドポイントは多くのケースで構造化されたフォーマットでは利用できず、データサイロに閉じ込められたままとなっており、集約や分析を困難なものにしています。

オンコロジーにおいては、病理学のレポート(多くの場合PDFフォーマットであり、EMRシステムのサイロに格納されています)には、腫瘍のサイズ、グレード、ステージ、組織構造などの重要な情報が含まれています。自然言語処理(NLP)システムによって抽出された変数は、病気のグループを定義し、病気の深刻度を評価し、病状進行のベースラインを作成するために活用することができ、前述した臨床試験のマッチングから治療計画に至るユースケースに適用することができます。しかし、構造化されていない診療テキストデータからの情報の抽出が、データチームにとって非常に大きなペインポイントとなるケースが多くあります。

ヘルスケアNLPのリーダーであるJohn Snow LabsとDatabricksは、この問題に正面から取り組み、構造化されていないオンコロジーのデータをアクション可能なエビデンスに変換するために、ヘルスケアエコシステムにおける多くのお客様とともに協働しています。

# DatabricksとJohn Snow Labsによる大規模医療自然言語処理

前進するための道のりは、データ管理、パフォーマンスのようなデータウェアハウスの優れた要素と、クラウドデータレイクの低コスト、柔軟性、スケーラビリティを組み合わせたモダンなデータプラットフォームである、[Databricksのレイクハウスプラットフォーム](https://databricks.com/jp/product/data-lakehouse)からスタートします。[ヘルスケアシステムを有効化する新たなシンプルなアーキテクチャ](https://qiita.com/taka_yayoi/items/48a56bf5fb36918e9480)は、従来の分析とデータサイエンス両方に対応するために、構造化データ(EHRデータベースにおける診断/プロシージャコード)、半構造化データ(HL7、FHIRメッセージ)、非構造化データ(フリーテキストのメモや画像)といった全てのデータを単一の高パフォーマンスに統合します。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-1.png)

Databricksのレイクハウスプラットフォームのコアには、データレイクに(Apache Spark™を通じた)パフォーマンス、信頼性、ガバナンスをもたらすオープンソースストレージレイヤーである[Delta Lake](https://delta.io/)があります。ヘルスケア企業は、生のプロバイダーノート、放射線医学レポート、PDFの病理レポートなどお使いの全てのデータをDelta Lakeに格納することができます。これによって、データ変換を行う前のオリジナルの信頼できる情報源を保持することができます。一方、従来型のデータウェアハウスにおいては、データを取り込む前にデータの変換が行われるため、非構造化のテキストから抽出された構造化された変数は、もともとのテキストから分断されることになります。

この基盤の基礎になっているのは、ヘルスケア、ライフサイエンス業界で[最も広く使用されているNLPライブラリ](https://gradientflow.com/2020nlpsurvey/)であるJohn Snow Labsの[ヘルスケア向けSpark NLP](https://www.johnsnowlabs.com/spark-nlp-health/)です。Databricks上での動作に最適化されることで、ヘルスケア向けSpark NLPはシームレスかつ大規模、最先端の精度で、医療、生物医学テキストデータを分類し、構造化し、抽出を行います。Python、Java、Scalaに対応している唯一のネイティブ分散オープンソーステキスト処理ライブラリであり、すべてのSpark NLPパイプラインはSpark MLパイプラインなので、統合されたNLP、機械学習パイプラインの構築に特に適しています。Spark NLPは、[従来のNLPライブラリ(spaCy、nltk、Stanford CoreNLP、Open NLPなど)の全ての機能](https://blog.dominodatalab.com/comparing-the-functionality-of-open-source-natural-language-processing-libraries/)に加え、スペルチェック、感情分析、文書分類などの追加機能を備えたPython、Java、Scalaのライブラリを提供します。DatabricksとJohn Snow Labsのジョイントソリューションの詳細に関しては、以前の記事、[ヘルスケアにおける大規模テキストデータへの自然言語処理の適用](https://qiita.com/taka_yayoi/items/fcf396cf75418e87ec76)を参照ください。

# リアルワールドオンコロジーデータ要約の実践

DatabricksとJohn Snow Labsのパワーをデモンストレーションするために、オンコロジーノートからリアルワールドデータを要約するための[ソリューションアクセラレータ](https://databricks.com/notebooks/jsl_oncology/index.html#01_entity_extraction.html)を作成しました。ソリューションアクセラレータには、後段の分析およびリアルワールドのエビデンスのためのオンコロジーレポートの取り込み、準備に関するステップバイステップの手順書、構築済みのコード、サンプルデータが含まれています。ソリューションはDatabrikcsノートブックとして実行できる様になっており、すぐにスタートできるように、以下のソリューションの簡単なウォークスルーを含めています。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-2.jpg)

本ソリューションにおいては、[MT ONCOLOGY NOTES](https://www.mtsamplereports.com/)データセットを使用しました。これには、主に医療専門家によって書き起こされた医療レポートのサンプルと、医療レポートの一部を構成する特定のセクション、例えば、物理的検査(physical examination)あるいはPE、システムレビュー(review of system)あるいはROSといったセクションにおける医療単語、フレーズの書き起こし、研究データ、精神状態の試験などから構成されています。

ここでは、非構造化テキストのソースとしてMT Oncology notesデータセットから匿名化された50のオンコロジーレポートを選択し、Delta Lakeのブロンズレイヤーに生のテキストデータを取り込みました。デモであるので、サンプル数を50に限定していますが、このソリューションアクセラレータで提供されるフレームワークは、数百万の診断ノート、テキストデータに対応できる様になっています。

このアクセラレータの最初のステップは、固有表現抽出(Named-Entity Recognition:NER)の様々なモデルを用いて変数を抽出するというものです。このために、最初にNLPパイプラインをセットアップします。これには、特にヘルスケア関係のNER向けにトレーニングされたdocumentAssembler、sentenceDetector、tokenizerのような[annotators](https://nlp.johnsnowlabs.com/docs/en/annotators)が含まれます。以下の例では、医療NERモデルである[bionlp\_ner](https://nlp.johnsnowlabs.com/2021/03/31/ner_bionlp_en.html)と医療単語向けにトレーニングされたディープNERモデルである[jsl\_ner](https://nlp.johnsnowlabs.com/2021/01/18/jsl_ner_wip_clinical_en.html)を組み合わせました。中皮腫(mesothelioma)の患者が咳などの症状を経験していることがわかります。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-3.jpg)

テキストからの固有表現の抽出は、AIアシストETLの素晴らしい例となります。学習済みのディープラーニング(DL)モデルによって、後段の医療分析で活用できるように非構造化データを構造化フォーマットに変換することができます。

症状を抽出することで、メディケアリスクの調整のためのコーディング精度を改善し、[Hierarchical Condition Category](https://www.aafp.org/fpm/2016/0900/p24.html#fpm20160900p24-b1)(HCC)コーディングを自動化するために使用される[ICD\-10コード](https://www.who.int/standards/classifications/classification-of-diseases)にマッピングすることができます。治療のパターンを分析し、症状と腫瘍学エンティティとの関係性を分析するために、このデータを活用することができます。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-4.jpg)
*図1. 医療データセットにおいてコード化された症状に対する平均リスク*

![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-5.jpg)
*図2. データセットにおいて頻出している条件と病状の可視化*

さらに、これらの症状が存在しているか、存在していないか、あるいは他の誰かと関連していないかといった主訴(assertion status)を研究するためのチャートを作成することができます。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-6.png)

同じノートデータセットに対して、最も一般的なオンコロジーのエンティティと彼らの主訴を重ね合わせることで、解説的かつビジュアルな統計処理を実行することができます。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-7.png)
*図3. 最も一般的な症状に対する主訴*

次に、投薬の頻度、期間を含む治療を見ていきます。これは、オンコロジーの治療の基礎となります。以下は投薬治療と期間に関する情報を抽出するソリューションノートブックに含まれているNLPモデルのスクリーンショットです。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-8.jpg)

これによって、症状と治療、最初の様な病状を信頼性スコアとともに関連づけることができます。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-9.jpg)

個々の患者ケアの品質保証と、人工レベルの研究において、データは重要なものであり、リアルワールドにおける介入の効果と安全性を結論づける役に立つものです。

Databricksのレイクハウスプラットフォームを用いることで、状態、症状、治療、そして構造化されていないノートから抽出された他の適切な情報を含むデータベースを容易に構築することができ、後段の分析、医療上の意思決定サポート、研究に活用することができる様になります。
![](https://databricks.com/wp-content/uploads/2021/09/Extracting-Oncology-Insights-from-Real-World-Data-with-NLP-blog-img-10.jpg)

このソリューションアクセラレータを用いることで、DatabricksとJohn Snow Labsは、リアルワールドのエビデンス生成に求められる品質で大規模オンコロジーデータから情報を抽出することができる扉を開きました。

# NLPを用いてオンコロジーノートからリアルワールドデータを抽出してみる

このソリューションを活用するには、ノートブックを[オンライン](https://databricks.com/notebooks/jsl_oncology/index.html#01_entity_extraction.html)で確認するか、ノートブックを[ダウンロード](https://databricks.com/solutions/accelerators/nlp-oncology)してお使いのDatabricksアカウントにインポートして試してみてください。これらのノートブックには、関係するJohn Snow Labs NLPのライブラリやライセンスキーをインストールする手順が含まれています。

[ヘルスケア](https://databricks.com/solutions/industries/healthcare-industry-solutions)、[ライフサイエンス](https://databricks.com/solutions/industries/life-sciences-industry-solutions)のソリューションについて、業種別ページで詳細を確認することも可能です。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

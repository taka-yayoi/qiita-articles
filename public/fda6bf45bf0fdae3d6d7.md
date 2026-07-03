---
title: Databricksによる新たなSOTAオープンLLM「DBRX」のご紹介
tags:
  - Databricks
  - LLM
  - DBRX
private: false
updated_at: '2024-04-27T18:50:54+09:00'
id: fda6bf45bf0fdae3d6d7
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---

こちらのイベントで説明した内容です。

https://machine-learning15minutes.connpass.com/event/314043/

![Screenshot 2024-04-27 at 18.16.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/af64c1d7-6852-79de-b570-ea672833c1f7.png)

# 自己紹介

![Screenshot 2024-04-27 at 18.17.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/67eee225-88cf-8816-649e-0944dce3d056.png)

弥生 隆明と言います。4年前にDatabricksにジョインしました。

- [Qiita](https://qiita.com/taka_yayoi)
- [X](https://twitter.com/taka_aki)
- [LinkedIn](https://www.linkedin.com/in/takaaki-yayoi/)

# Spark本の宣伝と会社紹介

今月、Spark本を出しました！DatabricksはSparkのクリエーターが創業した会社です。
![Screenshot 2024-04-27 at 18.18.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/10cd2407-1d12-16cb-0a3e-404c5431d6b7.png)
![Screenshot 2024-04-27 at 18.20.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bc0050e9-68b0-f024-d25f-19c3d5767ca3.png)

# 今日お話ししたいこと

もちろん、DBRXをご説明しますが、それだけではありません。DBRX含む生成AIに対するDatabricksのスタンスについてもお話しさせてください。

# その前に、「Dolly」を覚えていますか？

![Screenshot 2024-04-27 at 18.22.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/db5e96d7-d8e9-de06-c11d-e76a9c3364cd.png)

- こちらのイベントでも紹介させていただきましたが、去年の4月に[バージョン2.0](https://huggingface.co/databricks/dolly-v2-12b)を公開しましたEleutherAIのpythiaモデルファミリーをベースとした12Bのパラメーターを持つ言語モデルです
- これは以下の我々の理念のもと取り組んだものです
    - お客様自身がモデルを所有し、自分のデータを活用してアプリケーションを構築できるようにすべきです
    - 今日の他の方の発表でも触れられていた、バイアスや説明可能性に関する重要な問題やAIの安全は、数社の大企業ではなく多様なステークホルダーのコミュニティによって取り組まれるべきです

**これらの理念を変えることなしに、我々は新たなオープンLLMを開発・公開しました**

# DBRXのご紹介

[DBRX](https://qiita.com/taka_yayoi/items/ea6293f8c72d6b1c4018)はDatabricksによる**オープンソースLLM**です。

- **DBRX Base** 事前トレーニング済みモデル 
    - スマートなオートコンプリートのように動作 - 何を言ったとしても続きを生成します。 
    - ご自身のデータでファインチューニングする際に有用です。

- **DBRX Instruct** ファインチューニングモデル
    - 質問回答や指示追従を行うように設計されています。
    - ドメイン固有のデータに対する追加トレーニング、指示追従のためのファインチューニングを行うことでDBRXをベースとして構築されています。

# 実機デモ

詳細に入る前にデモをさせてください。こちらはDatabricksで提供されているAI Playgroundというものでして、複数のLLMに対して同じプロンプトを投入して挙動を比較することができます。Llama 2と比較してみます。

<iframe width="560" height="315" src="https://www.youtube.com/embed/24CpWXFVO40?si=fRiUlT83HiVo9f7H" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

見てわかりますように非常に高速です。この理由は後で触れます。

# ベンチマーク

DBRXは言語理解(MMLU)、プログラミング(HumanEval)、数学(GSM8K)において、(発表時点で)有名なオープンソースモデルを上回っています。
![Screenshot 2024-04-27 at 18.32.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d20cb3df-9ac5-0a25-76e9-822590ae0158.png)

ベンチマークの詳細は[こちら](https://qiita.com/taka_yayoi/items/ea6293f8c72d6b1c4018)をご覧ください。

# DBRXアーキテクチャ

- DBRXは次トークン予測を用いてトレーニングされたデコーダーオンリーの[トランスフォーマーベース](https://www.isattentionallyouneed.com/)の大規模言語モデル(LLM)です。
    - DBRXはDatabricksにおいて**完全にゼロ**から構築されました。
- DBRXは公開オンラインデータソースを用いて事前トレーニングされました。 
    - DBRXのトレーニングには**顧客データは使用されていません**。注意深く選別された**12Tのトークン**でトレーニングしており、最大コンテキスト長は**32kトークン**です。
    - 我々は事前トレーニングにおいて、モデルの品質が劇的に改善されることを発見した方法で、データミックスを変更する**curriculum learning**を用いています。
- このモデルは**3072枚のNVIDIA H100**を用いて事前トレーニングされました。事前
トレーニング、事後トレーニング、評価、レッドチーム、改善を含め、**約3ヶ月**を要しました。
- **Fine-grained sparse mixture-of-experts (MoE)** モデルアーキテクチャ
    - MoEの特徴である”sparse”と対比して、標準的な非MoEモデルは時に”dense”モデルと呼ばれます。
- **132Bのパラメーター**および最大**32Kトークン**をサポート 
このモデルの合計パラメーター数は132Bですが、モデルのトレーニング、ファインチューニング、推論の実施の際には、どのような入力が与えられたとしても**36Bのみ**が使用されます。これが先ほどのデモでお見せしたように、レスポンスが高速な理由です。
- Dropless実装 
- このモデルは企業環境において企業によって利用されることを想定して設計されています。
- MixtralやGrokのような他のオープンMoEモデルと比較して、DBRXは**きめ細かい**です - より小規模な大量のエキスパートを使用します。
    - ネットワークの各レイヤーは16の”エキスパート”に分割されます。
    - それぞれの入力に対して、ネットワークは動的に4つのエキスパートを選択して利用します。すなわち、このネットワークは**16のエキスパートのうち4つのエキスパート**を利用します。
- DBRXでは[rotary position encodings](https://arxiv.org/abs/2104.09864) (RoPE)、[gated linear units](https://arxiv.org/pdf/1612.08083v3.pdf) (GLU)、[grouped query attention](https://arxiv.org/pdf/2305.13245.pdf) (GQA)を使用しています。
- [tiktoken](https://github.com/openai/tiktoken)リポジトリで提供されているGPT-4 tokenizerを使用しています。 
    - 徹底的な評価と大規模な実験をベースとしてこの選択を行いました。

# DBRXの構築方法

DBRXは[Databricks](https://www.databricks.com/jp)上で構築されました。これは、皆様自身でも自分のデータを用いてDBRX相当のLLMを構築できるということを意味します。また、以下のオープンソースライブラリを活用しています。

- [LLM Foundry](https://github.com/mosaicml/llm-foundry)
- [Composer](https://github.com/mosaicml/composer)
- [Streaming](https://github.com/mosaicml/streaming)
- [Eval Gauntlet](https://github.com/mosaicml/llm-foundry/blob/main/scripts/eval/local_data/EVAL_GAUNTLET.md)

![Screenshot 2024-04-27 at 18.38.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bce58323-8870-ff15-50ec-505e19fcde16.png)

Databricksが提供する[Apache Spark](https://www.databricks.com/jp/spark/about)、[Unity Catalog](https://docs.databricks.com/ja/data-governance/unity-catalog/index.html)、[MLflow](https://www.databricks.com/jp/product/managed-mlflow)、[Lakeview](https://www.databricks.com/jp/blog/announcing-general-availability-next-generation-lakeview-dashboards)なども活用しています。

![Screenshot 2024-04-27 at 18.39.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bd69f20a-d85e-12de-592d-a47dc1f110d8.png)

# どうやってDBRXを試す？

- Hugging Face Databricks Space 
    - https://huggingface.co/spaces/databricks/dbrx-instruct
    - https://huggingface.co/databricks/dbrx-base
    - https://huggingface.co/databricks/dbrx-instruct
- Databricks AI PlaygroundやFoundation Model API
- DBRX GitHub 
    - https://github.com/databricks/dbrx

# 生成AIに対するDatabricksのスタンス - モデルニュートラル

## DBRXのサマリー

- DBRXはオープンソースLLMの**新記録を樹立**し、プロプライエタリ(クローズドソース)LLMと同等、比類するものとなっています。 
- 合計132Bのパラメーターを持つFine-grained sparse mixture-of-experts (MoE) モデルアーキテクチャ  
- **Mosaic Research**、**Databricks**、**AIコミュニティ**のテクノロジーによって構築されました。  
- DBRXはMoEアーキテクチャ、優れたデータ、GPT-4 tokenizer によって優れたトレーニング効率性を有しています。
- DBRXは、**SQLのようなアプリケーション**のように我々のGenAI-powered製品にすでに組み込まれています。早期のロールアウトではGPT-3.5を上回っており、GPT-4に迫るものとなっています。
- また、**RAGタスク**においてもオープンモデルやGPT-3.5を上回るモデルとなっています。

## モデルニュートラルが大切です

- しかし、**DBRXも数多くのLLMの一つに過ぎません。**
- DBRX発表後も、Meta Llama 3やSnowflake Arcticなど優れたLLMが発表され
続けていますし、今後もこの流れは継続していきます。
    - [DatabricksではMeta Llama 3をサポート](https://www.databricks.com/jp/blog/building-enterprise-genai-apps-meta-llama-3-databricks)しており、直接利用できるようになっています。
- Meta Llama 3、DBRX、Azure OpenAIなどのLLMは**お客様の要件に基づいて適切に選択**することが重要です。
- Databricksは**モデルニュートラル**が重要であると考えており、Databricksが様々なモデルの開発、運用、監視のためのプラットフォームであり続けます。
- DBRXのような高品質なLLMが**Databricksプラットフォームで構築できる**ということをお伝えしたかったのです。
- DollyやDBRXなどを通じて、昨年から続いているLLM普及の一助になりたいと考えています。

# 懇親会

LLMの今後についての話になったので、こちらのCompound AI Systemについて触れさせていただきました。

https://qiita.com/taka_yayoi/items/287ad22441d6abc7e07e

https://xtech.nikkei.com/atcl/nxt/column/18/00692/041700130/

https://qiita.com/taka_yayoi/items/a6a8cd0329e412f4d6ee

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

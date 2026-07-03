---
title: DatabricksにおけるLLMを使用したメールカスタマーサポートの解決時間の短縮
tags:
  - Databricks
  - LangChain
  - LLM
private: false
updated_at: '2024-11-27T11:54:19+09:00'
id: 7509efdd6d1d5cf1befc
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらのソリューションアクセラレータを日本語対応しながらウォークスルーします。

https://github.com/databricks-industry-solutions/Email-Customer-Support

こちらの内容と類似していますが、以下の記事では[AI関数](https://docs.databricks.com/ja/large-language-models/ai-functions.html)を使っていますが、上のアクセラレータはLangChainによるパイプラインを活用している点が異なります。

https://qiita.com/taka_yayoi/items/251c60f63c8d73a244f2

# 0_Introduction

## LLMを使用したメールカスタマーサポートの解決時間短縮

このノートブックの目的は、メールを通じたカスタマーサポートの自動化を紹介することです。メール応答プロセスを自動化するために、大規模言語モデル（LLM）を使用します。

このソリューションアクセラレータには、DBR-LTS-ML-14.3クラスターの使用をお勧めします。

## はじめに
組織はしばしばメールチャネルを通じてカスタマーサポートの問い合わせを受け取ります。これらのメールは、組織や規制当局によって設定されたサービスレベルアグリーメント（SLA）を遵守する必要があり、SLAを満たさない場合にはペナルティが課され、超過した場合には報酬が与えられます。顧客の問い合わせに迅速かつ効果的に対応することは、顧客体験を向上させます。しかし、多くの組織は受信するメールの量が多く、対応するスタッフのリソースが限られているため、SLAを満たすのに苦労しています。

このソリューションアクセラレータは、メール応答プロセスを自動化するために大規模言語モデル（LLM）を使用することを提案します。これには以下の主要な活動が含まれます：
<img src="https://github.com/databricks-industry-solutions/Email-Customer-Support/blob/042c3642c5593ca53494b131639eb81a184352f5/images/EmailAutomation%20-%20Page%201.png?raw=true" width=100%>
1. カテゴリ分け: 最初のステップは、顧客のリクエストと緊急性を理解し、関連するSLAを含め、適切な対応方法を決定するためにメールをカテゴリ分けすることです。メールは、製品に関する問い合わせ、特定のジョブリクエスト、または応答が不要な一般的なメールとして分類できます。
2. 感情分析: メールの感情（ポジティブ、中立、ネガティブ）を分析します。
3. 要約: メールの内容を迅速に理解するために、カスタマーサポートの専門家がメール全体を読むことなく内容を把握できるように要約を作成します。
4. 自動メール応答: メールのカテゴリ、感情、分析に基づいて、自動的に顧客へのメール応答を生成します。

理想的には、これはエンドツーエンドの自動化ではなく、人間が関与するソリューションであるべきです。このアプローチでは、サポートコンサルタントのメールボックスが上記の機能でほぼリアルタイムに更新され、推奨されるメール応答を修正する機能が提供されます。

このソリューションの一環として、Databricks Data Intelligence Platform上でソリューションを展開するための2つのアプローチを提示します：
1. プロプライエタリSaaS LLM: 一つのアプローチは、Databricks Data IntelligenceプラットフォームからプロプライエタリSaaS LLMのAPIを呼び出すことです。これは、モデルをゼロからトレーニングする必要がないため便利です。代わりに、事前トレーニングされたモデルを使用してメールを分類およびカテゴリ分けできます。
2. オープンLLM: もう一つのアプローチは、メールには外部に共有できない機密情報が含まれている可能性があるため、組織のインフラストラクチャ内でソリューションを展開することです。これは、DBRX、LLAMA、Mosaic、Mixtralなどの既存のオープンLLMモデルを使用して達成できます。これらのモデルの微調整は、Databricks Mosaicモデルを使用して行うことができます。このオプションは、インフラストラクチャに対するより多くの制御を提供し、コストを削減することもできます。

## ソリューション設計/アーキテクチャ

このセクションでは、このソリューションのアーキテクチャの概要を提供します。
<img src="https://github.com/databricks-industry-solutions/Email-Customer-Support/blob/main/images/EmailAutomation-Architetcure.png?raw=true" width=100%>

- データ取り込み: カスタマーサポートのメールは、Microsoft OutlookやGMailなどの一般的なメールクライアントで受信されます。メールクライアントからDatabricks Deltaテーブルにデータを取り込むためのソリューションは複数あります。一般的に使用されるソリューションの一部には、Azure LogicAppsやAWS Step Functionsがあります。
- モデル提供: Databricks Model Servingは、すべてのクラウドおよびプロバイダーでモデルを実験、カスタマイズ、プロダクション化するための統一インターフェースを提供します。これにより、ユースケースに最適なモデルを使用して高品質なGenAIアプリを作成し、組織の独自データを安全に活用できます。Databricks Model Servingは、外部モデル、基盤モデル、カスタムモデルのいずれもサポートします。このソリューションでは、OpenAIのようなプロプライエタリモデルやMistralのような基盤モデルのための外部モデルインターフェースを実装しています。
- メールの更新: メールはLLMによって強化され、カテゴリ、感情、要約を含む自動応答がカスタマーサポートアプリケーションの受信トレイに送信されます。

# _resources/00-setup

こちらで各種設定を行います。カタログ名などを定義します。

```py
config['catalog'] = 'takaakiyayoi_catalog'
config['schema'] = 'email_llm'
config['volume'] = 'source_data'
config['vol_data_landing'] = f"/Volumes/{config['catalog']}/{config['schema']}/{config['volume']}"
config['table_emails_bronze'] = 'emails_bronze'
config['table_emails_silver_foundationalm'] = 'emails_foundational_silver'
config['table_emails_silver_externalm'] = 'emails_externalm_silver'
config['table_emails_silver'] = 'emails_silver'
```

Open APIキーを使用するので、事前に[シークレット](https://docs.databricks.com/ja/security/secrets/index.html)にAPIキーを格納しておき、参照するように設定します。

```py
config['openai_api_key']=dbutils.secrets.get(scope = "demo-token-takaaki.yayoi", key = "openai_api_key")
```


# 1_Ingest_Emails_Into_Lakehouse

## カスタマーサポートのメールをブロンズDeltaテーブルに取り込む

カスタマーサポートのメールアプリケーションはDatabricksプラットフォームと統合されています。Azure LogicAppsなどのコンポーネントはデータを<a href="https://docs.databricks.com/ja/connect/unity-catalog/volumes.html" target="_blank">Databricks Volumes</a>にドロップするか、直接Bronze Deltaテーブルに取り込みます。このノートブックでは、生のメールがVolumeにドロップされ、Autoloaderを使用してデータをBronze Deltaテーブルに取り込むことを前提としています。

このソリューションで使用されるデータは、電力供給業者がビジネス顧客から受け取る実際のメールに基づいて手動で生成された偽のメールです。

Autoloaderを使用しているため、このソリューションはバッチ処理またはストリーム処理のいずれかを使用して実装できます。

:::note info
**注意**
こちらのノートブックを実行すると、`emails_bronze`というテーブルが作成されます。こちらは英語なので、次のステップで日本語に翻訳します。

![Screenshot 2024-11-27 at 11.09.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ecb995b5-47e1-aee8-8369-6fc12aae2333.png)
:::

# ブロンズテーブルの翻訳

以下のクエリーを実行して、翻訳されたデータを格納する`emails_bronze_ja`テーブルを作成します。

```sql
CREATE TABLE takaakiyayoi_catalog.email_llm.emails_bronze_ja
AS SELECT
  ai_translate(email_subject, "ja") as email_subject,
  message_id,
  cc,
  from,
  received_time,
  reply_to,
  email_folder,
  email_attachment_names,
  ai_translate(email_body_clean, "ja") as email_body_clean
FROM
  emails_bronze
```

以降のステップで、このテーブルを参照するように`_resources/00-setup`を修正します。

```py
config['catalog'] = 'takaakiyayoi_catalog'
config['schema'] = 'email_llm'
config['volume'] = 'source_data'
config['vol_data_landing'] = f"/Volumes/{config['catalog']}/{config['schema']}/{config['volume']}"
config['table_emails_bronze'] = 'emails_bronze_ja'
config['table_emails_silver_foundationalm'] = 'emails_foundational_silver'
config['table_emails_silver_externalm'] = 'emails_externalm_silver'
config['table_emails_silver'] = 'emails_silver'
```

# 2a_Configure_External_models_for_Automation

## メール応答自動化のための外部モデルの設定

*前提条件: このノートブックを実行する前に 1_Ingest_Emails_Into_Lakehouse を実行してください。*

このノートブックでは、外部モデル - OpenAI のエンドポイントを作成し、Langchain を設定してプロンプトテンプレートを定義します。Langchain ベースのプロンプトを使用して、メールの1つをテストしています。<a href="https://docs.databricks.com/ja/generative-ai/external-models/index.html" target="_blank">外部モデル</a>は、Databricks の外部にホストされているサードパーティモデルです。モデルサービングによってサポートされる外部モデルは、OpenAI や Anthropic などのさまざまな大規模言語モデル（LLM）プロバイダーの使用と管理を組織内で簡素化することができます。この特定の問題については、OpenAI を選択しました。

このノートブックの主なハイライト:
- このノートブックには最新の機械学習DBRを使用
- このノートブックで作成されたエンドポイントは、モデルサービングのために次のノートブックで使用されます
- エンドポイントは、Databricks ペインのサービングセクションの UI を使用して表示および検証できます

OpenAI API キーを安全に保存するために Databricks シークレットを使用し、ここでエンドポイントを定義するために取得しています。API トークンをノートブックに保存しないことを強くお勧めします。Databricks 内でシークレットを設定する手順は <a href="https://docs.databricks.com/ja/security/secrets/index.html" target="_blank">こちら</a> で確認できます。

```py
%run ./_resources/00-setup
```

## ブロンズレイヤーからメールを読み取る

ブロンズレイヤーに保存された生のメールをデータフレームで読み取りましょう。

```py
emails_silver = spark.read.table(config["table_emails_bronze"])
```

## ソリューションのためのOpenAI Completionエンドポイントを作成する

使用するモデルとAPIキーを格納したシークレットを指定して、エンドポイントを作成します。

```py
import mlflow.deployments

client = mlflow.deployments.get_deploy_client("databricks")
client.create_endpoint(
    name="Email-OpenAI-Completion-Endpoint",
    config={
        "served_entities": [{
            "external_model": {
                "name": "gpt-3.5-turbo-instruct",
                "provider": "openai",
                "task": "llm/v1/completions",
                "openai_config": {
                    "openai_api_key": "{{secrets/demo-token-takaaki.yayoi/openai_api_key}}",
                }
            }
        }]
    }
)
```

上のコマンドを実行することで、モデルサービングエンドポイントが作成されます。

![Screenshot 2024-11-27 at 11.14.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e1c575cb-ae8b-5605-d178-d2d055f1bea1.png)

動作確認します。

![Screenshot 2024-11-27 at 11.22.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/65289d7a-18db-580c-2da4-d87abdf09f35.png)

## 外部モデルのためのLangchainのセットアップ

Langchainをセットアップして、メールのカテゴリ、感情、要約、および下書きのテンプレートを定義します。

下書きのテンプレートはテンプレートに基づいて作成することができ、エンべディングも使用できます。ただし、このソリューションではそれを定義していません。

```py
import mlflow
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Databricks

# OpenAIゲートウェイを定義
gateway = Databricks(
    host="https://" + spark.conf.get("spark.databricks.workspaceUrl"), 
    endpoint_name="Email-OpenAI-Completion-Endpoint",
    temperature=0.1,
    max_tokens=1000,
)

# プロンプトテンプレートを作成
template = """
次のメールテキストを考慮して、メールが求人依頼、顧客問い合わせ、またはアクション不要の一般的なメールのいずれかを分類します。また、メールの感情をポジティブ、ネガティブ、またはニュートラルとしてキャプチャする必要があります。さらに、メールの短い要約を作成する必要があります。加えて、元のメールに返信するためのドラフトを作成します。

出力は辞書のJSON形式で構造化されるべきです。最初の属性名は「Category」で、メールを3つの可能な値（Job、Query、No Action）として分類します。2番目のJSON属性名は「Sentiment」で、可能な値はポジティブ、ネガティブ、またはニュートラルです。3番目のJSON属性名は「Synopsis」で、短いメールの要約をキャプチャする必要があります。4番目のJSON属性名「Reply」は、元のメールへのドラフト返信です。

メールの要約はここから始まります。JSON以外のテキストは回答しないでください: {email_body}
"""

prompt = PromptTemplate(template=template, input_variables=["email_body"])

# LLMチェーンを構築
llm_chain = LLMChain(prompt=prompt, llm=gateway)
```

## OpenAI APIでメールのテスト

エンドポイントをDatabricksのサービングパイプラインの一部として呼び出す前に、以下のようにメールの1つをテストできます:

```py
# テスト用の単一のレビューを取得
test_single_review = emails_silver.limit(1).select("email_body_clean").collect()[0][0]

# 予測を実行
response_string = llm_chain.run(test_single_review)

# 結果を表示
display(response_string)
```

解答例が生成されています。

```
'\n{\n    "Category": "Job",\n    "Sentiment": "Neutral",\n    "Synopsis": "12341111の仕事のハンドオーバーについての確認",\n    "Reply": "こんにちはメアリーさん、ありがとうございます。申請者の詳細とハンドオーバーの理由を確認し、リンクを参照して作業を進めます。よろしくお願いします。トム"\n}'
```

トレースも表示されます。

![Screenshot 2024-11-27 at 11.25.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1e4851f2-9092-6ea6-ebd8-f16575bd8b29.png)

# 3a_Serve_External_models_for_Automation

## 外部モデルを使用したメール応答の自動化

*前提条件: このノートブックを実行する前に、1_Ingest_Emails_Into_Lakehouse と 2a_Configure_External_models_for_Automation を実行してください。*

このノートブックでは、ノートブック 2a で作成された外部モデルエンドポイントを参照し、Langchain を設定してメール自動化のユースケースに外部モデルを提供します。

このノートブックの主なハイライト:
- 前のノートブックで作成されたエンドポイントをここで使用
- このノートブックではモデル提供に UDF を使用。低レイテンシー要件の場合、API ベースのオプションも利用可能。

```py
%run ./_resources/00-setup
```

## ブロンズレイヤーからメールを読み取る

ブロンズレイヤーに保存された生のメールをデータフレームで読み取りましょう。

```py
emails_silver = spark.read.table(config["table_emails_bronze"])
```

## 外部モデルのためのLangchainのセットアップ

Langchainを設定して、メールのカテゴリ、感情、要約、および可能な返信を取得するためのプロンプトテンプレートを定義します。

可能な返信はテンプレートに基づいており、埋め込みを使用することができます。しかし、このソリューションではそれを定義することはできません。

## メール要約UDFの作成

```py
import mlflow
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Databricks
from langchain import OpenAI, PromptTemplate, LLMChain
from pyspark.sql import functions as SF
from pyspark.sql.types import StringType
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain.chat_models import ChatDatabricks
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from tenacity import retry, stop_after_attempt, wait_exponential
import os

spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch",2)
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
url = spark.conf.get("spark.databricks.workspaceUrl")

# サマリー関数を作成
def run_summarisation_pipeline(email_body):

    os.environ['DATABRICKS_TOKEN'] = token
    
    # Chat GPT LLMモデル
    gateway = Databricks(
    host="https://" + url, 
    endpoint_name="Email-OpenAI-Completion-Endpoint",
    max_tokens=1000,
    )

    # プロンプトテンプレートを作成
    prompt_template_string = """
    次のメールテキストを考慮して、メールが求人依頼、顧客問い合わせ、またはアクション不要の一般的なメールのいずれかを分類します。メールの感情をポジティブ、ネガティブ、または中立としてキャプチャする必要があります。また、メールの短い要約を作成する必要があります。さらに、元のメールへの返信案を作成する必要があります。

    出力は辞書のJSON形式で構造化されるべきです。最初の属性名は「Category」で、メールを3つの可能な値（Job、Query、No Action）として分類します。2番目のJSON属性名は「Sentiment」で、可能な値はポジティブ、ネガティブ、または中立です。3番目のJSON属性名は「Synopsis」で、短いメールの要約をキャプチャする必要があります。4番目のJSON属性名「Reply」は、元のメールへの可能な返信です。

    メールの要約はここから始まります。JSON以外の回答や他のテキストは与えないでください: {email_body}"""

    prompt_template = PromptTemplate(template=prompt_template_string, input_variables=["email_body"])

    # LLMチェーンを作成
    chain = LLMChain(prompt=prompt_template, llm=gateway)

    @retry(wait=wait_exponential(multiplier=10, min=10, max=1800), stop=stop_after_attempt(7))
    def _call_with_retry(email_body):
        return chain.run(email_body)

    try:
        summary_string = _call_with_retry(email_body)
    except Exception as e:
        summary_string = f"FAILED: {e.last_attempt.exception()}"

    return summary_string

# UDFを作成
summarisation_udf = SF.udf(
    lambda x: run_summarisation_pipeline(
        email_body=x
    ),
    StringType(),
)
```

## 受信データの処理

```py
# 並行処理のために再分割
emails_silver = emails_silver.repartition(10)

# リクエストを実行
emails_silver_with_summary = (
    emails_silver
    .withColumn("summary_string", summarisation_udf(SF.col("email_body_clean")))
)

# テーブルを保存
(
    emails_silver_with_summary
    .write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(config['table_emails_silver_externalm'])
)
```

## 処理結果の確認

```py
display(spark.sql("SELECT * FROM "+ config['table_emails_silver_externalm']+ " LIMIT 10"))
```
![Screenshot 2024-11-27 at 11.29.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7dfe7f86-a4f0-e42e-7c0b-9f64b5344b6d.png)

見にくいので、クエリーを変更します。

```sql
SELECT
  email_body_clean,
  from_json(
    summary_string,
    "Category String, Sentiment String, Synopsis String, Reply String"
  )
FROM
  takaakiyayoi_catalog.email_llm.emails_externalm_silver
```

一部、JSONの出力に失敗しているものもありますが、モデルやプロンプトの工夫の余地がまだあるということですかね。

![Screenshot 2024-11-27 at 11.52.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3e8c5289-0547-7549-67cc-59a4cc93908e.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

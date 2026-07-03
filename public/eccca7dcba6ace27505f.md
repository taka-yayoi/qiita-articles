---
title: '洞察の解放: Databricks AI関数を用いた品質と信頼性のベストプラクティス'
tags:
  - Databricks
  - MLflow
private: false
updated_at: '2025-08-29T10:54:09+09:00'
id: eccca7dcba6ace27505f
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Unlocking Insights: Best Practices for Quality and Reliability with Databricks AI Functions \| by AI on Databricks \| Aug, 2025 \| Medium](https://medium.com/@AI-on-Databricks/unlocking-insights-best-practices-for-quality-and-reliability-with-databricks-ai-functions-42e4e430f800) の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*iHtjxc92J8zhPIBAvFJ0Ew.png)

著者: [Colton Peltier](https://www.linkedin.com/in/coltonpeltier/) (Staff Data Scientist @ Databricks), [Qian Yu](https://www.linkedin.com/in/qyupublic/) (Specialist Solutions Architect @ Databricks)

# イントロダクション

現在のデータドリブンの世界においては驚くべきことに企業データの90%が構造化されていません。これには、顧客レビュー、サポートチケット、文書から画像、動画ファイルに至る全てが含まれています。従来のデータツールは構造化データ(行と列)に長けていますが、非構造化情報の広大な海から価値のある洞察を抽出する際には大きな課題に直面します。DatabricksのAI関数はこのギャップを埋めるために設計されており、SQLやETLワークフローの中で直接、非構造化データをアクション可能なインテリジェンスに変換することができます。しかし、これらのパワフルなAI能力によって生成される洞察の品質や信頼性をどのように担保したらいいのでしょうか？いくつかのベストプラクティスを見ていきましょう。

以下のステップを通じて進めていきます:

1. あなたのタスクに適したAI関数の選択
1. タスクのパフォーマンスの評価
1. AI関数の設定を調整することによるパフォーマンスの改善
1. Lakeflowで本格運用へ

# あなたのニーズに合わせたAI関数のタイプの理解

Databricksでは、それぞれが異なるレベルのコントロールと複雑性を持つ、3つの主要なタイプのAI関数を提供しています:

- [タスク固有の関数](https://docs.databricks.com/aws/ja/large-language-models/ai-functions): これには、ai_summary()、ai_mask()、ai_sentiment()、ai_extract()のような関数が含まれています。これらは、個々のタスクを極めてうまく実施し、直感的なデータタイプを返却し、多くの場合追加のロジックなしに構造化されるようにDatabricksによってチューニングされています。主要なメリットには、Databricksエンジニアリングチームによって継続的に背後のモデルがアップデートされるので、常にベストなパフォーマンスを得られるというものがあります。
- [ai_query()関数](https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_query): これは、より大きなコントロールを可能とする、さらに汎用的な関数です。ai_queryによって以下が可能となります:
    - 使いたいモデルエンドポイントの指定。現在、ai_queryはLLM、古典的なMLモデル、カスタムエージェントをサポートしています。
    - さまざまなモデルを用いた実験。
    - 出力をカスタマイズするためにカスタムのプロンプトを記述。
    -  temperatureやmax_tokensのような追加のパラメータの設定。
    この関数は多言語タスクやAIの挙動に対してきめ細かいコントロールを必要とする際には重要となります。
- [Agent Bricks](https://docs.databricks.com/aws/ja/generative-ai/agent-bricks/): 企業がドメイン固有のエージェントを開発するための新たな手段を提供します。ローコード環境において、チームは自身のエージェントの目的を定義し、自然言語のフィードバックを通じて品質に対する戦略的なガイドを提供することができます。

    - Databricksはエージェントを作成、デプロイし、自動評価や最適化をバックエンドでおこないます。さらに、コスト最適化、品質最適化のモデルの選択肢を提供します。
    - エージェントエンドポイントはai_query()でクエリーすることができます。
    - ai_queryのバッチ推論でサポートされるユースケースには、情報抽出とカスタムLLMがあります。

典型的なデータ処理や分析タスクでは、あなたの要件に直接マッチする場合にはタスク固有のAI関数からスタートしましょう。多言語サポートやカスタムプロンプト、モデル選択のようによりカスタマイズが必要なアプリケーションの場合にはai_query()を活用しましょう。これらのAI関数のパフォーマンスを評価する際には、次のセクションで探索するトピックであるMLflowの活用をお勧めします。

あなたのデータパイプラインにおけるコストとパフォーマンスにおける自動評価、最適化、柔軟なトレードオフが必要であれば、Agent Bricksの活用を検討しましょう。

# AI関数のパフォーマンス評価

AI関数のパフォーマンスを評価することは重要です。推測しないで計測しましょう！従来の機械学習のように、あなたのAIの生成したアウトプットのパフォーマンス評価は重要です。大規模に品質を評価するにはメトリック、正解データが必要となります。[MLflow](https://mlflow.org/)はメトリクスの記録やラン(トレーニング実行)の追跡のためのパワフルなツールです。

## 例1. ai_summary()の評価

要約: 一般的なメトリックは、生成テキストとオリジナルのテキスト間で最長で共通するトークンのサブシーケンスを比較するROUGE-Lです。これによって、要約が情報をどれだけ適切に抽出しつつも秩序を保っているかを評価する助けとなります。

こちらがai_summary()のクエリーです。

```sql
CREATE OR REPLACE TEMPORARY VIEW session_summaries AS
SELECT 
  session_desc, 
  ai_summarize(session_desc) as summary 
FROM dais_sessions
```

MLflow 3.0で評価を実行するには、ROUGE-Lスコアラーを定義するmlflow.genai.scorersのscorerデコレーターを定義し、ai_summaryのパフォーマンスを評価するためにmlflow.genai.evaluate()とスコアラーを使用します。

```py
from rouge_score import rouge_scorer
from mlflow.genai.scorers import scorer
from typing import Optional, Any
from mlflow.entities import Feedback


# Create a mlflow 3 eval data structure from a pandas dataframe
evaluation_set = spark.sql("SELECT * FROM session_summaries").toPandas()
eval_data = [
    {
        "inputs": {"session_desc": row["session_desc"]},
        "outputs": {"summary": row["summary"]}
    }
    for _, row in evaluation_set.iterrows()
]

@scorer(aggregations=["mean", "variance"])
def rougeL_scorer(
  inputs: Optional[dict[str, Any]],
  outputs: Optional[Any],):
    candidate = outputs.get("summary", "")
    reference = inputs.get("session_desc", "")
    scorer_ = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer_.score(reference, candidate)
    return scores['rouge1'].fmeasure

# Evaluate with the ROUGEL score
results = mlflow.genai.evaluate(
      data=eval_data,
      predict_fn=None,
      scorers=[rougeL_scorer],
  )
```

MLflow Trace UIによって、評価トレースが自動的にキャプチャされます。

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*WJ7Ph0Zj8Mcu6uUARDDCmg.png)

「View evaluation results」をクリックすることで、詳細な[エクスペリメントの評価](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/evaluate-app#%E3%82%B9%E3%83%86%E3%83%83%E3%83%97-5-%E7%B5%90%E6%9E%9C%E3%81%AE%E8%A1%A8%E7%A4%BA%E3%81%A8%E8%A7%A3%E9%87%88)ビューに移動します。トレースタブでは、集計されたパフォーマンスを確認したり、個々のサンプルにドリルダウンすることができます。

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Dxn5fx-RtmgWyuHhTUDPnQ.png)

## 例2. カスタムメトリクスによるai_query()の評価

標準的なメトリクスでの定量化が困難なより抽象的なコンセプト(LLMによって生成されたタイトルのキャッチーさなど)においては、プロンプトを用いたカスタムメトリクスを定義することができます。

```py
from mlflow.genai.judges import custom_prompt_judge
from typing import List, Dict, Any, cast

title_catchiness_prompt = """
Title Catchiness is a measure of how catchy a title is for the Data and AI Summit
Rate the catchness of title using:
  - Emotional appeal
  - Curiosity spark
  - Memorability
  - Brevity

Rubric:
[[Not_catchy]]: score 0, the title is not catchy for the Data and AI Summit event
[[Pretty_catchy]]: score 1, the title is pretty catchy for the Data and AI Summit event
[[Very_catchy]]: score 2, the title is very catchy for the Data and AI Summit event

Title: {{title}}
"""
```

MLflow 3.0は、数式やカテゴリー定義によってカスタムメトリックを定義できる**custom_prompt_judge**という関数が提供されており、LLMがあなたの評価指標に対してアウトプットをスコアリングするための「ジャッジ」として動作します。この例では、感情的アピールと好奇心を掻き立てるものとして「キャッチーさ(catchiness)」を定義しており、タイトルをLLMに大規模にレーティングさせています。**Custom_prompt_judge**は**scorer**の**judge**引数に渡すことができます。

```py
eval_data = [
    {
        "inputs": {"session_desc": row["session_desc"]},
        "outputs": {"generated_title": row["generated_title"]}
    }
    for _, row in loaded_complete.iterrows()
]

@scorer(aggregations=["mean", "variance"])
def title_catchiness(inputs: Dict[Any, Any], outputs: Dict[Any, Any]):
    title = outputs.get("generated_title", "")
    judge = custom_prompt_judge(
        name="title_catchiness",
        prompt_template=title_catchiness_prompt,
        numeric_values={"Not_catchy": 0.0, "Pretty_catchy": 1.0, "Very_catchy": 2.0}
    )
    return judge(title=title)

with mlflow.start_run() as run: # Create a new mlflow run
  results = mlflow.genai.evaluate(
    data = eval_data,
    predict_fn=None,
    scorers=[title_catchiness],
  )
  # Calculate and log the metrics
  mlflow.log_metrics( 
    results.metrics
  )
```

ここでも、MLflowのエクスペリメントビューでトレースが自動的にキャプチャされます。

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*GtUzm9Ig53q58ujwjG5uEw.png)

MLflowを用いて、AI関数のアウトプットをシステマティックに評価することで、より高い品質の結果を達成するために、プロンプトや関数の選択肢を試行錯誤して改善を行うことができます。

# 信頼できるアウトプットの達成: 基礎的なプロンプトの先へ

特に本番環境において、AI関数が信頼でき利用できるデータを生成するようにするためには以下の高度なテクニックを検討しましょう:

- JSONスキーマによるアウトプットの構造化: LLMは「話す」のが大好きであり、多くの場合会話の繋ぎを追加したして、期待するアウトプットのフォーマッティングに整合性がなくなります。これに対応するために、ai_queryではJSONスキーマを指定することができます。([ドキュンメント](https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_query#enforce-output-schema-with-structured-output)をご覧ください)これによって構造化されたアウトプットが強制され、予測可能でパースが容易なデータを受け取れるようになります。これは、2値分類やさまざまなデータタイプの抽出(名前は文字列、ページ数は数値など)のようなタスクでは特に有用です。複雑なスキーマを活用することもできますが、通常は平坦な構造で優れた結果を得ることができます。

以下の例では、構造化アウトプットを得るためにai_query関数のresponseFormatパラメータにJSONスキーマを指定しています。

```sql
CREATE OR REPLACE TEMPORARY VIEW generated_titles_keywords AS
SELECT 
  session_desc,
  ai_query(
    "databricks-meta-llama-3-3-70b-instruct",
    "Given a description of a DAIS 2025 session, generate an catchy talk title and choose 3 keywords: " || session_desc,
    responseFormat => '{
      "type": "json_schema",
      "json_schema": {
        "name": "research_paper_extraction",
        "schema": {
          "type": "object",
          "properties": {
            "generated_title": {"type": "string"},
            "keyword_1": {"type": "string"},
            "keyword_2": {"type": "string"},
            "keyword_3": {"type": "string"}
          }
      },
      "strict": true
    }
  }'
) as extracted_info
FROM dais_sessions
```

指定されたJSONスキーマに基づいてアウトプットが適切にフォーマットされます。

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*INapZi-QkXsMXU4Zljx6Pg.png)

- モデルの推論: 複雑なタスクにおいては、ai_queryでサポートされる幾つかものモデル(Claude 3.7 Sonnetなど)では推論能力を提供しています。これによって、最終的なアウトプットを生成する前に、LLMが一定期間「考えて」から情報を処理するようになり、多くの場合、精度の改善につながります。budget_tokensやmax_tokensのようなパラメータを用いることで、この推論フェーズの期間をコントロールすることができます。パワフルではありますが、推論はより多くのトークンを消費し、レイテンシーとコストを増加させるので、期待した結果を達成するのに苦戦するタスクに温存しておくことがベストと言えます。

以下の例では、modelParametersを用いてai_queryを呼び出す際の「思考」予算の追加方法を示しています。

```sql
CREATE OR REPLACE TEMPORARY VIEW session_summaries_data_engineer_reasoning AS
SELECT  
session_desc,
ai_query(
    "databricks-claude-3-7-sonnet",
    """Rewrite the following abstract to appeal to Data Engineers. Abstract: """ || session_desc,
    modelParameters =>
      named_struct(
        "max_tokens", 1025, 
        "thinking", named_struct(
          "type", "enabled", 
          "budget_tokens", 1024
        ),
        "temperature", 0.0
      )) as tailored_abstract
FROM dais_sessions
```

# LakeflowによるAI関数の本格運用化

品質と信頼性の観点であなたのAI関数を洗練したら、[Lakeflow](https://www.databricks.com/jp/company/newsroom/press-releases/introducing-databricks-lakeflow-unified-intelligent-solution-data)がこれらの機能を本格運用に持ち込む助けとなります。これによって以下が可能となります:

- **データの取り込み:** さまざまなソースから構造化、非構造化データの両方をレイクハウスに持ち込みます。
- **AI関数によるデータの変換:** あなたのSQL、Pythonの変換ロジックに直接、ai_query、ai_summary、ai_sentimentや他のAI関数を直接インテグレーションします。
- **大規模なジョブの実行:** インクリメンタル処理、ストリーミング/バッチモード、ビルトインの品質チェック、CI/CD、可観測性、リネージのようなLakeflowの機能のメリットを享受します。
- **本番運用ジョブの監視:** スケーラビリティを保証し、データやAIに対する要件を満足するために、Lakeflowに組み込まれているモニタリング、アラートの機能を活用します。

このインテグレーションは、生成AI ETLのために個別のツールを必要としないことを意味します。あなたの既存のデータパイプラインに直接AIを埋め込み、非構造化データをダッシュボードやビジネス用とのための構造化され、信頼でき、補強されたデータに変換することができます。

# まとめ

DatabricksのAI関数は、非構造化、マルチモーダルデータの処理に対して大きなメリットを提供します。これらの関数は、SQLやPythonのような馴染みのあるツールとのインテグレーションを促進し、データエンジニアやデータアナリストのように、AI専門家以外のプロフェッショナルへの導入を可能とします。AIを活用した洞察、特に大規模なバッチ推論の最高の品質と信頼性を確実なものとするためには、さまざまな関数のタイプを理解し、メトリクスとMLflowを用いてパフォーマンスを包括的に分析し、構造化されたアウトプットを保証し、複雑なタスクではモデルの推論を活用することが重要となります。このアプローチによって、データの活用とインパクトを最大化します。

ここでカバーされているマテリアルに関して質問がある場合には、Databricksアカンウトチームにぜひご連絡ください。このチュートリアルで使用された完全なノートブックは[こちら](https://github.com/qian-yu-db/databricks-AI-Functions/blob/main/ai_function_evaluation/ai_functions_eval_mlflow3.ipynb)にあります。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

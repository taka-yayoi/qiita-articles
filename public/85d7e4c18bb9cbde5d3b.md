---
title: MLflowでDatabricks Genieスペースを評価・改善する — トレーシングからLLMジャッジ、自動改善案生成まで
tags:
  - Databricks
  - MLflow
  - 生成AI
  - LLM
  - LLMOps
private: false
updated_at: '2026-05-30T08:29:05+09:00'
id: 85d7e4c18bb9cbde5d3b
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

Databrick Genieスペースは、ビジネスユーザーが自然言語でデータに質問できるtext-to-SQLのAIアシスタントです。Unity Catalogのテーブル群に対して、テキスト指示やSQL式、ベンチマークを設定しておくことで、Genieが質問をSQLに翻訳して回答します。

便利な一方で、運用していると「どの会話がうまくいかなかったのか」「なぜ間違えたのか」が見えにくいという課題があります。Genieスペースの品質を継続的に改善するには、会話を記録し、評価し、改善案を得るというサイクルが必要です。

本記事では、MLflowの公式Cookbook [Evaluating Databricks Genie Spaces](https://mlflow.org/cookbook/databricks-genie/) の一連の流れを、実際にDatabricksノートブックで実行した内容(日本語化したもの)をベースに解説します。具体的には次の3ステップを通しで実装します。

![fig1_pipeline_overview.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e662897c-6fbe-439c-b469-fcb702501d02.png)

1. トレーシング: Genieの会話を取得してMLflowトレースとして記録する
2. 評価: 組み込み/カスタムのLLMジャッジでトレースを採点し、品質問題を洗い出す
3. 改善: 失敗したトレースをLLMに渡して、コピペで使える修正案を生成する

# 前提条件

このノートブックはDatabricks上で実行し、評価対象となるGenieスペースが必要です。本記事では `samples.bakehouse` のサンプルデータを使った「Bakehouse Sales Starter Space」を題材にしています。

必要なパッケージをインストールします。

```python
%pip install "mlflow[genai]" databricks-sdk -q
```

インストール後はカーネルを再起動して、更新したパッケージを反映させます。

```python
%restart_python
```

# Step 0: MLflowエクスペリメントのセットアップ

MLflowのクライアントとDatabricks SDKのWorkspaceClientを初期化し、トレースの記録先となるエクスペリメントを設定します。`SPACE_ID` には評価対象のGenieスペースのIDを指定します。

```python
import mlflow
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

SPACE_ID = "01f07ed9e2c81681aac9925f148c50d2"
EXPERIMENT_NAME = f"/Users/{w.current_user.me().user_name}/genie_eval"

mlflow.set_experiment(EXPERIMENT_NAME)
```

実行すると、設定したエクスペリメントの情報が返ります。

```
<Experiment: artifact_location='dbfs:/databricks/mlflow-tracking/823983741415220',
 experiment_id='823983741415220',
 name='/Users/takaakiyayoi@gmail.com/genie_eval', ...>
```

![Screenshot 2026-05-30 at 8.11.14.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d7ac05b1-55ac-45af-957f-cf24abf7b276.jpeg)

# Step 1: Genieの会話をMLflowトレースとして記録する

最初のステップは、Genieスペースで行われた会話を取得し、ひとつひとつをMLflowトレースとして記録することです。トレース化することで、MLflow UI上で会話を検索・比較・調査できるようになります。

![fig2_trace_flow.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8ced87ad-ab0f-4be8-82d5-b131f00562d5.png)

処理の流れは次の3つです。

1. すでにトレース化済みのGenieメッセージIDを集める(重複記録を避けるため)
2. Genieスペースのすべての会話を取得する
3. 各メッセージをループしてMLflowトレースとしてログする

各メッセージから、質問テキスト、テキスト回答、生成されたSQL、エラーを取り出し、`mlflow.start_span` でスパンの入出力として記録します。`message_id` をタグに付けておくことで、次回実行時に差分のみを追記できます。

```python
# 1. すでにトレースされたGenieメッセージIDを収集
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
existing_traces = mlflow.search_traces(
    experiment_ids=[experiment.experiment_id], return_type="list"
)
already_traced = {
    t.info.tags.get("message_id")
    for t in existing_traces
    if t.info.tags.get("message_id")
}

# 2. Genieスペースからすべての会話を取得
conversations = w.genie.list_conversations(
    space_id=SPACE_ID, include_all=True
)

# 3. ループしてMLflowトレースとしてログ
traced = 0
for convo in conversations.conversations or []:
    messages = w.genie.list_conversation_messages(
        space_id=SPACE_ID, conversation_id=convo.conversation_id
    )
    for msg in messages.messages or []:
        if not msg.content:
            continue
        if msg.message_id in already_traced:
            continue
        attachments = msg.attachments or []
        sql_att = next((a for a in attachments if a.query), None)
        text_att = next((a for a in attachments if a.text), None)
        with mlflow.start_span(name="genie_interaction") as span:
            span.set_inputs({"question": msg.content})
            span.set_outputs({
                "response": (text_att.text.content if text_att else None),
                "generated_sql": (sql_att.query.query if sql_att else None),
                "error": str(msg.error) if msg.error else None,
            })
            mlflow.update_current_trace(
                tags={"message_id": msg.message_id}
            )
        traced += 1

print(f"エクスペリメント {EXPERIMENT_NAME} に {traced} 件の新しいトレースをログしました")
```

実行すると、新たに記録されたトレース数が表示されます。今回は前回までに記録済みの会話があったため、新規分は1件でした。

```
エクスペリメント /Users/takaakiyayoi@gmail.com/genie_eval に 1 件の新しいトレースをログしました
```

メッセージのアタッチメントには、SQLクエリを持つもの(`a.query`)とテキスト回答を持つもの(`a.text`)があります。`next()` で先頭の該当アタッチメントを取り出している点に注目してください。これにより、Genieが生成したSQLと自然言語の回答を分けて記録できます。

![Screenshot 2026-05-30 at 8.10.38.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9537f7a9-5743-4ac3-afe6-9bba01e7994f.jpeg)

# Step 2: LLMジャッジでトレースを評価する

記録したトレースを採点します。MLflowには組み込みのLLMジャッジがあり、加えてガイドラインベースのカスタムジャッジやコードベースのスコアラーを自由に定義できます。本記事では合計7つのスコアラーを使います。

![fig3_scorers.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4d637d31-6150-4c71-b34b-337c3c832c16.png)

組み込みジャッジとして、回答が質問に関連しているかを見る `RelevanceToQuery`、安全性を見る `Safety`、取得した文脈に基づいているかを見る `RetrievalGroundedness` を使います。

カスタムジャッジとして、`Guidelines` を使い「回答品質」と「SQL品質」の観点を自然言語のルールで定義します。回答がユーザーの質問に直接答えているか、SQLが意図に合った集計関数やWHERE句を使っているか、といった点をチェックします。

コードベースのスコアラーとして、`@scorer` デコレータで「テキスト回答が存在するか」「エラーなく完了したか」を判定する関数を定義します。

```python
from mlflow.entities import Feedback
from mlflow.genai.scorers import (
    Guidelines,
    RelevanceToQuery,
    RetrievalGroundedness,
    Safety,
    scorer,
)

# 組み込みジャッジ
relevance = RelevanceToQuery()
safety = Safety()
groundedness = RetrievalGroundedness()

# カスタムジャッジ(回答品質)
response_quality = Guidelines(
    name="genie_response_quality",
    guidelines=[
        "レスポンスは、曖昧または一般的な回答ではなく、ユーザーのデータに関する質問に直接対応している必要がある。",
        "SQLが生成された場合、レスポンスはSQLクエリをエコーするだけでなく、データに基づいた回答を含む必要がある。",
        "テーブルに存在するはずのデータに関する質問に対して、レスポンスは「回答できません」と言うべきではない。",
    ],
)

# カスタムジャッジ(SQL品質)
sql_quality = Guidelines(
    name="genie_sql_quality",
    guidelines=[
        "SQLが存在する場合、ユーザーの意図に合致する適切な集約関数（SUM、COUNT、AVG）を使用している必要がある。",
        "SQLはユーザーの要求に応じてデータをフィルタリングするための適切なWHERE句を含む必要がある。",
        "SQLはLIMITまたは特定のフィルターなしで大きなテーブルに対してSELECT *を使用してはいけない。",
    ],
)

# コードベースのスコアラー
@scorer
def has_response(outputs) -> Feedback:
    """Genieがテキストレスポンスを返したかどうかを確認。"""
    resp = outputs.get("response") if isinstance(outputs, dict) else None
    if resp and len(str(resp).strip()) > 0:
        return Feedback(value="yes", rationale=f"{len(resp)} 文字")
    return Feedback(value="no", rationale="テキストレスポンスがありません")

@scorer
def no_error(outputs) -> Feedback:
    """インタラクションがエラーなしで完了したかどうかを確認。"""
    err = outputs.get("error") if isinstance(outputs, dict) else None
    if err and str(err).strip():
        return Feedback(value="no", rationale=f"エラー: {str(err)[:200]}")
    return Feedback(value="yes", rationale="エラーなし")

print("スコアラーを定義しました。")
```

スコアラーを定義したら、トレースをDataFrameとして取得し、`mlflow.genai.evaluate` に渡して一括評価します。

```python
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
traces_df = mlflow.search_traces(
    experiment_ids=[experiment.experiment_id],
    order_by=["timestamp DESC"],
    max_results=100,
)
print(f"評価対象のトレースが {len(traces_df)} 件見つかりました")

eval_results = mlflow.genai.evaluate(
    data=traces_df,
    scorers=[
        relevance,
        safety,
        groundedness,
        response_quality,
        sql_quality,
        has_response,
        no_error,
    ],
)
```

評価が完了すると、MLflow UI上でトレースごとに各ジャッジの採点結果が列として表示されます。今回は8件のトレースを評価しました。

```
評価対象のトレースが 8 件見つかりました
...
Evaluating: 0%| | 0/8 [Elapsed: 00:00, Remaining: ?]
2026/05/29 22:57:44 WARNING mlflow.genai.evaluation.harness: Some scorer
invocations failed during evaluation. Failure summary:
'retrieval_groundedness': 8/8 failed.
```

なお、`retrieval_groundedness` は8件中8件失敗しています。これは、Genieの会話には明示的な「取得した文脈(retrieved context)」のスパンが含まれていないため、グラウンデッドネスのジャッジが評価対象を見つけられないことが原因です。Genieのトレースを評価する場合、このジャッジは実質的に機能しない点に注意してください(他のジャッジは正常に動作します)。

![Screenshot 2026-05-30 at 8.14.05.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b92beb2e-c79f-4f60-99eb-43340b4c2a06.jpeg)

![Screenshot 2026-05-30 at 8.14.47.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2b12acf1-73c0-427f-afbe-67218c96aa8e.jpeg)

# Step 3: 失敗したトレースから改善案を生成する

最後のステップでは、評価で「失敗」と判定されたトレースを集め、LLMに渡してGenieスペースの具体的な改善案を生成させます。

まずはDatabricksのモデルサービングエンドポイントを、OpenAI互換クライアントとして利用できるように設定します。トークンとホストはノートブックのコンテキストから取得します。

```python
from openai import OpenAI
import json

# dbutils経由でDatabricksトークンを取得
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
host = w.config.host

client = OpenAI(
    base_url=f"{host}/serving-endpoints",
    api_key=token,
)

print(f"OpenAIクライアントを設定しました。ホスト: {host[:40]}...")
```

次に、評価結果から失敗したトレースを読み込みます。各トレースのアセスメント(`trace.info.assessments`)を調べ、値が `"no"` のチェックがひとつでもあれば「失敗した会話」として収集します。`root.outputs` は辞書・文字列・Noneのいずれかになり得るため、辞書のときだけ抽出するようにガードしています。

```python
# ステップ2: 評価から失敗したトレースを読み込み
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
all_traces = mlflow.search_traces(
    experiment_ids=[experiment.experiment_id],
    return_type="list",
)

failed_conversations = []
for trace in all_traces:
    assessments = trace.info.assessments or []
    failures = [a for a in assessments if a.value == "no"]
    if not failures:
        continue
    root = trace.data.spans[0]

    # root.outputsは辞書、文字列、またはNoneの可能性がある
    if isinstance(root.outputs, dict):
        failed_conversations.append({
            "question": root.inputs.get("question"),
            "response": root.outputs.get("response"),
            "generated_sql": root.outputs.get("generated_sql"),
            "error": root.outputs.get("error"),
            "failed_checks": [
                f"{a.name}: {a.value} - {a.rationale}"
                for a in failures
            ],
        })

print(f"{len(failed_conversations)} / {len(all_traces)} 件のトレースが失敗しました")
```

```
4 / 8 件のトレースが失敗しました
```

続いて、改善案生成のためにGenieスペースの構成情報を取得します。スペースのタイトルと、対象テーブルの一覧をプロンプトに含めるために用意します。

```python
# ステップ3: Genieスペースの設定を取得
space = w.genie.get_space(space_id=SPACE_ID)

print(f"スペース: {space.title}")
print(f"スペースID: {SPACE_ID}")

# Genieスペースから既知のテーブルを使用
table_names = [
    "samples.bakehouse.media_customer_reviews",
    "samples.bakehouse.media_gold_reviews_chunked",
    "samples.bakehouse.sales_customers",
    "samples.bakehouse.sales_franchises",
    "samples.bakehouse.sales_suppliers",
    "samples.bakehouse.sales_transactions",
]
print(f"テーブル: {len(table_names)}件")
```

```
スペース: Bakehouse Sales Starter Space
スペースID: 01f07ed9e2c81681aac9925f148c50d2
テーブル: 6件
```

いよいよ改善案の生成です。システムプロンプトで「Databricks Genieスペースの専門コンサルタント」という役割を与え、曖昧なアドバイスではなく、コピペで使える具体的な実装(SQL式、テキスト指示、サンプルSQL、カラム説明)を出力するよう指示します。分析プロンプトには失敗した会話と現在のスペース構成を埋め込み、日本語で回答するよう求めています。

関数には `@mlflow.trace` を付けているので、このLLM呼び出し自体もトレースとして記録されます。

```python
# ステップ4: LLMで修正案を生成
system_prompt = (
    "あなたはDatabricks AI/BI Genieスペースのエキスパートコンサルタントです。"
    "Genieが誤った回答または不完全な回答をした会話と、失敗した特定のチェックを受け取ります。"
    "具体的でコピー＆ペーストできる修正案を生成してください：SQL式、テキスト指示、サンプルSQL、カラムの説明。"
    "曖昧なアドバイスは絶対にしないでください。常に実際の実装を記述してください。"
)

analysis_prompt = f"""これらのGenie会話で見つかった問題を修正してください。

## 失敗した会話
{json.dumps(failed_conversations[:20], indent=2, ensure_ascii=False)}

## 現在のスペース設定
タイトル: {space.title}
テーブル: {', '.join(table_names[:10])}

失敗した各会話について、具体的な修正案を提供してください：新しいテキスト指示、
SQL式、サンプルクエリ、またはカラムの説明です。影響度で優先順位を付けてください。日本語で回答してください。"""

@mlflow.trace
def analyze_genie_space(user_prompt, sys_prompt):
    response = client.chat.completions.create(
        model="databricks-meta-llama-3-1-8b-instruct",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4000,
        temperature=0.2,
    )
    return response.choices[0].message.content

if not failed_conversations:
    print("失敗が見つかりませんでした - 分析するものはありません！")
else:
    print(f"{len(failed_conversations)} 件の失敗した会話を分析中...")
    recommendations = analyze_genie_space(
        analysis_prompt, system_prompt
    )
    print(recommendations)
```

実行すると、失敗した会話ごとに具体的な改善案が日本語で出力されます。今回の4件はいずれも「SQLは生成されたが、自然言語の回答が返っていない(SQLクエリだけが返却された)」という共通の傾向でした(この判定の解釈には注意が必要で、詳細は考察セクションを参照してください)。出力の抜粋を以下に示します。

```
4 件の失敗した会話を分析中...
失敗した各会話について、具体的な修正案を提供します。

### 会話1: 最も高い売上の店舗を尋ねる会話
* 問題点: 直接的な回答がなく、SQLクエリのみが返却されました。
* 修正案:
    + テキスト指示: "売上の最も高い店舗を知りたい場合は、以下のSQLクエリを実行してください。"
    + 返却されるテキスト: "売上の最も高い店舗は、`franchise_name`が`<franchise_name>`、
      `city`が`<city>`、`country`が`<country>`の店舗です。"

### 会話2: データセットの種類を尋ねる会話
* 問題点: SQLクエリのみが返却されました。
* 修正案:
    + 返却されるテキストに含めるデータセットの種類: media_customer_reviews、
      media_gold_reviews_chunked、sales_customers、sales_franchises、
      sales_suppliers、sales_transactions

### 会話4: 最も売れた製品を尋ねる会話
* 問題点: SQLクエリのみが返却されました。
* 修正案:
    + 返却されるテキスト: "最も売れた製品は、`product`が`<product>`の製品です。"
```

生成された改善案は、Genieスペースの設定画面でテキスト指示やSQL式、サンプルクエリとして登録することで、次回以降の回答品質の向上につなげられます。

![Screenshot 2026-05-30 at 8.15.54.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1f81e000-b9bb-4e42-ac37-c2df58e6160e.jpeg)

生成された改善案をそのまま採用してよいかは、後述の「考察」セクションで検討します。

# 補足: 利用可能なモデルエンドポイントの確認

改善案生成で使うモデルは、ワークスペースで利用可能なサービングエンドポイントから選べます。一覧は次のように確認できます。

```python
endpoints = w.serving_endpoints.list()
available = [e.name for e in endpoints]
print("Available endpoints:")
for name in available:
    print(f"  - {name}")
```

たとえば以下のようなエンドポイントが利用できます(環境によって異なります)。

```
  - databricks-claude-opus-4-8
  - databricks-meta-llama-3-3-70b-instruct
  - databricks-meta-llama-3-1-8b-instruct
  - databricks-gpt-oss-120b
  - databricks-qwen3-next-80b-a3b-instruct
  ...
```

改善案の品質を上げたい場合は、`model="databricks-meta-llama-3-1-8b-instruct"` の部分を `databricks-claude-opus-4-8` や `databricks-meta-llama-3-3-70b-instruct` などに差し替えるとよいでしょう。

# 考察: この修正案は妥当か

最後に、生成された修正案をそのまま採用してよいかを検討しておきます。結論から言うと、パイプラインの仕組みは有用ですが、今回出力された具体的な修正案は鵜呑みにできません。理由は2つあります。

## 1. 「回答なし」の失敗は誤検知の可能性がある

今回の4件はいずれも「SQLは生成されたが自然言語の回答が返っていない」と判定されました。しかしこれは、Genieが実際に失敗したのではなく、トレースの記録方法に起因するアーティファクトの可能性があります。

Step 1のコードでは、`response` にテキスト添付(`text_att.text.content`)だけを格納しています。

```python
span.set_outputs({
    "response": (text_att.text.content if text_att else None),
    "generated_sql": (sql_att.query.query if sql_att else None),
    "error": str(msg.error) if msg.error else None,
})
```

一方、Genieの典型的な挙動は「SQLを生成 → 実行 → 結果テーブルを表示」であり、テキスト要約を返さないケースも珍しくありません。その場合、Genieはデータで正しく答えているのに `response` が `None` になり、`genie_response_quality` ジャッジが「回答できていない」と誤判定します。

つまり、LLMが提案した「テキスト指示を追加して文章で回答させる」という修正は、根本原因ではなく計測上の見かけの問題に対処している恐れがあります。本来は、クエリ実行結果(結果テーブル)もトレースの `response` に含めるよう、Step 1の記録方法を見直すのが先決です。

## 2. 8Bモデルの修正案は品質が低い

今回利用した `databricks-meta-llama-3-1-8b-instruct` は軽量モデルのため、出力にいくつか問題が見られます。

具体性に欠ける表現が多く、「SQL式: 同じものを使用します」のように、システムプロンプトが要求した「コピペできる実装」になっていません。また会話3の可視化オプションに挙げられた「バイナリパッケージ」は可視化手法ではなく、ほぼ幻覚(hallucination)と考えられます。返却テキスト例も `<franchise_name>` のようなプレースホルダーのままで、そのまま設定に使える状態ではありません。

加えて、Step 2で触れたとおり `retrieval_groundedness` が8件中8件失敗している点も、評価セットアップの一部がGenieトレースに対して機能していないことを示しています。

改善案の品質を上げたい場合は、補足セクションで案内したモデルの差し替えが有効です。本記事のパイプラインは「品質改善のループを回す枠組み」として捉え、出力された個々の修正案は人間がレビューしてから適用することをおすすめします。

# まとめ

本記事では、MLflowのCookbookに沿って、Databricks Genieスペースを評価・改善する一連のパイプラインを実装しました。流れを振り返ると次のようになります。

トレーシングでGenieの会話をMLflowトレースとして記録し、評価で組み込み/カスタム/コードベースのスコアラーを使って品質を採点し、改善で失敗トレースをLLMに渡してコピペ可能な修正案を生成する、という3ステップです。今回の実行では8件中4件のトレースで「SQLは出るが自然言語の回答が返らない」という共通の傾向が見られ、改善を検討する出発点が得られました(ただしこの判定の解釈には注意が必要で、詳細は考察セクションを参照してください)。

このサイクルを定期的に回すことで、Genieスペースのテキスト指示やSQL式を継続的にブラッシュアップでき、ビジネスユーザーがより正確な回答を得られるようになります。Genieを本番運用しているチームにとって、データドリブンな改善ループを作る出発点として有用なアプローチです。ただし考察で述べたとおり、トレースの記録方法やLLMの出力品質によって結果が左右されるため、評価のセットアップと改善案のレビューは人間が担うことが前提となります。

# 参考リンク

- [Evaluating Databricks Genie Spaces (MLflow Cookbook)](https://mlflow.org/cookbook/databricks-genie/)
- [Genie Conversation Tracing Pipeline](https://mlflow.org/cookbook/genie-tracing-pipeline/)
- [Genie Evaluation with LLM Judges](https://mlflow.org/cookbook/genie-evaluation-judges/)
- [Genie Space Improvement Generator](https://mlflow.org/cookbook/genie-space-analyzer/)
- [Databricks AI/BI Genie ドキュメント](https://docs.databricks.com/aws/ja/genie/)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

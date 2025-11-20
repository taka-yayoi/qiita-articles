---
title: 'MLflowとDatabricksによるマルチターンチャットbotの評価: ステップバイステップのガイド'
tags:
  - Databricks
  - MLflow
  - エージェント
private: false
updated_at: '2025-04-15T16:21:42+09:00'
id: bff852da1bb445feaa9c
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Evaluate Multi‑Turn Chatbots on Databricks with MLflow: A Step‑by‑Step Guide](https://community.databricks.com/t5/technical-blog/evaluate-multi-turn-chatbots-on-databricks-with-mlflow-a-step-by/ba-p/114741)を翻訳しながら実行していきます。

こんにちは、Debuです。私は日々、LLMを活用したシステムの構築とストレステストに多くの時間を費やしています。そして、ある教訓が何度も繰り返されます。それは、**エージェントの行動を会話全体にわたって測定しないと、盲目的に進んでいることになる**ということです。以下は、Databricksでチャットボットのパフォーマンスをターンごとに評価し、その数値を時間とともに追跡するために使用する正確なノートブックパターンです。

# なぜマルチターン評価が必要なのか？

実際のユーザーは一度のメッセージで終わりません。彼らは話題を変えたり、フォローアップをしたり、ボットが文脈を覚えていることを期待します。単一ターンのテストでは、以下のような問題を表面化させることはできません：

- 以前の指示を見失う
- 3ターン後に矛盾する、または
- 対話が長くなると危険な領域に逸れる。

だからこそ、ここで見るすべての例は、会話を孤立したプロンプトではなく、メッセージのリストとして扱います。

# あなたが構築するもの

1. `databricks-sdk`と`databricks-agents`ライブラリを使用してノートブック環境を設定します。
1. 小さなマルチターン評価セットを作成します — それぞれ独自の指示を持つ2つの対話です。
1. 小さなルールベースのエージェントを作成し（後で実際のモデルに置き換えます）、`mlflow.trace`でラップします。
1. 有用性、明確さ、安全性のためのグローバルガイドラインを定義します。
1. 組み込みのDatabricksエージェントグレーダーを使用して`mlflow.evaluate`を実行します。
1. スコアをDeltaに保存し、トレンドを監視し、リグレッションをキャッチできるようにします。

# 1 - 前提条件と環境設定

DBR 14.3 LTSとMLflow ≥ 2.12を使用しています。追加ライブラリをインストールし、Pythonを再起動してDatabricksがそれらを認識するようにします:

```py
%pip install databricks-sdk databricks-agents
dbutils.library.restartPython()
```

次に、いつものライブラリをインポートします:

```py
import mlflow
from mlflow.deployments import get_deploy_client  # (オプション)本番環境デプロイ向け
import pandas as pd
```

# 2 - マルチターン評価データセットの作成

各行には、**これまでの全会話**と次の応答のための評価ガイドラインが含まれています:

```py
eval_set = [
    {
        "request": {
            "messages": [
                {"role": "user", "content": "こんにちは"},
                {"role": "assistant", "content": "こんにちは！今日はどのようにお手伝いできますか？"},
                {"role": "user", "content": "ジョークを教えて"}
            ]
        },
        "guidelines": [
            "応答はユーモラスで適切であるべき",
            "応答は簡潔であるべき"
        ]
    },
    {
        "request": {
            "messages": [
                {"role": "user", "content": "天気はどうですか？"},
                {"role": "assistant", "content": "リアルタイムの天気データは持っていません。天気情報を確認するには天気サービスを利用する必要があります。"},
                {"role": "user", "content": "LLMの仕組みを説明できますか？"}
            ]
        },
        "guidelines": [
            "応答は技術的でありながら理解しやすいものであるべき",
            "応答には注意メカニズムの簡単な説明を含めるべき"
        ]
    }
]

# DataFrameに変換して、mlflow.evaluateがテーブルのようなオブジェクトとして扱えるようにする
eval_df = pd.DataFrame(eval_set)
```

Pandasに保持しているのは、バージョン管理が容易で、迅速に検査できるためです。

# 3 - シンプルなエージェントの実装（デモのみ）
ここでは使い捨てのルールベースのエージェントを紹介します。重要なのは関数のシグネチャだけです — メッセージは全会話として入ってきます。

```py
@mlflow.trace(span_type="AGENT")
def my_agent(messages):
    """説明のための単純なルールベースのエージェント"""
    last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

    if "ジョーク" in last_user_message:
        return "なぜAIは美術学校に行ったのですか？結論を引き出す方法を学ぶためです！"
    elif "天気" in last_user_message:
        return "リアルタイムの天気データにはアクセスできませんが、一般的な天気のパターンについて説明できます。"
    elif any(term in last_user_message for term in ["LLM", "言語モデル"]):
        return (
            "大規模言語モデル（LLM）は、大量のテキストデータで訓練されたAIシステムです。"
            "トランスフォーマーアーキテクチャと注意メカニズムを使用して、トークン間の関係をモデル化します。"
        )
    else:
        return (f"あなたが尋ねたのは: '{last_user_message}' ですね。それについてどのようにお手伝いできますか？")
```

`mlflow.trace`は、レイテンシーとネストされた呼び出しのトレースを無料で提供してくれます。これを実際のチェーン・オブ・ソートやRAGパイプラインに置き換えたときに便利です。

# 4 - グローバルガイドライン

**すべての**行に適用される2番目のチェックレイヤーを追加します:

```py
global_guidelines = {
    "helpfulness": ["応答は役に立ち、ユーザーの質問に直接答えるものでなければなりません"],
    "clarity": ["応答は明確で、構造が整っている必要があります"],
    "safety": ["応答は安全で適切でなければなりません"]
}
```

# 5 - 評価の実行
次に、エージェントを評価しましょう。すべてはMLflowランの中にあるので、後で追跡できます:

```py
with mlflow.start_run(run_name="agent_evaluation_v1") as run:
    evaluation_results = mlflow.evaluate(
        data=eval_df,
        model=lambda request: my_agent(**request),
        model_type="databricks-agent",
        evaluator_config={
            "databricks-agent": {
                "global_guidelines": global_guidelines
            }
        }
    )
```
![Screenshot 2025-04-15 at 16.15.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bb40babd-73f2-4f28-9f8a-bfb214ec97ca.png)
![Screenshot 2025-04-15 at 16.16.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c28795b9-4d59-418d-b0c2-d6d040989f6a.png)
![Screenshot 2025-04-15 at 16.16.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d1c8df17-d3e6-489a-9872-063730ace614.png)

内部では、Databricksは独自の専門家LLMジャッジを呼び出し、helpfulness_score、clarity_score、およびsafety_scoreのようなスコアを返します。

# 6 - 結果の検査

```py
print("Aggregated metrics:\n", evaluation_results.metrics)
per_request_results = evaluation_results.tables["eval_results"]
print("\nPer‑request results:\n", per_request_results)
```
```
Aggregated metrics:
 {'agent/latency_seconds/average': 0.0, 'response/llm_judged/global_guideline_adherence/safety/rating/percentage': 1.0, 'response/llm_judged/relevance_to_query/rating/percentage': 0.5, 'response/llm_judged/safety/rating/percentage': 1.0, 'response/llm_judged/guideline_adherence/rating/percentage': 0.0, 'response/llm_judged/global_guideline_adherence/clarity/rating/percentage': 0.5, 'response/llm_judged/global_guideline_adherence/helpfulness/rating/percentage': 1.0, 'response/overall_assessment/rating/percentage': 0.0}

Per‑request results:
                                           request_id  ... agent/latency_seconds
0  ab7a3fc395f03594b9b0bf8f4619b8f629d3bb5c239d19...  ...                     0
1  01b156be210a86181b797e7904da9c99232b5f63985de2...  ...                     0

[2 rows x 21 columns]
```

すぐにビジュアルが必要ですか？ノートブックで次のコードを実行してください:

```py
display(per_request_results)
```
![Screenshot 2025-04-15 at 16.18.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bb616aaa-b816-4a9a-9947-4527e3a70cbe.png)

集計は退行をキャッチします。リクエストごとの行は、**どのターン**がガイドラインを破ったかを正確に教えてくれます。

# 7 - メトリクスをDeltaに永続化
すべての実行をDeltaにプッシュして、トレンドをチャート化し、アラートを設定します：

```py
def append_metrics_to_table(run_name, mlflow_metrics, delta_table_name):
    data = {k: v for k, v in mlflow_metrics.items() if "error_count" not in k}
    data.update({"run_name": run_name, "timestamp": pd.Timestamp.now().to_pydatetime()})

    (spark.createDataFrame([data])
        .write.mode("append")
        .saveAsTable(delta_table_name))

append_metrics_to_table("agent_evaluation_v1", evaluation_results.metrics, "users.takaaki_yayoi.agent_eval_results")
```
![Screenshot 2025-04-15 at 16.19.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/26985b53-8534-4341-874b-3be1cbfdf458.png)

# まとめと次のステップ
これで、繰り返し可能なマルチターン評価ループが完成しました：

- **再現可能** – すべての実行がMLflowにログされます。
- **交換可能** – おもちゃのエージェントを本番モデルに置き換えても、ハーネスはそのままです。
- **観測可能** – メトリクスとトレースは長期的な可視性のためにDeltaとMLflowに保存されます。

## ここからの展開

- 評価セットを敵対的なプロンプトや長いチャットで拡張します。
- 品質スコアと並行して、レイテンシー、トークン使用量、コストを追跡します。
- これをCI/CDに接続し、役立ち度が低下した場合にモデルのプロモーションをブロックします。
- すべてをUnity Catalogに保存してガバナンスを確保します。

これらのチェックを早期に組み込むことで、エージェントはリリースごとに改善され、実際のユーザーに到達したときに驚きがありません。質問や調整があれば、いつでも連絡してください。良い航海を！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

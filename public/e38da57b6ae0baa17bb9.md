---
title: 『MLflowで実践するLLMOps』の出版後、MLflow 3.10〜3.17で変わったことをサンプルコードを直しながらなぞる
tags:
  - MLflow
  - LLMOps
  - 生成AI
  - opentelemetry
  - pytest
private: false
updated_at: '2026-11-02T19:58:04+09:00'
id: e38da57b6ae0baa17bb9
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

2026年4月に技術評論社から『MLflowで実践するLLMOps――生成AIアプリケーションの実験管理と品質保証』を刊行しました。本書は MLflow 3.9 を対象に書いています。

- [書籍ページ (技術評論社)](https://gihyo.jp/book/2026/978-4-297-15573-5)
- [サンプルコードリポジトリ](https://github.com/takaaki-yayoi/mlflow_llmops)

本書の対象版 3.9 のリリースは2026年1月です。そこから10月の 3.17 までに、MLflow はマイナーバージョンが8回上がりました。サンプルコードを最新の 3.17.2 で動かし直したところ、そのままでは止まるスクリプトが出てきました。新しい機能のなかには、本書の章の続きとして読めるものもあります。

そこで、壊れた箇所の修正と新機能の補足サンプルをリポジトリに追加しました。この記事では、その内容を MLflow のバージョン順になぞります。各バージョンについて、次の3点を書いていきます。

- 何が変わったのか
- 本書のどの章に関係するのか
- サンプルの動かし方と、実際に動かした結果

# 確認した環境

- MLflow 3.17.2 (OSS)。Tracking Server はローカルで起動し、バックエンドは SQLite
- macOS、Python 3.12
- LLM は OpenAI の gpt-4o-mini

サンプルを動かすには、リポジトリを最新にして、各章で `make install` を実行します。

```bash
cd mlflow_llmops
git checkout main
git pull
```

ch4〜ch8 の `uv.lock` は 3.17.2 に固定しました。`pyproject.toml` の下限は本書の対象版のまま (`mlflow>=3.9.0`) にしてあり、今回の修正はすべて 3.9 でも動く形にしています。

Tracking Server は、本書のとおりポート5000で起動します。バージョンを上げる前に起動したサーバーが残っていると、古い版のサーバーがそのまま応答します。今回、私はここで少し手間取りました。`lsof -i :5000` でポートを使っているプロセスを確かめ、止めてから起動し直してください。macOS では AirPlay レシーバーがポート5000を使っていることもあります。その場合の対処は付録 B.2 にあります。

# 3.10: トレースにコストが記録されるようになった

本書 8.2.4 項で、MLflow 3.10 以降は Overview ダッシュボードの Usage ビューでトークンのコストが表示される、と紹介しました。同じコストは、コードからも `trace.info.cost` で取り出せます。

一方、第8章のサンプル `02_token_and_cost.py` は、トークン数から自前の料金表 (`cost_calculator.py`) でコストを計算しています。両者を並べるスクリプトを `ch8/monitoring/06_builtin_cost.py` として追加しました。

```bash
cd ch8
make cost-builtin
```

中心になるのは次の部分です。

```python
trace = mlflow.get_trace(trace_id=trace_id)

usage = trace.info.token_usage or {}
# MLflow が計算したコスト。{"input_cost", "output_cost", "total_cost"} (単位は USD)
builtin = trace.info.cost
# 本書のサンプルの料金表で計算したコスト
manual = calculate_cost(model, usage.get("input_tokens", 0), usage.get("output_tokens", 0))
```

実行結果です。「組み込み」の行が MLflow が自動で計算したコスト、「cost_calculator.py」の行が本書のサンプルの料金表で計算したコストです。

```text
=== 組み込みのコスト (trace.info.cost) と cost_calculator.py の比較 ===

プロンプト: Pythonのデコレータを簡潔に説明してください。...
  トークン: 入力 20 / 出力 232
  組み込み: $0.000142 (入力 $0.000003 + 出力 $0.000139)
  cost_calculator.py: $0.000142

プロンプト: MLflowのトレーシング機能について、主な利点を3つ挙げてください。...
  トークン: 入力 31 / 出力 401
  組み込み: $0.000245 (入力 $0.000005 + 出力 $0.000241)
  cost_calculator.py: $0.000245

=== コスト集計 (直近のトレース) ===

コストが記録されたトレース: 8件 / 8件
合計コスト: $0.002442
```

どちらのプロンプトでも、2つの金額は同じになりました。1つ目のプロンプトを料金表で計算すると、gpt-4o-mini の単価 (入力 $0.15、出力 $0.60、いずれも100万トークンあたり) から次のようになります。

- 入力: 20トークン × $0.15 ÷ 100万 = $0.000003
- 出力: 232トークン × $0.60 ÷ 100万 = $0.000139
- 合計: $0.000142

MLflow が計算した値も $0.000142 でした。料金表を自分で持たなくても、同じコストがトレースから取れるということです。

MLflow UI では、スパンごとにコストが表示されます。1つ目のプロンプトのトレースを開くと、スパンに $0.000142 と出ていました。なお、トレースのヘッダー部分は表示上 $0.00 になっていたので、細かい金額はスパン側で見るのが確実です。

![05_ch8_trace_cost.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/19fe75d9-1743-4e95-a095-bd61453adb8a.png)

8.2.4 項で紹介した Usage ビューには、モデル別の内訳と日ごとの推移が出ます。

![06_ch8_overview_cost.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/76257be3-51c4-4a06-bc6b-3083d2534953.png)

自前の料金表 `cost_calculator.py` は、契約価格や自社ホストのモデルなど、MLflow の料金データにない単価で計算したいときのために残しています。

# 3.11: extras の変更、OTel GenAI 規約、問題検出

3.11 は、本書のサンプルに関係する変更が一番多いバージョンでした。

## mlflow[genai] から litellm と gepa が外れた

ここが最初のハマりどころです。3.11 で、`mlflow[genai]` の extras から litellm と gepa が外れました。第6章の GEPA によるプロンプト最適化 (`make optimize-gepa`) を 3.11 以降で実行すると、次のエラーで止まります。

```text
  File ".../gepa/api.py", line 243, in optimize
    import litellm
ModuleNotFoundError: No module named 'litellm'
```

gepa はリポジトリの `pyproject.toml` に明記していましたが、gepa が内部で litellm を使っていました。ch6 の依存に litellm を追加して解消しています。

```toml
dependencies = [
    "mlflow[genai]>=3.9.0",
    # MLflow 3.11以降、genai extrasにlitellmとgepaが含まれなくなったため明記する。
    # gepaは内部でlitellmを使う
    "gepa>=0.0.18",
    "litellm>=1.0.0",
]
```

自分の環境で `pip install "mlflow[genai]"` から始める場合は、litellm と gepa を別途インストールしてください。

## OpenTelemetry の GenAI セマンティック規約で送れるようになった

本書 8.5 節では、MLflow のトレースを OTLP で OpenTelemetry Collector にも送るデュアルエクスポートを紹介しました。このとき送られるスパンの属性名は、`mlflow.spanInputs` のような MLflow 独自のものです。

3.11 で、環境変数 `MLFLOW_ENABLE_OTEL_GENAI_SEMCONV=true` を設定すると、OpenTelemetry の GenAI セマンティック規約 (`gen_ai.*` の属性) に変換して送れるようになりました。GenAI 規約に対応した監視基盤で、MLflow のトレースをそのまま扱いやすくなります。

違いを見るためのスクリプトを `ch8/monitoring/07_otel_genai_semconv.py` として追加しました。Collector の代わりに、受け取ったスパンを表示するだけの小さな OTLP 受信サーバーを Python で立てているので、Collector も Docker も要りません。

```bash
make otel-semconv
```

MLflow の設定は、MLflow を import する前に環境変数で行います。

```python
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = f"http://localhost:{RECEIVER_PORT}/v1/traces"
os.environ["OTEL_EXPORTER_OTLP_TRACES_PROTOCOL"] = "http/protobuf"
# MLflow の Tracking Server にも、OTLP の送信先にも送る
os.environ["MLFLOW_TRACE_ENABLE_OTLP_DUAL_EXPORT"] = "true"
```

GenAI 規約への変換を切り替える環境変数は、スパンが終わるときに読まれます。そのため、1つのスクリプトの中で呼び出しごとに切り替えられます。

```python
# この環境変数はスパンの終了時に読まれるので、呼び出しごとに切り替えられる
os.environ["MLFLOW_ENABLE_OTEL_GENAI_SEMCONV"] = "true" if semconv else "false"
```

同じ LLM 呼び出しを、変換なしと変換ありで送った結果です。

```text
=== 変換なし: MLFLOW_ENABLE_OTEL_GENAI_SEMCONV=false ===

スパン名: Completions
  mlflow.traceRequestId = "tr-fbd2c16bd6ee4f775e64417da88a1d46"
  mlflow.spanType = "CHAT_MODEL"
  mlflow.spanInputs = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "MLf...
  model = "gpt-4o-mini"
  mlflow.message.format = "openai"
  mlflow.llm.model = "gpt-4o-mini-2024-07-18"
  mlflow.chat.tokenUsage = {"input_tokens": 18, "output_tokens": 46, "total_tokens": 64, "cache_r...
  mlflow.spanOutputs = {"id": "chatcmpl-EfjABTJh9yLZncAzHY2WqOFpi8j9d", "choices": [{"finish_...
  mlflow.spanLogLevel = 20

=== 変換あり: MLFLOW_ENABLE_OTEL_GENAI_SEMCONV=true ===

スパン名: chat gpt-4o-mini-2024-07-18
  model = "gpt-4o-mini"
  gen_ai.operation.name = chat
  gen_ai.request.model = gpt-4o-mini-2024-07-18
  gen_ai.usage.input_tokens = 18
  gen_ai.usage.output_tokens = 57
  gen_ai.input.messages = [{"role": "user", "parts": [{"type": "text", "content": "MLflow Tracin...
  gen_ai.output.messages = [{"role": "assistant", "parts": [{"type": "text", "content": "MLflow T...
  gen_ai.response.id = chatcmpl-EfjAEJDaBAmiZCqh1TsFOLUN9GTLN
  gen_ai.response.model = gpt-4o-mini-2024-07-18
  gen_ai.response.finish_reasons = [stop]
```

変換なしでは、トークン数が `mlflow.chat.tokenUsage` に JSON でまとめて入っています。変換ありでは、`gen_ai.usage.input_tokens` と `gen_ai.usage.output_tokens` に分かれ、スパン名も規約どおり「操作名 モデル名」の形になりました。

## 問題検出 (Issue detection)

3.11 では、トレースから品質上の問題を見つける「問題検出」も追加されました。本書 8.3 節では、LLM ジャッジやユーザーフィードバックでトレースの品質を測りました。問題検出は、選んだトレースを LLM がまとめて読み、失敗のパターンを「問題」として分類する機能です。どのジャッジを用意すればよいか決まっていない段階で、まず何が起きているかをつかむのに使えます。

UI の機能なのでコードはありません。第8章のサンプル (`make cost`、`make feedback` など) で作ったトレース10件に対して実行しました。実験の Traces タブの右上にある「Detect Issues」を押すと、ダイアログが開きます。

![07_ch8_detect_issues_dialog.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ec27d65d-1cf4-4242-98a3-a44226c9bbb3.png)

モデルの既定は OpenAI で、対象のトレース数と費用の見積もりが出ます。初回は API キーを求められ、入力したキーは Settings > LLM Connections に保存されます。

ここで1回失敗しました。`.env` の行を `OPENAI_API_KEY=` ごと貼り付けてしまい、「Incorrect API key」で止まりました。貼るのはキーの部分だけです。保存したキーは LLM Connections の画面から編集できます。

完了すると、Evaluation runs に種類が「Issue detection」のランができます。今回は38.6秒で終わり、10件のトレースから3件の問題が見つかりました。費用は $0.1338 で、ダイアログの見積もり ($0.03〜$0.10) より少し多めでした。

![08_ch8_issue_detection_summary.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3dd60fe7-9186-49d0-81da-e928cf41525a.png)

Issues タブには、問題ごとに深刻度、影響を受けたトレースの数、説明が並びます。

![09_ch8_issues_tab.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e0c20ca1-1413-44eb-9204-a6de958aeb08.png)

検出された問題は次の3件でした。

| 深刻度 | 問題 | 影響を受けたトレース |
| --- | --- | --- |
| High | MLflow Tracing confused with Tracking | 4 |
| High | Invalid model deployment examples | 1 |
| Low | RAG中核評価指標の欠落 | 1 |

1件目は、「MLflow Tracing の利点は？」と聞いたのに、実験管理 (Tracking) の説明を返していた、という指摘です。第8章のサンプルは、検索ツールを持たない素の gpt-4o-mini に質問しているので、モデルの知識だけで答えて Tracing と Tracking を取り違えたのだと思われます。原因の説明にも「ツールを使わずに直接回答している経路で起きている」と書かれていました。

問題ごとに Resolve (対応済み) と Reject (問題ではない) に振り分けられます。問題検出の詳しい検証は、Databricks 上で試した記事に書いています。

- [MLflowの問題検出で、仕込んだ4つの問題が見つかるか試してみた](https://qiita.com/taka_yayoi/items/2e14c862f95a169648d1)

# 3.12: トレースが非同期で書き込まれるようになった

3.12 で、OSS の MLflow でもトレースが既定で非同期に書き込まれるようになりました。アプリケーションの処理がトレースの書き込みを待たなくなる、という改善です。

ただし、これで第8章の2本のスクリプトが止まるようになりました。

| スクリプト | 3.12 以降で起きたこと |
| --- | --- |
| `make cost` (02_token_and_cost.py) | `get_trace()` が None を返し、`AttributeError: 'NoneType' object has no attribute 'info'` |
| `make feedback` (03_feedback.py) | `log_feedback()` が `RESOURCE_DOES_NOT_EXIST: Trace with ID '...' not found.` |

どちらも、LLM を呼び出した直後に、そのトレースを取得したりフィードバックを付けたりしています。書き込みが非同期になったので、その時点ではまだトレースが Tracking Server に届いていません。当然といえば当然の挙動です。

トレース ID を取得した直後に、非同期の書き込みをフラッシュする1行を足して解消しました。

```python
trace_id = mlflow.get_last_active_trace_id()
# MLflow 3.12以降はトレースが非同期で書き込まれるため、取得前にフラッシュする
mlflow.flush_trace_async_logging()
trace = mlflow.get_trace(trace_id=trace_id)
```

本書のリスト8.9 (トークン使用量の取得) とリスト8.10 (フィードバックの記録) を写して 3.12 以降で動かす場合も、同じ1行が必要です。

`flush_trace_async_logging()` は 3.9 にもあるので、修正後のコードは本書の対象版でも動きます。ただし 3.9 では非同期の書き込みが無効なので、`Failed to flush trace async logging` という ERROR のログが出ます。処理には影響しません。

# 3.13: スパンにログレベルが付くようになった

エージェントのトレースには、LLM やツールの呼び出しのほかに、LangGraph の内部処理などの細かいスパンが大量に並びます。本書 4.4.2 項で見たとおりです。

3.13 で、スパンに Python の logging と同じ考え方のログレベル (DEBUG / INFO / WARNING / ERROR / CRITICAL) が付くようになりました。レベルの決まり方は次のとおりです。

- 何も指定しない場合は、スパンの種類で決まる。LLM、CHAT_MODEL、TOOL、RETRIEVER、AGENT、EMBEDDING は INFO、それ以外 (CHAIN や種類なし) は DEBUG
- `@mlflow.trace(log_level=...)` や `span.set_log_level(...)` で明示的に指定できる
- スパンの中で例外が起きると ERROR になる

第4章の QA エージェントを自前のスパンで包んで、レベルを一覧表示するスクリプトを `ch4/tracing/span_log_level.py` として追加しました。

```bash
cd ch4
make log-level
```

自前のスパンは3つ用意しました。

```python
@mlflow.trace(log_level="DEBUG")
def normalize_question(question: str) -> str:
    """前後の空白を取るだけの前処理。普段は見なくてよいので DEBUG にする。"""
    return question.strip()


@mlflow.trace
def validate_question(question: str) -> None:
    """空の質問を弾く。例外が起きるとこのスパンは自動で ERROR になる。"""
    if not question:
        raise ValueError("質問が空です")


@mlflow.trace(log_level="INFO")
def check_citation(answer: str) -> bool:
    """回答に URL が含まれるかを確認する。含まれないときは WARNING に上げる。"""
    has_url = bool(re.search(r"https?://", answer))
    if not has_url:
        mlflow.get_current_active_span().set_log_level("WARNING")
    return has_url
```

記録されたレベルは `span.log_level` で取り出せます。通常の質問と空の質問を1回ずつ流した結果です。

```text
=== 1. 通常の質問 ===
クエリを処理中: MLflowのトレースとは何ですか？
  INFO     AGENT       qa_request
  DEBUG    UNKNOWN     normalize_question
  DEBUG    UNKNOWN     validate_question
  DEBUG    CHAIN       LangGraph
  DEBUG    CHAIN       agent
  INFO     CHAT_MODEL  ChatOpenAI
  DEBUG    CHAIN       RunnableCallable
  DEBUG    CHAIN       tools
  INFO     TOOL        doc_search
  INFO     RETRIEVER   VectorStoreRetriever
  DEBUG    CHAIN       agent
  INFO     CHAT_MODEL  ChatOpenAI
  DEBUG    CHAIN       RunnableCallable
  INFO     UNKNOWN     check_citation

=== 2. 空の質問 (validate_question で例外) ===
例外: 質問が空です
  ERROR    AGENT       qa_request
  DEBUG    UNKNOWN     normalize_question
  ERROR    UNKNOWN     validate_question
```

14個のスパンのうち、INFO は6個です。LangGraph の内部処理 (CHAIN) は自動で DEBUG になっていて、INFO 以上だけを見れば、LLM 呼び出し、ツール呼び出し、検索に絞れます。2回目は、例外を起こした `validate_question` と、例外が伝わった親の `qa_request` が ERROR になりました。

MLflow UI でトレースを開くと、スパンは種類にかかわらずすべて並びます。

![01_ch4_trace_spans.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ec501039-2e91-4978-95dd-261051aa477d.png)

3.17.2 の時点では、UI の標準のトレース画面 (Traces タブ) に、ログレベルでスパンを絞り込む操作は見当たりませんでした。今回はログレベルを API で取り出して確認しています。

# 3.14: 評価を pytest のテストとして書けるようになった

3.14 で `@mlflow.test` が追加されました。`mlflow.genai.evaluate()` の結果を `assert result.passed, result.reason` で判定すると、評価がそのまま pytest のテストになります。本書の第5章では評価を実行して結果を MLflow UI で確認しましたが、これを CI で品質の後退を止める仕組みにつなげられます。

`@mlflow.test` の基本は、Databricks Free Edition で試した記事に書いています。

- [MLflow 3.14の @mlflow.test で、エージェントの評価をpytestのテストにする](https://qiita.com/taka_yayoi/items/91e13561a4ef3751df37)

今回は、第5章の QA エージェントそのものをテストする `ch5/tests/test_regression.py` を追加しました。

```bash
cd ch5
make test-regression
```

MLflow の pytest プラグインは自動では読み込まれないので、`tests/conftest.py` で有効にしています。

```python
from dotenv import load_dotenv

load_dotenv()

# @mlflow.test は MLflow の pytest プラグインを有効にしないと動かない
pytest_plugins = ["mlflow.pytest.plugin"]
```

テスト本体です。品質を落としたくない代表的な質問を parametrize で流し、回答が質問に沿っているか (`RelevanceToQuery`) と、参照リンクを含んでいるか (第5章の `has_reference_link`) を判定します。

```python
CRITICAL_QUESTIONS = [
    "MLflowとは何ですか？",
    "実験管理はどのように始めれば良いですか？",
]


@mlflow.test
@pytest.mark.parametrize("question", CRITICAL_QUESTIONS, ids=["what_is_mlflow", "start_tracking"])
def test_answer_quality(agent, question):
    """回答が質問に沿っていて、参照リンクを含むこと。"""
    result = mlflow.genai.evaluate(
        data=[{"inputs": {"question": question}}],
        predict_fn=make_predict_fn(agent),
        scorers=[RelevanceToQuery(), has_reference_link],
    )
    # すべてのスコアラーが合格 (yes / True) なら passed が True になる。
    # 不合格のときは、どのスコアラーがなぜ落ちたかが reason に入る
    assert result.passed, result.reason
```

実行すると、2件中1件が不合格になりました。

```text
tests/test_regression.py::test_answer_quality[what_is_mlflow] FAILED     [ 50%]
tests/test_regression.py::test_answer_quality[start_tracking] PASSED     [100%]
```

不合格の理由は、`result.reason` の内容としてそのまま表示されます。

```text
E       AssertionError: has_reference_link: The first guideline requires that the response includes the URL to official documentation or API references. The response does not contain any URLs or links. ...
```

「MLflowとは何ですか？」への回答に URL がなく、第5章で作った `has_reference_link` が不合格にしています。システムプロンプトでは URL を含む引用を指示しているので、品質としては落ちている回答です。テストがそれを検出して止めた、という狙いどおりの結果になりました。

MLflow UI では、Evaluation runs に種類が Test のランが1つでき、pytest の1回の実行がそこにまとまります。テストが1件でも失敗すると、ランの状態は失敗になります。

![02_ch5_test_run_list.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e9510eff-664c-491e-832f-489208fc68bb.png)

ランを開くと、テストごとの結果が並びます。合格したテストは 2/2、不合格のテストは 1/2 で、全体の合格率は50%です。

![03_ch5_test_results.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3661af26-f7b9-40c2-9f6c-fc623164aedb.png)

不合格のテストを開くと、どのアサーションが落ちたのかが分かります。

![04_ch5_test_failure_detail.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2900ad83-d32c-4f75-9341-9c628e24a5ec.png)

## 3.17.2 では expectations を使わない

ここが2つ目のハマりどころです。最初は第5章の評価データセットと同じく、`expectations` に期待する回答を入れて `Correctness` で判定しようとしました。ところが 3.17.2 では、データに `expectations` を含めると、スコアラーがすべて合格でも `result.passed` が False になります。

```python
@scorer
def always_true(outputs) -> bool:
    return True

# expectations なし
mlflow.genai.evaluate(data=[{"inputs": {"q": "a"}, "outputs": "x"}], scorers=[always_true]).passed
# → True

# expectations あり
mlflow.genai.evaluate(
    data=[{"inputs": {"q": "a"}, "outputs": "x", "expectations": {"expected_response": "x"}}],
    scorers=[always_true],
).passed
# → False
```

`result.passed` は、評価結果の表のうち名前が `/value` で終わる列をスコアラーの結果として判定しています。期待値の列 (`expected_response/value`) も同じ形の名前なので、合否の判定に含まれてしまうためです。MLflow の GitHub ですでに報告されていて (mlflow/mlflow#25701)、修正のプルリクエスト (#26151) も出ています。それまでは、期待値なしで判定できるスコアラーで組むのが確実です。

# 3.15〜3.17 で今回扱わなかったもの

3.15〜3.17 にも大きな機能追加がありましたが、本書のサンプルを直す必要はありませんでした。サンプルに関係が薄いので、今回は補足サンプルも作っていません。

- MCP Registry (3.15)。MCP サーバーを登録して、バージョンとエイリアスで管理する
- TypeSafe の型付き判定を使うジャッジ (3.17)
- ロールベースのアクセス制御の拡張 (3.13、3.17)

1点だけ、3.16 以降は `import mlflow` のたびに、コーディングエージェント向けの案内がログに出るようになりました。

```text
INFO mlflow.agent.hint: Load the `instrumenting-with-mlflow-tracing` skill at .../SKILL.md before writing any tracing code; it ships with this MLflow install. Set MLFLOW_DISABLE_AGENT_HINT=1 to silence this.
```

コーディングエージェントに MLflow の使い方を案内するためのものです。サンプルの実行時には不要なので、各章の Makefile で `MLFLOW_DISABLE_AGENT_HINT=1` を設定して抑制しています。

# リポジトリで直したそのほかの点

バージョンアップへの追従とあわせて、次の点も直しました。

- 第9章のノートブックで、`log_model()` の `artifact_path` を `name` に変更した。`artifact_path` は MLflow 3.x で非推奨になっている。本書のリスト9.3、リスト9.11、9.3.5 項のコードも `artifact_path="model"` なので、`name="model"` と読み替えてください
- 第7章の Legacy 方式の AI Gateway (`mlflow gateway start`) は 3.17.2 でも起動するが、非推奨の警告が出る。本書 7.4 節が解説している新方式を使ってください
- ノートブック 9.1 のサービングのポートを、本書と同じ8080番に揃えた
- ch3〜ch5 の CLI で、標準入力が終わったとき (Ctrl+D など) にエラー表示を繰り返していたのを直した

各章の差分は、リポジトリの `CHAPTER_NOTES.md` の末尾にまとめています。

# まとめ

本書の対象版 MLflow 3.9 から 3.17.2 までのアップデートを、サンプルコードを直しながらなぞりました。

- 3.10 から、トレースにコストが記録される。`trace.info.cost` で取り出せ、本書のサンプルの料金表と同じ値になった
- **3.11 で `mlflow[genai]` から litellm と gepa が外れた。第6章の GEPA による最適化には litellm を別途インストールする**
- 3.11 で、OTLP で送るスパンを OpenTelemetry の GenAI セマンティック規約に変換できるようになった
- 3.11 の問題検出で、第8章のトレース10件から3件の問題が見つかった。費用は約 $0.13
- **3.12 からトレースの書き込みが非同期になった。LLM 呼び出しの直後にトレースを取得するコードには `mlflow.flush_trace_async_logging()` が必要**
- 3.13 から、スパンにログレベルが付く。LangGraph の内部処理は自動で DEBUG になる
- 3.14 の `@mlflow.test` で、第5章の評価を pytest のテストにできた。 **3.17.2 ではデータに expectations を含めると `result.passed` が常に False になるので、期待値なしのスコアラーで組む**

一番の収穫は、壊れた箇所と新機能が同じバージョンにまとまって現れることを実感したことでした。3.11 と 3.12 はとくにそうで、本書のサンプルが止まる原因と、本書の章の続きとして使える機能が、同じリリースに入っていました。リリースノートを読むときは、新機能の一覧だけでなく Breaking Changes と既定値の変更も、自分のコードに当てはめて確かめるようにします。リポジトリは今後もバージョンアップに合わせて更新していきます。

# 参考リンク

- [MLflowで実践するLLMOps (技術評論社)](https://gihyo.jp/book/2026/978-4-297-15573-5)
- [サンプルコードリポジトリ](https://github.com/takaaki-yayoi/mlflow_llmops)
- [MLflow CHANGELOG](https://github.com/mlflow/mlflow/blob/master/CHANGELOG.md)
- [MLflow GenAI ドキュメント](https://mlflow.org/docs/latest/genai/)
- [mlflow/mlflow#25701: EvaluationResult.passed が評価データの期待値も判定に含める](https://github.com/mlflow/mlflow/issues/25701)
- [『MLflowで実践するLLMOps』が1,000部に届いたので、リポジトリのその後とLLMOpsの現在地をまとめる](https://qiita.com/taka_yayoi/items/44eba61afdd77b85e16d)
- [MLflow 3.14の @mlflow.test で、エージェントの評価をpytestのテストにする](https://qiita.com/taka_yayoi/items/91e13561a4ef3751df37)
- [MLflowの問題検出で、仕込んだ4つの問題が見つかるか試してみた](https://qiita.com/taka_yayoi/items/2e14c862f95a169648d1)

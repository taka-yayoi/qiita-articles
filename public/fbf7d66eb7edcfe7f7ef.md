---
title: 'Databricks の MLflow トレースに個人情報を残さない: スパンプロセッサーで送信前に書き換える'
tags:
  - Databricks
  - MLflow
  - LLMOps
  - 生成AI
  - Databricks_Free_Edition
private: false
updated_at: '2026-11-23T09:19:30+09:00'
id: fbf7d66eb7edcfe7f7ef
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

MLflow のトレースには、アプリの入力と出力がそのまま記録されます。デバッグには便利ですが、ユーザーが入力したメールアドレスや、ツールが返した電話番号もそのまま残ります。本番のエージェントでトレースを取り続けるなら、個人情報の扱いは避けて通れません。

以前、Unity Catalog に保存したトレースをマスクする方法を2本の記事にしました。

- [MLflowトレースのPIIマスキング — Unity Catalogカラムマスクとai_mask() ETLの2層構成](https://qiita.com/taka_yayoi/items/4cd0e5f814d1dfc30699)
- [MLflowトレースのPIIマスキング (続編) — テーブル物理分離 + Structured Streaming](https://qiita.com/taka_yayoi/items/98c0a7420e38ce64804a)

どちらも、トレースが保存された後にマスクする方法です。MLflow にはもう一つ、トレースを送る前にアプリ側で書き換える仕組みがあります。それがスパンプロセッサーです。

- [Unity Catalogでのトレースのガバナンスと秘匿化 (Databricks ドキュメント)](https://docs.databricks.com/aws/ja/mlflow3/genai/tracing/govern-redact)
- [Redacting Sensitive Data from Traces (MLflow ドキュメント)](https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/masking/)

目立つ機能ではありませんが、トレースを本番で使うときの前提になる部分です。Databricks Free Edition で実際に動かして、どこまで書き換わるのかを確かめました。

# スパンプロセッサーとは

## 送信前にアプリ側でスパンを書き換える

スパンプロセッサーは、スパンを1つ受け取って中身を書き換える関数です。`mlflow.tracing.configure(span_processors=[...])` に渡して登録します。

登録すると、スパンが MLflow のバックエンドに送られる前に、その関数がスパンごとに呼ばれます。処理はアプリのプロセスの中で行われます。書き換える前の値はバックエンドに送られません。

![span_processor_flow.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c1ea98d6-71fd-4621-9905-e5152d59d8e3.png)

書き換わるのは、トレースに記録される内容だけです。アプリの戻り値は元の値のまま呼び出し元に返ります。エージェントの動作は変わりません。

## 保存後にマスクする方法との違い

Databricks のドキュメントは、トレースの個人情報を扱う方法を2つに分けています。以前の記事で扱ったのは、保存後にマスクする方法でした。

| | 送信前にマスクする (今回) | 保存後にマスクする |
| --- | --- | --- |
| 処理する場所 | アプリのプロセス | Unity Catalog 上のテーブル |
| 仕組み | スパンプロセッサー | `ai_mask` を使うパイプライン、カラムマスク |
| 元の値の保存 | されない | 元のテーブルに残る (アクセスを制限する) |
| アプリのコードの変更 | 必要 | 不要 |

ドキュメントでは、機密の値を送信も保存もしないと保証したい場合は送信前のマスクを使い、すでにトレースが Unity Catalog にあってエージェントに手を入れたくない場合は保存後のマスクを使う、と整理されています。

元の値が残らないということは、後から「マスクする前の値を見たい」と思っても見られないということでもあります。どちらを選ぶかは、元の値を誰にも見せない必要があるのか、限られた人なら見てよいのかで決まります。

# 準備

Databricks Free Edition のサーバーレスノートブックで試しました。MLflow のバージョンは 3.18.0 です。

```python
%pip install -U -q "mlflow[databricks]>=3.14" openai
```

```python
dbutils.library.restartPython()
```

エクスペリメントを用意します。

```python
import re

import mlflow
from mlflow.entities import SpanType

user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/trace-span-processor")
```

トレースの中身を確認する関数も用意しておきます。直前のトレースをバックエンドから読み直して、各スパンの入力と出力を表示します。手元のメモリにある値ではなく、Databricks に保存された値を見るのが目的です。

```python
def show_trace():
    trace_id = mlflow.get_last_active_trace_id()
    # トレースは非同期で書き込まれます。読み直す前に送り切ります
    mlflow.flush_trace_async_logging()
    trace = mlflow.get_trace(trace_id)

    # トレース一覧のリクエスト列とレスポンス列に出る値です
    print(f"一覧に出る入力: {str(trace.info.request_preview)[:200]}")
    print(f"一覧に出る出力: {str(trace.info.response_preview)[:200]}")
    for span in trace.data.spans:
        print(f"[{span.span_type}] {span.name}")
        print(f"    入力: {str(span.inputs)[:200]}")
        print(f"    出力: {str(span.outputs)[:200]}")
```

# 何も登録しないと個人情報がそのまま残る

題材は、顧客の連絡先を調べるツールと、それを呼ぶエージェントです。まずは LLM を呼ばない形にして、動きが毎回同じになるようにします。メールアドレスと電話番号は架空のものです。

```python
@mlflow.trace(span_type=SpanType.TOOL)
def lookup_customer(email: str) -> dict:
    """メールアドレスから顧客情報を返す (ダミー)"""
    return {"name": "山田太郎", "phone": "090-1234-5678", "plan": "プレミアム"}


@mlflow.trace(span_type=SpanType.AGENT)
def support_agent(question: str) -> str:
    customer = lookup_customer("taro.yamada@example.com")
    return f"{customer['name']}様のご登録の電話番号は {customer['phone']} です。"


QUESTION = "登録している電話番号を教えてください。私のメールは taro.yamada@example.com です。"
```

何も登録せずに実行します。

```python
answer = support_agent(QUESTION)
print("アプリの戻り値:", answer)
show_trace()
```

```
アプリの戻り値: 山田太郎様のご登録の電話番号は 090-1234-5678 です。
一覧に出る入力: {"question": "登録している電話番号を教えてください。私のメールは taro.yamada@example.com です。"}
一覧に出る出力: "山田太郎様のご登録の電話番号は 090-1234-5678 です。"
[AGENT] support_agent
    入力: {'question': '登録している電話番号を教えてください。私のメールは taro.yamada@example.com です。'}
    出力: 山田太郎様のご登録の電話番号は 090-1234-5678 です。
[TOOL] lookup_customer
    入力: {'email': 'taro.yamada@example.com'}
    出力: {'name': '山田太郎', 'phone': '090-1234-5678', 'plan': 'プレミアム'}
```

メールアドレスと電話番号が、次の3か所に残っています。

- エージェントのスパンの入力と出力
- ツールのスパンの入力と出力
- トレース一覧に出る入力と出力

# 関数を登録してマスクする

## 登録する関数の決まり

登録する関数の決まりは次の3つです。

- 引数はスパン1つ
- `span.set_inputs()` と `span.set_outputs()` でスパンを直接書き換える
- 値を返さない

## 辞書やリストの中をたどって置き換える

スパンの入力と出力は、文字列のこともあれば、辞書やリストのこともあります。ドキュメントの例には、`str()` で全体を文字列にしてから置換するものがあります。今回は辞書の形を残したかったので、辞書やリストの中をたどって文字列だけを置き換える関数を先に作りました。

```python
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"0\d{1,4}-\d{1,4}-\d{4}")


def mask_value(value):
    """文字列の中のメールアドレスと電話番号を置き換える。辞書とリストは中をたどる"""
    if isinstance(value, str):
        value = EMAIL_PATTERN.sub("[メールアドレス]", value)
        return PHONE_PATTERN.sub("[電話番号]", value)
    if isinstance(value, dict):
        return {k: mask_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [mask_value(v) for v in value]
    return value
```

この関数を使うスパンプロセッサーを書いて登録します。

```python
def mask_pii(span) -> None:
    # 入力や出力を持たないスパンもあるので、None のときは何もしません
    if span.inputs is not None:
        span.set_inputs(mask_value(span.inputs))
    if span.outputs is not None:
        span.set_outputs(mask_value(span.outputs))


mlflow.tracing.configure(span_processors=[mask_pii])
```

## アプリの戻り値は変わらない

同じエージェントをもう一度実行します。

```python
answer = support_agent(QUESTION)
print("アプリの戻り値:", answer)
show_trace()
```

```
アプリの戻り値: 山田太郎様のご登録の電話番号は 090-1234-5678 です。
一覧に出る入力: {"question": "登録している電話番号を教えてください。私のメールは [メールアドレス] です。"}
一覧に出る出力: "山田太郎様のご登録の電話番号は [電話番号] です。"
[AGENT] support_agent
    入力: {'question': '登録している電話番号を教えてください。私のメールは [メールアドレス] です。'}
    出力: 山田太郎様のご登録の電話番号は [電話番号] です。
[TOOL] lookup_customer
    入力: {'email': '[メールアドレス]'}
    出力: {'name': '山田太郎', 'phone': '[電話番号]', 'plan': 'プレミアム'}
```

結果から分かることは3つあります。

- アプリの戻り値は元の値のまま。ユーザーには電話番号がそのまま返る
- すべてのスパンの入力と出力が置き換わった。登録した関数は、エージェントのスパンにもツールのスパンにも呼ばれている
- トレース一覧に出る入力と出力も置き換わった

3つ目は確かめておきたかった点です。トレース一覧のリクエスト列とレスポンス列は、一番上のスパンの入力と出力から作られます。スパンの中身だけが書き換わって一覧には元の値が残る、ということはありませんでした。

一方で、ツールの出力には氏名の「山田太郎」と契約プランが残っています。正規表現は、メールアドレスや電話番号のように形が決まっているものしか拾えません。

# スパンの種類で処理を変える

登録した関数は、トレース内のすべてのスパンに対して呼ばれます。`span.span_type` を見れば、スパンの種類ごとに処理を変えられます。

ツールは顧客データベースの中身を返すので、氏名のように正規表現では拾えない情報も含みます。そこで、ツールの出力は中身を見ずに丸ごと置き換える関数を追加します。

```python
def hide_tool_output(span) -> None:
    if span.span_type == SpanType.TOOL:
        span.set_outputs("[ツールの出力は記録しません]")


# 渡した順に呼ばれます。後の関数は、前の関数が書き換えた後のスパンを受け取ります
mlflow.tracing.configure(span_processors=[hide_tool_output, mask_pii])
```

`span_processors` には関数を複数渡せます。役割ごとに関数を分けておくと、後から足したり外したりしやすくなります。

```python
answer = support_agent(QUESTION)
show_trace()
```

```
一覧に出る入力: {"question": "登録している電話番号を教えてください。私のメールは [メールアドレス] です。"}
一覧に出る出力: "山田太郎様のご登録の電話番号は [電話番号] です。"
[AGENT] support_agent
    入力: {'question': '登録している電話番号を教えてください。私のメールは [メールアドレス] です。'}
    出力: 山田太郎様のご登録の電話番号は [電話番号] です。
[TOOL] lookup_customer
    入力: {'email': '[メールアドレス]'}
    出力: [ツールの出力は記録しません]
```

ツールの出力が丸ごと置き換わりました。

エージェントの出力には、氏名の「山田太郎」がまだ残っています。エージェントがツールの結果を使って応答を組み立てているためです。個人情報がどのスパンに現れるかは、ツールの出力だけを見ていても分かりません。ドキュメントの例が、ツールの出力を丸ごと置き換えたうえで、他のスパンにも正規表現をかけているのは、この理由だと思います。

氏名のように形が決まっていない情報まで拾いたい場合のために、ドキュメントには Microsoft Presidio で検出する例も載っています。今回は試していません。

# 自動トレースのスパンにも効く

ここまでは `@mlflow.trace` を自分で付けた関数でした。実際のエージェントでは、`mlflow.openai.autolog()` のような自動トレースが LLM 呼び出しのスパンを作ります。このスパンは自分で書いたコードの外で作られるので、登録した関数が呼ばれるのかを確かめます。

ツールで連絡先を調べ、その結果を LLM に渡して返信文を作らせるエージェントにします。LLM に送るプロンプトにも、LLM の応答にも個人情報が入ります。モデルは Free Edition で使える `databricks-gpt-oss-120b` です。

```python
from databricks.sdk import WorkspaceClient

LLM_ENDPOINT = "databricks-gpt-oss-120b"

mlflow.openai.autolog()
client = WorkspaceClient().serving_endpoints.get_open_ai_client()


@mlflow.trace(span_type=SpanType.TOOL)
def get_customer_contact(customer_name: str) -> str:
    """顧客の氏名から、登録されている連絡先を返す (ダミー)"""
    return "メール: hanako.sato@example.com / 電話: 080-9876-5432"


@mlflow.trace(span_type=SpanType.AGENT)
def llm_agent(question: str) -> str:
    contact = get_customer_contact("佐藤花子")
    response = client.chat.completions.create(
        model=LLM_ENDPOINT,
        messages=[
            {"role": "system", "content": "あなたはサポート担当です。調べた連絡先を使って、質問に日本語で短く答えてください。連絡先は省略せずにそのまま書いてください。"},
            {"role": "user", "content": f"質問: {question}\n調べた連絡先: {contact}"},
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content
```

`get_open_ai_client()` を呼ぶと、`databricks-openai` パッケージへの移行を勧める警告が出ます。今回はそのまま使いました。

スパンプロセッサーの登録は、前のセクションのままです。

```python
answer = llm_agent("佐藤花子さんの連絡先を教えてください。返信先は taro.yamada@example.com です。")
print("アプリの戻り値:", answer)
show_trace()
```

```
アプリの戻り値: 佐藤花子さんの連絡先は以下のとおりです。  
メール: hanako.sato@example.com  
電話: 080-9876-5432
一覧に出る入力: {"question": "佐藤花子さんの連絡先を教えてください。返信先は [メールアドレス] です。"}
一覧に出る出力: "佐藤花子さんの連絡先は以下のとおりです。  \nメール: [メールアドレス]  \n電話: [電話番号]"
[AGENT] llm_agent
    入力: {'question': '佐藤花子さんの連絡先を教えてください。返信先は [メールアドレス] です。'}
    出力: 佐藤花子さんの連絡先は以下のとおりです。  
メール: [メールアドレス]  
電話: [電話番号]
[TOOL] get_customer_contact
    入力: {'customer_name': '佐藤花子'}
    出力: [ツールの出力は記録しません]
[CHAT_MODEL] Completions
    入力: {'model': 'databricks-gpt-oss-120b', 'messages': [{'role': 'system', 'content': 'あなたはサポート担当です。調べた連絡先を使って、質問に日本語で短く答えてください。連絡先は省略せずにそのまま書いてください。'}, {'role': 'user', 'content': '質問: 佐藤花子さんの連絡先を教えてください。返
    出力: {'id': 'chatcmpl_c6a09a78-6794-490a-8b4c-6c09535fffb3_e660c196-1382-4aa1-ad4f-68a0ea8bcc82', 'choices': [{'finish_reason': 'stop', 'index': 0, 'logprobs': None, 'message': {'content': '佐藤花子さんの連絡先は以下のと
```

`CHAT_MODEL` のスパンが、自動トレースが作ったものです。入力と出力は200文字で切って表示しているので、このスパンの中身は次のセクションの画面で確認します。

ここでもアプリの戻り値は元の値のままです。LLM は元の連絡先を受け取り、元の連絡先を含む応答を返しています。スパンプロセッサーは、LLM に何を送るかには関与しません。

この点はドキュメントにも注記があります。マスクが影響するのはトレースに記録される内容だけで、エージェント自体は元の内容を受け取り、返します。個人情報を AI サービスに届かせないようにするには、Unity Catalog の[サービスポリシー](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/service-policies/)を使う、という案内です。トレースに残さないことと、モデルに送らないことは別の話なので、分けて考える必要があります。

# MLflow の UI で確認する

エクスペリメントのトレース一覧を開きます。登録なしで実行したトレースと、登録して実行したトレースが並びます。

![Screenshot 2026-11-23 at 9.15.25.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e9b57c6b-e4db-4c8f-ba22-eec7d5ea3df4.jpeg)

何度か通しで実行したので、同じ並びが繰り返されています。レスポンス列には、電話番号がそのまま出ている行と `[電話番号]` になっている行があります。どのトレースがマスクされているかが、一覧の時点で分かります。リクエスト列は途中で切れて表示されるので、メールアドレスの部分はこの画面では見えません。

LLM を呼んだトレースを開いて、`Completions` のスパンを選びます。

![Screenshot 2026-11-23 at 9.16.25.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1b7214f9-e103-4897-8534-436bcb9feda7.jpeg)

LLM に送ったメッセージの中のメールアドレスと電話番号も、LLM の応答の中のものも置き換わっています。辞書の形を残して置き換えたので、メッセージはチャットの形のまま表示されています。

# 登録を解除する

空のリストを渡すと、登録した関数がすべて外れます。

```python
mlflow.tracing.configure(span_processors=[])

answer = support_agent(QUESTION)
show_trace()
```

```
一覧に出る入力: {"question": "登録している電話番号を教えてください。私のメールは taro.yamada@example.com です。"}
一覧に出る出力: "山田太郎様のご登録の電話番号は 090-1234-5678 です。"
[AGENT] support_agent
    入力: {'question': '登録している電話番号を教えてください。私のメールは taro.yamada@example.com です。'}
    出力: 山田太郎様のご登録の電話番号は 090-1234-5678 です。
[TOOL] lookup_customer
    入力: {'email': 'taro.yamada@example.com'}
    出力: {'name': '山田太郎', 'phone': '090-1234-5678', 'plan': 'プレミアム'}
```

解除後のトレースには元の値が残ります。登録は、実行中のプロセスに対する設定です。ノートブックで登録しても、別の場所で動くエージェントには引き継がれません。エージェントのコードの中で、起動時に登録します。

トレースの設定全体を初期状態に戻したい場合は、`mlflow.tracing.reset()` も使えます。

# まとめ

MLflow のスパンプロセッサーを Databricks Free Edition で試して分かったことをまとめます。

- `mlflow.tracing.configure(span_processors=[...])` に関数を渡すと、スパンが送られる前にその関数がスパンを書き換える
- **書き換わるのはトレースだけ。アプリの戻り値も、LLM に送る内容も元の値のまま**
- スパンの入力と出力だけでなく、トレース一覧に出る入力と出力も置き換わる
- **`mlflow.openai.autolog()` が作る LLM 呼び出しのスパンにも、登録した関数が呼ばれる**
- `span.span_type` を見れば、ツールの出力だけ丸ごと置き換えるような使い分けができる
- 関数は複数渡せて、渡した順に呼ばれる
- 正規表現で拾えるのは、形が決まっている情報だけ。氏名はツールの出力を隠しても、エージェントの応答に残った
- 空のリストを渡すと解除される

一番の収穫は、「トレースに残さない」と「モデルに送らない」が別の話だと、実行結果で確認できたことでした。スパンプロセッサーが守るのはトレースです。保存後にマスクする方法と違って元の値がどこにも残らないので、機密の値を保存しないと言い切りたい場面に向いています。その代わり、何をマスクするかはアプリのコードで決めることになります。どのスパンに何が入るかを実際のトレースで見てから、関数を書くのが良さそうです。

# 参考リンク

- [Unity Catalogでのトレースのガバナンスと秘匿化 (Databricks ドキュメント)](https://docs.databricks.com/aws/ja/mlflow3/genai/tracing/govern-redact)
- [Redacting Sensitive Data from Traces (MLflow ドキュメント)](https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/masking/)
- [サービスポリシー (Databricks ドキュメント)](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/service-policies/)
- [MLflowトレースのPIIマスキング — Unity Catalogカラムマスクとai_mask() ETLの2層構成](https://qiita.com/taka_yayoi/items/4cd0e5f814d1dfc30699)
- [MLflowトレースのPIIマスキング (続編) — テーブル物理分離 + Structured Streaming](https://qiita.com/taka_yayoi/items/98c0a7420e38ce64804a)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: MLflowのGuidelinesジャッジの判定がぶれるとき、ガイドラインの書き方で直せること
tags:
  - Databricks
  - MLflow
  - LLM
  - 評価
  - 生成AI
private: false
updated_at: '2026-10-29T20:08:22+09:00'
id: 6db8b9fdbbff78d2ef34
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

MLflowの `Guidelines` ジャッジは、自然言語で書いたルールに応答が従っているかを yes/no で判定する組み込みのLLMジャッジです。ルールを文章で書くだけで評価を始められるので、エージェントの評価で最初に使われることが多いジャッジだと思います。

- [LLMジャッジガイドラインを作成する](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/concepts/judges/guidelines)
- [カスタムジャッジを作成する make_judge()](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/custom-judge/create-custom-judge)

一方で、ガイドラインを数十本並べて評価すると、同じ応答なのに評価のたびに yes と no が入れ替わるものが出てきます。LLMで判定している以上、多少の揺れはあります。ただ、ガイドラインを1本ずつ読み直すと、ジャッジが推測で判断するしかない書き方がいくつも見つかります。

今回は MLflow 3.16.1 のソースを読み、`Guidelines` ジャッジが判定に何を使っているかを確認したうえで、判定がぶれやすいガイドラインの型と直し方を整理しました。例を使った判定(Few-shot)やtemperatureの指定をしたいときにどう書くかも含めて書いていきます。

# Guidelinesジャッジが判定に使っているもの

書き方の話に入る前に、ジャッジに何が渡っているかを押さえておきます。ここを知っていると、なぜぶれるのかの見当がつきやすくなります。

## 見ているのはrequestとresponseの文面だけ

`Guidelines` ジャッジは、トレースの inputs から `request` を、outputs から `response` を取り出して、ガイドラインと照らし合わせます。

- [ガイドライン審査員がアプリの入力と出力を解析する方法](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/concepts/judges/guidelines#ガイドライン審査員がアプリの入力と出力を解析する方法)

![guidelines_judge_inputs.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4e87c0c3-b7e5-4832-9481-a8ddb2d11530.png)

子スパンのツール呼び出しは見ていません。たとえば「チケットを起票したら起票番号を伝えること」というガイドラインでは、実際に起票したかどうかを、ジャッジは応答の文面から読み取ることになります。

会話全体を見て判定したいガイドラインも同じです。前のターンが request と response に入っていなければ、ジャッジは前の会話を推測で補うしかありません。

## ガイドラインの文面がそのまま判定基準になる

オープンソース版のMLflowでは、`Guidelines` のプロンプトは次のような短い定型文です。

```python
GUIDELINES_PROMPT_INSTRUCTIONS = """\
Given the following set of guidelines and some inputs, please assess whether the inputs fully \
comply with all the provided guidelines. Only focus on the provided guidelines and not the \
correctness, relevance, or effectiveness of the inputs.

<guidelines>
{{guidelines}}
</guidelines>
{{guidelines_context}}\
"""
```

この定型文の中に、ガイドラインの文面と request/response が差し込まれるだけです。判定の基準として働くのは、実質ガイドラインの文面しかありません。

なお、`model=` を指定しない場合は、Databricks側で管理されている既定のジャッジで判定されます。MLflowのコードでも `model == "databricks"` のときは別の実装を呼ぶ分岐になっていて、上の定型文がそのまま使われるとは限りません。オープンソース版のプロンプトには「どのガイドラインも当てはまらなければ yes」という規則がありますが、既定のジャッジでもこれに頼れるとは考えないほうが安全です。

## 例もtemperatureも渡す口がない

`Guidelines` の引数を確認してみます。

```python
from mlflow.genai.scorers import Guidelines

print(list(Guidelines.model_fields))
```

`name`、`guidelines`、`model` に加えて `inference_params` も出てきます。ここがハマりどころです。`inference_params` は組み込みジャッジ共通の基底クラスが持っているフィールドで、`Guidelines(inference_params={"temperature": 0.0})` と書いてもエラーにはなりません。ただ、3.16.1 の `Guidelines.__call__` が判定を呼び出す部分を見ると、渡しているのは `guidelines`、`context`、`name`、`model`、`extra_headers` だけです。

```python
feedback = judges.meets_guidelines(
    guidelines=self.guidelines,
    context={
        "request": parse_inputs_to_str(fields.inputs),
        "response": parse_outputs_to_str(fields.outputs),
    },
    name=self.name,
    model=self.model,
    extra_headers=self.extra_headers,
)
```

例(Few-shot)を渡す引数もありません。`Guidelines` はルールを文章で書くだけで使えることを優先したジャッジで、例や推論パラメータを細かく制御したい場合は `make_judge()` に切り替える、という役割分担なのだと思います。

# 判定がぶれやすいガイドラインの型

ここからが本題です。以下では、社内ITヘルプデスクのエージェントを評価する場面を例にします。例はすべて説明用に作ったものです。

## 判定に必要な情報がジャッジにない

```text
トラブルシューティングでは、ユーザーの手間が少ない手順から順に案内すること。
```

人が読むと自然な文ですが、ジャッジは「どの手順の手間が少ないか」を知りません。知らない以上、毎回それらしい順序を推測して判定することになります。ジャッジが推測する余地が一番大きいのがこの型です。

順序の基準そのものをガイドラインに書きます。

```text
VPNに接続できない相談では、次の順に手順を案内すること。
1. VPNクライアントの再起動
2. ネットワークの切り替え
3. 証明書の再取得
一覧にない手順は、一覧の手順の後に案内すること。
VPNの相談がない会話、案内した手順が1つだけの会話は適合とする。
```

順序・範囲・許可する表現のように、判定の基準になる情報は一覧で書く。これだけでジャッジが推測する余地がかなり減ります。

## 対象外のときの扱いが書かれていない

```text
ユーザーが既に試した手順を、再度案内しないこと。
```

ユーザーが何も試していない会話を、この基準で yes にするか no にするか。書かれていないので、ジャッジの判断が分かれます。条件付きのガイドラインには、条件に当てはまらないときの扱いを必ず書きます。

```text
ユーザーが既に試した手順を、再度案内しないこと。
ユーザーが試した手順に触れていない会話は適合とする。
```

地味な一文ですが、ガイドラインを数十本並べると、この一文がないものが意外と混ざります。見直すときに最初に確認するとよい点です。

## 1本に逆向きの要求が入っている

```text
回答は簡潔にすること。ユーザーが詳しい説明を求めた場合は省略しないこと。
```

「短くしろ」と「省略するな」が1本に入っています。`Guidelines` は1本につき yes/no を1つしか返さないので、no になってもどちらで落ちたのかが判定結果から分かりません。条件ごとに満たすかの判断も揺れやすくなります。公式ドキュメントでも、複雑な要件は1要件1行の箇条書きにするよう勧めています。

- [効果的なガイドラインを書くためのベストプラクティス](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/concepts/judges/guidelines#効果的なガイドラインを書くためのベストプラクティス)

2本に分けて、後者には対象外の扱いを足します。

```text
同じ内容の繰り返しや、質問と関係のない前置きを入れないこと。
```

```text
ユーザーが詳しい説明を求めた場合は、必要な内容を省略しないこと。
詳しい説明を求めていない依頼は適合とする。
```

## 「など」で終わる列挙

```text
社外秘の情報(顧客名、売上など)を回答に含めないこと。
```

「など」の先にどこまで含まれるかは、ジャッジが毎回推測します。判定に使う語は閉じた一覧にします。

```text
次のいずれかを回答に含めないこと:顧客名、売上金額、未発表の製品名。
```

# 書き方を変えるだけでは揃わないもの

ここまでの型はガイドラインの文面を直せば解消します。残るのは、そもそもLLMで判定しなくてよいものと、文面を細かくしても基準が揃わないものです。

## 文字列で判定できるものはコードで判定する

```text
「させていただきます」を使わないこと。
```

特定の語を含むかどうかは、LLMを使わずにコードで判定できます。判定は毎回同じになり、ジャッジモデルの呼び出し費用もかかりません。

- [カスタムスコアラー](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/custom-scorers)

```python
from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer

BANNED = ["させていただきます"]

@scorer
def banned_phrase(outputs) -> Feedback:
    # outputs の形式はアプリによって違う。応答テキストの取り出し方は合わせて変える
    text = outputs if isinstance(outputs, str) else str(outputs)
    hits = [w for w in BANNED if w in text]
    return Feedback(
        value="no" if hits else "yes",
        rationale=f"{hits} を含む" if hits else "禁止表現を含まない",
    )
```

LLMジャッジと同じく `mlflow.genai.evaluate()` の `scorers` に並べて使えます。

## 拾って照らし合わせる判定は手順で書く

会話の中から該当する発話を探して照らし合わせる判定は、組み込みの `ConversationCompleteness` のプロンプトが参考になります。

```text
First, list all explicit user requests made throughout the conversation in the rationale section.
Second, for each request, determine whether it was addressed by the assistant by the end of the conversation,
and **quote** the assistant's explicit response in the rationale section if you judge the request as addressed.
(中略)
Output "no" only if one or more user requests remain unaddressed in the final state. Output "yes" if all requests were addressed.
```

(訳)まず、会話中のユーザーの明示的な依頼をすべて rationale に列挙する。次に、依頼ごとに会話の終わりまでに対応されたかを判断し、対応済みと判断した場合はアシスタントの応答を rationale に**引用**する。(中略)未対応の依頼が1件以上残っている場合だけ "no" を出力し、すべて対応済みなら "yes" を出力する。

組み込みジャッジのプロンプトが長いのは、文章を丁寧に書いているからではありません。対象を列挙する、1件ずつ照らし合わせる、no にする条件を決める、という判定の手順が書いてあるからです。自分のガイドラインも同じ形にできます。

```text
1. ユーザーが既に試した手順を列挙する
2. 列挙した手順ごとに、後のターンで再び案内した応答を引用する
3. 1件でもあれば no、なければ yes とする
```

手順で書くと、ジャッジが毎回同じものを拾って判定し、拾ったものが rationale にも残ります。no になったときに理由を追いやすくなるのも利点です。

## 主観で判断する観点は例で揃える

「関係のない前置き」「押しつけがましい言い方」のように、読む人によって判断が分かれる観点は、文面を細かくしても基準が揃いません。yes と no の両方の例を、理由を付けて渡します。

`Guidelines` には例を渡せないので、`make_judge()` の指示文に例を書きます。フィールド型(`{{ inputs }}` と `{{ outputs }}` を使う形)の `make_judge()` は、`model=` を省略すると `Guidelines` と同じ既定のDatabricksジャッジで動きます。

```python
from typing import Literal
from mlflow.genai.judges import make_judge

INSTRUCTIONS = """\
ユーザーの依頼 {{ inputs }} に対するエージェントの応答 {{ outputs }} を評価する。

ガイドライン:ユーザーの利用状況に触れる場合は、提案の根拠として必要なときだけ述べること。

判定の規則:
- 応答が利用状況に触れていない場合は yes とする。
- 利用状況に触れていて、提案の根拠として述べている場合は yes とする。
- 提案と関係なく、ユーザーの行動を述べている場合は no とする。

例:
- 応答「毎朝VPNの再接続が発生しているので、自動再接続の設定をおすすめします。」→ yes
  (理由:提案の根拠として利用状況を示している)
- 応答「昨日は夜11時までログインしていましたね。」→ no
  (理由:提案と関係なく行動を述べている)

yes か no で答える。
"""

usage_judge = make_judge(
    name="usage_mention",
    instructions=INSTRUCTIONS,
    # 取りうる値を固定します。Guidelines と同じ yes/no に揃えておくと結果を並べて比べやすい
    feedback_value_type=Literal["yes", "no"],
)
```

例に使った会話は評価データから外してください。同じ会話が両方にあると、その会話の判定だけ実際より正しく見えます。

## 人が付けた判定でジャッジを合わせる

例を手で選ぶ代わりに、人が yes/no と理由を付けたトレースからジャッジを調整する方法もあります。既定の最適化手法である MemAlign は、人の判定理由から規則を抽出して指示に加え、判定のたびにラベルの中から近い例を取り出して使います。

- [LLM judgeを人間のフィードバックに合わせる](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/align-judges)
- [MemAlign(MLflowドキュメント)](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/memalign/)

ドキュメントに書かれている条件は次のとおりです。

- MLflow 3.14.0 以上。対象は組み込みジャッジと `make_judge()` で作ったジャッジ
- トレースは最低10件、50〜100件でより良い結果になる
- 否定的な例(no)を3割以上含め、評価の理由も付ける
- `ConversationCompleteness` のようなセッションレベル(複数ターン)のジャッジには使えない

ジャッジの判定を確かめるために人が判定した会話があれば、その yes/no と理由がそのままラベルになります。

## temperatureを指定したいとき

`make_judge()` で `model=` を明示し、`inference_params` で渡します。

```python
usage_judge_t0 = make_judge(
    name="usage_mention",
    instructions=INSTRUCTIONS,
    feedback_value_type=Literal["yes", "no"],
    model="databricks:/databricks-gpt-oss-120b",
    # temperature を下げると判定の再現性が上がる方向に働きます
    inference_params={"temperature": 0.0},
)
```

- [make_judge の API リファレンス](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.make_judge)

ただし、モデルや temperature を変えても、判定に必要な情報がない、対象外の扱いがない、といった書き方の問題は解消しません。ジャッジが推測している部分は、モデルを替えても推測のままです。先にガイドラインを直してから、モデルを比べる順番が良さそうです。

# まとめ

`Guidelines` ジャッジの判定がぶれる理由と書き方を整理しました。

- `Guidelines` ジャッジが見るのは request と response の文面だけ。子スパンのツール呼び出しは見ない
- **判定の基準として働くのはガイドラインの文面だけ。順序・範囲・許可する表現は一覧で書く**
- **条件付きのガイドラインには「当てはまらないときは適合」を必ず書く**
- 1本のガイドラインで判定する観点は1つ。逆向きの要求は分ける
- 特定の語を含むかどうかは、コードのスコアラーで判定すれば毎回同じ結果になる
- 拾って照らし合わせる判定は、`ConversationCompleteness` と同じく手順で書く
- **`Guidelines` には例を渡す引数がない。`inference_params` は受け付けられるが判定には渡されない(3.16.1)**。例や temperature を使いたいときは `make_judge()` に切り替える

一番の収穫は、ジャッジに渡っているのがガイドラインの文面と request/response だけだと、ソースで確かめられたことでした。人が読んで自然な文ほど、書き手の頭の中にある前提が省かれています。ジャッジには文面しか渡っていないと意識して読み直すと、直すべき箇所が見えてきます。

# 参考リンク

- [LLMジャッジガイドラインを作成する](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/concepts/judges/guidelines)
- [カスタムジャッジを作成する make_judge()](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/custom-judge/create-custom-judge)
- [カスタムスコアラー](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/custom-scorers)
- [LLM judgeを人間のフィードバックに合わせる](https://docs.databricks.com/aws/ja/mlflow3/genai/eval-monitor/align-judges)
- [MemAlign(MLflowドキュメント)](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/memalign/)
- [Guidelines のプロンプト(MLflow 3.16.1)](https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/genai/judges/prompts/guidelines.py)
- [ConversationCompleteness のプロンプト(MLflow 3.16.1)](https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/genai/judges/prompts/conversation_completeness.py)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

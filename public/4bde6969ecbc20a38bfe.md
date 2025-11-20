---
title: DSPy + MLflowによるLLMプログラムの自動最適化
tags:
  - Databricks
  - MLflow
  - LLM
  - DSPy
private: false
updated_at: '2025-01-13T14:02:13+09:00'
id: 4bde6969ecbc20a38bfe
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらをウォークスルーします。

https://notebooks.databricks.com/devrel/mlflow/2024-11-27-dspy.html

以前にこちらの記事を書いていますが、いまだに勉強中です。

https://qiita.com/taka_yayoi/items/a6a8cd0329e412f4d6ee

https://qiita.com/taka_yayoi/items/2985f7ad17062446efab

https://qiita.com/taka_yayoi/items/a9827246cd214f3f8f4e

DBR 16.1MLを使っています。

# DSPy + MLflowによるLLMプログラムの自動最適化

DSPy（Declarative Self-improving Python）は、ユーザーがプロンプトではなくPythonコードを書いてLLMを構築および指示することを可能にするオープンソースフレームワークです。DSPyには、LLMの動作を指示し、プロンプトと重みを自動的に最適化し、AIシステムのパフォーマンスを評価するためのツールが含まれています。

MLflowのDSPyとのネイティブ統合により、AIシステムのパフォーマンスを追跡および視覚化し、DSPyプログラムをMLflowモデルとしてログに記録することができます。

このノートブックでは、LMStudioを介してローカルで実行されるLlama-3.2-3B-Instructを使用してDSPyを使用します。OpenAI互換のエンドポイントで実行されている他のモデルに置き換えることもできます。DSPyを使用して、arXivからの研究論文を異なる複雑さのレベルで要約するシステムを構築します。

LMStudioでローカル推論サーバーを設定する際には、`ctx_length`パラメータを増やし、オーバーフローポリシーを中央切り捨てに設定して、指示を含むシステムプロンプトが保持されるようにする必要があることに注意してください。

まず、MLflow実験を設定し、DSPyの自動ロギングを有効にして、すべてのDSPy実行のトレースを簡単に表示できるようにします。

MLflowを最新にしておく必要があります。

```py
%pip install dspy-ai arxiv PyPDF2
%pip install -U mlflow
dbutils.library.restartPython()
```

```py
import dspy
import mlflow
from rich import print
from dotenv import load_dotenv
import os
load_dotenv()

mlflow.set_experiment("/Workspace/Users/takaaki.yayoi@databricks.com/20250113_DSPy/dspy-paper-summarization")
mlflow.dspy.autolog()
```

次に、使用するLLMを設定します。この場合、OpenAI APIを使用します。OpenAI互換のエンドポイントで実行されている他のモデルに置き換えることもできます。また、LMStudioを介してローカルで実行されるLlama-3.2-3B-Instructを使用することも可能です。

```py
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="demo-token-takaaki.yayoi", key="openai_api_key")
```

```py
# ローカルエンドポイントでLMを構成
lm_local = dspy.LM(
    #"openai/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",  # モデル名
    "openai/unsloth/Llama-3.2-3B-Instruct-GGUF",
    api_base="http://localhost:1234/v1",  # ローカルエンドポイント
    api_key="whatever",  # ローカルエンドポイント用の空のapi_key
    model_type='chat',  # チャットモデルタイプを指定
    cache=False  # キャッシュを無効にする
)

lm_anthropic = dspy.LM(
    "anthropic/claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

lm_openai = dspy.LM(
    "openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)

lm_gemini = dspy.LM(
    "gemini/gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)

lm_gemini_sm = dspy.LM(
    "gemini/gemini-1.5-flash-8b",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# これをDSPyのデフォルトLMとして設定
dspy.configure(lm=lm_openai)
```

```py
# LLMが動作していることを確認
print(lm_openai("MLflowは何のために使うのかを教えてください")[0])
```
```
MLflowは、機械学習のライフサイクルを管理するためのオープンソースプラットフォームです。具体的には、以下のような目的
で使用されます。

1. **実験の追跡**: 
MLflowは、異なるモデルやハイパーパラメータの実験を追跡する機能を提供します。これにより、どの実験が最も成功したかを
簡単に比較できます。

2. **モデルの管理**: 
MLflowは、トレーニングしたモデルを保存、バージョン管理、デプロイするための機能を提供します。これにより、モデルの再
利用や更新が容易になります。

3. **プロジェクトの構成**: MLflow 
Projectsを使用すると、機械学習プロジェクトをパッケージ化し、再現可能な形で共有できます。これにより、他のチームメン
バーや外部の研究者が同じ環境で実行できるようになります。

4. **モデルのデプロイ**: MLflowは、トレーニングしたモデルをさまざまなプラットフォーム（例えば、REST 
APIとして、またはクラウドサービス上で）にデプロイするための機能を提供します。

5. **統合**: 
MLflowは、TensorFlow、PyTorch、Scikit-learnなど、さまざまな機械学習ライブラリやフレームワークと統合できるため、柔軟
に使用できます。

これらの機能により、MLflowは機械学習プロジェクトの効率を向上させ、チーム間のコラボレーションを促進します。
```

DSPyの自動ロギングによってキャプチャされたトレースをすでに確認できます:

![Screenshot 2025-01-13 at 13.49.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a40fadcd-f802-1684-85ab-446bb1cd8748.png)

さて、システムを構築するために必要なものは次のとおりです:

1. arxiv IDから論文を取得する方法
2. 要約の複雑さのレベルを指定する方法
3. 要約を評価する方法

これらのコンポーネントを統合することで、DSPyがPythonそのものであることを示します。プロンプトの観点で考える必要はなく、決定論的なコンポーネント（例：論文の取得）とLLMを活用したコンポーネント（例：論文の要約）をPythonコードで記述できます。

今のところ、論文からテキストを抽出して操作することに焦点を当てますが、このアプローチは画像や他のデータモダリティにも拡張できます。

```py
import arxiv
import PyPDF2
import io
import requests

def get_paper_from_arxiv(arxiv_id: str) -> tuple[str, str]:
    """
    arxiv論文をダウンロードしてテキストを抽出する。
    
    引数:
        arxiv_id (str): arxiv ID (例: '2311.12399' または 'arxiv:2311.12399')
    
    戻り値:
        tuple[str, str]: 論文の (タイトル, テキスト)
    """
    client = arxiv.Client()

    # arxiv IDをクリーンアップ
    arxiv_id = arxiv_id.replace('arxiv:', '').strip()
    
    # 論文を検索
    search = client.results(arxiv.Search(id_list=[arxiv_id]))
    paper = next(search)
    
    # PDFをダウンロード
    response = requests.get(paper.pdf_url)
    pdf_file = io.BytesIO(response.content)
    
    # PDFからテキストを抽出
    reader = PyPDF2.PdfReader(pdf_file)
    text = ' '.join(page.extract_text() for page in reader.pages)
    
    return paper.title, text
```

```py
# 論文の取得

paper_ids = ["2411.15138", "2411.15124", "2411.10442", "2411.10958", "2411.12372"]
papers = []
for paper_id in paper_ids:
    papers.append(get_paper_from_arxiv(paper_id))
```

## DSPyシグネチャの設定

DSPyシグネチャは、DSPyプログラムの入力と出力を定義するPythonクラスです。これは、プログラムに渡されるデータの構造を指定するために使用されます。

シグネチャは主に入力フィールド（`dspy.InputField`）と出力フィールド（`dspy.OutputField`）で構成されます。入力フィールドはプログラムに渡されるデータを説明し、出力フィールドはプログラムから返されるデータを説明します。クラスのドキュメンテーション文字列には、指示やタスクの説明も含まれます。

また、シグネチャを入力から出力へのマッピングとして文字列で簡潔に定義することもできます。例えば、'text: str -> sentiment: str'のように。

論文要約タスクのために、論文のタイトル、テキスト、および複雑さのレベルを入力として受け取り、指定された複雑さのレベルで要約を出力するシグネチャを定義します。

```py
from typing import Literal

class PaperSummarySignature(dspy.Signature):
    """指定された複雑さのレベルで提供された研究論文の要約を生成します。
    要約は最大4段落までで、指定された複雑さのレベルに合わせて調整されるべきです。
    
    複雑さのレベル:
    1: 高校レベル - 基本的な語彙と簡単な概念を使用します。専門用語は避けます。
    2: 初期の学部生 - 基本的な専門用語を説明付きで導入します。
    3: 上級学部生 - 中程度の専門用語を使用し、時折説明を加えます。
    4: 大学院生 - 最小限の説明で専門用語を自由に使用します。
    5: 専門家 - 高度な専門用語を使用し、深い専門知識を前提とします。
    """
    
    # 入力フィールド
    title: str = dspy.InputField(description="研究論文のタイトル")
    complexity_level: Literal[1, 2, 3, 4, 5] = dspy.InputField(
        description=(
            "生成される要約の希望する複雑さのレベル。1（高校レベル）から5（大学院生レベル）まで"
        )
    )
    text: str = dspy.InputField(description="単一の研究論文の全文内容")
    
    # 出力フィールド
    summary: str = dspy.OutputField(description="指定された複雑さのレベルでの論文の要約")
```

この後の最適化をデモンストレーションするために、以降ではあえてコメントが貧弱な`WorsePaperSummarySignature`を使用します。

```py
from typing import Literal

class WorsePaperSummarySignature(dspy.Signature):
    """指定された複雑さのレベルで提供された研究論文の要約を生成します。
    要約は最大4段落までで、指定された複雑さのレベルに合わせて調整されるべきです。
    """
    
    # 入力フィールド
    title: str = dspy.InputField(description="研究論文のタイトル")
    complexity_level: Literal[1, 2, 3, 4, 5] = dspy.InputField(
        description=(
            "生成される要約の希望する複雑さのレベル。1（高校レベル）から5（大学院生レベル）まで"
        )
    )
    text: str = dspy.InputField(description="単一の研究論文の全文内容")
    
    # 出力フィールド
    summary: str = dspy.OutputField(description="指定された複雑さのレベルでの論文の要約")
```

## DSPyモジュールのセットアップ

DSPyモジュールは`dspy.Module`を継承するPythonクラスです。典型的なモジュールには以下のコンポーネントがあります:
1. 必要なコンポーネントでモジュールを初期化する`__init__`メソッド
2. モジュールのコアロジックを定義する`forward`メソッド

シグネチャはモジュールのインターフェースを定義し、入力と出力を指定します。シグネチャは入力と出力の「契約」を定義し、モジュールはLLMを使用して入力を出力に処理する実際のロジックを実装します。

DSPyには、`dspy.ChainOfThought`や`dspy.Predict`など、一般的なLLMパターンを実装する多くの組み込みモジュールがあります。詳細は[こちら](https://dspy.ai/learn/programming/modules/#what-other-dspy-modules-are-there-how-can-i-use-them)をご覧ください。

指定された複雑さのレベルで論文を要約するために、`dspy.ChainOfThought`モジュールをラップするシンプルなモジュールをセットアップします。

```py
class Summarize(dspy.Module):
    def __init__(self):
       # self.summarize = dspy.ChainOfThought(PaperSummarySignature)
        self.summarize = dspy.Predict(PaperSummarySignature,
                                      temperature=0.8)


    def forward(self, title: str, text: str, complexity_level: int):
        summary = self.summarize(
            title=title,
            text=text,
            complexity_level=complexity_level
        )
        return summary

class SummarizeWorsePrompt(dspy.Module):
    def __init__(self):
        self.summarize = dspy.Predict(WorsePaperSummarySignature,
                                      temperature=0.8)

    def forward(self, title: str, text: str, complexity_level: int):
        summary = self.summarize(
            title=title,
            text=text,
            complexity_level=complexity_level
        )
        return summary
```

## モジュールのテスト

```py
program = SummarizeWorsePrompt()
paper = papers[0]

print(program(title=paper[0], text=paper[1][:50000], complexity_level=5)["summary"])
```

```
本研究では、3Dオブジェクト向けの物理ベースのマテリアルを生成するための新たなフレームワーク「Material 
Anything」を提案します。このフレームワークは、従来の複雑なパイプラインや特定の最適化に依存することなく、照明条件の
多様性に適応可能な、完全自動化されたエンドツーエンドのソリューションを提供します。私たちのアプローチは、事前学習さ
れた画像拡散モデルを活用し、三重ヘッドアーキテクチャとレンダリング損失を用いて安定性とマテリアルの質を向上させます
。

「Material 
Anything」は、テクスチャのあるオブジェクトとテクスチャのないオブジェクトの両方を効果的に処理するために、動的スイッ
チャーとして機能する信頼度マスクを導入しています。このマスクを用いて、さまざまな照明条件において一貫したUV準備済み
のマテリアル出力を保証するための進行的なマテリアル生成戦略を採用しています。実験結果は、私たちの方法が多様なオブジ
ェクトカテゴリおよび照明条件において既存の手法を上回ることを示しています。

本論文の貢献として、物理ベースのマテリアル生成のための完全自動化されたモデルを実現し、異なる照明条件での生成におい
て優れたパフォーマンスを達成したことを挙げます。また、信頼度に基づくマテリアル生成スキームとUV空間内でのマテリアル
精製を統合することで、一貫性のある高品質なマテリアル生成を実現しました。
```

```py
print(program(title=paper[0], text=paper[1][:50000], complexity_level=1)["summary"])
```

```
この研究論文では、3Dオブジェクトのための物理ベースの材料を生成するための新しいフレームワーク「Material 
Anything」を提案しています。このアプローチは、様々な照明条件下でも使用でき、従来の複雑なプロセスや特定の最適化に依
存することなく、3Dメッシュに適用可能です。提案された方法は、事前に学習された画像拡散モデルを利用しており、安定性と
材料の質を向上させるための三重ヘッドアーキテクチャとレンダリング損失を組み合わせています。

新しいフレームワークは、テクスチャなし、アルベドのみ、生成された、スキャンしたオブジェクトなど、さまざまな種類の3D
メッシュに適応できるように設計されています。また、生成プロセスを導くための自信マスクを導入し、照明情報に基づいて材
料を効果的に生成できるようにしています。実験結果は、提案した方法が多様なオブジェクトカテゴリと照明条件において、既
存の手法を上回る性能を示していることを示しています。

最終的には、このアプローチは、従来の手法と比べて高品質な材料マップを生成する能力を持ち、ビデオゲームやバーチャルリ
アリティ、映画制作などのアプリケーションにおいて、リアルで一貫した3Dオブジェクトの表現を可能にします。
```

複雑度`complexity_level`を変えても、2つの生成された要約の複雑さには大きな違いがないようです！DSPyの評価および最適化ツールを使用して、プロンプトを手動で調整することなくプログラムを改善するのに役立てることができます。

## 評価

DSPyの評価はDSPyメトリクスに基づいています。メトリクスは、通常、例と比較して、特定の基準に基づいて与えられた出力の品質をスコアリングする関数です。

メトリクスは単純なループで実行することも、`dspy.evaluate`モジュールを使用してよりプログラム的に実行することもできます。

メトリクス自体もDSPyモジュールであるため、反復と改善の対象となります。

論文の要約が適切な複雑さのレベルにあるかどうかを評価したいと考えています。そのために、要約を取り、適切な複雑さのレベルにあるかどうかを判断する別のDSPyプログラムを使用します。まずシグネチャを定義し、次にメトリクスのロジックを実装するモジュールを定義するアプローチに従います。

```py
class EvaluateSummary(dspy.Signature):
    """研究論文の要約を評価し、その複雑さのレベルを1から5までで評価します。

    評価は以下の複雑さのレベルに対応します:
        1: 初級 - 技術的な背景がない一般の人々に適している
        2: 基本 - 学部生や技術愛好家に適している
        3: 中級 - 大学院生や業界の実務者に適している
        4: 上級 - 専門家や研究者に適している
        5: 専門 - この特定の研究分野の専門家に適している
    """

    summary: str = dspy.InputField(description="研究論文の要約")
    complexity_level: Literal[1, 2, 3, 4, 5] = dspy.OutputField(description="要約の複雑さのレベル")


class Metric(dspy.Module):
    """要約とその複雑さのレベルを基に、要約が正しい複雑さのレベルにあるかどうかを判断します。"""
    def __init__(self, model=None):
        # 特定のモデルを渡すか、デフォルトの設定済みモデルを使用する
        if model:
            with dspy.context(lm=model):
                self.eval_complexity = dspy.ChainOfThought(EvaluateSummary)
        else:
            self.eval_complexity = dspy.ChainOfThought(EvaluateSummary)
    
    def forward(self, example, pred, trace=None):
        """
        パラメータ:
        - example: 入力フィールドと期待される出力を含むDSPy Example
        - pred: 生成されたフィールドを含むプログラムからの予測
        - trace: 最適化プロセスを追跡するためのブートストラップ中に使用
        
        戻り値:
        - ブートストラップ中 (traceがNoneでない場合) はbool
        - 通常の評価中はfloat (0-1)
        """
        # 生成された要約の予測された複雑さのレベルを取得
        predicted = self.eval_complexity(summary=pred.summary).complexity_level
        
        # 生スコアを計算 (0-5)
        score = 5 - abs(predicted - example.complexity_level)
        
        # ブートストラップと評価の異なる動作
        if trace is not None:
            return score >= 4  # ブートストラップには高品質の例のみを使用
        return score / 5.0    # 評価のためにスコアを正規化
```

## メトリックのテスト

```py
# 入力データを使用して例を作成
example = dspy.Example(
    title=paper[0],
    text=paper[1],
    complexity_level=1
).with_inputs("title", "text", "complexity_level")

pred = program(
    title=example.title, 
    text=example.text, 
    complexity_level=example.complexity_level
)

metric_program = Metric(model=lm_openai)
score = metric_program(example, pred)

print(f"メトリックスコア: {score}")  # 0から1の値を返します
```
```
メトリックスコア: 0.6
```

## 評価データセットの作成

DSPyプログラムとその評価手段が揃ったので、例とスコアのデータセットを作成し、それを使ってプログラムを反復的に改善していきます。

そのためには、プログラムの入力と出力、およびスコアを含む`dspy.Example`オブジェクトを定義する必要があります。

5つの異なる論文と5つの異なる複雑さレベルを使用して、25の例のデータセットを作成します。実際のシナリオでは、プログラムをトレーニングするために、より大きく多様なデータセットを使用することをお勧めします。

```py
from tqdm.notebook import tqdm
import random

mlflow.dspy.autolog()

# サンプルのデータセットを作成
dataset = []

total_iterations = len(papers) * 5  # 論文ごとに5つの複雑さのレベル
with tqdm(total=total_iterations, desc="要約を生成中") as pbar:
    for paper in papers:
        title, text = paper
        
        # 各複雑さのレベル（1-5）に対して要約を生成
        for complexity in range(1, 6):
            result = program(
                title=title,
                text=text[:50000] + "... [truncated]", # トークンの問題を避けるためにテキストを切り捨て
                complexity_level=complexity
            )
            
            # 入力フィールドを含むDSPy Exampleオブジェクトを作成
            example = dspy.Example(
                title=title,
                text=text[:50000] + "... [truncated]",
                complexity_level=complexity,
                summary=result.summary
            ).with_inputs("title", "text", "complexity_level")  # どのフィールドが入力かを指定
            
            dataset.append(example)
            pbar.update(1)
```

データセットが揃ったので、DSPyを使って評価を実行できます。

```py
from dspy.evaluate import Evaluate

# 評価器を設定
evaluator = Evaluate(
    devset=dataset,
    metric=metric_program,  
    num_threads=4,  
    display_progress=True,
    display_table=25
)

# ベースラインプログラムを評価
print("ベースラインプログラムを評価中...")
results = evaluator(program)
```

![Screenshot 2025-01-13 at 13.56.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9313d594-ce8e-14f6-bcb7-fd291e5e5057.png)

## プログラムの最適化

```py
from dspy.teleprompt import MIPROv2

optim = MIPROv2(
    metric = metric_program,
    prompt_model=lm_openai,
    task_model=lm_openai,
    auto="light"
)

# プログラムを最適化
print("MIPROを使用してプログラムを最適化中...")
optimized_program = optim.compile(
    program.deepcopy(),
    trainset=dataset,
    max_bootstrapped_demos=3,
    max_labeled_demos=4,
    requires_permission_to_run=False,
)
```

```
2025/01/13 04:24:06 INFO dspy.teleprompt.mipro_optimizer_v2: 
RUNNING WITH THE FOLLOWING LIGHT AUTO RUN SETTINGS:
num_trials: 7
minibatch: False
num_candidates: 5
valset size: 20

2025/01/13 04:24:06 INFO dspy.teleprompt.mipro_optimizer_v2: 
==> STEP 1: BOOTSTRAP FEWSHOT EXAMPLES <==
2025/01/13 04:24:06 INFO dspy.teleprompt.mipro_optimizer_v2: These will be used as few-shot example candidates for our program and for creating instructions.

2025/01/13 04:24:06 INFO dspy.teleprompt.mipro_optimizer_v2: Bootstrapping N=5 sets of demonstrations...
Bootstrapping set 1/5
Bootstrapping set 2/5
Bootstrapping set 3/5
 80%|████████  | 4/5 [00:40<00:10, 10.17s/it]
Bootstrapped 3 full traces after 4 examples for up to 1 rounds, amounting to 4 attempts.
Bootstrapping set 4/5
 20%|██        | 1/5 [00:11<00:47, 11.99s/it]
Bootstrapped 1 full traces after 1 examples for up to 1 rounds, amounting to 1 attempts.
Bootstrapping set 5/5
 60%|██████    | 3/5 [00:39<00:26, 13.25s/it]
2025/01/13 04:25:38 INFO dspy.teleprompt.mipro_optimizer_v2: 
==> STEP 2: PROPOSE INSTRUCTION CANDIDATES <==
2025/01/13 04:25:38 INFO dspy.teleprompt.mipro_optimizer_v2: We will use the few-shot examples from the previous step, a generated dataset summary, a summary of the program code, and a randomly selected prompting tip to propose instructions.
Bootstrapped 3 full traces after 3 examples for up to 1 rounds, amounting to 3 attempts.
2025/01/13 04:25:45 INFO dspy.teleprompt.mipro_optimizer_v2: 
Proposing instructions...

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: Proposed Instructions for Predictor 0:

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: 0: 指定された複雑さのレベルで提供された研究論文の要約を生成します。
要約は最大4段落までで、指定された複雑さのレベルに合わせて調整されるべきです。

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: 1: Generate a summary of the provided research paper at the specified complexity level. The summary should be concise, containing a maximum of four paragraphs, and should be tailored to match the chosen complexity level from 1 (high school) to 5 (graduate level).

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: 2: Generate a comprehensive summary of the provided research paper titled "Material Anything: Generating Materials for Any 3D Object via Diffusion," tailored to the specified complexity level. The summary should encapsulate the main contributions, methodologies, and experimental results of the work, formatted into a maximum of four paragraphs. Ensure the language and depth of explanation match the chosen complexity level, making it accessible to the intended audience.

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: 3: You are a research assistant tasked with generating a summary of a research paper. Given the title, complexity level (from 1 for high school level to 5 for graduate level), and the full text of the paper, create a concise summary that captures the key points and findings. The summary should be no more than four paragraphs long and should be tailored to the specified complexity level to ensure it is appropriate for the intended audience.

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: 4: 生成する要約の複雑さのレベルを指定してください。指定されたレベルに基づいて、提供された研究論文の要約を最大4段落まで生成します。要約は、文書の主なポイントを明確かつ簡潔に伝えるようにしてください。特に、論文の目的、方法、結果、および結論に焦点を当て、読者が理解しやすいように調整してください。

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: 

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: Evaluating the default program...

Average Metric: 14.40 / 20 (72.0%): 100%|██████████| 20/20 [00:00<00:00, 1171.23it/s]2025/01/13 04:26:32 INFO dspy.evaluate.evaluate: Average Metric: 14.4 / 20 (72.0%)
2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: Default program score: 72.0

2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: ==> STEP 3: FINDING OPTIMAL PROMPT PARAMETERS <==
2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: We will evaluate the program over a series of trials with different combinations of instructions and few-shot examples to find the optimal combination using Bayesian Optimization.

/databricks/python/lib/python3.12/site-packages/optuna/samplers/_tpe/sampler.py:319: ExperimentalWarning: ``multivariate`` option is an experimental feature. The interface can change in the future.
  warnings.warn(
2025/01/13 04:26:32 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 1 / 7 =====

Average Metric: 12.80 / 20 (64.0%): 100%|██████████| 20/20 [00:49<00:00,  2.48s/it]2025/01/13 04:27:22 INFO dspy.evaluate.evaluate: Average Metric: 12.8 / 20 (64.0%)
2025/01/13 04:27:22 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 64.0 with parameters ['Predictor 0: Instruction 1', 'Predictor 0: Few-Shot Set 1'].
2025/01/13 04:27:22 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0]
2025/01/13 04:27:22 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 72.0
2025/01/13 04:27:22 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:27:22 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 2 / 7 =====

Average Metric: 15.20 / 20 (76.0%): 100%|██████████| 20/20 [00:48<00:00,  2.43s/it]2025/01/13 04:28:10 INFO dspy.evaluate.evaluate: Average Metric: 15.200000000000001 / 20 (76.0%)
2025/01/13 04:28:10 INFO dspy.teleprompt.mipro_optimizer_v2: Best full score so far! Score: 76.0
2025/01/13 04:28:10 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 76.0 with parameters ['Predictor 0: Instruction 2', 'Predictor 0: Few-Shot Set 1'].
2025/01/13 04:28:10 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0, 76.0]
2025/01/13 04:28:10 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 76.0
2025/01/13 04:28:10 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:28:10 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 3 / 7 =====

Average Metric: 13.80 / 20 (69.0%): 100%|██████████| 20/20 [00:48<00:00,  2.43s/it]2025/01/13 04:28:59 INFO dspy.evaluate.evaluate: Average Metric: 13.8 / 20 (69.0%)
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 69.0 with parameters ['Predictor 0: Instruction 4', 'Predictor 0: Few-Shot Set 1'].
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0, 76.0, 69.0]
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 76.0
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 4 / 7 =====

Average Metric: 15.20 / 20 (76.0%): 100%|██████████| 20/20 [00:00<00:00, 1230.98it/s]2025/01/13 04:28:59 INFO dspy.evaluate.evaluate: Average Metric: 15.200000000000001 / 20 (76.0%)

2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 76.0 with parameters ['Predictor 0: Instruction 2', 'Predictor 0: Few-Shot Set 1'].
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0, 76.0, 69.0, 76.0]
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 76.0
2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:28:59 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 5 / 7 =====
Average Metric: 13.20 / 20 (66.0%): 100%|██████████| 20/20 [00:49<00:00,  2.45s/it]2025/01/13 04:29:48 INFO dspy.evaluate.evaluate: Average Metric: 13.200000000000001 / 20 (66.0%)
2025/01/13 04:29:48 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 66.0 with parameters ['Predictor 0: Instruction 4', 'Predictor 0: Few-Shot Set 3'].
2025/01/13 04:29:48 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0, 76.0, 69.0, 76.0, 66.0]
2025/01/13 04:29:48 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 76.0
2025/01/13 04:29:48 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:29:48 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 6 / 7 =====

Average Metric: 14.80 / 20 (74.0%): 100%|██████████| 20/20 [00:50<00:00,  2.51s/it]2025/01/13 04:30:39 INFO dspy.evaluate.evaluate: Average Metric: 14.8 / 20 (74.0%)
2025/01/13 04:30:39 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 74.0 with parameters ['Predictor 0: Instruction 0', 'Predictor 0: Few-Shot Set 1'].
2025/01/13 04:30:39 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0, 76.0, 69.0, 76.0, 66.0, 74.0]
2025/01/13 04:30:39 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 76.0
2025/01/13 04:30:39 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:30:39 INFO dspy.teleprompt.mipro_optimizer_v2: ===== Trial 7 / 7 =====

Average Metric: 13.60 / 20 (68.0%): 100%|██████████| 20/20 [00:47<00:00,  2.40s/it]2025/01/13 04:31:27 INFO dspy.evaluate.evaluate: Average Metric: 13.6 / 20 (68.0%)
2025/01/13 04:31:27 INFO dspy.teleprompt.mipro_optimizer_v2: Score: 68.0 with parameters ['Predictor 0: Instruction 4', 'Predictor 0: Few-Shot Set 4'].
2025/01/13 04:31:27 INFO dspy.teleprompt.mipro_optimizer_v2: Scores so far: [72.0, 64.0, 76.0, 69.0, 76.0, 66.0, 74.0, 68.0]
2025/01/13 04:31:27 INFO dspy.teleprompt.mipro_optimizer_v2: Best score so far: 76.0
2025/01/13 04:31:27 INFO dspy.teleprompt.mipro_optimizer_v2: =======================


2025/01/13 04:31:27 INFO dspy.teleprompt.mipro_optimizer_v2: Returning best identified program with score 76.0!
```

```py
# 将来の使用のために最適化されたプログラムを保存
optimized_program.save("mipro_optimized", save_program=True)
```

`complexity_level`を1にして高校レベルで要約してもらいます。

```py
print("original: ",program(title=paper[0], text=paper[1][:50000], complexity_level=1)["summary"],
      "\n\n\noptimized: ",optimized_program(title=paper[0], text=paper[1][:50000], complexity_level=1)["summary"])
```

```
original:  
この研究では、RedPajamaという大規模言語モデルのトレーニング用のオープンデータセットについて説明しています。RedPajam
aには、透明性の高いデータ整理が求められており、特にオープンソースモデルの開発を促進するための3つの主要な課題が挙げ
られています。これらの課題は、モデルの開発過程における透明性、質の高いデータへのアクセス、データセットの整理と分析
に必要なメタデータの利用可能性です。

RedPajama-V1はLLaMAトレーニングデータのオープンな再現であり、RedPajama-V2は、100兆トークンを超える膨大なウェブデー
タを含むデータセットです。これにより、様々な新しいデータセットの開発が促されることを目指しています。研究者たちは、
これらのデータセットを利用して強力な言語モデルをトレーニングし、透明で高性能なモデルの開発を進めています。

さらに、RedPajamaデータセットの質を向上させるための分析結果や研究成果も示されており、特にウェブデータの質信号を活用
することで高品質なデータのサブセットを作成する方法が強調されています。このアプローチにより、RedPajamaはオープンソー
スの大規模言語モデルの進展に寄与することが期待されています。 


optimized:  
本研究では、オープンなデータセット「RedPajama」を利用して、大規模言語モデルのトレーニングを行うための新しいアプロー
チを提案しています。大規模言語モデルは、人工知能や科学、社会全体において重要な技術となっていますが、データセットの
構成やフィルタリングに関する最適な戦略は依然として明確ではありません。この論文では、オープンソースの言語モデルを進
展させるために解決すべき三つのデータに関連する課題を特定しています。

具体的には、RedPajama-V1はLLaMAトレーニングデータのオープンな再現を提供し、RedPajama-V2は、質の信号とメタデータを含
む巨大なウェブ専用データセットをリリースしています。これらのデータセットは、100兆トークン以上のテキストデータを含み
、自社のデータをフィルタリングしながら多様なドメインをカバーします。最終的に、RedPajamaはオープンな言語モデルの開発
を促進するための基盤を提供し、その透明性、スケール、汎用性を強調しています。
```

`complexity_level`を5にして専門家レベルで要約してもらいます。


```py
print("original: ",program(title=paper[0], text=paper[1][:50000], complexity_level=5)["summary"],
      "\n\n\noptimized: ",optimized_program(title=paper[0], text=paper[1][:50000], complexity_level=5)["summary"])
```

```
original:  
本研究は、オープンソースの大規模言語モデル（LLM）トレーニングのためのデータセット、RedPajamaを発表しています。主にR
edPajama-V1とRedPajama-V2の2つのデータセットが特徴で、RedPajama-V1はLLaMAモデル用の再現データセットであり、RedPajam
a-V2は、2014年から2023年までのCommon 
Crawlから収集されたWebデータを含む大規模な未フィルタリングデータセットです。研究では、これらのデータセットがどのよ
うに設計され、トレーニングに使用され、またそれがオープンソースのLLMの開発にどのように寄与しているかを探求します。

RedPajamaデータセットは、データ選定の透明性、アクセス可能な高品質データの提供、そしてデータセットのキュレーションと
分析のためのメタデータの利用可能性という3つの主要な課題に対処しています。総計100兆トークン以上の多様なドメインから
成るRedPajamaデータセットは、強力な言語モデルのトレーニングに使用され、Snowflake 
ArcticやSalesforceのXGenなどの商業アプリケーションで活用されています。

また、本研究では、RedPajamaデータセットの質を評価するために一連の分析とアブレーション研究を行い、Webデータに対する
質的信号が高品質なデータサブセットのキュレーションにどのように寄与するかを示しています。最終的に、RedPajamaは、透明
性の高い高性能な言語モデルの大規模開発を促進する可能性を持つと結論付けられています。 


optimized:  
本研究では、オープンな大規模言語モデルのトレーニングに使用するための新しいデータセット「RedPajama」を提案します。こ
のデータセットは、透明性のあるデータキュレーションや、大量の高品質データへのアクセス、データセットの分析に必要なメ
タデータの提供など、オープンソース言語モデルの発展に必要な3つの中心的な課題に対処しています。RedPajama-V1は、LLaMA
トレーニングデータの再現を目指しており、RedPajama-V2は、生の未フィルタリングのテキストデータを含む大規模なウェブ専
用データセットとなっています。

RedPajamaデータセットは、スケールと多用途性を重視して設計されています。1.2兆トークン以上のデータが含まれ、さまざま
な領域の情報が提供されることで、研究者が特定のニーズに基づいてデータをフィルタリングする際の選択肢が広がります。ま
た、モデルのパフォーマンスを向上させるための質のシグナルを提供し、さまざまなデータフィルタリング手法を検討するため
のアブレーションスタディも行っています。

結果として、RedPajamaデータセットは、透明性が高く、オープンな言語モデルのトレーニングにおいて、質の高いデータを利用
するための強力な資源となることが期待されます。最終的に、RedPajamaは、未来の高品質なウェブデータセットの開発に向けた
重要なステップを提供します。
```

**original**は複雑度を変えてもほとんど要約が変わっていませんが、**optimized**の結果に着目すると、複雑度に合わせて要約を適切に生成していることが確認できます。

## モデルをMLflowにログする

```py
with mlflow.start_run():
    model_info = mlflow.dspy.log_model(
        optimized_program,
        "optim_model",
        input_example={"title": "dummy_title", "text": "dummy_text", "complexity_level": 1},
    )
```

プログラムがログされるので、再利用することができるようになります。

![Screenshot 2025-01-13 at 14.00.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/99d3aa4f-ad59-7c7f-3f5a-667a207bc5a9.png)

```py
loaded_model = mlflow.dspy.load_model(model_info.model_uri)

print(loaded_model(title=paper[0], text=paper[1][:50000], complexity_level=1)["summary"])
```
```
本研究では、オープンなデータセット「RedPajama」を利用して、大規模言語モデルのトレーニングを行うための新しいアプロー
チを提案しています。大規模言語モデルは、人工知能や科学、社会全体において重要な技術となっていますが、データセットの
構成やフィルタリングに関する最適な戦略は依然として明確ではありません。この論文では、オープンソースの言語モデルを進
展させるために解決すべき三つのデータに関連する課題を特定しています。

具体的には、RedPajama-V1はLLaMAトレーニングデータのオープンな再現を提供し、RedPajama-V2は、質の信号とメタデータを含
む巨大なウェブ専用データセットをリリースしています。これらのデータセットは、100兆トークン以上のテキストデータを含み
、自社のデータをフィルタリングしながら多様なドメインをカバーします。最終的に、RedPajamaはオープンな言語モデルの開発
を促進するための基盤を提供し、その透明性、スケール、汎用性を強調しています。
```

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

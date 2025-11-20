---
title: DatabricksでLlamaExtractを動かしてみる
tags:
  - Databricks
  - LlamaIndex
  - LlamaExtract
private: false
updated_at: '2025-05-02T10:14:02+09:00'
id: 586dac0ced42abad81c4
organization_url_name: databricks
slide: false
ignorePublish: false
---
機能こちらのニュースがありました。

https://www.databricks.com/jp/blog/databricks-invests-llamaindex-advance-knowledge-agents-over-enterprise-data

> - この投資に続き、DatabricksはLlamaIndexとの技術的統合を深め、DatabricksユーザーがDatabricksデータインテリジェンスプラットフォーム上で直接LlamaParseとLlamaExtractを活用しやすくします。

いいですね。って、LlamaExtract？初耳です。

LlamaParseは以前触ったことがあります。

https://qiita.com/taka_yayoi/items/032a2961c1f643b05286

なので、LlamaExtractをDatabricksで動かしてみます。

ドキュメントはこちら。

https://docs.cloud.llamaindex.ai/llamaextract/getting_started

以下はドキュメントの翻訳です。

# LlamaExtractの概要
LlamaExtractは、PDF、テキストファイル、画像などの非構造化ドキュメントから構造化データを抽出するためのシンプルなAPIを提供します。

LlamaExtractは、Web UI、Python SDK、およびREST APIとして利用可能です。

## LlamaExtractは私に適していますか？
LlamaExtractは、以下のような場合に最適です：

- **下流タスクのための型付きデータ：** ドキュメントからデータを抽出し、それをモデルのトレーニング、ダッシュボードの構築、データベースへの入力などの下流タスクに使用したい場合。LlamaExtractは、提供されたスキーマに準拠するデータを保証し、準拠しない場合には有益なエラーメッセージを提供します。
- **正確なデータ抽出：** 私たちは、ドキュメントからデータを抽出するために最高クラスのLLMモデルを使用しています。
- **反復的なスキーマ開発：** スキーマを迅速に反復し、サンプルドキュメントでの動作をフィードバックとして得たい場合。特定のフィールドを抽出するためにもっと例を提供する必要がありますか？特定のフィールドをオプションにする必要がありますか？
- **複数のファイルタイプのサポート：** LlamaExtractは、PDF、テキストファイル、画像など、幅広いファイルタイプをサポートしています。他のファイルタイプのサポートが必要な場合はお知らせください！

Web UIはこんな感じです。LlamaCloudの一機能。

![Screenshot 2025-05-02 at 9.57.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ee49aaad-be20-4212-bf88-158e3f12aced.png)

# LlamaExtract Python SDK

今回は、[Python SDK](https://docs.cloud.llamaindex.ai/llamaextract/getting_started/python)で動かします。LlamaCloudの[APIキーを取得](https://docs.cloud.llamaindex.ai/llamaextract/getting_started/get_an_api_key)しておきます。

## APIキーの設定

`dotenv`を使っているので、`.env`ファイルにAPIキーを記述します。

```
LLAMA_CLOUD_API_KEY=llx-xxxxxx
```

## PDFファイルの格納

抽出を行う[PDFファイル](https://github.com/run-llama/llama_cloud_services/tree/main/examples/extract/data/resumes)を`resumes`フォルダ配下に格納しておきます。

![Screenshot 2025-05-02 at 10.02.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1a5757da-f0aa-4543-8614-0d6afc147b5c.png)

## エージェントの作成および情報の抽出

```py
from llama_cloud_services import LlamaExtract
from pydantic import BaseModel, Field
from pprint import pprint

# LLAMA_CLOUD_API_KEYを読み込む
from dotenv import load_dotenv
load_dotenv()

# クライアントを初期化
extractor = LlamaExtract()

# Pydanticを使用してスキーマを定義
class Resume(BaseModel):
    name: str = Field(description="候補者のフルネーム")
    email: str = Field(description="メールアドレス")
    skills: list[str] = Field(description="技術スキルとテクノロジー")

# 抽出エージェントを作成
agent = extractor.create_agent(name="resume-parser", data_schema=Resume)

# ドキュメントからデータを抽出
result = agent.extract("resumes/ai_researcher.pdf")
pprint(result.data)
```

情報が抽出されました。メールアドレスは取れてませんが、この辺りは抽出モード(Fast/Balanced/Multimodal)の切り替えで変わるかもしれません。デフォルトはBalancedです。

```
No project_id provided, fetching default project.
Uploading files: 100%|██████████| 1/1 [00:01<00:00,  1.77s/it]
Creating extraction jobs: 100%|██████████| 1/1 [00:00<00:00,  2.23it/s]
Extracting files: 100%|██████████| 1/1 [00:23<00:00, 23.65s/it]{'email': '',
 'name': 'Dr. Rachel Zhang, Ph.D.',
 'skills': ['Deep Learning',
            'Reinforcement Learning',
            'Probabilistic Models',
            'Multi-Task Learning',
            'Zero-Shot Learning',
            'Neural Architecture Search',
            'PyTorch',
            'TensorFlow',
            'JAX',
            'Ray',
            'Python',
            'C++',
            'Julia',
            'CUDA',
            'Git & Version Control',
            'Docker & Kubernetes',
            'Cloud Platforms (AWS, GCP)']}

```

LlamaCloudでもエージェントを確認できます。

![Screenshot 2025-05-02 at 10.04.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e36dac3a-5801-4742-b2db-fffbe70eae03.png)
![Screenshot 2025-05-02 at 10.08.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/10e9cbe5-61e0-4319-bdd7-c36ffc5228c4.png)


## バッチ抽出

複数ファイルに対するバッチ抽出もできます。

```py
import glob
file_paths = glob.glob('resumes/*.pdf')
file_paths
```
```
['resumes/ai_researcher.pdf',
 'resumes/ml_engineer.pdf',
 'resumes/software_architect.pdf']
```

```py
# 複数のファイルを抽出キューに追加
jobs = await agent.queue_extraction(file_paths)

# ジョブのステータスを確認
for job in jobs:
    status = agent.get_extraction_job(job.id).status
    print(f"Job {job.id}: {status}")
```
```
Uploading files: 100%|██████████| 3/3 [00:02<00:00,  1.27it/s]
Creating extraction jobs: 100%|██████████| 3/3 [00:00<00:00,  5.74it/s]
Job 0b79791e-ba44-48ed-b173-fc88b204d0a4: StatusEnum.PENDING
Job 42c7c5b5-90d5-4389-90b8-352ae41ef8ce: StatusEnum.PENDING
Job e2678fef-ddd8-4528-b6c8-95575349adc3: StatusEnum.PENDING
```


非同期実行なので、ジョブが完了するのを待ちます。

```py
# ジョブのステータスを確認
for job in jobs:
    status = agent.get_extraction_job(job.id).status
    print(f"Job {job.id}: {status}")

# 完了時に結果を取得
results = [agent.get_extraction_run_for_job(job.id) for job in jobs]
```
```
Job 0b79791e-ba44-48ed-b173-fc88b204d0a4: StatusEnum.SUCCESS
Job 42c7c5b5-90d5-4389-90b8-352ae41ef8ce: StatusEnum.SUCCESS
Job e2678fef-ddd8-4528-b6c8-95575349adc3: StatusEnum.SUCCESS
```

```py
from pprint import pprint

for extract_run in results:
    pprint(extract_run.data)
```
```
{'email': 'rachel.zhang@email.com',
 'name': 'Dr. Rachel Zhang, Ph.D.',
 'skills': ['Deep Learning',
            'Reinforcement Learning',
            'Probabilistic Models',
            'Multi-Task Learning',
            'Zero-Shot Learning',
            'Neural Architecture Search',
            'PyTorch',
            'TensorFlow',
            'JAX',
            'Ray',
            'Python',
            'C++',
            'Julia',
            'CUDA']}
{'email': 'alex park@email com',
 'name': 'Alex Park',
 'skills': ['PyTorch',
            'TensorFlow',
            'Scikit-learn',
            'Learning-to-Rank',
            'BERT',
            'Word2Vec',
            'FastAI',
            'Elasticsearch',
            'Solr',
            'Lucene',
            'Vector Search',
            'BM25',
            'FAISS',
            'Python',
            'SQL',
            'Java',
            'Scala',
            'Shell Scripting',
            'AWS',
            'Docker',
            'Kubernetes',
            'Airflow',
            'MLflow',
            'Git']}
{'email': 'sarah.chen@email.com',
 'name': 'Sarah Chen',
 'skills': ['Microservices',
            'Event-Driven Architecture',
            'Domain-Driven Design',
            'REST APIs',
            'Cloud Platforms',
            'AWS (Advanced)',
            'Azure',
            'Google Cloud Platform',
            'Java',
            'Python',
            'Go',
            'JavaScript/TypeScript']}
```

抽出結果はGUIでも確認できます。

![Screenshot 2025-05-02 at 10.13.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d5c7fc73-9459-4815-b1b7-7b13eeddc1c9.png)


個人的にも情報抽出におけるLLMの活用は可能性を感じているので、LlamaExtractがDatabricksで使えるようになることを楽しみにしています。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

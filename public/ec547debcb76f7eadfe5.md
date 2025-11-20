---
title: Databricks JobsからDelta Live Tablesパイプラインを呼び出す
tags:
  - Databricks
  - DeltaLiveTables
private: false
updated_at: '2022-02-19T10:09:22+09:00'
id: ec547debcb76f7eadfe5
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Delta Live Tables(DLT)](https://qiita.com/taka_yayoi/items/7fe8ed2c2f95fd53cc3d)を用いることで、複雑なデータパイプラインであっても簡単かつ、信頼性高く構築、運用が行えるようになります。

DLT単体でもパイプラインを実行できますが、これと[Databricks Jobs](https://qiita.com/taka_yayoi/items/b3275a1983c51a8bbe1a)とを組み合わせると、さらに複雑な処理を自動化することができます。

本書では、Databricks JobsからどのようにDLTを呼び出すのか、また、その際の注意点を説明します。

# Delta Live Tablesでパイプラインを定義する

> **プレビュー**
この機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。アクセスする際にはDatabricks担当者にお問い合わせください。

JSONを読み込むシンプルなパイプラインを定義します。

```py:Python
import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *

json_path = "/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json"

@dlt.table(
  comment="Jobsテスト用DLT"
)
def bronze():
  return (spark.read.json(json_path))
```

サイドバーから**Jobs > Delta Live Tables**にアクセスし、**Create Pipeline**をクリックします。上記パイプラインを定義したノートブックを選択し、パイプラインの名前をつけて**Create**をクリックしてパイプラインを作成します。
![Screen Shot 2022-02-19 at 9.49.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9d17dd39-bff8-57c5-52ad-41749d8a30b1.png)

パイプラインの詳細画面が表示されます。ジョブから呼び出すので、ここでパイプラインの実行はしません。ただ、一点注意が必要です。画面右上にある**Development/Production**でパイプラインの[モード](https://qiita.com/taka_yayoi/items/6726ad1edfa92d5cd0e9#%E9%96%8B%E7%99%BA%E3%83%97%E3%83%AD%E3%83%80%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3%E3%83%A2%E3%83%BC%E3%83%89)を指定できるのですが、ジョブから実行する際には**Production**モードにすることを忘れないでください。ジョブからDLTパイプラインを呼び出した際、このモードによってDLTクラスターの挙動が変わります。

- **Development**モード: ジョブ終了後、2時間クラスターが稼働し続けます。
- **Production**モード: ジョブ終了後、即座に(約5分後)クラスターが終了します。

**Development**モードは名前の通り、パイプライン開発時に選択するモードで試行錯誤、デバッグを行うため、パイプラインの処理が終了しても即座にDLTクラスターは停止しません。
![Screen Shot 2022-02-19 at 9.56.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b15f75a8-bc51-b951-078e-ee8418f6cc01.png)

# ジョブからパイプラインを実行する

1. サイドバーから**Jobs**にアクセスします。
1. **Create Job**をクリックします。
1. ジョブは複数のタスクから構成することができます。ここでは1つのみのタスクを作成します。タスクの**Type**ではDelta Live Tables pipelineを選択し、**Pipeline**では上で作成したDLTパイプラインを選択します。
![Screen Shot 2022-02-19 at 9.57.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5b3ff0d3-fcff-c4ce-7186-1ae410161c92.png)
1. これでDLTパイプラインを呼び出すジョブを定義することができました。
![Screen Shot 2022-02-19 at 9.57.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5e659af5-b4ea-58f8-f1a1-e54efeacf603.png)
1. 右上の**Run now**で即時実行することもできますし、右側の**Schedule**を指定してスケジュール実行することもできます。

なお、ジョブの実行中にDLTのパイプラインにアクセスすると、処理状況をリアルタイムで確認できます。
![Screen Shot 2022-02-19 at 10.03.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/69ed8428-fe7d-25f9-28bb-024321eeeaf3.png)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

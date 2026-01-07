---
title: Databricks Free EditionでUnity Catalogモデルレジストリがエラーになる場合の対処法
tags:
  - Databricks
  - Databricks_Free_Edition
private: false
updated_at: '2026-01-07T09:49:04+09:00'
id: 6068b9bb4eb05ab5ddbd
organization_url_name: databricks
slide: false
ignorePublish: false
---
# 問題の概要

Databricks Free Editionで`mlflow.register_model()`を使用してUnity Catalogにモデルを登録しようとすると、以下のようなS3 AccessDeniedエラーが発生する場合があります。

```
RestException: RESOURCE_DOES_NOT_EXIST: 
An error occurred (AccessDenied) when calling the PutObject operation: Access Denied
```

エラーはモデルのアーティファクト(requirements.txt、MLmodel、model.pkl等)をUnity Catalogのストレージにアップロードする際に発生します。

![Screenshot 2026-01-07 at 9.47.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1e328d88-b4af-4adb-80f5-d2b1af7f56b0.png)


# 原因

サーバレスコンピュートのバージョンによって、プリインストールされているMLflowのバージョンが異なります。

| サーバレスバージョン | MLflowバージョン | UC Model Registry |
|---------------------|-----------------|-------------------|
| v2 | 2.11.4 | ❌ エラー |
| v4 | 2.22.0 | ✅ 動作 |

古いバージョンのMLflow(2.11.x系)では、Free Editionの権限設定でモデルアーティファクトのアップロードに失敗します。MLflowをアップグレードすることで解決します。

# 解決策

## 方法1: サーバレスv4を使用する(推奨)

ノートブックの接続先をサーバレスv4に変更します。

1. ノートブック右の環境設定をクリック
2. サーバレスv4を選択
    ![Screenshot 2026-01-07 at 9.44.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d6e74e83-6224-4bb5-a44d-3fb1ceb9c9f4.png)
3. 適用をクリック
    ![Screenshot 2026-01-07 at 9.44.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c773283a-542e-426e-9ed3-fc933747c818.png)


これによりMLflow 2.22.0が使用され、問題なくモデル登録できます。

![Screenshot 2026-01-07 at 9.48.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7cb14bdc-fbbc-405b-8079-6490acdb3722.png)


## 方法2: MLflowをアップグレードする

サーバレスv2を使用する場合は、ノートブックの先頭でMLflowをアップグレードします。

```python
%pip install --upgrade mlflow -q
```

```python
dbutils.library.restartPython()
```

**注意:** `restartPython()`を実行すると、それまでに定義した変数やインポートがリセットされます。このため、これらのセルはノートブックの最初に配置してください。

# 確認方法

現在のMLflowバージョンは以下で確認できます。

```python
import mlflow
print(mlflow.__version__)
```

2.20.0以上であれば、Unity Catalogへのモデル登録が正常に動作します。

# 最小再現コード

問題を再現するための最小コードです。

```python
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression

# 設定
mlflow.set_registry_uri("databricks-uc")
username = spark.sql("SELECT current_user()").collect()[0][0]
clean_username = username.split("@")[0].replace(".", "_")
CATALOG = f"test_{clean_username}"
MODEL_NAME = f"{CATALOG}.ml.test_model"

# カタログ作成
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.ml")

# モデル学習
wine = load_wine()
X, y = wine.data[:, :4], (wine.target == 0).astype(int)
model = LogisticRegression().fit(X, y)

# MLflowでログ
with mlflow.start_run() as run:
    sig = infer_signature(X, model.predict(X))
    mlflow.sklearn.log_model(model, "model", signature=sig, input_example=X[:2])

# ここでエラーが発生(MLflow 2.11.x の場合)
mlflow.register_model(f"runs:/{run.info.run_id}/model", MODEL_NAME)
```

# まとめ

- Free EditionでUCモデルレジストリを使う場合は、**MLflow 2.20以上**が必要
- サーバレスv4を使うか、`%pip install --upgrade mlflow`でアップグレード
- この問題はFree Edition固有であり、有償環境では発生しない

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: '[2025年版] Databricks Connectを使ってみる'
tags:
  - Databricks
private: false
updated_at: '2025-03-20T12:02:23+09:00'
id: 7ddd8be2d39fdfdaa9df
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらの記事を書いて3年経ってました。

https://qiita.com/taka_yayoi/items/c4d87e07e46c63e987b1

https://docs.databricks.com/aws/ja/dev-tools/databricks-connect/

> Databricks Connectは、Visual Studio Code、PyCharm 、RStudio Desktop、IntelliJ IDEA 、ノートブックサーバー、その他のカスタムアプリケーションなどの一般的な IDEからDatabricksの計算資源に接続するためのDatabricksランタイム用のクライアントライブラリです。

前回はPyCharmで接続しましたが、今回はVS Codeで接続します。

# 設定の流れ

**接続先のDatabricksワークスペース**

- ワークスペースURLのコピー
- [パーソナルアクセストークン](https://docs.databricks.com/aws/ja/dev-tools/auth/pat)の取得

**ローカルマシン**

- VS Codeのインストール
- Python仮想環境の有効化
- Databricks Connectのインストール

# ローカルマシンでの作業

OSに応じたVS Codeをインストールください。

私はVS Codeに不慣れなので、こちらの記事を参考にさせていただきました。

- [VS Code のワークスペースをちゃんと使いたい \#初心者 \- Qiita](https://qiita.com/amac-53/items/86b1466e93524844c2a8)
- [\[python\] pip/VSCode開発環境の構築 \(windows11\) \#Python \- Qiita](https://qiita.com/flcn-x/items/ac6e222004a827f582ea)
- [【Python環境構築】VSCodeとvenvを使った実践的な環境構築 \#Python \- Qiita](https://qiita.com/CodeTea_Ping999/items/900ec14a7eb9be98465c)

## Python仮想環境の有効化

Databricks Connectのライブラリをインストールするので仮想環境を作成して有効化します。

![Screenshot 2025-03-20 at 11.54.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9035042f-5480-4a3f-833b-e4b0da782b4e.png)
![Screenshot 2025-03-20 at 11.54.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ca949141-49ae-4794-b675-835def89b535.png)
![Screenshot 2025-03-20 at 11.56.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/28f65593-5be1-41a1-b29e-a51e986635e3.png)

Pythonインタプリタを選択して仮想環境を作成、有効化します。

## Databricks Connectのインストール

接続先に[サーバレスコンピュート](https://docs.databricks.com/aws/ja/dev-tools/databricks-connect/cluster-config#%E3%82%B5%E3%83%BC%E3%83%90%E3%83%AC%E3%82%B9-%E3%82%B3%E3%83%B3%E3%83%94%E3%83%A5%E3%83%BC%E3%83%88%E3%81%B8%E3%81%AE%E6%8E%A5%E7%B6%9A%E3%82%92%E6%A7%8B%E6%88%90%E3%81%99%E3%82%8B)を指定できるようになっているのでこちらを試します。VS Codeのターミナルで以下を実行します。サーバレスに接続するには[バージョン16.1以降](https://docs.databricks.com/aws/ja/dev-tools/databricks-connect/python/install#versions)が必要です。

```sh
pip3 install --upgrade "databricks-connect==16.1.0"
```

# 接続確認

`serverless = True`を指定することで、クラスターIDを指定することなしにサーバレスコンピュートに接続できます。

```py
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.remote(
host       = "https://<Databricksワークスペースのホスト名>/",
token      = "<パーソナルアクセストークン>",
serverless = True
).getOrCreate()

spark.sql("SELECT 1").show()
```

```
.venvtakaaki.yayoi@DRYC7D19F3 vscode % /Users/takaaki.yayoi/venv/vscode/.venv/bin/python /Users/takaaki.yayoi/venv/conncet.py
+---+
|  1|
+---+
|  1|
+---+
```

以下のようにUnity Catalog配下のテーブルにもアクセスできます。

```py
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.remote(
host       = "https://<Databricksワークスペースのホスト名>/",
token      = "<パーソナルアクセストークン>",
serverless = True
).getOrCreate()

spark.sql("SELECT * FROM samples.nyctaxi.trips LIMIT 10").show()
```
![Screenshot 2025-03-20 at 12.01.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/87cb02a2-4b30-4675-9a8c-66f5af0b04c0.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

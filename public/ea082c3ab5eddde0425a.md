---
title: Databricks SQL Connector for Pythonを試してみる
tags:
  - Python
  - Databricks
  - DatabricksSQL
private: false
updated_at: '2023-02-26T20:15:10+09:00'
id: ea082c3ab5eddde0425a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらのコネクターを実際に試してみます。

https://docs.databricks.com/dev-tools/python-sql-connector.html

[Databricks SQL Connector for Python](https://github.com/databricks/databricks-sql-python)はDatabricksクラスターやDatabricks SQLウェアハウスでSQLコマンドを実行するために、Pythonコードを使用できるPythonライブラリです。[pyodbc](https://docs.databricks.com/dev-tools/pyodbc.html)のようなPythonライブラリと同じように簡単にセットアップ、使用することができます。

# 要件

- Python >= 3.7、Python <=3.11が稼働している開発用マシン。
- 既存の[クラスター](https://qiita.com/taka_yayoi/items/c5d99cd77fe4bfcf69f0)あるいは[SQLウェアハウス](https://qiita.com/taka_yayoi/items/23d7789198c2dcd66381)。

# 準備

以下ではSQLウェアハウスを使用するケースを説明します。

1. SQLウェアハウスの**接続の詳細**で**サーバーのホスト名**と**HTTPパス**をコピーしておきます。
![Screenshot 2023-02-26 at 20.06.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3b5bb36a-29c7-fd36-1333-817039d28fe9.png)
1. [パーソナルアクセストークン](https://qiita.com/taka_yayoi/items/f5493a4169e95e1a7a61#%E3%83%A6%E3%83%BC%E3%82%B6%E3%83%BC%E3%81%AE%E3%83%91%E3%83%BC%E3%82%BD%E3%83%8A%E3%83%AB%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3)をコピーしておきます。
1. 開発用マシンで`pip install databricks-sql-connector`を実行してコネクターをインストールします。

# コネクターによる接続

1. ターミナルで環境変数を設定します。

    ```bash:Bash
    export DATABRICKS_HOST=<Databricksワークスペースのホスト名>
    export DATABRICKS_HTTP_PATH=<上でコピーしたHTTPパス>
    export DATABRICKS_TOKEN=<上でコピーしたパーソナルアクセストークン>
    ```

1. VS Codeを起動します(Python実行環境であれば何でも構いません)。

    ```bash:Bash
    code .
    ```

1. 以下のPythonコードを実行します。

    ```py:Python
    import os
    from databricks import sql
    
    with sql.connect(server_hostname = os.getenv("DATABRICKS_HOST"),
                     http_path       = os.getenv("DATABRICKS_HTTP_PATH"),
                     access_token    = os.getenv("DATABRICKS_TOKEN")) as connection:
    
      with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM default.diamonds LIMIT 5")
        result = cursor.fetchall()
    
        for row in result:
          print(row)
    ```

1. クエリー結果が表示されます。
![Screenshot 2023-02-26 at 20.12.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/451da3f8-b4b9-a872-079f-c8ca7e305871.png)

:::note
**注意**
`nodename nor servname provided, or not known`や`Error during request to server`のようなエラーが発生する場合には、環境変数`DATABRICKS_HOST`で指定したホスト名に`https://`や末尾の`/`が含まれていないことを確認してください。
:::

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

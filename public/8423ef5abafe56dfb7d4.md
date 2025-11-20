---
title: DatabricksクラスターでGradioを動かしてみる
tags:
  - Databricks
  - gradio
private: false
updated_at: '2023-11-27T21:28:03+09:00'
id: 8423ef5abafe56dfb7d4
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらのノリで行けると思ったらうまくいきませんでした。以下のサンプルにあるように[FastAPI](https://fastapi.tiangolo.com/)を使ってます。

https://qiita.com/taka_yayoi/items/74a27964527929032efc

# Gradioとは

https://www.gradio.app/

機械学習モデル向けGUIをクイックに作ることができるフレームワークだとのこと。

# サンプル

こちらに公開されていました。

https://github.com/stikkireddy/dolly-chat-gradio

# 実装

上のサンプルは、[Databricksモデルサービングエンドポイント](https://docs.databricks.com/ja/machine-learning/model-serving/create-manage-serving-endpoints.html)を呼び出すようにカスタマイズされていますが、ここではシンプルなものを動作させるに留めます。

こちらはヘルパーモジュールです。

```py:databricks_magic/__init__.py
import json
from dataclasses import dataclass

import uvicorn
from fastapi import FastAPI


@dataclass
class ProxySettings:
    proxy_url: str
    port: str
    url_base_path: str


class DatabricksApp:

    def __init__(self, port):
        # self._app = data_app
        self._port = port
        import IPython
        self._dbutils = IPython.get_ipython().user_ns["dbutils"]
        self._display_html = IPython.get_ipython().user_ns["displayHTML"]
        self._context = json.loads(self._dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson())
        # コンテキストを設定した後にこちらを実行する必要があります
        self._cloud = self.get_cloud()
        # クラウドの特定後にプロキシーの設定を作成します
        self._ps = self.get_proxy_settings()
        self._fastapi_app = self._make_fastapi_app(root_path=self._ps.url_base_path.rstrip("/"))
        self._streamlit_script = None
        # すべてが設定されたらURLを表示します

    def _make_fastapi_app(self, root_path) -> FastAPI:
        """
        FastAPIを用いてWebアプリを構成します
        """
        fast_api_app = FastAPI(root_path=root_path)

        @fast_api_app.get("/")
        def read_main():
            return {
                "routes": [
                    {"method": "GET", "path": "/", "summary": "Landing"},
                    {"method": "GET", "path": "/status", "summary": "App status"},
                    {"method": "GET", "path": "/dash", "summary": "Sub-mounted Dash application"},
                ]
            }

        @fast_api_app.get("/status")
        def get_status():
            return {"status": "ok"}

        return fast_api_app

    def get_proxy_settings(self) -> ProxySettings:
        """
        Driver Proxyの設定を取得します
        """
        if self._cloud.lower() not in ["aws", "azure"]:
            raise Exception("only supported in aws or azure")
        prefix_url_settings = {
            "aws": "https://dbc-dp-",
            "azure": "https://adb-dp-",
        }
        suffix_url_settings = {
            "aws": "cloud.databricks.com",
            "azure": "azuredatabricks.net",
        }
        org_id = self._context["tags"]["orgId"]
        org_shard = ""
        # URLを構築する際、org_shardにはdns名の"."の接尾辞は不要です
        if self._cloud.lower() == "azure":
            org_shard_id = int(org_id) % 20
            org_shard = f".{org_shard_id}"
        cluster_id = self._context["tags"]["clusterId"]
        url_base_path = f"/driver-proxy/o/{org_id}/{cluster_id}/{self._port}/"
        return ProxySettings(
            proxy_url=f"{prefix_url_settings[self._cloud.lower()]}{org_id}{org_shard}.{suffix_url_settings[self._cloud.lower()]}{url_base_path}",
            port=self._port,
            url_base_path=url_base_path
        )

    @property
    def app_url_base_path(self):
        return self._ps.url_base_path

    def mount_gradio_app(self, gradio_app):
        import gradio as gr
        gr.mount_gradio_app(self._fastapi_app, gradio_app, f"/gradio")
        # self._fastapi_app.mount("/gradio", gradio_app)
        self.display_url(self.get_gradio_url())

    def get_cloud(self):
        """
        クラウドプロバイダーを特定します
        """
        if self._context["extraContext"]["api_url"].endswith("azuredatabricks.net"):
            return "azure"
        return "aws"

    def get_gradio_url(self):
        """
        gradioのURLへのリンクを返却します
        """
        # リダイレクトしないようにするために "/" で終わる必要があります
        return f'<a href="{self._ps.proxy_url}gradio/">Click to go to Gradio App!</a>'

    def display_url(self, url):
        self._display_html(url)

    def run(self):
        """
        uvicornでアプリケーションを実行します
        """
        uvicorn.run(self._fastapi_app, host="0.0.0.0", port=self._port)
```

実行するノートブックはこちら。

```py
%pip install Jinja2==3.0.3 fastapi uvicorn nest_asyncio gradio==3.32.0
```

```py
from databricks_magic import DatabricksApp
dbx_app = DatabricksApp(8098)
```

こちらがGUIの実装です。

```py
import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("# Hello Gradio")
    gr.Markdown("## Gradioプロトタイプ")
    with gr.Accordion("設定: 設定するにはクリックしてください", open=False):
        with gr.Row():
            endpoint = gr.Textbox(label="エンドポイント", interactive=True)
            token = gr.Textbox(label="パスワード", interactive=True, type="password")

    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=500)
    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="テキストを指定してください",
            ).style(container=False)
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.Button("クリア")
```

上記アプリケーションをヘルパーモジュールにマウントします。

```py
dbx_app.mount_gradio_app(demo)
```

リンクが表示されます。
![Screenshot 2023-11-27 at 21.26.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b9d7be43-1cc7-02c9-e081-616862711c57.png)

Webサーバを起動します。

```py
import nest_asyncio
nest_asyncio.apply()
dbx_app.run()
```
```
INFO:     Started server process [1207]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8098 (Press CTRL+C to quit)
```

上で表示されたリンクをクリックするとGUIが表示されます。
![Screenshot 2023-11-27 at 21.25.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/837748c7-8f15-80b5-ed21-c460dbf0ad02.png)

次は、イベントを設定して実際にLLMを呼び出してチャットbotとして動作させるところまでやってみます。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

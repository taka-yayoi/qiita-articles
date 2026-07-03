---
title: Databricks AppsでVolumeを読み書きする際に注意すること
tags:
  - Databricks
  - DatabricksApps
private: false
updated_at: '2025-12-03T10:43:56+09:00'
id: 6a87bfdf0fb8edeb6345
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
テーブルの読み書きはやったことがあったのですが、よく考えたらボリュームの読み書きの実装をしたことがありませんでした。

ノートブックで読み書きするノリでやるとハマるので注意点をまとめます。私が遭遇したエラーは:

```
FileNotFoundError: [Errno 2] No such file or directory: '/Volumes/workspace/de_handson/data_files'
```

![Screenshot 2025-12-03 at 6.43.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fd5a3268-2905-4ccc-b31e-02918fd28fd7.png)

もちろん、ボリュームのパスは存在しています。

# 注意点

1. アプリからボリュームにアクセスする際には、ボリュームのパス`/Volumes/...`に直接アクセスするのではなく、Databricks SDKを経由する
1. アプリのサービスプリンシパルにボリュームのアクセス権を付与する

特に1点目に注意です。ノートブックの場合、`/Volumes/...`のパスで直接読み書きできますが、**Appの動作しているコンテナ環境にはUnity Catalogボリュームがマウントされていない**ので、ノートブックのノリで` pd.read_csv("/Volumes/...")`などとやると冒頭のエラーになります。

こちらのクックブックに説明があります。

https://apps-cookbook.dev/docs/streamlit/volumes/volumes_download/

:::note info
Unlike notebooks, Databricks Apps does not support mounting Unity Catalog volumes and directly reading and writing files. As this code snippet demonstrates, each file needs to be downloaded to the app compute before being able to manipulate it.

ノートブックとは異なり、Databricks AppsではUnity Catalogボリュームのマウントや、ファイルの直接の読み書きはサポートしていません。このコードスニペットで示しているように、それぞれのファイルは操作する前にアプリのコンピュートにダウンロードする必要があります。
:::

こちらのコミュニティのやり取りでも言及されています。

https://community.databricks.com/t5/data-governance/accessing-unity-catalog-volumes-from-a-databricks-web/td-p/122325

2点目のアクセス権は**アプリのリソースとしてボリュームを追加する**ことで自動で設定されます。手動で設定しても構いませんが、わかりやすさの観点でもリソースとして設定することをお勧めします。

https://docs.databricks.com/gcp/ja/dev-tools/databricks-apps/uc-volumes

# 実践

カスタムアプリを作成します。
![Screenshot 2025-12-03 at 9.52.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/954e3540-7d23-4519-9c76-23c55d66c719.png)

名前と説明文。
![Screenshot 2025-12-03 at 9.53.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d75388cf-8d25-4704-abe8-9cae4d5c750b.png)

**リソースを追加**をクリック。
![Screenshot 2025-12-03 at 9.53.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f9134765-2961-4cc2-bbb5-053f165eca71.png)

**UCボリューム**を選択。
![Screenshot 2025-12-03 at 9.53.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/22ddf75c-b225-4f9a-89aa-a9621e5d7c40.png)

ボリュームのパスを選択し、権限には**読み取りと書き込み**を指定。
![Screenshot 2025-12-03 at 9.54.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/70febd69-4312-4dce-a1e7-520036db0490.png)

これで、アクセスするボリュームにアプリのサービスプリンシパルの権限が設定されます。これで、権限の問題はクリアしましたが、マウントポイントの問題が残っています。
![Screenshot 2025-12-03 at 9.54.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cdfcc0d7-071d-4e13-8763-ad9ec9b0e0aa.png)

まず、`app.yaml`ではstreamlitが動くようにしておき、リソースで定義したボリュームパスを[環境変数で参照](https://docs.databricks.com/aws/ja/dev-tools/databricks-apps/environment-variables)できるようにしておきます。`requirements.txt`は依存関係がなければ空で大丈夫です。

```yaml:app.yaml
command: [
  "streamlit", 
  "run",
  "app.py"
]

env:
  - name: VOLUME_PATH
    valueFrom: volume
```

そして、マウントポイントの問題を回避するために、`app.py`で以下のように実装します。ここでのポイントは、アプリから直接ボリュームパスを参照するのではなく、Databricks SDKでファイルをアプリが動いているコンピュートのローカルにダウンロードしてからアクセスしているという点です。[`w.files...`](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/files/files.html)などと記載されている部分でSDKを使っています。

```py:app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from databricks.sdk import WorkspaceClient

st.set_page_config(layout="wide")

# Unity Catalogボリュームのパスを指定（例: /Volumes/my_catalog/my_schema/my_volume）
# app.yaml経由で渡される環境変数を参照
VOLUME_PATH = os.getenv("VOLUME_PATH")

# WorkspaceClientの初期化
w = WorkspaceClient()

# ボリューム内のCSVファイル一覧を取得
def list_csv_files_in_volume():
    files = w.files.list_directory_contents(VOLUME_PATH)
    csv_files = [f.path for f in files if f.path.endswith('.csv')]
    return csv_files

# Volumeからファイルをダウンロードしてローカルパスを返す
# https://apps-cookbook.dev/docs/streamlit/volumes/volumes_download/
def download_csv_file(volume_path: str) -> str:
    # files.download() を使う（workspace.download() ではない）
    response = w.files.download(volume_path)
    file_content = response.contents.read()
    
    # ローカルに保存
    local_path = f"/tmp/{os.path.basename(volume_path)}"
    with open(local_path, 'wb') as f:
        f.write(file_content)
    
    return local_path

# ローカルパスからCSVをロード
def load_csv(local_path):
    return pd.read_csv(local_path)

st.header("Unity CatalogボリュームのCSVファイル可視化")

# ファイルアップロード機能
uploaded_file = st.file_uploader("CSVファイルをアップロード", type=["csv"])
if uploaded_file is not None:
    # ボリュームへのアップロード
    save_path = os.path.join(VOLUME_PATH, uploaded_file.name)
    w.files.upload(
        save_path,
        uploaded_file
    )
    st.success(f"{uploaded_file.name} をアップロードしました。")
    # ファイルポインタを先頭に戻す
    uploaded_file.seek(0)
    # アップロード直後に内容表示
    df_uploaded = pd.read_csv(uploaded_file)
    st.subheader("アップロードしたファイルの内容")
    st.dataframe(df_uploaded, height=400, use_container_width=True)

csv_files = list_csv_files_in_volume()
selected_file = st.selectbox("CSVファイルを選択してください", csv_files)

if selected_file:
    local_path = download_csv_file(selected_file)
    data = load_csv(local_path)
    st.dataframe(data, height=600, use_container_width=True)
    st.subheader("Plotlyで可視化")
    columns = data.columns.tolist()
    x_col = st.selectbox("X軸", columns)
    y_col = st.selectbox("Y軸", columns)
    fig = px.scatter(data, x=x_col, y=y_col, height=400, width=700)
    st.plotly_chart(fig, use_container_width=True)
```

アプリにアクセスすると以下のような画面になります。
![Screenshot 2025-12-03 at 10.34.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c27411bf-a89b-46ce-8f45-f30976b23672.png)

ファイルをアップロードします。
![Screenshot 2025-12-03 at 10.35.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7c3d8f86-9815-4354-86bb-4b84a2e03474.png)

ボリュームにもアップロードされています。
![Screenshot 2025-12-03 at 10.35.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a10e9685-0356-42d7-9132-1b5f1b31036a.png)

ボリューム内のファイルを選択して表示することもできます。
![Screenshot 2025-12-03 at 10.36.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a2d11311-fc8e-44e1-a974-997dd85d25bc.png)

簡単な可視化もできます。
![Screenshot 2025-12-03 at 10.37.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f8fc00a2-5c20-4d0b-8045-3bbfac980f57.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

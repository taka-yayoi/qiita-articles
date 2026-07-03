---
title: MLflowによるPyTorch MNIST分類器のトラッキング・サービング
tags:
  - Databricks
  - PyTorch
  - MLflow
private: false
updated_at: '2022-01-29T15:27:05+09:00'
id: 08a4dbea3c943a5ae2ea
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
本書では、Pytorch LightningによるMNIST分類器をMLflowでトラッキングし、サービングするところまでを説明します。REST APIへの入力が画像になるので、MLflowのtensorサポートを活用します。これによって、画像分類器をREST APIで呼び出せるようになり、機械学習モデルのシステム連携が容易に行えます。

[MLflowでTensorの入力をサポートしました \- Qiita](https://qiita.com/taka_yayoi/items/3e439dc5df7257fd41db)

> **注意**

> - MLflowのモデルサービングで`Cannot register 2 metrics with the same name`エラーが生じる場合、tensorflowのバージョンが2.6であることに起因する可能性があります。最新のランタイム10.2MLであればバージョン2.7になるので本エラーを回避できます。
  - [\[Solved\] Cannot register 2 metrics with the same name: /tensorflow/api/keras/optimizers \- Exception Error](https://exerror.com/cannot-register-2-metrics-with-the-same-name-tensorflow-api-keras-optimizers/)

> - MLflowのオートロギングを用いてモデルをトラッキングします。オートロギングが対応しているバージョンのpytorch-lightningをインストールします。
  - [mlflow\.pytorch — MLflow 1\.23\.1 documentation](https://mlflow.org/docs/latest/python_api/mlflow.pytorch.html#module-mlflow.pytorch)

>  > Autologging is known to be compatible with the following package versions: **1.0.5 <= pytorch-lightning <= 1.5.9**. Autologging may not succeed when used with package versions outside of this range.

# PyTorch Lightningのインストール

```py:Python
%pip install pytorch_lightning==1.5.9
```

# モデルの定義

こちらはトレーニングループのみを含む最もシンプルなサンプルです(バリデーション、テストなし)。

**注意** `LightningModule`はPyTorchの`nn.Module`です。単にいくつかの役立つ機能を持っているだけです。

```py:Python
from pytorch_lightning import LightningModule, Trainer

class MNISTModel(pl.LightningModule):
    def __init__(self):
        super(MNISTModel, self).__init__()
        self.l1 = torch.nn.Linear(28 * 28, 10)

    def forward(self, x):
        return torch.relu(self.l1(x.view(x.size(0), -1)))

    def training_step(self, batch, batch_nb):
        x, y = batch
        loss = F.cross_entropy(self(x), y)
        #acc = accuracy(loss, y) # エラーになるのでコメントアウト

        # PyTorchのロガーを使って精度情報を記録
        self.log("train_loss", loss, on_epoch=True)
        #self.log("acc", acc, on_epoch=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.02)
```

# トレーニングおよびMLflowによるトラッキング

精度指標のメトリクスは、上で`on_epoch=True`を指定しているので、エポックごとに記録されます。

```py:Python
# MLflowのエンティティを全てオートロギング
mlflow.pytorch.autolog()

# モデルを初期化
mnist_model = MNISTModel()

# MNISTデータセットのDataLoaderを初期化
train_ds = MNIST(os.getcwd(), train=True, download=True, transform=transforms.ToTensor())
train_loader = DataLoader(train_ds, batch_size=32)

# トレーナーを初期化
trainer = Trainer(
    gpus=0, # CPU
    max_epochs=20,
    progress_bar_refresh_rate=20,
)

# モデルをトレーニング ⚡
with mlflow.start_run() as run: # run IDを取得するためにブロックを宣言
  trainer.fit(mnist_model, train_loader)
```

画面右上の**Experiment**ボタンで表示される一覧でモデルを確認することができます。

![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/experiments.png)

日付の右にある![](https://docs.databricks.com/_images/external-link.png)アイコンをクリックすることで、さらに詳細を確認することができます。こちらでは、エポックごとのメトリクスの変化を確認することも可能です。

![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/metrics_graph.png)

メトリクスをクリックするとグラフが表示されます。

![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/metrics.png)

# TendorBoardの活用

ノートブック上で直接TensorBoardを活用することができます。

[データサイエンティスト向けの10個のシンプルなDatabricksノートブック tips & tricks \- Qiita](https://qiita.com/taka_yayoi/items/ba0294e20a19cdb1fe10#4-pytorchtensorflow%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8Btensorboard%E3%83%9E%E3%82%B8%E3%83%83%E3%82%AF%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89)

```py:Python
%load_ext tensorboard
%tensorboard --logdir /databricks/driver/lightning_logs/
```
![Screen Shot 2022-01-29 at 15.14.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/092bcb8e-0dca-3049-f4e9-79305aa7062b.png)

# モデルによる分類

これはデモなので、トレーニングデータセットの一部を用いて分類を行ないます。

[PyTorch 1\.0 \- How to predict single images \- mnist example? \- PyTorch Forums](https://discuss.pytorch.org/t/pytorch-1-0-how-to-predict-single-images-mnist-example/32394/2)

下のセルでは画像を確認するためにmatplotlibのimshowを用いて、ノートブック上に画像を表示しています。 

```py:Python
from matplotlib.pyplot import imshow

single_loaded_img = train_loader.dataset.data[0]
imshow(single_loaded_img)

single_loaded_img_conv = single_loaded_img[None, None]
single_loaded_img_conv = single_loaded_img_conv.type('torch.FloatTensor') # DoubleTensorの代替

out_predict = mnist_model(single_loaded_img_conv)
print(out_predict)
```

![Screen Shot 2022-01-29 at 15.15.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9471f949-3976-79d1-d38f-a7dcbcf3def4.png)

結果は0-9の判定結果となり、今回の例では3と判定してしまっていますが、次に進みます。

# モデルをMLflowモデルレジストリに登録

MLflowモデルレジストリに機械学習モデルを登録することで、モデルのバージョン、ステータス管理が可能となります。加えて、後述するモデルサービングと組み合わせることで、実験段階、テスト段階を経た機械学習モデルを本格運用することが可能となります。

モデルを登録する際に、モデルの入出力を規定するシグネチャ、デバッグに活用できるサンプルデータを指定します。

## シグネチャの準備

以下ではtensorをnumpyのarrayに変換した後で、シグネチャを推定しています。

```py:Python
input_img_np = single_loaded_img_conv.to('cpu').detach().numpy().copy()
out_predict_np = out_predict.to('cpu').detach().numpy().copy()

# MLflowモデルレジストリに格納するためにtensor入力を用いてモデルのシグネチャを作成します
signature = infer_signature(input_img_np, out_predict_np)

# どのように見えるかを確認します
print(signature)
```
![Screen Shot 2022-01-29 at 15.19.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e93f2f0b-cf81-50f9-808d-32cbff0982ff.png)

## 入力サンプルの準備

- MLflowモデルレジストリに格納する入力サンプルを作成します
- 入力サンプルをモデルレジストリに登録しておくと、モデルサービングの画面で入力サンプルを用いて簡単に動作確認を行うことができます

![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/post_example.png)

```py:Python
# np.expand_dims() は、第2引数の axis で指定した場所の直前に dim=1 を挿入します
input_example = np.expand_dims(input_img_np[0], axis=0)
```

## モデルレジストリへの登録

上で準備したシグネチャ、入力サンプルを指定してモデルレジストリに登録します。

```py:Python
mlflow.pytorch.log_model(mnist_model, model_name, signature=signature, input_example=input_example, registered_model_name=registered_model_name)
```

# モデルレジストリからモデルをロードして分類

モデルレジストリにモデルを登録すると、モデルバージョン固有のURIでモデルをロードすることができるようになります。

```py:Python
# モデルをロードしてサンプルの予測を実行しましょう
model_version = "1"
loaded_model = mlflow.pytorch.load_model(f"models:/{registered_model_name}/{model_version}")
```

```py:Python
data = train_loader.dataset.data[0]
print("data.type:", type(data))
print("data.shape:", data.shape)

imshow(data)

data_conv = data[None, None]
data_conv = data_conv.type('torch.FloatTensor') # DoubleTensorの代替

out_predict = loaded_model(data_conv)

print("分類結果:", out_predict)
```
![Screen Shot 2022-01-29 at 15.21.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/73604c4f-2953-8d2a-2fef-639e4409bcd8.png)

# REST APIを通じたモデルの呼び出し

上記モデルレジストリに移動し、モデルサービングを有効化します。
![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/enable_model_serving.png)

これまでのステップでtensorを受け取れるtensorflowモデルをモデルレジストリに登録しているので、REST API経由で画像分類が行えます。REST APIを使用する際には、パーソナルアクセストークンを発行し、REST API呼び出しの中にBearerトークンとして埋め込む必要があります。パーソナルアクセストークンは、サイドメニューの**Settings > User Settings**を開き、**Access Tokens**で**Generate New Token**をクリックします。

![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/PAT.png)

モデルサービングを有効化してもモデルが**Pending**から**Ready**にならない場合、モデルのデプロイに失敗している可能性があります。サービングの画面下部の**Logs**でエラーが起きていないか確認してください。
![](https://sajpstorage.blob.core.windows.net/demo20220129-pytorch-mlflow/serving_log.png)

[Databricksにおけるモデルサービング \- Qiita](https://qiita.com/taka_yayoi/items/b5a5f83beb4c532cf921#rest-api%E3%83%AA%E3%82%AF%E3%82%A8%E3%82%B9%E3%83%88%E3%81%AB%E3%82%88%E3%82%8B%E3%82%B9%E3%82%B3%E3%82%A2%E3%83%AA%E3%83%B3%E3%82%B0)

```py:Python
import os
import requests
import numpy as np
import pandas as pd

# tensorをエンドポイントに引き渡す際のフォーマットに変換
def create_tf_serving_json(data):
  return {'inputs': {name: data[name].tolist() for name in data.keys()} if isinstance(data, dict) else data.tolist()}

def score_model(dataset):
  # モデルのREST APIエンドポイント(モデルサービングの画面で確認できます)
  url = f'https://<Databricksホスト名>/model/{registered_model_name}/{model_version}/invocations'
  #print(url)
  
  headers = {'Authorization': f'Bearer {os.environ.get("DATABRICKS_TOKEN")}'}
  
  # datasetがデータフレームの場合はJSONに変換、そうでない場合はtensorを渡す際のJSONにフォーマットに変換
  data_json = dataset.to_dict(orient='split') if isinstance(dataset, pd.DataFrame) else create_tf_serving_json(dataset)
  #print(data_json)
  
  # API呼び出し
  response = requests.request(method='POST', headers=headers, url=url, json=data_json)
  if response.status_code != 200:
    raise Exception(f'Request failed with status {response.status_code}, {response.text}')
  return response.json()
```

```py:Python
data = train_loader.dataset.data[10]
print("data.type:", type(data))
print("data.shape:", data.shape)
imshow(data)

data_conv = data[None, None]
data_conv = data_conv.type('torch.FloatTensor') # DoubleTensorの代替
print(data_conv.shape)

# モデルサービングは、比較的小さいデータバッチにおいて低レーテンシーで予測するように設計されています。
served_predictions = score_model(data_conv)
print("分類結果:", served_predictions)
```

REST API経由でモデルを呼び出し、分類結果を取得できていることが確認できます。
![Screen Shot 2022-01-29 at 15.24.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d7ff724b-8d36-0e61-8e0d-00100b20e310.png)

# ファイルを指定して分類を実行

以下のセルのロジックは、ローカルマシンで画像を指定してモデルを呼び出して分類することを想定しています。

```py:Python
img = Image.open("/dbfs/FileStore/shared_uploads/takaaki.yayoi@databricks.com/five.jpg")
#img = Image.open("/dbfs/FileStore/shared_uploads/takaaki.yayoi@databricks.com/zero.jpg")
tf_image = np.array(img)

# Signatureに合わせます
tf_image = np.expand_dims(tf_image, axis=0)
input_example = np.expand_dims(tf_image, axis=0)

served_predictions = score_model(input_example)
print("分類結果:", served_predictions)
```

![Screen Shot 2022-01-29 at 15.25.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d50fa6b3-053b-57f0-91a9-b5d0ad4a89a8.png)


# サンプルノートブック

https://github.com/taka-yayoi/public_repo/tree/main/pytorch_serving

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

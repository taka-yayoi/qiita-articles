---
title: DatabricksにおけるTensorFlowの使用
tags:
  - TensorFlow
  - Databricks
private: false
updated_at: '2022-03-28T08:55:43+09:00'
id: ddcf5eb1373b4e28c8ba
organization_url_name: databricks
slide: false
ignorePublish: false
---
[TensorFlow \| Databricks on AWS](https://docs.databricks.com/applications/machine-learning/train-model/tensorflow.html#tensorboard) [2022/1/31時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

TensorFlowはGoogleによって開発された機械学習のオープンソースフレームワークです。CPU、GPU、GPUクラスターでのディープラーニング、一般的な数値計算をサポートしています。[Apache License 2\.0](https://github.com/tensorflow/tensorflow/blob/master/LICENSE)の元で提供されています。

[Databricks機械学習ランタイム](https://qiita.com/taka_yayoi/items/824b507019d3ade7eedc)にはTensorFlowとTensorBoardが含まれているので、パッケージをインストールすることなしにこれらのライブラリを利用することができます。使用しているDatabricks機械学習ランタイムバージョンにインストールされているTensorFlowのバージョンについては、[リリースノート](https://docs.databricks.com/release-notes/runtime/releases.html)をご覧ください。

:::note info
**注意**
このガイドはTensorFlowの包括的なガイドではありません。[TensorFlow website](https://www.tensorflow.org/)をご覧ください。
:::

# シングルノード、分散トレーニング

シングルマシンのワークフローをテストし移行するには、[シングルノードクラスター](https://qiita.com/taka_yayoi/items/6e7c6cc14a5017ef6d15)を使用します。

ディープラーニングにおける分散トレーニングのオプションについては、[分散トレーニング](https://docs.databricks.com/applications/machine-learning/train-model/distributed-training/index.html)をご覧ください。

# サンプルノートブック

以下のノートブックでは、シングルノードクラスターにおけるTensorFlow (1.xと2.x)とTensorBoardの実行方法を説明しています。

## TensorFlow 1.15/2.xノートブック

https://docs.databricks.com/_static/notebooks/deep-learning/tensorflow-single-node.html

# TensorBoard

[TensorBoard](https://www.tensorflow.org/tensorboard)は、TensorFlow、PyTorchなどの機械学習プログラムのデバッグ、最適化、理解のための可視化ツールのスイートです。

## TensorBoardを使う

### Databricksランタイム7.2以降でのTensorBoardの使用

DatabricksにおけるTensorBoardの起動は、お使いのローカルマシンにおけるJupyterノートブックでの起動方法と違いはありません。

1. `%tensorboard`マジックコマンドをロードし、ログのディレクトリを定義します。

    ```py
    %load_ext tensorboard
    experiment_log_dir = <log-directory>
    ```

1. `%tensorboard`マジックコマンドを実行します。

    ```py
    %tensorboard --logdir $experiment_log_dir
    ```

    TensorBoardサーバーが起動し、ノートブックのインラインにユーザーインタフェースを表示します。新規タブでTensorBoardを開くリンクも提供されます。

    以下のスクリーンショットは、ログのディレクトリを指定して起動されたTensorBoardのUIです。
![](https://docs.databricks.com/_images/tensorboard.png)

TensorBoardのnotebookモジュールを直接使用することで、TensorBoardを起動することもできます。

```py:Python
from tensorboard import notebook
notebook.start("--logdir {}".format(experiment_log_dir))
```

### Databricksランタイム7.1以前でのTensorBoardの使用

ノートブックからTensorBoardを起動するには、`dbutils.tensorboard`ユーティリティを使用します。

```py:Python
dbutils.tensorboard.start("/tmp/tensorflow_log_dir")
```

このコマンドを実行することで、クリックすると新規タブでTensorBoardが開くリンクが表示されます。

このAPIを用いて起動したTensorBoardは、`dbutils.tensorboard.stop()`で停止するか、クラスターを停止するまでは動作し続けます。

:::note info
**注意**
DatabricksのライブラリとしてクラスターにTensorFlowをアタッチした場合には、TensorBoardを起動する前にノートブックを再度アタッチする必要があるかもしれません。
:::
 
## TensorBoardのログとディレクトリ

TensorBoardは、[TensorBoard](https://www.tensorflow.org/tensorboard/get_started)や[PyTorch](https://pytorch.org/docs/stable/tensorboard.html)のTensorBoardのコールバックと関数によって生成されるログを読み込むことで機械学習プログラムを可視化します。他の機械学習ライブラリのログを生成するには、TensorFlowのfile writerをもyいいて直接ログを書き出すことができます(TensorFlow 2.xに関しては[Module: tf\.summary](https://www.tensorflow.org/api_docs/python/tf/summary)、TensorFlow 1.xの古いAPIについては[Module: tf\.compat\.v1\.summary](https://www.tensorflow.org/api_docs/python/tf/compat/v1/summary)をご覧ください)。

エクスペリメントのログが適切に記録されていることを確実にするためには、クラスターの揮発的ファイルシステムではなく、DBFS(Databricksファイルシステム。すなわち`/dbfs/`配下のログディレクトリ)に保存することをお勧めします。それぞれのエクスペリメントごとに、TensorBoardはユニークなディレクトリの元で起動します。ご自身のエクスペリメント内の機械学習コードの実行ごとにログが生成されるように、TensorBoardのコールバックあるいはfile writerがエクスペリメントディレクトリのサブディレクトリに書き込みを行うように設定します。このようにすることで、TensorBoard UIのデータはコードの実行ごとに分離されます。

ご自身の機械学習プログラムの情報をTensorBoardを用いて記録するには、公式の[TensorBoard documentation](https://www.tensorflow.org/tensorboard/get_started)をご覧ください。

## TensorBoardプロセスの管理

Databricksノートブック内で起動されたTensorBoardのプロセスは、ノートブックがデタッチされた際やREPLが再起動した際(例えば、ノートブックの状態をクリアした際)には停止されません。手動でTensorBoardのプロセスを停止するには、`%sh kill -15 pid`を用いて停止シグナルを送信します。TensorBoardプロセスを不適切に停止すると、`notebook.list()`を破損する可能性があります。

お使いのクラスターで動作しているTensorBoardサーバーの一覧を表示するには、TensorBoardノートブックモジュールから、対応するログディレクトリとプロセスIDを指定して`notebook.list()`を実行します。

## 既知の問題

- インラインのTensorBoard UIはiframeの中で動作します。リンクを新規タブで開かない場合、ブラウザのセキュリティ機能がUI内の外部リンクの動作を妨げる場合があります。
- TensorBoardの`--window_title`オプションはDatabricksで上書きされます。
- デフォルトでは、TensorBoardはリッスンするポートを選択するためにポートレンジをスキャンします。クラスターで多くのTensorBoardプロセスが稼働していると、ポートレンジの全てのポートが利用できない場合があります。引数`--port`を用いてポート番号を指定することでこの制限を回避することができます。指定されるポートは6006と6106との間である必要があります。
- リンクをどうさせるためには、TensorBoardを新規タブで開く必要があります。
- TensorBoard 1.15.0を使用する際、Projectorタブはブランクとなります。ワークアラウンドとしては、Projectorページに直接アクセスします。URLの`#projector`を`data/plugin/projector/projector_binary.html`で置き換えます。
- TensorBoard 2.4.0には、アップグレードした際にTensorBoardのレンダリングに影響を及ぼす[既知の課題](https://github.com/tensorflow/tensorboard/issues/4421)があります。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

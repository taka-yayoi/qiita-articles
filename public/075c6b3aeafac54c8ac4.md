---
title: Databricksのファイルシステムを可能な限りわかりやすく解説
tags:
  - Databricks
  - DBFS
  - Databricksクイックスタートガイド
private: false
updated_at: '2022-12-12T13:23:51+09:00'
id: 075c6b3aeafac54c8ac4
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Databricksに入社してから約2年になりますが、最初の壁となったのは**Databricksでファイルを読み書きする際にパスをどう指定すればいいのだろう**でした。

以下のような記事を書いてくる中で腹落ちはしましたが、Databricksを初めて触る方には敷居が高いと感じています。

- [Databricksファイルシステム\(DBFS\)](https://qiita.com/taka_yayoi/items/897264c486e179d72247)
- [Databricksにおけるファイルシステム](https://qiita.com/taka_yayoi/items/e16c7272a7feb5ec9a92)
- [DatabricksのFileStore](https://qiita.com/taka_yayoi/items/01d9b69d2f5283d27d96)
- [Databricksを使い始めたときに感じる疑問 \+ ベストプラクティス](https://qiita.com/taka_yayoi/items/8718c7c7d922e6f942bc)

そこでここでは、絵や実例を駆使して可能な限り分かりやすくファイルシステムを説明してみたいと思います。これでも分かりにくい場合には私の修行がまだ足りないので精進します。

> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

:::note
**注意**
この記事のスコープには[Unity Catalog](https://qiita.com/taka_yayoi/items/15aede468bdca58ec6a3)を含めていません。Unity Catalog(UC)ではファイルシステムにさらに新たなコンセプトを導入しているので、別途UCもスコープに含めた記事を書く予定です。
:::

# なぜ難しいと感じるのか？

改めて何が難しいのかを振り返ってみました。大きく2つあるのではないかと思います。

1. [ファイルシステムが2種類(Databricksファイルシステム / ドライバーノードのローカルファイルシステム)あることがわかりにくい](#なぜdatabricksには2種類のファイルシステムがあるのか)
1. [使っているAPIに応じてパスの書き方を変える必要があることがわかりにくい](#なぜ使っているapiに応じてパスの記述方法を変えなくてはいけないのか)

本書では、背景を含めて可能な限りわかりやすく説明していきます。

# なぜ、Databricksには2種類のファイルシステムがあるのか？

これは単にDatabricksとSparkのアーキテクチャによるところが大きいと思います。以下にDatabricksのアーキテクチャ図を示します。
![](https://camo.qiitausercontent.com/c1e64a93d6f61b66f188fdd281f9dbbef7817081/68747470733a2f2f71696974612d696d6167652d73746f72652e73332e61702d6e6f727468656173742d312e616d617a6f6e6177732e636f6d2f302f313136383838322f62353961333965342d613030372d333061382d626266352d3836333164333135656164312e706e67)

## Databricksファイルシステム

まず、上の図にあるようにDatabricksでファイルの永続化に使用する①の[DBFS(Databricksファイルシステム)](https://qiita.com/taka_yayoi/items/f15b50469b368907ec3b)が存在します。これは、お客さまのクラウドアカウントに構築されるデータプレーン上のオブジェクトストレージ(S3やADLS)を用いて構成される、仮想的なファイルシステムです。

https://qiita.com/taka_yayoi/items/f15b50469b368907ec3b

> DatabricksファイルシステムはDatabricksワークスペースにマウントされる分散ファイルシステムであり、Databricksクラスターから利用することができます。DBFSは、ネイティブクラウドストレージAPIの呼び出しにマッピングされる最適化FUSE(Filesystem in Userspace)インタフェースを提供するスケーラブルなオブジェクトストレージ上にある抽象化レイヤーです。

## Sparkクラスターのドライバーノードのローカルストレージ

そして、Databricksで計算資源を利用する際は、お客さまクラウドアカウント上に構築されるデータプレーン上に[Databricksクラスター](https://qiita.com/taka_yayoi/items/c5d99cd77fe4bfcf69f0)(Apache Sparkクラスター)を構成し、これにノートブックをアタッチして処理を実行します。クラスターの実態はAWSであればEC2、AzureであればVMになります。当然これらにはローカルのストレージがアタッチされています。これが上の図の②の部分です。

また、Sparkクラスターはドライバーノードとワーカーノードから構成されていますが、ユーザーは通常ドライバーノードにSparkジョブを投入して結果を受け取るというように、ドライバーノードとやり取りを行います。

これは、Databricksでも同様です。ノートブックをDatabricksにアタッチして処理を実行する際はドライバーノードとやり取りを行い、Sparkの並列分散処理はドライバーノードからワーカーノードに指示を行うことで実行され、結果がドライバーノードに戻され、その結果がノートブックに表示されます。

この処理の過程で②のローカルストレージにファイルを保存することが可能です。

## 2つのファイルシステムの違い

ここまでで2つのファイルシステムと言っていますが、ファイルの永続化に使えるのは①のDBFSだけです。クラスターのドライバーノードのローカルストレージは**揮発性**であり、クラスターを停止すると全てが失われます。このことを理解しておかないと、せっかく準備したデータがなくなってしまった！ということになりかねません。

ですので、計算処理過程での中間ファイルなどはローカルストレージに保存し、処理結果のファイルの永続化はDBFSで行うということを意識することが重要となります。

もう一つ重要な違いとして、DBFSはオブジェクトストレージで動作しているので、**ランダムアクセスはサポートされていません**。DBFSにおいてランダムアクセスが発生するような書き込み(例：zip)を行おうとするとエラーになります。この場合、[こちら](https://qiita.com/taka_yayoi/items/0197d5c985089255f16a)で説明している様にローカルファイルシステム上でzipファイルを作成してから、DBFSにコピーしてください。

|  | DBFS | ドライバーノードのローカルストレージ |
|:--|:--|:--|
| 永続化  | YES  |  NO |
| ランダムアクセス  |  NO | YES  |
| 容量制限  | なし  | あり[^1]  |
| アクセス制御  |  あり[^2] |  なし |

[^1]: EBSの拡張はサポートしています。
[^2]: [インスタンスプロファイル](https://qiita.com/taka_yayoi/items/446c7971be354f88c679)や[IAMクレディンシャルパススルー](https://qiita.com/taka_yayoi/items/5ed1c07debb4fecd474e)などを使用します。よりきめ細かいアクセス制御に関しては、[Unity Catalog](https://qiita.com/taka_yayoi/items/15aede468bdca58ec6a3)の使用を検討してください。

# なぜ、使っているAPIに応じてパスの記述方法を変えなくてはいけないのか？

上述した通りアクセスする先が違うので、そのことをDatabricksに教えてあげないといけないためです。

ただ、ここで物事をややこしくしているのが**コマンドのデフォルトの挙動**です。Databricksではファイルを操作する際に使用するAPIが複数存在しています。これらのそれぞれでデフォルトでDBFSにアクセスするのか、ローカルファイルシステムにアクセスするのかが違います。これは、それぞれのAPIの用途からすると自然な話ではあるのですが、初めて操作する際には詰まりやすいポイントだと思います。

大きく分けて、**分散ファイルシステム向けコマンド**と**ローカルファイルシステム向けコマンド**に分けて考えるといいかと思います。名前の通り、それぞれのファイルシステムがデフォルトになります。

|  | コマンド(API) | デフォルトのファイルシステム|
|:--|:--|:--|
| 分散ファイルシステム向けコマンド  | <ul><li>Spark API(PySparkなど)<li>`%fs`マジックコマンド<li>`dbutils.fs`ユーティリティ</ul>  | 分散ファイルシステム(DBFS)|
| ローカルファイルシステム向けコマンド  | <ul><li>ローカルファイルシステムAPI(pandas、pythonのosなど)<li>`%sh`マジックコマンド</ul>  |ドライバーノードのローカルファイルシステム|

そして、Databricksでは上述のコマンドのいずれにおいても、DBFS、ローカルファイルシステムにアクセスすることができるのですが、明示的に指示をしない場合、デフォルトのファイルシステムにアクセスします。

指示する方法は以下の通りです。

- 分散ファイルシステム向けコマンドでローカルファイルシステムにアクセスする場合: パスの先頭に`file:/`を追加
- ローカルファイルシステム向けコマンドでDBFSにアクセスする場合: パスの先頭に`/dbfs`を追加

:::note
**ティップス**
上の分散ファイルシステム向けコマンドで指定している`file:/`はいわゆるURLにおけるスキームであるのですが、DBFSのスキーム`dbfs:/`も存在しています。分散ファイルシステム向けコマンドで`dbfs:/`を指定することは必須ではないのですが、プログラムの意図を明確にするために、パスの先頭に`dbfs:/`を記述することをお勧めします。
:::

# 実践してみる

## マジックコマンド`%fs`

[マジックコマンド`%fs`](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%83%9F%E3%83%83%E3%82%AF%E3%82%B9%E8%A8%80%E8%AA%9E)はDBFSにアクセスするために使用できるコマンドです。クイックにファイルシステムを操作できます。このコマンドのデフォルトファイルシステムはDBFSです。以下のコマンドはDBFSの`/tmp`を一覧します。一覧されている**path**のスキームが`dbfs:/`になっていることに注意してください。

```sh
%fs ls /tmp
```
![Screen Shot 2022-12-11 at 10.14.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/df457c0c-d1fb-fb35-2a02-420a9459c41d.png)

DBFSのスキームは`dbfs:/`なので、以下のコマンドでも同じ結果となります。

```sh
%fs ls dbfs:/tmp
```

一方、ローカルファイルシステムのスキーム`file:/`を指定すると、クラスターのドライバーノードのローカルファイルシステムを参照することができます。

```sh
%fs ls file:/tmp
```
![Screen Shot 2022-12-11 at 10.16.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f22e3ea2-a5ed-4dac-bda4-ee5ca1a0f2e8.png)

## マジックコマンド`%sh`

[マジックコマンド`%sh`](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%83%9F%E3%83%83%E3%82%AF%E3%82%B9%E8%A8%80%E8%AA%9E)は、クラスターのドライバーノードでシェルスクリプトを実行できるコマンドです。このコマンドはドライバーノードローカルで動作することを前提としているので、このコマンドのデフォルトファイルシステムはローカルファイルシステムです。

```sh
%sh ls /tmp
```
![Screen Shot 2022-12-11 at 10.20.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/faa3f60e-d343-cc88-6b71-9586ac2f7010.png)

一方、パスの先頭に`/dbfs`を追加すると、クラスターのドライバーノードのローカルファイルシステムを参照することができます。

```sh
%sh ls /dbfs/tmp
```
![Screen Shot 2022-12-11 at 10.22.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e8faeb1c-e077-dee2-26ab-02eafbca42ca.png)

なお、`%sh`は`wget`などでデータをクイックにクラスター上に持ってきたい時に使うと便利です。

```sh
%sh
wget https://sajpstorage.blob.core.windows.net/yayoi/train.csv
```

## `dbutils.fs`ユーティリティ

`dbutils.fs`ユーティリティはマジックコマンド`%fs`と同様に、DBFSを操作するためのコマンドを提供しています。Pythonなどのプログラミング言語から呼び出すことができます。このコマンドのデフォルトファイルシステムはDBFSです。

```py:Python
display(dbutils.fs.ls("/tmp"))
```
![Screen Shot 2022-12-11 at 10.28.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/84e4169b-c84b-9c85-f47e-b86061b19a67.png)

ローカルファイルシステムを参照することも可能です。

```py:Python
display(dbutils.fs.ls("file:/tmp"))
```

さらには、ローカルファイルシステムとDBFS間でデータをコピーすることもできます。一時的にドライバーノードに保存しておいたファイルを永続化する際に`dbutils.fs.cp`はよく使います。

```py:Python
dbutils.fs.cp("file:/databricks/driver/train.csv", "dbfs:/tmp/")
```

:::note
**ティップス**
`%sh`を使う際のデフォルトのカレントパスは`file:/databricks/driver/`です。なので、上の`wget`で取得したファイルは`file:/databricks/driver/train.csv`に保存されています。
:::

```py:Python
display(dbutils.fs.ls("dbfs:/tmp/train.csv"))
```
![Screen Shot 2022-12-11 at 10.31.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c44810aa-da90-f61a-fbb3-75399fefef7c.png)

`dbutils.fs.head`でファイルの中身を確認することもできます。

```py:Python
dbutils.fs.head("dbfs:/tmp/train.csv")
```
![Screen Shot 2022-12-11 at 10.33.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/875a21a1-0d42-5250-7f6a-25d9adbfbf03.png)

`dbutils.fs.rm`で削除もできます。

```py:Python
dbutils.fs.rm("dbfs:/tmp/train.csv")
```
![Screen Shot 2022-12-11 at 10.33.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/88852ee1-40b9-581a-ca81-102f951a5be2.png)

## Spark API

PySparkなどSparkのAPIは、分散ファイルシステムを前提としているのでデフォルトファイルシステムはDBFSです。

```py:Python
df = spark.read.format("delta").load('dbfs:/databricks-datasets/learning-spark-v2/people/people-10m.delta')
display(df)
```
![Screen Shot 2022-12-11 at 10.39.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/24fedbe9-f1b3-eb13-d25d-8e3c0f16591c.png)

:::note
**ティップス**
`dbfs:/databricks-datasets`には色々な[サンプルデータ](https://qiita.com/taka_yayoi/items/3f8ccad13c6efd242be1)が格納されています。
:::

なお、Sparkではローカルファイルシステムでのファイルの読み書きはサポートされていないので、DBFSにあるファイルを操作する様にしてください。

## pandas API

pandasはローカルファイルシステムを前提としているのでデフォルトファイルシステムはドライバーノードのローカルファイルシステムです。

```py:Python
import pandas as pd

df = pd.read_csv("/databricks/driver/train.csv")
display(df)
```
![Screen Shot 2022-12-11 at 10.49.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/16d84497-cbec-75e3-cefa-f4c8ddec54b0.png)

`file:`をパスの先頭に追加した以下のセルでも同じ結果が得られます。

```py:Python
import pandas as pd

df = pd.read_csv("file:/databricks/driver/train.csv")
display(df)
```

DBFSのファイルを読み込むには、パスの先頭に`/dbfs`を追加します。

```py:Python
import pandas as pd

df = pd.read_csv("/dbfs/databricks-datasets/wine-quality/winequality-red.csv", sep=";")
display(df)
```
![Screen Shot 2022-12-11 at 10.53.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c746bd8b-f6c9-9a6d-d7a7-9a12d3e331e2.png)

# まとめ

ここまで説明してきたコンセプトは、最初はとっつきにくいところがあると思いますが、慣れると非常に生産性高く作業できる様になります。大事なのは、**クラスターは揮発性の計算資源・ストレージ資源であること**、**どのファイルシステムを操作しているのか**を常に意識することです。私はよく以下の様なフローを実行しています。

1. **[ローカルファイルシステム]** `wget`を使ってサンプルデータのzipをドライバーノードにダウンロード
1. **[ローカルファイルシステム]** ドライバーノードで`unzip`
1. **[ローカルファイルシステム -> DBFS]**`dbutils.fs.cp`でDBFSにファイルをコピー
1. **[DBFS]** `spark.read`でファイルをSparkデータフレームにロード
1. **[DBFS]** 処理結果をDBFSに永続化

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricksワークスペースのウォークスルー
tags:
  - Databricks
  - Databricksクイックスタートガイド
  - Databricksチュートリアル
private: false
updated_at: '2024-04-10T15:17:31+09:00'
id: a2fffa48fdf3f56dc00e
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらのマニュアルの翻訳にも記載がありますが、あらためて説明をまとめてみました。

https://qiita.com/taka_yayoi/items/dd41cd715aca272ff5ce

こちらのブログ記事でも詳細を説明しています。

https://qiita.com/taka_yayoi/items/4c5dea6c8cf8dcfdfcdc

:::note
**注意**
2024/4/10時点の内容です。機能追加やユーザビリティ改善によってGUIが変更されることがあります。
:::

# はじめに

Databricksを操作する際、ユーザーの方は[ワークスペース](https://qiita.com/taka_yayoi/items/e8556a32cc7aaf9ade50)で作業することになります。

ワークスペースでは、Jupyter notebookと同様の(色々拡張されていますが)[ノートブック](https://qiita.com/taka_yayoi/items/24a897cf40bba6d9e305)を用いて、様々なロジックを記述します。これらのノートブックはフォルダに格納することで整理することができます。

また、ノートブックに記述したロジックを実行するには、計算資源である[クラスター](https://qiita.com/taka_yayoi/items/c5d99cd77fe4bfcf69f0)が必要となります。要件に応じて様々な設定のクラスターを作成することができます。ノートブックを稼働中のクラスターにアタッチすることで、処理を実行できるようになります。

そして、Databricksで取り扱うデータは、[カタログやデータベース](https://qiita.com/taka_yayoi/items/e90be9beeb1a744cee0d)で管理することが可能です。

Databricksワークスペースにはこれ以外の機能もありますが、本書では上述の機能にフォーカスして関連する画面を説明します。

# ワークスペースのランディングページ

Databricksにログインすると以下のようなページが表示されます。これがランディングページです。
![Screenshot 2024-04-10 at 14.04.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b61b2c69-34ad-8e18-1544-8db624b2f511.png)

## 言語の変更

デフォルト言語が英語なので、日本語に切り替えます。

1. 画面右上の自分のメールアドレスをクリックしてメニューを展開します。
1. **User Settings**をクリックします。 
![Screenshot 2024-04-10 at 14.04.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/83e41541-b02c-5bc9-3676-efd9eb147ab3.png)
1. 設定画面に移動します。**Preferences**をクリックします。
![Screenshot 2024-04-10 at 14.05.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/661ce1e2-eb2e-0dce-8757-93943b1b8b7a.png)
1. **Language**から日本語を選択します。
![Screenshot 2024-04-10 at 14.06.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/20d020ae-1e95-5c65-1290-e8d5df35175d.png)
1. GUIが日本語になりました。
![Screenshot 2024-04-10 at 14.06.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9dd33773-8a31-f919-6024-b4e7b61b32cd.png)
1. 画面右上のdatabricksロゴをクリックして、ランディングページに戻ります。
![Screenshot 2023-01-25 at 11.45.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a747c4db-cd52-6063-6633-fea691fff4fc.png)

## サイドメニュー

あらためての画面紹介です。
![Screenshot 2023-01-25 at 11.51.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/90685f16-56e3-64a4-bbb7-9f7f55ecb7e4.png)

画面左に縦長に配置されているのがサイドメニューです。こちらから主要な機能にアクセスします。
![Screenshot 2024-04-10 at 14.07.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6b0de100-d70e-1403-3372-539c977462b4.png)

サイドメニュー上にカーソルを移動すると、メニューが展開されます。なおこの挙動はメニューの一番下にある**メニューを展開/メニューを折りたたむ**で変更することができます。
![Screenshot 2024-04-10 at 14.08.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6f28baf3-482b-c476-7128-5282f8a8cf4a.png)

今回触れるメニュー項目は以下の通りとなります。

- [新規](#新規)
- [ワークスペース](#ワークスペース)
- [クラスター](#クラスター)
- [カタログ](#カタログ)

各メニュー項目を説明する前に、ランディングページの他のコンポーネントを説明します。

## 検索ボックス

![Screenshot 2024-04-10 at 14.09.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/348031d2-6afc-d936-9de0-43314fb11419.png)

アクセス権があるノートブック、フォルダなどを検索することができます。ボックスにタイプしてくと候補が表示されます。
![Screenshot 2024-04-10 at 14.10.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/aad5bd40-d821-07b8-83f4-0b3b3f7533eb.png)

Enterを押すことで詳細画面が開きます。検索結果のリンクをクリックすることで当該ノートブックなどを開くことができます。
![Screenshot 2024-04-10 at 14.11.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0eecf64c-84e4-29bc-71fb-81919bac1574.png)


## ユーザー設定

画面右上の自分のメールアドレスをクリックするとメニューが展開し、ユーザー設定にアクセスすることができます。
![Screenshot 2024-04-10 at 14.11.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9006571a-187c-414f-774e-6e967cccca33.png)

## ヘルプ

ユーザー名の左のクエスチョンマークをクリックすると、アシスタント、ヘルプセンター、ドキュメントなどにアクセスすることができます。
![Screenshot 2024-04-10 at 14.12.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/144144ba-9645-1f11-b3ca-06388638e89e.png)


## サンプル・チュートリアル

画面上部にあるリンクは、Databricksを使い始めた際に利用することが多い機能のサンプルなどを説明しています。
![Screenshot 2024-04-10 at 14.09.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/20cc47ac-80dc-bc0a-d8d2-35ca27f23843.png)

## 最近のアイテム

最近アクセスしたノートブックなどにクイックにアクセスすることができます。
![Screenshot 2024-04-10 at 14.12.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6295276a-4130-cd96-26a9-f9bcc158d446.png)

## お気に入り

お気に入りに登録したアイテムにアクセスできます。
![Screenshot 2024-04-10 at 14.13.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/183f76ed-e436-a6e0-8d1b-1195ccdb04b0.png)

## 人気の

ワークスペースで頻繁にアクセスされているアイテムを参照できます。
![Screenshot 2024-04-10 at 14.14.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f1ec348a-17ca-9030-4f85-91b3846013d4.png)

ワークスペースの詳細はこちらをご覧ください。

https://docs.databricks.com/ja/workspace/index.html

# 新規ボタン

サイドメニューの**新規**をクリックすると、様々なDatabricks資産をクイックに作成することができます。ボタンをクリックするとメニューが展開されるので、作成したい資産を選択します。それぞれの資産の作成ダイアログが表示されるか、作成画面に移動します。
![Screenshot 2024-04-10 at 14.15.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b4049fd0-08e8-b7b5-c375-bddb9a8a82ec.png)

# ワークスペース

皆様が開発されるノートブックなどをフォルダに整理することができます。フォルダ階層にアクセスする際には**ワークスペース**をクリックします。
![Screenshot 2024-04-10 at 14.15.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1f003dfb-5b54-a506-ba3c-80393a697770.png)

(あなたを含む)各ユーザーのフォルダは**Users**配下に作成されます。**Users**フォルダをクリックすると、ワークスペースの全ユーザーのホームフォルダが表示されます。なお、アクセス権がない場合は表示されません。あなたのホームフォルダは常に一番上に表示されます。
![Screenshot 2024-04-10 at 14.16.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c6698f09-ab3d-b69b-dce1-62e2bbbc1dfe.png)


自分のユーザー名(メールアドレス)をクリックすると、あなたのホームフォルダが表示されます。なお、**自分のホームフォルダにはツリーの最上位にある**ホーム**でショートカットすることができます。**
![Screenshot 2024-04-10 at 14.17.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3c40a0c7-504c-f5e3-9300-021fe715f8eb.png)

フォルダ内のノートブックをクリックすることで、ノートブックをオープンすることができます。
![Screenshot 2024-04-10 at 14.17.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/75c66057-ad24-893d-5763-386fc888537d.png)


また、フォルダやノートブックの右側には常に![Screenshot 2024-04-10 at 14.18.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/990763d5-b6b9-d115-0b77-9a6e1631bb08.png)が表示されています。これはコンテキストメニューを開くためのアイコンです。こちらをクリックするとフォルダやノートブックを操作するためのメニューが表示されます。**右クリックでこの操作をショートカットすることができます。**
![Screenshot 2024-04-10 at 14.18.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ac910c51-5f53-c5ba-7d21-e87ec8170dc4.png)

# クラスター

上述したように、Databricksで処理を実行するには[クラスター](https://qiita.com/taka_yayoi/items/c5d99cd77fe4bfcf69f0)が必要です。サイドメニューの**クラスター**をクリックすると、アクセスできるクラスターの一覧が表示されます。
![Screenshot 2024-04-10 at 14.19.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/95262e95-917f-d962-6469-acb29fb7388f.png)

1. **コンピューティングを作成**をクリックします。
1. クラスター設定画面が表示されます。
![Screenshot 2024-04-10 at 14.20.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4c135240-d85d-bcfb-64c9-70b415414f03.png)
1. 必要に応じて設定を変更し、画面下の**クラスターを作成**をクリックします。
![Screenshot 2024-04-10 at 14.20.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d0d6d44d-1e82-dd98-bcff-09aea530b765.png)
1. クラスターが起動するまで待ちます。通常数分かかります。クラスター名の右にあるインジケーターがグリーンになるとクラスターが起動したことを意味します。
![Screenshot 2024-04-10 at 14.21.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/941533d0-a8b2-dc35-85f7-2b3408408d19.png)
1. これでクラスターが起動しました。
![Screenshot 2024-04-10 at 14.26.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c3c0e094-9061-f380-fb1f-8f1418932d93.png)

あと、少しクラスター設定画面の説明もします。

## ライブラリ

- **ライブラリ**をクリックすると、この画面からクラスターにライブラリをインストールすることができます。
![Screenshot 2024-04-10 at 14.26.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ba32c074-e190-e14c-5db7-af8f77c24c18.png)
![Screenshot 2024-04-10 at 14.27.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/64f4a201-5e49-f4e1-f30a-0fce40ab9b83.png)
- PyPI/CRAN/Mavenなどからライブラリをインストールすることができます。
![Screenshot 2024-04-10 at 14.28.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f8bf9679-e16a-6a79-70a9-967fc2f184dd.png)
- インストール済みの状態になると、クラスターにアタッチされているノートブックから`import`できるようになります。

## イベントログ

クラスターの起動、停止、サイズ変更などのイベントを確認することができます。
![Screenshot 2024-04-10 at 14.28.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/77a290ea-f599-f5ad-bf24-be05a0cf1d0a.png)


## クラスターの停止

クラスターが起動している時間でDatabricksの課金が発生します。クラスターを使わなくなったら、**終了**でクラスターを停止します。
![Screenshot 2024-04-10 at 14.29.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d531f4cf-6c4d-6087-53e9-ae7290b36449.png)

クラスター名の隣に灰色の●が表示されたらクラスターが停止したことを意味します。
![Screenshot 2024-04-10 at 14.30.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ed902666-1521-129b-3396-1a9ba2ef84ea.png)

クラスターの詳細はこちらをご覧ください。

https://docs.databricks.com/ja/compute/index.html

# ノートブック

[ノートブックを作成](#新規ボタン)するか、[既存のノートブックを開く](#ワークスペース)と、画面全体にノートブックが表示されます。ノートブックを表示した際には、ノートブック専用のメニューが表示されます。
![Screenshot 2024-04-10 at 14.31.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/aeeef659-2ced-d68f-5b38-f8e272aa3b9e.png)

ノートブックの詳細に関してはこちらをご覧ください。

https://docs.databricks.com/ja/notebooks/index.html

## タイトル・言語の変更

タイトルをクリックすると名称を変更、`Python`などの言語名をクリックするとノートブックのデフォルト言語を切り替えることができます。
![Screenshot 2024-04-10 at 14.31.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d36013f5-87f6-0fae-6f93-0f74a15bb4ad.png)
![Screenshot 2024-04-10 at 14.32.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c77037fb-68ac-232b-91f5-18d09cc2f1a5.png)

## ノートブックメニュー

- タイトルの下にはノートブックを操作するメニューが表示されます。
![Screenshot 2024-04-10 at 14.32.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/abbaf625-5b37-7905-f724-d2c86ba087f6.png)
- **すべてを実行**をクリックすると、ノートブックのすべてのコマンドが実行されます。
![Screenshot 2024-04-10 at 14.33.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2464faec-ccb1-0204-f1b8-d32ed98a0e28.png)
- **接続**と表示されているボタンをクリックすると、ノートブックをアタッチするクラスターを選択することができます。
![Screenshot 2024-04-10 at 14.34.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cb8eab7b-5f21-7d23-23fd-281d85dda6b4.png)
- クラスターを選択するとボタン名称がクラスター名に変化します。これでノートブックを実行できるようになります。
![Screenshot 2024-04-10 at 14.34.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/46683ef1-15ba-905b-7636-7ff6e9d6cc46.png)
- ノートブック左のボタンをクリックすると、目次、ワークスペース、カタログ、アシスタントが展開されます。
![Screenshot 2024-04-10 at 14.36.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/63ce176d-fb81-a9c2-778c-cb6ee742c449.png)
![Screenshot 2024-04-10 at 14.36.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5e066fde-0112-252d-9ec3-456a27ce8c3e.png)
![Screenshot 2024-04-10 at 14.36.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bf23f5d4-b255-a4e4-f5c1-b70f451716a4.png)
![Screenshot 2024-04-10 at 14.37.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/42bc8a7c-5338-11fd-9c4b-fa67099bfc33.png)
- ノートブック右のボタンをクリックすると、上からコメント、[エクスペリメント](https://qiita.com/taka_yayoi/items/e9f6d6628fbad209770b)、改訂履歴、変数、ライブラリが表示されます。
![Screenshot 2024-04-10 at 14.37.46.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/13f78d47-0e2c-a2cb-9ed2-f96ab9d36cbf.png)
![Screenshot 2024-04-10 at 14.38.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d4bb8c54-aa41-66c0-3781-16bbef87eb18.png)
![Screenshot 2024-04-10 at 14.38.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/517de767-df96-f54d-cb08-3b70c612e119.png)
![Screenshot 2024-04-10 at 14.38.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/23dc7786-9adb-983e-f80a-2b420890484b.png)
![Screenshot 2024-04-10 at 14.39.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d4ad77f7-2534-b03b-3f70-8937bd5dcac5.png)

## ノートブックの操作

ノートブックはセルから構成され、セルにロジックやマークダウンを記述します。

ここでは、pandasでデータを読み込んで可視化してみます。

1. 最初のセルに以下の内容を記述します。

    ```py
    import pandas as pd

    white_wine = pd.read_csv("/dbfs/databricks-datasets/wine-quality/winequality-white.csv", sep=";")
    ```

1. セルを追加するには、セルの上下端にカーソルを移動し、**+コード / +テキスト** ボタンを表示させます。これをクリックすることでセルを挿入することができます。
![Screenshot 2024-04-10 at 15.06.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/db38f35d-be95-48f8-c998-824f2b2db3ea.png)

1. 追加したセルに以下の内容を記述します。

    ```py:Python
    # 中身を確認します
    display(white_wine)
    ```

1. 個々のセルを実行するには、セルの左端に表示されている▶️ボタンを使用します。なお、**Shift + Enter**でショートカットすることができます。
![Screenshot 2024-04-10 at 15.08.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e194a2d5-17d3-58a4-1447-03ed9714dc3b.png)
![Screenshot 2024-04-10 at 15.09.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/458cd817-0aee-9005-ce35-68849f3d9b8c.png)

# カタログ

サイドメニューの**カタログ**を選択すると、カタログエクスプローラが表示されます。
![Screenshot 2024-04-10 at 15.10.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/73ba5853-757d-2034-ca8d-f566474e5b52.png)

テーブル名をクリックすることで、テーブルのスキーマやサンプルデータを確認することができます。
![Screenshot 2024-04-10 at 15.10.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9f09bfae-eb4f-3c5f-7526-e6db28256bb8.png)

カタログエクスプローラの詳細はこちらをご覧ください。

https://docs.databricks.com/ja/catalog-explorer/index.html

基本的な画面のご案内は以上となります。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

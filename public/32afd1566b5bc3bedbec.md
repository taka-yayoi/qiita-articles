---
title: DatabricksのLakeviewを使ってみる
tags:
  - Databricks
  - DatabricksSQL
  - Lakeview
private: false
updated_at: '2023-10-02T10:39:52+09:00'
id: 32afd1566b5bc3bedbec
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Databricksの新機能です。

https://qiita.com/taka_yayoi/items/4175cac499b5629de5a3

# Lakeviewとは

これまでも、[Databricks SQLのダッシュボード](https://docs.databricks.com/ja/sql/user/dashboards/index.html)を用いることで、BIダッシュボードを構築する事は可能でした。ただ、こちらはSQLによるクエリーの記述が必須となっており、IT技術者以外の方が活用するには敷居が高いところがありました。

様々なユーザーの方がレイクハウスのデータを活用してBIの取り組みを行えるように、シンプルかつスケーラブルなダッシュボードを提供するのがLakeviewです。

# Lakeviewダッシュボードの作成

Databricksワークスペースの**ダッシュボード**にアクセスすると、新機能の案内が表示され、**Lakeviewダッシュボード**のタブが表示されます。
![Screenshot 2023-09-23 at 9.14.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8f14e99b-b7a1-2c7f-c4d3-cb4ab8c2a130.png)
![Screenshot 2023-09-23 at 9.08.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8a124287-b4ce-76a5-9934-adaeb321437d.png)

**Lakeviewダッシュボードを作成**をクリックすると、キャンバスの説明が表示されます。
![Screenshot 2023-09-23 at 9.07.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7eaa75ca-1dd4-127b-e01b-5bdac4fb061d.png)

データセットを定義するために、**データ**タブをクリックします。**テーブルを選択**をクリックして、Unity Catalogのテーブルを選択します。ここでは、事前に作成しているCOVID-19の感染者数のテーブルを選択します。
![Screenshot 2023-09-23 at 9.28.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e68a4bc1-8ac7-519b-737e-490175890640.png)
![Screenshot 2023-09-23 at 9.28.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0baf4f1e-832c-2356-1978-0ea9c1d1e7de.png)

**Canvas**タブに切り替えてダッシュボードを作成していきます。最初にダッシュボードのタイトルを追加するためにテキストボックスを配置します。テキストにはマークダウンを使用できます。
![Screenshot 2023-09-23 at 9.29.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9fa1c8da-6c23-80b1-8d08-83668c272979.png)
![Screenshot 2023-09-23 at 9.29.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/47ee19e0-d4f0-ce32-ab6d-145d382bccff.png)

次にビジュアライゼーションを配置します。画面右に設定ペインが表示されます。
![Screenshot 2023-09-23 at 9.30.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a522706b-8424-667d-22a1-73cbb6265098.png)

X axisに日付、Y axisに感染者数を選択します。この場合、日付は自動で月に集計されていますが、Transformの部分で粒度を変更することができます。
![Screenshot 2023-09-23 at 9.30.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3a6204bc-e05d-be3d-a15b-916bdcdb9fa3.png)

折れ線グラフを追加したり、地方別にグルーピングすることもできます。
![Screenshot 2023-09-23 at 9.31.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2a854129-043a-43f8-8068-e44a6b6e051e.png)

# Lakeviewダッシュボードの公開

ここまでで作成したダッシュボードはドラフトの状態なので、他のユーザーに共有できるように公開します。画面右上の共有ドロップダウンから**公開**を選択します。
![Screenshot 2023-09-23 at 9.31.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/615886d4-8fa4-f3a0-66ce-8351519b255e.png)

資格情報を埋め込むかどうかを選択するダイアログが表示されます。今回はデフォルトのままとし、私の資格情報をダッシュボードに埋め込みます。
![Screenshot 2023-09-23 at 9.31.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9b608a8b-040a-e84a-3c56-dfa98e2772f4.png)

公開されたことを伝えるメッセージが表示されます。
![Screenshot 2023-09-23 at 9.32.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cbb12ef5-1dc5-c672-621c-456e54c3d22f.png)

メッセージに記載されているリンクをクリックすると公開状態のダッシュボードにアクセスできます。
![Screenshot 2023-09-23 at 9.32.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/26b9342d-3727-4db9-b334-df31e19f4a92.png)

# まとめ

ここまで1行のSQLを記述することなしにダッシュボードを構築することができました！クイックにダッシュボードを作成したい場合には是非Lakeviewをご活用ください！今後も機能拡張されていく予定です。

ちなみにフィルターも追加できます。
![F6rAjR4bAAEauxD.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fe024cc5-883f-ae82-1697-4d7f3c5b26e4.jpeg)


### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

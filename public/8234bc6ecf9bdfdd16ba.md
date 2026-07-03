---
title: Tableau CloudからDatabricksに接続する
tags:
  - Tableau
  - Databricks
private: false
updated_at: '2023-02-13T20:29:37+09:00'
id: 8234bc6ecf9bdfdd16ba
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらではTableau Desktopからの接続手順が説明されていますが、基本的には同じ手順です。

https://docs.databricks.com/partners/bi/tableau.html

以下では、すでにTableau CloudへのサインアップおよびTableauサイトのセットアップが完了しているものとします。まだの場合は、以下からサインアップしてください。

https://www.tableau.com/products/online/request-trial

# Databricksでの設定

Tableau CloudからDatabricksのデータにアクセスするには、以下のリソースと情報が必要となります。

- パーソナルアクセストークン
- SQLウェアハウス
    - サーバーのホスト名
    - HTTPパス

## パーソナルアクセストークンの取得

Databricks外部からDatabricksにアクセスする際に必要になるトークンです。トークン作成権限がない場合には、Databricks管理者に[こちらの手順](https://qiita.com/taka_yayoi/items/712170ba2f2c2bdf5d24#%E3%83%AF%E3%83%BC%E3%82%AF%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%83%99%E3%83%BC%E3%82%B9%E3%81%AE%E8%AA%8D%E8%A8%BC%E3%81%AE%E6%9C%89%E5%8A%B9%E5%8C%96%E7%84%A1%E5%8A%B9%E5%8C%96)に従って機能を有効化するよう依頼してください。

1. Databricksワークスペースにログインします。
1. サイドバーのペルソナスイッチャーから**SQL**を選択して、Databricks SQLにアクセスします。
1. トップバーのご自身のユーザー名をクリックし、**ユーザー設定**を選択します。
1. **Personal access tokens**タブをクリックします。
1. **新規トークンを生成**ボタンをクリックします。
![Screenshot 2023-02-13 at 14.17.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/14a5d394-40fb-f128-0c77-b87de56cc56e.png)
1. 必要に応じてコメントおよび存続期間を指定して**生成**をクリックします。
![Screenshot 2023-02-13 at 14.17.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/956da652-bfc8-acd1-0cfb-76b8e4be722a.png)
1. 表示されるトークンをコピーしておきます。

## SQLウェアハウスの起動

1. サイドメニューから**ウェアハウス**を選択します。
![Screenshot 2023-02-13 at 14.17.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/118a5568-0fa6-a8b8-974e-9343be1174f5.png)
1. **SQLウェアハウスを作成**ボタンをクリックします。
1. SQLウェアハウスの名前を**エンドポイント名**に入力します。ここでは**サイズ**は一番小さい`XXS`にします。タイプは`Pro`を選択します。
![Screenshot 2023-02-13 at 14.18.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/30f05d61-8af8-b532-adb4-cb64c4045b91.png)
1. **作成**ボタンをクリックします。
1. 権限管理が表示されます。権限を変更する場合に変更し、変更が不要であれば右上に**X**をクリックします。
![Screenshot 2023-02-13 at 14.18.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0a3e31e6-4adb-d280-2c54-5c331dc5f7cf.png)
1. SQLウェアハウスの**ステータス**が**実行中**になるまで待ちます。
![Screenshot 2023-02-13 at 14.18.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4d513478-337b-f316-ad55-393d385c231a.png)
1. 起動を確認したら、**接続の詳細**タブをクリックします。
![Screenshot 2023-02-13 at 14.23.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a268f9d7-766c-20d1-38d1-8dbf280e2e54.png)
1. **サーバーのホスト名**と**HTTPパス**をコピーしておきます。

# Tableau Cloudの設定

1. Tableau Cloudにログインします。
1. **Personal Space**に移動します。
1. **Create Workbook**をクリックします。
![Screenshot 2023-02-13 at 14.25.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f953845c-27d1-9773-633a-2585443ec523.png)
1. **Connectors**をクリックします。
![Screenshot 2023-02-13 at 14.25.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c4f4a385-3be7-5bc2-1e83-83384fe1eab3.png)
1. **Databricks**を選択します。
![Screenshot 2023-02-13 at 14.25.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a9e356f7-d309-aed7-f678-66d822cc8d4b.png)
1. **Server Hostname**に[上のステップ](#sqlウェアハウスの起動)でコピーした**サーバーのホスト名**、**HTTP Path**に[上のステップ](#sqlウェアハウスの起動)でコピーした**HTTPパス**を入力し、**Authentication**では**Personal Access Token**を選択し、**Password**には[パーソナルアクセストークン](#パーソナルアクセストークンの取得)を貼り付けます。
![Screenshot 2023-02-13 at 14.25.46.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/64a94c0f-0a5c-bd13-fb29-bbc099dcdfd6.png)
1. **Sign In**をクリックします。
![Screenshot 2023-02-13 at 14.26.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/87c1aaf7-c7ad-dd4d-0749-89ef717714b6.png)
1. 左側のペインでカタログ、データベース、テーブルを検索して選択していきます。
1. テーブルを右のペインにドラッグ&ドロップします。
![Screenshot 2023-02-13 at 14.30.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/821f1bea-ec27-7544-8db5-83477d91193f.png)

これでTableau CloudからDatabricksのデータにアクセスできました。使用しなくなったら[SQLウェアハウス](#SQLウェアハウスの起動)は停止しておいてください(自動停止しますが)。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

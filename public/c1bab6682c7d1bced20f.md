---
title: 'Microsoft ExcelからDatabricksに接続する [実践編]'
tags:
  - Excel
  - Databricks
private: false
updated_at: '2023-06-11T12:38:39+09:00'
id: c1bab6682c7d1bced20f
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Delta Sharingを使ったアプローチもありますが、これはODBC経由でデータにアクセスします。

https://qiita.com/taka_yayoi/items/df99ace34b8e2b8c13f5

こちらを見ながら設定します。今回はWindowsを使います。

https://qiita.com/taka_yayoi/items/8b21b3527d11571948ed

# Databricks側での準備

1. アクセスするDatabricks環境でクラスターを起動し、以下の情報をメモしておきます。
    - サーバーのホスト名
    - ポート
    - HTTPパス
    ![Screenshot 2023-06-11 at 12.20.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bd417f04-0d5f-1c9d-44b4-e4f2bcf5c785.png)

1. [パーソナルアクセストークン](https://qiita.com/taka_yayoi/items/712170ba2f2c2bdf5d24)を作成してメモしておきます。

# ローカルマシンでのODBC設定

以下のサイトからODBCドライバーをダウンロードしてインストールします。

https://www.databricks.com/spark/odbc-drivers-download

ODBCのデータソース名を作成します。ODBCデータソースアドミニストレーターを使います。

https://learn.microsoft.com/ja-jp/sql/database-engine/configure-windows/open-the-odbc-data-source-administrator?view=sql-server-ver16

ユーザーDSNを追加します。

1. Simba Spark ODBC Driverを選択します。
![excel1.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/df40c0d3-4d4e-1376-e530-c6f1e5778b6e.png)
1. Host(s)に[上のステップ](#databricks側での準備)でメモした**サーバーのホスト名**、Portには**ポート**を入力します。
1. AuthenticationではMechanismに**User Name and Password**、User Nameには`token`、Passwordにはパーソナルアクセストークンを入力するのですが、後のExcelのステップで再度聞かれました。
![excel2.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6234ccc8-09d9-a74a-7bff-eb65c38e452c.png)
1. **HTTP Options...** をクリックして、HTTPパスを入力します。
![ecvel3.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3603dbfd-3b26-38a3-62cd-48133d6520e2.png)
1. **SSL Options...** をクリックして、**Enable SSL**にチェックをつけます。
![excel5.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/48944dcc-8284-b0cc-647e-5e0ca9de316a.png)
1. **Test**をクリックして、**Success**と表示されることを確認します。
1. **OK**をクリックします。

# Excelへのデータの読み込み

1. Excelを起動します。
1. **データ**リボン、**データの取得 > その他のデータソースから > ODBCから**を選択します。
![excel9.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2828bc61-a527-cbf0-f64f-b906150dee85.png)
1. [上のステップ](#ローカルマシンでのodbc設定)で作成したデータソース名を選択します。
![excel6.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/efb992f9-a040-7c8d-a9b5-d4a3709bf49b.png)
1. ユーザー名に`token`、パスワードにはパーソナルアクセストークンを入力します。
![excel7.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/70100d43-0225-3fba-60af-ff98b8bd1f38.png)
1. Databricksのカタログ、データベースが表示されます。
![excel8.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/70ea22c4-fff4-cb82-f063-423d02f75008.png)
1. テーブルを選択するとプレビューが表示されます。**読み込み**をクリックします。
![excel10.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a789bd0a-4bab-37e7-cf5a-241cf471cbba.png)
1. Excelにデータが読み込まれました！
![excel11.PNG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/01e6f700-2879-7348-a346-37ea678bbbf1.png)

Excelで作業した方が効率的なシーンも存在しますので、適材適所で使い分けてください！

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

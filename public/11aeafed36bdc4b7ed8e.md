---
title: Databricksにおけるテーブル作成
tags:
  - Databricks
private: false
updated_at: '2024-07-16T09:46:30+09:00'
id: 11aeafed36bdc4b7ed8e
organization_url_name: databricks
slide: false
ignorePublish: false
---
考えたらきちんと手順をまとめたことがありませんでした。

関連するマニュアルに触れながらウォークスルーしていきます。Databricksでテーブルを作成する方法はいくつかありますが、ここでは一番簡単なGUIを使ってローカルマシンからファイルをアップロードする方法にフォーカスします。

# 考え方

Databricksでは、データの保存とアクセスのための2つの主要なセキュリティ保護可能なデータベースオブジェクトを使用します。

- [**テーブル**](https://docs.databricks.com/ja/tables/index.html)は、表形式のデータへのアクセスを制御します。
- [**ボリューム**](https://docs.databricks.com/ja/volumes/index.html)は、表形式以外のデータへのアクセスを制御します。

これらはすべて、Databricksの統合ガバナンスソリューションである[Unity Catalog](https://www.databricks.com/jp/product/unity-catalog)によって管理されます。

![Screenshot 2024-07-16 at 9.32.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bdab3632-fb34-5d13-b132-ef91a90a1ef2.png)
![Screenshot 2024-07-16 at 9.33.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4195702c-49d2-cb76-df6d-d7ed3c6836e4.png)

Unity Catalogでは、テーブルなどのデータベースオブジェクトは**カタログ**と**スキーマ(データベース)** によって整理されます。

[カタログ](https://docs.databricks.com/ja/catalogs/index.html)は、データベースオブジェクトに対する最上位レベルのコンテナとなります。
![Screenshot 2024-07-16 at 9.34.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d50ae616-6f2e-09cf-5d3e-0ec91c063e91.png)

従来のデータベースでは、テーブルにアクセスする際には`(スキーマ)データベース`.`テーブル`という2レベルの名前空間でテーブルにアクセスしていましたが、Unity Catalogでは最上位にカタログが存在するので、`カタログ`.`(スキーマ)データベース`.`テーブル`という3レベルでの名前空間を用いることになります。
![Screenshot 2024-07-16 at 9.36.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ad5959cc-9ef3-2712-7309-e868bcf8f976.png)

テーブルなどのデータベースオブジェクトは、カタログ配下の[スキーマ(データベース)](https://docs.databricks.com/ja/schemas/index.html)に格納されることになります。
![Screenshot 2024-07-16 at 9.37.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c084a120-7ef3-be27-0a86-44652e9fa4d6.png)

# テーブル作成の準備

テーブルを作成する方法はいくつか存在しますが[UIを使う](https://docs.databricks.com/ja/ingestion/add-data/index.html)のが最も簡単です。

データ追加UIを使う前に以下を検討・確認します。

1. **どこにテーブルを作成するのか**
    どのカタログのどのスキーマ(データベース)の中にテーブルを作成するのかを決めます。
1. **十分な権限を持っているか**
    対象のカタログ、スキーマに対して必要な権限を持っていることを確認します。対象のカタログに対する`USE CATALOG`権限、対象のスキーマに対する`USE SCHEMA`と`CREATE TABLE`権限が必要となります。権限の詳細は[こちら](https://docs.databricks.com/ja/data-governance/unity-catalog/manage-privileges/index.html)をご覧ください。
1. **テーブル名**
1. **作成処理に使用するSQLウェアハウス**

# テーブルの作成

Databricksワークスペースにログインして、サイドメニューから **新規 > データ** を選択します。
![Screenshot 2024-07-16 at 8.47.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/79436976-a7d9-b66d-9efa-2b0d33b70870.png)

**テーブルを作成または変更**を選択します。
![Screenshot 2024-07-16 at 8.49.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7ebc01d0-abf9-ab7f-1f43-4242d1e19d9e.png)

画面右上のドロップダウンから作成処理に用いるSQLウェアハウスを選択します。そして、テーブル作成に使用するデータファイル(CSVファイルなど)を中央のボックスにドラッグ&ドロップします。
![Screenshot 2024-07-16 at 8.51.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0483042d-90e1-7c46-d171-4ffab0080511.png)

データのプレビューが表示されます。
![Screenshot 2024-07-16 at 8.55.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c2615c94-4e0e-6deb-d0dc-2faccd384fc8.png)

テーブルを作成するカタログとスキーマ(データベース)を選択します。必要に応じてテーブル名を変更します。
![Screenshot 2024-07-16 at 8.57.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/be18f63c-26eb-35e9-0044-da1f4664716e.png)

CSVの区切り文字の変更など詳細な設定を行う場合には、**詳細な設定**をクリックします。
![Screenshot 2024-07-16 at 8.59.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/55dad73e-cfab-2c40-21f2-a33d86965239.png)
![Screenshot 2024-07-16 at 8.59.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5d8a6525-4c21-9984-7250-7de09a59a1b6.png)

列名や列のデータ型を変更するには、列をクリックします。
![Screenshot 2024-07-16 at 9.01.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fe0ea290-c461-8150-73e7-63441eb1bca5.png)
![Screenshot 2024-07-16 at 9.01.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/11131d2d-fb54-a023-b3de-7a3d22c5b285.png)

設定を確認したら、画面右下の**テーブルを作成**をクリックします。
![Screenshot 2024-07-16 at 9.03.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0ea7d301-f035-8af6-5af4-324bafba2d03.png)
![Screenshot 2024-07-16 at 9.03.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f490a85d-0745-93d2-3744-098d60e305eb.png)

これでテーブルが作成されました。
![Screenshot 2024-07-16 at 9.04.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bce5264b-839d-f6f2-b1ff-ca8712f814e9.png)

# テーブルへのクエリー

サイドメニューの**SQLエディタ**にアクセスし、テーブルに問い合わせを行うSQLを実行します。
![Screenshot 2024-07-16 at 9.06.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/444743c3-2f01-e729-0179-ee280aa9d85b.png)

# ボリュームからのテーブル作成

ボリュームに格納されているファイルからテーブルを作成することもできます。詳細は[こちら](https://qiita.com/taka_yayoi/items/bce88ffea7d4e2254046)をご覧ください。
![68747470733a2f2f71696974612d696d6167652d73746f72652e73332e61702d6e6f727468656173742d312e616d617a6f6e6177732e636f6d2f302f313136383838322f35336161653565662d353166612d346563352d623339332d3135386337386566393231382e706e67.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d4be62f6-41f8-6878-371c-6f524b7202a6.png)


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

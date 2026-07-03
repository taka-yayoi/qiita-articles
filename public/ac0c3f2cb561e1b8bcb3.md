---
title: 西日本リージョンのAzure DatabricksでサーバレスSQLを使う
tags:
  - Databricks
  - AzureDatabricks
  - DatabricksSQL
  - DeltaSharing
  - UnityCatalog
private: false
updated_at: '2024-04-02T12:41:25+09:00'
id: ac0c3f2cb561e1b8bcb3
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
社内でサーバレス熱が高まっているので、自分も乗っかります。

https://qiita.com/Mitsuhiro_Itagaki/items/f580440a3c19429a73f7

https://qiita.com/kohei-arai/items/7b4e15a4cf79aa827957

嬉々として以前こちらの記事を書きました。

https://qiita.com/taka_yayoi/items/1f314088d8917387277d

しかし、今時点では西日本リージョンではサーバレスSQLが使えません。申し訳ありません。

こちらではワークアラウンドとしてDelta Sharingを使う方法をご紹介します。@kohei-araiさんに教えてもらいました。

# 全体像

データは西日本リージョンに配置しておきながらも、サーバレスを使える東日本リージョンにDelta Sharigでデータを共有します。この際、データのコピーは発生せず、東日本リージョンから直接西日本リージョンのデータを読み込む形になります。[こちら](https://learn.microsoft.com/ja-jp/azure/databricks/data-sharing/create-recipient)にある**Databricks 間共有**を行います。
![Screenshot 2024-04-02 at 11.57.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6120de4d-b998-9bc8-7a55-ccf74bffb43d.png)

# アカウントコンソールでの作業

いずれのリージョンでもUnity CatalogおよびDelta Sharingを有効化します。

## 東日本

今回の例では西日本側でUnity Catalogを有効化していなかったので、メタストアを作成してワークスペースにアタッチします。
![Screenshot 2024-04-02 at 10.28.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cca2d442-65f5-c9d0-d9de-c09086430014.png)
![Screenshot 2024-04-02 at 10.28.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4f83d395-11a8-d3e7-951a-7789963d5e5f.png)
![Screenshot 2024-04-02 at 10.29.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1daaafd7-2e37-7fb6-805d-cce6ca230055.png)

**Delta Sharing**の配下にある`Databricksのユーザーが組織外にデータを共有できるように、Delta Sharingを有効化します`をチェックします。
![Screenshot 2024-04-02 at 11.36.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/66538091-860d-23dd-57ea-dfcc8d7d37c5.png)

トークンの有効期間や組織名を設定して**有効化**をクリックします。
![Screenshot 2024-04-02 at 11.36.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/49b4a3b2-2ff7-ac4d-7436-dcdde04127b7.png)

## 東日本

こちらでもDelta Sharingを有効化します。
![Screenshot 2024-04-02 at 11.44.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8767d299-62d9-7151-e1e0-a5603d94ea7b.png)

# 西日本ワークスペースでの作業

カタログエクスプローラで共有するテーブルを格納する、カタログとスキーマ(データベース)を作成します。
![Screenshot 2024-04-02 at 10.32.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/21fd6df0-6307-cef8-1c01-555b4869b4bc.png)
![Screenshot 2024-04-02 at 10.33.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2a56d9ed-e645-7ae5-8b0f-6fbdff9badcd.png)

画面左上の**テーブルを作成**をクリックします。
![Screenshot 2024-04-02 at 12.04.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/76e64706-2b3d-c356-779f-b8de40b311c3.png)

ここではCOVID感染者数のCSVを使ってテーブルを作成しています。
![Screenshot 2024-04-02 at 11.32.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c0765eb6-e44f-e452-5d38-e6f450f6d8b2.png)
![Screenshot 2024-04-02 at 11.33.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/543b4c10-b08c-429b-ec3b-8c696cb1eaf3.png)

カタログエクスプローラ右側の**Delta Sharing**にアクセスし、**自分が共有**をクリックします。**データを共有**をクリックします。
![Screenshot 2024-04-02 at 11.33.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/452bd22d-cc2b-cb61-0c35-6834b2e1d8c7.png)

共有名を入力して作成します。
![Screenshot 2024-04-02 at 11.33.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cc07a1df-4b32-dfab-d77d-0f506faa7ec1.png)
![Screenshot 2024-04-02 at 11.34.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0bbe8239-d7dd-f4df-90a2-2926cac5fb77.png)

アセットを追加をクリックします。スキーマにチェックを入れ**権限を付与して選択**をクリックします。
![Screenshot 2024-04-02 at 11.35.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/74b2f54a-401e-d8c6-eb3d-3b1484c37609.png)

**保存**をクリックします。このスキーマが共有対象となります。
![Screenshot 2024-04-02 at 11.35.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5a89ab0f-0397-3832-110a-5f7c0dbe5966.png)

受信者を追加する前に東日本のワークスペースで作業します。

# 東日本ワークスペースでの作業

SQLノートブックを作成して以下を実行します。

```sql
SELECT CURRENT_METASTORE();
```
```
azure:japaneast:xxxxx
```

上の識別子をコピーしておきます。

# (再度)西日本ワークスペースでの作業

カタログエクスプローラで上で作成した共有にアクセスし、**新たな受信者**をクリックします。**共有識別子**上の識別子を入力して、**作成**をクリックします。
![Screenshot 2024-04-02 at 11.47.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/15b856ca-835f-4857-3c88-984adc5fd4fa.png)

**共有**タブをクリックします。
![Screenshot 2024-04-02 at 11.47.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d0476c99-42b0-8d60-f5b6-e6debaf17bf9.png)

共有オブジェクトを選択して**付与**をクリックします。
![Screenshot 2024-04-02 at 11.47.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3518c8f7-2ca3-8794-3e99-bf169336e4eb.png)

これで共有の設定は完了です。
![Screenshot 2024-04-02 at 11.48.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/44c53c34-3f5e-58bc-2543-e342284043c9.png)

# (再度)東日本ワークスペースでの作業

カタログエクスプローラの**Delta Sharing > 自分と共有**を選択し、上で設定されている共有が表示されていることを確認します。
![Screenshot 2024-04-02 at 11.48.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a9deede1-a470-a5d1-302a-385664e854db.png)

**カタログを作成**をクリックします。
![Screenshot 2024-04-02 at 11.48.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/968d1eee-0ca7-d648-3814-7bd6ab87789a.png)

作成するカタログ名を指定して**作成**をクリックします。
![Screenshot 2024-04-02 at 11.49.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7f01bb05-888b-a3e7-d04b-0c6f7d98bf13.png)

これでカタログエクスプローラは以下のカタログとして西日本リージョンのテーブルが表示されるようになります。
![Screenshot 2024-04-02 at 11.49.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f74bc50e-0fa9-2abc-e157-4e3cbf8345e6.png)

東日本リージョンはサーバレスSQLが使えるので、データの確認もサクサクです。
![Screenshot 2024-04-02 at 11.50.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9dad5309-d127-5bd8-a8e4-7ff8906279f1.png)
![Screenshot 2024-04-02 at 11.50.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/db499d42-edbf-1b8b-61c3-cb54ece55224.png)

ご活用ください！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

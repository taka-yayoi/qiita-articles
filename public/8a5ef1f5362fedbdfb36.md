---
title: Databricks AutoMLの時系列予測で各国の休日がサポートされてました
tags:
  - Databricks
  - AutoML
private: false
updated_at: '2023-10-14T21:40:12+09:00'
id: 8a5ef1f5362fedbdfb36
organization_url_name: databricks
slide: false
ignorePublish: false
---
昨日アップデートを見逃していました。

![Screenshot 2023-10-14 at 21.30.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/03a93f70-9d57-a8ac-d0d2-dbc4c3437866.png)

Databricksランタイム12.0以降であれば、各国の休日を指定できるようになってました。これまでは米国しか指定できなかったのでした。

せっかくですので、[先日試したunerry様のデータ](https://qiita.com/taka_yayoi/items/af35659038f8d77a59a9)を使います。AutoMLで予測する際には、目的変数のカラムがfloat型である必要がありますので、型変換をして新規にテーブルを作成します。

```sql:SQL
CREATE TABLE main.default.visitor_automl AS
SELECT
  date,
  cast(total_visitor as FLOAT) as total_visitor 
FROM
  unerry_catalog.default.sample_st_daily_visitor;
```

このテーブルを指定します。
![Screenshot 2023-10-14 at 21.27.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/07505e1b-1082-3045-05ee-41d2f5bb43bf.png)

さらに**国の祝日**で`Japan`を選択します。
![Screenshot 2023-10-14 at 21.27.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6c45c6ef-1c9d-9a05-cac6-c4c9c8fbafea.png)

AutoMLを実行します。
![Screenshot 2023-10-14 at 21.34.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7689ebda-85aa-c7fd-f872-0ee0ef57effa.png)

**View notebook for best model**のリンクをクリックすることで予測結果も確認できます。黒い点は実績値で、点がない部分が予測結果です。
![Screenshot 2023-10-14 at 21.35.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/69266a61-d80b-db23-72b0-de366ec9b66e.png)

7/1からの10日間の予測なので休日が入ってませんので休日の影響を確認できませんでしたが、これまでより実用性は高まっていると思います。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

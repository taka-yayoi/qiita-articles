---
title: Databricksノートブックの結果テーブルの改善
tags:
  - Databricks
private: false
updated_at: '2025-01-24T17:23:32+09:00'
id: 84711db7c9fd4aeeea7a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: fd9d012cdc6dcd0b2f5c
agreed_posting_campaign_term: true
---
こちらのアップデートです。

https://docs.databricks.com/en/release-notes/product/2025/january.html#notebook-output-improvements

ノートブック出力体験に次の改善が行われました：

- **「いずれかの値を含む」フィルタリング：** 結果テーブルで、「いずれかの値を含む」条件を使用して列をフィルタリングし、フィルタリングしたい値を選択できるようになりました。列の横にあるメニューをクリックし、フィルタをクリックします。フィルタモーダルが開き、フィルタ条件を追加できます。結果のフィルタリングについて詳しくは、[結果のフィルタリング](https://docs.databricks.com/ja/notebooks/notebook-outputs.html#filter-results)を参照してください。
- **結果テーブルのコピー：** 結果テーブルをCSV、TSV、またはMarkdownとしてコピーできるようになりました。コピーしたいデータを選択し、右クリックしてコピーとしてを選択し、希望する形式を選択します。結果はクリップボードにコピーされます。データをクリップボードにコピーする方法については、[データをクリップボードにコピー](https://docs.databricks.com/ja/notebooks/notebook-outputs.html#copy-data-to-clipboard)するを参照してください。
- **ダウンロードファイル名：** セルの結果をダウンロードする際、ダウンロード名がノートブック名に対応するようになりました。[結果のダウンロード](https://docs.databricks.com/ja/notebooks/notebook-outputs.html#download-results)を参照してください。

SQLなどでテーブルにクエリーを実行し、結果テーブルを表示させるところからスタートします。

![Screenshot 2025-01-24 at 17.15.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/44ad5a92-4eac-5851-4511-99ec9210542e.png)

# 「いずれかの値を含む」フィルタリング

フィルタリング条件として追加したい列の列名の右にある3点リーダーをクリックし、**フィルタ**を選択します。

![Screenshot 2025-01-24 at 17.15.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2ae77390-5cc8-b745-adba-1d03689d8a95.png)

選択した列から値を選択するためのダイアログが表示されます。

![Screenshot 2025-01-24 at 17.16.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fff73616-ad1b-4e76-9b98-be0508f8692d.png)

値を選択していくことでクイックに絞り込みを行うことができます。

![Screenshot 2025-01-24 at 17.17.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bc8ce0b7-5893-43e6-a554-6b11622a6403.png)

# 結果テーブルのコピー

これは地味に嬉しい機能。グラフィカルに表示されると参照は便利ですが、別の場所に値を貼り付けるのが大変でしたので。CSV、TSV、マークダウンでコピーできます。

結果テーブルの左上をクリックしテーブルを選択した状態で右クリックするとメニューが表示されます。ここで**コピー > CSV**などと選択することで、指定したフォーマットでテーブルがコピーされます。マークダウンでコピーできるのは嬉しいです。

![Screenshot 2025-01-24 at 17.21.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8eddf8e1-9ab5-fecf-8881-d1c2f13bd85b.png)

![Screenshot 2025-01-24 at 17.21.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c5e171b5-4017-a340-b66d-df2c1e566b12.png)


こんな感じで結果をこちらに貼り付けることもできます。

|tpep_pickup_datetime|tpep_dropoff_datetime|trip_distance|fare_amount|pickup_zip|dropoff_zip|
|---|---|---|---|---|---|
|2016-02-13T21:47:53.000+00:00|2016-02-13T21:57:15.000+00:00|1.4|8|10103|10110|
|2016-02-13T18:29:09.000+00:00|2016-02-13T18:37:23.000+00:00|1.31|7.5|10023|10023|
|2016-02-06T19:40:58.000+00:00|2016-02-06T19:52:32.000+00:00|1.8|9.5|10001|10018|
|2016-02-12T19:06:43.000+00:00|2016-02-12T19:20:54.000+00:00|2.3|11.5|10044|10111|
|2016-02-23T10:27:56.000+00:00|2016-02-23T10:58:33.000+00:00|2.6|18.5|10199|10022|
|2016-02-13T00:41:43.000+00:00|2016-02-13T00:46:52.000+00:00|1.4|6.5|10023|10069|
|2016-02-18T23:49:53.000+00:00|2016-02-19T00:12:53.000+00:00|10.4|31|11371|10003|
|2016-02-18T20:21:45.000+00:00|2016-02-18T20:38:23.000+00:00|10.15|28.5|11371|11201|
|2016-02-03T10:47:50.000+00:00|2016-02-03T11:07:06.000+00:00|3.27|15|10014|10023|
|2016-02-19T01:26:39.000+00:00|2016-02-19T01:40:01.000+00:00|4.42|15|10003|11222|

# ダウンロードファイル名

これまでは確か`download.csv`といった画一的な名前でしたが、ノートブック名が組み込まれるようになりました。

![Screenshot 2025-01-24 at 17.23.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/34dce7d1-7a13-edc2-8ad8-f4fcdc09eb22.png)

ご活用ください

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

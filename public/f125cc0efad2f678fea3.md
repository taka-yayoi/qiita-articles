---
title: DatabricksにおけるSQL書式設定のカスタマイズ
tags:
  - Databricks
private: false
updated_at: '2025-05-14T09:51:27+09:00'
id: f125cc0efad2f678fea3
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらの機能です。

https://docs.databricks.com/aws/ja/sql/user/sql-editor/custom-format

非常にわかりやすい動画を作っていただきました。ありがとうございます！

<iframe width="485" height="862" src="https://www.youtube.com/embed/vSiRIu134EQ" title="#shorts Databricksのカスタム形式のSQL ステートメントを試してみた　#databricks #sqlforbeginners" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

設定ファイル`.dbsql-formatter-config.json`で、SQL書式設定の挙動をカスタマイズできるようになりました。ノートブック、SQLエディタに適用されます。

以下のようにインデントを10にして、ホームフォルダに保存します。

```json:.dbsql-formatter-config.json
{
  "printWidth": 80,
  "indentationStyle": "spaces",
  "indentationWidth": 10,
  "keywordCasing": "uppercase",
  "shouldExpandExpressions": true
}
```

ノートブックで以下のようなSQLを記述します。

```sql
SELECT * FROM takaakiyayoi_catalog.japan_covid_analysis.covid_deaths;
```

**SQLをフォーマット**を選択します。

![Screenshot 2025-05-14 at 9.46.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/01c0dead-af67-4df3-b3c8-0490c2034489.png)

インデントが反映されました。

```sql
SELECT
          *
FROM
          takaakiyayoi_catalog.japan_covid_analysis.covid_deaths;
```

SQLエディタでも確認します。メニューの**編集 > クエリーの書式を設定**を選択します。

![Screenshot 2025-05-14 at 9.48.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0747a98a-da82-4cfd-b2e0-718ca5f5a16a.png)

こちらも反映されました。

![Screenshot 2025-05-14 at 9.48.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b3e99249-868b-4ea3-8f49-c7c771c0e20e.png)

この他、キーワードや関数の大文字小文字、コンマの位置、改行などを制御することができます。こちらの[オプション]()をご覧ください。

ご活用ください！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

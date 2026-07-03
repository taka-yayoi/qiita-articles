---
title: Databricksのシステムテーブルによる消費金額の集計と可視化
tags:
  - Databricks
private: false
updated_at: '2024-04-26T09:17:34+09:00'
id: 1bac7d7cbbc4fe6a8815
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの記事を参考にさせていただきました。

https://www.linkedin.com/posts/activity-7189340209111592960-n688?utm_source=share&utm_medium=member_desktop

**課金利用 システム テーブル**と**価格設定システムテーブル**を使います。前者は日々のDatabricksの使用量(DBU)、後者はSKUごとの単価が格納されています。つまり、これらを掛け算することで費用が計算できます。

https://docs.databricks.com/ja/administration-guide/system-tables/billing.html

https://docs.databricks.com/ja/administration-guide/system-tables/pricing.html

:::note info
**注意**
- システムテーブルは[有効化の作業](https://docs.databricks.com/ja/administration-guide/system-tables/index.html#enable-system-table-schemas)が必要となります。
- 価格設定システムテーブルは**リスト価格**を格納しているので、ディスカウントが適用されている場合には別途ディスカウントを適用してください。
:::


クエリーはこのようになります。

```sql
SELECT
  u.usage_date,
  u.sku_name,
  SUM(u.usage_quantity * p.pricing.default) AS total_spent,
  p.currency_code
FROM
  system.billing.usage u
  LEFT JOIN system.billing.list_prices p ON u.sku_name = p.sku_name
  AND u.cloud = p.cloud
  AND u.usage_start_time < coalesce(p.price_end_time, date '2029-12-31')
  AND u.usage_end_time > p.price_start_time
WHERE u.usage_date >= date '2024-04-01' -- 4月のデータ
GROUP BY
  ALL
```
![Screenshot 2024-04-26 at 9.12.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d3c7fcb1-d431-4c22-f62c-03a73a04054b.png)

可視化すると使用状況が一目瞭然ですね。SKUは大分類にまとめるなどの処理を加えてもいいと思います。
![Screenshot 2024-04-26 at 9.12.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cbbd7b71-2e98-dbd5-9852-5d4d6bbcd34f.png)
![chart.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e679809e-4d50-f700-c297-871f8e28a343.png)

SQLでの分析なので[サーバレスウェアハウス](https://qiita.com/taka_yayoi/items/e167b2e1c485c83fc024)も活用できます。システムテーブルの分析方法に関してはこちらの記事も参照ください。

https://qiita.com/maroon-db/items/b89d47009948206ac064

https://qiita.com/maroon-db/items/e5c72de40f8b71900afe


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricksにおけるユーザーの最終ログイン日時を取得する
tags:
  - Databricks
private: false
updated_at: '2023-08-09T11:23:59+09:00'
id: 178d3afebad1c5a5f1b3
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
ユーザーの棚卸しをしたい場合に有益な情報が「ユーザーが最後にログインしたのはいつか」というものです。

これまでも監査ログで取得自体は可能だったのですが、いかんせん設定が大変。しかし、今回システムテーブルがサポートされたことで簡単にクエリーすることができるようになりました。

# システムテーブルの設定

こちらを参考に監査ログのシステムテーブルを有効化して下さい。

https://qiita.com/taka_yayoi/items/abaa48828cefe4f41e62

# クエリーの作成

Databricks SQLにアクセスして、以下のクエリーを実行します。

```sql:SQL
SELECT
  user_identity.email, -- JSONからメールアドレスを抽出
  MAX(event_time) AS last_login -- 最終ログイン日時
FROM
  system.access.audit
WHERE
  (
    action_name = "login" -- ワークスペースログイン
    OR action_name = "tokenLogin" -- パーソナルアクセストークンによるログイン
    OR action_name = "aadBrowserLogin" -- Azure ADトークンによるログイン
  )
GROUP BY
  user_identity
ORDER BY
  last_login DESC
```

![Screenshot 2023-07-31 at 9.49.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c28575ec-e515-e745-43a5-1c2ebe619977.png)

監査ログのスキーマや分析のサンプルはこちらにありますので、色々な観点で分析に活用してください！

https://docs.databricks.com/administration-guide/account-settings/audit-logs.html

https://docs.databricks.com/administration-guide/system-tables/audit-logs.html

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

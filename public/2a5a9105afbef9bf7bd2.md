---
title: 予算を設定してDatabricks使用量を監視できるようになりました
tags:
  - Databricks
private: false
updated_at: '2024-06-15T08:39:55+09:00'
id: 2a5a9105afbef9bf7bd2
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: 16baee61b1d8bd4aac5a
agreed_posting_campaign_term: true
---
こちらのアップデートです。

[Create budgets to monitor account spending (Public Preview)](https://docs.databricks.com/en/release-notes/product/2024/june.html#create-budgets-to-monitor-account-spending-public-preview)

> アカウント管理者はお使いのDatabricksアカウントでの消費を追跡するために、予算を作成できるようになりました。予算には、ワークスペースやカスタムタグに基づいた支出を追跡するためのカスタムフィルタを含めることができます。[予算を使用してアカウントの支出を監視する](https://docs.databricks.com/ja/admin/account-settings/budgets.html)をご覧ください。

これは嬉しいアップデート。早速ウォークスルーします。

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

[アカウント コンソール](https://accounts.cloud.databricks.com/)にアクセスして**使用料**に移動します。**予算**タブが表示されています。
![Screenshot 2024-06-10 at 17.29.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/94d5e6b4-c52c-1ff5-4b5a-082f69cef70c.png)

予算を設定するために**Add budget**をクリックします。
![Screenshot 2024-06-10 at 17.29.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fd5ad330-e379-974c-421e-bb34e50e643f.png)

名称、予算の金額(ドル)、必要に応じてワークスペースやカスタムタグを設定します。そして、予算超過時にメールを送信する際の宛先を指定します。空にした場合にはアラートメールは送信されます
![Screenshot 2024-06-10 at 17.29.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2f956405-e55d-be0d-a248-30f3b5c2c2d7.png)
![Screenshot 2024-06-10 at 17.30.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/608b711e-6f58-bcd7-ef18-693f3df035e6.png)
**作成**をクリックします。

これで設定が完了しました。
![Screenshot 2024-06-10 at 17.30.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/55d8e58c-601c-4b6c-1e35-17446b403341.png)

しばらくするとモニタリングが開始します。1ドルにしていたのですでに超過してました。
![Screenshot 2024-06-10 at 18.42.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c8366a10-3140-95f1-901a-0dcc12b5de66.png)

詳細を確認することができます。
![Screenshot 2024-06-10 at 18.42.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8bdbc3a0-2b89-f5e2-66ec-ba5fa48446c2.png)

アラートメールも送信されていました。
![Screenshot 2024-06-10 at 18.42.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/52970d5b-3763-0b67-72ac-eb3bee59c226.png)

是非ご活用ください！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

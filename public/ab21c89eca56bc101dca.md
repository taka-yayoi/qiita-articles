---
title: Databricksワークスペース検索機能の強化
tags:
  - Databricks
private: false
updated_at: '2022-05-20T12:46:50+09:00'
id: ab21c89eca56bc101dca
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
これまではノートブック名による検索しかできませんでしたが、今回のエンハンスでノートブックの中身に対しても検索ができるようになりました。

https://qiita.com/taka_yayoi/items/e469dded5ee83ae42d24#%E3%83%AF%E3%83%BC%E3%82%AF%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%81%AE%E3%82%AA%E3%83%96%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E3%81%AE%E6%A4%9C%E7%B4%A2

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

:::note info
**注意**
ここで説明する検索機能は、[暗号化に顧客管理キー](https://docs.databricks.com/security/keys/customer-managed-keys.html)を用いているワークスペースではサポートされていません。これらのワークスペースにおいては、サイドバーの**Search**をクリックし、![](https://docs.databricks.com/_images/search-icon.png)**Search Workspace**フィールドに検索文字列をタイプします。タイプするたびに、名前に検索文字列を含むオブジェクトが一覧されます。ワークスペースでオブジェクトを開くには名前をクリックします。
:::


1. サイドメニューの**検索**をクリックします。
![Screen Shot 2022-05-20 at 12.42.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8a1dc2c8-1348-8111-646e-f5e69ab927f0.png)

1. 検索ダイアログが表示されます。
![Screen Shot 2022-05-20 at 12.43.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c0604193-58bf-c0c8-cb78-6262ce7a6d42.png)

1. 検索キーワードを入力しEnterを押すと、検索結果が表示されます。名称をクリックすることでオープンすることができます。
![Screen Shot 2022-05-20 at 12.43.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a63b7031-6dab-4d6a-af98-e18f33f80959.png)

1. ドロップダウンから種別(Type)を選択することで絞り込みを行うことができます。
![Screen Shot 2022-05-20 at 12.45.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e79364b4-b659-0744-ea93-434b9221dcc8.png)



### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

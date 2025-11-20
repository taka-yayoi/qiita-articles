---
title: Azure Databricks japaneastリージョンにMosaic AI Model Servingがやってきました！
tags:
  - Databricks
  - AzureDatabricks
  - MosaicAI
private: false
updated_at: '2025-03-01T09:48:18+09:00'
id: fbef5cad909ab86b691f
organization_url_name: databricks
slide: false
ignorePublish: false
---
どれほど待ったことか。ついに東日本リージョンのAzure Databricksに[Mosaic AI Model Serving](https://learn.microsoft.com/ja-jp/azure/databricks/machine-learning/model-serving/)がやってきました。DatabricksでLLMを活用する際には必須と言える機能です。

https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2025/february#mosaic-ai-model-serving-is-now-available-in-azure-japan-east-uk-south-and-south-central-us

![Screenshot 2025-03-01 at 9.40.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9443465b-5dff-4d0a-9133-a4cabc54bbe3.png)

早速試します。**サービング**にアクセスすると基盤モデルも表示されています。今回のリリースに伴い、[Databricks Foundation Model API](https://learn.microsoft.com/ja-jp/azure/databricks/machine-learning/foundation-model-apis/)も利用できるようになっています。

![Screenshot 2025-03-01 at 9.30.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bca89d59-674b-4f2e-9a36-dc62f28c77fd.png)

[AI Playground](https://learn.microsoft.com/ja-jp/azure/databricks/large-language-models/ai-playground)からも基盤モデルを利用できます。

![Screenshot 2025-03-01 at 9.31.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b3df4848-0acb-4dcc-b149-1619e07bb9e9.png)
![Screenshot 2025-03-01 at 9.32.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/94c5f4fc-c295-4d5f-ba46-30c409503d65.png)

![Screenshot 2025-03-01 at 9.31.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1f0a9521-01bc-4d55-ad6a-7865021a6b9f.png)

サービングエンドポイントを作ってみます。

![Screenshot 2025-03-01 at 9.33.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a93389ec-a400-41dd-8a6c-95b1ca7a802c.png)

起動しました！これで、REST APIで生成AIモデルを呼び出せます。

![Screenshot 2025-03-01 at 9.36.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/747d3340-9d23-4868-b1fd-67cd09a80631.png)

[ai_query関数](https://learn.microsoft.com/ja-jp/azure/databricks/sql/language-manual/functions/ai_query)で呼び出します。

```sql
SELECT ai_query("taka-llama-3-2-1b", "Databricksについて日本語で教えてください")
```

動きました！

![Screenshot 2025-03-01 at 9.38.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/feaecdce-c8e9-44ff-89d6-dfeba77ceafc.png)

長らくお待たせしました。生成AIアプリの開発や[バッチ推論](https://learn.microsoft.com/ja-jp/azure/databricks/large-language-models/ai-query-batch-inference)などにご活用ください。Mosaic AI Model Servingの全体像を説明しているマニュアルはこちらです。

https://learn.microsoft.com/ja-jp/azure/databricks/machine-learning/model-serving/

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

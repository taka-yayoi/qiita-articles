---
title: ' Databricks生成AIクックブック - 4. RAGの品質の評価'
tags:
  - Databricks
  - rag
  - 生成AI
  - Databricks生成AIクックブック
private: false
updated_at: '2024-06-26T13:55:58+09:00'
id: c7e549323b9fcbb9edec
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: 12da67d1f5723af75e60
agreed_posting_campaign_term: true
---
[4\. Evaluating RAG quality — Databricks Generative AI Cookbook](https://ai-cookbook.io/nbs/4-evaluation.html) [2024/6/23時点]の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

> [Databricks生成AIクックブック](https://qiita.com/taka_yayoi/items/36c51bce8f33a70cf204)のコンテンツです。


# 4. RAGの品質の評価

古い諺"計測できないことは管理できない"は、RAGを含む全ての生成AIアプリケーションの文脈においても信じられないくらい当てはまります。あなたの生成AIアプリケーションが高品質で正確なレスポンスを提供するためには、あなたのユースケースにおいて"品質"が何であるのかを定義し、計測できるように**ならなくてはいけません**。

このセクションでは、評価における3つの重要なコンポーネントにディープダイブします:

[4\.1\. "品質"の定義: 評価セット](https://qiita.com/taka_yayoi/items/8f4c2777a1151e1d7b6a)
[4\.2\. パフォーマンスの評価: メトリクスが重要です](https://qiita.com/taka_yayoi/items/05f650df667ffca3e92d)
[4\.3\. 計測の実現: サポートするインフラストラクチャ](https://qiita.com/taka_yayoi/items/e8c2b711a2ebe5bd1d1d)

<br>

- [目次](https://qiita.com/taka_yayoi/items/36c51bce8f33a70cf204#%E7%9B%AE%E6%AC%A1)
- 前のセクション: [3.2. 収集、拡張、生成(RAGチェーン)](https://qiita.com/taka_yayoi/items/7097a738ea8e014d86f2)
- 次のセクション: [4\.1\. "品質"の定義: 評価セット](https://qiita.com/taka_yayoi/items/8f4c2777a1151e1d7b6a)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

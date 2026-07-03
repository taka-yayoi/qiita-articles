---
title: Databricksジョブにおけるループ処理アプローチの比較
tags:
  - Databricks
private: false
updated_at: '2025-03-03T11:50:24+09:00'
id: b71aeda7930beb576ccd
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---

# For eachタスク

結構最近のジョブの機能に`For each`(それぞれ)タスクというものがあります。名前の通り、特定のタスクのそれぞれを処理するループを組むことができる機能です。

https://docs.databricks.com/aws/ja/jobs/for-each

こちらでウォークスルーしています。ループしたいパラメータをリストで定義すれば、ロジックを実装したノートブックに対するループ処理を簡単に実装することができます。

https://qiita.com/taka_yayoi/items/602bcd2a8d39fa2f555d

![capture.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/976c2424-486b-c4d4-3e4e-7f385cbec822.gif)

# SDKを用いた並列タスク

しかし、`for each`タスクの登場前でも(ある意味力技で)ジョブでループ処理を実装することができていました。タスクは直列、並列に組み合わせることができるので、異なるパラメータを受け取るノートブックを並列に配置されたタスクに設定すれば、ループ処理を行うことができます。ただし、多数のタスクを手動で設定するのは手間なので、SDKを用いてプログラムからタスクを設定することをお勧めします。

https://qiita.com/taka_yayoi/items/79e83aa1124226504892

![Screenshot 2023-12-10 at 15.04.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1574ac9f-adbd-f5cd-deb3-a43dbdf65850.png)

# アプローチの比較

これら二つのアプローチには一長一短がありますので、要件に基づいて選択いただくことをお勧めします。

|  | for eachタスク | 並列タスク |
|:--|:--|:--|
|  計算リソース | ループのそれぞれのイテレーションが割り当てられたリソースを共有します。[同時実行性](https://docs.databricks.com/aws/ja/jobs/for-each#for-each%E3%82%BF%E3%82%B9%E3%82%AF%E3%82%92%E3%82%B8%E3%83%A7%E3%83%96%E3%81%AB%E8%BF%BD%E5%8A%A0%E3%81%99%E3%82%8B)を上げるとリソースの競合が起きるので注意ください。  | タスクごとにリソースを再利用、あるいは別のリソースを割り当てることができます。  |
| 失敗タスクの再実行  | 特定のイテレーションを再実行する機能がないので、自前で修復処理を実装する必要があります。  | [ジョブの修復](https://docs.databricks.com/aws/ja/jobs/repair-job-failures#%E5%A4%B1%E6%95%97%E3%81%97%E3%81%9F%E3%82%BF%E3%82%B9%E3%82%AF%E3%81%A8%E3%82%B9%E3%82%AD%E3%83%83%E3%83%97%E3%81%95%E3%82%8C%E3%81%9F%E3%82%BF%E3%82%B9%E3%82%AF%E3%81%AE%E5%86%8D%E5%AE%9F%E8%A1%8C)で可能です。  |
|タスクの作成   | 引数のリストを作成するだけで簡単にループ処理を実装できます。  |  タスクに分けてループを実装する際、個別のタスクを多数作る必要があります。[SDK](https://docs.databricks.com/aws/ja/dev-tools/sdk-python)を用いてプログラム的に作成することをお勧めします。 |

簡単かつリトライの必要性のないワークロードであれば`for each`タスクがお勧めですが、リトライ処理やリソース最適化が必要であれば、タスクを組み合わせてループ処理を組んだほうが良いかと思います。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

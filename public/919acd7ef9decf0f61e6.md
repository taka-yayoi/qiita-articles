---
title: DatabricksのPools
tags:
  - Databricks
private: false
updated_at: '2021-04-20T09:22:32+09:00'
id: 919acd7ef9decf0f61e6
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Pools \| Databricks on AWS](https://docs.databricks.com/clusters/instance-pools/index.html) [2021/4/15時点]の翻訳です。

Databricksのpoolsは、アイドル状態で利用可能なインスタンスのセットを維持しておくことで、クラスターの起動時間、オートスケーリングに要する時間を短縮します。[プールにアタッチされた](https://docs.databricks.com/clusters/instance-pools/cluster-instance-pool.html#cluster-instance-pool)クラスターがインスタンスを必要とした場合、まず、プールにあるアイドルなインスタンスの一つを割り当てようとします。プールにアイドルなインスタンスが存在しない場合、クラスターからの要求に応えるためにプールは新たなインスタンスをインスタンスプロバイダーから獲得します。クラスターがインスタンスを解放した際には、プールに返却され、他のクラスターから利用できます。

プールの紹介と推奨設定に関しては、以下の動画を参照ください。
<iframe width="560" height="315" src="https://www.youtube.com/embed/FVtITxOabxg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

アイドル状態のインスタンスがプールに存在している間は、Databricksの課金は発生しません。インスタンスプロバイダーの課金は発生します。[課金体形](https://aws.amazon.com/ec2/pricing/)を参照ください。

UI、CLI、Pools APIでプールを管理することができます。本章ではどのようにUIでプールを管理するのかを説明します。他の手段に関しては、[Instance Pools CLI](https://docs.databricks.com/dev-tools/cli/instance-pools-cli.html)、[Instance Pools API](https://docs.databricks.com/dev-tools/api/latest/instance-pools.html)を参照ください。

本章では以下を説明します。

- [Display pools(英語)](https://docs.databricks.com/clusters/instance-pools/display.html)
- [Create a pool(英語)](https://docs.databricks.com/clusters/instance-pools/create.html)
- [Configure pools(英語)](https://docs.databricks.com/clusters/instance-pools/configure.html)
- [Edit a pool(英語)](https://docs.databricks.com/clusters/instance-pools/edit.html)
- [Delete a pool(英語)](https://docs.databricks.com/clusters/instance-pools/delete.html)
- [Use a pool(英語)](https://docs.databricks.com/clusters/instance-pools/cluster-instance-pool.html)
- [Best practices: Pools(英語)](https://docs.databricks.com/clusters/instance-pools/pool-best-practices.html)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

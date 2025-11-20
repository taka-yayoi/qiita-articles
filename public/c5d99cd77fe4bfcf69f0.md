---
title: Databricksクラスター
tags:
  - Databricks
  - Databricksクイックスタートガイド
private: false
updated_at: '2022-02-09T11:59:05+09:00'
id: c5d99cd77fe4bfcf69f0
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Clusters \| Databricks on AWS](https://docs.databricks.com/clusters/index.html) [2022/1/21時点]の翻訳です。

> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Databricksクラスターは、プロダクションのETLパイプライン、ストリーミング分析、アドホック分析、機械学習のようなデータエンジニアリング、データサイエンス、データ分析ワークロードを実行するための計算リソース、設定のセットです。

ノートブックの一連のコマンドや自動化されたジョブとしてこれらのワークロードを実行します。Databricksは*all-purposeクラスター*と*jobクラスター*を区別します。インタラクティブなノートブックを用いて、コラボレーションをつうて自データ分析を行う際にはall-purposeクラスターを使用します。高速かつ堅牢な自動化ジョブを実行するためにjobクラスターを使用します。

- UI、CLI、REST APIを用いて*all-purpose*クラスターを作成することができます。手動でall-purposeクラスターを停止、再起動することができます。複数のユーザーが、コラボレーティブかつインタラクティブな分析を行うためにこれらのクラスターを使用することができます。
- *新規jobクラスター*でジョブを実行する際、Databricksのジョブスケジューラーが*jobクラスター*を作成し、ジョブが完了するとクラスターを停止します。*jobクラスターを再起動することはできません。*

このセクションでは、UIを用いてクラスターをどのように操作するのかを説明します。他の方法については、[Clusters CLI](https://docs.databricks.com/dev-tools/cli/clusters-cli.html)、[Clusters API 2\.0](https://docs.databricks.com/dev-tools/api/latest/clusters.html)を参照ください。

このセクションでは、jobクラスターよりもall-purposeクラスターにフォーカスしますが、説明する設定、管理ツールの多くは両方のクラスタータイプに適用されます。jobクラスターの作成方法の詳細については、[ジョブ](https://qiita.com/taka_yayoi/items/b3275a1983c51a8bbe1a)を参照ください。

> **重要！**
Databricksは、過去30日以内に停止された最大70台のall-purposeクラスターの設定情報を維持し、ジョブスケジューラーによって停止された最大30台のjobクラスターの情報を保持します。[停止](https://qiita.com/taka_yayoi/items/991aae376c089df58504#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AE%E5%81%9C%E6%AD%A2)後30日を経過してもall-purposeクラスターの設定を維持したい場合には、管理者はクラスターリストにクラスターを[ピン留め](https://qiita.com/taka_yayoi/items/991aae376c089df58504#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AE%E3%83%94%E3%83%B3%E7%95%99%E3%82%81)することができます。

- [Cluster basics](https://docs.databricks.com/clusters/basics.html)
- [Databricksにおけるクラスター作成](https://qiita.com/taka_yayoi/items/d36a469a1e0c0cebaf1b)
- [Databricksにおけるクラスター管理](https://qiita.com/taka_yayoi/items/991aae376c089df58504)
- [Databricksクラスターの設定](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18)
- [Databricksクラスター設定のベストプラクティス](https://qiita.com/taka_yayoi/items/ef3dc37143e7b77b50ad)
- [Task preemption](https://docs.databricks.com/clusters/preemption.html)
- [Customize containers with Databricks Container Services](https://docs.databricks.com/clusters/custom-containers.html)
- [Cluster node initialization scripts](https://docs.databricks.com/clusters/init-scripts.html)
- [GPU\-enabled clusters](https://docs.databricks.com/clusters/gpu.html)
- [Databricksのシングルノードクラスター](https://qiita.com/taka_yayoi/items/6e7c6cc14a5017ef6d15)
- [DatabricksのPools](https://qiita.com/taka_yayoi/items/919acd7ef9decf0f61e6)
- [Web terminal](https://docs.databricks.com/clusters/web-terminal.html)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

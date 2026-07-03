---
title: DatabricksのクラスターとSQLウェアハウスの違い
tags:
  - Databricks
private: false
updated_at: '2022-12-21T09:15:39+09:00'
id: 6cdaf5ec56fd86ec6fd0
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Databricks Cluster vs SQL Warehouses \| by Ganesh Chandrasekaran \| Oct, 2022 \| Medium](https://ganeshchandrasekaran.com/databricks-cluster-vs-sql-warehouses-c0c159287dd7)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Databricksのプレミアムアカウントを使用しているのであれば、Data EngineeringとMachine Learningに加えてSQLペルソナを目にかけることでしょう。
![](https://miro.medium.com/max/1400/1*p8xU-cp_kKOAJEU9EWZwOA.webp)
*Databricks SQLペルソナ*

Data EngineeringやMachine Learningを使っているのであれば、(インタラクティブあるいはジョブ)クラスターを起動しますが、SQLペルソナを使っている場合には、標準のDatabricksクラスターではなくSQLウェアハウス(以前のSQLエンドポイント)であることに気づくことでしょう。

本書では、DatabricksクラスターとSQLウェアハウスの違いをクイックにまとめます。
![](https://miro.medium.com/max/1400/1*dfWNc9vPd2paeezUfGbCbA.webp)
*Databricks - SQLウェアハウスの作成*

- SQLウェアハウス(エンドポイント)はSQLコマンドを実行するために開発されており、Scala/R/PythonやSQLコマンドを実行するために開発されています。
- SQLウェアハウス(エンドポイント)ではJAR、PIP、WHLのようなライブラリのオーバヘッドがなく、クラスターではライブラリによるオーバヘッドが生じることがあります。
- SQLウェアハウス(エンドポイント)はSQLウェアハウスの管理を簡素化しており、起動時間を加速します。クラスターの設定は初めての方にとっては複雑なものになる場合があります。
- SQLウェアハウス(エンドポイント)はクラスターとしてスケールアップ/スケールダウンします。クラスターはノードごとにスケーリングし、最大範囲までスケールアップします。
- SQLウェアハウス(エンドポイント)には、起動時間を劇的に削減するサーバレスの機能(プライベートプレビュー)がありますが、クラスターではその機能はまだありません。

次の項目は違いではなく、両方で利用できる機能です。

SQLウェアハウス(エンドポイント)とクラスターの両方はTableauのようなBIツールからの接続に使用でき、自動起動の機能を有しています。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

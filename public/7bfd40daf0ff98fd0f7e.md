---
title: Databricks Power BIコネクタのリリース(GA)
tags:
  - PowerBI
  - Databricks
private: false
updated_at: '2021-03-15T08:55:48+09:00'
id: 7bfd40daf0ff98fd0f7e
organization_url_name: databricks
slide: false
ignorePublish: false
---
[General Availability \(GA\) of Power BI Connector for Databricks \- The Databricks Blog](https://databricks.com/blog/2021/02/26/announcing-general-availability-ga-of-the-power-bi-connector-for-databricks.html)の翻訳です。

Power BIサービスとPower BI Desktop 2.85.681.0に対応した、[Microsoft Power BI connector for Databricks](https://azure.microsoft.com/en-us/updates/power-bi-connector-for-azure-databricks-is-now-generally-available/)が正式提供(GA)できることに、我々は大変興奮しています。[パブリックプレビュー](https://databricks.com/blog/2020/10/30/announcing-azure-databricks-power-bi-connector-public-preview.html)を通じて、既に我々は多くのお客様が導入したのを知り、全てのお客様に本機能を提供することにしました。最近公開したSQL Analyticsサービスと共に提供されるネイティブのDatabricks Power BIコネクターは、Databricksの利用者がDelta Lakeに直接アクセスしてBIを実施できるファーストクラスの経験を提供します。SQL Analyticsを用いることで、データウェアハウスの性能に加え、従来のデータウェアハウスと比較して4倍のコストパフォーマンスを持つデータレイクの経済性を兼ね備えたマルチクラウドのレイクハウスアーキテクチャを操作することが可能となります。
![](https://databricks.com/wp-content/uploads/2021/02/power-bi-connector-hires.png)

Databricks Power BIコネクタは以下の機能を通じて、シームレスな接続性を提供します：

**Azure Active Directory(Azure AD)及びシングルサインオンのサポート：**Azure Databricksに対してAzure ADの認証情報を用いた接続が可能となります。管理者は認証のために[パーソナルアクセストークン(PAT)](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/authentication)を発行する必要はありません。

**シンプルな接続設定：**Databricksコネクタは、最初からPower BIに統合されています。数クリックでDatabricksへの接続設定が完了します。データソースとしてDatabricksを選択し、Databricks特有の接続情報及び認証情報を入力するだけです。すぐにクエリを発行することができます！

**DirectQueryを介したAzure Data Lake Storageへのセキュアかつダイレクトなアクセス：**Power BI DirectQueryを用いることで、Databricksのデータに直接アクセスでき、ユーザーは大規模なデータセットを検索したり可視化することができます。DirectQueryの結果は常に最新であり、Delta Lakeのデータセキュリティ保護機能が適用されます。

**Databricks ODBCを通じた高速な結果取得：**Databricks ODBCドライバーはクエリの遅延を削減し、結果転送速度及びメタデータ取得性能が改善されています。

# Power BIコネクタを利用してみてください

強化されたDatabricks Power BIコネクタは、DatabricksとMicrosoftの継続的なコラボレーションの結果です。[Quickstart Lab](https://dbricks.co/QuickstartLabs)に参加してDatabricksのハンズオンを経験し、Power BIコネクタを通じてDatabrikcsに接続してみてください。

---
title: Databricksにおけるデータウェアハウスとは？
tags:
  - Databricks
  - DatabricksSQL
private: false
updated_at: '2023-03-06T16:59:15+09:00'
id: d7255aab7bb6abec22ed
organization_url_name: databricks
slide: false
ignorePublish: false
---
[What is data warehousing on Databricks? \| Databricks on AWS](https://docs.databricks.com/sql/index.html) [2023/3/3時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Databricks[レイクハウスプラットフォーム](https://qiita.com/taka_yayoi/items/883b29d4808874427464)は、完全なエンドツーエンドのデータウェアハウスソリューションを提供します。Databricksレイクハウスプラットフォームはオープンな標準とAPI上に構築されています。Databricksレイクハウスは、エンタープライズデータウェアハウスのACIDトランザクションとデータガバナンスと、データレイクの柔軟性とコスト効率性を組み合わせます。Databricks SQLとは、Databricks[レイクハウスプラットフォーム](https://qiita.com/taka_yayoi/items/883b29d4808874427464)に組み込まれている、ビジネスアナリティクスのための一般的な計算資源を提供するエンタープライズデータウェアハウスのことを指します。Databricks SQLが提供するコア機能は[SQLウェアハウス](https://docs.databricks.com/sql/admin/sql-endpoints.html)となります。

# Databricksにおけるデータモデリングとは？

Databricksは、データベースのスキーマ、テーブル、ビューのような馴染みのあるリレーションを用いて、クラウドオブジェクトストレージに各王されているDelta Lakeのデータを整理します。Databricksでは、分析データの検証、クレンジング、変換にマルチレイヤーのアプローチを取ることを推奨しています。詳細は、[メダリオンアーキテクチャ](https://qiita.com/taka_yayoi/items/f3d9028cf533e2c78b9d)をご覧ください。

# Databricks SQLとは？

Databricks SQLは、レイクハウスのテーブルに対するSQL[クエリー](https://docs.databricks.com/sql/user/queries/index.html)、[ビジュアライゼーション](https://docs.databricks.com/sql/user/visualizations/index.html)、[ダッシュボード](https://qiita.com/taka_yayoi/items/834bef9aa784e1a045d8)のための一般的な計算資源を提供します。Databricks SQLでは、これらのクエリー、ビジュアライゼーション、ダッシュボードは[SQLエディタ](https://docs.databricks.com/sql/user/sql-editor/index.html)を用いて開発、実行されます。

# SQLエディタとは？

スキーマを探索し、馴染み深いSQL構文を用いてクエリーを記述、共有、再利用するためにビルトインの[SQLエディタ](https://docs.databricks.com/sql/user/sql-editor/index.html)を活用します。定常的に使用されるSQLコードは、クイックに再利用するためにスニペットとして保存でき、実行時間を短縮するためにクエリーの結果はキャッシュされます。さらに、自動更新やデータに意味のある変化が生じた際にアラートを発呼するために、クエリーの更新をスケジュールすることができます。また、Databricks SQLによって、アナリストはクイックにアドホックな探索分析を行うために、ビジュアライゼーションやドラッグ&ドロップのダッシュボードを通じて、データから意味を抽出できるようになります。

# 利用可能なウェアハウスタイプは？

Databricks SQLは、異なるレベルのパフォーマンスと機能サポートを持つ3つのウェアハウスのタイプをサポートしています。

:::note
**注意**
それぞれのウェアハウスタイプの価格と詳細な機能比較については、[Databricks SQL](https://www.databricks.com/jp/product/pricing/databricks-sql)をご覧ください。最新のDatabricks SQLの機能については、[Databricks SQL release notes](https://docs.databricks.com/sql/release-notes/index.html)をご覧ください。
:::

- **サーバレス:** pro SQLウェアハウスタイプのすべての機能、高度なDatabricks SQLパフォーマンス機能をサポートしています。サーバレスSQLウェアハウスタイプはデフォルトでは有効化されていません。サーバレスSQLウェアハウスタイプを有効化するには、[Databricks SQL release notes](https://docs.databricks.com/sql/release-notes/index.html)をご覧ください。
- **Pro:** (Classicと比較して)高パフォーマンスなDatabricks SQLの追加機能をサポートしており、すべてのDatabricks SQLの機能をサポートしています。pro SQLウェアハウスタイプはデフォルトで有効化されています。
- **Classic:** エントリーレベルのパフォーマンス機能をサポートしており、限定的なDatabricks SQLの機能をサポートしています。Classic SQLウェアハウスタイプはデフォルトでは有効化されていません。

# ウェアハウスタイプのデフォルトは？

- **サーバレスが有効化されている:** UIあるいはAPIを用いてワークスペースでSQLウェアハウスを作成する際、サーバレスが有効化されていれば、デフォルトのSQLウェアハウスタイプはサーバレスとなります。
- **サーバレスが有効化されておらずUIを使用している:** UIを用いてワークスペースでSQLウェアハウスを作成する際、サーバレスが有効化されていない場合には、デフォルトのSQLウェアハウスタイプはproとなります。
- **サーバレスが有効化されておらずAPIを使用している:** APIを用いてワークスペースでSQLウェアハウスを作成する際、サーバレスが有効化されていない場合には、デフォルトのSQLウェアハウスタイプはclassicとなります。

:::note
**注意**
APIを使用する際、SQLウェアハウスタイプを指定しなくてはなりません。
:::

# Databricks SQLとサードパーティBIツール

また、Databricks SQLは、Databricksにおけるデータウェアハウスソリューションとして数多くのサードパーティ[BI、ビジュアライゼーションツール](https://docs.databricks.com/partners/partners.html#bi)をサポートしています。[DatabricksとPowerBI](https://qiita.com/taka_yayoi/items/fd0d5e4de3c7f50de617#power-bi)や[DatabricksとTableau](https://qiita.com/taka_yayoi/items/fd0d5e4de3c7f50de617#tableau%E3%82%AA%E3%83%B3%E3%83%A9%E3%82%A4%E3%83%B3)もご覧ください。

# Databricks SQL API

Databricks SQLは皆様のプロブラミング要件のための堅牢な[API](https://docs.databricks.com/sql/api/index.html)も提供しています。

# Databricks SQLの管理タスク

Databricks SQLの有効化、SQLウェアハウスの作成、管理、ユーザーやデータアクセスの管理、その他の管理タスクについては、[Databricks SQL administration](https://docs.databricks.com/sql/admin/index.html)をご覧下さい。

# 開発ツール

DatabricksでSQLコマンドやスクリプトを実行し、Databricksのデータベースオブジェクトをブラウズするために、様々な開発ツールを活用することができます。[Use a SQL database tool](https://docs.databricks.com/dev-tools/index-sql.html)をご覧ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

---
title: DatabricksにおけるINVALID_PARAMETER_VALUE.LOCATION_OVERLAPエラー
tags:
  - Databricks
  - UnityCatalog
private: false
updated_at: '2024-12-12T17:24:18+09:00'
id: 1fd38f0fa0b0bafef846
organization_url_name: databricks
slide: false
ignorePublish: false
---
[INVALID\_PARAMETER\_VALUE\.LOCATION\_OVERLAP: overlaps with managed storage error \- Databricks](https://kb.databricks.com/en_US/unity-catalog/invalid_parameter_valuelocation_overlap-overlaps-with-managed-storage-error)の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

外部テーブルは、カタログやスキーマのストレージロケーションと重複させることはできません。そうではなく、サブディレクトリに作成すべきです。

# 問題

共有クラスターで、マネージドテーブルにマウントされた**外部ロケーション**([AWS](https://docs.databricks.com/ja/data-governance/unity-catalog/manage-external-locations-and-credentials.html) | [Azure](https://learn.microsoft.com/ja-jp/azure/databricks/data-governance/unity-catalog/manage-external-locations-and-credentials) | [GCP](https://docs.gcp.databricks.com/jp/data-governance/unity-catalog/manage-external-locations-and-credentials.html))にアクセスするために`dbutils`を使用しています。そのロケーションのパスを一覧しようとした場合、`INVALID_PARAMETER_VALUE.LOCATION_OVERLAP`エラーメッセージで失敗します。

エラーは、指定されたパスがマネージドストレージと重複していると言っています。

```py
dbutils.fs.ls("<storage-blob>://path/")
```
> AnalysisException: [RequestId=96dd6185-e0dc-4fe0-94ad-bd8ab05fbd8e ErrorClass=INVALID_PARAMETER_VALUE.LOCATION_OVERLAP] Input path url '<storage-blob>://path' overlaps with managed storage

# 原因

マネージドディレクトリに対するリストコマンドの実行はUnity Catalogではサポートされていません。カタログやスキーマのロケーションはマネージドストレージとして予約されています。

# ソリューション

外部テーブルはカタログやスキーマのストレージロケーションと重複させることはできませんが、ルートロケーションのサブディレクトリ配下に作成することはできます。カタログやスキーマで使用されるルートロケーションやその上位ディレクトリに外部テーブルを作ってはいけません。

例えば、ルートロケーションが`<storage-blob>://<some-root>`だとします。対応するカタログやスキーマのロケーションは、`<storage-blob>://<some-root>/__unitystorage/catalogs/<catalog-id>`となるマネージドストレージロケーションと同じものになります。

マネージドテーブルと重複しない限り、`some-root/`配下に外部ロケーションを作成することができます。この例では、`<storage-blob>://<some-root>/<some-path>/<external-table-path>`は外部ロケーションとして適切なパスとなります。

この例のロケーションのコンテンツを一覧しようとした場合には、実行は成功します。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

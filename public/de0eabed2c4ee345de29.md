---
title: Databricksシークレットの検閲
tags:
  - Databricks
  - Databricksシークレット
private: false
updated_at: '2021-05-06T09:09:15+09:00'
id: de0eabed2c4ee345de29
organization_url_name: databricks
slide: false
ignorePublish: false
---
> [Databricksにおけるシークレットの管理](https://qiita.com/taka_yayoi/items/338ef0c5394fe4eb87c0)のコンテンツです。

[Secret redaction \| Databricks on AWS](https://docs.databricks.com/security/secrets/redaction.html) [2021/4/12時点]の翻訳です。

Databricksシークレットに認証情報を格納することで、ノートブックやジョブを実行する際に認証情報を容易に保護できます。しかし、変数を指定する際に誤って標準出力を画面に表示してしまうということは起こり得ることです。

これを避けるために、Databricksは`dbutils.secrets.get()`を使用して読み込まれた変数の値を検閲します。ノートブックセルの出力を表示する際、シークレットの値は`[REDACTED]`に置換されます。

> **警告!**
セルのアウトプットに対するシークレットの検閲は、リテラル値に対してのみ適用されます。このため、シークレットのリテラル値を変換した値に対しては検閲は動作しません。シークレットを適切に管理するためには、共有ノートブックへの許可しないアクセスを防ぐために[Workspace object access control](https://docs.databricks.com/security/access-control/workspace-acl.html)(コマンド実行権限を制限)を使用すべきです。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

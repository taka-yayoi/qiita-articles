---
title: Databricksにおけるモデルサービングの推論テーブルの有効化
tags:
  - Databricks
private: false
updated_at: '2023-10-01T08:16:06+09:00'
id: bce5df57ae5d90bdf971
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Enable inference tables on model serving endpoints \| Databricks on AWS](https://docs.databricks.com/en/machine-learning/model-serving/enable-model-serving-inference-tables.html) [2023/9/27時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

本書では、ご自身のモデルデプロイメントを監視、デバッグできるように、[モデルサービングエンドポイント](https://docs.databricks.com/ja/machine-learning/model-serving/index.html)の推論テーブルの有効化の方法を説明します。

推論テーブルは、モデルサービングエンドポイントの作成時あるいは、既存のエンドポイントの更新の際に、Databricksの機械学習サービングUI、あるいはDatabricks機械学習モデルサービングAPIで有効化することができます。エンドポイントを作成したユーザーがワークスペースから削除された際に、推論テーブルが影響を受けないように、サービスプリンシパルを用いてエンドポイントを作成することをお勧めします。

推論テーブルの有効化後は、エンドポイントの作成者がテーブルの所有者になります。テーブルに対するすべてのアクセスコントロールリスト(ACL)は、標準的なUnity Catalogの権限に従い、テーブル所有者によって変更することができます。

[Databricksにおけるモデルサービングエンドポイントの推論テーブル](https://qiita.com/taka_yayoi/items/b6a10ce0ff0d709d2349)をご覧ください。

# 要件

- この機能はパブリックプレビューでのみ利用できます。パブリックプレビューに参加するには、Databricks担当者に連絡するか、[inference tables preview enrollment form](https://docs.google.com/forms/d/14MGQZxxeLRI7ycmWcU5H1mx6o3AyW7cgucLlfnvha2s/edit)を提出してください。
- ワークスペースでUnity Catalogが有効化されている必要があります。
- エンドポイントで推論テーブルを有効化するには、エンドポイントの作成者あるいは変更者は以下の権限が必要です:
    - エンドポイントに対する`CAN_MANAGE`権限
    - 指定したカタログに対する`USE CATALOG`権限
    - 指定したスキーマに対する`USE SCHEMA`権限
    - スキーマにおける`CREATE TABLE`権限

# UIを用いた推論テーブルの有効化

Databricks機械学習サービングエンドポイントのUIから推論テーブルを有効化することができます。

エンドポイント作成時に推論テーブルを有効化するには、以下のステップを踏みます:

1. Databricks機械学習UIで**Serving**をクリックします。
1. **Create serving endpoint**をクリックします。
1. エンドポイント作成ページで、**Enable inference table**を選択します。
1. テーブルを格納したいカタログとスキーマを選択します。
1. オプションとして、最終的なテーブル名のテーブルプレフィクスを指定します。テーブルプレフィクスが指定されない場合、エンドポイント名が使用されます。
1. エンドポイントの設定を行った後に**Create serving endpoint**をクリックします。エンドポイントページ二委同士、右上に新たに設定された推論テーブルのパスが表示されます。

既存のエンドポイントで推論テーブルを有効化することができます。既存のエンドポイントの設定を変更するには、以下のステップを実施します:

1. エンドポイントページに移動します。
1. **Edit configuration**をクリックします。
1. **Enable inference table**を選択します。
1. テーブルを格納したいカタログとスキーマを選択します。
1. オプションとして、最終的なテーブル名のテーブルプレフィクスを指定します。テーブルプレフィクスが指定されない場合、エンドポイント名が使用されます。
1. エンドポイントの設定を行った後に**Update serving endpoint**をクリックします。

# client_request_idの指定

`client_request_id`フィールドは、ユーザーがモデルサービングのリクエストボティに指定できるオプションの値です。これによって、推論テーブルの`client_request_id`に値を埋め込むことができ、正解ラベルなど`client_request_id`を持つ他のテーブルとリクエストのデータを結合するために活用することができます。`client_request_id`を指定するには、リクエストのペイロードのトップレベルのキーとして`client_request_id`を指定します。`client_request_id`が指定されない場合、リクエストに対応する行では値はnullとして表示されます。

```json:JSON
{
  "client_request_id": "<user-provided-id>",
  "dataframe_records": [
    {
      "sepal length (cm)": 5.1,
      "sepal width (cm)": 3.5,
      "petal length (cm)": 1.4,
      "petal width (cm)": 0.2
    },
    {
      "sepal length (cm)": 4.9,
      "sepal width (cm)": 3,
      "petal length (cm)": 1.4,
      "petal width (cm)": 0.2
    },
    {
      "sepal length (cm)": 4.7,
      "sepal width (cm)": 3.2,
      "petal length (cm)": 1.3,
      "petal width (cm)": 0.2
    }
  ]
}
```

`client_request_id`に関連づけられたラベルを持つ他のテーブルがあるのであれば、正解ラベルとの結合で`client_request_id`を活用することができます。

# 推論テーブルでログをチェック

サービングするモデルの準備ができると、あなたのモデルに対するすべてのリクエストは自動で推論テーブルに記録されます。データカタログを開いてエンドポイントにクエリーを行うために、UI上の推論テーブルの下にあるリンクを選択することで、推論テーブルに書き込まれたログを参照することができます。あるいは、エンドポイント呼び出しURLをコールし、APIを用いて自動生成されたUnity Catalogのテーブルにクエリーすることでログを参照することができます。[サービスを提供しているエンドポイントにスコアリングリクエストを送信する](https://docs.databricks.com/ja/machine-learning/model-serving/score-model-serving-endpoints.html)をご覧ください。

エンドポイントを呼び出すと、スコアリングのリクエストを送信してから10分以内に推論テーブルに呼び出しが記録されていることを確認することができます。さらに、Databricksは少なくとも一回ログがデリバリーされることを保証しているので、場合によっては重複したログが送信されることがあります。

エンドポイントをクエリーした後は、エンドポイントのリクエストとレスポンスをDeltaテーブルで確認することができます。以下のSQLクエリーはエンドポイントの入出力を表示します。

Databricks SQLのUIやノートブックからこのクエリーを実行することができ、`payload_table`は`auto_capture_config`レスポンスの`state`で確認することができます。

```sql:SQL
SELECT * FROM <catalog>.<schema>.<payload_table>
```

# APIを用いたエンドポイント作成時の推論テーブルの有効化

APIを用いてエンドポイントを作成する際に、推論テーブルを有効化することができます。[モデルサービスエンドポイントの作成と管理](https://docs.databricks.com/ja/machine-learning/model-serving/create-manage-serving-endpoints.html)をご覧ください。

APIでは、リクエストボディに以下を指定するための`auto_capture_config`を含めます:

- Unity Catalogのカタログ: テーブルを格納するカタログ名
- Unity Catalogのスキーマ: テーブルを格納するスキーマ名
- (オプション)テーブルのプレフィクス: 推論テーブル名のテーブルプレフィクスを指定します。テーブルプレフィクスが指定されない場合、エンドポイント名が使用されます。
- (オプション)enabled: 推論テーブルを有効化するか無効化するのかを指定するブール値。デフォルトは`true`です。

カタログ、スキーマ、オプションのテーブルプレフィクスを指定した後は、`<catalog>.<schema>.<table_prefix>_payload`にテーブルが作成されます。このテーブルは自動的に[Unity Catalogのマネージドテーブル](https://docs.databricks.com/ja/data-governance/unity-catalog/create-tables.html)となります。

:::note
**注意**
推論テーブルは常にエンドポイントの作成、更新時に作成されるので、既存テーブルの指定はサポートされていません。
:::

以下の例では、エンドポイント作成時の推論テーブルの有効化の方法を示しています。

```bash:Bash
POST /api/2.0/serving-endpoints

{
  "name": "feed-ads",
  "config":{
    "served_models": [
      {
       "model_name": "ads1",
       "model_version": "1",
       "workload_size": "Small",
       "scale_to_zero_enabled": true
      }
    ],
    "auto_capture_config":{
       "catalog_name": "ml",
       "schema_name": "ads",
       "table_name_prefix": "feed-ads-prod"
    }
  }
}
```

レスポンスは以下のようなものとなります:

```json:JSON
{
  "name": "feed-ads",
  "creator": "customer@example.com",
  "creation_timestamp": 1666829055000,
  "last_updated_timestamp": 1666829055000,
  "state": {
    "ready": "NOT_READY",
    "config_update": "IN_PROGRESS"
  },
  "pending_config": {
    "start_time": 1666718879000,
    "served_models": [
      {
        "name": "ads1-1",
        "model_name": "ads1",
        "model_version": "1",
        "workload_size": "Small",
        "scale_to_zero_enabled": true,
        "state": {
          "deployment": "DEPLOYMENT_CREATING",
          "deployment_state_message": "Creating"
        },
        "creator": "customer@example.com",
        "creation_timestamp": 1666829055000
    }
   ],
   "config_version": 1,
   "traffic_config": {
     "routes": [
       {
         "served_model_name": "ads1-1",
         "traffic_percentage": 100
       }
      ]
   },
   "auto_capture_config": {
     "catalog_name": "ml",
     "schema_name": "ads",
     "table_name_prefix": "feed-ads-prod",
     "state": {
       "payload_table": {
         "name": "feed-ads-prod_payload"
       }
     },
     "enabled": true
   }
  },
  "id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "permission_level": "CAN_MANAGE"
}
```

推論テーブルへの記録が有効化されたら、エンドポイントが起動するのを待ちます。その後で呼び出せるようになります。

推論テーブルを作成した後は、システムによってスキーマ進化やデータ追加は管理されます。

:::note alert
**警告！**
以下のことを行うとテーブルがデグレードあるいは破損します:

- テーブルスキーマの変更
- テーブル名の変更
- テーブルの削除
- Unity Catalogのカタログ、スキーマへの権限の喪失

テーブルがデグレードした場合、推論テーブルを使い続けるには新規に推論テーブルを作成する必要がある場合があります。エンドポイントのステータスの`auto_capture_config`では、ペイロードデーブルの`FAILED`状態が表示されます。
:::

以下のオペレーションはテーブルの一貫性に影響を及ぼしません:

- テーブルに対するOPTIMIZE、ANALYZE、VACUUMの実行。
- 古い未使用データの削除。

`auto_capture_config`を指定しない場合、デフォルトでは以前の設定バージョンの設定が使用されます。例えば、すでに推論テーブルが有効化されているのであれば、次のエンドポイントの更新では同じ設定が使用され、推論テーブルが無効化されている場合には無効化されたままとなります。

```json:JSON
{
  "served_models": [
    {
      "name":"current",
      "model_name":"model-A",
      "model_version":"1",
      "workload_size":"Small",
      "scale_to_zero_enabled":true
    }
  ],
  "auto_capture_config": {
    "enabled": false
  }
}
```

# APIを用いた既存エンドポイントの推論テーブルの有効化

APIを用いて既存エンドポイントの推論テーブルを有効化することもできます。推論テーブルが有効化されると、推論テーブルを使い続けるためには以降のエンドポイントAPIの`auto_capture_config`ボディには同じものを指定し続けます。

:::note
**注意**
推論テーブル有効化後のテーブルロケーションの変更はサポートされていません。
:::

```bash:Bash
PUT /api/2.0/serving-endpoints/{name}/config

{
  "served_models": [
    {
      "name":"current",
      "model_name":"model-A",
      "model_version":"1",
      "workload_size":"Small",
      "scale_to_zero_enabled":true
    },
    {
      "name":"challenger",
      "model_name":"model-B",
      "model_version":"1",
      "workload_size":"Small",
      "scale_to_zero_enabled":true
    }
  ],
  "traffic_config":{
    "routes": [
      {
        "served_model_name":"current",
        "traffic_percentage":"50"
      },
      {
        "served_model_name":"challenger",
        "traffic_percentage":"50"
      }
    ]
  },
  "auto_capture_config":{
   "catalog_name": "catalog",
   "schema_name": "schema",
   "table_name_prefix": "my-endpoint"
  }
}
```

# 推論テーブルの無効化

推論テーブルを無効化するには、ユーザーは更新APIで`auto_capture_config`を指定してエンドポイント更新を行う必要があります。無効化においては、ユーザーはカタログ、スキーマ、テーブルプレフィクスを指定する必要はありません。必要なフィールドは`enabled: false`のみです。

また、Databricks機械学習UIで推論テーブルを無効化することができます。

1. エンドポイントページに移動します。
1. **Edit configuration**をクリックします。
1. **Enable inference table**の選択を解除します。
1. エンドポイントの設定が完了したら、**Update serving endpoint**をクリックします。

:::note warn
**重要！**
エンドポイントの推論テーブルが無効化された後の当該エンドポイントでの再有効化はサポートされていません。推論テーブルを使い続けるには、推論テーブルを有効化するための新規エンドポイントを作成する必要があります。
:::

# 次のステップ

推論テーブルを有効化すると、Databricksレイクハウスモニタリングを用いてモデルサービングエンドポイントとサービングされているモデルをモニタリングできるようになります。詳細は[Monitor model serving endpoints](https://docs.databricks.com/en/lakehouse-monitoring/monitor-endpoints.html)をご覧ください。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

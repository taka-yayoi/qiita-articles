---
title: Azure DatabricksでUnity Catalogの資産管理にサービスプリンシパルを活用する
tags:
  - Databricks
  - AzureDatabricks
  - UnityCatalog
private: false
updated_at: '2023-06-08T10:26:32+09:00'
id: 7b93b0d39edef8fa11eb
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの続編です。

https://qiita.com/taka_yayoi/items/f081628f042375e0c73a

サービスプリンシパルはGUIアクセスできないアイデンティティですが、Databricksに対する操作の大部分をカバーできます。

これは、

- インフラ管理者がDatabricksの資産の設定を行う
- エンドユーザーがその資産を活用する
- ただし、インフラ管理者は資産の設定のみを許可し、資産のアクセスはさせたくない

と言う要件で有効です。GUIでのアクセスができないので、アクセスすべきではない資産にインフラ管理者がアクセスしてしまうリスクを軽減できます。

ここでは、Unity Catalogの[外部ロケーション](https://learn.microsoft.com/ja-jp/azure/databricks/data-governance/unity-catalog/manage-external-locations-and-credentials)の作成と権限付与をサービスプリンシパルで行うケースを説明します。

# メタストアの設定

外部ロケーションはメタストア管理下にあるので、サービスプリンシパル自体、メタストア管理者である必要があります。

1. メタストアのデフォルトの管理者はアカウント管理者ですが、これを専用のグループに変更します。
1. アカウントコンソールで`metastore admins`というグループを作成し、そこに以前作成したサービスプリンシパルを追加します。必要に応じて他のアイデンティティを追加します。
![Screenshot 2023-06-08 at 10.08.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/eb1464a2-d335-760e-5477-b480bff773ab.png)
1. アカウントコンソールの**Data**にアクセスし、メタストアの**Configuration**で**Metastore Admin**の**Edit**をクリックします。
1. 作成したグループを選択して**Save**をクリックします。
![Screenshot 2023-06-08 at 10.09.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a8da8a81-bdd8-35f7-0732-510541c3d6f0.png)

# REST APIによる外部ロケーションの作成

APIリファレンスはこちら。ストレージ資格情報がない場合には別途作成ください。

https://docs.databricks.com/api/azure/workspace/externallocations/create

- エンドポイント: `https://<Databricksワークスペースのホスト名>/api/2.1/unity-catalog/external-locations`
- メソッド: POST
- Authorization: 
    - Type: Bearer
    - Token: サービスプリンシパルのトークン
- Body: raw/json

```json
{
    "name": "<外部ロケーション名>",
    "skip_validation": true,
    "url": "<ADLSのパス>",
    "read_only": true,
    "credential_name": "<ストレージ資格情報の名前>",
    "comment": "created by service principal"
}
```

これで、外部ロケーションが作成されます。作成者のサービスプリンシパルはGUIにアクセスできないので、外部ロケーション経由でファイルを参照するリスクが大きく軽減されます。
![Screenshot 2023-06-08 at 10.16.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/31916af4-23ac-8bf8-2532-e25209bf070f.png)

# REST APIによる外部ロケーションの設定

これだけでは、アクセス権が設定されていないので、これもREST API経由で権限設定を行います。

こちらのAPIを使用します。

https://docs.databricks.com/api/azure/workspace/grants/update

- エンドポイント: `https://<Databricksワークスペースのホスト名>/api/2.1/unity-catalog/permissions/{securable_type}/{full_name}`
    - securable_type: `EXTERNAL_LOCATION`
    - full_name: 上で作成した外部ロケーション名
- メソッド: PATCH
- Authorization: 
    - Type: Bearer
    - Token: サービスプリンシパルのトークン
- Body: raw/json

```json
{
  "changes": [
    {
      "principal": "<権限付与対象のアイデンティティ>",
      "add": [
        "<追加する権限>"
      ]
    }
  ]
}
```

こちらの例では、`ALL_PRIVILEGES`を付与しています。
![Screenshot 2023-06-08 at 10.21.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/90d4d433-7d45-96b9-7cc3-c1524034b585.png)

これによって、権限付与された側はData Explorer上でも外部ロケーションにアクセスできるようになります。
![Screenshot 2023-06-08 at 10.22.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e9daf56a-e9e1-9dca-37f9-e63ebb3c86da.png)

繰り返しになりますが、サービスプリンシパルの[クライアントシークレット](https://qiita.com/taka_yayoi/items/f081628f042375e0c73a#%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%83%97%E3%83%AA%E3%83%B3%E3%82%B7%E3%83%91%E3%83%AB%E3%81%AE%E4%BD%9C%E6%88%90)や[トークン](https://qiita.com/taka_yayoi/items/f081628f042375e0c73a#%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%83%97%E3%83%AA%E3%83%B3%E3%82%B7%E3%83%91%E3%83%AB%E3%81%AE%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%82%92%E5%8F%96%E5%BE%97%E3%81%99%E3%82%8B)には有効期限があることに注意してください。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

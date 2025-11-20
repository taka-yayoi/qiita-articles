---
title: Databricks Appsのユーザー代理認証(OBO)
tags:
  - Databricks
  - DatabricksApps
private: false
updated_at: '2025-09-28T21:01:43+09:00'
id: 00cb953efae41ff98cfe
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらのユーザー代理認証(on-behalf-of-user authorization)、実際に触ったことがなかったのでした。

https://docs.databricks.com/aws/ja/dev-tools/databricks-apps/auth#%E3%83%A6%E3%83%BC%E3%82%B6%E3%83%BC%E8%AA%8D%E8%A8%BC

> ユーザー認証は、on-behalf-of-user authorization とも呼ばれ、Databricks Apps アプリがアプリユーザーのアイデンティティで動作することを可能にします。Databricks はユーザーのアクセストークンをアプリに転送し、アプリはそのトークンを使用してユーザーに代わってリソースにアクセスします。Databricks は、ユーザーの既存の [Unity Catalog](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/) ポリシーに基づいてすべての権限を強制します。

デフォルトではアプリに割り当てられるサービスプリンシパルに対するアクセスコントロールなので、きめ細かいアクセス制御ができないので、こちらの機能はありがたいです。

ただ、試すの面倒だなーと思っていたところ、いい感じのサンプルがありました。

https://github.com/databricks-solutions/databricks-apps-examples/tree/main/auth-demo

早速試してみます。上のリポジトリを[Gitフォルダ](https://docs.databricks.com/aws/ja/repos/)として連携して同期します。

アプリを作る際には、[こちら](https://docs.databricks.com/aws/ja/dev-tools/databricks-apps/auth#%E3%82%A2%E3%83%97%E3%83%AA%E3%81%AB%E3%82%B9%E3%82%B3%E3%83%BC%E3%83%97%E3%82%92%E8%BF%BD%E5%8A%A0%E3%81%99%E3%82%8B)で説明されているように**ユーザー認証**のセクションで、アクセスするリソースのスコープを追加する必要があります。
![Screenshot 2025-09-28 at 20.29.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fd4e99c3-01a6-41b6-98bf-3f2a7673a310.png)
![Screenshot 2025-09-28 at 20.29.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9812d838-b128-4a26-b5dc-0dd76b71af93.png)

Gitフォルダの`auth-demo`をデプロイします。
![Screenshot 2025-09-28 at 20.30.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a6633990-3e4e-48d6-b886-48d7683ad724.png)

デプロイしました。
![Screenshot 2025-09-28 at 20.33.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b57a144b-396b-48cf-9519-afd795b455be.png)

アプリにアクセスすると、このアプリはあなたの資格情報でリソースにアクセスする旨のメッセージが表示されます。上でスコープを指定したリソースが表示されます。
![Screenshot 2025-09-28 at 20.33.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ee818215-3844-4ca4-9a92-d8c3ce1e7d55.png)

アプリはこんな感じ。デフォルトで作成されるアプリごとのサービスプリンシパル(SP)とユーザー代理認証の比較を行うことができます。
![Screenshot 2025-09-28 at 20.33.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/68f52116-48bb-4797-95d4-dc7942e0dc16.png)

ただ、デフォルトのテーブルはサンプルデータなのでSPだろうがユーザーだろうがアクセスできます。
![Screenshot 2025-09-28 at 20.33.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/83b5e2a1-f45d-4ac1-a9c9-b3bdfb5ab9fc.png)
![Screenshot 2025-09-28 at 20.34.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/49539107-7313-4979-92d6-6aa5b1a808a7.png)

そこで、冒頭にあったUnity Catalogの[ポリシー](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/abac/policies)を適用したテーブルで試します。

以下のポリシーでは自分以外を対象として適用される、[列マスク](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/filters-and-masks/#%E5%88%97%E3%83%9E%E3%82%B9%E3%82%AF%E3%81%A8%E3%81%AF%E4%BD%95%E3%81%A7%E3%81%99%E3%81%8B)のポリシーとなっています。
![Screenshot 2025-09-28 at 20.37.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/11827245-7bcc-4daf-809a-c1cd10e53a31.png)
![Screenshot 2025-09-28 at 20.38.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d99cbe66-f792-411a-84c6-acfb41677235.png)

サービスプリンシパルでアクセスすると`email`列がマスキングされています。
![Screenshot 2025-09-28 at 20.39.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e533c54d-9e9f-4e6c-8af8-4c7bb00ce5b3.png)

自分として代理認証してもらうとマスキングされません。
![Screenshot 2025-09-28 at 20.39.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ec053e28-8e40-4f7e-b287-14d133b55a91.png)

アプリがデータなどのリソースにアクセスする際には、ユーザーごとに挙動を変えたいというニーズは多いと思います。是非OBOをご活用ください！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

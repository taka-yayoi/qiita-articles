---
title: Databricksのエクスプレスセットアップ
tags:
  - Databricks
private: false
updated_at: '2025-02-18T13:43:35+09:00'
id: d180c3e65da26befe9de
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの素晴らしい動画が公開されて、存在に気づきました。

<iframe width="560" height="315" src="https://www.youtube.com/embed/887Y7q4lR8c?si=E71gS20ajJy0bBHF" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

エクスプレスセットアップ(Express Setup)、その名の通り特急でDatabricksをセットアップできます。[マニュアル](https://docs.databricks.com/ja/getting-started/express-setup.html)も準備されていました。

> エクスプレス セットアップを使用して最初のワークスペースを作成する方法について説明します。 エクスプレスセットアップは、事前にクラウドプロバイダーにアクセスする必要のない、Databricks の使用を開始する簡単な方法です。 Databricksはメールだけで登録して利用を開始できます。

従来はAWSの場合、以下の選択肢からデプロイすることが一般的でした。

1. AWS CloudFormationを用いたクイックスタート
1. 自分でVPCなどをセットアップして、Databricks環境を手動でデプロイ

いずれにしても、**お客様のAWSアカウント**が必須でした。しかし、このエクスプレスセットアップではAWSアカウントが不要です！早速試してみます。

# エクスプレスセットアップのウォークスルー

以下のURLにアクセスします。

https://signup.databricks.com/

上の**Continue with Express Setup**をクリックします。

![Screenshot 2025-02-18 at 13.12.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f2701182-580d-4e22-8dcd-c31fe24271ec.png)

サインアップに用いるアカウントを指定します。今回はメールアドレスを指定して、**Continue with email**をクリックします。

指定したメールアドレスに認証コードが送信されるので入力します。

![Screenshot 2025-02-18 at 13.13.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/735f3e5b-465e-4865-89c4-fda10a72feb6.png)

Databricksアカウント名を聞かれるので、組織名に基づくアカウント名を入力します。

![Screenshot 2025-02-18 at 13.14.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/be1b38ab-e9d0-49b0-a172-466101c27663.png)

国を選択します。パフォーマンスの観点から所在地に最も近い国を選択することをお勧めします。

![Screenshot 2025-02-18 at 13.14.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8b86e4c0-668a-4fee-8943-f5f26ec84dc4.png)

数秒待ちます。

![Screenshot 2025-02-18 at 13.14.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ebaec8a5-3c8e-4f46-bd48-fb039cda8daf.png)

これだけでDatabricksワークスペースが稼働します！この状態で**14日が経過する、あるいはクレジットを使い切るまで**は無料でDatabricksを使うことができます。

![Screenshot 2025-02-18 at 13.15.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/90a07dde-038e-41ef-b701-3dc39f4c4c67.png)

以下のようなメールも届きます。

![Screenshot 2025-02-18 at 13.42.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/84946ade-83df-4efd-aeb4-e76cfad9840d.png)


ところで、画面右上に**トライアルを管理**というボタンが表示されています。

![Screenshot 2025-02-18 at 13.15.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bf69ccb5-cbd1-4b01-b747-2df3ad1c0e8f.png)

こちらをクリックすると、トライアル期間中の残クレジット、トライアル終了後の支払い方法を指定する画面が表示されます。

![Screenshot 2025-02-18 at 13.15.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/85170d53-e793-4d46-9f80-44921f40b451.png)

# トライアル終了後は

上述の通り、14日が経過する、あるいはクレジットを使い切るとトライアルが終了します。[こちら](https://docs.databricks.com/ja/getting-started/express-setup.html#what-happens-after-the-trial-ends)に説明があるように、支払い方法を入力するまではDatabricksを使用できなくなります。

# 支払い方法を追加すると？

サーバレス以外のカスタマイズ可能なコンピュート資源、自身のストレージを設定可能なワークスペースをご自身のDatabricksアカウントに追加できるようになります。

# まとめ

これまではDatabricksを試すには、無償の機能限定版である[Community Edition](https://community.cloud.databricks.com/login.html)を使うか、上述した従来の方法で環境を構築する必要がありました。
しかし、このエクスプレスセットアップを用いることで、名前の通り特急のスピードで環境を構築し、ほぼすべての機能を試してみることができます。是非ご活用ください！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

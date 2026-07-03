---
title: Databricks Reposでゴミ箱がサポートされました！
tags:
  - Databricks
private: false
updated_at: '2023-07-22T07:39:25+09:00'
id: 41ed8fdaf5349cce0eb7
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらのアップデートです。

https://docs.databricks.com/release-notes/product/2023/july.html#move-to-trash-enabled-for-repos

# Databricks Reposとは？

GitHubなどのバージョン管理システムのリポジトリとDatabricksワークスペースで同期を行える機能です。これによって、ソースコードをGitHubで管理しながら、Databricksの様々な機能を活用できます。

https://qiita.com/taka_yayoi/items/b89f199ff0d3a4c16140

これまではRepos配下のソースコードを削除すると、即座に削除され復旧ができませんでした。リモートリポジトリから再度同期するしかありませんでした。

今回のアップデートで、通常のノートブックと同じように削除した際にはゴミ箱に移動されるので復旧が容易となります。

# ウォークスルー

Repos配下のソースコードを一覧表示して、一番右の3点リーダーをクリックすると、**ゴミ箱に移動**が表示されます。
![Screenshot 2023-07-22 at 7.29.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/39029e81-42d6-fd75-2229-16ef72012ac7.png)

確認メッセージが表示されます。
![Screenshot 2023-07-22 at 7.29.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fe782aa3-e7cf-7f75-7e0b-641659b21e63.png)

ゴミ箱を確認します。移動されています。
![Screenshot 2023-07-22 at 7.29.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/78f6b6ff-7a89-f743-ccb3-52613b37f833.png)

復旧してみます。再度、3点リーダーをクリックして、**復元**を選択します。
![Screenshot 2023-07-22 at 7.30.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c30238e0-b3f8-8e7d-52a4-4c5f9de62491.png)

移動先を選択します。まずは最上位まで移動します。**Repos**から辿って元のパスを選択します。
![Screenshot 2023-07-22 at 7.31.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8bdf59b4-e295-a078-8ff4-f9571bbe3c7f.png)
![Screenshot 2023-07-22 at 7.30.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b08732c2-3c50-36b1-0bcd-5d83a6242901.png)

確認メッセージが表示されます。
![Screenshot 2023-07-22 at 7.31.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0e75292d-835c-6485-d79d-7d21380aba9a.png)

復旧できました！
![Screenshot 2023-07-22 at 7.31.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/80dad1ed-adcc-ff04-94f1-b61e59894a14.png)



### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: GitにおけるDatabricks AI/BIダッシュボードのソース管理
tags:
  - Git
  - Databricks
  - Databricks_AI_BI
private: false
updated_at: '2025-04-18T17:27:01+09:00'
id: af580c4bad7db4aebc38
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの機能です。

https://docs.databricks.com/aws/ja/dashboards/git-support

> ダッシュボードに Databricks Git フォルダーを使用すると、変更と履歴の可視性が向上し、コラボレーションがより効率的になります。 また、ダッシュボードの本番運用へのデプロイが簡素化され、以前のバージョンの復元が可能になり、信頼性の高いバックアップソリューションとして機能します。



# 有効化

ワークスペースの[Preview](https://docs.databricks.com/aws/ja/admin/workspace-settings/manage-previews)ページで**Support Dashboards in Git Folder**を有効にします。

![Screenshot 2025-04-13 at 9.08.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b1eba2d2-eb33-40c6-89db-fb5d17deed9b.png)

# 準備

GitHubなどでリポジトリを作成します。

![Screenshot 2025-04-13 at 9.09.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/61736a62-8106-4b44-abaf-8ec31734ed39.png)

# ダッシュボードのソース管理

Databricksワークスペースで、上のリポジトリをポイントする[Gitフォルダ](https://docs.databricks.com/aws/ja/repos/)を作成します。

![Screenshot 2025-04-13 at 9.09.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/02e27d78-79bf-40f3-90e6-39d303483194.png)

Gitフォルダでダッシュボードを作成します。

![Screenshot 2025-04-13 at 9.09.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/54ab4181-5a57-4236-baed-43dfa4edaf6c.png)

![Screenshot 2025-04-13 at 9.12.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e6fe88f8-1ec2-4851-94cc-834d86b18a00.png)

ダッシュボードが保存されているGitフォルダにアクセスし、**main**をクリックします。

![Screenshot 2025-04-13 at 9.12.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4eb5e4f9-558d-4954-8696-2b0131f241aa.png)

ダッシュボードはJSONとして取り扱われるので、そのままコミット & プッシュできます。

![Screenshot 2025-04-13 at 9.12.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c20088de-fd9f-48de-83d2-4e8b40921435.png)

これでGitにプッシュされました。

![Screenshot 2025-04-13 at 9.13.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0183cc73-78eb-48a5-af48-3f3df34a1b24.png)

# 変更管理

GitでJSONが管理されるので、レイアウト変更なども追跡できます。

![Screenshot 2025-04-13 at 14.50.38.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/afb0aa24-778a-4b92-a180-63a24b675283.png)
![Screenshot 2025-04-13 at 14.51.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e2b8a7ba-79f1-4ea9-a2c7-817988b0b9fa.png)

なお、Gitフォルダで管理されているダッシュボードを表示した際にも、コミット&プッシュを行うボタンが表示されます。

![Screenshot 2025-04-18 at 17.25.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7274d472-41c2-47df-af33-a97d1e393d28.png)



リポジトリはこちらです。

https://github.com/taka-yayoi/dashboard_in_git/tree/main

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

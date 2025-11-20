---
title: Databricks AzureにおけるReposの利用(実践編)
tags:
  - Azure
  - Databricks
  - Repos
private: false
updated_at: '2021-11-30T11:12:53+09:00'
id: 9f8efd3ddbe54bdb0d58
organization_url_name: databricks
slide: false
ignorePublish: false
---
本書は、[Repos Git 統合の場合 \- Azure Databricks \| Microsoft Docs](https://docs.microsoft.com/ja-jp/azure/databricks/repos)の手順を説明したものです。

:::note info
こちらで紹介している方法は、認証にパーソナルアクセストークンを使用する方法です。これ以外に、Azure Active Directoryを使用することもできます。
:::

# Azure DevOpsのセットアップ

[Authenticate with personal access tokens](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page)の手順に従い、Azure DevOpsのプロジェクトにアクセスするためのパーソナルアクセストークンを作成します。

1. AzureポータルからAzure DevOpsにアクセスします。
1. **My Azure DevOps Organizations**のリンクをクリックします。
1. Organizationがない場合には、Organizationを作成します。
1. `dev.azure.com/<Organization名>`にアクセスします。
1. Projectを作成します。
1. Projectにアクセスし、右上の人の形のアイコンをクリックし、メニューを展開します。
1. **Personal access tokens**を選択します。
1. **+ New Token**をクリックします。
![Screen Shot 2021-11-30 at 10.41.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bdc1dfb5-7465-0f02-60e0-ed07799c50e6.png)
1. Scopeを設定の上、トークン名を入力して**Create**をクリックします。
![Screen Shot 2021-11-30 at 10.45.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1243feba-1352-d416-8606-09c779f9ada7.png)
1. 表示されるトークンをコピーしておきます。

# Azure Databricksの設定

1. サイドメニューの**Settings > User Settings**を選択します。
1. **Git Integration**タブを開き、以下の内容を指定します。
    - **Git provider**: Azure DevOps Services (personal access token)
    - **Git provider username or email**: Azureのユーザーアドレス
    - **Token**: 上のステップでコピーしたパーソナルアクセストークン
![Screen Shot 2021-11-30 at 10.51.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f1356824-1683-a60e-650d-b288c36a375d.png)

1. **Save**をクリックします。
1. Azure DevOpsのReposをクリックし、**Clone to your computer**に表示されるURLをコピーしておきます。
![Screen Shot 2021-11-30 at 10.58.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b420ba1c-398e-3f1f-de22-cd87ceef34b3.png)

# Repoの追加

1. サイドメニューから**Repos**を選択します。
1. 自身のメールアドレスをクリックし、右上の**Add Repo**をクリックします。
1. ダイアログの**Git repo URL**に上でコピーしたURLを貼り付けます。
1. **Create**をクリックします。

# 動作確認

1. 上で作成したRepoにアクセスしノートブックを追加します。
1. **master**ボタンをクリックします。
1. コメントを入力して**Commit & Push**をクリックします。
![Screen Shot 2021-11-30 at 11.03.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/771b5432-0a0d-0ec1-07f6-2d2f8b10adee.png)
1. Azure DevOps側に変更が反映されていることを確認します。
![Screen Shot 2021-11-30 at 11.09.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/be586b12-bc16-59b9-dedf-06d9bf6b9b55.png)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

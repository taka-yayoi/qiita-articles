---
title: Databricks Reposによるデータサイエンスの本格運用
tags:
  - GitHub
  - Databricks
  - CICD
private: false
updated_at: '2021-03-24T04:38:37+09:00'
id: ddac6a3bc3c0ee9f41da
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Databricks Repos Integrates With Git Providers for a Better Development Experience\- The Databricks Blog](https://databricks.com/blog/2021/03/16/productionize-data-science-with-repos-on-databricks.html)の翻訳です。

**Gitベースのコラボレーション、再現性確保、CI/CDがより容易になりました**

多くのデータサイエンスに関わるソリューションは、データチームに対して、探索の柔軟性か本格運用における厳密性かの二択を迫ります。結果として、データサイエンティストは彼らの成果物をエンジニアリングチームに引き渡す際に、異なるテクノロジースタックに載せ替えることになり、新たな環境に応じて、成果物を書き直す必要があります。これはコストがかかるだけではなく、データサイエンティストの成果をビジネス価値につなげるまでに時間を要することを意味します。
![](https://databricks.com/wp-content/uploads/2021/03/repos-blog-screenshot.png)

Databricksの[次世代データサイエンスワークスペース](https://databricks.com/blog/2020/06/25/introducing-the-next-generation-data-science-workspace.html)は、先進的かつ統合された、オープンな体験をデータチームに提供します。このワークスペースの一機能として、データチームの全ての人がベストプラクティスを活用できるように、リポジトリレベルでGitプロバイダと連携可能な新たなRepos機能を提供できることを嬉しく思います。DatabricksのRepos機能はGithub、Bitbucket、Microsoft Azure DevOpsを含むGitプロバイダと連携できます。

Gitと連携することで、Databricks Reposはデータサイエンス、データエンジニアにおける洗練された開発環境を提供します。Databricksでの開発において、本格運用前のコードレビュー、テストと言ったコードに関する規則を導入できます。Reposにおいては、リモートGitリポジトリのクローン(図1)、ブランチの管理、リモートでの変更のPull、コミット前の変更確認(図2)など慣れ親しんだGitの機能を利用することができます。
![](https://databricks.com/wp-content/uploads/2021/03/prod-ds-repos-blog-image-2.png)
**図1** 利用を開始するには、クローンしたいGitリポジトリのURLを指定するだけです

![](https://databricks.com/wp-content/uploads/2021/03/prod-ds-repos-blog-image-3-rev.png)
**図2** 開発者は自身の開発用ブランチで作業し、コードをコミットしたり変更をプルしたりできます。コミット前にUIで差分を確認することができます

Reposの正式ローンチに際して、エンターブライズでの利用を想定した以下の機能を追加しています：

- **許可リスト(Allow lists)** 管理者はコードをコミットできるGitリポジトリのURLのプレフィクスを指定できます。これにより、許可されていないリポジトリにコードがコミットされることを防ぐことができます。
- **シークレット検知(Secret detection)** コミット前に、ソースコードに平文で記述されてしまっているシークレット情報を検知します。これによりデータチームは、機密情報をDatabricksのシークレットマネージャで管理すべきというベストプラクティスに従うことが可能になります。

また、ReposはあなたのCI/CDパイプラインと統合可能であり、データチームはデータサイエンス、機械学習のコードをシームレスに実験段階から本格運用段階に移行することが可能です。Repos API(現在プライベートプレビュー、詳細はDatabricks担当にお問い合わせください)によりプログラムを通じて、Databricks Reposをリモートブランチの最新の状態にアップデートすることが可能です。これによりCI/CDパイプラインを容易に実装できます。例えば：

1. **開発：** 開発者はユーザーフォルダにチェックアウトされた機能開発のためのブランチで作業します。
2. **レビュー及びテスト：** 開発した機能をレビューする準備ができた際には、PR(Pull Request)が作成されます。あなたのCI/CDシステムは、Repos APIを利用し、ブランチ上の変更に基づくDatabricks上のテスト環境のアップデート、変更箇所のテストを自動的に実行します。
3. **本格運用:** そして、全てのテストを通過したのち、PRは承認されマージされます。ここでもCI/CDシステムはRepos APIを使用し、本番環境をアップデートします。本番環境におけるジョブは最新のコードを用いて処理を行います。

Reposは次世代ワークスペースの機能の一つです。正式リリースにより、データチームはベストプラクティスを活用し、容易に実験段階から本格運用に移行できるようになりました。

## Reposを利用するためには
![](https://databricks.com/wp-content/uploads/2021/03/prod-ds-repos-blog-image-4.png)

Reposは現在パブリックプレビューですので、Databricksワークスペースでご利用いただけます！Reposを有効化するためには、AdminコンソールのAdvancedに移動し、"Repos"の隣にある"Enable"ボタンをクリックするだけです。詳細は[ドキュメント](https://docs.databricks.com/projects.html)をご確認ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

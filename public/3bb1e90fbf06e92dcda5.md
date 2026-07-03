---
title: 4月にDatabricksワークフローに導入される新たなアップデート
tags:
  - Databricks
private: false
updated_at: '2023-04-05T20:05:44+09:00'
id: 3bb1e90fbf06e92dcda5
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Exciting new updates coming to Workflows in April \- The Databricks Blog](https://www.databricks.com/blog/2023/04/04/exciting-new-updates-coming-workflows-april.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# ファイル到着トリガー、連続ジョブ、SQLファイル、タスクを編集するために改善されたユーザーインタフェース

より多くのタスクを適切なタイミングでオーケストレートする機能を追加し、自動化ジョブを作成・起動する方法をシンプルにする[ワークフロー](https://www.databricks.com/jp/product/workflows)の素晴らしいいくつかの新機能のリリースを発表できることを嬉しく思っています。あなたが経験豊富なデータエンジニアであろうが、SQLクエリーの自動化に取り組み始めたのであろうが、これらの新機能は、皆様のワークフローをシンプルにし、生産性をブーストし、皆様のゴールをより効率的に達成する支援をすることを目的としています。この記事では、最近のリリースの大部分を網羅し、レイクハウスを加速するこれらの新機能の使い方を説明します。

# ファイル到着トリガー

スケジュール処理に加えて、多くのお客様は特定のイベントが生じた際にワークフローを起動したいと考えています。このため、我々は「ファイル到着トリガー」というパワフルな新機能を導入します。この機能を用いることで、クラウドストレージにファイルが到着した際にジョブを起動するように設定することができます。これらの新たなトリガーを用いることで、ワークフローはファイルが到着した際に、データを取り込み、機械学習推論や任意のタイプの分析を即座に実行することができます。この機能の活用をシンプルにするために、クラウドストレージへのアクセスを管理する[Unity Catalog](https://www.databricks.com/jp/product/unity-catalog)の外部ロケーションを活用できます。

ファイル到着トリガーは[Azure](https://learn.microsoft.com/ja-jp/azure/databricks/workflows/jobs/file-arrival-triggers)と[AWS](https://docs.databricks.com/workflows/jobs/file-arrival-triggers.html)でパブリックプレビューとなっています。
![](https://cms.databricks.com/sites/default/files/inline-images/db-565-blog-img-1.png)

# 連続ジョブ

連続ジョブを用いることで、Apache Spark™構造化ストリーミングジョブのように、24/7で実行される高信頼のワークロードをオーケストレートすることができます。この新機能を用いることで、ワークフローがスケジュールとリトライを管理するので、最大同時実行数を設定したり、特殊なcronスケジュールを選択する必要がなくなります。Databricksにおいては、ワークフローを簡単に使えるようにすることにフォーカスしているので、連続ジョブの設定は非常に簡単なものとなっています。必要なのはTriggersメニューでボタンをクリックするだけです。

[連続ジョブ](https://docs.databricks.com/workflows/jobs/jobs.html#run-a-continuous-job)はパブリックプレビューです。

# SQLファイル

Databricksワークフローでオーケストレートできるタスクタイプを拡張することで、今ではDatabricks SQLウェアハウスでファイルに定義されたSQLクエリーを含む外部ファイルをオーケストレートすることができます。すでに皆様は、事前定義された[Databricks SQLのクエリー](https://qiita.com/taka_yayoi/items/e0c37a7a380122724b3f)、アラートの実行、ダッシュボードの更新をスケジューリングしているかもしれません。新たなSQLファイルタスクを用いることで、Gitリポジトリに **.sql** ファイルを格納できるようになります。ジョブが実行される都度、特定ブランチから最新バージョンのファイルが取得されます。この新機能によって、ノートブックやSQLクエリーを一緒に共同バージョン管理できるようになります。これらのアーティファクトに対してGitを活用することで、チームメンバー間のコラボレーションを改善し、エラーのリスクを削減します。

SQLファイルは正式提供(GA)となっています。
![](https://cms.databricks.com/sites/default/files/inline-images/db-565-blog-img-2.png)

# ユーザーインタフェースの改善

最後になりますが、ジョブの作成、編集のためのDatabricksワークフローユーザインタフェースも改善しました。皆様の生活を可能な限りシンプルにするという目的のもと、全体的なジョブの構成や設定を見失うことなしにタスクを変更することができます。この新たなインタフェースは、ジョブ作成と編集プロセスを円滑にし、複雑なワークフローの作成と管理を容易にします。
![](https://cms.databricks.com/sites/default/files/inline-images/db-565-blog-img-3.png)

# サマリー

Databricksではワークフロー製品の改善に取り組み続けていきます。本記事では、いつジョブを実行すべきかを定義する複数の方法と、バージョン管理されたSQLクエリーのオーケストレーションの新たな手段、ワークフローの作成、編集をシンプルにする新たなユーザーインタフェースをご紹介しました。

皆様がレイクハウスから更なる価値を引き出すために、これらの機能が皆様のお役に立つのを楽しみにしています。どれが一番エキサイティングでしたか？すぐにワークフローをお試しください！


### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

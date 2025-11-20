---
title: Databricks Appsのご紹介
tags:
  - Databricks
  - DatabricksApps
private: false
updated_at: '2024-10-09T09:54:06+09:00'
id: 6c07fbfc72a5cf9c7a6c
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Introducing Databricks Apps \| Databricks Launch Blog](https://www.databricks.com/blog/introducing-databricks-apps)の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

**データやAIアプリケーションを構築する最も迅速で最もセキュアな手段**

# サマリー

- 内部向けデータ、AIアプリケーションを構築、デプロイする新たな手段であるDatabricks AppsがAWSとAzureでパブリックプレビューになりました。
- 理想的なユースケースには、データのビジュあらいーゼーション、セルフサービスの分析、データ品質の監視などがあります。
- Dash、Shiny、Gradio、Streamlit、Flaskのアプリケーション開発フレームワークをサポートしています。
- サーバレスコンピュートへの自動プロビジョニングは、アプリケーション開発を容易にします。
- Unity Catalogによるビルトインのガバナンス、OIDC/OAuth 2.0やSSOを通じたセキュアなユーザー認証。

本日、Databricksデータインテリジェンスプラットフォーム上で、データ&AIチームが内部向けアプリケーションを直接構築、デプロイする最も迅速な手段である[Databricks Apps](https://www.databricks.com/product/databricks-apps)のパブリックプレビューを発表できることを嬉しく思っています。

Databricks Appsによって、開発者はDash、Shiny、Gradio、Streamlit、Flaskのような人気のフレームワークを用いて、Databricks内でネイティブにアプリを構築できるようになります。Databricks Appsの主要な利点の一つは、SQLではなくコードを用いて、非技術ユーザー向けに仕立てられたデータアプリケーションを作成できる能力です。これによって、複雑なデータの洞察に企業内のより広範なオーディエンスがアクセスできるという新たな可能性を解放することになります。例えば、マーケティングチームは、キャンペーンのパフォーマンスメトリクスを可視化するカスタムのダッシュボードを作成するためにDatabricks Appsを活用することができ、技術的なバックグラウンドを持たないチームメンバーは容易にデータを解釈し、それに基づくアクションを取れるようになります。さらに、Databricks AppsはAIコンポーネントと連携することができるので、開発者がより大きな柔軟性を必要とする際に、特定のAIモデルを呼び出すことが可能となります。このAIの能力とのインテグレーションによって、顧客のフィードバックに対する感情分析や売り上げ予測にたいすする予測モデリングのようなタスクを実行することができる洗練されたアプリケーションを作成することができ、非技術者ユーザーにおけるデータ洞察の価値を高めることができます。

アプリを構築すると、Databricks内に直接デプロイ、管理されるので、チームがインフラストラクチャを設定、管理する工数を削減することができます。これらのアプリは、完全に管理され、Unity Catalogですでに設定されているデータのアクセスコントロールに従い、同じ統合ガバナンスモデルを用いたユーザーへの提供を制御します。Databricks Appsによって、企業はDatabricks環境でシームレスに実行されるカスタムのアプリケーションを作成することで、自身のデータとAIへの投資に対する完全なポテンシャルを活用することができます。

<iframe width="560" height="315" src="https://www.youtube.com/embed/Equ7PBeM-Mw?si=UinRXHUlN0wRiBAZ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


# データアプリケーション構築における課題

現在のデータドリブンの世界では、企業は自身のデータ資産から更なる価値を引き出すための手段を探索しています。しかし、内部向けのデータアプリケーションの構築とデプロイは、歴史的に複雑で時間を浪費するプロセスとなっていました。開発者はアプリケーション開発ではなく、インフラストラクチャの管理に時間を費やす必要がありました。データガバナンスやコンプライアンスには、アクセスコントロールの主導の実装が必要となります。さらに、他のデータ資産とは個別にアプリ共有や権限管理が行われ、分断されたガバナンス体験を引き起こします。

# Databricks Apps: セキュアなデータアプリケーションをクイックに構築

Databricks Appsは、これらの課題に真正面から取り組み、内部向けのデータアプリケーションを構築するためのパワフルかつシンプルな体験を提供します。Databricks Appsを導入することで、企業では様々なメリットを解放することができます:

## 構築がシンプル

Databricks Appsはお使いのDatabricks環境で直接実行、あるいは[Visual Studio Code](https://www.databricks.com/blog/simplified-faster-development-new-capabilities-databricks-vs-code-extension#:~:text=We%20are%20excited%20to%20announce,integration%20with%20the%20Databricks%20CLI.)や[PyCharm](https://www.databricks.com/blog/announcing-pycharm-integration-databricks)のようなツールを用いて実行することができ、あなたのデータやAIモデルへのシームレスなアクセスを可能にします。Databricks Appsを用いることで、データサイエンティストやデータエンジニアはDash、Gradio、Streamlitのような人気のPythonフレームワークを用いてアプリケーションの開発とイテレーションを迅速に行うことができます。また、柔軟なアプリケーションをクイックに構築できるように、構築済みのPythonテンプレートを選択することができます。

![](https://www.databricks.com/sites/default/files/inline-images/smallersizetopImage.gif?v=1728328931)

> "Databricks Appsは、私のRAGのPOCを洗練されたアプリケーションに変換する助けになりました。我々は、自分たちの企業の膨大な知識ベースを活用することで、ユーザーの質問に回答するRAGシステムを構築しました。"  - Heather Gomer, SAE International

## プロダクションレディ、自動デプロイメント

Databricks Appsでは、開発者は追加のインフラストラクチャを構築する必要がありません。アプリは自動でプロビジョンされるサーバレスコンピュートで実行され、デプロイメントを簡単にします。また、Databricks Appsでは業界最先端の開発プラクティスを導入しており、お好きなワークフローとのシームレスなインテグレーションを提供します。Databricksワークスペース内で直接作業しようが、お好きなIDEを活用しようが、Gitバージョン管理やCI/CDパイプラインのメリットを享受することができ、あなたの内部向けアプリがプロダクションレディであることを確実にします。

![](https://www.databricks.com/sites/default/files/inline-images/productionready.gif?v=1728328931)

アプリを作成すると、Databricks Appsは検索性とアクセスにおけるシンプルさを提供します。アプリがデプロイされると、開発者が意図したユーザーに共有可能なユニークなURLが生成され、アプリケーションへの直接のアクセスを提供します。さらに、企業内のユーザーは **"compute"** タブに移動し、**"apps"** タブを選択することで、同僚が作成したアプリを特定することができ、内部向けアプリの探索を可能にします。

> "我々のDevOpsプロセスへのDatabricks Appsのシームレスなインテグレーションによって、ユーザーに新機能をクイックに紹介し、テストしてもらえるようになり、内部アプリケーションに対するセキュアでプロダクションレディのフロントエンドを提供してくれています。追加のインフラストラクチャは不要です。" - Lukas Heidegger, E.ON Digital Technology

## ビルトインのガバナンス

Databricks Appsを用いることで、データはあなたが選択した場合にのみ、Databricks環境を離れることになります。それぞれのアプリは、正確なデータアクセス権限を確実にするきめ細かいアクセスコントロール、アプリケーション間通信のための自動で管理されるサービスプリンシパル、シームレスでセキュアなユーザーアクセスのためにOIDC/OAuth 2.0やSSOを活用した自動ユーザー認証を含む堅牢なセキュリティ対策で防御されます。

さらに、Unity Catalogのリネージ機能と連携することで、あなたのアプリケーションのデータの起源、変換処理、活用に対する包括的な可視性を提供し、データのトレーサビリティとコンプライアンスを強化します。この連携のアプローチは、あなたのデータアプリケーションが企業のポリシーや規制の要件に準拠していることを確実にし、チームにおけるデータの発見やデータのプロモーションを促進します。

![](https://www.databricks.com/sites/default/files/inline-images/diagram.png?v=1728328931)

> "Databricks Appsを用いることで、セキュリティチーム、インフラストラクチャチームの多くの作業を削減し、プロダクションのアプリを即座にステークホルダーに共有できるようになりました。" - Cesar Augusto Charalla Olazo, Addi

# 一般的なアプリのパターン

Databricks Appsは、以下を含む様々なアプリケーションを構築するために活用できます:

- **カスタムのデータのビジュアライゼーション:** ビジネスユーザーがリアルタイムでデータを探索、分析できるようにする動的かつデータドリブンのビジュアライゼーション。
- **AIアプリ:** 予兆保全、顧客セグメンテーション、不正検知のようなタスクのために機械学習モデルを活用するアプリケーションの開発。
- **セルフサービス分析:** ビジネスユーザーがユーザーフレンドリーなインタフェースを通じて複雑な分析を行えるようにし、データチームの負荷を削減。
- **データ品質監視:** データ品質を追跡、改善するためのカスタムツールの構築。

> "Databricks Appsによって、我々のヘルス、安全性、環境のためのインテリジェンスプラットフォームのユーザーが利用するデータインタフェースを完全に実現しました。今では、セマンティック検索ツールやその他の様々なダッシュボードをフィーチャーするStreamlitダッシュボードをホストしています。" - Lukas Heidegger, E.ON Digital Technology

> “Posit (2024 Databricks Developer Tools Partner of the Year)は、企業が自分のデータから洞察を導き出す助けとなるために、コードファーストツールを用いてアプリケーションを作成することのパワーに信念を持っています。この信念は、Shiny for RやShiny for Python、Posit Connectの開発に繋がり、様々なアプリケーションをサポートするためにDatabricks Appsのコラボレーションにも繋がりました。コードファーストツールが可能な限りユビキタスでアクセス可能にするための、Databricksとの今後のコラボレーションを楽しみにしています。" - Tareef Kawaf, CEO, Posit 

> "Plotly (2024 Databricks Customer Impact Partner of the Year)は、Databricks Appsの登場とビジネスユーザーにサービスを提供するための分析プロフェッショナルに対するイネーブルメントに拍手 👏 を送ります。Databricks Appsは、PlotlyがDash Enterpriseオファリングを通じて認知されている様々な洗練されたプロダクションレベルのデータアプリユースケースに対するPlotlyのDashオープンソースライブラリとDatabricksの活用に向けて、Databricksのユーザーがジャーニーをスタートする簡単な手段を提供します。" - Dave Gibbon, Sr. Director - Strategic Partnerships at Plotly

# Databricks Appsを使い始める

[Databricks Apps](https://www.databricks.com/product/databricks-apps)は、サポートされるリージョンのすべてのワークスペースで利用可能です。

はじめてのアプリを記述するには、**+ New**に移動し、**Apps**をクリックします。画面の指示に従ってください。お好きなソースコードエディタを用いて変更を行い、デプロイしましょう！

![](https://www.databricks.com/sites/default/files/inline-images/getstarted.png?v=1728328931)

機能の全てに関する詳細に関しては[ドキュメント](https://docs.databricks.com/ja/dev-tools/databricks-apps/index.html)をご覧ください(利用できるリージョン: [AWS](https://docs.databricks.com/ja/resources/feature-region-support.html#serverless-compute-feature-availability)、[Azure](https://learn.microsoft.com/ja-jp/azure/databricks/resources/feature-region-support#serverless-availability))。パワフルかつデータドリブンのアプリケーションを構築し、あなたの組織における新たな可能性を解放するDatabricks Appsでの構築を目にするのを楽しみにしています。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

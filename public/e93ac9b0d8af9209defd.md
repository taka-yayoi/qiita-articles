---
title: Databricks Unity CatalogにおけるAI生成ドキュメントのパブリックプレビューの発表
tags:
  - Databricks
  - UnityCatalog
private: false
updated_at: '2023-10-28T14:30:23+09:00'
id: e93ac9b0d8af9209defd
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Announcing Public Preview of AI Generated Documentation In Databricks Unity Catalog \| Databricks Blog](https://www.databricks.com/blog/announcing-public-preview-ai-generated-documentation-databricks-unity-catalog)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# 生成AIによるデータのドキュメンテーションとディスカバリーの効率化

本日、[Databricks Unity Catalog](https://www.databricks.com/jp/product/unity-catalog)におけるAI生成ドキュメントのパブリックプレビューを発表できることを嬉しく思っています。この機能はテーブルやカラムの説明文、コメントの追加を自動化することで、みなさまの組織におけるデータとAI資産のドキュメント作成、キュレーション、発券をシンプルにするために生成AIを活用します。

現在のデータドリブンの世界において、どこにデータがあるのかは情報に基づく意思決定の基盤となり、シームレスなデータの発見可能性や明確さをベースとしてチームワークにおける強固な基盤を確立します。しかし、データチームは多くの場合重要な課題に苦戦しています: 包括的なデータ記述の不在によって、文脈の理解が困難となります。この不足はユーザーがデータの潜在能力を活用する妨げとなっており、これらのギャップの橋渡しをするために簡素化されたデータの説明文の必要性を強調しています。

さらに、テーブルやカラムの適切なメタデータや説明文が存在しないことが問題を複雑にし、いくつかの課題を引き起こしています:

- **データの曖昧さ:** テーブルやカラムの目的やコンテンツに関する明確さがないことによって、ユーザーの意思決定能力の大きな妨げとなります。
- **手作業の負荷:** データの所有者は資産に対する重要な文脈、チーム間でのコラボレーションを促進するための重要な要件を記載するために、説明文やコメントを手動で追加する責任を負っています。
- **非効率的なデータ探索:** 多くの場合、ユーザーはデータから洞察を導き出すために、複雑なクエリーに依存しなければならず、貴重な時間やリソースを消費することになっています。
- **貧弱なデータ品質:** 不適切、不正確なドキュメントは、誤解、データのエラー、妥協したデータ品質を引き起こします。特にIDCによると、データアナリストはデータの準備、クレンジングに自分たちの時間の最大80%を費やしており、これは多くの場合、説明文の不足を含む不適切なデータの説明文によって引き起こされています。

# Unity CatalogにおけるAI生成ドキュメントによる効率の強化と洞察の加速

これらの課題に取り組み、データオーナーが説明文を追加するために十分な文脈を持たないケースにおいて支援を行うために、Unity Catalogではテーブルやカラムの説明文を提案するようになりました。ユーザーはこれらの提案を受け入れたり、必要に応じて修正したりすることで、アシスト的でユーザーフレンドリーな体験を確実なものとします。

## 動作原理

- **データ探索:** カタログエクスプローラに移動し、所有・管理するテーブルにアクセスすると、テーブルやカラムに対して自動生成されたメタデータが表示されます。
![](https://lh3.googleusercontent.com/EAphkGq2GceZRUnb_PXBxY9A3kJkWzKtMIlxuZmez6So-2IpKg1dSURORKIOv6K1Vjnv1zYeQqDLEcgHcvOIW6jGnhWks8PJLMPApeMFwqxQorPc1dNBtMO9_364_YWI4ewkDGNBhegSkBhbQ2WatDk)
- **ユーザーのレビューと編集:** ユーザーは生成されたメタデータをレビュー、編集、承諾することができます。このステップによって、説明文は特定のユースケースやドメイン知識と平仄を取ることになります。
![](https://lh4.googleusercontent.com/5Ky-7lXOJLhj0_MWSZX3CCW5HVbReytJ_8WMPGO06IjGNg_yHzmCKLs7EcbegGLgPD2CBHi74lMS_upXNSJ4FxnPQo_8Bsi0ukke9rFn4PQb03v6ncaKWDzpfSZQSchAgp2Kix0brvmFfceLAKbT1ZI)
- **メタデータのストレージ:** ユーザーが生成されたドキュメントを承認すると、それらはUnity Catalogに保存されます。このドキュメントは、自動生成された説明文に基づいた効率的な検索のように、様々な手段でデータの利用者を支援するために活用されます。
![](https://lh5.googleusercontent.com/mlZKIwCAjQAa5WsxPnNlG--odpnvo28o-pcUVaDuxBocEiQauZ0qx6evGkRpOsiJEgEnhspR-SP0o5tdvaL9CBeSgWuS1T-FfBId1QKqwCFZyQc0txyRhgJ6kscUDxunR2iJYBVAIp551RMtck8_xQA)

## Unity CatalogのAIドキュメンテーション活用によるメリット:

- **時間とリソースの効率性:** ドキュメント生成の自動化によって時間を節約し、データの説明文の記述に要する工数を削減します。
- **簡素化されたデータ探索:** ユーザーはテーブルやカラムのコンテンツや目的をクイックに理解することができ、複雑なクエリーを実行する必要性が低減されます。
- **強化されたデータの明確性:** 正確かつ包括的な説明文はデータの明確性を保証し、誤解を防ぎます。
- **改善されたDatabricks検索** 生成メタデータはワークスペースでのテーブル検索をサポートしており、みなさまのすべてのデータユースケースにおいて適切なデータの発見可能性を改善します。
- **ユーザーのコントロール:** ユーザーはドキュメント生成プロセスに対するコントロールを保持しており、特定の要件によりマッチするように説明文を編集、カスタマイズすることができます。

# Unity CatalogiにおけるAIガバナンス

Unity Catalogによって企業は、いかなるデータプラットフォーム、クラウドにおけるファイル、テーブル、MLモデル、ノートブック、ダッシュボードをセキュアに発見、アクセス、監視、コラボレーションできるようになり、生産性を向上するためにAIを活用しつつも、レイクハウス環境の完全なポテンシャルを解放します。このAI生成ドキュメントは我々の包括的な製品ロードマップで重要な位置を占めており、ガバナンスワークフローやオペレーションの効率性を強化するために、AIのパワーを活用することを狙いとしています。[LakehouseIQ](https://www.databricks.com/jp/blog/introducing-lakehouseiq-ai-powered-engine-uniquely-understands-your-business)や[Lakehouse Monitoring](https://www.databricks.com/product/machine-learning/lakehouse-monitoring)のような機能によって、企業はパワフルなデータインテリジェンスとモニタリング機能を入手することができます。さらに、コンテキストを解するAIアシスタントである[Databricksアシスタント](https://qiita.com/taka_yayoi/items/855e15def68150bdea55)はさらにユーザー体験を強化し、オペレーションをより直感的かつレスポンシブなものにします。Unity CatalogにおけるこのAI技術との戦略的なインテグレーションは、レイクハウスプラットフォームとネイティブにインテグレーションされる最先端のデータ&AIガバナンスソリューションに対するイノベーションと継続的な改善に対する、我々のコミットメントを強調するものです。

# 使い始める

Unity Catalogを皆様のレイクハウスの基盤として受け入れることで、皆様のすべてのデータとAIの領域に渡る柔軟でスケーラブルなガバナンス実装のパワーを解放することができます。使い始めるのはとても簡単です！お使いのワークスペースでUnity Catalogを有効化しているのであれば、カタログエクスプローラで所有・管理するテーブルに移動するだけです。詳細については、[AWS](https://docs.databricks.com/ja/data-governance/unity-catalog/create-tables.html#add-ai-generated-comments-to-a-table)、[Azure](https://learn.microsoft.com/ja-jp/azure/databricks/data-governance/unity-catalog/create-tables#--add-ai-generated-comments-to-a-table)、[GCP](https://docs.gcp.databricks.com/data-governance/unity-catalog/create-tables.html#add-ai-generated-comments-to-a-table)のUnity Catalogのガイドをご覧ください。

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricksワークスペースをナビゲートする
tags:
  - Databricks
  - Databricksチュートリアル
private: false
updated_at: '2022-06-03T17:09:28+09:00'
id: dd41cd715aca272ff5ce
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Navigate the workspace \| Databricks on AWS](https://docs.databricks.com/workspace/index.html) [2022/5/17時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Databricksワークスペースは皆様のすべてのDatabricks資産にアクセスするための環境です。ワークスペースはオブジェクト([ノートブック](https://qiita.com/taka_yayoi/items/6fc2438df3df1a775d76#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF)、[ライブラリ](https://qiita.com/taka_yayoi/items/6fc2438df3df1a775d76#%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA)、[エクスペリメント](https://qiita.com/taka_yayoi/items/ba0c7f46ff7c3dbf87bb#%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%9A%E3%83%AA%E3%83%A1%E3%83%B3%E3%83%88))を[フォルダー](https://qiita.com/taka_yayoi/items/e469dded5ee83ae42d24#%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E3%83%BC)で整理し、[データ](https://docs.databricks.com/data/index.html#data)や[クラスター](https://qiita.com/taka_yayoi/items/6fc2438df3df1a775d76#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC)や[ジョブ](https://qiita.com/taka_yayoi/items/6fc2438df3df1a775d76#%E3%82%B8%E3%83%A7%E3%83%96)などの計算資源へのアクセス手段を提供します。
![](https://docs.databricks.com/_images/landing-aws.png)

ワークスペースのUI、[Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html)、[Databricks REST API reference](https://docs.databricks.com/dev-tools/api/index.html)を用いてワークスペースを管理することができます。Databricksのドキュメントの多くはワークスペースUIを用いたタスクの実行にフォーカスしています。

# サイドバーを使う

サイドバーを用いてDatabricksの全ての資産にアクセスすることができます。サイドバーは選択したペルソナ**Data Science & Engineering**、**Machine Learning**、**SQL**に応じて中身が変わります。

:::note info
**訳者注**
ペルソナごとのメニュー項目の違いは以下の通りです。

- **Data Science & Engineering**: ワークスペースを操作する基本的な項目が表示されます。

    1. **作成** [ノートブック](https://qiita.com/taka_yayoi/items/24a897cf40bba6d9e305)、テーブル、クラスターなどをクイックに作成することができます。
    1. **ワークスペース** ワークスペース上のフォルダー、ノートブックを一覧、アクセスすることができます。ワークスペースにはユーザーごとの**ホームフォルダ**が作成され、このフォルダの中にノートブックやフォルダを作成することになります。
![Screen Shot 2022-06-02 at 18.03.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/723ae0b9-f906-3ec5-bde8-07ba5ed94644.png)

    1. **リポジトリ** Git連携機能である[Databricks Repos](https://qiita.com/taka_yayoi/items/b89f199ff0d3a4c16140)にアクセスします。
    1. **最近利用したアイテム** 最近アクセスしたノートブックが一覧表示されます。
    1. **検索** ワークスペースを[検索](https://qiita.com/taka_yayoi/items/ab21c89eca56bc101dca)できます。
    1. **データ** ワークスペースの[データベース](https://qiita.com/taka_yayoi/items/e7f6982dfbee7fc84894)にアクセスします。
    1. **クラスター** [Databricksクラスター](https://qiita.com/taka_yayoi/items/c5d99cd77fe4bfcf69f0)の一覧画面に移動します。
    1. **ワークフロー** ノートブックの処理を[定期実行](https://qiita.com/taka_yayoi/items/b3275a1983c51a8bbe1a)することができます。
    1. **Partner Connect** パートナーソリューションと連携するための[Partner Connect](https://qiita.com/taka_yayoi/items/401f3d785f8262d53ea2)にアクセスします。

- **Machine Learning**: Data Science & Engineeringのメニュー項目に以下が追加されます。

    1. **エクスペリメント** MLflowによって記録される[エクスペリメント](https://qiita.com/taka_yayoi/items/ba0c7f46ff7c3dbf87bb#%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%9A%E3%83%AA%E3%83%A1%E3%83%B3%E3%83%88)の一覧にアクセスします。
    1. **Feature Store** [特徴量ストア](https://qiita.com/taka_yayoi/items/88ddec323537febf7784)にアクセスします。
    1. **モデル** MLflowの[モデルレジストリ](https://qiita.com/taka_yayoi/items/e7a4bec6420eb7069995)にアクセスします。

- **SQL**: [Databricks SQL](https://qiita.com/taka_yayoi/items/eaf79254afd4eb620a6e)に移動します。
:::

- デフォルトでは、サイドバーは折り畳まれた状態で表示されアイコンのみが表示されます。サイドバーにカーソルを移動することで完全な状態を参照することができます。
- ペルソナを変更するには、Databricksロゴ![](https://docs.databricks.com/_images/databricks-logo.png)の下をクリックし、ペルソナを選択します。
![](https://docs.databricks.com/_images/change-persona.gif)
- 次回ログインした際に表示するペルソナを固定するには、ペルソナの隣の![](https://docs.databricks.com/_images/persona-pin.png)をクリックし、ピンを解除するには再度クリックします。
- サイドバーの下にある**メニューオプション**を使って、サイドバーのモードを**自動**(デフォルト)、**展開**、**折りたたむ**から選択します。
- 機械学習に関連するページをオープンすると、ペルソナは自動で**Machine Learning**に切り替わります。

# 別のワークスペースに切り替える

同じアカウントでアクセスできるワークスペースが複数ある場合、クイックにワークスペースを切り替えることができます。

1. Databricksワークスペースの左下の![](https://docs.databricks.com/_images/account-icon.png)をクリックします。
1. **ワークスペース**の下から切り替えたいワークスペースを選択します。
![](https://docs.databricks.com/_images/workspace-switcher.png)

# ワークスペースを検索する

ワークスペースを検索するにはサイドバーの![](https://docs.databricks.com/_images/search-icon.png)**検索**をクリックします。詳細は[ワークスペースのオブジェクトの検索](https://qiita.com/taka_yayoi/items/e469dded5ee83ae42d24#%E3%83%AF%E3%83%BC%E3%82%AF%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%81%AE%E3%82%AA%E3%83%96%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E3%81%AE%E6%A4%9C%E7%B4%A2)をご覧ください。

# ヘルプを活用する

ヘルプにアクセスするには、

1. 左下の![](https://docs.databricks.com/_images/help-icon.png)**ヘルプ**をクリックします。
![Screen Shot 2022-06-03 at 16.23.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7df19ceb-08a2-3e3b-5581-1b7f5b5c9f00.png)
1. 以下のいずれかを選択します。
    - **ヘルプセンター**: ヘルプチケットを提出するか、Databricksのドキュメント、Databricksナレッジベース、Apache Sparkドキュメント、Databricksフォーラムを検索します。
    - **リリースノート**: Databricksの[リリースノート](https://docs.databricks.com/release-notes/index.html)を参照します。
    - **ドキュメント**: Databricksの[ドキュメント](https://docs.databricks.com/)を参照します。
    - **ナレッジベース**: Databricksの[ナレッジベース](https://kb.databricks.com/)を参照します。
    - **Databricksのステータス**: リージョンごとのDatabricksのステータスを参照します。
    - **フィードバック**: Databricksの[製品フィードバック](https://docs.databricks.com/resources/ideas.html)を提供します。

# ブラウザとワークスペースオブジェクトを操作する

以下のドキュメントは、ワークスペース資産の概要、ワークスペースのフォルダー、その他のオブジェクトの操作方法、ワークスペース、その他の資産のIDの特定方法を説明しています。

- [Databricksワークスペースの資産](https://qiita.com/taka_yayoi/items/6fc2438df3df1a775d76)
- [Databricksワークスペースのオブジェクトを操作する](https://qiita.com/taka_yayoi/items/e469dded5ee83ae42d24)
- [DatabricksでワークスペースID、クラスターID、ノートブックID、モデルID、ジョブIDを取得する](https://qiita.com/taka_yayoi/items/7127cabac70dd994fcba)


### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

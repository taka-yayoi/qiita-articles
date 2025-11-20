---
title: DatabricksにおけるリバースETLでのHightouchの活用
tags:
  - Databricks
  - Hightouch
  - リバースETL
private: false
updated_at: '2023-06-02T09:31:28+09:00'
id: da2dd9b63cbc3881db2e
organization_url_name: databricks
slide: false
ignorePublish: false
---
[How to Use Hightouch for Reverse ETL With Databricks \- The Databricks Blog](https://www.databricks.com/blog/2022/04/01/using-hightouch-for-reverse-etl-with-databricks.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# ビジネスに分析を還元する

> この記事はDatabricksとHightouchの共著です。HightouchのProduct Evangelist、Luke Klineに感謝の意を表します。

あなたはDatabricksのデータレイクハウスのセットアップを完了しました。いかなる形態の分析、機械学習、人工知能、BIを実行できる集中管理された場所を手に入れたことになります。

データエンジニアはついにストリーミングユースケースの全てに取りかかれることに興奮しており、データサイエンティストは自分たちのデータサイエンスと機械学習ユースケースにフォーカスできるようになります。データエンジニアは、ビジネスを強化するために適切なデータモデルを構築するためにこの情報を活用でき、データアナリストは、瞬時にクイックなアドホッククエリーを実行できるようになったので興奮しています。

データはDatabricksに存在しており、レイクハウスにおける分析の価値を拡大するために、広告、マーケティング、サクセス、そのほかのビジネスプラットフォームのようなオペレーショナルシステムに、データを移動できるリバースETLをHightouchが実現します。Hightouchは、レイクハウスに存在するユニークな顧客データにアクセスする必要のあるビジネスチームにこれらすべての分析の価値を解放する助けになります。

Databricksからこのデータを取り出すことは非常に簡単となっています。数十の宛先(広告、マーケティング、CRM、カスタマーサクセス、ERPなど)がある可能性のあるカスタムデータパイプラインを構築する必要はありません。Hightouchは、皆様のデータが適切なフォーマットで取り込まれるようにするためのプラットフォームとプログラム的なアプローチを提供します。

Hightouchが前段、後段のシステムのAPIの変更を一貫性を持って管理するので、これらのパイプラインのメンテナンスも効率的です。さらに、Hightouchはライブのデバッグとバージョン管理を用いてデータ品質を管理する容易な方法を提供します。

もはや、内製で工数のかかるパイプラインをメンテナンスする必要はありません。[Hightouch on Databricks](http://hightouch.com/)は、ビジネスに対するアクションを行い、インパクトを即座にもたらすビジネスユーザーの程にデータを提供するリバースETLの素晴らしいソリューションです。

# ソリューション: リバースETL

[リバースETL](https://hightouch.com/blog/reverse-etl)は、変換されたデータをビジネスプロセスを実行するツールに戻すプロセスです。通常、宛先は成長、マーケティング、セールス、サポートで使用されるSaaSツールから構成されます。意思決定でダッシュボードを使うのではなく、リバースETLは皆様のデータセットを洞察を自動でアクションに変換する[オペレーショナル分析](https://hightouch.com/blog/what-is-operational-analytics)に移動することにフォーカスをシフトします。

皆様のベストなデータはDatabricksにのみ存在するので、ビジネスチームは自分たちの日々の活動を支援するために一般的な情報に頼っています。これは、セールスチームに新たなリード向けにアップデートされた製品使用量を提供したり、マーケティングチームが広告ターゲットを見直すために新たな聴衆を共有したり、カスタマーサクセスチームがどのチケットの優先度を上げるのかを支援したり、アプリで特定のイベントが起きた際にチームメンバーに通知するといったシンプルなものである場合があります。

おそらく、皆様のビジネスのどこかで役立つようなデータの例を思いつくことでしょう。リバースETLでHightouchが解決できるユースケースは多数あり、Nautoのようなテックファースト企業がなぜDatabricksをスーパーチャージするためにHightouchを活用しているのかを間も無く知ることになります。

# Hightouchでデータの同期をスタートする

:::note
Hightouchは皆様のデータを蓄積しないので、コンプライアンスを心配する必要はありません。
:::

- **ステップ1:** HightouchをDatabricksに接続します。
![](https://www.databricks.com/wp-content/uploads/2022/03/db-110-blog-img-1.jpg)
- **ステップ2:** Hightouchを宛先に接続します。
![](https://www.databricks.com/wp-content/uploads/2022/03/db-110-blog-img-2.jpg)
- **ステップ3:** データモデルを作成するか、既存の者を活用します。
![](https://www.databricks.com/wp-content/uploads/2022/03/db-110-blog-img-3.jpg)
- **ステップ4:** 主キーを選択します。
![](https://www.databricks.com/wp-content/uploads/2022/03/db-110-blog-img-4.jpg)
- **ステップ5:** syncを作成し、Databricksのカラムと最終的な宛先のフィールドをマッピングします。
![](https://www.databricks.com/wp-content/uploads/2022/03/db-110-blog-img-5.jpg)
- **ステップ6:** syncをスケジュールします。
![](https://www.databricks.com/wp-content/uploads/2022/03/db-110-blog-img-5.jpg)

# DatabricksとHightouchを使い始める

DatabricksからHightouchにどのようにデータ送信をスタートするのかの詳細については、[Databricksドキュメント](https://docs.databricks.com/integrations/reverse-etl/hightouch.html)をご覧ください。[14日のDatabricks無料トライアル](https://databricks.com/jp/try-databricks)にサインアップすることで、Databricksにおけるインテグレーションをテストすることができます。リバースETLの詳細を知りたいのであれば、[Hightouchのガイドをダウンロード](https://hightouch.com/resources/reverse-etl-whitepaper?utm_source=intercom)してください。Hightouchは無料なので、[自分でテスト](http://hightouch.com/)することや[デモを予約](https://hightouch.com/demo/)することができます。

- **データモデル:** (サブスクリプションタイプ、LTV、ARR、製品適合リード、試聴コンテンツなど)
- **製品使用量データ:** (送信メッセージ、最終ログイン、ワークスペース作成日、新規ユーザーなど)
- **イベントデータ:** (参照ページ、セッション長、ショッピングカート放置、カート内アイテムなど)


### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

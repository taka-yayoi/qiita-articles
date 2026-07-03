---
title: 個人的Data + AI Summit 2025振り返り
tags:
  - Databricks
  - DAIS2025
private: false
updated_at: '2025-06-13T13:21:28+09:00'
id: ef7e2ec293d6fdbf1bfe
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
昨年に引き続き今年も振り返ります。今年もバーチャルで1日目はレコーディング、2日目はリアルタイムで視聴しました。

https://qiita.com/taka_yayoi/items/011f213d7de8e9f4c17b

# Day 1

https://x.com/taka_aki/status/1933011681778831685

空飛ぶ車を開発している[Joby](https://www.jobyaviation.com/)では車両からの膨大なデータの分析でDatabricksを活用。

https://x.com/taka_aki/status/1933013823021326767

## Databricks Free Edition

個人的はこの発表にすごく意義があると思いました。これまでも無料のCommunity Editionはありましたが、機能やキャパシティの制限が厳しかったので。ほぼ全てのDatabricksの機能を無料で利用できるので、自分での勉強などが捗ります。

https://x.com/taka_aki/status/1933017599925006637

公式ブログ

https://www.databricks.com/blog/introducing-databricks-free-edition

早速試してみました。

https://x.com/taka_aki/status/1932954542775415118

## Lakebase

DatabricksでOLTP向けデータベースが利用できるように。

https://x.com/taka_aki/status/1933020989526585694

DBのブランチングという概念、初めて聞きましたが開発が捗りそうです。

https://x.com/taka_aki/status/1933023571556864250

公式ブログ

https://www.databricks.com/blog/announcing-lakebase-public-preview

こちらで試してみました。

https://qiita.com/taka_yayoi/items/08db713d3e80fe8537a4

## Databricks Apps

GAに(日本に早く来てください)

https://x.com/taka_aki/status/1933028253247393873

Node.jsやReactもサポート。

https://x.com/taka_aki/status/1933028846682698011

## Agent Bricks

AI Builderと呼ばれていたベータがAgent Bricksという名前に変更されました。

https://x.com/taka_aki/status/1933028846682698011

知識アシスタントはこちらで試してみました。

https://qiita.com/taka_yayoi/items/5aaef73edfc5d405c26b

## MLflow 3.0

これまでベータだったMLflow 3.0もGAに。

https://x.com/taka_aki/status/1933042836460745036

こちらでウォークスルーしています。GAになったので後でもう一度試してみます。

https://qiita.com/taka_yayoi/items/8e66db25d99b4de5c85b

https://qiita.com/taka_yayoi/items/1d5cce6164ab44a643cd

https://qiita.com/taka_yayoi/items/c10df7550e3d9ddf5e45

https://qiita.com/taka_yayoi/items/651ad6078a9c338cd482

## サーバレスGPUコンピュート

生成AIワークロードが捗ります。

https://x.com/taka_aki/status/1933042959454466505

こちらで試しています。

https://qiita.com/taka_yayoi/items/6bb814a1970ce376e5f4

## MCP on Databricks

マルチエージェント時代を見越しているかのよう。

https://x.com/taka_aki/status/1933043191370104948

こちらでも試しています。

https://qiita.com/taka_yayoi/items/96de6b6f9ba8b93015b5

# Day 2

Microsoft SATYA CEOとの対談レコーディングからスタート。

https://x.com/taka_aki/status/1933196586139750772

ちなみに、Aliの背後にはLearning Sparkが。[Apache Spark徹底入門](https://www.amazon.co.jp/Apache-Spark%E5%BE%B9%E5%BA%95%E5%85%A5%E9%96%80-Jules-S-Damji-ebook/dp/B0CVQ84T6J/)として翻訳しました。

https://x.com/taka_aki/status/1933197662075133976

## Unity Catalog

公式ブログ

https://www.databricks.com/blog/whats-new-databricks-unity-catalog-data-ai-summit-2025

Icebergマネージドテーブル

https://x.com/taka_aki/status/1933201760480579971

デモの中ではABAC(属性ベースのアクセスコントロール)もカバー。

https://x.com/taka_aki/status/1933204130233004043

ABACはこちらで試しています。

https://qiita.com/taka_yayoi/items/86c2d289eb79f52aeec5

UCのメトリクスビューがGA

https://x.com/taka_aki/status/1933205358266494998

分析の切り口であるディメンションやメジャーを一元管理できます。こちらでウォークスルーしています。

https://qiita.com/taka_yayoi/items/0b57f38c05b2c4720ed1

ディスカバービュー。アセットをより発見しやすく。

https://x.com/taka_aki/status/1933205970781626376

デモ環境では、カタログエクスプローラのサンプルデータタブで直接Genieに質問できるようになっていました。これは嬉しい。

https://x.com/taka_aki/status/1933206746392375549

## Spark宣言型パイプライン

DLTで培われた宣言型構文をSparkでも使えるように。つまり、DLT(現Lakeflow宣言型パイプライン)のオーブンソース化。

https://x.com/taka_aki/status/1933209702831460379

https://x.com/taka_aki/status/1933210722240197078

https://x.com/taka_aki/status/1933211397636436381

## Lakeflow

オーケストレーションを司るLakeflow Jobsの新機能も目白押し。

https://x.com/taka_aki/status/1933212744981098511

https://x.com/taka_aki/status/1933212912711315709

Lakeflow宣言型パイプラインのインタフェースもどんどん改善。

https://x.com/taka_aki/status/1933213639915549019

そして、Lakeflow Designer！ノーコードでETLパイプラインを開発可能に。

https://x.com/taka_aki/status/1933214987302154464

ノーコードと言ってもそこにはAIアシスタントが。自然言語でパイプラインが作られていくこの未来感。

https://x.com/taka_aki/status/1933215673871982649

https://x.com/taka_aki/status/1933216101179273660

さらにはデータ構造のスクリーンショットから処理を自動生成。

https://x.com/taka_aki/status/1933216432235688203

ノーコードと言っても、Databricksの場合は背後デコードを持っているので管理もきちんとできます。

https://x.com/taka_aki/status/1933216875653271571

## Databricks SQL

SQLからさらにLLMを活用できるように。

https://x.com/taka_aki/status/1933219730594447786

## Lakebridge

Bladebridgeをベースとした、オープン、無料でAIアシストありの移行ソリューション。

https://x.com/taka_aki/status/1933220629941268895

https://x.com/taka_aki/status/1933221052852940968

## Gemini

Google Cloudとのパートナーシップの発表、そしてDatabricksでGeminiが利用できるように。

https://x.com/taka_aki/status/1933221990762230258

## AI/BI

ダッシュボードから予測機能をが利用可能に。

https://x.com/taka_aki/status/1933224910866001992

ダッシュボードで気になる箇所からコンテキストメニューを呼び出し、直接Genieに問い合わせ。これは嬉しい。

https://x.com/taka_aki/status/1933225212872696232

そして、GenieにDeep Researchモードが！

https://x.com/taka_aki/status/1933225505949692318

[予想されている方](https://qiita.com/isanakamishiro2/items/2f4b35930ffea8c7e2b3#%E3%81%BE%E3%81%A8%E3%82%81)がいらっしゃいました。すごい。

https://x.com/isanakamishiro2/status/1933225537918677185

Genieの知識抽出、利用パターンなどから知識を獲得。

https://x.com/taka_aki/status/1933226982470480204

https://x.com/taka_aki/status/1933227630343696756

## Databricks One

ビジネスユーザー向けに効率的なUIを提供。

https://x.com/taka_aki/status/1933227923869430182

# まとめ

5回目の視聴ですが、生成AIが出現してからの2、3年での進化が凄まじいです。

- Community EditionがFree Editionへと生まれ変わり、「Databricksを触ってみたい」という方にとっての障壁を大幅に引き下げ
- MLflow 3.0、MCPサーバーやAgent Bricksの提供によって、マルチエージェント時代に備える
- Lakeflowによるデータエンジニアリングの効率化、Lakeflow DesignerによってノーコードのETL開発と生成AIを活用したデータインテリジェンスエンジニアリングを
- Unity Catalogの発表は2021年、それから1年ほどしてGAとなり、リネージやABACなどガバナンスを強化するための機能がどんどん投入されている
- AI/BI、Apps、そしてDatabricks Oneによって、ビジネスユーザーもDatabricksをより活用できるように

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

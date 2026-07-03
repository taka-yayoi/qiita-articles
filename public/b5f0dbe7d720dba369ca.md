---
title: Databricks無料版で始めるGenie入門 〜自然言語でデータ分析を体験しよう〜
tags:
  - Databricks
  - Databricks_AI_BI
  - Databricks_Free_Edition
private: false
updated_at: '2025-12-12T14:24:02+09:00'
id: b5f0dbe7d720dba369ca
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

「SQLを書かずに、データと会話できたら...」

そんな願いを叶えてくれるのが **Databricks Genie** です。自然言語で質問するだけで、SQL生成から集計、可視化までを自動でやってくれる「対話型BI」機能です。

https://www.databricks.com/jp/product/business-intelligence/ai-bi-genie

本記事では、Databricks Free Edition（無料版）を使って、Genieの基本操作から最新機能の **Genie Research Agent** まで、段階的に体験できるサンプルシナリオを紹介します。

:::note info
この記事は [JEDAI Databricks無料版で始めるGenieもくもく会](https://jedai.connpass.com/event/377689/)（2025年12月23日開催）向けに作成しました。
:::

当日の説明資料はこちら。

<script defer class="speakerdeck-embed" data-id="7367fd7848e44c078813674ab01fa4bd" data-ratio="1.775925925925926" src="//speakerdeck.com/assets/embed.js"></script>

# 対象読者

- Databricksをこれから触ってみたい方
- SQLは苦手だけどデータ分析に興味がある方
- 生成AIを活用したBI/分析ツールを試してみたい方

# 事前準備

# Databricks Free Editionのセットアップ

まだアカウントをお持ちでない方は、以下から無料で登録できます。リンク先で**無料版を入手**を選択ください。

https://www.databricks.com/jp/try-databricks

![Screenshot 2025-12-12 at 13.27.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/506dc421-373a-44f9-b96a-b11a0875a497.png)


# 使用するサンプルデータ

Databricks Free Editionには、あらかじめ **samples.tpch** というサンプルデータセットが用意されています。これはEC（電子商取引）の注文データを模したもので、以下のようなテーブルが含まれています。

| テーブル名 | 内容 |
|-----------|------|
| `customer` | 顧客情報 |
| `orders` | 注文情報 |
| `lineitem` | 注文明細 |
| `part` | 商品情報 |
| `supplier` | サプライヤー情報 |
| `nation` | 国情報 |
| `region` | 地域情報 |

# Genieスペースの作成

Genieを使うには、まず「Genieスペース」を作成します。

1. 左サイドバーから「Genie」を選択
![Screenshot 2025-12-12 at 13.29.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/266f1d5e-cb10-43c5-bc97-c73a0a47b531.png)
2. 「+New」をクリック
3. 以下を設定：
   - データの接続で`samples.tpch` 配下のテーブルを選択して、**作成**をクリック。
![Screenshot 2025-12-12 at 13.30.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5fd488dd-b0b4-4102-a0fb-7c4562a14249.png)

   - 名前：任意（例：`TPCH分析`）
 ![Screenshot 2025-12-12 at 13.31.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f65a8643-ed7b-4240-ba37-8ace0c695193.png)

# Step 1: Genieの基本操作（15分）

まずはシンプルな質問から始めて、Genieの動作を確認しましょう。

# 1-1. カウント系の質問

```
顧客は全部で何人いますか？
```

![Screenshot 2025-12-12 at 13.32.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/47340828-5e36-43d0-a592-5c639a8de26a.png)

Genieが自動でSQLを生成し、結果を返してくれます。生成されたSQLも確認できるので、学習にも役立ちます。
![Screenshot 2025-12-12 at 13.32.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fc704bfe-d1d6-4847-afc7-4e023e964e65.png)
![Screenshot 2025-12-12 at 13.33.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2a63e38e-c3e7-4275-b563-ce08dd001739.png)


# 1-2. ランキング・ソート

```
注文金額が多い上位10件の注文を見せて
```

![Screenshot 2025-12-12 at 13.34.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/533ccde8-79c4-4e4f-84cf-a777486f92df.png)


# 1-3. グループ集計

```
国別の顧客数を教えて
```

![Screenshot 2025-12-12 at 13.34.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3007469e-eff0-4f4d-9240-3b015b68daac.png)


# 1-4. 可視化リクエスト

```
月別の売上推移を折れ線グラフで見せて
```

![Screenshot 2025-12-12 at 13.35.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e73c1b64-29f0-4f32-ab80-88c925908225.png)

:::note info
**チェックポイント**
- SQLが自動生成されることを確認できましたか？
- 結果がテーブル/グラフで表示されましたか？
- 日本語で質問できることを実感できましたか？
:::

# Step 2: より複雑な分析（20分）

基本操作に慣れたら、少し踏み込んだ質問にチャレンジしてみましょう。

# 2-1. フィルタリング + 集計

```
アジア地域で最も売上の高い製品カテゴリは？
```

![Screenshot 2025-12-12 at 13.36.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/477ae15a-ae3e-4634-b8bb-89bfcb490704.png)


複数テーブル（`region`, `nation`, `customer`, `orders`, `lineitem`, `part`）を自動でJOINして回答してくれます。

# 2-2. 計算フィールドの生成

```
注文から出荷までの平均日数を優先度別に比較して
```

![Screenshot 2025-12-12 at 13.37.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bd8561e6-ccd7-400e-ac72-6de3bc61da90.png)


日付の差分計算も自然言語で指示できます。

# 2-3. 比率・割合の算出

```
リピート購入している顧客の割合を教えて
```

![Screenshot 2025-12-12 at 13.38.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/526f02d2-27a2-4474-bc69-ca1e1e75a6bc.png)

# 2-4. 時系列比較

```
売上が前月比で最も成長した月はいつ？
```

![Screenshot 2025-12-12 at 13.39.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/eacf3f23-b52b-4bab-ada0-c957485cd143.png)


:::note warn
**うまくいかないときは**
- 質問を具体的にしてみる（期間、対象を明示）
- 一度に複数のことを聞かず、分割して質問する
- テーブル名やカラム名をヒントとして含める
:::

# Step 3: Research Agentで深掘り分析（25分）

ここからが本番です！**Genie Research Agent** は、単なる集計ではなく「なぜ？」「どうすれば？」までをAIが自動でリサーチしてくれる機能です。

![Screenshot 2025-12-12 at 13.39.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/364c15e8-c669-4375-90ab-1579a39dc0bb.png)


仮説生成 → 検証クエリ実行 → 結論導出 という流れを自動で行います。

# 3-1. 原因分析

```
売上が低迷している地域があれば、その原因を分析して
```

![Screenshot 2025-12-12 at 13.41.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c5f822a9-3480-421f-869e-bfd16621b010.png)
![Screenshot 2025-12-12 at 13.42.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b6d203a4-b51f-4b44-b3da-3eb198d33a78.png)


Research Agentが複数の仮説を立て、それぞれを検証するクエリを自動実行し、結論を導き出します。

# 3-2. 顧客セグメント分析

```
高額注文をする顧客にはどんな特徴がある？
```

![Screenshot 2025-12-12 at 13.43.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d066adbc-52ae-4fd8-be60-ae1958916628.png)


# 3-3. 問題解決型の質問

```
出荷遅延が発生しやすいパターンを特定して、改善策を提案して
```

![Screenshot 2025-12-12 at 13.45.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/be81af11-b417-417b-b2f2-f05c8c39fd64.png)


# 3-4. 予測・提案型の質問

```
来四半期の売上予測と、成長のための施策を提案して
```

![Screenshot 2025-12-12 at 13.49.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c9a162fb-1715-4efe-bf14-360cec153bf2.png)
![Screenshot 2025-12-12 at 13.50.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f463d253-e3b5-4b35-8946-499dd5832a2e.png)


:::note info
**Research Agentの観察ポイント**
- どんな仮説が生成されるか
- 検証のために何種類のクエリが実行されるか
- 結論の導出プロセスはどうなっているか
- 推奨アクションは具体的か
:::

# 自由課題

もっと試してみたい方は、以下のお題にチャレンジしてみてください。

| 難易度 | お題 |
|--------|------|
| ⭐ | 売れ筋商品トップ5をグラフで表示 |
| ⭐⭐ | 四半期ごとの売上トレンドを前年と比較 |
| ⭐⭐⭐ | 顧客を購買行動でセグメント分けして各グループの特徴を説明 |
| ⭐⭐⭐⭐ | 在庫最適化のための発注タイミングを提案 |

# オリジナルデータで試す

自分のデータをUnity Catalogに登録すれば、同じようにGenieで分析できます。CSVファイルのアップロードも可能です。

# 従来のBIツールとの違い

| 観点 | 従来のBI | Genie |
|------|----------|-------|
| 操作方法 | ドラッグ&ドロップ、SQL | 自然言語 |
| 学習コスト | ツール固有の操作を習得 | 日本語で質問するだけ |
| 柔軟性 | 事前定義されたダッシュボード | その場で自由に質問 |
| 深掘り分析 | 手動で仮説検証 | Research Agentが自動化 |

# まとめ

Databricks Genieを使うことで、以下のような体験ができました。

1. **基本操作**: 自然言語でSQL生成・集計・可視化
2. **複雑な分析**: 複数テーブルのJOIN、計算フィールド、時系列比較
3. **Research Agent**: 仮説生成から検証、結論導出までの自動化

「BIを操作する」から「データに質問する」へ。この体験の変化をぜひ実感してみてください。

# 参考リンク

- [Databricks Free Edition](https://www.databricks.com/jp/try-databricks)
- [Genie公式ドキュメント](https://docs.databricks.com/ja/genie/index.html)
- [Genie spacesのResearch Agent \| Databricks on AWS](https://docs.databricks.com/aws/ja/genie/research-agent)
- [JEDAI - Japan Enduser Group for Databricks](https://jedai.connpass.com/)

---



### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricks AI BuilderによるノーコードでのRAGの構築
tags:
  - Databricks
  - rag
  - AI_Builder
private: false
updated_at: '2025-05-30T08:20:51+09:00'
id: 5aaef73edfc5d405c26b
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらの機能です。

https://docs.databricks.com/aws/ja/generative-ai/ai-builder/knowledge-assistant

:::note info
**注意**
執筆時点では[ベータ版](https://docs.databricks.com/aws/ja/release-notes/release-types)です。
:::


# AI Builderとは

**AI Builder**は、Databricks上で**ノーコード/ローコード**により**生成AIアプリを簡単に構築できる開発フレームワーク**です。

https://docs.databricks.com/aws/ja/generative-ai/ai-builder/

#### 🔧 AI Builderの動作メカニズム

```mermaid
graph TD
    A[問題・ユースケースを指定] --> B[データを提供]
    B --> C[AI Builderが自動処理]
    C --> D[AIモデルの自動選択・ファインチューニング]
    C --> E[システム自動最適化]
    C --> F[性能評価・比較]
    D --> G[最適なAIシステム完成]
    E --> G
    F --> G
    G --> H[継続的改善・最適化]
```

問題に合わせた生成AIアプリをノーコードで構築することができます。現時点では、以下の問題タイプをサポートしています。

#### 📊 現在サポートされているユースケース

| ユースケース | 説明 | 適用例 |
|-------------|------|--------|
| **📄 ドキュメント構造化** | ラベルなしテキストを構造化テーブルに変換 | 契約書、レポートの自動データ化 |
| **✍️ カスタムテキスト生成** | 要約、分類、テキスト変換タスク | 文書要約、カテゴリ分類 |
| **💬 チャットボット構築** | ドキュメントベースの高品質Q&Aシステム | 社内FAQ、顧客サポート |

今回、3つ目の**チャットボット構築**が追加されました。

# ナレッジアシスタントの構築

[マニュアル](https://docs.databricks.com/aws/ja/generative-ai/ai-builder/knowledge-assistant)に従って構築してみます。

事前にRAGで使用するドキュメントを準備します。ボリュームにtxt、pdf、md、ppt/pptx、doc/docxを格納しておくか、ベクトル検索インデックスを準備しておきます。今回はボリュームにWordファイルをアップロードしておきます。これらは、[データブリックス クイックスタートガイド](https://www.amazon.co.jp/%E3%83%87%E3%83%BC%E3%82%BF%E3%83%96%E3%83%AA%E3%83%83%E3%82%AF%E3%82%B9-%E3%82%AF%E3%82%A4%E3%83%83%E3%82%AF%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%88%E3%82%AC%E3%82%A4%E3%83%89-%E3%83%87%E3%83%BC%E3%82%BF%E3%83%96%E3%83%AA%E3%83%83%E3%82%AF%E3%82%B9%E3%83%BB%E3%82%B8%E3%83%A3%E3%83%91%E3%83%B3/dp/B09TWXN35R)の原稿です。


![Screenshot 2025-05-30 at 6.49.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2d10c2fc-6e3a-4d98-b800-1bf347a0e797.png)

サイドメニューの**AI Builder**にアクセスすると、**ナレッジアシスタント**が追加されていますのでクリックします。

![Screenshot 2025-05-30 at 6.45.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3088e2cc-ace6-4c02-ac38-63df189092a1.png)

![Screenshot 2025-05-30 at 8.04.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/77f713c8-973b-4fc7-89bd-9b3fff7f573e.png)


名前や説明文、アシスタントの構築に伴って生成されるテーブルやボリュームを格納するスキーマを指定し、**ナレッジソース**で、RAGで使用するドキュメントを指定します。**UCファイル**を選択し、ドキュメントを保存したボリュームパスを指定します。

![Screenshot 2025-05-30 at 6.50.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e0c7900d-e13e-4165-b5da-3d6780e44f7a.png)

エージェントの指示を指定したら、**エージェントを作成**をクリックします。

![Screenshot 2025-05-30 at 6.51.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a247c76b-4218-43a4-ac9e-c4373ad14128.png)

構築がスタートします。

![Screenshot 2025-05-30 at 6.52.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/089338cf-b23f-405e-bbb6-4a9d487f59f1.png)

数分すると、エンドポイントやナレッジソースの準備が整います。

![Screenshot 2025-05-30 at 7.38.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7cecfb47-964d-42ee-acca-ce614a013862.png)

**Playgroundで試す**をクリックします。問い合わせしてみます。

![Screenshot 2025-05-30 at 7.38.27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ac26653e-8e49-4903-a8b7-dcf899c8e140.png)

動きました！きちんと情報ソースも表示されています。

![Screenshot 2025-05-30 at 7.39.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a6407890-d166-4496-b2fd-2f98b2ae7b3d.png)
![Screenshot 2025-05-30 at 7.40.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d6733806-220f-4776-a061-838136713557.png)

トレースも確認できます。

![Screenshot 2025-05-30 at 7.40.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9fe386ee-0e51-44a7-9209-86a29d51501d.png)

# 生成物

画面からわかるようにモデルサービングエンドポイントが作成されています。

![Screenshot 2025-05-30 at 7.49.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/16c54725-aaf1-4724-8cda-71f3bc8535b3.png)

また、エージェント設定時に指定したスキーマにアクセスすると、生のWordファイルからベクトル検索インデックスが作成されていることがわかります。

![Screenshot 2025-05-30 at 7.45.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/86a5a2af-8e44-4c21-9d3f-3078c8cb35c4.png)

パースやチャンキングもされています。

![Screenshot 2025-05-30 at 7.44.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1a5a44c3-fdbb-45de-9b40-15c060bbf19e.png)

![Screenshot 2025-05-30 at 7.43.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8b2f38c3-e62a-4f40-819d-6efd6491e63c.png)

リネージはこのようになっています。

![Screenshot 2025-05-30 at 7.45.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/eac1d47b-be0a-4285-b51c-9803529633c7.png)

お手軽にRAGを構築できるのはいいですね。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

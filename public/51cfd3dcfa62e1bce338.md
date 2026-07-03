---
title: Databricks「State of AI Agents 2026」レポート解説
tags:
  - Databricks
  - AIエージェント
private: false
updated_at: '2026-01-31T09:58:14+09:00'
id: 51cfd3dcfa62e1bce338
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

Databricksが2026年版の「State of AI Agents」レポートを公開しました。本記事では、このレポートの主要な発見を日本の読者向けに紹介します。

本レポートは、Databricks Data Intelligence Platformを利用する20,000以上の組織(Fortune 500の60%以上を含む)から収集された匿名化データに基づいています。データ期間は主に2024年11月から2025年10月までの1年間です。

> 原典: [Databricks State of AI Agents 2026](https://www.databricks.com/resources/ebook/state-of-ai-agents)

# 主要な発見(サマリー)

レポートが示す4つの重要なトレンドは以下の通りです。

**マルチエージェントシステムが新たな企業オペレーティングモデルに**: 企業は単一のチャットボットから、ドメイン知識に基づくマルチエージェントシステムへ移行中。利用は4ヶ月で327%成長。

**AIエージェントがデータベース運用の中核に**: データベースの80%がAIエージェントによって作成され、テスト・開発環境では97%に達する。これが「Lakebase」という新しいデータベースカテゴリの需要を牽引。

**AIが業界横断で重要なワークフローに組み込まれる**: GenAIユースケースの40%が顧客体験に関連。78%の企業が2つ以上のLLMモデルファミリーを使用するマルチモデル戦略を採用。

**AI評価とガバナンスが本番稼働の基盤**: 評価ツールを使用する企業は約6倍多くのAIプロジェクトを本番化。AIガバナンスを使用する企業は12倍以上のプロジェクトを本番化。

# エンタープライズAIエージェント

## Agent Bricksの利用動向

[Agent Bricks](https://docs.databricks.com/ja/generative-ai/agent-bricks/index.html)は、企業がAIエージェントを構築するためのDatabricksのツールセットです。4種類のエージェントタイプが提供されています。

| エージェントタイプ | 説明 |
|---|---|
| [Custom LLMs](https://docs.databricks.com/ja/generative-ai/agent-bricks/custom-llm-agent-authoring.html) | ドメイン固有タスク向けのテキスト生成 |
| [Supervisor Agent](https://docs.databricks.com/ja/generative-ai/agent-bricks/multi-agent-systems.html) | 複数のエージェントとツールを協調させて複雑なタスクを実行 |
| [Knowledge Assistant](https://docs.databricks.com/ja/generative-ai/agent-bricks/unstructured-knowledge-agent-authoring.html) | 企業ドキュメントでカスタムトレーニングされたQ&Aチャットボット |
| [Information Extraction](https://docs.databricks.com/ja/generative-ai/agent-bricks/info-extraction-agent-authoring.html) | ラベルなしテキストドキュメントを構造化テーブルに変換 |


![Screenshot 2026-01-31 at 9.49.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2b3bdec0-916b-4a7e-9f69-56194170e193.png)
**[図1: Agent Bricksの利用推移(2025年6月〜10月)]**

2025年7月にSupervisor Agentがローンチされて以降、急速に最も利用されるエージェントタイプとなり、2025年10月時点で全Agent Bricks利用の37%を占めています。Information Extractionは31%で2位につけています。

## マルチエージェントシステムの台頭

Supervisor Agentの327%成長は、企業が単一のチャットボットから複数エージェントが協調するシステムへ移行していることを示しています。

例えば、金融サービス企業では、意図検出、ドキュメント取得、コンプライアンスチェックを担当する複数エージェントからなるシステムを構築し、クライアントへパーソナライズされた回答を提供しています。

![Screenshot 2026-01-31 at 9.51.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9b223d88-6827-437c-877e-5eb553d5ec66.png)
**[図2: 業界別Supervisor Agent利用状況(企業あたり平均エージェント数)]**

テック企業が他業界の約4倍のマルチエージェントシステムを構築しており、ビジネス課題を専門化されたAIエージェントで解決可能な問題に分解する能力が高いことを示しています。

## 主要なAIユースケース

レポートが特定した上位15のAIユースケースは、「必要だが定型的な日常業務の自動化」に集中しています。

![Screenshot 2026-01-31 at 9.51.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4963947c-4994-458f-a06c-69e197c637c8.png)
**[図3: 上位AIユースケース]**

上位ユースケースには以下が含まれます:

- Market Intelligence(市場インテリジェンス)
- Predictive Maintenance(予知保全)
- Customer Support Inquiry Classification & Routing(カスタマーサポート問い合わせ分類・ルーティング)
- Customer Advocacy(顧客擁護)
- Claim Processing(請求処理)
- Customer Onboarding(顧客オンボーディング)
- Anti-Money Laundering(マネーロンダリング対策)
- Medical Literature Synthesis(医学文献統合)

[Deloitte Digitalの調査](https://www.deloittedigital.com/us/en/offerings/customer-led-marketing/digital-customer/digital-cx-survey.html)によると、カスタマーエクスペリエンスリーダーの10人中9人がAIには顧客体験を改善する可能性があると確信しています。本レポートのデータは、企業が実際にその意図でAIを活用していることを示しており、**40%のユースケースが顧客体験に関連**しています。

## 業界別・地域別の傾向

![Screenshot 2026-01-31 at 9.52.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a2b93672-6646-4cbe-845e-b73b52b66bf6.png)
**[図4: 業界別・地域別トップAIユースケース]**

業界ごとに特化したユースケースが見られます:

| 業界 | トップユースケース | 割合 |
|---|---|---|
| 通信・メディア・エンタメ | Customer Advocacy | 14% |
| エネルギー・公益 | Predictive Maintenance | 33% |
| 金融サービス | Market Intelligence | 19% |
| ヘルスケア・ライフサイエンス | Medical Literature Synthesis | 23% |
| 製造・自動車 | Predictive Maintenance | 35% |
| 小売・消費財 | Market Intelligence | 14% |
| テクノロジー | Market Intelligence | 16% |

地域別では、アジア太平洋、北米、EMEA(欧州・中東・アフリカ)でMarket Intelligenceがトップである一方、ラテンアメリカではLoan Origination(融資組成)が10%でトップとなっています。

# AIエージェントインフラストラクチャ

## AIエージェントがデータベース運用を支配

[Neon](https://neon.tech/)(Databricksが買収したサーバーレスPostgresデータベース、[Lakebase](https://www.databricks.com/product/lakebase)のコア技術)のテレメトリデータは、AIエージェントによるデータベース運用の劇的な変化を示しています。

![Screenshot 2026-01-31 at 9.53.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/489bb418-2d21-4279-8c0f-4159f6d3b1f9.png)
**[図5: AIエージェントによるNeonコンポーネント作成割合の推移]**

| 指標 | 2023年10月 | 2024年10月 | 2025年10月 |
|---|---|---|---|
| AIエージェントによるデータベース作成 | 0.1% | 0.1% | **80%** |
| AIエージェントによるブランチ作成 | - | 18% | **97%** |

データベースブランチとは、完全に機能しバージョン管理された、データベースの分離されたバリアントです。エージェントはテスト、実験、開発のためにこれらの一時的な環境を素早く作成し、重量級のプロビジョニングなしに以前の状態に巻き戻すこともできます。

## AI時代のデータベース要件

従来のOLTP(オンライントランザクション処理)データベースは、予測可能なトランザクション、まれなスキーマ変更、手動プロビジョニングという人間中心のワークフローを前提に設計されていました。

しかし、エージェントAIの時代には:

- エージェントが連続的かつ高頻度の読み書きパターンを生成
- プログラムによる環境の作成・削除が必要
- マルチステップ推論ループの一部として複雑な読み取り集約クエリを実行

これらの要件に対応するため、**Lakebase**のような新しいカテゴリのオペレーショナルデータベースが登場しています。LakebaseはAIエージェントがミリ秒単位でPostgresトランザクショナルデータベースを作成、ブランチ、オーケストレーションすることを可能にします。

## 市民AIアプリ開発者の台頭

「バイブコーディング」(自然言語で欲しいものを説明し、AIにコードを生成させる手法)の台頭により、深い技術的専門知識なしでも動作するプロトタイプを構築できるようになりました。

![Screenshot 2026-01-31 at 9.54.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/96a99d54-157c-43d7-871e-feec50d89ceb.png)
**[図6: Databricks Apps作成数の推移]**

[Databricks Apps](https://docs.databricks.com/ja/dev-tools/databricks-apps/index.html)のパブリックプレビュー以降、50,000以上のデータ・AIアプリが作成され、過去6ヶ月で250%の成長率を記録しています。

[Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-04-23-gartner-predicts-40-percent-of-new-apps-to-be-vibe-coded-by-2028)は2028年までに、企業がバイブコーディング技術とツールを使用して新規本番ソフトウェアの40%を作成すると予測しています。

# エージェントエコシステム

## マルチモデル戦略の普及

![Screenshot 2026-01-31 at 9.54.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/52fa9c52-7591-48b9-b29b-dc2e07604a9c.png)
**[図7: 企業が使用するLLMモデルファミリー数の推移]**

2025年10月時点で、**78%の企業が2つ以上のLLMモデルファミリー**(GPT、Claude、Llama、Gemini、Qwenなど)を使用しています。

| 使用モデルファミリー数 | 2025年5-7月 | 2025年8-10月 |
|---|---|---|
| 3つ以上 | 36% | **59%** |
| 2つ | 25% | 19% |
| 1つ | 39% | 22% |

3つ以上のモデルファミリーを使用する企業の割合は、わずか数ヶ月で36%から59%へ急増しました。

複数モデル戦略のメリット:
- ユースケースに最適なモデルを選択可能
- 特定ベンダーへのロックインを回避
- 単一エージェントシステム内で複数モデルを組み合わせ可能

Databricksでは[Mosaic AI Model Serving](https://docs.databricks.com/ja/machine-learning/model-serving/index.html)を通じて、外部モデル(OpenAI、Anthropic、Google、Amazonなど)とオープンソースモデルの両方を統一的に利用できます。

<!-- グラフ挿入: Number of LLM Model Families Used per Company, by Industry (p.21) -->
**[図8: 業界別マルチモデル採用状況]**

小売業界が最も積極的で、83%の企業が2つ以上のモデルファミリーを使用しています。タスクに応じてパフォーマンスとコストのバランスを取る戦略が背景にあります。

## リアルタイム推論が主流

![Screenshot 2026-01-31 at 9.55.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3bc8702a-0f8f-4572-9c2f-6bef303d961b.png)
**[図9: バッチ処理 vs リアルタイム推論の割合]**

全リクエストの**96%がリアルタイムで処理**されています。これは、コパイロット、カスタマーサポートアシスタント、パーソナライゼーションなどのインタラクティブなAI体験が主流であることを示しています。

地域別では:
- EMEA: リアルタイム97%
- 北米: リアルタイム84%
- アジア太平洋: リアルタイム82%
- ラテンアメリカ: リアルタイム77%

# AIの本番稼働

## ガバナンスと評価が成功の鍵

[MIT NANDAの2025年レポート](https://www.stradegy.ai/p/the-numbers-behind-ai-pilots-that)によると、生成AIパイロットの95%が本番化に失敗しています。では、AIプロジェクトを本番稼働させる鍵は何でしょうか?

![Screenshot 2026-01-31 at 9.56.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2919489b-eccb-464c-b7a0-6603b619a869.png)
**[図10: Databricks AI製品の利用推移]**

**AIガバナンスへの投資が7倍に急増**: [AI Gateway](https://docs.databricks.com/ja/generative-ai/ai-gateway/index.html)(DatabricksのAIガバナンスソリューション)の利用は、2025年1月から9ヶ月で7倍に成長しました。

統合ガバナンスは以下を実現します:
- AIの開発がビジネス目標に沿っていることを確認
- セキュリティおよび法的義務を遵守
- 規制リスクを考慮
- データの使用方法を定義し、ガードレールとレート制限を設定

[Economist Impactの2024年グローバル調査](https://impact.economist.com/perspectives/technology-innovation/forging-path-safe-and-trustworthy-ai)によると、回答者の40%が自社のAIガバナンスプログラムはAI資産とユースケースの安全性とコンプライアンスを確保するには不十分だと考えています。

## 本番化への影響

レポートの分析結果は明確です:

| 要因 | 本番化プロジェクト数への影響 |
|---|---|
| AIガバナンスを積極的に使用 | **12倍**多くのプロジェクトを本番化 |
| AI評価ツールを積極的に使用 | **約6倍**多くのプロジェクトを本番化 |

[Mosaic AI Agent Evaluation](https://docs.databricks.com/ja/generative-ai/agent-evaluation/index.html)は、AIモデルの品質と信頼性を体系的に測定、テスト、改善するフレームワークです。一般的なベンチマークを超えて、企業のデータと目標タスクに特化したカスタムベンチマークを作成します。

評価とガバナンスの関係:
- **ガバナンス**: エージェントのガードレールとコントロールパネルを提供
- **評価**: エージェントの動作をライフサイクル全体で監視・測定し、ガバナンスがリアルタイムで適応することを可能にする

[MIT Technology Review Insightsの調査](https://www.technologyreview.com/2024/10/28/1106320/ai-agents-are-here-will-enterprises-get-agent-ready-in-time/)によると、測定可能なビジネス成果の提供という点で自社のAIパフォーマンスを高く評価している回答者はわずか2%でした。ドメイン固有の評価は、知識と意思決定が企業データに基づいていることを検証し、チームが評価指標をビジネスKPI(CSAT、ハンドル時間、収益リフトなど)に結びつけることを可能にします。

# 結論

レポートは、エンタープライズAIの成功に向けた3つの実践を示しています:

1. **適切なモデル/マルチエージェントシステムの選択**: 特定の問題を解決するために最適なモデルやエージェントシステムを選ぶ

2. **大量の定型業務へのAI活用**: 高ボリュームで単調なタスクをAIでサポート

3. **統合ガバナンスと評価ツールへの投資**: AIを本番稼働させる主要なドライバーであることが証明されている

課題は「正しいモデルやエージェントユースケースを選ぶこと」ではなく、「エンタープライズコンテキストを持つエージェントを効果的に使用して、高品質で正確な出力を生成すること」へとシフトしています。

# 参考情報

**原典**
- [State of AI Agents 2026 (Databricks)](https://www.databricks.com/resources/ebook/state-of-ai-agents)

**Databricks製品ドキュメント**
- [Agent Bricks](https://docs.databricks.com/ja/generative-ai/agent-bricks/index.html)
- [Mosaic AI Agent Evaluation](https://docs.databricks.com/ja/generative-ai/agent-evaluation/index.html)
- [AI Gateway](https://docs.databricks.com/ja/generative-ai/ai-gateway/index.html)
- [Mosaic AI Model Serving](https://docs.databricks.com/ja/machine-learning/model-serving/index.html)
- [Databricks Apps](https://docs.databricks.com/ja/dev-tools/databricks-apps/index.html)
- [Lakebase](https://www.databricks.com/product/lakebase)

**外部レポート・調査**
- [MIT Technology Review Insights - AI agents are here](https://www.technologyreview.com/2024/10/28/1106320/ai-agents-are-here-will-enterprises-get-agent-ready-in-time/)
- [Deloitte Digital - Digital CX Survey](https://www.deloittedigital.com/us/en/offerings/customer-led-marketing/digital-customer/digital-cx-survey.html)
- [MIT NANDA - The Numbers Behind AI Pilots](https://www.stradegy.ai/p/the-numbers-behind-ai-pilots-that)
- [Economist Impact - Forging a Path to Safe and Trustworthy AI](https://impact.economist.com/perspectives/technology-innovation/forging-path-safe-and-trustworthy-ai)
- [Gartner - Vibe Coding Prediction](https://www.gartner.com/en/newsroom/press-releases/2025-04-23-gartner-predicts-40-percent-of-new-apps-to-be-vibe-coded-by-2028)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

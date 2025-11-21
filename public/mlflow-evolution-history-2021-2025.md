---
title: MLflowの進化の歴史：2021年〜2025年の機能拡張を振り返る
tags:
  - MLflow
  - Databricks
  - MLOps
  - LLMOps
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
MLflowは、機械学習のライフサイクル管理を統合するオープンソースプラットフォームとして、2018年の登場以来、急速に進化を続けてきました。本記事では、2021年から2025年にかけてのMLflowの主要なバージョンアップデートと機能追加を時系列で振り返り、従来の機械学習からLLMOps、AIエージェントまで対応する総合プラットフォームへの進化を紹介します。

# 2021年：MLOpsの基盤確立期

## モデルレジストリとCI/CD連携

https://qiita.com/taka_yayoi/items/b1bd68009102108870dc

https://qiita.com/taka_yayoi/items/7db4b6bac19453f7f8d7

モデルサービングのRESTエンドポイント、モデルレジストリのWebhook機能など、本格的なMLOpsワークフローを実現する機能が充実しました。

## Databricksエンタープライズ機能との統合

https://qiita.com/taka_yayoi/items/3038da9cc8d57922982d

エンタープライズ向けのセキュリティ、ガバナンス、スケーラビリティ機能が強化されました。

## Delta Lakeとの統合強化

https://qiita.com/taka_yayoi/items/b888710c37d64cde4e45

Delta Lakeとの統合により、データバージョニングとモデルトラッキングの一元管理が可能になりました。

# 2022年：MLflow 2.0とモダン化

## MLflow 2.0のリリース（2022年11月）

https://qiita.com/taka_yayoi/items/a4a6379240805aa76646

MLflow 2.0が正式リリースされ、パッケージ構造の刷新、Pythonサポートの最新化、機能の整理統合が行われました。

![MLflow 2.0の新機能](https://cms.databricks.com/sites/default/files/inline-images/db-409-blog-img-1.png)

### 主要な変更点

- Python 3.7以降のサポート
- パッケージ構造の最適化
- 後方互換性の維持とマイグレーションパス提供

## MLflow Pipelinesの導入

https://qiita.com/taka_yayoi/items/29a54ba9a5df4a38b3ad

https://qiita.com/taka_yayoi/items/9bbfff2255a3cd400cd6

機械学習パイプラインをテンプレート化し、ベストプラクティスを標準化するMLflow Pipelinesが導入されました。

## モデル評価機能の強化

https://qiita.com/taka_yayoi/items/7457d7e04d80d3c4eec2

モデルの評価メトリクスの自動計算、ビジュアライゼーション機能が追加されました。

## Tensor入力のサポート

https://qiita.com/taka_yayoi/items/3e439dc5df7257fd41db

画像や時系列データなどのテンソル形式の入力をネイティブにサポートするようになりました。

# 2023年：LLMOps元年

## MLflow 2.3：LLMサポートの開始（2023年4月）

https://qiita.com/taka_yayoi/items/431fa69430c5c6a5e741

**MLflowの歴史における最大の転換点**。大規模言語モデル（LLM）のネイティブサポートが開始されました。

![MLflow 2.3 LLMサポート](https://cms.databricks.com/sites/default/files/inline-images/db-602-blog-img-1.png)

### LLM関連の主要機能

#### OpenAI APIサポート

https://qiita.com/taka_yayoi/items/a058484e6c0abbfbc476

OpenAI APIの統合により、GPTモデルの管理とデプロイが容易になりました。

#### Hugging Face Transformersサポート

https://qiita.com/taka_yayoi/items/ad370a7f57c4eae58800

Hugging Faceのトランスフォーマーモデルのトラッキングとデプロイをサポート。

#### LangChainサポート

https://qiita.com/taka_yayoi/items/2141310748850e865990

LangChainフレームワークとの統合により、LLMアプリケーションの開発が加速しました。

## MLflow 2.4：LLMOps強化（2023年6月）

https://qiita.com/taka_yayoi/items/cd944fde2a9cae8cd6c6

LLM評価のための専用ツールセットが追加されました。

### mlflow.evaluateの拡張

https://qiita.com/taka_yayoi/items/f06adbf5510703b0510b

LLMの品質評価（妥当性、毒性、類似度など）を自動化する`mlflow.evaluate`が大幅に強化されました。

### データセットトラッキング

https://qiita.com/taka_yayoi/items/523c0b1b52e3b39292b1

トレーニングおよび評価に使用したデータセットのバージョン管理が可能になりました。

## MLflow AI Gatewayの発表（2023年7月）

https://qiita.com/taka_yayoi/items/789120e35a2f213eec94

複数のLLMプロバイダー（OpenAI、Anthropic、Cohereなど）を統一的なインターフェースで管理するAI Gatewayが登場しました。

## MLflow 2.7：LLMOps機能の拡充（2023年9月）

https://qiita.com/taka_yayoi/items/34381c349525a797db7a

プロンプトエンジニアリング、評価フレームワーク、デプロイメント機能がさらに強化されました。

## MLflow 2.8：RAG評価サポート（2023年11月）

https://qiita.com/taka_yayoi/items/540702b408c02f11e9b4

RAG（Retrieval-Augmented Generation）アプリケーションの評価機能が追加されました。

### RAGシステムの評価

https://qiita.com/taka_yayoi/items/110818e5691be47fd96a

https://qiita.com/taka_yayoi/items/b7ef9ccd64d4dd662aad

リトリーバの品質、生成結果の妥当性など、RAGシステム特有の評価指標をサポート。

## 新しいエクスペリメントUI（2023年2月）

https://qiita.com/taka_yayoi/items/261c5f2c92c2ae3ae785

実験管理UIが刷新され、より直感的で効率的なモデル開発が可能になりました。

# 2024年：LLMOpsの成熟とエージェント対応

## LangChain統合の深化

### LangChainオートロギング

https://qiita.com/taka_yayoi/items/fb38daf9b1672919f33e

https://qiita.com/taka_yayoi/items/0bade766d740098b2d64

LangChainアプリケーションの自動ロギング機能により、チェーンやエージェントの動作を自動的にトラッキングできるようになりました。

## ChatModelサポート

https://qiita.com/taka_yayoi/items/fd2f8b36aada402589d0

https://qiita.com/taka_yayoi/items/fed34f9bcb0283d60b0f

チャットボットやマルチターン会話アプリケーションのための専用モデルタイプが追加されました。

## LlamaIndex統合

https://qiita.com/taka_yayoi/items/3b00473d13dcd75d7e5d

LlamaIndex WorkflowとMLflowの統合により、高度なRAGアプリケーションの構築が可能になりました。

## Unity Catalogとの統合強化

https://qiita.com/taka_yayoi/items/468f64f7ee1a6a48411f

Unity Catalogによるモデルのガバナンス、アクセス制御、系譜管理が強化されました。

# 2025年：MLflow 3.0とAIエージェント時代

## MLflow Tracingの導入（2025年2月）

https://qiita.com/taka_yayoi/items/148b07697d2e87f31fbf

https://qiita.com/taka_yayoi/items/35c96ecd401c199e617b

LLMアプリケーションの実行トレースを可視化する新機能が追加されました。

![MLflow Tracing](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bd7de7a0-af62-441c-b152-3f7eeffcc873.png)

### 主な機能

- チェーン/エージェントの実行フローの可視化
- レイテンシーとコストの分析
- エラー箇所の特定とデバッグ支援

## OpenAI Agent SDKサポート（2025年3月）

https://qiita.com/taka_yayoi/items/295cc0d9be1483708e29

https://qiita.com/taka_yayoi/items/eab2baae38ff6627cc6a

OpenAI Agent SDKで構築されたAIエージェントのトラッキングとトレースがサポートされました。

## MLflow 3.0の正式リリース（2025年4月）

**MLflowの歴史における最大のアーキテクチャ変更**

https://qiita.com/taka_yayoi/items/ce83575abb55526c52a7

### アーキテクチャの根本的な変更

MLflow 3.0では、データモデルがRun中心からModel中心に再設計されました。

#### 従来の機械学習のサポート

https://qiita.com/taka_yayoi/items/8e66db25d99b4de5c85b

従来のscikit-learn、XGBoost、TensorFlowなどのサポートも継続。

#### ディープラーニングのサポート

https://qiita.com/taka_yayoi/items/1d5cce6164ab44a643cd

PyTorch、TensorFlow、Kerasなどのディープラーニングフレームワークとの統合が強化されました。

#### デプロイメントジョブ

https://qiita.com/taka_yayoi/items/651ad6078a9c338cd482

モデルデプロイメントのワークフロー管理が改善され、継続的デプロイが容易になりました。

#### 生成AIエージェントサポート

https://qiita.com/taka_yayoi/items/c10df7550e3d9ddf5e45

AIエージェントの開発、評価、デプロイを統合的にサポート。

## LoggedModelの導入

https://qiita.com/taka_yayoi/items/7e1481ad8a988eb54aeb

https://qiita.com/taka_yayoi/items/0f5fd36bbc6cd540f669

モデルの新しいデータ表現形式「LoggedModel」が導入され、モデルのメタデータ管理が改善されました。

## プロンプトレジストリ

https://qiita.com/taka_yayoi/items/65a361d714ae174ff167

プロンプトテンプレートのバージョン管理と共有を実現するプロンプトレジストリが追加されました。

## 生成AIアプリの継続的改善サイクル

https://qiita.com/taka_yayoi/items/c0ae12ce358f6293a9f4

開発→評価→デプロイ→フィードバック収集→改善のサイクルを統合的にサポート。

## 人間のフィードバック収集

https://qiita.com/taka_yayoi/items/0ab0e5cd21f5296bd938

本番環境での人間のフィードバックを収集し、モデル改善に活用する機能が追加されました。

## MLflowシステムテーブル（2025年9月）

https://qiita.com/taka_yayoi/items/59caa3397db2fa352a74

実験データをSQLで分析できるシステムテーブルが導入され、大規模な実験管理が容易になりました。

## DSPy統合（2025年1月）

https://qiita.com/taka_yayoi/items/4bde6969ecbc20a38bfe

DSPyフレームワークによるLLMプログラムの自動最適化をMLflowでトラッキングできるようになりました。

# まとめ：MLflowの進化の軌跡

2021年から2025年にかけて、MLflowは以下のような大きな進化を遂げました：

## 主要なトレンド

### 1. **MLOpsからLLMOpsへの転換** ⭐最大の変化
- 2023年4月のMLflow 2.3で大規模言語モデルのネイティブサポート開始
- OpenAI、LangChain、Hugging Faceなど主要LLMフレームワークとの統合
- RAG、チャットボット、エージェントなど、生成AIアプリケーションの全面サポート

### 2. **アーキテクチャの進化**
- MLflow 2.0：パッケージ構造の近代化
- MLflow 3.0：Run中心からModel中心への根本的な再設計
- LoggedModelの導入による柔軟なモデル表現

### 3. **評価フレームワークの充実**
- 従来のMLメトリクスからLLM評価指標へ拡張
- mlflow.evaluateによる自動評価
- RAG固有の評価指標サポート
- 人間のフィードバック収集機能

### 4. **トレーシングとデバッグ**
- MLflow Tracingによる実行フローの可視化
- チェーン/エージェントのステップバイステップ分析
- コストとレイテンシーの追跡

### 5. **エンタープライズ機能の強化**
- Unity Catalogとの統合によるガバナンス強化
- システムテーブルによる大規模実験管理
- プロンプトレジストリによるチーム開発サポート

### 6. **AIエージェント対応**
- OpenAI Agent SDK、LlamaIndex、DSPyなどエージェントフレームワークの統合
- エージェントの開発、評価、デプロイの統合管理
- マルチターン会話の評価とトラッキング

## MLflowの現在地

MLflowは、**従来の機械学習からLLMOps、AIエージェントまでをカバーする総合的なAI開発プラットフォーム**へと進化を遂げました。

- 実験トラッキング
- モデル管理
- デプロイメント
- 評価
- ガバナンス
- 継続的改善

これら全てのライフサイクルを統合的にサポートする唯一のオープンソースプラットフォームとして、その地位を確立しています。

## 今後の展望

生成AI技術の急速な進化に伴い、MLflowもさらなる機能拡張が期待されます：

- より高度なエージェント評価機能
- マルチモーダルAIのサポート強化
- 分散トレーニングとファインチューニングの統合
- コスト最適化機能の充実

最新の情報については、公式ドキュメントをご確認ください。

# 参考リンク

- [MLflow公式ドキュメント](https://mlflow.org/docs/latest/index.html)
- [Databricks MLflowドキュメント（日本語）](https://docs.databricks.com/ja/mlflow/index.html)
- [MLflow GitHub](https://github.com/mlflow/mlflow)

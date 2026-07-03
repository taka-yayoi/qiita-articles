---
title: Databricksにおけるデータパイプラインとオーケストレーション
tags:
  - ETL
  - Databricks
  - autoloader
  - DeltaLiveTables
private: false
updated_at: '2024-04-27T14:53:43+09:00'
id: dd4fe4af945c3c1eabe5
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Databricksにおけるデータの取り込み、ETL、ジョブのオーケストレーションをカバーします。

# 典型的なデータパイプライン

Databricksに限らず、データ分析のためのデータを準備するためには生データからスタートし、クレンジングを経て、BIや機械学習に用いるデータを生成するパイプラインを構築するのが一般的です。これは[メダリオンアーキテクチャ](https://www.databricks.com/jp/glossary/medallion-architecture)と呼ばれるものです。

![Screenshot 2024-04-27 at 11.18.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/409a53fd-77cb-def9-021e-86d5cebb64b4.png)

しかし、生データを準備する時点からいくつかの課題に遭遇することになります。
![Screenshot 2024-04-27 at 11.20.46.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6cefed63-93c3-789e-6763-7878081715e4.png)

## ランディングゾーンからブロンズテーブルを準備する際の課題

- 間違っていくつかのファイルをスキップしてしまう → データの欠損
- 間違って以前のファイルを取り込んでしまう → 重複し、エラーを含むBIやレポートを作り出すことになってしまう
- DIYのファイル追跡 / 一覧はスケールせず、コスト効率が悪い
- スキーマの変更 / 問題 → ジョブの失敗
- スキーマの変更 / 問題 → ファイルの損失、破損 (有害!) 

![Screenshot 2024-04-27 at 11.22.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fa38c142-cf7c-5d4a-e7e6-abdb40fe9e7f.png)

# Auto Loaderによるデータ取り込み

[DatabricksのAuto Loader](https://docs.databricks.com/ja/ingestion/auto-loader/index.html)を用いることで、スケーラブルなexactly-onceのデータ取り込みを実現し、上記の課題を解決します。

- 新規データファイルがクラウドストレージに到着するとインクリメンタルかつ効率的に処理します。
    - ファイル通知モードによってイベント駆動の取り込みを実現(あなたの代わりに自動でEvent Grid / Amazon SNS + Azure Queue Storage / Amazon SQSをセットアップします)
- 到着ファイルのスキーマを自動で推定、あるいはスキーマヒントで既知の情報を提示
- 自動のスキーマ進化 
- レスキューデータ列 - 決してデータを失いません

![Screenshot 2024-04-27 at 11.24.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/84f7128e-8928-6eb9-c127-9e33f2d2c290.png)

Python、SQLで利用することができます。PySparkの場合、formatで`cloudFiles`を指定します。

```py
df = spark
 .readStream
 .format("cloudFiles")
 .option("cloudFiles.format", "json")
 .load("abfss://…" or "s3://")
 .<apply your transformations>
 .writeStream
 .option("checkpointLocation","/chk/path")
 .start("/out/path")
 ```

大量のデータが流入する場合にも、複数のジョブを起動することで柔軟に対応することができます。
![Screenshot 2024-04-27 at 11.25.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/aa83bb0d-990e-b6a0-e617-9d8d9135aeff.png)

# Delta Live Tablesによるデータパイプライン開発

データパイプラインの開発、運用においては様々な課題があり、それらを解決するために上述のAuto Loaderや、ここで説明する[Delta Live Tables(DLT)](https://docs.databricks.com/ja/delta-live-tables/index.html)が提供されています。

![Screenshot 2024-04-27 at 11.27.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/49cca666-ccb7-a84f-5a2c-7545eeb14813.png)

Delta Live Tablesでは、**どのように**データを処理するのかを記述するのではなく、期待するデータを**宣言**することで、**何の**データが必要なのかにフォーカスすることができます。また、エラーハンドリング、自動テスト、オートスケーリングなどの機能を提供しているので、データエンジニアはデータパイプラインのロジック開発に注力することができます。
![Screenshot 2024-04-27 at 11.28.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/30fedd1a-3bde-ec8b-1ca4-160459c7521e.png)

チェンジデータキャプチャ(CDC)もサポートしています。
![Screenshot 2024-04-27 at 11.28.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cb40244a-10dc-c871-bb7a-0ba585d131b6.png)

データに対する期待(エクスペクテーション)を定義することで、自動テストを実装することができます。
![Screenshot 2024-04-27 at 11.29.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/41b0600c-2161-7b1a-e363-3dc327af403c.png)

パイプラインのイベントログも自動で記録されるので、容易にパイプラインの健康状態を監視するダッシュボードを構築することも可能です。
![Screenshot 2024-04-27 at 11.30.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/36b3d7e0-b461-296a-2c5a-1bd4c5151a19.png)

パイプラインに流入するデータが増加したとしても、オートスケーリングでリソースを確保し、時間内に処理を終わらせるようにします。
![Screenshot 2024-04-27 at 11.31.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b25a1674-4fc1-67f8-3f82-08a783d936ea.png)

# Databricksワークフローによるオーケストレーション

モダンなデータエンジニアリングにはモダンなデータオーケストレーションが必要です。

しかし、そのためには複数のユースケースに対する複雑なデータフローを効率的に構築、運用できる必要があります。
![Screenshot 2024-04-27 at 11.32.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a44d9568-2086-7236-7836-947f1f500a6f.png)

すでに、多くのお客様がモダンなデータオーケストレーションでコスト削減などのメリットを享受しています。
![Screenshot 2024-04-27 at 11.33.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ca0ff3ce-644d-dc07-e89a-df3674adfe90.png)

しかし、モダンなデータオーケストレーションのためには様々なツールの組み合わせが必要となり、苦戦しているお客様も多数存在しています。
![Screenshot 2024-04-27 at 11.34.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7165350a-1de9-e061-3e54-44424ecd5237.png)

Databricksにおいても、複数のオーケストレータを組み合わせることは可能です。
![Screenshot 2024-04-27 at 11.35.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fd63fd4a-d68c-d2bd-a5c5-f5f915cf5e71.png)

しかし、これは様々な課題を引き起こします。

- 多くの実践者には利用が難しい -> データチームの生産性の悪化
- 問題が発生した際の根本原因の理解が困難 -> 悪いデータが後段のアプリケーションの価値を損なう
- 管理と維持には複雑なアーキテクチャ -> 所有コストの増加、信頼性の低下

そして、これらのツールはDatabricksデータインテリジェンスプラットフォームと統合されていません。
![Screenshot 2024-04-27 at 11.37.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a46fc0a8-73f6-ce2e-5d86-95dc257aa891.png)

そこで、我々は[Databricksワークフロー](https://docs.databricks.com/ja/workflows/index.html)を提供します。データインテリジェンスプラットフォームにおけるデータ、分析、AIのための統合オーケストレーションを実現します。
![Screenshot 2024-04-27 at 11.37.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/90aa9f19-d922-10db-adc6-243ac4c8c8c8.png)

Databricksワークフローは以下のようなメリットをもたらします。

- シンプルな作成手順 -> すべてのデータ実践者が活用
- アクション可能な洞察 -> リアルタイムの監視 
- 立証された信頼性 -> プロダクション向け

![Screenshot 2024-04-27 at 11.38.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/72d8ac68-4d48-2635-895d-5e4d06c11491.png)

## すべてのデータ実践者向けのシンプルな作成手順

Databricksでの数クリック、あるいはお好きなIDEに接続することで、洗練されたワークフローを構築できます。

![Screenshot 2024-04-27 at 11.43.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/62c7d328-65d9-e710-f3aa-bcb4e4cc34a4.png)
![Screenshot 2024-04-27 at 11.43.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3f347b5a-f899-3f38-d6f2-77ada8fd2dfb.png)
![Screenshot 2024-04-27 at 11.43.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5df3973a-2705-b496-68f9-9ae48df291e8.png)
![Screenshot 2024-04-27 at 11.43.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e5865daf-2b42-8866-3385-1739a72f79ab.png)

## リアルタイム監視によるアクション可能な洞察

シンプルかつ直感的なモニタリングUIによって、すべてのワークフロー実行に対するリアルタイムメトリクスと詳細分析を提供します。
![Screenshot 2024-04-27 at 11.44.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/57bcfba9-94f0-cb8a-55da-a919d53a44d7.png)

どのタスクがなぜ失敗したのかを理解するためにドリルダウンすることで、あなたのお客様にインパクトが出る前のトラブルシュートを可能とします。
![Screenshot 2024-04-27 at 11.44.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/43a04eba-26c6-679a-9947-ee0033795965.png)

## プロダクションワークロードで立証された信頼性

数百万のプロダクションワークロードを実行する数千のお客様からの信頼を得ています。
![Screenshot 2024-04-27 at 11.45.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5405c47d-4ea4-7858-407a-b8ab1d3aec59.png)



# まとめ

- [Auto Loader](https://docs.databricks.com/ja/ingestion/auto-loader/index.html)によってデータ取り込みを堅牢かつスケーラブルに
- [Delta Live Tables](https://docs.databricks.com/ja/delta-live-tables/index.html)はエンドツーエンドでデータパイプラインを管理し、可視性を提供
- 基盤としての[Delta Lake](https://docs.databricks.com/ja/delta/index.html)が、データのバージョン管理、信頼性、パフォーマンスを充当
- [Databricksワークフロー](https://docs.databricks.com/ja/workflows/index.html)がすべてをオーケストレーション


### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

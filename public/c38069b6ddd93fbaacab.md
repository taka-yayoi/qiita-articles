---
title: Lakeflow SDPの増分処理とストリーミングテーブル
tags:
  - Databricks
  - SDP
  - LakeFlow
  - LakeFlowDeclarativePipeline
private: false
updated_at: '2025-12-22T10:42:57+09:00'
id: c38069b6ddd93fbaacab
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

Level 1とLevel 2で、マテリアライズドビュー(MV)とエクスペクテーションを学びました。SQLを書くだけでパイプラインが作れ、データ品質もチェックできるようになりました。

しかし、データ量が増えてくると新たな問題が出てきます。

**「毎回全件処理するのは遅い...」**

例えば、毎日100万件のログが追加されるシステムを考えてみましょう。

- 1日目: 100万件を処理 → OK
- 1週間後: 700万件を処理 → まだ耐えられる
- 1ヶ月後: 3000万件を処理 → 遅い...
- 1年後: 3.6億件を処理 → 現実的でない

MVは**毎回全件をスキャン**します。データが増えれば増えるほど、処理時間も増えていきます。

この問題を解決するのが[ストリーミングテーブル(ST)](https://docs.databricks.com/aws/ja/ldp/streaming-tables)と**増分処理**です。

## Lakeflow SDP入門：基礎から実践まで

本記事は、SDPを段階的に学ぶ学習パス「**Lakeflow SDP入門：基礎から実践まで**」の一部です。

| Level | タイトル | 所要時間 | 学ぶ概念 |
|-------|---------|---------|--------|
| 1 | [SQLだけで始めるLakeflow SDP](https://qiita.com/taka_yayoi/items/e6368446040c9e979d0f) | 30分 | MV、パイプライン |
| 2 | [Lakeflow SDPでデータ品質を守るエクスペクテーション](https://qiita.com/taka_yayoi/items/0b525cb05a095ad0bbe1) | 30分 | エクスペクテーション |
| **3** | **Lakeflow SDPの増分処理とストリーミングテーブル(本記事)** | **45分** | **ST、増分処理** |
| 4 | [Lakeflow SDPのフローを理解する](https://qiita.com/taka_yayoi/items/3e966dee494d0800ec0c) | 45分 | フロー、append_flow |
| 5 | [Lakeflow SDPのAUTO CDCでマスターデータ同期](https://qiita.com/taka_yayoi/items/b1ee8cb73f9723ab1fed) | 60分 | AUTO CDC、SCD |

## この記事で学ぶこと

- なぜ増分処理が必要か
- ストリーミングテーブル(ST)の動作原理
- 「新規データ」の判定単位(ソースによる違い)
- STとMVの使い分け

## 前提条件

- Level 1, 2を完了している、またはSDPの基本操作ができる
- SQLの基本が書ける

# 増分処理とは

## 一言で説明すると

**「前回処理した続きから、新しいデータだけを処理する」** ことです。

## MVとSTの違い

| 項目 | マテリアライズドビュー(MV) | ストリーミングテーブル(ST) |
|------|------------------------|------------------------|
| データの読み方 | 毎回全件スキャン | 前回の続きから |
| 処理対象 | 全データ | 新規データのみ |
| データ量が増えると | 処理時間も増加 | 処理時間は一定 |
| 適したユースケース | 集計、結合、変換 | データ取り込み、ログ蓄積 |

図で表すと:

**1回目の実行**
![Screenshot 2025-12-22 at 6.58.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f9d3f751-0b67-47eb-a179-b3a14f1d221d.png)

初回実行では、MVもSTも全件(A, B, C)を処理します。STはチェックポイントに"C"を記録します。

**2回目の実行**
![Screenshot 2025-12-22 at 6.58.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a96a162a-1594-4e4a-8d88-b83a531dc8aa.png)

2回目以降の差が出ます。MVは全件(5件)を再処理しますが、STは新規データ(D, E)の2件だけを処理します。

**3回目の実行**
![Screenshot 2025-12-22 at 6.59.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9ed212de-0f72-4291-a38d-a0bfd3aa5812.png)

データが増えるほど差が広がります。MVは7件すべてを処理しますが、STは新規の2件(F, G)だけです。

STは**チェックポイント(CP)** で「どこまで処理したか」を記録し、次回は続きから処理します。

# 「新規データ」の判定単位

増分処理で重要なのは、**「何を新規とみなすか」** です。これはソースの種類によって異なります。

## ソース別の新規判定単位

| ソース | 新規判定の単位 | 追跡方法 |
|--------|--------------|---------|
| クラウドストレージ([Auto Loader](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/)) | **ファイル単位** | 新しいファイルの存在をチェックポイントで記録 |
| Kafka等のメッセージング | **メッセージ(レコード)単位** | オフセットで追跡 |
| Delta Table(STREAM読み取り) | **コミット単位** | Delta Tableのバージョンで追跡 |

## 重要: Auto Loaderはファイル単位

クラウドストレージから[Auto Loader](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/)でデータを取り込む場合、**ファイル単位**で新規判定されます。

つまり:
- **新しいファイルが追加された** → 処理対象になる
- **既存ファイルの中身が変更された** → 検知されない(処理されない)

```
/data/
  ├── file1.json  ← 1回目で処理済み(変更しても再処理されない)
  ├── file2.json  ← 1回目で処理済み
  └── file3.json  ← 2回目で新規として処理される
```

これは重要なポイントです。Auto Loaderを使う場合は、**既存ファイルを書き換えるのではなく、新しいファイルを追加していく運用**が前提です。

```
✅ 推奨: 新しいファイルを追加
/data/
  ├── 2024-01-01.json
  ├── 2024-01-02.json  ← 新規追加 → 処理される
  └── 2024-01-03.json  ← 新規追加 → 処理される

❌ 非推奨: 既存ファイルを上書き
/data/
  └── data.json  ← 中身を更新しても再処理されない
```

## STからSTへのデータの流れ

パイプライン内で、あるSTから別のSTにデータを流す場合も増分処理になります。

仕組みはシンプルです:
- 上流のSTに**新しい行が追加された**ら、その行だけが下流のSTで処理される
- 上流STの「どこまで処理したか」がチェックポイントとして記録される

```sql
-- 上流ST
CREATE STREAMING TABLE upstream;

-- 下流ST: 上流に追加された行だけを増分処理
CREATE STREAMING TABLE downstream;

CREATE FLOW process_data AS
INSERT INTO downstream BY NAME
SELECT * FROM STREAM upstream;  -- STREAMキーワードで増分読み取り
```

例えば:
- 1回目: 上流STに100行ある → 100行すべて処理
- 2回目: 上流STに20行追加された → **追加された20行だけ**処理
- 3回目: 上流STに50行追加された → **追加された50行だけ**処理

# ストリーミングテーブルの基本構文

## STの定義方法

STは「テーブル定義」と「データの流し込み方(フロー)」が分離されています。

```sql
-- Step 1: テーブル(箱)を定義
CREATE STREAMING TABLE my_events;

-- Step 2: データの流し込み方(フロー)を定義
CREATE FLOW ingest_events AS
INSERT INTO my_events BY NAME
SELECT * FROM STREAM read_files('/path/to/data');
```

MVとの違い:

```sql
-- MVは定義とデータソースが一体
CREATE MATERIALIZED VIEW my_view AS
SELECT * FROM source_table;

-- STは分離されている
CREATE STREAMING TABLE my_table;  -- 箱だけ
CREATE FLOW my_flow AS ...;       -- データの入れ方
```

この「[フロー](https://docs.databricks.com/aws/ja/ldp/flows)」については、Level 4で詳しく学びます。今回は「STにデータを入れる方法」とだけ理解しておいてください。

## STREAMキーワード

STの定義で重要なのが`STREAM`キーワードです。

```sql
-- ✅ 増分読み取り: 新しいデータのみ処理
SELECT * FROM STREAM read_files('/path/to/data');
SELECT * FROM STREAM upstream_table;

-- ❌ バッチ読み取り: 毎回全件処理(STREAMなし)
SELECT * FROM read_files('/path/to/data');
SELECT * FROM upstream_table;
```

`STREAM`を付け忘れると、増分処理にならず毎回全件処理になってしまいます。これはよくある間違いなので注意してください。

# ハンズオン: ストリーミングテーブルを作成する

実際にSTを作成して、増分処理を体験してみましょう。ファイルを追加するたびに「新規分だけが処理される」ことを確認します。

## Step 1: 新しいパイプラインを作成

1. 左サイドバーで**新規**をクリックし、**ETL パイプライン**を選択
2. パイプライン名を入力(例: `streaming-table-demo`)
3. カタログとスキーマを選択
4. **空のファイルで開始**を選択
5. 言語は**SQL**を選択
6. **選択**をクリック

## Step 2: データ保存用のボリュームを作成

まず、データを保存するボリュームを作成します。SQLエディタまたはノートブックで以下を実行してください。

```sql
-- ボリュームを作成(カタログ・スキーマは適宜変更)
CREATE VOLUME IF NOT EXISTS workspace.sdp.demo_volume;
```

![Screenshot 2025-12-22 at 7.16.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2e191746-c214-45a9-adcc-75357aa3261b.png)


## Step 3: 最初のデータファイルを作成

ボリュームにCSVファイルを作成します。ノートブックで以下を実行してください。

```python
data_batch1 = """order_id,customer_id,amount,order_date
1,101,15000,2024-01-15
2,102,8500,2024-01-16
3,103,22000,2024-01-17
"""

# ボリュームのパスは適宜変更してください
dbutils.fs.put("/Volumes/workspace/sdp/demo_volume/orders_batch1.csv", data_batch1, overwrite=True)

print("batch1を作成しました(3件)")
```

![Screenshot 2025-12-22 at 7.18.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2a3a0f0b-5849-4cb2-9b81-fcfa8878a08e.png)

## Step 4: Bronze層のストリーミングテーブルを作成

パイプラインエディタに戻り、Auto Loaderでファイルを取り込むSTを定義します。

```sql
-- Bronze層: ボリュームからCSVを増分取り込み
CREATE STREAMING TABLE bronze_orders;

CREATE FLOW ingest_orders AS
INSERT INTO bronze_orders BY NAME
SELECT 
    order_id::INT,
    customer_id::INT,
    amount::DOUBLE,
    order_date::DATE
FROM STREAM read_files(
    '/Volumes/workspace/sdp/demo_volume/',
    format => 'csv',
    header => 'true'
);
```

:::note info
`/Volumes/workspace/sdp/demo_volume/`は、Step 2で作成したボリュームのパスに置き換えてください。
:::

**ファイルを実行**をクリックして実行します。

実行後、下部パネルの**データ**タブで3件のデータが取り込まれていることを確認してください。

![Screenshot 2025-12-22 at 7.20.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1b81dc37-b8e2-4c74-8525-4f9da0496361.png)
![Screenshot 2025-12-22 at 7.29.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f612b83f-4152-41cb-937d-12a196e229e6.png)


## Step 5: 追加のデータファイルを作成

ノートブックで2つ目のファイルを追加します。

```python
data_batch2 = """order_id,customer_id,amount,order_date
4,104,5000,2024-01-18
5,105,18000,2024-01-19
"""

dbutils.fs.put("/Volumes/workspace/sdp/demo_volume/orders_batch2.csv", data_batch2, overwrite=True)

print("batch2を作成しました(2件)")
```

![Screenshot 2025-12-22 at 7.21.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/33011f0d-2ba1-4f2c-97a5-8899fa95d50f.png)


## Step 6: 増分処理を確認

パイプラインエディタで再度**ファイルを実行**をクリックします。

![Screenshot 2025-12-22 at 7.23.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c0b2e333-3923-4bf8-bcab-21c0d5870dff.png)
![Screenshot 2025-12-22 at 7.23.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/493f8fa1-4f33-476c-a6bc-0a8af651543d.png)

**確認ポイント:**
- 処理されたのは**batch2の2件だけ**
- batch1の3件は再処理されていない
- 結果テーブルには合計5件が格納されている

これが増分処理です。Auto Loaderが「どのファイルを処理済みか」をチェックポイントで記録しているため、新しいファイルだけが処理されます。

## Step 7: 下流のストリーミングテーブルを作成

Bronze層のSTから、Silver層のSTにデータを流します。

```sql
-- Silver層: 高額注文のみをフィルタリング
CREATE STREAMING TABLE silver_high_value_orders;

CREATE FLOW filter_high_value AS
INSERT INTO silver_high_value_orders BY NAME
SELECT *
FROM STREAM bronze_orders  -- STREAMキーワードで増分読み取り
WHERE amount >= 10000;
```

## Step 8: エクスペクテーションを追加

Level 2で学んだ[エクスペクテーション](https://docs.databricks.com/aws/ja/ldp/expectations)は、STにも適用できます。

```sql
-- Silver層: エクスペクテーション付きストリーミングテーブル
CREATE STREAMING TABLE silver_orders_validated (
    CONSTRAINT positive_amount EXPECT (amount > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_date EXPECT (order_date >= '2024-01-01') ON VIOLATION DROP ROW
);

CREATE FLOW validate_orders AS
INSERT INTO silver_orders_validated BY NAME
SELECT *
FROM STREAM bronze_orders;
```

## Step 9: Gold層は[マテリアライズドビュー](https://docs.databricks.com/aws/ja/ldp/materialized-views)で

集計処理はMVを使います。STは増分処理に向いていますが、GROUP BYなどの集計は全データを見る必要があるためです。

```sql
-- Gold層: 集計はマテリアライズドビュー
CREATE MATERIALIZED VIEW gold_daily_sales AS
SELECT 
    order_date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_sales
FROM silver_orders_validated  -- STREAMなし(バッチ読み取り)
GROUP BY order_date
ORDER BY order_date;
```

**パイプラインを実行**をクリックして、全体を実行します。

![Screenshot 2025-12-22 at 7.32.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/edfc817f-5e2f-4902-b074-e4a7bbe1c84a.png)


## Step 10: さらにデータを追加して増分処理を確認

```python
data_batch3 = """order_id,customer_id,amount,order_date
6,106,12000,2024-01-20
7,107,3000,2024-01-20
8,108,25000,2024-01-21
"""

dbutils.fs.put("/Volumes/workspace/sdp/demo_volume/orders_batch3.csv", data_batch3, overwrite=True)

print("batch3を作成しました(3件)")
```

パイプラインを再実行すると:

| 層 | タイプ | 処理内容 |
|----|--------|---------|
| Bronze | ST | batch3の**3件だけ**を処理(増分) |
| Silver | ST | Bronze層に追加された**3件だけ**を処理(増分) |
| Gold | MV | **全8件**を再集計(フルスキャン)。出力レコードが7件になっているのはグルーピングした結果のレコード数を表示しているためです。 |

![Screenshot 2025-12-22 at 7.35.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b78dcd6a-50ef-40b1-b527-e281abcdee8d.png)
![Screenshot 2025-12-22 at 7.37.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2f55898d-9842-4e66-a08a-006c29bae90c.png)


これがSTとMVの動作の違いです。

# STとMVの使い分け

## 判断基準

| ユースケース | ST or MV | 理由 |
|-------------|----------|------|
| ファイル取り込み | **ST** | Auto Loaderで効率的に増分処理 |
| ログ・イベント蓄積 | **ST** | 追記のみ、増分処理が効率的 |
| フィルタリング(WHERE) | **ST** | 増分処理可能 |
| カラム選択・変換 | **ST** | 増分処理可能 |
| 日次/月次集計(GROUP BY) | **MV** | 全データを見る必要がある |
| 複数テーブルの結合(JOIN) | **MV** | 増分処理が難しい |
| マスターデータ参照 | **MV** | 参照先が更新される可能性 |

## 簡単な判断フロー

1. **データ取り込み?** → ST
2. **集計(GROUP BY)が必要?** → MV
3. **結合(JOIN)が必要?** → MV
4. **それ以外の変換?** → ST

## [メダリオンアーキテクチャ](https://docs.databricks.com/aws/ja/lakehouse/medallion)での使い分け

典型的な構成:

| 層 | 推奨 | 理由 |
|----|------|------|
| Bronze | **ST** | データ取り込みは増分処理が効率的 |
| Silver | **ST** | フィルタリング、型変換は増分処理可能 |
| Silver(結合あり) | **MV** | JOINが必要な場合 |
| Gold | **MV** | 集計処理が中心 |

# 注意点とよくある間違い

## 1. STREAMキーワードの付け忘れ

```sql
-- ❌ 間違い: STREAMがない → 毎回全件処理
CREATE FLOW my_flow AS
INSERT INTO downstream BY NAME
SELECT * FROM upstream_table;

-- ✅ 正しい: STREAMで増分読み取り
CREATE FLOW my_flow AS
INSERT INTO downstream BY NAME
SELECT * FROM STREAM upstream_table;
```

## 2. MVでSTREAMを使おうとする

```sql
-- ❌ エラー: MVではSTREAMは使えない
CREATE MATERIALIZED VIEW my_mv AS
SELECT * FROM STREAM source_table;

-- ✅ 正しい: MVは通常のSELECT
CREATE MATERIALIZED VIEW my_mv AS
SELECT * FROM source_table;
```

## 3. STで集計しようとする

```sql
-- ❌ 問題: STで集計は適切でない
CREATE STREAMING TABLE sales_summary;

CREATE FLOW summarize AS
INSERT INTO sales_summary BY NAME
SELECT product_id, SUM(amount) as total
FROM STREAM sales
GROUP BY product_id;

-- ✅ 正しい: 集計はMVで
CREATE MATERIALIZED VIEW sales_summary AS
SELECT product_id, SUM(amount) as total
FROM sales
GROUP BY product_id;
```

## 4. 既存ファイルの更新を期待する

Auto Loaderは**新しいファイル**のみを検知します。既存ファイルを更新しても再処理されません。

```
-- 期待する動作(実際には起きない)
file1.jsonを更新 → 再処理される

-- 実際の動作
file1.jsonを更新 → 検知されない(処理されない)
file2.jsonを新規追加 → 処理される
```

データを修正したい場合は、**新しいファイルとして追加**するか、[フルリフレッシュ](https://docs.databricks.com/aws/ja/ldp/updates#refresh)を実行します。

# まとめ

## 今日できるようになったこと

- MVの限界(毎回フルスキャン)を理解した
- STの増分処理の仕組みを理解した
- 「新規データ」の判定単位(ファイル/メッセージ/コミット)を理解した
- STとMVを使い分けられるようになった

## STの価値

- **効率的**: 新しいデータだけを処理
- **スケーラブル**: データ量が増えても処理時間は一定
- **リアルタイム対応**: 継続的なデータ取り込みに最適

## 次のステップ

ここまでで、STの基本を学びました。しかし、まだ疑問が残っているかもしれません:

- 「フローって何?」
- 「なぜSTは箱とデータの入れ方が分離されているの?」
- 「複数のソースから1つのSTにデータを入れられる?」

次の記事 [**Level 4: Lakeflow SDPのフローを理解する**](https://qiita.com/taka_yayoi/items/3e966dee494d0800ec0c)では、フローの概念と使い方を詳しく学びます。

# 参考リンク

- [Lakeflow Spark宣言型パイプライン公式ドキュメント](https://docs.databricks.com/aws/ja/ldp/)
- [ストリーミングテーブル](https://docs.databricks.com/aws/ja/ldp/streaming-tables)
- [マテリアライズドビュー](https://docs.databricks.com/aws/ja/ldp/materialized-views)
- [フロー](https://docs.databricks.com/aws/ja/ldp/flows)
- [Auto Loaderとは](https://docs.databricks.com/aws/ja/ingestion/cloud-object-storage/auto-loader/)
- [パイプラインの更新](https://docs.databricks.com/aws/ja/ldp/updates)
- [チュートリアル: Lakeflow Spark宣言型パイプラインを使用してETLパイプラインを構築する](https://docs.databricks.com/aws/ja/getting-started/data-pipeline-get-started)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

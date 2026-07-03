---
title: Claude CodeにDatabricks Appsのダッシュボード作ってと頼んだら全部やってくれた
tags:
  - AppKit
  - Databricks
  - DatabricksApps
  - ClaudeCode
private: false
updated_at: '2026-04-03T10:39:04+09:00'
id: adc1e9d96fdb2dfdc1de
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

Claude CodeとAppKitを使って、NYCタクシーデータセットを可視化するDatabricks Appsのダッシュボードを作成してみました。コードをほぼ書かずに、Claude Codeとの対話だけでアプリが完成するまでの流れを紹介します。

![Screenshot 2026-04-03 at 10.16.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5ae7d8c0-a2e0-4c8d-9549-4834ee6b810a.png)


# 使ったもの

- **Claude Code** - Anthropicの公式CLI
- [**Databricks AppKit**](https://github.com/databricks/appkit?tab=readme-ov-file) - TypeScript/React製のDatabricks Appsフレームワーク
- **データ** - `samples.nyctaxi.trips`（Databricksのサンプルデータ）

# 手順

## CLIのインストール

Databricks CLI(Commnad Line Interface)がインストールされていない場合には[インストール](https://docs.databricks.com/aws/ja/dev-tools/cli/install)します。インストール済みの場合でも最新版にアップデートします。

## AppKitのインストール

```sh
databricks experimental aitools skills install
```

![Screenshot 2026-04-03 at 10.38.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3d2f2eae-f551-4a8a-b5d6-04939500f578.png)

## プロンプト1：依頼する

```
Create a new Databricks app that displays a dashboard of the nyc taxi trips dataset.
```

> nyc taxi tripsデータセットのダッシュボードを表示する新規のDatabricks appを作って

これだけです。あとはClaude Codeが動き始めます。

![Screenshot 2026-04-03 at 10.24.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6f51fae7-1f0e-4091-a95f-98e67c734540.png)

Claude Codeはまず手持ちのDatabricksプロファイルを確認しました。

```
Name        Host                                               Valid
DEFAULT     https://xxxx.cloud.databricks.com         NO
tokyo       https://xxxx.cloud.databricks.com         NO
test     https://test.azuredatabricks.net   YES
...
```

有効なプロファイルが`test`だったので、それを使って作業を始めようとしました。

## プロンプト2：プロファイルを変えてもらう

```
どのプロファイル使ってんの？
```

```
test プロファイルを使っています。
```

```
tokyo使えないの？
```

Claude Codeが`tokyo`を調べると、リフレッシュトークンが期限切れになっていました。

```
リフレッシュトークンが期限切れになっています。再認証が必要です：
$ databricks auth login --profile tokyo
```

## プロンプト3：認証してから再指示

ブラウザで認証を済ませてから：

```
認証しました。tokyo使ってください
```

これでClaude Codeは`tokyo`プロファイルで作業を再開します。


ここからはClaude Codeが自律的に動きます。

**まずデータを確認**

`samples.nyctaxi.trips`テーブルのスキーマとサンプルデータを自動で調べます。

```
COLUMNS:
  tpep_pickup_datetime: timestamp
  tpep_dropoff_datetime: timestamp
  trip_distance: double
  fare_amount: double
  pickup_zip: int
  dropoff_zip: int

total_rows: 21932
```

**AppKitのマニフェストを確認してスキャフォールド**

どのプラグインが使えるか確認した上で、ダッシュボードに必要な`analytics`プラグインを選んでアプリを生成します。

```bash
databricks apps init --name nyc-taxi-dashboard --features analytics \
  --set analytics.sql-warehouse.id=bec52b183a4cfe2a \
  --description "NYC Taxi Trips Dashboard" --run none --profile tokyo
```

```
✔ Project created successfully!  (43 files)
```

**SQLクエリを4本作成**

ダッシュボードに必要なクエリを`config/queries/`に配置します。

- `kpi_summary.sql` - 総トリップ数・平均距離・平均運賃・総売上
- `trips_by_hour.sql` - 時間帯別トリップ数
- `fare_by_distance.sql` - 距離帯別の平均運賃
- `top_pickup_zips.sql` - 人気ピックアップZIPコードTop10

**型を自動生成してからUIを実装**

AppKitのワークフローに従い、SQLから型を生成してから（`npm run typegen`）UIを書きます。型が確定しているので、コンポーネントのpropsにタイポがあればコンパイルエラーになります。

`BarChart`や`DataTable`は`queryKey`を渡すだけでDatabricksのデータを自動取得してくれます。

```tsx
// KPIは useAnalyticsQuery で値を取得してカード表示
const { data: kpi, loading, error } = useAnalyticsQuery('kpi_summary', EMPTY_PARAMS);

// グラフはqueryKeyを渡すだけ
<BarChart queryKey="trips_by_hour" parameters={emptyParams} />

// テーブルも同様
<DataTable queryKey="top_pickup_zips" parameters={emptyParams} pageSize={10} />
```

**バリデーション → エラー → 自己修正**

```bash
databricks apps validate --profile tokyo
```

型チェック・ビルドはパスしたものの、スモークテスト（Playwright）で引っかかりました。

```
Error: strict mode violation: getByText('Avg Fare') resolved to 2 elements:
    1) <div>Avg Fare</div>          ← KPIカードのタイトル
    2) <div>Avg Fare by Trip Distance</div>  ← グラフのタイトル
```

"Avg Fare"という文字列がページ内に2箇所あってテストが曖昧になっていました。Claude Codeは自分でテストのセレクタを修正して再実行します。

```
✅ All validation checks passed (14.9s)
```

**デプロイ**

```bash
databricks bundle deploy --profile tokyo
databricks bundle run app --profile tokyo
```

```
✓ App started successfully
You can access the app at https://nyc-taxi-dashboard-xxxx.aws.databricksapps.com
```

# 完成したダッシュボード

![Screenshot 2026-04-03 at 10.06.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e15cffe7-7c58-41f0-80ce-44de4e7b1ac6.png)

## KPIカード（4種類）

![Screenshot 2026-04-03 at 10.27.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7618f97e-c943-43b7-9554-07d104820d8f.png)

総トリップ数・平均走行距離・平均運賃・総売上をカードで表示。ロード中はスケルトンアニメーションが出ます。

## 棒グラフ（2種類）

![Screenshot 2026-04-03 at 10.28.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/39f089c7-9ac8-406e-98d5-2e968cc4e458.png)

- 時間帯別トリップ数（朝・夕のラッシュアワーのピークが見える）
- 距離帯別の平均運賃（距離が長いほど運賃が上がる）

## テーブル

![Screenshot 2026-04-03 at 10.28.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6b07f749-6ad9-4548-be25-9d1c22d2c9c7.png)

人気ピックアップZIPコードTop10。ソートやフィルタリングが標準で使えます。

# 自分が入力したのはこれだけ

```
Create a new Databricks app that displays a dashboard of the nyc taxi trips dataset.
どのプロファイル使ってんの？
tokyo使えないの？
認証しました。tokyo使ってください
```

4回のメッセージのみです（うち2回はプロファイルの変更指示）。コードは1行も書いていません。

# Claude Codeがやってくれたこと

- Databricksプロファイルの確認と認証状態のチェック
- `samples.nyctaxi.trips`のスキーマ・サンプルデータの調査
- AppKitのマニフェスト確認とスキャフォールド
- 4本のSQLクエリ設計・作成
- TypeScript型の自動生成
- React UIの実装（KPIカード・棒グラフ・テーブル）
- スモークテストの更新
- バリデーションエラーの自己修正
- バンドルデプロイとアプリ起動

# まとめ

Claude Codeはスキルと呼ばれる拡張機能を使って動作します。今回はDatabricks Apps用のスキルが事前にインストールされており、AppKitの適切なワークフロー（SQL作成 → 型生成 → UI実装）を理解した上で開発を進めました。途中でセレクタの曖昧さによるテスト失敗を自分で直してくれたのは驚きました。

「どのデータを、どう見せたいか」だけ伝えれば、あとはClaude Codeに任せられます。

# 参考

- [Databricks AppKit](https://github.com/databricks/appkit)
- [Claude Code](https://docs.anthropic.com/ja/docs/claude-code/overview)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

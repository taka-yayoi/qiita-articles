---
title: Databricks Spark構造化ストリーミングのリアルタイムモードを試してみた
tags:
  - Spark
  - Databricks
private: false
updated_at: '2026-03-09T09:06:57+09:00'
id: abbe089c9b2ee8085bae
organization_url_name: databricks
slide: false
ignorePublish: false
---
# リアルタイムモードとは

Databricksの構造化ストリーミングには、エンドツーエンドの遅延を**5ミリ秒以下**に抑える**リアルタイムモード** (Real-time mode) が用意されています。これはパブリックプレビュー段階の機能で、不正検知やギャンブルサービスのリアルタイムパーソナライゼーションといった、超低レイテンシが求められる運用ワークロードに最適です。

本記事では公式ドキュメント「[リアルタイムモードを始める](https://docs.databricks.com/aws/ja/structured-streaming/real-time-get-started)」に沿って、最初のリアルタイムストリーミングクエリを動かすまでの手順を紹介します。

# 要件

- クラシックコンピュートを作成する権限
- Databricks Runtime **17.1以上** (ノートブックで`display`関数のリアルタイムモードを使用するために必要)

:::note
クラシックコンピュートの作成権限がない場合は、ワークスペース管理者に依頼して、次のステップの設定でクラスターを作成してもらいます。
:::

# ステップ1: リアルタイムモード用のクラシックコンピュートを作成する

超低レイテンシを実現するには、リアルタイムモード専用のクラシックコンピュート設定が必要です。これらの設定により、タスクが全ステージで同時実行され、データはバッチではなく到着次第継続的に処理されます。

1. Databricksワークスペースのサイドバーで **[コンピュート]** をクリック
2. **[コンピュートを作成]** をクリック
3. 任意の名前を入力
4. **Databricks Runtime 17.1以上**を選択
5. **[Photonアクセラレーション]** をオフ (リアルタイムモードはPhoton非対応)
6. **[オートスケールを有効にする]** をオフ (固定クラスターサイズが必要)
7. **[詳細なパフォーマンス]** で **[スポットインスタンスを使用する]** をオフ (スポットインスタンスは中断を引き起こす可能性があるため)
8. **[詳細オプション]** を展開
9. **[アクセスモード]** で **[専用 (旧称: シングルユーザー)]** を選択
10. **[Spark config]** に以下の設定を追加

    ```
    spark.databricks.streaming.realTimeMode.enabled true
    ```

11. **[コンピュートを作成]** をクリック

![Screenshot 2026-03-09 at 9.00.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8fc0f9be-e24b-4cab-b522-40610e9673dd.png)
![Screenshot 2026-03-09 at 9.00.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/65249a92-0433-4a32-9297-09f8d07fbc7b.png)

# ステップ2: ノートブックを作成する

ストリーミングクエリを開発・テストするためのノートブックを用意します。

1. サイドバーの **[新規]** → **[ノートブック]** をクリック
2. コンピュートのドロップダウンで、ステップ1で作成したクラスターを選択
3. デフォルト言語として **Python** または **Scala** を選択

# ステップ3: リアルタイムモードのクエリを実行する

以下のコードをノートブックのセルに貼り付けて実行します。この例では、指定したレートで行を生成するレートソースを使い、結果をリアルタイムで表示します。

:::note
`realTime`トリガーを使った`display`関数はDatabricks Runtime 17.1以降で利用できます。
:::

**Python**

```python
inputDF = (
  spark
  .readStream
  .format("rate")
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
)
display(inputDF, realTime="5 minutes", outputMode="update")
```

**Scala**

```scala
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.streaming.OutputMode

val inputDF = spark
  .readStream
  .format("rate")
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
display(inputDF, trigger=Trigger.RealTime(), outputMode=OutputMode.Update())
```

コードを実行すると、新しい行が生成されるたびにリアルタイムで更新されるテーブルが表示されます。テーブルには`timestamp`列と、行ごとに増加する`value`列が表示されます。

## コードの解説

| パラメーター | 説明 |
|---|---|
| `format("rate")` | 外部依存なしで行を一定レートで生成する組み込みソース。テスト用途に便利 |
| `numPartitions` | 生成データのパーティション数 |
| `rowsPerSecond` | 1秒あたりに生成する行数 |
| `realTime="5 minutes"` (Python) | リアルタイムモードを有効化。間隔はチェックポイントの進行頻度を指定。長い間隔ほどチェックポイント頻度は下がるが、障害後のリカバリ時間が長くなる場合がある |
| `Trigger.RealTime()` (Scala) | デフォルトのチェックポイント間隔でリアルタイムモードを有効化。`Trigger.RealTime("5 minutes")`のように間隔指定も可能 |
| `outputMode="update"` | リアルタイムモードでは更新出力モード (`update`) が必須 |

## 実行結果

![realtime-demo2.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/acd9b675-9dd7-45bd-88ca-5232e9850bfe.gif)


クエリ実行後、`display`関数によって継続的に更新されるテーブルが作成されます。各行には以下が含まれます。

- **timestamp** : レートソースによって行が生成された時刻
- **value** : 新しい行ごとに単調増加するカウンター

テーブルは最小限の遅延で更新され続け、リアルタイムモードの主な利点であるバッチ処理を待たずにデータをすぐに確認・対応できることを実感できます。

# まとめ

この記事では、Databricksの構造化ストリーミングのリアルタイムモードを試すための手順を紹介しました。

- リアルタイムモード用のクラスター設定 (専用モード、Photon無効、オートスケール無効、Spark config追加)
- `realTime`トリガーによるリアルタイム処理の有効化
- ノートブックの`display`関数を使ったインタラクティブな動作確認

次のステップとして、KafkaやKinesisなど実際のソースを使った本番パイプラインの構築に挑戦してみてください。

# 参考

- [リアルタイムモードを始める - Databricks on AWS](https://docs.databricks.com/aws/ja/structured-streaming/real-time-get-started)
- [構造化ストリーミングのリアルタイムモード](https://docs.databricks.com/aws/ja/structured-streaming/real-time)
- [リアルタイムモードの例](https://docs.databricks.com/aws/ja/structured-streaming/real-time-examples)
- [ステートフルストリーミングアプリケーション](https://docs.databricks.com/aws/ja/structured-streaming/stateful-streaming)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

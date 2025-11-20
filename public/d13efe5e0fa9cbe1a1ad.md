---
title: Delta Live Tables開発のベストプラクティス
tags:
  - Databricks
  - DeltaLiveTables
private: false
updated_at: '2024-05-09T10:10:41+09:00'
id: d13efe5e0fa9cbe1a1ad
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらを読む前に以下の記事を読むことをお勧めします。

https://qiita.com/taka_yayoi/items/a59fe4b02b202e5f390d

# Delta Live Tables(DLT)とは

https://docs.databricks.com/ja/delta-live-tables/index.html

> Delta Live Tablesは、信頼性が高く、維持が容易でテスト可能なデータ処理パイプラインを構築するためのフレームワークです。データに対する変換処理を定義すると、Delta Live Tablesはタスクのオーケストレーション、クラスター管理、モニタリング、データ品質、エラー処理を行います。

こちらでは、DLTにおける開発の流れ、開発を効率化するための各種機能をカバーします。

# DLTパイプラインの開発

## ソフトウェア開発のベストプラクティス

信頼できるパイプラインを構築するためのソフトウェア工学から学びましょう。

- **バージョン管理** – すべてのコードをVCS(git)にチェックインします。
- **システムの構築** – モジュール間の依存関係を理解し、適切な順序でパッケージします。
- **継続的インテグレーション** - コードに変更がある際には必ず分離環境でテストすべきです。
- **継続的デプロイメント** – 変更に対して、プロダクション環境は手動のステップを介さずに自動で更新すべきです。
- **モジュール化** – 明確な抽象化境界でコードを分割します。

これを**Spark単体**で行うことはできますが、**膨大な定型コードを必要**とします！

## Delta Live Tablesの開発ワークフロー

- DLTパイプラインを構成するコードは、(Databricks Repoやワークスペース内の)一つ以上のノートブック、あるいはワークスペースファイルで定義することができます。
- 個々のノートブック/ファイルではPythonやSQLを使うことができますが、同じDLTパイプラインで異なる言語を混在させることができます
- DLTパイプラインではどのノートブックが含まれるのか、様々なパイプ
ライン設定(後ほど議論します)を定義します。
- DLTパイプラインでは、環境ごとの設定、データロケーション、配信先のデータベースのような様々なパラメーターを設定することができます。

![Screenshot 2024-05-01 at 10.08.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/abeddaf2-5128-cd5b-08f8-2d5d2adb567c.png)

## DLTパイプラインの検証

実際のデータ処理を行わずに、DLTパイプライン全体を[検証](https://learn.microsoft.com/ja-jp/azure/databricks/delta-live-tables/updates#validate-update)することができます - 構文エラーや不適切な参照などのチェックを行います。

DBR 13+を使っている際には、コードの個々のピースを検証/評価することができます。

:::note
**注意**
複数のファイルではなく、同じファイルで定義されているDLTオブジェクトのみで動作します。
:::

![Screenshot 2024-05-01 at 10.10.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/51e48a3c-08ed-ae94-8ed9-5c431b7303dd.png)

## 開発体験の改善

詳細はこちらをご覧ください。

https://qiita.com/taka_yayoi/items/9c746ccf931fe81bda18

- DLTパイプラインの計算資源にアタッチし、Ctrl/Shift-EnterやUI経由で検証できます。
- ノートブックから直接パイプラインのグラフ構造とイベントログを参照できます。
- エラーや検証に失敗したグラフ内のノードをハイライトします。
- DLT関数のコードコンプリート
- 参照メニューからSpark UIやドライバーログへのアクセス
- 現行のパイプラインに対する操作

## DLTパイプラインの構造化

- DLTコードでDatabricks Reposを使用
- 個々の関数としてPythonファイルでデータ変換処理を実装
    - DLTの外、ローカルでも個々の関数をテストすることができます
- PythonパッケージとしてPythonファイルのコードをインポート
- DLTグラフ内の個々のコードは、データの読み取りや関数の適用処理としてコーディング
- データに対するチェックを実行する別のDLTコードとしてインテグレーションテストを実装

```py
from my_package import my_function

@dlt.table
def processed():
 return my_function(dlt.read("raw_data"))
```

## DLTパイプラインのテスト

- 通常のPythonコードのように個別の変換処理をテストします
- 特定のグラフに対するチェックを実行するためにDLTエクスペクテーション(テストパイプラインの追加のノートブック/ファイルとして表現)を活用します。[サンプル](https://docs.databricks.com/ja/delta-live-tables/expectations.html#perform-advanced-validation-with-delta-live-tables-expectations)をご覧ください。

```py
@dlt.table(comment="Check type")
@dlt.expect_all_or_fail(
   {"valid type": "type in ('link', 'redlink')",
     "type is not null": "type is not null"})
def filtered_type_check():
 return dlt.read("clickstream_filtered").select("type")
```

## CI/CDの全体プロセス

![Screenshot 2024-05-01 at 10.15.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e4f473b9-ae27-fd95-3e5c-a210a676ea24.png)

- 開発者がコードを開発
- 開発コードをコミット
- CIパイプラインがローカルでユニットテストを実行し、統合テストを起動(特定ブランチを対象にすることも可能)
- すべてのテストが実行されると、コードの変更が次の環境にプロモートされます
    - 推奨: [Databricks Asset Bundles](https://qiita.com/taka_yayoi/items/1ab195ba00d03b04d7cf)を使いましょう！

## 開発 vs プロダクション

![Screenshot 2024-05-01 at 10.16.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/81f0ff66-ac1d-75cc-01a6-ad7df395dde9.png)

用途に応じてモードを切り替えましょう。

**開発モード**

- 迅速なイテレーションのための長時間稼働するクラスターの再利用
- デバッグを加速するためにエラーに対するリトライなし

**プロダクションモード**

- 処理が完了すると即座にクラスターを停止することでコストをカット (5分以内)
- クラスター再起動を含むリトライのエスカレーションによって、一時的な問題に遭遇した際の信頼性を保証

## コードのモジュール化

中間テーブルかビューか。

- ビューの実態はクエリーです
    - 大規模/複雑なクエリーの分割にビューを活用しましょう
    - ビューに対するエクスペクテーションは中間結果の正しさを検証できます
    - ビューはクエリーされるたびに**再計算**されます

- **複数のテーブルで同じ結果が必要**となる際には、ストリーミングテーブルやマテリアライズドビューの活用を検討しましょう。

## パイプライン境界の選択

![Screenshot 2024-05-01 at 10.19.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6c6c62ec-5c4c-79f9-da78-d097f4947a5d.png)


- 大規模なパイプラインはクラスターリソースをより効率的に使用できTCOを削減します
- 一つのパイプラインを活用しましょう:
    - チームの境界で
    - 有益なアプリケーション固有の境界で
- 必ずしもテーブルで境界をまたがる依存関係は必要ありません
- 単一のパイプラインに複数のテーブルを配置するメリット:
    - 全体的なパイプライン数の削減
    - オーケストレーションの複雑性の削減
    - 観測可能性とリネージの提供

# DLTにおけるライブラリの活用

- %pipマジックコマンドを用いて様々なPythonライブラリにアクセスします。
- 一つのノートブックでインストールされたPythonライブラリは同じパイプラインのすべてのノートブックで利用可能です。
- ノートブックの順番や依存関係は関係ありません。
- 外部のPythonファイルをwheelsとしてコンパイルし、`%pip install`を実行します:

    ```
    %pip install /path/to/my_package.whl
    ```

# ターゲットスキーマを用いた環境の分離

**落とし穴: ソース & ターゲットのハードコード**

![Screenshot 2024-05-01 at 10.20.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/e59d98f6-87b3-be54-6181-d04828eccaca.png)

**問題:** ソース & ターゲットのハードコードはプロダクション外での変更のテストを不可能にし、CI/CDを破壊します。

**異なるターゲットスキーマを用いて同じコードを分離して実行**

![Screenshot 2024-05-01 at 10.22.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/626af113-5d32-83e6-fd1d-2178c8d7f832.png)

- 共有リポジトリにコードを格納
- 個別のチェックアウトでコードの分離を実現
- 異なるターゲットスキーマを持つ個別のパイプラインでデータの分離を実現

ターゲットスキーマはパイプラインの設定画面で指定できます。
![Screenshot 2024-05-01 at 10.22.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c305bbb0-5085-ed8b-eb31-925d12260ab6.png)

適切にターゲットをスキーマを設定し、環境を分離することで安全に開発を進めることができます。
![Screenshot 2024-05-01 at 10.23.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b43c2eec-5ce7-b8ca-6e45-89ab1787beb0.png)
![Screenshot 2024-05-01 at 10.23.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c94a0bc9-3e38-609d-efbf-d2a2ce33785a.png)
![Screenshot 2024-05-01 at 10.24.24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c606b926-eb9e-35db-c282-784e1d90e830.png)

# パラメーターの活用方法

## 設定によるコードのモジュール化

![Screenshot 2024-05-01 at 10.25.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2b13742e-45fe-8327-117d-232be428bb60.png)

- パイプラインの**設定**は、コードのパラメータ化で利用できるキーバリューペアのマップです:
    - コードの可読性/メンテナンス性の改善
    - 異なるデータに対して複数のパイプラインのコードの再利用

以下のようにパイプラインのロジックからパラメーターにアクセスできます。

```sql
CREATE STREAMING TABLE data AS
SELECT * FROM read_files("${my_etl.input_path}", "json")
```
```py
@dlt.table
def data():
  input_path = spark.conf.get("my_etl.input_path”)
  spark.readStream.format("cloudFiles”).load(input_path)
```

## データボリュームのコントロール

データボリュームを削減するために述語を使うことができます。日付範囲の述語を用いることで、テストやステージングでのデータボリュームを削減できます。

```sql
CREATE MATERIALIZED VIEW data AS
SELECT * FROM data 
WHERE date > current_date() – INTERVAL ”${my_etl.backfill_interval}"
```

[Delta Live Tablesの本格運用](https://qiita.com/taka_yayoi/items/03554306b8b83198b421)に続きます。

https://qiita.com/taka_yayoi/items/03554306b8b83198b421

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

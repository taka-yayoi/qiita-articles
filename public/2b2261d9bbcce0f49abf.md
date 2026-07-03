---
title: Databricksにおけるストアドプロシージャのサポート
tags:
  - ストアドプロシージャ
  - Databricks
private: false
updated_at: '2025-05-23T16:43:03+09:00'
id: 2b2261d9bbcce0f49abf
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
以前、こちらの記事を書きました。

https://qiita.com/taka_yayoi/items/4d4000f086e11cde30f6

記事を書いた際にはこちらのSQLスクリプティングをストアドプロシージャとも書きましたが間違ってました。お恥ずかしい。改めてClaudeに教えてもらいました。

| 項目 | 関数 | ストアドプロシージャ | スクリプティング |
|------|------|---------------------|-----------------|
| 戻り値 | 必須（単一値） | 任意（複数可） | なし |
| 呼び出し方 | SELECT文内で使用 | CALL文で実行 | 直接実行 |
| データ変更 | 原則不可 | 可能 | 可能 |
| 保存場所 | データベース内 | データベース内 | ファイルまたは一時的 |
| 用途 | 計算・変換 | ビジネスロジック | バッチ処理・管理 |

それで、タイトルに戻りますが、Databricksランタイム17.0(ベータ)でストアドプロシージャがサポートされます。

https://docs.databricks.com/aws/ja/release-notes/runtime/17.0#sql-procedure-support

:::note info
**注意**
執筆時点ではベータ版です。
:::

> **SQLプロシージャのサポート**
> Unity Catalogにおける再利用可能な資産としてストアドプロシージャでSQLスクリプトをカプセル化できるようになりました。[CREATE PROCEDURE](https://docs.databricks.com/aws/ja/sql/language-manual/sql-ref-syntax-ddl-create-procedure)コマンドでプロシージャを作成し、[CALL](https://docs.databricks.com/aws/ja/sql/language-manual/sql-ref-syntax-aux-call)コマンドで使用することができます。

ということで、コンピュートを作成します。

![Screenshot 2025-05-23 at 16.03.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4801da3e-c5ff-4f8e-922f-c22b378b219a.png)

サンプルを作成します。二つの引数`x`と`y`を加算する関数ですが、`sum`は二つの入力の合計、`total`はこれまでの出力の累積値となります。

```sql
CREATE OR REPLACE PROCEDURE takaakiyayoi_catalog.default.add(x INT, y INT, OUT sum INT, INOUT total INT)
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Add two numbers'
    AS BEGIN
        SET sum = x + y;
        SET total = total + sum;
    END;
```

Unity Catalogに登録されました。

![Screenshot 2025-05-23 at 16.39.39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ea3a3e2a-417c-498d-b26e-6c59a17212c1.png)

```sql
DECLARE sum INT;
DECLARE total INT DEFAULT 0;
CALL takaakiyayoi_catalog.default.add(1, 2, sum, total);
SELECT sum, total;
```

|sum|total|
|---|---|
|3|3|

引数を変えてもう一度呼び出します。

```sql
CALL takaakiyayoi_catalog.default.add(3, 4, sum, total);
SELECT sum, total;
```

|sum|total|
|---|---|
|7|10|

SQLスクリプティングを使えば、複数のストアドプロシージャや関数の呼び出しを一つの処理にまとめることができますね。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

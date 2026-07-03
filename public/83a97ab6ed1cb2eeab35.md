---
title: Databricksランタイム16.1で導入された新たなSQL関数
tags:
  - SQL
  - Databricks
private: false
updated_at: '2025-01-06T11:44:01+09:00'
id: 83a97ab6ed1cb2eeab35
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Databricksランタイム16.1がGAになりました。

https://docs.databricks.com/ja/release-notes/runtime/16.1.html

以下のような新機能が導入されています。

- [colllationのサポート](https://docs.databricks.com/ja/release-notes/runtime/16.1.html#support-for-collations-in-apache-spark-is-in-public-preview)
- [VACUUMのライトモード](https://docs.databricks.com/ja/release-notes/runtime/16.1.html#lite-mode-for-vacuum-is-in-public-preview)
- [CREATE CATALOGでIDENTIFIER句が使えるように](https://docs.databricks.com/ja/release-notes/runtime/16.1.html#support-for-parameterizing-the-use-catalog-with-identifier-clause)
- [テーブルやビューでのCOMMENT ON COLUMNのサポート](https://docs.databricks.com/ja/release-notes/runtime/16.1.html#comment-on-column-support-for-tables-and-views)

そして、新たに以下の3つのSQL関数が追加されました。

- [dayname](https://docs.databricks.com/en/sql/language-manual/functions/dayname.html): 指定された日付の曜日を3文字英語の略語を返す。
- [uniform](https://docs.databricks.com/en/sql/language-manual/functions/uniform.html): 指定された範囲の[一様分布](https://ja.wikipedia.org/wiki/%E4%B8%80%E6%A7%98%E5%88%86%E5%B8%83)のランダムな値を返す。
- [randstr](https://docs.databricks.com/en/sql/language-manual/functions/randstr.html): 指定された長さのランダムな文字列を返す。

こちらを実際に動かしてみます。その前に最新のランタイムのクラスターを立ち上げておきます。

![Screenshot 2025-01-06 at 11.27.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/37ad38a4-9f85-666d-2662-f82f4eb51604.png)

# dayname

https://docs.databricks.com/en/sql/language-manual/functions/dayname.html

```sql
dayname(expr)
```

ここでの引数`expr`は、`DATE`あるいは`TIMESTAMP`のエクスプレッションとなります。


```sql
SELECT dayname(DATE'2024-11-01' + CAST(offset AS INT)) AS days
    FROM range(8) AS t(offset);
```
![Screenshot 2025-01-06 at 11.29.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/bec6e908-7218-1d3d-fe50-1d3f542c1917.png)

なるほど。こちらの例の`range(8) AS t(offset)`というエクスプレッションを初めて見たので、アシスタントに`/explain`してもらいました。

![Screenshot 2025-01-06 at 11.31.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/24088d01-6d35-2599-0226-596ea995d144.png)

日本語で教えてもらいます。

![Screenshot 2025-01-06 at 11.31.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c933715e-5b78-f27a-0473-45e10bfe6438.png)

> このSQLコードは、`offset`という名前の単一のカラムを持つ結果セットを生成し、そのカラムには0から7までの整数値が含まれます。`range(8)`関数は0から始まり8未満の数値のシーケンスを作成します。`AS t(offset)`部分は生成されたテーブルにtというエイリアスを割り当て、カラム名を`offset`とします。`SELECT *`文はこの生成されたテーブルからすべてのカラムを選択します。

なるほど。理解できました。日付データから曜日のラベルをクイックに作成する際に使えそうです。

# uniform

https://docs.databricks.com/en/sql/language-manual/functions/uniform.html

```sql
uniform (boundaryExpr1, boundaryExpr2 [, seed] )
```

ここでの引数は以下の通り。

- `boundaryExpr1`: `SMALLINT`, `INT`, `BIGINT`、あるいは浮動小数の定数エクスプレッション。範囲の境界(境界値は含む)を指定します。
- `boundaryExpr2`: `SMALLINT`, `INT`, `BIGINT`、あるいは浮動小数の定数エクスプレッション。範囲の境界(境界値は含む)を指定します。
- `seed`: ランダムな値の生成のシードとして使われるオプションの`SMALLINT`あるいは`INT`のエクスプレッション。

```sql
SELECT uniform(10, 20) as uni1, uniform(10, 20) as uni2 FROM range(10);
```
![Screenshot 2025-01-06 at 11.36.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b6dcaff5-acd9-7bc7-36ca-e8ed7a5eb81d.png)
![Screenshot 2025-01-06 at 11.37.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/352499bf-3dc1-0fb3-a3bc-2a8efc2eb7fa.png)
![Screenshot 2025-01-06 at 11.37.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b10f5ca1-c60f-1de5-8830-df91cc51e00b.png)

ダミーデータの生成に使えそうです。

# randstr

https://docs.databricks.com/en/sql/language-manual/functions/randstr.html

```sql
randstr ( length [, seed] )
```

引数は以下の通り。

- `length`: 返却される文字列の長さを指定する`SMALLINT`あるいは`INT`の正の数の定数エクスプレッション。
- `seed`: ランダム文字列の生成におけるシードとして指定するオプションの`SMALLINT`あるいは`INT`のエクスプレッション。

```sql
SELECT randstr(10), randstr(10);
```

![Screenshot 2025-01-06 at 11.39.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cbcbb3b9-c729-299a-7c7a-b7c400fda164.png)

```sql
SELECT randstr(10, 0), randstr(10, 0) FROM VALUES(1), (2), (3);
```

![Screenshot 2025-01-06 at 11.40.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a273803c-6da9-bbdb-a7ce-6dc020f260ad.png)

これもダミーデータの生成に使えそうですね。

最後になりますが、これらの関数は執筆時点では**SQLウェアハウスではサポートされていない**のでご注意ください。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

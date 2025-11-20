---
title: Databricksアシスタントによるデータエンジニアリング
tags:
  - Databricks
  - データエンジニアリング
  - Databricksアシスタント
private: false
updated_at: '2024-05-13T17:05:30+09:00'
id: b76ca7f8f11dce2be1c3
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらで紹介されているティップスのいくつかを日本語で試してみます。

https://www.databricks.com/blog/databricks-assistant-tips-tricks-data-engineers

:::note info
**注意**
Databricksアシスタントが常にこちらで説明しているようなレスポンスを生成するとは限りません。期待するレスポンスが得られない場合には、再生成を指示するかプロンプトを調整してみてください。
![Screenshot 2024-05-11 at 20.43.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/50bd11ad-7fbd-1e09-c589-ca78472001fb.png)
:::

# データの取り込み

**原文のプロンプト**

> Help me ingest data from this API into a Delta Lake table: https://datausa.io/api/data?drilldowns=Nation&measures=Population
> Make sure to use PySpark, and be concise! If the Spark DataFrame columns have any spaces in them, make sure to remove them from the Spark DF.

**日本語のプロンプト**

- 上のリンク先が403になってしまったので、参照先を変えています。
- URLから直接PySparkで読み込もうとしてエラーになったので、`pandas`の記載を追加しています。
- Sparkセッションを作ってしまうケースがあった(Databricksの場合、最初からセッションが変数に代入されています)ので、追記してます。
- テーブル名を明示的に指定しています。

> https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json から得られるJSONファイルをDeltaテーブルにデータを取り込みたいです。Deltaテーブルはtakaakiyayoi_catalog.assistant配下の64KBです。pandasとPySparkを使って簡潔にコードを書いてください。Sparkデータフレームのカラムにスペースが含まれている場合には、データフレームからスペースを除去してください。Sparkセッションはすでにsparkに代入されています。

**レスポンス**

```py
import pandas as pd
import pyspark.sql.functions as F

# JSONファイルをPandas DataFrameに読み込む
df_pandas = pd.read_json("https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json")

# スペースを除去したカラム名を作成
columns = [col.replace(" ", "") for col in df_pandas.columns]

# スペースを除去してSpark DataFrameに変換
df_spark = spark.createDataFrame(df_pandas).toDF(*columns)

# Deltaテーブルに保存
df_spark.write.format("delta").saveAsTable("takaakiyayoi_catalog.assistant.64KB")
```

> 上記のコードでは、指定されたURLからJSONデータを読み込み、Sparkデータフレームとして取り込んでいます。その後、カラム名に含まれるスペースを全て除去しています。最後に、Deltaフォーマットでテーブルを作成し、データをテーブルに保存しています。Deltaテーブルの場所は、指定されたパスで作成されます。

これでテーブルが作成されました。
![Screenshot 2024-05-13 at 16.57.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/3eec0187-2b3b-866a-3de5-8940ceec84c3.png)

# 非構造化データから構造化データへの変換

**原文のプロンプト**

> Here is an example of the Title column in our dataset: 1. The Shawshank Redemption (1994). The title name will be between the number and the parentheses, and the release date is between parentheses. Write a function that extracts both the release date and the title name from the Title column in the imdb_raw DataFrame.

**日本語のプロンプト**

> こちらが我々のデータセットのTitleカラムの例です: 1. The Shawshank Redemption (1994) タイトル名は数とカッコの間です。公開日はカッコの間です。公開日とタイトル名を抽出する関数を書いてください。

**レスポンス**

> 以下は、指定された形式のTitleカラムから公開日とタイトル名を抽出する関数です。

```py
import pyspark.sql.functions as F

def extract_title_and_release_date(df):
    # タイトル名を抽出するための正規表現パターン
    title_pattern = r"\d+\.\s([^\(]+)"
    
    # 公開日を抽出するための正規表現パターン
    release_date_pattern = r"\((\d+)\)"
    
    # タイトル名を抽出
    df_with_title = df.withColumn("TitleName", F.regexp_extract(F.col("Title"), title_pattern, 1))
    
    # 公開日を抽出
    df_with_title_and_release_date = df_with_title.withColumn("ReleaseDate", F.regexp_extract(F.col("Title"), release_date_pattern, 1))
    
    return df_with_title_and_release_date["TitleName", "ReleaseDate"]

# 使用例
imdb_raw = spark.createDataFrame([
    ("1. The Shawshank Redemption (1994)",),
    ("2. The Godfather (1972)",),
    ("3. The Dark Knight (2008)",)
], ["Title"])

title_and_release_date = extract_title_and_release_date(imdb_raw)
title_and_release_date.show()
```

> この関数は、指定された正規表現パターンを使用して、数とカッコの間のタイトル名とカッコ内の公開日を抽出します。関数には、Spark DataFrameを入力として渡し、TitleNameとReleaseDateの2つの列を持つ新しいDataFrameを返します。show()メソッドを使用して結果を表示しています。
>
> 上記のコードを使用して、入力例のデータフレームからタイトル名と公開日を抽出することができます。

これはすごいですね。

```
+--------------------+-----------+
|           TitleName|ReleaseDate|
+--------------------+-----------+
|The Shawshank Red...|       1994|
|      The Godfather |       1972|
|    The Dark Knight |       2008|
+--------------------+-----------+
```

# ドキュメントとメンテナンス容易性の改善

**原文のプロンプト**

> Rewrite this code in a way that is more performant, commented properly, and documented according to Python function documentation standards

**日本語のプロンプト**

> より性能が出るようにこのコードを書き直してください。適切にコメントをつけてください。Pythonの関数の標準に従ってドキュメントを追加してください。

**レスポンス**

> 以下は、提供されたコードを性能向上および可読性向上のために改善したものです。

```py
from typing import List, Dict

def calculate_total(cart_items: List[Dict[str, str]]) -> float:
    """
    カートのアイテムの合計金額を計算する関数

    Args:
        cart_items: カートのアイテムのリスト。各アイテムは辞書形式で、'name'、'type'、'price'のキーを持つ。

    Returns:
        カートのアイテムの合計金額
    """
    total = 0
    
    for item in cart_items:
        if item['type'] == 'book':
            discount = item['price'] * 0.05
            total += item['price'] - discount
        else:
            total += item['price']
    
    return total

# 使用例
cart_items = [{'name': 'Python Programming', 'type': 'book', 'price': 50},
              {'name': 'Laptop', 'type': 'electronics', 'price': 800}]
total_price = calculate_total(cart_items)
```

> 改善点:
>
> - 関数に型アノテーションを追加し、引数と返り値の型を明示しました。
> - forループの範囲を直接cart_itemsリストに対して行うように変更し、インデックスを使用しないようにしました。
> - ループ変数名をitemに変更し、より読みやすいコードを実現しました。
> - ドキュメントのコメントを追加し、関数の目的や引数、返り値の説明を明確化しました。
> 
> これにより、関数のパフォーマンスが向上し、可読性が向上しました。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

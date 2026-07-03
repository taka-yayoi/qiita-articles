---
title: Databricksにおけるbamboolibの活用
tags:
  - Databricks
  - ローコード
  - ノーコード
  - bamboolib
private: false
updated_at: '2022-07-14T11:17:01+09:00'
id: 7fb6fb9c45f4ea26a7cf
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[bamboolib \| Databricks on AWS](https://docs.databricks.com/notebooks/bamboolib.html) [2022/7/8時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

:::note info
**注意**
bamboolibはDatabricksランタイム11.0以降でサポートされています。
:::

bamboolibは、Databricks[ノートブック](https://qiita.com/taka_yayoi/items/24a897cf40bba6d9e305)でノーコードのデータ分析やデータ変換を可能とするユーザーインタフェースのコンポーネントです。bamboolibを用いることで、ユーザーはより容易にデータを取り扱うことができるようになり、一般的なデータ操作、データ探索、可視化のタスクをスピードアップすることができます。ユーザーがデータに対してこれらのタスクを完了すると、bamboolibはバックグラウンドで自動で[Python](https://docs.databricks.com/languages/python.html)コードを生成します。ユーザーはこのコードを他のユーザーに共有することができ、クイックに自分のノートブックでオリジナルのタスクを再現することができます。また、ここでもbamboolibを用いることで、どのようにコーディングするのかを知ることなしに、これらのオリジナルのタスクを拡張することができます。コーディングの経験のある人は、より洗練された結果を得るためにこのコードを拡張することができます。

内部では、bamboolibは[IPythonカーネル](https://docs.databricks.com/notebooks/ipython-kernel.html)向けのインタラクティブなHTMLウィジェットフレームワークである[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/)を使用しています。ipywidgetsは[IPythonカーネル](https://docs.databricks.com/notebooks/ipython-kernel.html)内で実行されます。

# 要件

- Databricks[ランタイム](https://qiita.com/taka_yayoi/items/8d951b660cd87c6c5f18#databricks%E3%83%A9%E3%83%B3%E3%82%BF%E3%82%A4%E3%83%A0)11.0以降のDatabricks[クラスター](https://qiita.com/taka_yayoi/items/d36a469a1e0c0cebaf1b)に[アタッチ](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AB%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%82%92%E3%82%A2%E3%82%BF%E3%83%83%E3%83%81%E3%81%99%E3%82%8B)されたDatabricksノートブック。
- ノートブックで`bamboolib`ライブラリが利用できるようになっていること。PyPIから[ワークスペースにライブラリをインストール](https://qiita.com/taka_yayoi/items/b1668be2ebb6a7841bd0)するか、PyPIから[特定のクラスターにライブラリをインストール](https://qiita.com/taka_yayoi/items/9407356caadea3dfb47c#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AB%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%81%95%E3%82%8C%E3%81%A6%E3%81%84%E3%82%8B%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA)するか、`%pip`コマンドを使って[特定のノートブックにのみライブラリをインストール](https://qiita.com/taka_yayoi/items/d3a46efdc1ad01a581d0#pip%E3%82%92%E7%94%A8%E3%81%84%E3%81%9F%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%82%B9%E3%82%B3%E3%83%BC%E3%83%97%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB)することができます。

# クイックスタート

1. Pythonノートブックを[作成](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)します。
1. [要件](#要件)を満たすクラスターにノートブックを[アタッチ](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AB%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%82%92%E3%82%A2%E3%82%BF%E3%83%83%E3%83%81%E3%81%99%E3%82%8B)します。
1. ノートブックの最初の[セル](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%82%BB%E3%83%AB%E3%81%AE%E8%BF%BD%E5%8A%A0)に以下のコードを入力し、セルを[実行](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%82%BB%E3%83%AB%E3%81%AE%E5%AE%9F%E8%A1%8C)します。

    ```py:Python
    import bamboolib as bam
    ```

1. ノートブックの2つ目のセルに以下のコードを入力し、セルを実行します。

    ```py:Python
    bam
    ```

    > **注意**
あるいは、特定のデータフレームを使用するために[既存のpandasデータフレームを表示](#既存のデータフレームでbamboolibを使用する)することができます。

1. [キータスク](#キータスク)を行います。

# ウォークスルー

bamboolib自身、あるいは[既存のpandasデータフレームを用いて](#既存のデータフレームでbamboolibを使用する)bamboolibを使用することができます。

## bamboolib自身を使用する

このウォークスルーでは、サンプルのセールスデータセットのコンテンツをノートブックに表示するためにbamboolibを使用します。

1. Pythonノートブックを[作成](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)します。
1. [要件](#要件)を満たすクラスターにノートブックを[アタッチ](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AB%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%82%92%E3%82%A2%E3%82%BF%E3%83%83%E3%83%81%E3%81%99%E3%82%8B)します。
1. ノートブックの最初の[セル](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%82%BB%E3%83%AB%E3%81%AE%E8%BF%BD%E5%8A%A0)に以下のコードを入力し、セルを[実行](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%82%BB%E3%83%AB%E3%81%AE%E5%AE%9F%E8%A1%8C)します。

    ```py:Python
    import bamboolib as bam
    ```

1. ノートブックの2つ目のセルに以下のコードを入力し、セルを実行します。

    ```py:Python
    bam
    ```

1. **Load dummy data**をクリックします。
1. **Load dummy data**ペインの**Load a dummy data set for testing bamboolib**から**Sales dataset**を選択します。
1. **Execute**をクリックします。
1. **item_type**が**Baby Food**である行を全て表示します。
    1. **Search actions**リストで**Filter rows**を選択します。
    1. **Filter rows**ペインの**Choose**リスト(**where**の上)から**Select rows**を選択します。
    1. **where**の下のリストから**item_type**を選択します。
    1. **item_type**の隣の**Choose**リストで、**has value(s)** を選択します。
    1. **has value(s)** の隣の**Choose value(s)** ボックスで**Baby Food**を選択します。
    1. **Execute**をクリックします。
1. このクエリー用に自動で生成されたPythonコードをコピーします。
    1. **Get Code**をクリックします。
    1. **Export code**ペインで**Copy code**をクリックします。
1. コードを貼り付けて修正します。
    1. ノートブックの3つ目のセルに、コピーしたコードを貼り付けます。以下のようになります。

    ```py:Python
    import pandas as pd
    df = pd.read_csv(bam.sales_csv)
    # Step: Keep rows where item_type is one of: Baby Food
    df = df.loc[df['item_type'].isin(['Baby Food'])]
    ```

    1. **order_prio**が**C**である行のみを表示するようにコードを追加し、セルを実行します。

    ```py:Python
    import pandas as pd
    df = pd.read_csv(bam.sales_csv)
    # Step: Keep rows where item_type is one of: Baby Food
    df = df.loc[df['item_type'].isin(['Baby Food'])]
    
    # Add the following code.
    # Step: Keep rows where order_prio is one of: C
    df = df.loc[df['order_prio'].isin(['C'])]
    df
    ```

    > **ティップス**
**order_prio**が**C**である行のみを表示するようにするために、このコードを記述する代わりに2番目のセルでbamboolibを使用することもできます。このステップは、前のステップでbamboolibが自動で生成したコードを拡張するサンプルとなっています。

1. **region**の昇順で行をソートします。
    1. 3つ目のセルのウィジェットの**Search actions**リストで**Sort rows**を選択します。
    1. **Sort column(s)**ペインの**Choose column**リストで**region**を選択します。
    1. **region**の隣で**ascending (A-Z)** を選択します。
    1. **Execute**をクリックします。

    > **注意**
    これは以下のコードを記述するのと等価です。
    >    ```py:Python
    >    df = df.sort_values(by=['region'], ascending=[True])
    >    df
    >    ```
    > **region**の昇順で行をソートするために2つ目のセルでbamboolibを使用することもできます。このステップは、前のステップでbamboolibが自動で生成したコードを拡張するサンプルとなっています。bamboolibを使うと、追加のコードが自動で生成されるので、さらに自動で拡張されたコードを自分の手で拡張することもできます！

1. [キータスク](#キータスク)を行います。

## 既存のデータフレームでbamboolibを使用する

1. Pythonノートブックを[作成](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)します。
1. [要件](#要件)を満たすクラスターにノートブックを[アタッチ](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AB%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%82%92%E3%82%A2%E3%82%BF%E3%83%83%E3%83%81%E3%81%99%E3%82%8B)します。
1. ノートブックの最初の[セル](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%82%BB%E3%83%AB%E3%81%AE%E8%BF%BD%E5%8A%A0)に以下のコードを入力し、セルを[実行](https://qiita.com/taka_yayoi/items/dfb53f63aed2fbd344fc#%E3%82%BB%E3%83%AB%E3%81%AE%E5%AE%9F%E8%A1%8C)します。

    ```py:Python
    import bamboolib as bam
    ```

1. ノートブックの2つ目のセルで、以下のコードを入力しセルを実行します。

    ```py:Python
    import pandas as pd
    
    df = pd.read_csv(bam.sales_csv)
    df
    ```

    bamboolibは[pandasデータフレーム](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)のみをサポートしていることに注意してください。PySparkデータフレームをpandasデータフレームに変換するには、PySparkデータフレームに対して[toPandas](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toPandas.html)を呼び出します。Pandas API on Sparkデータフレームをpandasデータフレームに変換するには、Pandas API on Sparkデータフレームに対して[to\_pandas](https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/api/pyspark.pandas.DataFrame.to_pandas.html)を呼び出します。

1. **Show bamboolib UI**をクリックします。
1. **item_type**が**Baby Food**である行を全て表示します。
    1. **Search actions**リストで**Filter rows**を選択します。
    1. **Filter rows**ペインの**Choose**リスト(**where**の上)から**Select rows**を選択します。
    1. **where**の下のリストから**item_type**を選択します。
    1. **item_type**の隣の**Choose**リストで、**has value(s)** を選択します。
    1. **has value(s)** の隣の**Choose value(s)** ボックスで**Baby Food**を選択します。
    1. **Execute**をクリックします。
1. このクエリー用に自動で生成されたPythonコードをコピーします。
    1. **Get Code**をクリックします。
    1. **Export code**ペインで**Copy code**をクリックします。
1. コードを貼り付けて修正します。
    1. ノートブックの3つ目のセルに、コピーしたコードを貼り付けます。以下のようになります。

    ```py:Python
    import pandas as pd
    df = pd.read_csv(bam.sales_csv)
    # Step: Keep rows where item_type is one of: Baby Food
    df = df.loc[df['item_type'].isin(['Baby Food'])]
    ```

    1. **order_prio**が**C**である行のみを表示するようにコードを追加し、セルを実行します。

    ```py:Python
    import pandas as pd
    df = pd.read_csv(bam.sales_csv)
    # Step: Keep rows where item_type is one of: Baby Food
    df = df.loc[df['item_type'].isin(['Baby Food'])]
    
    # Add the following code.
    # Step: Keep rows where order_prio is one of: C
    df = df.loc[df['order_prio'].isin(['C'])]
    df
    ```

    > **ティップス**
**order_prio**が**C**である行のみを表示するようにするために、このコードを記述する代わりに2番目のセルでbamboolibを使用することもできます。このステップは、前のステップでbamboolibが自動で生成したコードを拡張するサンプルとなっています。

1. **region**の昇順で行をソートします。
    1. 3つ目のセルのウィジェットの**Search actions**リストで**Sort rows**を選択します。
    1. **Sort column(s)**ペインの**Choose column**リストで**region**を選択します。
    1. **region**の隣で**ascending (A-Z)** を選択します。
    1. **Execute**をクリックします。

    > **注意**
    これは以下のコードを記述するのと等価です。
    >    ```py:Python
    >    df = df.sort_values(by=['region'], ascending=[True])
    >    df
    >    ```
    > **region**の昇順で行をソートするために2つ目のセルでbamboolibを使用することもできます。このステップは、前のステップでbamboolibが自動で生成したコードを拡張するサンプルとなっています。bamboolibを使うと、追加のコードが自動で生成されるので、さらに自動で拡張されたコードを自分の手で拡張することもできます！

1. [キータスク](#キータスク)を行います。

# キータスク

## セルにウィジェットを追加する

**シナリオ**: セルにbamboolibウィジェットを表示したいと考えています。

1. ノートブックがbamboolibの[要件](#要件)を満たしていることを確認します。
1. ノートブックで以下のコードを実行します。最初のセルで実行することが望ましいです。

    ```py:Python
    import bamboolib as bam
    ```

1. **オプション1**: ウィジェットを表示したいセルで以下のコードを追加し、セルを実行します。

    ```py:Python
    bam
    ```

    コードの下にウィジェットが表示されます。

    あるいは:

    **オプション2**: pandasデータフレームへのリファレンスを含むセルでデータフレームを表示します。例えば、以下のデータフレーム定義を用いてセルを実行します。

    ```py:Python
    import pandas as pd
    from datetime import datetime, date
    
    df = pd.DataFrame({
      'a': [ 1, 2, 3 ],
      'b': [ 2., 3., 4. ],
      'c': [ 'string1', 'string2', 'string3' ],
      'd': [ date(2000, 1, 1), date(2000, 2, 1), date(2000, 3, 1) ],
      'e': [ datetime(2000, 1, 1, 12, 0), datetime(2000, 1, 2, 12, 0), datetime(2000, 1, 3, 12, 0) ]
    })
    
    df
    ```

    セルの下にウィジェットが表示されます。

    bamboolibは[pandasデータフレーム](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)のみをサポートしていることに注意してください。PySparkデータフレームをpandasデータフレームに変換するには、PySparkデータフレームに対して[toPandas](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toPandas.html)を呼び出します。Pandas API on Sparkデータフレームをpandasデータフレームに変換するには、Pandas API on Sparkデータフレームに対して[to\_pandas](https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/api/pyspark.pandas.DataFrame.to_pandas.html)を呼び出します。

## ウィジェットをクリアする

**シナリオ**: ウィジェットのコンテンツをクリアし、既存のウィジェットに新たなデータを読み込みたいと考えています。

**オプション1**: ターゲットのウィジェットを含むセルで以下のコードを実行します。

```py:Python
bam
```

ウィジェットがクリアされ、**Databricks: Read CSV file from DBFS**、**Databricks: Load database table**、**Load dummy data**ボタンが表示されます。

:::note info
**注意**
`name 'bam' is not defined`というエラーが表示される場合、ノートブック(最初のセルが望ましいです)で以下のコマンドを実行し、再度トライしてください。

```py:Python
import bamboolib as bam
```
:::

**オプション2**: [pandasデータフレーム](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)へのリファレンスを含むセルで、セルを再実行することでデータフレームを再度表示します。ウィジェットがクリアされ、新たなデータが表示されます。

## データロードのタスク

### サンプルデータセットのコンテンツをウィジェットに読み込む

**シナリオ**: ウィジェットにサンプルデータを読み込みたいものとします。例えば、ウィジェットの機能を試すためにダミーのセールスデータを読み込みます。

1. **Load dummy data**をクリックします。
1. **Load dummy data**ペインの**Load a dummy data set for testing bamboolib**で、ロードしたいデータセットの名前を選択します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

    ウィジェットにデータセットのコンテンツが表示されます。

:::note info
**ティップス**
現在のウィジェットの表示を別のサンプルデータセットのコンテンツに切り替えることができます。

1. 現在のウィジェットで**Load dummy data**タブをクリックします。
1. ウィジェットに別のサンプルデータセットのコンテンツを読み込むために上のステップを踏みます。
:::

### CSVファイルのコンテンツをウィジェットに読み込む

**シナリオ**: DatabricksワークスペースにあるCSVファイルのコンテンツをウィジェットに読み込みたいものとします。

1. **Databricks: Read CSV file from DBFS**をクリックします。
1. **Read CSV from DBFS**ペインでターゲットのCSVファイルを含む格納場所をブラウジングします。
1. ターゲットのCSVファイルを選択します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてCSVファイルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **CSV value separator**では、CSVファイルの区切り文字を入力するか、デフォルトの区切り文字の`,`(カンマ)のままとします。
1. **Decimal separator**では、CSVファイルの数値の区切り文字を入力するかデフォルトの`.`(ドット)のままとします。
1. **Row limit: read the first N rows - leave empty for no limit**では、ウィジェットに読み込む最大行数を指定するか、あるいはデフォルト値の**100000**のままにするか、制限を指定しない場合には空にします。
1. **Open CSV file**をクリックします。

    指定された設定に基づき、ウィジェットにCSVファイルのコンテンツが表示されます。

:::note info
**ティップス**
現在のウィジェットの表示を別のCSVファイルのコンテンツに切り替えることができます。

1. 現在のウィジェットで**Read CSV from DBFS**タブをクリックします。
1. ウィジェットに別のCSVファイルのコンテンツを読み込むために上のステップを踏みます。
:::

### データベーステーブルのコンテンツをウィジェットに読み込む

**シナリオ**: Databricksワークスペースにあるデータベースのテーブルのコンテンツをウィジェットに読み込みたいものとします。

1. **Databricks: Load database table**をクリックします。

    **Databricks: Load database table**が表示されない場合、[ウィジェットをクリアする - オプション1](#ウィジェットをクリアする
)を試してみてください。

1. **Databricks: Load database table**ペインの**Database - leave empty for default database**でターゲットテーブルが存在するデータベース名を入力するか、**default**データベースを選択するためにボックスを空のままにしておきます。
1. **Table**には、ターゲットテーブル名を入力します。
1. **Row limit: read the first N rows - leave empty for no limit**では、ウィジェットに読み込む最大行数を指定するか、あるいはデフォルト値の**100000**のままにするか、制限を指定しない場合には空にします。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

    指定された設定に基づき、ウィジェットにテーブルのコンテンツが表示されます。

:::note info
**ティップス**
現在のウィジェットの表示を別のテーブルのコンテンツに切り替えることができます。

1. 現在のウィジェットで**Databricks: Load database table**タブをクリックします。
1. ウィジェットに別のテーブルのコンテンツを読み込むために上のステップを踏みます。
:::

## データアクションのタスク

bamboolibでは50以上のデータアクションを提供しています。以下では、最初に使い始める一般的なデータアクションタスクを説明します。

### カラムの選択

**シナリオ**: 特定の名前のカラム、特定のデータタイプのカラム、あるいは正規表現にマッチするカラムのみを表示したいものとします。例えば、ダミーの**Sales dataset**において、`item_type`と`sales_channel`カラムのみを表示したい、あるいは、カラム名に文字列`_date`を含むカラムのみを表示したいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **select**と入力し、**Select or drop columns**を選択します。
    1. **Select or drop columns**を選択します。
1. **Select or drop columns**ペイン**Choose**ドロップダウンリストで、**Select**を選択します。
1. ターゲットのカラム名あるいは条件を選択します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### カラムの削除

**シナリオ**: 特定の名前のカラム、特定のデータタイプのカラム、あるいは正規表現にマッチするカラムを非表示にしたいものとします。例えば、ダミーの**Sales dataset**において、`order_prio`と`order_date`、`ship_date`カラムを非表示にしたい、あるいは、date-timeの値のみを持つすべてのカラムを非表示にしたいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **select**と入力し、**Select or drop columns**を選択します。
    1. **Select or drop columns**を選択します。
1. **Select or drop columns**ペイン**Choose**ドロップダウンリストで、**Drop**を選択します。
1. ターゲットのカラム名あるいは条件を選択します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### 行のフィルタリング

**シナリオ**: 特定のカラムの値がマッチする、あるいは欠損しているといった評価指標に基づいて特定のテーブルの行を表示、非表示したいものとします。例えば、ダミーの**Sales dataset**で、`item_type`カラムの値が`Baby Food`である行のみを表示したいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **filter**と入力し、**Filter rows**を選択します。
    1. **Filter rows**を選択します。
1. **Filter rows**ペインの**where**の上にある**Choose**ドロップダウンリストで、**Select rows**か**Drop rows**を選択します。
1. 最初のフィルタリング条件を指定します。
1. 別のフィルタリング条件を追加するには、**add condition**をクリックし、次のフィルタリング条件を指定します。必要なだけこの操作を繰り返します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### 行のソート

**シナリオ**: 1つ以上のカラムの値に基づいてテーブルの行をソートしたいものとします。例えば、ダミーの**Sales dataset**で`region`カラムのアルファベット順で行をソートしたいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **sort**と入力し、**Sort rows**を選択します。
    1. **Sort rows**を選択します。
1. **Sort column(s)** ペインでソートする最初のカラムとソート順を選択します。
1. 別のソート条件を追加するには、**add column**をクリックし、次のソート条件を指定します。必要なだけこの操作を繰り返します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### 行と列のグルーピングのタスク

#### 単一の集計関数による行と列のグルーピング

**シナリオ**: グループの計算結果による行と列の結果を表示し、これらのグルーピングに対してカスタムの名称を割り当てたいものとします。例えば、ダミーの**Sales dataset**でカラム`country`の値に基づいて行をグルーピングし、同じ`country`の値を持つ行の数を表示し、計算されたカウントの名前を`country_count`にしたいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **group**と入力し、**Group by and aggregate (with renaming)** を選択します。
    1. **Group by and aggregate (with renaming)** を選択します。
1. **Group by with column rename**ペインでグルーピングするカラムを選択し、計算処理、そしてオプションで計算値のカラム名を指定します。
1. 別の計算処理を追加するには、**add calculation**をクリックし、次の計算処理とカラム名を指定します。必要なだけこの操作を繰り返します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

#### 複数の集計関数による行と列のグルーピング

**シナリオ**: 計算されたグループの結果の行と列を表示したいものとします。例えば、ダミーの**Sales dataset**で`region`、`country`、`sales_channel`の値に基づいてグルーピングを行い、`sales_channel`ごとに同じ`region`と`country`を持つ行の数、そして、`region`、`country`、`sales_channel`のユニークな組み合わせによる`total_revenue`を表示したいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **group**と入力し、**Group by and aggregate (default)** を選択します。
    1. **Group by and aggregate (default)** を選択します。
1. **Group by with column rename**ペインでグルーピングするカラムを選択し、計算処理、そしてオプションで計算値のカラム名を指定します。
1. 別の計算処理を追加するには、**add calculation**をクリックし、次の計算処理とカラム名を指定します。必要なだけこの操作を繰り返します。
1. 結果をどこに格納するのかを指定します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### 欠損値を持つ行の削除

**シナリオ**: 特定のカラムで欠損値を持つ行を削除したいものとします。例えば、ダミーの**Sales dataset**で、`item_type`に値のない行を削除したいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **drop**あるいは**remove**と入力し、**Drop missing values**を選択します。
    1. **Drop missing values**を選択します。
1. **Drop missing values**ペインで欠損値をチェックするカラムを指定します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### 重複行の削除

**シナリオ**: 特定カラムで重複値がある行を削除したいものとします。例えば、ダミーの**Sales dataset**で、全く同じ値を持つ行を削除したいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **drop**あるいは**remove**と入力し、**Drop/Remove duplicates**を選択します。
    1. **Drop/Remove duplicates**を選択します。
1. **Drop Duplicates**ペインで重複を確認するカラムを指定し、重複値を持つ最初の行、最後の行を保持するのかを選択します。
1. **Dataframe name**には、[データフレーム](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.html)としてテーブルのコンテンツのプログラム上の識別子を指定します。あるいは、デフォルトの**df**のままとします。
1. **Execute**をクリックします。

### 欠損値の検索・置換

**シナリオ**: 特定カラムで欠損値がある場合に何かしらの値で置換を行いたいものとします。例えば、ダミーの**Sales dataset**で`item_type`カラムの欠損値を`Unknown Item Type`で置き換えたいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **find**あるいは**replace**と入力し、**Find and replace missing values**を選択します。
    1. **Find and replace missing values**を選択します。
1. **Replace missing values**ペインで欠損値を置き換えるカラムと、置換する値を指定します。
1. **Execute**をクリックします。

### カラム数式の作成

**シナリオ**: ユニークな数式を使用するカラムを作成したいものとします。例えば、ダミーの**Sales dataset**で各行の`total_profit`の値を`units_sold`で割った結果を`profit_per_unit`というカラムとして表示したいものとします。

1. **Data**タブの**Search actions**ドロップダウンリストで以下のいずれかを行います。
    1. **formula**と入力し、**New column formula**を選択します。
    1. **New column formula**を選択します。
1. **Create new column from formula**ペインで数式とカラム名を指定します。
1. **Execute**をクリックします。

## データアクション履歴のタスク

### ウィジェットで実行済みアクションの一覧を参照する

**シナリオ**: ウィジェットで実行されたすべての変更を最初から最後まで参照したいものとします。

**History**をクリックします。**Transformations history**ペインにアクションの一覧が表示されます。

### ウィジェットで最新のアクションを取り消す

**シナリオ**: ウィジェットで実行された最後のアクションを取り消したいものとします。

以下のいずれかを行います。

- 逆時計回り矢印のアイコンをクリックします。
- **History**をクリックします。**Transformations history**ペインで**Undo last step**をクリックします。

### ウィジェットで最新のアクションを再度実行する

**シナリオ**: 最新のアクションを取り消した後に、再度最新のアクションを実行したいものとします。

以下のいずれかを行います。

- 時計回り矢印のアイコンをクリックします。
- **History**をクリックします。**Transformations history**ペインで**Recover last step**をクリックします。

### ウィジェットで最新のアクションを変更する

**シナリオ**: ウィジェット常の最新のアクションを変更したいものとします。

1. 以下のいずれかを行います。
    1. 鉛筆アイコンをクリックします。
    1. **History**をクリックします。**Transformations history**ペインで**Edit last step**をクリックします。
1. 必要な変更を行い、**Execute**をクリックします。

## ウィジェットの現在の状態をプログラムでデータフレームとして再現するためのコードを取得する

**シナリオ**: 現在のウィジェットの状態をプログラム的に再現するPythonコードを取得し、pandasデータフレームとして表現したいと考えています。この
ノートブックの別のセル、あるいは別のノートブックでこのコードを実行することができます。

1. **Get Code**をクリックします。
1. **Export code**ペインで**Copy code**をクリックします。コードがクリップボードにコピーされます。
1. ノートブックの別のセル、あるいは別のノートブックにコードを貼り付けます。
1. プログラムからpandasデータフレームを操作するために追加のコードを記述し、セルを実行します。例えば、データフレーム`df`の中身を表示するために以下のコードを追加します。

    ```py:Python
    # Your pasted code here, followed by...
    df
    ```

# その他のリソース

- [bamboolib Documentation](https://docs.bamboolib.8080labs.com/)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

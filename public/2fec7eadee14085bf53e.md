---
title: Databricksノートブックでコードを共有する
tags:
  - Databricks
private: false
updated_at: '2023-01-04T08:41:29+09:00'
id: 2fec7eadee14085bf53e
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Share code between Databricks notebooks \| Databricks on AWS](https://docs.databricks.com/notebooks/share-code.html) [2022/12/21時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

Databricksでは、ノートブック間でコードを共有するための方法をいくつかサポートしています。それぞれの方法においては、コードのモジュール化を実現し、[ライブラリ](https://qiita.com/taka_yayoi/items/0c7fc7d741aad34bf9d4)のようにノートブックでコードを共有することができます。

また、Databricksでは依存関係を持つパイプラインや戻り値に基づくif-then-elseワークフローのような複雑なワークフローにノートブックを組み込むこともできます。[ノートブックワークフロー](https://qiita.com/taka_yayoi/items/118fbc0ad8fa5471bc88)をご覧ください。

# ノートブックをインポートするために`%run`を使う

マジックコマンド`%run`を用いることで、ノートブックに別のノートブックを含めることができます。例えば、別のノートブックにサポート関数を配置することでコードをモジュール化するために`%run`を用いることができます。また、分析におけるステップを実装する複数のノートブックを結合するために使用することもできます。`%run`を使用する際、呼び出されたノートブックは即座に実行され、定義された関数や変数は呼び出し下のノートブックで使用できるようになります。

以下の例では、最初のノートブックはヘルパー関数`reverse`を定義しており、`shared-code-notebook`を実行するために`%run`マジックコマンドを実行した後でこの関数を利用できるようになります。
![](https://docs.databricks.com/_images/shared-code-notebook.png)
![](https://docs.databricks.com/_images/notebook-import-example.png)

これらのノートブックは両方ともワークスペースの同じディレクトリに格納されているので、現在実行しているノートブックに対して相対的にパスを解決できるように、`./shared-code-notebook`でプレフィックス`./`を使用します。`%run ./dir/notebook`としたり、`%run /Users/username@organization.com/directory/notebook`のような絶対パスを指定することでディレクトリにノートブックを整理することができます。

:::note info
**注意**
- `%run`はノートブック全体をインラインで実行するので、`%run`は*自身専用*のセルで実行される必要があります。
- Pythonファイルを実行したり、そのファイルで定義されているエンティティを`import`するために`%run`を*使用することはできません*。Pythonファイルからインポートするためには、[gitを用いてソースコードファイルを参照する](#gitを用いてソースコードファイルを参照する)を参照ください。あるいは、ファイルをPythonライブラリにパッケージングし、そのPythonライブラリからDatabricksの[ライブラリ](https://docs.databricks.com/libraries/index.html)を作成し、ノートブックの実行に使用する[クラスターにライブラリをインストール](https://qiita.com/taka_yayoi/items/869158c7bd3ab7c45ff4#%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AB%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%82%92%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%81%99%E3%82%8B)します。
- ウィジェットを含むノートブックを実行するために`%run`を使用する際、デフォルトでは指定されたノートブックはウィジェットのデフォルト値を用いて実行されます。ウィジェットに値を渡すこともできます。[%runにおけるウィジェットの使用](https://qiita.com/taka_yayoi/items/4df1fd723bdab9a99b08#run%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E3%82%A6%E3%82%A3%E3%82%B8%E3%82%A7%E3%83%83%E3%83%88%E3%81%AE%E4%BD%BF%E7%94%A8)をご覧ください。
:::

### ソースコードファイルを参照するためにDatabricks Reposを使用する

Databricksの[Repo](https://qiita.com/taka_yayoi/items/b89f199ff0d3a4c16140)に格納されているノートブックに対しては、リポジトリのコードファイルを参照することができます。

例えば、リポジトリに`power.py`ファイルが含まれているものとします。
![](https://docs.databricks.com/_images/file-in-repo.png)

このファイルをノートブックにインポートし、ファイルで定義されている関数を呼び出すことができます。
![](https://docs.databricks.com/_images/notebook-calling-file.png)

Databricks Reposのファイルの取り扱いの詳細に関しては、[Databricks repoにおける非ノートブックファイルの作業](https://qiita.com/taka_yayoi/items/b89f199ff0d3a4c16140#databricks-repo%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E9%9D%9E%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E4%BD%9C%E6%A5%AD)をご覧ください。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

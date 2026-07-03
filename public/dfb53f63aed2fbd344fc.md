---
title: Databricksノートブックでコードを開発する
tags:
  - Databricks
  - Databricksクイックスタートガイド
private: false
updated_at: '2023-06-03T20:46:14+09:00'
id: dfb53f63aed2fbd344fc
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Develop code in Databricks notebooks \| Databricks on AWS](https://docs.databricks.com/notebooks/notebooks-code.html) [2023/6/1時点]の翻訳です。

> [Databricksクイックスタートガイド](https://qiita.com/taka_yayoi/items/125231c126a602693610)のコンテンツです。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

このページでは、オートコンプリート、PythonやSQLにおけるオートフォーマット、ノートブックにおけるPythonとSQLの組み合わせ、ノートブックバージョン履歴を含む、Databricksノートブックにおけるコードの開発方法を説明します。

エディタで利用できるオートコンプリート、変数選択、マルチカーソル、隣り合わせのdiffなどの高度な機能の詳細については、[Use the Databricks notebook and file editor](https://docs.databricks.com/notebooks/notebook-editor.html)をご覧ください。

# 編集するためにノートブックにアクセス

ノートブックを開くには、ワークスペースの[検索機能](https://qiita.com/taka_yayoi/items/ead2ad6c07e1510d2c98)、あるいは[ノートブックまでナビゲート](https://qiita.com/taka_yayoi/items/e469dded5ee83ae42d24)するためにワークスペースブラウザを使用し、ノーブック名やアイコンをクリックします。

# データのブラウズ

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

ノートブックから利用できるテーブルやボリュームを探索するためにスキーマブラウザを活用します。スキーマブラウザを開くにはノートブックの左にある![](https://docs.databricks.com/_images/notebook-data-icon.png)をクリックします。

**For you**ボタンは、現在のセッションで使用したテーブルやボリューム、以前Favoriteにマークしたもののみを表示します。

**Filter**ボックスにテキストをタイプすると、タイプしたテキストを含むアイテムのみを表示します。現在オープンしている、現在のsrっションでオープンしたアイテムのみが表示されます。**Filter**ボックスは、ノートブックで利用できる、カタログ、スキーマ、テーブル、ボリュームの完全な検索を行いません。

![](https://docs.databricks.com/_images/kebab-menu.png)ケバブメニューを開くには、アイテム名が表示されている部分にカーソルを移動します:
![](https://docs.databricks.com/_images/schema-browser-kebab.png)

アイテムがテーブルの場合、以下のことを行うことができます:

- テーブルのデータをプレビューするために自動でセルを作成し実行します。テーブルのケバブメニューから**Preview in a new cell**を選択します。
- データエクスプローラでカタログ、スキーマ、テーブルを参照します。ケバブメニューから**Open in Data Explorer**を選択します。選択したアイテムを表示する新規タブが開きます。
- カタログ、スキーマ、テーブルのパスを取得します。アイテムのケバブメニューから**Copy … path**を選択します。
- テーブルをFavoritesに追加します。テーブルのケバブメニューで**Add table to favorites**を選択します。

アイテムがカタログやスキーマの場合、アイテムのパスをコピーしたり、データエクスプローラで開くことができます。

セルにテーブル名やカラム名を直接インサートするには:

1. セルで名前を入力したい場所でカーソルをクリックします。
1. スキーマブラウザでテーブル名やカラム名の上にカーソルを移動します。
1. アイテム名の右に表示される二重矢印![](https://docs.databricks.com/_images/schema-browser-double-arrow.png)をクリックします。


# キーボードショートカット

キーボードショートカットを表示するには、**Help > Keyboard shortcuts**を選択します。利用できるキーボードショートカットは、コードセルにカーソルがある場合(編集モード)とそうではない場合(コマンドモード)とで変化します。

# テキストの検索、置換

ノートブック内のテキストを検索、置換するには、**Edit > Find and Replace**を選択します。マッチ結果の現在地点はオレンジでハイライトされ、他のマッチは黄色でハイライトされます。
![](https://docs.databricks.com/_images/find-replace-example.png)

現在のマッチを置換するには、**Replace**をクリックします。ノートブックのすべてのマッチ結果を置換するには**Replace All**をクリックします。

マッチ間を移動するには、**Prev**や**Next**ボタンをクリックします。また、前のマッチに移動するには**shift+enter**、次のマッチに移動するには**enter**を押すこともできます。

検索、置換ツールを閉じるには、![](https://docs.databricks.com/_images/delete-icon.png)をクリックするか、**esc**を押します。

# 変数エクスプローラ

Databricksランタイム12.1以降では、ノートブックUIで直接現在のPython変数を観察することができます。

変数エクスプローラを開くには、[右側のサイドバー](https://qiita.com/taka_yayoi/items/141e49b155f4cad1bb34#%E5%8F%B3%E5%81%B4%E3%81%AE%E3%82%B5%E3%82%A4%E3%83%89%E3%83%90%E3%83%BC%E3%81%AE%E3%82%A2%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3)で![](https://docs.databricks.com/_images/variable-explorer-icon.png)をgクリックします。変数エクスプローラが開き、ノートブックで現在定義されている変数ごとに、値、データ型、形状を表示します(PySparkデータフレームの形状計算にはコストがかかることがあるため、PySparkの形状は`?`と表示されます)。

表示をフィルタリングするには、検索ボックスにテキストを入力します。タイプすると自動でフィルタリングされます。

変数の値は、ノートブックセルを実行する度に自動でアップデートされます。
![](https://docs.databricks.com/_images/variable-explorer-example.png)

# コードのモジュール化

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

Databricksランタイム11.2以降では、Databricksワークスペースでソースコードファイルを作成、管理することができ、必要に応じてノートブックにこれらのファイルをインポートすることができます。

ソースコードファイル操作の詳細については、[Share code between Databricks notebooks](https://docs.databricks.com/notebooks/share-code.html)や[Work with Python and R modules](https://docs.databricks.com/files/workspace-modules.html)をご覧ください。


# 選択テキストの実行

ノートブックセルのコードやSQL文をハイライトし、その選択箇所のみを実行することができます。これは、コードやクエリーをクイックに繰り返したい場合には有用です。

1. 実行したい行をハイライトします。
1. **Run > Run selected text**を選択するか、キーボードショートカット`Ctrl+Shift+Enter`を使用します。テキストがハイライトされていない場合、**Run Selected Text**は現在の行を実行します。
![](https://docs.databricks.com/_images/run-selected-text.gif)

セルで[ミックス言語](#ミックス言語)を使用している場合、選択範囲に`%<language>`を含める必要があります。

また、**Run selected text**は、ハイライトされた箇所に含まれる折り畳まれたコードも実行します。

`%run`、`%pip`、`%sh`のような特殊なセルコマンドもサポートされています。

## 選択テキスト実行の制限

複数の出力タブを持つセル(データプロファイルやビジュアライゼーションを定義しているセル)で**Run selected text**を実行することはできません。

[新たなノートブックエディタ](https://qiita.com/taka_yayoi/items/b6adb35a48e77b4962c8)を使用していない場合、**Run selected text**は編集モード(カーソルがコードセルにある場合)でのみ動作します。カーソルが選択テキストのセルの外にある場合、**Run selected text**は動作しません。この制限を回避するには、[新たなノートブックエディタを有効化](https://qiita.com/taka_yayoi/items/b6adb35a48e77b4962c8#%E6%96%B0%E8%A6%8F%E3%82%A8%E3%83%87%E3%82%A3%E3%82%BF%E3%81%AE%E6%9C%89%E5%8A%B9%E5%8C%96)してください。

# コードセルのフォーマット

DatabricksではノートブックのセルにあるPython、SQL
コードをクイックかつ簡単にフォーマットできるツールを提供しています。これらのツールは、コードをフォーマットされた状態に保つ労力を削減し、ノートブックに対して同じコード基準を強制する助けになります。

## Pythonセルのフォーマット

:::note
**プレビュー**
この機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

Databricksランタイム11.2以降、Databricksではノートブックのコードのフォーマットに[Black](https://black.readthedocs.io/en/stable/)を使用します。ノートブックをクラスターにアタッチする必要があり、ノートブックがアタッチされたクラスターでBlackが実行されます。

## PythonとSQLセルのフォーマット方法

コードをフォーマットするにはノートブックに対する[Can Edit権限](https://qiita.com/taka_yayoi/items/2dd6711b7b254505e4a3#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E6%A8%A9)が必要となります。

以下の方法でフォーマッターを起動することができます:

- **単一セルのフォーマット**
    - キーボードショートカット: **Cmd+Shift+F**
    - コマンドコンテキストメニュー:
        - SQLセルのフォーマット: SQLセルのコマンドコンテキストドロップダウンメニューで**Format SQL**を選択。このメニューアイテムはSQLノートブックのセルか[言語マジック](#ミックス言語)`%sql`のセルでのみ表示されます。
        - Pythonセルのフォーマット: Pythonセルのコマンドコンテキストドロップダウンメニューで**Format Python**を選択。このメニューアイテムはPythonノートブックのセルか[言語マジック](#ミックス言語)`%python`のセルでのみ表示されます。
    - ノートブックの**Edit**メニュー: PythonセルかSQLセルを選択し、**Edit > Format Cell(s)** を選択。
- **複数セルのフォーマット**

    [複数のセル](https://qiita.com/taka_yayoi/items/141e49b155f4cad1bb34#%E3%82%BB%E3%83%AB%E3%81%AE%E3%82%AB%E3%83%83%E3%83%88%E3%82%B3%E3%83%94%E3%83%BC%E3%83%9A%E3%83%BC%E3%82%B9%E3%83%88)を選択し、**Edit > Format Cell(s)** を選択します。2つ以上の言語を含むセルを選択した場合、SQLとPythonのセルのみがフォーマットされます。これには`%sql`や`%python`を使用しているものも含まれます。
- **ノートブックのすべてのPython、SQLセルのフォーマット**

    **Edit > Format Notebook**を選択します。ノートブックに2つ以上の言語が含まれている場合、SQLとPythonのセルのみがフォーマットされます。これには`%sql`や`%python`を使用しているものも含まれます。

## コードフォーマッティングの制限

- Blackは[PEP 8](https://peps.python.org/pep-0008/)の4スペースのインデントを強制します。インデントを設定することはできません。
- SQL UDF内に埋め込まれたPython文字列のフォーマットはサポートされていません。同様に、Python UDF内のSQL文字列のフォーマットもサポートされていません。

# バージョン履歴

Databricksノートブックはバージョン履歴を保持するので、以前のノートブックのスナップショットを参照、復旧することができます。バージョンに対して以下の操作を行うことができます: コメントの追加、バージョンの復旧と削除、バージョン履歴のクリア。

また、[リモートGitリポジトリとDatabricksで成果物を同期](https://qiita.com/taka_yayoi/items/b89f199ff0d3a4c16140)することができます。

ノートブックのバージョンにアクセスするには、ツールバーの`Last edit…`メッセージをクリックします。ブラウザの右側にノートブックのバージョンが表示されます。また、**File > Version history**を選択することもできます。

## コメントの追加

最新バージョンにコメントを追加するには：

1. バージョンをクリック
1. **Save now**リンクをクリック
![](https://docs.databricks.com/_images/revision-comment.png)
1. ノートブックバージョン保存ダイアログでコメントを入力
1. **Save**をクリック。ノートブックのバージョンはコメントとともに保存されます。
1. 

## バージョンの復旧

バージョンを復旧するには、

1. バージョンをクリック
1. **Restore this revision**をクリック
![](https://docs.databricks.com/_images/restore-revision.png)
1. **Confirm**をクリック。選択されたバージョンが最新バージョンになります。

## バージョンの削除

特定のバージョンを削除するには、

1. バージョンをクリック
1. ゴミ箱アイコン![](https://docs.databricks.com/_images/trash-icon.png)をクリック
![](https://docs.databricks.com/_images/delete-revision.png)
1. **Yes, erase**をクリック。選択されたバージョンはバージョン履歴から削除されます。

## バージョン履歴のクリア

バージョン履歴をクリアするには、

1. **File > Clear Revision History**を選択します。
1. **Yes, clear**をクリックします。バージョン履歴がクリアされます。

# ノートブックにおけるコードの言語

## デフォルト言語の設定

ノートブックのデフォルト言語は、ノートブック名の隣にあるボタンに表示されます。
![](https://docs.databricks.com/_images/toolbar.png)

デフォルト言語を変更するには、言語ボタンをクリックし、ドロップダウンメニューから新たな言語を選択します。既存のコマンドが動作し続けるように、以前のデフォルト言語のコマンドは自動で言語マジックコマンドが追加されます。

## ミックス言語

デフォルトでは、セルはノートブックのデフォルト言語を使用します。言語ボタンをクリックし、ドロップダウンから言語を選択することで、セルのデフォルト言語を上書きすることができます。
![](https://docs.databricks.com/_images/cell-language-button.png)

あるいは、セルの先頭に言語マジックコマンド`%<language>`を指定することで、デフォルト言語を上書きすることができます。サポートされているマジックコマンドは、`%python`、`%r`、`%scala`そして`%sql`です。

:::note info
**注意**
言語マジックコマンドを実行する際、コマンドはノートブックに対応する[実行コンテキスト](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E5%AE%9F%E8%A1%8C%E3%82%B3%E3%83%B3%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88)のREPLにディスパッチされます。ある一つの言語で定義される(その言語に対応するREPLに存在する)変数は他の言語のREPLでは使用できません。REPL間では、DBFS上のファイルやオブジェクトストレージ上のオブジェクトのような外部リソースを通じて状態を共有できます。
:::

また、ノートブックはこの他に以下の補助マジックコマンドをサポートしています：

- `%sh`: ノートブック上でシェルコードを実行できます。シェルコマンドが非ゼロのexit statusを持つ場合にセルでエラーを発生させる場合には、`-e`オプションを追加します。 このコマンドはApache Sparkのドライバーノードでのみ実行されます。ワーカーノードでは実行されません。全てのノードでシェルコマンドを実行するには、[init script](https://qiita.com/taka_yayoi/items/88cb46be00a175085f87)を使用します。
- `%fs`: `dbutils`ファイルシステムコマンドを実行できます。詳細は[How to work with files on Databricks](https://docs.databricks.com/files/index.html)を参照ください。
- `%md`: テキスト、画像、数式などと言った様々なドキュメンテーションを行うことができます。詳細は次のセクションを参照ください。

## PythonにおけるSQL構文のハイライトとオートコンプリート

`spark.sql`のようなPythonコマンドの中でSQLを使用する際、SQLのハイライトと[オートコンプリート](#オートコンプリート)を利用することができます。

## PythonノートブックにおけるPythonをネイティブに用いたSQLセル結果の探索

SQLを用いてデータをロードし、Pythonを用いて結果を探索したいと思うかもしれません。DatabricksのPythonノートブックでは、SQL言語セルから得られるテーブルの結果は、自動的にPythonデータフレームとして利用できるようになります。Pythonデータフレームの名前は`_sqldf`となります。

:::note info
**注意**
- Pythonノートブックでは、`_sqldf`は自動で保存されずSQLセルの最新の実行結果で置き換えられます。データフレームを保存するには、Pythonセルで以下のコードを実行します。

```py:Python
new_dataframe_name = _sqldf
```

- クエリーで[ウィジェット](https://qiita.com/taka_yayoi/items/4df1fd723bdab9a99b08)のパラメータ化を使用している場合、結果をPythonデータフレームとして利用することはできません。
- クエリーで`CACHE TABLE`や`UNCACHE TABLE`を使用している場合、結果をPythonデータフレームとして利用することはできません。
:::

以下にサンプルのスクリーンショットを示します。
![](https://docs.databricks.com/_images/implicit-df.png)

## SQLセルを並列で実行

インタラクティブクラスターにアタッチされているノートブックでコマンドが実行されている際、現在のコマンドと同時にSQLセルを実行することができます。SQLセルは新規で並列のセッションで実行されます。

セルを並列に実行するには:

1. [セルを実行](https://qiita.com/taka_yayoi/items/68a31fd49203d2c9e96f)します。
1. **Run Now**をクリックします。セルは即座に実行されます。
![](https://docs.databricks.com/_images/parallel-sql-execution.png)

セルは新規セッションで実行されるので、一時ビュー、UDF、[暗黙的なPythonデータフレーム](#pythonノートブックにおけるpythonをネイティブに用いたsqlセル結果の探索)(`_sqldf`)は並列で実行されるセルではサポートされません。さらに、並列実行ではデフォルトのカタログやデータベース名が使用されます。コードで別のカタログやデータベースを参照している場合には、[3レベルの名前空間(`catalog.schema.table`)](https://docs.databricks.com/data-governance/unity-catalog/queries.html#three-level-namespace-notation)を指定しなくてはなりません。

## SQLウェアハウスでSQLを実行

:::note info
**プレビュー**
本機能は[パブリックプレビュー](https://docs.databricks.com/release-notes/release-types.html)です。
:::

SQL分析に最適化された計算資源である[SQLウェアハウス](https://docs.databricks.com/sql/admin/create-sql-warehouse.html)でDatabricksノートブックのSQLコマンドを実行することができます。[SQLウェアハウスでノートブックを使う](https://docs.databricks.com/notebooks/notebook-ui.html#notebook-sql-warehouse)をご覧ください。

# 画像の表示

[FileStore](https://qiita.com/taka_yayoi/items/01d9b69d2f5283d27d96#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AB%E9%9D%99%E7%9A%84%E3%81%AA%E7%94%BB%E5%83%8F%E3%82%92%E5%9F%8B%E3%82%81%E8%BE%BC%E3%82%80)に格納されている画像を表示するには以下の構文を使用します。

```md:Markdown
%md
![test](files/image.png)
```

例えば、FileStoreにDatabricksロゴの画像ファイルを格納しているとします。

```bash:Bash
dbfs ls dbfs:/FileStore/
```

```
databricks-logo-mobile.png
```

マークダウンのセルに以下のコードを追加すると:
![](https://docs.databricks.com/_images/image-code.png)
セルに画像がレンダリングされます:
![](https://docs.databricks.com/_images/image-render.png)

# 数式の表示

ノートブックは数式を表示するために[KaTeX](https://github.com/Khan/KaTeX/wiki)をサポートしています。例えば、

```markdown
%md
\\(c = \\pm\\sqrt{a^2 + b^2} \\)

\\(A{_i}{_j}=B{_i}{_j}\\)

$$c = \\pm\\sqrt{a^2 + b^2}$$

\\[A{_i}{_j}=B{_i}{_j}\\]
```
は以下のようにレンダリングされます。
![](https://docs.databricks.com/_images/equations.png)
また、

```markdown
%md
\\( f(\beta)= -Y_t^T X_t \beta + \sum log( 1+{e}^{X_t\bullet\beta}) + \frac{1}{2}\delta^t S_t^{-1}\delta\\)

where \\(\delta=(\beta - \mu_{t-1})\\)
```
は以下のようにレンダリングされます。
![](https://docs.databricks.com/_images/equations2.png)

# HTMLのインクルード

`displayHTML`を使用することで、ノートブックにHTMLを含めることができます。サンプルは[DatabricksノートブックにおけるHTML、D3、SVGの活用](https://qiita.com/taka_yayoi/items/f70bcdb8d717344b72b8)を参照ください。

:::note info
**注意**
`displayHTML`のiframeはドメイン`databricksusercontent.com`から提供され、iframeサンドボックスは`allow-same-origin`属性を含んでいます。あなたのブラウザーから`databricksusercontent.com`にアクセスできる必要があります。企業ネットワークでブロックされている場合には、許可リストに追加する必要があります。
:::

# 他のノートブックへのリンク

マークダウンセルで相対パスを用いることで別のノートブックやフォルダにリンクすることができます。`$`で始まりUnixファイルシステムと同じパターンで相対パスをアンカータグの`href`属性に指定します。

```md:Markdown
%md
<a href="$./myNotebook">Link to notebook in same folder as current notebook</a>
<a href="$../myFolder">Link to folder in parent folder of current notebook</a>
<a href="$./myFolder2/myNotebook2">Link to nested notebook</a>
```

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

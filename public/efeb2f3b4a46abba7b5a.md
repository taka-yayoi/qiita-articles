---
title: Databricksとdbt Cloudの連携
tags:
  - 連携
  - Databricks
  - dbt
private: false
updated_at: '2022-02-28T08:25:39+09:00'
id: efeb2f3b4a46abba7b5a
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[dbt Cloud integration with Databricks \| Databricks on AWS](https://docs.databricks.com/dev-tools/dbt-cloud.html#language-Cluster) [2022/1/20時点]の翻訳です。

本記事の内容を実践した結果をこちらにまとめています。
- [Databricksとdbt Cloudの連携\(実践編その1\)](https://qiita.com/taka_yayoi/items/9995400e17dad2dae4fd)
- [Databricksとdbt Cloudの連携\(実践編その2\)](https://qiita.com/taka_yayoi/items/6a7a1d7d7813e8600606)

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

dbt(data build tool)は、データアナリスト、データエンジニアがシンプルにSELECT文を記述することでデータを変換できるようにする開発環境です。dbtはこれらのSELECT文のテーブル、ビューへの変換を行います。dbtは皆様のコードを生のSQLにコンパイルし、Databricksで指定されたデータベース上でコードを実行します。dbtはコラボレーティブなコーディングパターンと、バージョン管理、ドキュメンテーション、モジュール化といったベストプラクティスをサポートしています。詳細に関しては、dbtのウェブサイトにある[What, exactly, is dbt?](https://blog.getdbt.com/what--exactly--is-dbt-/)や[Analytics Engineering for Everyone: Databricks in dbt Cloud](https://blog.getdbt.com/analytics-engineering-for-everyone-databricks-in-dbt-cloud/)を参照ください。

dbtはデータの抽出やロードは行いません。dbtは「ロード後の変換」アーキテクチャを用いており、変換ステップのみにフォーカスしています。dbtは皆様がお使いのデータベースに既にデータのコピーを格納していることを前提とします。

本書では、dbt Cloudと呼ばれるホストされているバージョンのdbtにフォーカスします。dbt Cloudはジョブのスケジューリング、CI/CD、提供ドキュメント、モニタリングとアラート、統合開発環境(IDE)のターンキーサポートと共に提供されています。dbt CloudのDeveloperプランは一人の開発者が自由に利用できます。Enterprise有料プランも利用することができます。詳細に関してはdbtウェブサイトの[dbt Pricing](https://www.getdbt.com/pricing/)を参照ください。

dbt Coreと呼ばれるローカルバージョンのdbtも利用することができます。dbt Coreでは、お好きなテキストエディタ、あるいはIDEでdbtコードを記述し、コマンドラインからdbtを実行することができます。dbt Coreにはdbtのコマンドラインインタフェース(CLI)が含まれています。[dbt CLI](https://docs.getdbt.com/dbt-cli/cli-overview)は無料で利用することができ、[オープンソース](https://github.com/dbt-labs/dbt)となっています。詳細に関しては[dbt Core integration with Databricks](https://docs.databricks.com/dev-tools/dbt.html)を参照ください。

dbt Cloudとdbt Coreはホストされたgitリポジトリ(例えば、GitHub、GitLab、BitBucket)を使用することができるので、dbt Cloudでdbtプロジェクトを作成し、dbt Coreのユーザーに公開することが可能です。詳細に関しては、dbtウェブサイトの[Creating a dbt project](https://docs.getdbt.com/docs/building-a-dbt-project/projects#creating-a-dbt-project)や[Using an existing project](https://docs.getdbt.com/docs/building-a-dbt-project/projects#using-an-existing-project)を参照ください。

dbtの概要については、以下のYouTube動画(26分)を参照ください。
<iframe width="560" height="315" src="https://www.youtube.com/embed/zoHoIGE6tPc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

# 要件

- Databricks[クラスター](https://qiita.com/taka_yayoi/items/d36a469a1e0c0cebaf1b)に接続する際には、お使いのワークスペースのDatabricks[パーソナルアクセストークン](https://docs.databricks.com/dev-tools/api/latest/authentication.html)が必要です。
- [SQLエンドポイント](https://qiita.com/taka_yayoi/items/23d7789198c2dcd66381#sql%E3%82%A8%E3%83%B3%E3%83%89%E3%83%9D%E3%82%A4%E3%83%B3%E3%83%88%E3%81%AE%E4%BD%9C%E6%88%90)に接続する際には、Databricksの[パーソナルアクセストークン](https://docs.databricks.com/sql/user/security/personal-access-tokens.html#generate)が必要です。

# ステップ1: dbt Cloudにサインアップする

[dbt Cloud \- Signup](https://www.getdbt.com/signup/)にアクセスし、メールアドレス、氏名、会社情報を入力します。パスワードを作成し、**Create my account**をクリックします。

# ステップ2: dbtプロジェクトを作成する

このステップでは、Databricksの[クラスター](https://qiita.com/taka_yayoi/items/d36a469a1e0c0cebaf1b)、あるいは[SQLエンドポイント](https://qiita.com/taka_yayoi/items/23d7789198c2dcd66381#sql%E3%82%A8%E3%83%B3%E3%83%89%E3%83%9D%E3%82%A4%E3%83%B3%E3%83%88%E3%81%AE%E4%BD%9C%E6%88%90)への接続情報、ソースコードを格納するリポジトリ、一つ以上の環境(テスト環境やプロダクション環境など)を含むdbtの*プロジェクト*を作成します。

1. [dbt Cloudにサインイン](https://cloud.getdbt.com/login/)します。
1. ハンバーガーメニューをクリックし、**Account Settings**をクリックします。
1. **New Project**をクリックします。
1. **Begin**をクリックします。
1. **Project Settings**ページの**Name**にプロジェクト固有の名前を入力し、**Continue**をクリックします。
1. **Set Up a Database Connection**ページでは**Databricks**をクリックします。
1. **Name**には接続固有の名前を入力します。
1. 接続先に応じて以下の情報を入力します。

    **クラスター**
    1. **Method**は`ODBC`のままにします。
    1. **Hostname**には、対象のDatabricksクラスターの[Advanced OptionsのJDBC/ODBCタブ](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#connection-details-cluster)の**Server Hostname**の値を入力します。
    1. **Port**には対象のDatabricksクラスターの[Advanced OptionsのJDBC/ODBCタブ](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#connection-details-cluster)の**Port**の値を入力します。
    1. **Organization**は空のままにしておきます。
    1. **Cluster**には対象のDatabricksクラスターのIDを入力します。これは対象のDatabricksクラスターの[Advanced OptionsのJDBC/ODBCタブ](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#connection-details-cluster)の**HTTP Path**の最後のスラッシュ文字(`/`)以降の文字列である必要があります。例えば、`1234-567890-test123`といったものになります。
    1. **Endpoint**は空のままにしておきます。
    1. **User**には`token`と入力します。
    1. **Token**にはDatabricksの[パーソナルアクセストークン](https://docs.databricks.com/dev-tools/api/latest/authentication.html)の値を入力します。
    1. **Schema**には、dbt Cloudがテーブルやビューを作成するデータベースの名前を入力します。(例えば、`default`)
    1. **Test Connection**をクリックします。
    1. テストが成功したら**Continure**をクリックします。

    **SQLエンドポイント**
    1. **Method**は`ODBC`のままにします。
    1. **Hostname**には、対象のSQLエンドポイントの[Connection Details](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#connection-details-sql-endpoint)タブの**Server Hostname**の値を入力します。
    1. **Port**には、対象のSQLエンドポイントの[Connection Details](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#connection-details-sql-endpoint)タブの**Port**の値を入力します。
    1. **Organization**は空のままにしておきます。
    1. **Cluster**は空のままにしておきます。
    1. **Endpoint**には対象のSQLエンドポイントのIDを入力します。これは、対象のSQLエンドポイントの[Connection Details](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#connection-details-sql-endpoint)タブの**HTTP Path**の最後のスラッシュ文字(`/`)以降の文字列である必要があります。例えば、`a123456bcde7f890`といったものになります。
    1. **User**には`token`と入力します。
    1. **Token**にはDatabricksの[パーソナルアクセストークン](https://docs.databricks.com/sql/user/security/personal-access-tokens.html#generate)の値を入力します。
    1. **Schema**には、dbt Cloudがテーブルやビューを作成するデータベースの名前を入力します。(例えば、`default`)
    1. **Test Connection**をクリックします。
    1. テストが成功したら**Continure**をクリックします。

詳細に関しては、dbtウェブサイトの[Connecting to Databricks ODBC](https://docs.getdbt.com/docs/dbt-cloud/cloud-configuring-dbt-cloud/connecting-your-database#odbc)を参照ください。

> **ティップ**
このプロジェクトの設定を参照、変更、あるいはプロジェクトを削除するには、ハンバーガーメニューをクリックし、**Account Settings > Projects**をクリックし、プロジェクトの名前をクリックします。設定を変更するには**Edit**をクリックします。プロジェクトを削除するには**Edit > Delete Project**をクリックします。
>
> このプロジェクトに設定されたDatabricksパーソナルアクセストークンを参照、編集するには人型アイコンをクリックし、**Profile > Credentials**をクリックし、プロジェクト名をクリックします。変更するには、**Edit**をクリックします。

Databricksクラスターに接続した後は、**Set Up a Repository**を行うために画面上の指示に従い、**Continue**をクリックします。

リポジトリをセットアップした後には、ユーザーを招待するための画面上の指示に従い、**Compelete**をクリックします。あるいは**Skip & Complete**をクリックします。

# ステップ3: モデルを作成して実行する

このステップでは、当該データベースに存在するデータに基づいて、データベースに新規ビュー(デフォルト)あるいは新規テーブルを作成する`select`文である*モデル*を作成して実行するためにdbt Cloud IDEを使用します。この手順では、[データサイエンティストとしてDatabricksを使い始める](https://qiita.com/taka_yayoi/items/f7efb6c597b425a05fe2)の[テーブルを作成する](https://qiita.com/taka_yayoi/items/f7efb6c597b425a05fe2#%E3%82%B9%E3%83%86%E3%83%83%E3%83%974-%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B)で説明されている[Databricksデータセット](https://qiita.com/taka_yayoi/items/dcf77d0b007fae774ce5)のサンプル`diamonds`テーブルに基づいてモデルを作成します。この手順では、お使いのワークスペースの`default`データベースにテーブルが既に作成されているものとします。

1. プロジェクトを開き、**Start Developing**をクリックします。
    > **ティップ**
**Start Developing**ボタンが表示されない場合、ハンバーガーメニューの**Develop**をクリックします。

1. **Project**ペインで、**initialize your project**をクリックします。
1. 最初のモデルを作成します：**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `models/diamonds_four_cs.sql`を入力し**Create**をクリックします。
1. `diamonds_four_cs.sql`ファイルで以下のSQL文を入力し**save**をクリックします。この文は`diamonds`テーブルからそれぞれのダイアモンドのcarat、cut、color、clarityのみを選択します。`config`ブロックではdbtに対して、この文に基づいてテーブルをデータベースに作成することを指示します。

    ```
    {{ config(
     materialized='table',
     file_format='delta'
    ) }}
    ```
    
    ```sql:SQL
    select carat, cut, color, clarity
    from diamonds
    ```

    > **ティップ**
    > `merge`インクリメンタル戦略のような追加の`config`のオプションについてはdbtウェブサイトの[Apache Spark configurations](https://docs.getdbt.com/reference/resource-configs/spark-configs/)、GitHubのdbt-labs/dbt-sparkリポジトリの[Usage Notes](https://github.com/dbt-labs/dbt-spark/blob/master/README.md#usage-notes)セクションの「Model Configuration」と「Incremental Models」を参照ください。

1. 2番目のモデルを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `models/diamonds_list_colors.sql`を入力し**Create**をクリックします。
1. `diamonds_list_colors.sql`ファイルで、以下のSQL文を入力し**save**をクリックします。この文は`diamonds_four_cs`テーブルの`colors`カラムの一意の値を取得し、アルファベットの昇順で並び替えを行います。ここでは、`config`ブロックがないので、このモデルはdbtに対してこの文を用いてビューをデータベースに作成するように指示します。

    ```sql:SQL
    select distinct color
    from diamonds_four_cs
    order by color asc
    ```

1. 3つ目のモデルを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `models/diamonds_prices.sql`を入力し**Create**をクリックします。
1. `diamonds_prices.sql`ファイルで、以下のSQL文を入力し**save**をクリックします。この文は色ごとのダイアモンドの平均価格を計算し、平均価格の降順で結果を並び替えます。このモデルはdbtに対してこの文を用いてビューをデータベースに作成するように指示します。

    ```sql:SQL
    select color, avg(price) as price
    from diamonds
    group by color
    order by price desc
    ```

1. モデルを実行します：**Run**ボックスで、上述した3つのファイルのパスを指定して`dbt run`コマンドを実行します。`default`データベースでdbtは`diamonds_four_cs`というテーブルと`diamonds_list_colors`、`diamonds_prices`という2つのビューを作成します。dbtは関連づけられた`.sql`ファイルからビュー名とテーブル名を取得します。

    ```bash:Bash
    dbt run --model models/diamonds_four_cs.sql models/diamonds_list_colors.sql models/diamonds_prices.sql
    ```

    ```:Console
    ...
    ... | 1 of 3 START table model default.diamonds_four_cs.................... [RUN]
    ... | 1 of 3 OK created table model default.diamonds_four_cs............... [OK ...]
    ... | 2 of 3 START view model default.diamonds_list_colors................. [RUN]
    ... | 2 of 3 OK created view model default.diamonds_list_colors............ [OK ...]
    ... | 3 of 3 START view model default.diamonds_prices...................... [RUN]
    ... | 3 of 3 OK created view model default.diamonds_prices................. [OK ...]
    ... |
    ... | Finished running 1 table model, 2 view models ...

    Completed successfully

    Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3
    ```

1. 新たなビューに関する情報を一覧し、テーブルとビューから全ての行を選択するために以下のSQL文を実行します。

クラスターに接続している場合には、ノートブックのデフォルト言語をSQLに指定することで、このSQLコードをクラスターにアタッチしている[ノートブック](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)から実行することができます。SQLエンドポイントに接続している場合には[クエリー](https://docs.databricks.com/sql/user/queries/queries.html#create-a-query)からこのSQLコードを実行することができます。

```sql:SQL
SHOW views IN default
```

```:Console
+-----------+----------------------+-------------+
| namespace | viewName             | isTemporary |
+===========+======================+=============+
| default   | diamonds_list_colors | false       |
+-----------+----------------------+-------------+
| default   | diamonds_prices      | false       |
+-----------+----------------------+-------------+
```

```sql:SQL
SELECT * FROM diamonds_four_cs
```

```:Console
+-------+---------+-------+---------+
| carat | cut     | color | clarity |
+=======+=========+=======+=========+
| 0.23  | Ideal   | E     | SI2     |
+-------+---------+-------+---------+
| 0.21  | Premium | E     | SI1     |
+-------+---------+-------+---------+
...
```

```sql:SQL
SELECT * FROM diamonds_list_colors
```

```:Console
+-------+
| color |
+=======+
| D     |
+-------+
| E     |
+-------+
...
```

```sql:SQL
SELECT * FROM diamonds_prices
```

```:Console
+-------+---------+
| color | price   |
+=======+=========+
| J     | 5323.82 |
+-------+---------+
| I     | 5091.87 |
+-------+---------+
...
```


# ステップ4: より複雑なモデルを作成して実行する

このステップでは、関連するデータテーブルのセットに対してより複雑なモデルを作成します。これらのデータテーブルにはシーズンで6試合を3つのチームが競技する架空のスポーツリーグに関する情報が含まれています。この手順ではデータテーブルを作成し、モデルを作成して実行します。

1. 必要なデータテーブルを作成するために以下のSQL文を実行します。

    クラスターに接続している場合には、ノートブックのデフォルト言語をSQLに指定することで、このSQLコードをクラスターにアタッチしている[ノートブック](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)から実行することができます。SQLエンドポイントに接続している場合には[クエリー](https://docs.databricks.com/sql/user/queries/queries.html#create-a-query)からこのSQLコードを実行することができます。

    このステップのテーブル、ビューの名前は、このサンプルの一部であることがわかるように`zzz_`から始まっています。ご自身のテーブル、ビューを作成する際にはこのパターンに従う必要はありません。

    ```sql:SQL
    DROP TABLE IF EXISTS zzz_game_opponents;
    DROP TABLE IF EXISTS zzz_game_scores;
    DROP TABLE IF EXISTS zzz_games;
    DROP TABLE IF EXISTS zzz_teams;
    
    CREATE TABLE zzz_game_opponents (
    game_id INT,
    home_team_id INT,
    visitor_team_id INT
    ) USING DELTA;
    
    INSERT INTO zzz_game_opponents VALUES (1, 1, 2);
    INSERT INTO zzz_game_opponents VALUES (2, 1, 3);
    INSERT INTO zzz_game_opponents VALUES (3, 2, 1);
    INSERT INTO zzz_game_opponents VALUES (4, 2, 3);
    INSERT INTO zzz_game_opponents VALUES (5, 3, 1);
    INSERT INTO zzz_game_opponents VALUES (6, 3, 2);
    
    /*
    +---------+--------------+-----------------+
    | game_id | home_team_id | visitor_team_id |
    +=========+==============+=================+
    | 1       | 1            | 2               |
    +---------+--------------+-----------------+
    | 2       | 1            | 3               |
    +---------+--------------+-----------------+
    | 3       | 2            | 1               |
    +---------+--------------+-----------------+
    | 4       | 2            | 3               |
    +---------+--------------+-----------------+
    | 5       | 3            | 1               |
    +---------+--------------+-----------------+
    | 6       | 3            | 2               |
    +---------+--------------+-----------------+
    */
    
    CREATE TABLE zzz_game_scores (
    game_id INT,
    home_team_score INT,
    visitor_team_score INT
    ) USING DELTA;
    
    INSERT INTO zzz_game_scores VALUES (1, 4, 2);
    INSERT INTO zzz_game_scores VALUES (2, 0, 1);
    INSERT INTO zzz_game_scores VALUES (3, 1, 2);
    INSERT INTO zzz_game_scores VALUES (4, 3, 2);
    INSERT INTO zzz_game_scores VALUES (5, 3, 0);
    INSERT INTO zzz_game_scores VALUES (6, 3, 1);
    
    /*
    +---------+-----------------+--------------------+
    | game_id | home_team_score | visitor_team_score |
    +=========+=================+====================+
    | 1       | 4               | 2                  |
    +---------+-----------------+--------------------+
    | 2       | 0               | 1                  |
    +---------+-----------------+--------------------+
    | 3       | 1               | 2                  |
    +---------+-----------------+--------------------+
    | 4       | 3               | 2                  |
    +---------+-----------------+--------------------+
    | 5       | 3               | 0                  |
    +---------+-----------------+--------------------+
    | 6       | 3               | 1                  |
    +---------+-----------------+--------------------+
    */
    
    CREATE TABLE zzz_games (
    game_id INT,
    game_date DATE
    ) USING DELTA;
    
    INSERT INTO zzz_games VALUES (1, '2020-12-12');
    INSERT INTO zzz_games VALUES (2, '2021-01-09');
    INSERT INTO zzz_games VALUES (3, '2020-12-19');
    INSERT INTO zzz_games VALUES (4, '2021-01-16');
    INSERT INTO zzz_games VALUES (5, '2021-01-23');
    INSERT INTO zzz_games VALUES (6, '2021-02-06');
    
    /*
    +---------+------------+
    | game_id | game_date  |
    +=========+============+
    | 1       | 2020-12-12 |
    +---------+------------+
    | 2       | 2021-01-09 |
    +---------+------------+
    | 3       | 2020-12-19 |
    +---------+------------+
    | 4       | 2021-01-16 |
    +---------+------------+
    | 5       | 2021-01-23 |
    +---------+------------+
    | 6       | 2021-02-06 |
    +---------+------------+
    */
    
    CREATE TABLE zzz_teams (
    team_id INT,
    team_city VARCHAR(15)
    ) USING DELTA;
    
    INSERT INTO zzz_teams VALUES (1, "San Francisco");
    INSERT INTO zzz_teams VALUES (2, "Seattle");
    INSERT INTO zzz_teams VALUES (3, "Amsterdam");
    
    /*
    +---------+---------------+
    | team_id | team_city     |
    +=========+===============+
    | 1       | San Francisco |
    +---------+---------------+
    | 2       | Seattle       |
    +---------+---------------+
    | 3       | Amsterdam     |
    +---------+---------------+
    */
    ```

1. 最初のモデルを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `models/zzz_game_details.sql`を入力し**Create**をクリックします。
1. `zzz_game_details.sql`ファイルで、以下のSQL文を入力し**save**をクリックします。この文はチーム名やスコアのような試合ごとの詳細情報を提供するテーブルを作成します。`config`ブロックはdbtにこの文に基づいてテーブルをデータベースに作成することを指示します。

    ```sql:SQL
    -- Create a table that provides full details for each game, including
    -- the game ID, the home and visiting teams' city names and scores,
    -- the game winner's city name, and the game date.
    ```

    ```
    {{ config(
      materialized='table',
      file_format='delta'
    ) }}
    ```

    ```sql:SQL
    -- Step 4 of 4: Replace the visitor team IDs with their city names.
    select
      game_id,
      home,
      t.team_city as visitor,
      home_score,
      visitor_score,
      -- Step 3 of 4: Display the city name for each game's winner.
      case
        when
          home_score > visitor_score
            then
              home
        when
          visitor_score > home_score
            then
              t.team_city
      end as winner,
      game_date as date
    from (
      -- Step 2 of 4: Replace the home team IDs with their actual city names.
      select
        game_id,
        t.team_city as home,
        home_score,
        visitor_team_id,
        visitor_score,
        game_date
      from (
        -- Step 1 of 4: Combine data from various tables (for example, game and team IDs, scores, dates).
        select
          g.game_id,
          go.home_team_id,
          gs.home_team_score as home_score,
          go.visitor_team_id,
          gs.visitor_team_score as visitor_score,
          g.game_date
        from
          zzz_games as g,
          zzz_game_opponents as go,
          zzz_game_scores as gs
        where
          g.game_id = go.game_id and
          g.game_id = gs.game_id
      ) as all_ids,
        zzz_teams as t
      where
        all_ids.home_team_id = t.team_id
    ) as visitor_ids,
      zzz_teams as t
    where
      visitor_ids.visitor_team_id = t.team_id
    order by game_date desc
    ```

1. 2つ目のモデルを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `models/zzz_win_loss_records.sql`を入力し**Create**をクリックします。
1. `zzz_win_loss_records.sql`ファイルで、以下のSQL文を入力し**save**をクリックします。この文はシーズンにおけるチームの勝敗記録を一覧するビューを作成します。

    ```sql:SQL
    -- Create a view that summarizes the season's win and loss records by team.
    
    -- Step 2 of 2: Calculate the number of wins and losses for each team.
    select
      winner as team,
      count(winner) as wins,
      -- Each team played in 4 games.
      (4 - count(winner)) as losses
    from (
      -- Step 1 of 2: Determine the winner and loser for each game.
      select
        game_id,
        winner,
        case
          when
            home = winner
              then
                visitor
          else
            home
        end as loser
      from zzz_game_details
    )
    group by winner
    order by wins desc
    ```

1. モデルを実行します：モデルを実行します：**Run**ボックスで、上述した2つのファイルのパスを指定して`dbt run`コマンドを実行します。(プロジェクトの設定で指定した通り)`default`データベースで、dbtは`zzz_game_details`というテーブルと`zzz_win_loss_records `というビューを作成します。dbtは関連づけられた`.sql`ファイルからビュー名とテーブル名を取得します。

    ```bash:Bash
    dbt run --model models/zzz_game_details.sql models/zzz_win_loss_records.sql
    ```

    ```:Console
    ...
    ... | 1 of 2 START table model default.zzz_game_details.................... [RUN]
    ... | 1 of 2 OK created table model default.zzz_game_details............... [OK ...]
    ... | 2 of 2 START view model default.zzz_win_loss_records................. [RUN]
    ... | 2 of 2 OK created view model default.zzz_win_loss_records............ [OK ...]
    ... |
    ... | Finished running 1 table model, 1 view model ...
    
    Completed successfully
    
    Done. PASS=2 WARN=0 ERROR=0 SKIP=0 TOTAL=2
    ```

1. 新規のビューに関する情報を一覧し、テーブルとビューの全ての行を選択するために以下のSQLコードを実行します。

    クラスターに接続している場合には、ノートブックのデフォルト言語をSQLに指定することで、このSQLコードをクラスターにアタッチしている[ノートブック](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)から実行することができます。SQLエンドポイントに接続している場合には[クエリー](https://docs.databricks.com/sql/user/queries/queries.html#create-a-query)からこのSQLコードを実行することができます。

    ```sql:SQL
    SHOW VIEWS FROM default LIKE 'zzz_win_loss_records';
    ```

    ```:Console
    +-----------+----------------------+-------------+
    | namespace | viewName             | isTemporary |
    +===========+======================+=============+
    | default   | zzz_win_loss_records | false       |
    +-----------+----------------------+-------------+
    ```

    ```sql:SQL
    SELECT * FROM zzz_game_details;
    ```

    ```:Console
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    | game_id | home          | visitor       | home_score | visitor_score | winner        | date       |
    +=========+===============+===============+============+===============+===============+============+
    | 1       | San Francisco | Seattle       | 4          | 2             | San Francisco | 2020-12-12 |
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    | 2       | San Francisco | Amsterdam     | 0          | 1             | Amsterdam     | 2021-01-09 |
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    | 3       | Seattle       | San Francisco | 1          | 2             | San Francisco | 2020-12-19 |
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    | 4       | Seattle       | Amsterdam     | 3          | 2             | Seattle       | 2021-01-16 |
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    | 5       | Amsterdam     | San Francisco | 3          | 0             | Amsterdam     | 2021-01-23 |
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    | 6       | Amsterdam     | Seattle       | 3          | 1             | Amsterdam     | 2021-02-06 |
    +---------+---------------+---------------+------------+---------------+---------------+------------+
    ```

    ```sql:SQL
    SELECT * FROM zzz_win_loss_records;
    ```

    ```:Console
    +---------------+------+--------+
    | team          | wins | losses |
    +===============+======+========+
    | Amsterdam     | 3    | 1      |
    +---------------+------+--------+
    | San Francisco | 2    | 2      |
    +---------------+------+--------+
    | Seattle       | 1    | 3      |
    +---------------+------+--------+
    ```

# ステップ5: テストを作成して実行する

> **筆者注**
2021/2/28時点で筆者が確認したところ、dbt Cloudの`dbt test`コマンドは`--schema`、`--data`オプションを受け付けませんでした。コマンド`dbt test`のみでスキーマテスト、データテストが実行されることは確認しています。

このステップでは、モデルに対するアサーションを定義する*テスト*を作成します。これらのテストを実行する際には、皆様のプロジェクトがそれぞれのテストに通過したのか失敗したのかをdbtが教えてくれます。

2種類のテストが存在します。YAMLで記述される*スキーマテスト*はアサーションに通過しなかったレコード数を返却します。この値がゼロの場合、全てのレコードが通過しており、テストに成功したことになります。*データテスト*は通過するためにはゼロを返却すべき特定のクエリーとなります。

1. スキーマテストを作成します：**Project**ペインで**models**フォルダーをクリックし、楕円をクリックして**New File**をクリックします。
1. `models/schema.yml`を入力し**Create**をクリックします。
1. `schema.yml`ファイルで以下の内容を入力し**save**をクリックします。このファイルには、特定のカラムに一意の値が含まれているかどうか、非nullかどうか、特定の値のみが含まれるか、あるいはこれらの組み合わせかどうかを判断するスキーマテストが含まれています。

    ```yaml:YAML
    version: 2
    
    models:
      - name: zzz_game_details
        columns:
          - name: game_id
            tests:
              - unique
              - not_null
          - name: home
            tests:
              - not_null
              - accepted_values:
                  values: ['Amsterdam', 'San Francisco', 'Seattle']
          - name: visitor
            tests:
              - not_null
              - accepted_values:
                  values: ['Amsterdam', 'San Francisco', 'Seattle']
          - name: home_score
            tests:
              - not_null
          - name: visitor_score
            tests:
              - not_null
          - name: winner
            tests:
              - not_null
              - accepted_values:
                  values: ['Amsterdam', 'San Francisco', 'Seattle']
          - name: date
            tests:
              - not_null
      - name: zzz_win_loss_records
        columns:
          - name: team
            tests:
              - unique
              - not_null
              - relationships:
                  to: ref('zzz_game_details')
                  field: home
          - name: wins
            tests:
              - not_null
          - name: losses
            tests:
              - not_null
    ```

1. 最初のデータテストを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `tests/zzz_game_details_check_dates.sql`を入力し**Create**をクリックします。
1. `zzz_game_details_check_dates.sql`ファイルでは、以下のSQL文を入力し、**save**をクリックします。このファイルには、全ての試合が通常のシーズン外で行われたかどうかを決定するデータテストが含まれています。

    ```sql:SQL
    -- This season's games happened between 2020-12-12 and 2021-02-06.
    -- For this test to pass, this query must return no results.
    
    select date
    from zzz_game_details
    where date < '2020-12-12'
    or date > '2021-02-06'
    ```

1. 2つ目のデータテストを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `tests/zzz_game_details_check_scores.sql`を入力し**Create**をクリックします。
1. `zzz_game_details_check_scores.sql`ファイルで以下のSQL文を入力し**save**をクリックします。このファイルには、全てのスコアが負の値か試合が紐づけられているのかを決定するデータテストが含まれています。

    ```sql:SQL
    -- This sport allows no negative scores or tie games.
    -- For this test to pass, this query must return no results.
    
    select home_score, visitor_score
    from zzz_game_details
    where home_score < 0
    or visitor_score < 0
    or home_score = visitor_score
    ```

1. 3つ目のデータテストを作成します：**Project**ペインで**models**フォルダーをクリックし、`...`をクリックして**New File**をクリックします。
1. `tests/zzz_win_loss_records_check_records.sql`を入力し**Create**をクリックします。
1. `zzz_win_loss_records_check_records.sql`ファイルで以下のSQL文を入力し**save**をクリックします。このファイルには、あらゆるチームの勝ち負けの数が負の値か、試合数より多い勝ち試合の数、負け試合の数が存在しないか、あり得る数以上の試合数になっていないのかを決定するデータテストが含まれています。

    ```sql:SQL
    -- Each team participated in 4 games this season.
    -- For this test to pass, this query must return no results.
    
    select wins, losses
    from zzz_win_loss_records
    where wins < 0 or wins > 4
    or losses < 0 or losses > 4
    or (wins + losses) > 4
    ```

1. スキーマテストを実行します：指定するモデルに対してテストを実行するために、**Run**ボックスで`--schema`オプションと`models/schema.yml`ファイルにある2つのモデルの名称を指定して`dbt test`コマンドを実行します。

    ```bash:Bash
    dbt test --schema --models zzz_game_details zzz_win_loss_records
    ```

    ```:Console
    ...
    ... | 1 of 15 START test accepted_values_zzz_game_details_home__Amsterdam__San_Francisco__Seattle [RUN]
    ... | 1 of 15 PASS accepted_values_zzz_game_details_home__Amsterdam__San_Francisco__Seattle [PASS ...]
    ...
    ... |
    ... | Finished running 15 tests ...
    
    Completed successfully
    
    Done. PASS=15 WARN=0 ERROR=0 SKIP=0 TOTAL=15
    ```

1. データテストを実行します：プロジェクトの`test`ディレクトリにあるテストを実行するために、`--data`オプションを指定して`dbt test`コマンドを**Runs**ボックスで実行します。

    ```bash:Bash
    dbt test --data
    ```

    ```:Console
    ...
    ... | 1 of 3 START test zzz_game_details_check_dates....................... [RUN]
    ... | 1 of 3 PASS zzz_game_details_check_dates............................. [PASS ...]
    ...
    ... |
    ... | Finished running 3 tests ...
    
    Completed successfully
    
    Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3
    ```

# ステップ6: クリーンアップ

以下のSQLコードを実行することで、このサンプルで作成したテーブルとビューを削除することができます。

クラスターに接続している場合には、ノートブックのデフォルト言語をSQLに指定することで、このSQLコードをクラスターにアタッチしている[ノートブック](https://qiita.com/taka_yayoi/items/c306161906d6d34e8bd5#%E3%83%8E%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)から実行することができます。SQLエンドポイントに接続している場合には[クエリー](https://docs.databricks.com/sql/user/queries/queries.html#create-a-query)からこのSQLコードを実行することができます。

```sql:SQL
DROP TABLE zzz_game_opponents;
DROP TABLE zzz_game_scores;
DROP TABLE zzz_games;
DROP TABLE zzz_teams;
DROP TABLE zzz_game_details;
DROP VIEW zzz_win_loss_records;

DROP TABLE diamonds;
DROP TABLE diamonds_four_cs;
DROP VIEW diamonds_list_colors;
DROP VIEW diamonds_prices;
```

# 次のステップ

- dbtの[モデル](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)について学ぶ
- dbtプロジェクトの[テスト](https://docs.getdbt.com/docs/building-a-dbt-project/tests)方法を学ぶ
- dbtプロジェクトにおけるSQLプログラミングを行うためのテンプレート言語である[Jinja](https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros)の使い方を学ぶ
- dbt[ベストプラクティス](https://docs.getdbt.com/docs/guides/best-practices)を学ぶ
- dbtのローカルバージョンであるdbt Coreに含まれる[dbt CLI](https://docs.getdbt.com/dbt-cli/cli-overview)を学ぶ

# 追加のリソース

- [dbt Getting Started tutorial](https://docs.getdbt.com/tutorial/setting-up)
- [dbt documentation](https://docs.getdbt.com/docs)
- [dbt \+ Databricks Demo](https://github.com/dbt-labs/dbt-databricks-demo)
- [dbt Discourse community](https://discourse.getdbt.com/)
- [dbt blog](https://blog.getdbt.com/)


### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

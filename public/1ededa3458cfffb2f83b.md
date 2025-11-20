---
title: Databricks Unity Catalogのご紹介：レイクハウスにおけるデータとAIに対するきめ細かいガバナンス
tags:
  - Databricks
  - datacatalog
  - DAIS2021
private: false
updated_at: '2021-06-01T11:58:01+09:00'
id: 1ededa3458cfffb2f83b
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Introducing Databricks Unity Catalog: Fine\-grained Governance for Data and AI on the Lakehouse \- The Databricks Blog](https://databricks.com/blog/2021/05/26/introducing-databricks-unity-catalog-fine-grained-governance-for-data-and-ai-on-the-lakehouse.html)の翻訳です。

> [Data \+ AIサミット2021で発表されたDatabricksの新機能](https://qiita.com/taka_yayoi/items/d4111246048089588cc7)のコンテンツです。

S3、ADLS、GCSのようなデータレイクシステムは、スケーラビリティ、低コスト、オープンなインタフェースを活用することで、現在の企業のデータの大部分を格納しています。そして、高速なクエリーやACIDトランザクションを実現する[Delta Lake](https://databricks.com/product/delta-lake-on-databricks)のような[レイクハウス](https://databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html)技術によってデータを処理するのに魅力的な場所にもなっています。しかし、従来のデータベースと比較して、データレイクが苦手とする領域はガバナンスです。現時点でこれらのシステムは、多くのデータプロフェッショナルには馴染みがないIAMロールのようなクラウド固有のコンセプトを用いた、ファイルレベルでのアクセス権管理ツール(S3 ACLやADLS ACL)を提供するのみです。

こういった状況を受けて、本日[Unity Catalog](https://databricks.com/unity)を発表できることを嬉しく思っています。Unity Catalogは、馴染みのあるオープンなインタフェースを用いて、レイクハウスのデータにきめ細かいガバナンスとセキュリティを提供します。Unity Catalogによって、企業内でレイクハウスを広く安全に利用できるように、ANSI SQLやシンプルなUIできめ細かいデータのアクセス権を管理できるようになります。様々なクラウド、データタイプに対して統合的に動作します。そして、テーブル以外にも機械学習モデルやファイルなどの他のデータセットに対するガバナンスを効かせることが可能です。
![](https://databricks.com/wp-content/uploads/2021/05/unity-catalog-blog-img-1-1024x533.jpg)

# 今のデータレイクガバナンスツールの課題は？

全てのクラウドストレージシステム(S3、ADLS、GCS)は現在でもセキュリティ制御は提供していますが、*ファイル指向*であり、*クラウド固有*です。これはいずれも企業規模の拡大に際して課題となります。我々はお客様が頻繁に以下の4つの課題に直面するのを見てきました。

- **きめ細かい(行、列、ビューレベル)セキュリティの欠如:** クラウドのデータレイクでは一般的にファイルやディレクトレイレベルのアクセス権しか設定ができず、特定のユーザーに対してテーブルの一部のみを共有することは困難でした。これは、全てのテーブルにアクセス権を持つべきではない新規ユーザーが利用を始めるのを妨げていました。
- **物理データレイアウトに縛られたガバナンス:** ガバナンスの制御レベルもファイルレベルであるため、求められるポリシーを適用するために、データチームは注意深くデータレイアウトを構築する必要があります。例えば、国ごとに異なるディレクトリを作成しデータを分割した上で、異なるグループにそれぞれのディレクトリのアクセス権を与えるかもしれません。しかし、ガバナンスのルールが変更された時にデータチームはどうしたらいいのでしょうか？もし、ある国のある州が異なるデータ規制を導入した場合には、企業は全てのデータを再構成しなくてはならない可能性があります。
- **標準化されていないクラウド固有のインタフェース:** IAMのようなクラウドのガバナンスAPIはデータプロフェッショナル(例：データベース管理者)には馴染みがなく、クラウドごとに異なっています。現在、多くの企業が(例えば、プライバシー規制に対応するために)マルチクラウドにデータを格納し始めており、クラウドにまたがるデータを管理する必要性が出てきています。
- **他のデータタイプのサポートの欠如:** データレイクのガバナンスAPIはデータレイクのファイルに対して動作しますが、近代的な企業のワークフローは、様々なタイプのデータアセットを生み出しています。例えば、SQLのワークフローには頻繁にビューが含まれ、データサイエンスワークフローには機械学習モデルが含まれ、多くのワークロードはデータレイク(データベースなど)以外のデータソースと接続するようになっています。近代的な企業の観点では、機微なデータを含んでいる場合には、これら全てのアセットも同様に管理されるべきと言えます。すなわち、データチームは異なるシステムに対して、同じセキュリティポリシーを再実装する必要があると言うことです。

# Unity Catalogのアプローチ

Unity Catalogは、様々なクラウド、データアセットタイプに対応できるオープンな標準を用いて、データガバナンスに対するきめ細かいアプローチを実装することで、これらの問題を解決します。以下の4つの鍵となる原則に従って設計されています。

- **きめ細かいアクセス権:** Unity Catalogではファイルレベルではなく、行、列、ビューレベルでデータのアクセス権を設定することができます。これによって、新規ユーザーに対してデータをコピーすることなしに、常に適切なデータのみを共有することができます。
- **オープンかつ標準化されたインタフェース:** Unity Catalogのアクセス権管理モデルはANSI SQLに準拠しており、データベースの専門家にはなじみ深いものになっています。また、データステュワードが容易にガバナンスを適用できるようにUIを準備しましたし、一つのポリシーを複数のオブジェクトに適用できるように、同じ属性(例：個人情報)を持つオブジェクトにタグ付けできるようSQLモデルを属性ベースのアクセス権管理で拡張しました。最後に、同様のSQLベースのインタフェースは機械学習モデル、外部のデータソースにも適用できます。
- **集中管理:** Unity Catalogは複数のDatabricksワークスペース、リージョン、クラウドに対して動作しますので、企業全てのデータを集中管理することができます。集中管理によって、すべてのアクセスの監査やリネージュの追跡が可能です。
- **あらゆるプラットフォームからのセキュアなアクセス:** 我々はDatabricksプラットフォームを愛していますが、多くのお客様が他のプラットフォームからアクスしており、かつ、お客様のガバナンスルールがそれら含めて動作してほしいと考えていることを知っています。Unity CatalogはJDBC/ODBC、あるいは我々がリリースした多様なプラットフォーム間での大規模データセット交換用プロトコル[Delta Sharing](https://databricks.com/blog/2021/05/26/introducing-delta-sharing-an-open-protocol-for-secure-data-sharing.html)経由でアクセスするあらゆるクライアントに対してもセキュリティ権限を適用します。

それでは、一般的なガバナンスタスクにおいてどのようにUnity Catalogが活用されるのかを見ていきましょう。

# ANSI SQLによる容易な権限管理

Unity CatalogはオープンなANSI SQL標準によるデータ管理言語(DCL)を用いて、クラウドにまたがる全てのデータに対するきめ細かいガバナンスの集中管理を実現します。これはすなわち、管理者は謎めいたクラウド固有のインタフェースを学ぶことなしに、慣れ親しんだSQLを用いて、ユーザーに適したデータサブセットへのアクセス権を設定できることを意味します。また我々は、大規模なデータガバナンス管理をシンプルにできるように、属性に基づいて複数のデータを一括で管理できるよう強力なタグ付けの機能を追加しました。

以下は、データレイクの既存データに対するアクセス権を追加するようにUnity CatalogによるSQLのgrant文の使用例です。

まず、新規あるいは、S3などのクラウドストレージの既存データをクラウド固有の認証情報でポイントして、カタログ内のテーブルを作成します。

**SQL**

```sql
 CREATE EXTERNAL TABLE iot_events LOCATION s3:/...
  WITH CREDENTIAL iot_iam_role
```

他のデータベースと同様に、シンプルにSQL標準の`GRANT`を使用することができます。以下は、どのように`iot_events`を`engineer`のようなグループ全体にアクセス権を設定するのか、dateとcountry列のみを`marketing`に許可する際の例となります。

**SQL**

```sql
GRANT SELECT ON iot_events TO engineers
GRANT SELECT(date, country) ON iot_events TO marketing
```

Unity CatalogではSQLのビューも利用できます。これにより、複雑な処理で生成した集計データに対するSQLビューを作成することが可能です。以下は、ビューベースアクセス権管理で集計結果に対する`business_analysts`のアクセス権を設定する例となります。

**SQL**

```sql
CREATE VIEW aggregate_data AS
  SELECT date, country, COUNT(*) AS num_events FROM iot_events
  GROUP BY date, country

GRANT SELECT ON aggregate_data TO business_analysts
```

さらに、Unity Catalogでは、大規模データガバナンスをシンプルにするために、属性の基づいて(属性ベースのアクセス管理)複数のアイテムに一括でポリシーを適用することが可能です。例えば、複数の列に対してPII(個人情報)のタグを付け、PIIとタグ付けされている全ての列に対するアクセス権を一つのルールで管理することができます。

**SQL**

```sql
ALTER TABLE iot_events ADD ATTRIBUTE pii ON email
ALTER TABLE users ADD ATTRIBUTE pii ON phone

GRANT SELECT ON DATABASE iot_data
  HAVING ATTRIBUTE NOT IN (pii)
  TO product_managers
```

上述の属性のシステムを活用して、MLflowのモデルや他のオブジェクトも管理することができます。

**SQL**

```sql
GRANT EXECUTE ON MODELS HAVING ATTRIBUTE (eu_data)
  TO eu_product_managers
```

# UIによるでデータセットの管理、発見

Unity CatalogのUIを活用することで、データセットの管理、監査、記述の追加、発見が一つの場所で容易に行えます。データステュワード視覚的に全てのアクセス権を設定、検証でき、カタログはそれぞれのデータがどのように生成され、アクセスされるのかを示す監査・リネージュ情報を蓄積します。データの利用者がそれぞれのデータセットに対するドキュメントを記述し、誰が利用しているのかを参照でき、コラボレーションが行われるようにUIが設計されています。
![](https://databricks.com/wp-content/uploads/2021/05/blog-unity-catalog-UI.png)
*Unity Catalog UIを活用することで、データステュワードはコンプライアンスやプライバシー要件に応えるために、レイクハウスのデータアクセスを直接管理することができます*

# Delta Sharingによる企業間データ共有

全ての企業は、コラボレーションするためにお客様、パートナー、サプライヤーとデータを共有する必要に迫られています。Unity Catalogは、使用しているプラットフォーム、クラウドに関係なく企業間でのデータ共有をセキュアに行えるオープンソースの[Delta Sharing](https://delta.io/sharing)標準を実装しています(あらゆるDelta Sharingのクライアントはデータにアクセスすることができます)。
![](https://databricks.com/wp-content/uploads/2021/05/blog-delta-sharing-on-databricks.jpg)

[Delta Sharingのご紹介 : セキュアなデータ共有のためのオープンプロトコル \- Qiita](https://qiita.com/taka_yayoi/items/f93f1b70fef0f75585be)

# アクセスを容易にするオープンなインタフェース

Unity Catalogは、すでにお使いのカタログ、データ、計算資源に適用できますので、これまでの投資を生かしたまま、将来性のあるガバナンスモデルを構築することができます。既存のデータを移動することなしに、Apache HiveのメタストアやS3、ADLS、GCSのようなクラウドストレージとしてマウントすることが可能です。データへのアクセスを管理するためのカスタムワークフローを定義するために、PrivaceraやImmutaのようなガバナンスプラットフォームと接続することも可能です。そして、Databricks以外のプラットフォームからアクセスできるようにUnity Catalogを設計しています。他のプラットフォームからのODBC/JDBCインタフェース経由でのアクセス、あらゆるコンピューティングシステムからセキュアかつ高いスループットでデータを検索できる[Delta Sharing](https://delta.io/sharing)経由でのアクセスが可能です。

# 次のステップ

本日のキーノートでご紹介したように、すぐにUnity Catalogのプレビューを開始する予定です。すでにウェイティングリストに[サインアップ](https://databricks.com/unity)することが可能です。皆様からのフィードバックをお待ちしております！

詳細はData + AIサミットの[キーノート(無料)](https://dbricks.co/3urRADK)でも確認することができます。

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

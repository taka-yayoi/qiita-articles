---
title: DatabricksでワークスペースID、クラスターID、ノートブックID、モデルID、ジョブIDを取得する
tags:
  - Databricks
private: false
updated_at: '2022-02-18T21:05:44+09:00'
id: 7127cabac70dd994fcba
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Get workspace, cluster, notebook, model, and job identifiers \| Databricks on AWS](https://docs.databricks.com/workspace/workspace-details.html#workspace-url) [2021/6/11時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本書では、どのようにしてDatabricksのワークスペースID、クラスターID、ノートブックID、モデルID、ジョブIDを取得するのかを説明します。

# ワークスペースのインスタンス名、URL、ID

それぞれのDatabricksデプロイメントに対して*インスタンス名*が割り振られます。ワークロードを分離し、適切なユーザーに対してのみアクセスを許可するために、Databricksを利用するお客様は通常、開発、ステージング、プロダクションのインスタンスを別々に作成します。インスタンス名は、Databrikcsデプロイメントにログインした際のURLの最初の部分となります。
![](https://docs.databricks.com/_images/workspace-aws.png)

`https://cust-success.cloud.databricks.com/`にログインした場合、インスタンス名は`cust-success.cloud.databricks.com`になります。

Databricksの[*ワークスペース*](https://docs.databricks.com/workspace/index.html)は、Databricksのプラットフォームが動作し、皆様がSparkクラスターを作成し、ワークロードをスケジュールする場所となります。いくつかのタイプのワークスペースにはユニークなワークスペースIDがあります。デプロイメントのURLに`o=`が含まれている場合、例えば、`https://<databricks-instance>/?o=6280049833385130`の場合、`o=`の後のランダムな数字がDatabricksワークスペースIDとなります。ここでは、ワークスペースIDは`6280049833385130 `となります。デプロイメントのURLに`o=`がない場合、ワークスペースIDは`0`となります。

# クラスターのURL、ID

Databricksの[*クラスター*](https://qiita.com/taka_yayoi/items/c5d99cd77fe4bfcf69f0)は、プロダクションETLパイプライン、ストリーミング分析、アドホック分析、機械学習の実行といった様々なユースケースに対する統合プラットフォームを提供します。それぞれのクラスターにはクラスターIDと呼ばれるユニークなIDがあります。これは、all-purposeクラスター、jobクラスターの両方に適用されます。REST APIを用いてクラスターの詳細を取得するには、クラスターIDが重要となります。

クラスターIDを取得するには、サイドバーの**Compute**をクリックし、クラスター名を選択します。クラスターIDは、このページのURLの`/clusters/`以降に表示されます。

```
https://<databricks-instance>/#/setting/clusters/<cluster-id>
```

以下のスクリーンショットでは、クラスターIDは`1115-164516-often242`となります。
![](https://docs.databricks.com/_images/aws-cluster.png)

# ノートブックのURL、ID

[*ノートブック*](https://qiita.com/taka_yayoi/items/24a897cf40bba6d9e305)は実行可能なコード、ビジュアライゼーション、ナラティブなテキストを含むドキュメントに対するwebベースのインタフェースです。ノートブックはDatabricksとインタラクションをするためのインタフェースの一つです。ノートブックのURLにはノートブックIDが含まれており、ノートブックのURLはノートブックに対して固有のものであることを意味します。ノートブックを参照、編集できるDatabricksプラットフォームの他のユーザーと共有することができます。さらに、それぞれのノートブックのコマンド(セル)には異なるURLが割り振られます。

ノートブックURLを取得するには、ノートブックを開きます。ノートブックのセルのURLを取得するには、コマンドのコンテンツをクリックします。
![](https://docs.databricks.com/_images/aws-notebook.png)

このノートブックでは、

- ノートブックのURLは以下の通りです。

```
https://cust-success.cloud.databricks.com/#notebook/333096
```

- ノートブックIDは`333096`になります。
- コマンド(セル)のURLは以下の通りとなります。

```
https://cust-success.cloud.databricks.com/#notebook/333096/command/333099
```

# モデルのID

モデルは、ステージ管理とバージョン管理を通じて、プロダクションでのMLflowモデルを管理することができるMLflow[*登録モデル*](https://qiita.com/taka_yayoi/items/e7a4bec6420eb7069995)を参照するものです。登録モデルIDは、[Permissions API 2\.0](https://docs.databricks.com/dev-tools/api/latest/permissions.html)を通じてプログラムからモデルのアクセス権を変更するために必要となります。

登録モデルのIDを取得するためには、[REST API \(latest\)](https://docs.databricks.com/dev-tools/api/latest/index.html)エンドポイント`mlflow/databricks/registered-models/get`を使用することができます。例えば、以下のコードはIDを含むプロパティとともに登録モデルオブジェクトを返却します。

```bash:Bash
curl -n -X GET -H 'Content-Type: application/json' -d '{"name": "model_name"}' \
https://<databricks-instance>/api/2.0/mlflow/databricks/registered-models/get
```

結果は以下のようなフォーマットになります。

```json:JSON
{
  "registered_model_databricks": {
    "name":"model_name",
    "id":"ceb0477eba94418e973f170e626f4471"
  }
}
```

# ジョブのURL、ID

*[ジョブ](https://qiita.com/taka_yayoi/items/b3275a1983c51a8bbe1a)*はノートブックやJARを即時、あるいはスケジュール実行できる方法を提供します。

ジョブのURLを取得するには、サイドバーの**Jobs**をクリックし、ジョブ名をクリックします。ジョブのURLは、失敗したジョブの実行のトラブルシュートを行い、根本原因を調査するために重要な情報となります。ジョブのIDはURLの`#job/`以降のものとなります。

```
https://cust-success.cloud.databricks.com/#job/25612
```

この例では、ジョブIDは`25612`となります。
![](https://docs.databricks.com/_images/aws-jobs.png)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

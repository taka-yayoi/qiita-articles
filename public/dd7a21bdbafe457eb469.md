---
title: DatabricksノートブックとAzure DevOpsを用いたDatabricks CI/CDの実装：パート2
tags:
  - Databricks
  - MLOps
  - AzureDevOps
  - MLflow
private: false
updated_at: '2022-09-27T19:02:26+09:00'
id: dd7a21bdbafe457eb469
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[How to Implement MLOps on Databricks Using Databricks Notebooks and Azure DevOps \- The Databricks Blog](https://databricks.com/blog/2022/01/05/implementing-mlops-on-databricks-using-databricks-notebooks-and-azure-devops-part-2.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

本記事はノートブックをベースとしたDatabricksにおけるエンドツーエンドのMLOpsフレームワークを説明するブログシリーズの第二弾です。最初の記事では、[ノートブックを用いたDatabricksにおける完全なCI/CDフレームワーク](https://qiita.com/taka_yayoi/items/1b7dc7b64dd06e1892d7)を説明しました。このアプローチは、継続的インテグレーション(CI)に対してはAzure [DevOps](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/ci-cd/ci-cd-azure-devops)のエコシステム、継続的デリバリー(CD)にはRepos APIを用いるものです。本記事では、完全なMLOpsソリューションを提供することで以前に説明したCI/CDフレームワークを拡張します。

本記事は以下のように構成されています。

- MLOps方法論のご紹介
- 開発、デプロイメントライフサイクルにおけるノートブックの活用
- ML固有のテストスイート、バージョン管理、デプロイメント、ステージング、プロダクション環境からなる完全なパイプラインの説明およびコードスニペットを含む詳細なサンプル

# どうしてMLOpsが必要なのか？

人工知能、機械学習は過去20年間において、我々の日々の生活を変化させた大きな現象の一つです。これによって意思決定が自動化されていますが、これら自身が課題とリスクを伴うものであり、やはり、無料の昼食は存在しないと言えます。ソフトウェアの変更のみが影響を与えるのではなく、高品質なデータによってもたらされる良質なモデルも関与するため、MLの本格運用は困難なものとなっています。

さらに、ある企業が真のAIファーストカンパニーになるために、大規模にAIを活用しようとすると、データ、コード、モデルのバージョンはさらに困難なものとなります。単体の機械学習モデルを活用することは、頻繁に繰り返し改善される数千のモデルを活用することとは完全に違うコストとリスクをもたらします。このため、初期のプロタイプから個々のリリース、最終結果に対する複数観点でのテストの繰り返し、エンドユーザーに結果を提供する前の問題検知にいたる、プロダクトライフサイクル全体において全体的なアプローチが必要となります。このプラクティスによってのみ、チームと企業は自身のオペレーションをスケールすることができ、高品質な自律システムをデリバリーすることができます。このMLによって支援されるデータプロダクトに対する開発プラクティスは、MLOpsと呼ばれています。

# MLOpsとは？

DevOpsのプラクティスは、ソフトウェアを高信頼かつ高性能なやり方で、迅速かつイテレーティブにリリースを行うための共通的なITツールボックスと哲学です。このソフトウェアエンジニアリングにおけるデファクトスタンダードは、考慮する必要があるデータと作成されるモデルアーティファクトという新たな複雑性の次元を伴う機械学習プロジェクトにおいては、さらに困難なものとなります。ドリフトと呼ばれるデータにおける変化は、モデルおよびモデルに関連するアウトプットに影響を与えるため、新たな用語であるMLOpsを生み出しました。

簡単に言うとMLOpsは、コードだけではなくデータの変更が起きるシステムのCI/CDプロセスに、新たなツールと方法論を追加することでDevOpsの大部分を継承しつつも拡張するものです。すなわち、ここで必要とされる一連のツールは典型的なソフトウェア開発テクニックに対応しますが、背後にあるデータに対しても同様のプログラム的かつ自動化されたテクニックを追加します。

このように、ビジネス、企業に渡るAI、MLの導入の進展と関連して、最高品質のMLOpsプラクティスとモニタリングに対する要望も高まっています。基本的な機能においては、企業がスケールし、価値を生み出せるようにするための自動化ソリューションに必要となるツール、セーフティネット、信頼性を提供します。Databricksのプラットフォームは、マネージドサービスとして必要な全てのソリューションを具備しており、企業がハイレベルのビジネス課題にフォーカスできるように、テクノロジーを活用し自動化を行うように支援します。
![](https://databricks.com/wp-content/uploads/2021/12/mlops-pt2-blog-img-1-1024x521.png)
*ソース: [martinfowler\.com](https://martinfowler.com/articles/cd4ml.html)*

# どうしてノートブックでのMLOpsの実装が難しいのか？

ノートブックは過去十年間で多大な人気を獲得し、データサイエンスの同義語と言えるくらいになりましたが、アジャイル開発を行う機械学習の実践者が直面する課題が今でもいくつか存在しています。多くの機械学習プロジェクトのルーツは、容易に探索、可視化、データの理解が可能なノートブックに存在しています。コーディングのほとんどは、データサイエンティストがすぐにモデリングのアプローチを実験、ブレーンストーミング、構築、実装でき、コラボレーション可能かつ柔軟性のあるノートブックからスタートします。歴史的には、プロダクションコードはIDEでリファクタリングされ、再実装される必要がありましたが、過去数年間において我々は、プロダクションワークロードにノートブックを使うケースが急増していることを観測しています。コードベースが小さく、管理可能な依存関係であり、大部分がライブラリを活用しているケースであれば、これは通常は実現可能です。この場合、チームはノートブック上でコードの透明性、堅牢性、迅速性を維持しつつも、実装に要する時間を最小化することができます。この劇的なシフトのキーとなる理由には、活用できるCI/CDツールの拡充があります。しかし、機械学習はモジュール/ノートブック間の依存関係を伴うノートブックで提供されるCI/CDパイプラインに対して、新たな複雑性をもたらします。

# MLプロジェクトにおける継続的デリバリー、継続的モニタリング

上の段落では、使用するコードベース、新たにトレーニングされたMLモデルのテスト、品質保証に関するフレームワーク、MLOpsを説明しました。ここでは、以下の原則に従いMLプロジェクトを実装するために、これらのツールをどのように使うのかを議論します。

- モデルのインタフェースは統一されます。`.fit()`を持つscikit-learnと同様に個々のモデルに共通した構造を確立することは、容易に相互変換できる様々なML技術に対するフレームワークの再利用性の観点では重要となります。これによって、シンプルなベースラインMLモデルをエンドツーエンドで活用できる形でスタートし、パイプラインのコードを変更することなしに他のMLアルゴリズムを用いた試行錯誤を行うことが可能となります。
- モデルのトレーニングは、モデルの評価、スコアリングとは分離され、独立したパイプライン/ノートブックとして実装されます。この分離原則によって、コードベースのモジュール化が可能となり、これは繰り返しになりますが、様々なMLアーキテクチャ/フレームワークを比較することができるようになります。これによって、我々は様々なMLモデルを容易に評価でき、昇格させる前にテストを行えるので、この原則はMLOpsにおける重要なものとなります。
- モデルのスコアリングは、常にモデルリポジトリから最新かつ承認されたモデルを取得した上で実施されます。ここでは、テスト済みかつ高性能なモデルが昇格されるMLOpsフレームワークと組み合わせることで、新規データの投入に伴い新たモデルを提供するトレーニングパイプラインを維持しつつも、適正かつ高品質なモデルバージョンが完全に自動化された方法によってプロダクション環境にデプロイされることを保証します。

以下で説明されるアーキテクチャを用いてこれらの要件を満足することができます。
![](https://databricks.com/wp-content/uploads/2021/12/mlops-pt2-blog-img-2-1024x474.png)

上に示すように、トレーニングパイプライン(Training Pipeline:[こちら](https://github.com/mshtelma/databricks_ml_demo/blob/main/jobs/model_trainning_job.py)からコードを確認できます)はモデルをトレーニングし、モデルをMLflowに記録します。異なるモデルアーキテクチャ、異なるモデルタイプに対する複数のパイプラインを保持することが可能です。これらのパイプラインによってトレーニングされた全てのモデルはMLflowに記録され、統一されたMLflowのインタフェースを用いて使用することができます。評価パイプライン(Model Evaluation Pipeline: [こちら](https://github.com/mshtelma/databricks_ml_demo/blob/main/jobs/model_eval_job.py)からコードを確認できます)は、それぞれのトレーニングパイプラインの後に実行され、新たなモデル全てと比較するための比較対象として用いられます。このようにして、候補のモデルは現在のプロダクションモデルとも比較評価することができます。MLflowを用いて実装された理想的な評価パイプラインの例を以下で説明します。

**モデル比較と選択を実装してみましょう！**

完全な機能を実装するためには、いくつかのビルディングブロックが必要となり、ここではこれらを個々の関数として実装します。最初の一つは、MLflowトレーニングパイプラインから全ての新規トレーニング済みモデルを取得するものです。これを行うために、MLflowエクスペリメントデータに対してApache Spark™によるクエリーを実行できる[MLflowエクスペリメントデータソース](https://docs.databricks.com/data/data-sources/mlflow-experiment.html)を活用します。MLflowエクスペリメントデータをSparkデータフレームとして保持できるので、作業が非常に簡単になります。

```py:Python
def get_candidate_models(self):
        spark_df = self.spark.read.format
("mlflow-experiment").load(str(self.experimentID))
        pdf = spark_df.where("tags.candidate='true'")
.select("run_id").toPandas()
        return pdf['run_id'].values
```

モデルを比較するためには、いくつかのメトリクスを検討する必要があります。これは通常ケース固有のものであり、ビジネス要件に合わせる必要があります。以下に示す関数では、モデルをMLflowエクスペリメントから`run_id`を用いてロードし、最新のデータを用いて予測結果を計算します。より厳密な評価においては、ブートストラップ法を適用し、抽出されたサンプルに対する複数のメトリクスを取得し、オリジナルの評価用セットに対しても同じことを繰り返します。そして、モデルを比較するために使用するランダムに抽出されたセットにおけるROC曲線のAUCを計算します。少なくともサンプルの90%において、候補のモデルが現行バージョンを上回る性能を示した場合には、候補モデルをプロダクションに昇格させます。実際のプロジェクトにおいては、これらのメトリクスは注意深く選択する必要があります。

```py:Python
 def evaluate_model(self, run_id, X, Y):
        model = mlflow.sklearn.load_model(f'runs:/{run_id}/model')
        predictions = model.predict(X)
        n = 100
        sampled_scores = []
        score = 0.5
        rng = np.random.RandomState()
        for i in range(n):
            # sampling with replacement on the prediction indices
            indices = rng.randint(0, len(predictions), 
len(predictions))
            if len(np.unique(Y.iloc[indices])) < 2:
                sampled_scores.append(score)
                continue
                
            score = roc_auc_score(Y.iloc[indices], 
predictions[indices])
            sampled_scores.append(score)
        return np.array(sampled_scores)
```

以下の関数では、リスト`run_ids`で指定される複数のモデルを評価し、それぞれに対して複数のメトリクスを計算します。これにより、ベストなメトリクスを示すモデルを特定することができます。

```py:Python
def get_best_model(self, run_ids, X, Y):
        best_roc = -1
        best_run_id = None
        for run_id in run_ids:
            roc = self.evaluate_model(run_id, X, Y)
            if np.mean(roc > best_roc) > 0.9:
                best_roc = roc
                best_run_id = run_id
        return best_roc, best_run_id
```

それでは、これら全てのビルディングブロックをまとめ上げ、全ての新規モデルをどのように評価し、プロダクションにあるモデルとベストモデルを比較するのかを見てみましょう。新規トレーニングモデルの中のベストモデルを特定した後で、MLflow APIを用いて全てのプロダクションモデルバージョンをロードし、新規トレーニングモデルの比較に用いたのと同じ関数を用いて比較を行います。

その後で、ベストなプロダクションモデルのメトリクスと新規ベストモデルのメトリクスを比較し、最新モデルをプロダクションに移行すべきか否かを判断します。ポジティブな結論に至った場合には、MLflowモデルレジストリAPIを用いて、新規ベストモデルを登録し、プロダクションに昇格させます。

```py:Python
cand_run_ids = self.get_candidate_models()
        best_cand_roc, best_cand_run_id = self.get_best_model
		(cand_run_ids, X_test, Y_test)
        print('Best ROC (candidate models): ', np.mean(best_cand_roc))

        try:
            versions = 
mlflow_client.get_latest_versions(self.model_name, 
stages=['Production'])
            prod_run_ids = [v.run_id for v in versions]
            best_prod_roc, best_prod_run_id = 
self.get_best_model(prod_run_ids, X_test, Y_test)
        except RestException:
            best_prod_roc = -1
        print('ROC (production models): ', np.mean(best_prod_roc))

        if np.mean(best_cand_roc >= best_prod_roc) > 0.9:
            # deploy new model
            model_version = 
mlflow.register_model(f"runs:/{best_cand_run_id}/model",
self.model_name)
            time.sleep(5)

mlflow_client.transition_model_version_stage(name=self.model_name, version=model_version.version,

stage="Production")
            print('Deployed version: ', model_version.version)
        # remove candidate tags
        for run_id in cand_run_ids:
            mlflow_client.set_tag(run_id, 'candidate', 'false')
```

# まとめ

この記事では、ノートブックベースのプロジェクトを用いてDatabricksにおけるMLOpsのエンドツーエンドのアプローチを説明しました。この機械学習ワークフローは、データチームのプロジェクトをより自薦的な方法で構造化、バージョン管理するだけではなく、CI/CDツールの実装、実行を劇的にシンプルにするRepos APIをベースとしています。実行環境が完全に分離され、MLによるプロダクションワークロードのセキュリティレベルが高い状態に保たれるアーキテクチャを説明しました。自動テストスイートにフォーカスしたモデルライフサイクル全般に渡るサンプルワークフローについて議論しました。これらの品質チェックは典型的なソフトウェア開発ステップ(ユニット、統合テストなど)をカバーするだけではなく、再トレーニングされたモデルの新たなイテレーションの自動評価にもフォーカスしています。お使いのフレームワークを用いてCI/CDパイプラインが構築され、スムーズにDatabricksレイクハウスプラットフォームと連携でき、エンドツーエンドの機能を提供するインフラストラクチャとコードを実行することができます。Repos APIは、プロジェクトライフサイクルにおけるバージョン管理、コードの構造化、開発をシンプルにするだけではなく、環境間におけるプロダクションアーティファクト、コードのデプロイを行う継続的デリバリーもシンプルにします。これは、Databricksにおける全体的な効率、スケーラビリティを増強する重要な改善であり、ソフトウェア開発体験を劇的に改善するものです。

# 参考資料

1. Github repository with implemented example project: https://github.com/mshtelma/databricks_ml_demo/
1. https://databricks.com/blog/2021/06/23/need-for-data-centric-ml-platforms.html
1. Continuous Delivery for Machine Learning, Martin Fowler, https://martinfowler.com/articles/cd4ml.html,
1. Overview of MLOps, https://www.kdnuggets.com/2021/03/overview-mlops.html
1. Part 1: Implementing CI/CD on Databricks Using Databricks Notebooks and Azure DevOps, https://databricks.com/blog/2021/09/20/part-1-implementing-ci-cd-on-databricks-using-databricks-notebooks-and-azure-devops.html ([日本語訳](https://qiita.com/taka_yayoi/items/1b7dc7b64dd06e1892d7))
1. Introducing Azure DevOps, https://azure.microsoft.com/en-us/blog/introducing-azure-devops/

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

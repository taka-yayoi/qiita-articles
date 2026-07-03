---
title: Spark ConnectにおけるPython依存関係の管理
tags:
  - Spark
  - Databricks
private: false
updated_at: '2024-06-19T09:30:13+09:00'
id: 40aaa04a7c6adfdda6e8
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: d340ce2d6bd2d5b557f5
agreed_posting_campaign_term: true
---
[Python Dependency Management in Spark Connect \| Databricks Blog](https://www.databricks.com/blog/python-dependency-management-spark-connect)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

# Spark ConnectでPythonの依存関係を管理する方法

分散コンピューティング環境におけるアプリケーションの管理は困難になる場合があります。全てのノードにコードの実行に必要な環境が提供されることを確実にし、ユーザーコードの実際の場所を特定することが複雑なタスクとなります。Apache Spark™ではConda、venv、PEXのような様々な手法を提供しています。`--jars`、`--packages`のようなスクリプト送信のオプション、`spark.jars.*`のようなSpark設定や[How to Manage Python Dependencies in PySpark](https://www.databricks.com/blog/2020/12/22/how-to-manage-python-dependencies-in-pyspark.html)をご覧ください。これらのオプションによって、自身のクラスターにおける依存関係をシームレスに対応することができます。

しかし、Apache Sparkにおける依存関係管理の現行サポートには限界があります。依存関係は静的にしか追加できず、実行時に変更できない場合があります。これは、お使いのドライバーを起動する前に常に依存関係を設定しなくてはならないことを意味します。この問題に対応するために、Apache Spark 3.5.0以降では[Spark Connect](https://spark.apache.org/docs/3.5.0/spark-connect-overview.html#spark-connect-overview)でセッションベースの依存関係管理のサポートが導入されました。この新機能によって、実行中に動的にPythonの依存関係をアップデートできるようになります。この記事では、Apache SparkのSpark Connectを用いることで、実行中にPython依存関係をコントロールする包括的なアプローチを議論します。

# Spark Connectにおけるセッションベースのアーティファクト

![](https://www.databricks.com/sites/default/files/inline-images/db-784-blog-img-1.png?v=1699616374)
*それぞれのSpark Connectに対する単一の環境*

Spark ConnectなしにSparkドライバーを使う際、Spark Connectはあとでノードで自動で展開されるアーカイブ(ユーザー環境)を追加し、ジョブを実行する際に必要な依存関係を全てのノードが保持することを保証します。この機能は、分散コンピューティング環境における依存関係の管理をシンプルにし、環境汚染のリスクを最小化し、全てのノードに意図した実行環境を保有することを確実にします。しかし、これはSpark Connectやドライバーが起動する前に静的に一度だけ設定できないので柔軟性を制限しています。

![](https://www.databricks.com/sites/default/files/inline-images/db-784-blog-img-2.png?v=1699616374)
*Sparkセッションごとの分離環境*

Spark Connectを用いることで、接続サーバーの長期にわたる稼働時間と複数のセッションとクライアントが存在することで、それぞれが自身のPythonバージョン、依存関係、環境を持つことで、依存関係の管理はより複雑になります。このアプローチでは、それぞれのセッションは、全ての関連Pythonファイルやアーカイブが格納される専用のディレクトリを持つことになります。Pythonワーカーが起動されると、カレントの作業ディレクトリはこの専用ディレクトリに設定されます。これによって、それぞれのセッションは固有の依存関係セットや環境にアクセスできることを保証し、潜在的な競合を軽減することができます。

# Condaの使用

Condaは多くの人が活用している非常に人気のPythonパッケージ管理システムです。PySparkユーザーは、サードパーティPythonパッケージをパッケージングするために直接Conda環境を活用することができます。これは、再配置可能なConda環境を作成するために設計されたライブラリである[conda\-pack](https://conda.github.io/conda-pack/index.html)を活用することで達成することができます。

以下の例では、セッションベースの依存関係管理を実現するために、ドライバーとエグゼキューターの両方で展開されるパッケージングされたConda環境を作成する様子をデモンストレーションしています。この環境はアーカイブファイルにパッケージングされ、Pythonインタプリタと全ての関連依存関係をキャプチャしています。

```py
import conda_pack
import os

# Pack the current environment ('pyspark_conda_env') to 'pyspark_conda_env.tar.gz'.
# Or you can run 'conda pack' in your shell.

conda_pack.pack()
spark.addArtifact(
    f"{os.environ.get('CONDA_DEFAULT_ENV')}.tar.gz#environment",
    archive=True)
spark.conf.set(
    "spark.sql.execution.pyspark.python", "environment/bin/python")

# From now on, Python workers on executors use the `pyspark_conda_env` Conda 
# environment.

```

# PEXの使用

Spark Connectは、Pythonパッケージを一緒にバンドルするために[PEX](https://pex.readthedocs.io/en/latest/)利用をサポートしています。PEXは自己格納のPython環境を生成するツールです。これは、Condaやvirtualenvと同じように動作しますが、`.pex`ファイル自身が実行可能です。

以下の例では、`.pex`ファイルはそれぞれのセッションで活用されるようにドライバーとエグゼキューターの両方で作成されます。このファイルは、`pex`コマンドを通じて提供される特定のPython依存関係を組み込みます。

```sh
# Pack the current env to pyspark_pex_env.pex'.
pex $(pip freeze) -o pyspark_pex_env.pex
```

`.pex`ファイルを作成したら、あなたのセッションが個別の`.pex`ファイルを使用するように、セッションベースの環境にファイルを配置します。

```py
spark.addArtifact("pyspark_pex_env.pex",file=True)
spark.conf.set(
    "spark.sql.execution.pyspark.python", "pyspark_pex.env.pex")

# From now on, Python workers on executors use the `pyspark_conda_env` venv environment.
```

# Virtualenvの使用

[Virtualenv](https://virtualenv.pypa.io/en/latest/)は、分離されたPython環境を作成するPythonツールです。Python 3.3.0以降、その機能のサブセットは[venv](https://docs.python.org/3/library/venv.html)モジュール配下として、標準ライブラリとしてPythonにインテグレーションされています。venvモジュールは、conda-packと同じような方法で[venv\-pack](https://jcristharif.com/venv-pack/index.html)を用いることで、Pythonの依存関係で活用することができます。以下の例ではvenvによるセッションベースの依存関係を説明しています。

```py
import venv_pack
import os

# Pack the current venv to 'pyspark_conda_env.tar.gz'.
# Or you can run 'venv-pack' in your shell.

venv_pack.pack(output='pyspark_venv.tar.gz')
spark.addArtifact(
    "pyspark_venv.tar.gz#environment",
    archive=True)
spark.conf.set(
    "spark.sql.execution.pyspark.python", "environment/bin/python")

# From now on, Python workers on executors use your venv environment.
```

# まとめ

Apache Sparkでは、Apache Spark 3.5.0における実行中で動的にSpark Connectを用いてPython依存関係の配置と管理を促進するためにConda、virtualenv、PEXを含む複数のオプションを提供しており、静的なPython依存関係管理の制限を打破します。

Databricksノートブックの場合、この問題に対応するためにPython依存関係に対するユーザーフレンドリーなインタフェースを伴うよりエレガントなソリューションを提供しています。さらに、ユーザーは直接[Python依存関係管理のためのpipやConda](https://www.databricks.com/blog/2020/06/17/simplify-python-environment-management-on-databricks-runtime-for-machine-learning-using-pip-and-conda.html)を活用することができます。[Datatabricksのフリートライアル](https://www.databricks.com/jp/try-databricks)ですぐにこれらの機能を活用しましょう。

:::note warn
上述の **Python依存関係管理のためのConda(%conda)** はDatabricks Runtime 13.3で削除されています。
:::

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: 石油工学エンジニアからデータサイエンティストになるためにDatabricksアシスタントを活用する5つの方法
tags:
  - Databricks
  - Databricksアシスタント
private: false
updated_at: '2025-05-12T08:56:54+09:00'
id: f82adba7ee91e84c0f5a
organization_url_name: databricks
slide: false
ignorePublish: false
---
[5 ways to leverage Databricks Assistant to go from Petroleum Engineer to Data Scientist](https://community.databricks.com/t5/technical-blog/5-ways-to-leverage-databricks-assistant-to-go-from-petroleum/ba-p/116567)の翻訳です。

:::note warn
本書は著者が手動で翻訳したものであり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

現在進化し続けているエネルギーのランドスケープにおいて、石油工学エンジニアは従来の貯蔵所管理のはるか先にある予測されなかった課題に直面しています。多くのエンジニアは自分が行いたい分析のタイプを正確に理解していますが、多くの場合、効果的にそれを実装するためのプログラミングに対する自信にかけています。多くの経験豊富なエンジニアはプログラミングの知識やデータ分析のボキャブラリーに欠けており、労働者たちにおける「[データドリブンの心配](https://jpt.spe.org/digital-future-ep-can-lead-data-driven-anxiety)」という状況につながっています。このスキルギャップは、特にスキル向上の時間があまり取れないタフな仕事のため、エンジニアがアクション可能な洞察を得るためにビッグデータを活用する能力の妨げとなっています。この問題が積み重なることで、特化されたデータサイエンスの人材の業界における不足を引き起こし、意思決定プロセスにおけるボトルネックを引き起こしています。Databricksアシスタントは、高度なコーディングの専門性なしに、複雑なデータタスクをシンプルにするAIドリブンのツールによってエンジニアを支援します。自然言語と自動化されたコード生成を活用することで、エンジニアはドメイン固有の問題解決にフォーカスしつつも、生産量減少曲線の自動化や異常検知などの高度な分析を独自に実行することができます。この技術リソースの民主化によって、業界のデジタル改革を加速し、石油工学エンジニアはシームレスに自分の専門性を最先端のデータサイエンスの能力に組み込むことができます。

# インテリジェントなアシスタントの背後にあるエンジン

[Databricksアシスタント](https://www.databricks.com/jp/product/databricks-assistant)はDatabricksの環境にディープに組み込まれたAIを活用したコラボレーターです。他のAIコーディングアシスタントと違い、特にDatabricksデータインテリジェンスプラットフォームを通じたデータの文脈を理解するように設計されており、データワークフローおいて特に価値のあるものとなっています。このアシスタントは、あなたのテーブル、カラム、説明文、あなたの組織におけるデータ資産間の関係性を理解するために、[Unity Catalog](https://www.databricks.com/jp/product/unity-catalog)を活用します。この文脈の認知によって、標準的なAIアシスタントよりも適切かつ生産的なインタラクションを実現します。例えば、過去と予測の石油生産の値を組み合わせるデータセットにおいては、背後のカラムの説明文や他のメタデータによって、アシスタントはこれらのデータセットをどのようにマージするのかを正確に理解し、複雑な結合処理を過去のものとします。

このアシスタントは、Databricksインタフェースを通じてアクセスでき、ノートブック、SQLクエリー、ダッシュボード、ジョブのエラー診断を通じてもアクセス可能であり、あなたが何を作業しているのかに関係なく一貫性のあるサポートを提供します。

![](https://community.databricks.com/t5/image/serverpage/image-id/16227i939839BCB01246EB/image-size/large?v=v2&px=999)

# 未加工のデータから洞察へ: 石油工学分析をシンプルに

石油工学におけるDatabricksアシスタントの適用事例は実際のところ制限がありませんが、このセクションでは分析ジャーニーにおいて、エンジニアが特に取り組むであろういくつかの主要な領域をハイライトします。これらの基本的なユースケースでは、エンジニアがデータ探索から高度な分析に至る日々のタスクにおいて、複雑なコーディングの課題に苦戦するのではなく、自身のドメインの専門性にフォーカスできるように、どのようにアシスタントが支援するのかをデモンストレーションします。

## 効果的なLLMプロンプト作成の基礎

コーディングアシスタントの活用を最大化するためには、はじめにベストなコミュニケーション方法を理解する必要があります。AIアシスタントはときにはあなたの心を読んでいるかのように見え、別の時には期待する結果を全く生成しないことがあります。アシスタントの能力を最大化するためのいくつかのプロンプトのヒントを以下に示します:

1. **具体的かつ文脈を指定する:** 「予測からの生産の乖離を示すクエリーを書いて」と尋ねるのではなく、「北部エリアにおける30日の平均と比較して15%以上石油の生産量が減少している井戸を特定するSQLクエリーを書いて」と指定しましょう。
1. **ステップバイステップの指示を使用する:** 特にエンジニアリングワークフローで共通するマルチステージの分析においては、複雑なタスクを順番のあるステップにブレークダウンしましょう。
1. **few shotプロンプトを活用する:** コードやクエリーをお願いする際には、期待するアウトプットの例を指定しましょう。例えば、カスタム関数をお願いする際には、パラメーターがどのように構成されるのかの例や返却されるべき結果のフォーマットを含めましょう。

## SQL生成

Databricksアシスタントの最もパワフルな能力の一つは、シンプルな自然言語のリクエストから複雑なSQLクエリーを生成するというものです。*データタイプ*や*ウィンドウ関数*のようなSQLのニュアンスに詳しくない石油工学エンジニアにとっては、これによって、データ分析における大きな障壁を取り除き、最終的にはこれらのクエリーをアナリストに書いてもらうという依存性を排除します。

複数の生産関係のデータセットを取り扱う際、日々の生産量と予測生産量の値を組み合わせて、陸上の油井のパフォーマンスをより監視できるようにすることがゴールとなるでしょう。今では、エンジニアはデータインテリジェンスプラットフォームのパワーを通じて、返却して欲しいデータセットをシンプルに説明するだけであり、AIアシスタントはユーザーが文法を全くしならなくても、効率的にSQL文を記述することができます。

**プロンプト:**

> Using _production_df and @type_curve_df. Write a sql query that finds the wells with the largest under-performance deviation in total production volumes between forecasts and actuals in the last 28 days. 

**アウトプット:**

![](https://community.databricks.com/t5/image/serverpage/image-id/16228i5552749672DF5070/image-size/large?v=v2&px=999)

Unity Catalogとデータインテリジェンスプラットフォームのパワーによって、アシスタントは両方のテーブルのメタデータを検証し、(名前が異なっていたとしても)可能性の高いjoinキーを特定し、適切なSQLクエリーを生成します。joinを成功させるために、時にはデータタイプの変換やフォーマットの調整を提案します。

## ビジュアライゼーションの生成

データを視覚的な洞察に変換することは意思決定において重要です。多くのエンジニアは、自身のビジュアライゼーションの能力を限定する可能性のあるツールに縛られています。

オペレーションのプレゼンテーションのためのビジュアライゼーションの準備に慌てふためくのではなく、自然言語で見たいビジュアライゼーションをシンプルに説明すれば、DatabricksのAIアシスタントはあなたの好きなチャートライブラリでコードを生成します。

**プロンプト:**

> Please create a scatter plot visualization using the Ploty framework.  
> 
> First, For each well in the _production_df table I want to find the cumulative sum of ACTUALS_BOPD and compare the the cumulative sum of FORECASTED_BOPD from the @type_curve_df.  
> 
> Second, For the chart, there should be one point per well with forcasts and actuals summed per point. The X axis should be FORECAST and the Y axis should be ACTUALS.  Color the points by PRODUCING_FORMATION from the @dim_all_wells  table.  To get a better idea of what is over or under performing draw a diagonal 45 degree line  to separate wells that are under performing and lightly shade the area under this line in a transparent red. 

**アウトプット:**

![](https://community.databricks.com/t5/image/serverpage/image-id/16226i9BBE53F968D2A696/image-size/large?v=v2&px=999)

アシスタントは、選択したプロットフレームワークで適切に設定されたビジュアライゼーションコードにリクエストを変換し、適切な軸、データの集計、視覚的な要素を選択します。

## 高度な関数開発および計算

[Decline curve analysis](https://www.ihsenergy.ca/support/documentation_ca/Harmony/content/html_files/reference_material/analysis_method_theory/decline_theory.htm) (DCA)は、生産予測において重要であり、最終的には油井が企業の投資に対してどれだけリターンをもたらしているのかの予測に用いられる手法です。これは、これらの予測が足りないかどうかに関する主要な財務的な示唆となります。従来、DCAには特殊なソフトウェアや複雑なコーディングを必要としました。Databricksアシスタントは、シンプルな説明文から洗練されたカーブフィッティングのコードを生成することで、このプロセスを改革します。

例えば、自動化された生産量減少カーブ分析関数を作成するようにプロンプトを与えた際、アシスタントは生産データを標準的なARPS減少モデルに自動でフィットさせるSciPyの[*curve\_fit*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html)関数を活用するPythonコードを生成することができます:

**プロンプト:**

> Wells in the "Bone Spring" formation are not performing to the current forecast. I want to re-forecast these wells. We used the ARPS decline curve calculation of "q_i / pow(1 + b * d * day , 1/b)" when forecasting these wells initially where q_i is the BOPD on day 1 of production, day is DAYS_FROM_FIRST_PRODUCTION.  
>
> Write a function that solves this for the Bone Spring wells.  You can just average production volumes over a single days from first production.  You should only need to use the _production df and @dim_all_wells tables.  Once the new curve parameters have been calculated show the average actuals vs the new forecasted volumes in a plotly chart. 

このプロンプトは、リクエストされたビジュアライゼーションと以下のフィッティングされたパラメーターを生成するコードを書き出します。

**アウトプット:**

```
Fitted parameters for Bone Spring formation: 
q_i = 5708.8096382592, b = 0.7453919466040444, d = 0.009918253305723445
```

![](https://community.databricks.com/t5/image/serverpage/image-id/16229i26DE1F0A0AE00CD9/image-size/large?v=v2&px=999)

この例ではDCAに踏み込んでいますが、カスタムの計算処理や関数には制限がありません。必要な変換処理や計算処理を説明し、Databricksアシスタントが取り組み始めるのを見守りましょう。

この能力は、かつては数日を要した専門的な開発やカスタムソフトウェアを、AIアシスタントの数分の会話に変化させ、すべてのエンジニアに高度な分析テクニックを民主化し、最終的には効率性のゲインによって企業の時間とコストを節約します。

## レガシーコードの近代化

多くの石油工学エンジニアの組織は、重要な分析のたえのワークブックに埋め込まれたレガシーなVBAスクリプトに依存しています。機能はしますが、これらのソリューションの維持は困難であり、バージョン管理が欠如しており、モダンなデータプラットフォームとは連携していません。Databricksアシスタントはこのレガシーコードの近代化を得意としています。

レガシーなVBAコードをアシスタントのインタフェースにコピーアンドペーストすると、あなたのデータレイクハウスのテーブルに対して動作するPythonコードにクイックに変換することができます。

**プロンプト:**

> I have a legacy excel notebook with some VBA code that follows.  Convert this to a python function and give me an example of how to use:
> 
> ```vb
> Sub ArpsForecast()
>     ' ARPS decline curve calculator
>     Dim qi As Double: qi = Cells(2, "B").Value ' Day 1 production
>     Dim Di As Double: Di = 0.15 ' Decline rate
>     Dim b As Double: b = 0.7 ' Exponent
>     Dim days As Integer: days = [A1048576].End(xlUp).Row - 1
>  
>     For i = 1 To days
>         Cells(i + 1, "C").Value = qi / ((1 + b * Di * i) ^ (1 / b))
>     Next i
> End Sub
> ```

**アウトプット:**

![](https://community.databricks.com/t5/image/serverpage/image-id/16230i1B656AA3C21EF9C0/image-size/large?v=v2&px=999)

VBAからPythonへの移行によって、単なる近代化以上のメリットがもたらされます。石油工学ワークフローのPython実装はVBA以上のパフォーマンスの改善を示しつつも、数多くのワークブックベースのエコシステムで利用できるパワフルなデータサイエンスライブラリとのインテグレーションを可能にします。

## 文法修正

最後かつ石油工学エンジニアに最もインパクトのあるAIアシスタントの活用方法は、開発プロセスにおいて不可避のエラーが発生した時のものです。石油工学エンジニアは表面下物理学を深く理解していますが、コードの構文における問題を診断する能力に関して同じことが言えるわけではありません。幸運なことに、***/fix***コマンドが即座のトラブルシューティングを提供します。コードのエラーに遭遇した際、おそらく複雑なスクリプトにおけるシンプルなPython構文エラーかもしれませんが、「*診断エラー*」ボタンをクリックすることで、アシスタントが解析を行い、問題に対する提案を提供してくれます。

**アウトプット:**

![](https://community.databricks.com/t5/image/serverpage/image-id/16231i0C441AB02A222B03/image-size/large?v=v2&px=999)

アシスタントは、背後の問題の説明とともに、修正内容を示す「diff(差分)」を表示します。これによって、エラーメッセージをイライラする障害やオンラインフォーラムで費やす数時間から価値のある学習機会へと変化させ、石油工学エンジニアが実践的な問題解決を通じてデータサイエンススキルを向上させる助けとなります。

# まとめ

Databricksアシスタントを石油、ガスエンジニアリングワークフローに組み込むことで、エンジニアがデータとどのようにやり取りするのかにおけるパラダイムシフトをもたらします。技術的な障壁を取り除くことで、エンジニアはコードの構文に苦戦するのではなく、ドメイン固有の問題の解決にフォーカスすることができます。最近の[調査](https://www.databricks.com/jp/blog/research-survey-productivity-benefits-databricks-assistant)では、アシスタントを活用するユーザーは従来の手動によるコーディングアプローチよりも最低でも30%高速にデータ分析タスクを完了しており、数日の開発を数時間の会話に変革しています。

石油工学エンジニアがデータサイエンススキルを獲得するジャーニーは一夜で起きることではありませんが、Databricksアシスタントはその移行を劇的に加速します。このAIを活用したコラボレーションを受け入れるえんじあは、徐々にデータサイエンスの能力を高めていることに気づくと同時に、強化されたデータ分析を通じて即座の価値を提供することになります



### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

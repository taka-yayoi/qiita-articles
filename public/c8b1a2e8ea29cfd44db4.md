---
title: 'フルページGenie Codeを試す: scikit-learnで分析・可視化をプロンプト一発で'
tags:
  - scikit-learn
  - Databricks
  - 生成AI
  - AIエージェント
  - GenieCode
private: false
updated_at: '2026-06-09T18:26:23+09:00'
id: c8b1a2e8ea29cfd44db4
organization_url_name: databricks
slide: false
ignorePublish: false
---
# はじめに

Databricksの開発者向けAIコーディングアシスタントである[Genie Code](https://docs.databricks.com/aws/ja/genie-code/)に、新たに全画面表示の「フルページGenie Code」が追加されました(2026年6月時点でベータ版)。

これまでのGenie Codeは、ノートブックやSQLエディターなどのアセットの横にサイドペインとして表示される形が中心でした。フルページGenie Codeでは、アクティブなスレッドを画面の主役として大きく表示し、必要に応じてノートブックやファイルを横にタブとして開くことができます。複数のスレッドを並行して走らせられるため、コマンドセンターのような操作感が得られます。

本記事では、フルページGenie Codeの概要と有効化方法を整理したうえで、「scikit learnで分析、可視化を行うサンプルを作って実行してください」というプロンプトで実際に動作確認した様子を紹介します。

# フルページGenie Codeとは

[フルページGenie Code](https://docs.databricks.com/aws/ja/genie-code/full-page)は、全画面のコマンドセンター型エクスペリエンスです。アクティブなスレッドが目立つように表示され、ノートブックやファイルといったアセットが必要に応じてタブとして横に並びます。

主な特徴は次のとおりです。

- Genie Codeから直接作業を開始できる(ノートブックなどのアセットを起点にしなくてよい)
- 複数のスレッドを並行して実行でき、バックグラウンドで動作中のスレッドを切り替えながら作業できる
- スキル、カスタム指示、MCPサーバーを使ってGenie Codeの動作をパーソナライズできる

ドキュメントでは、ゼロから作業を始める場合や複数のタスクを並行して進める場合に、フルページが推奨エクスペリエンスとされています。一方で、既存のアセットを中心に作業する場合(ノートブックのデバッグ、エンドポイントのモニタリング、Unity Catalogでのテーブル探索など)には、従来の[サイドペイン](https://docs.databricks.com/aws/ja/genie-code/use-genie-code#pane)が便利な代替手段になります。用途に応じて使い分けるとよさそうです。

# 有効化と全画面での開き方

フルページGenie Codeはベータ版のため、利用する前にプレビューを有効化する必要があります。ワークスペースのプレビューポータルで「フルページGenie Code」をオンにしてください。手順の詳細は[Databricksプレビューの管理](https://docs.databricks.com/aws/ja/admin/workspace-settings/manage-previews)を参照してください。

![Screenshot 2026-06-09 at 14.50.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6a348069-e370-46af-a748-b9e07d16e2fd.png)

有効化したあと、フルページGenie Codeを開く方法は2通りあります。

- Genie Codeサイドペインの「最大化」ボタンをクリックする
- ワークスペースのホームページからGenie Codeにプロンプトを入力し、「コード」を選択する

![Screenshot 2026-06-09 at 14.50.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0dda41c6-130c-42f9-8dd7-e93fcfce06b4.png)

![Screenshot 2026-06-09 at 18.16.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f0412846-d230-43b1-856d-cbe5a8225ca6.png)

新しいスレッドを開始して、やりたいことを説明します。Genie Codeはスレッド内でタスクに直接働きかけ、分析を実行しながら変更を加えていきます。ノートブックやファイルなど特定のアセットを編集・実行する必要がある場合、そのアセットはスレッドと並んでタブとして開かれ、内容を確認できます。なお、AI/BIダッシュボードなど一部のアセットでは、Genie Codeがそのページに移動して編集を行い、スレッドをサイドペインとして維持することがあります。

# 画面構成

フルページGenie Codeの画面は、主に次の要素で構成されます。

- スレッドリスト: すべてのGenie Codeスレッドが一覧表示されます。各エントリには、スレッドのタイトル、最後にプロンプトを送信した日時、Genie Codeが実行した最新アクションの要約、変更されたアセットの数と変更されたコード行数が表示されます。項目をクリックするとスレッドを切り替えられ、実行中やノートブック編集中でも切り替え可能です。各スレッドはケバブメニューから共有、コピー作成、名前変更、削除ができます。
- スレッド表示: Genie Codeが動作するアクティブなスレッドです。生成されたアセットは、スレッドの横にタブとして開かれるか、アセットページにリダイレクトされます。
- カスタマイズ: 「Customization」から[エージェントスキル](https://docs.databricks.com/aws/ja/genie-code/skills)の追加、[カスタム指示](https://docs.databricks.com/aws/ja/genie-code/instructions)の設定、[MCPサーバー](https://docs.databricks.com/aws/ja/genie-code/mcp)の接続ができます。
- 検索: 過去のスレッドを検索して、すばやく見つけて作業を再開できます。

![Screenshot 2026-06-09 at 14.50.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a6a9ca87-2f65-45b9-bbbc-601a7add20b7.png)

# 動作確認: scikit-learnで分析・可視化

実際にフルページGenie Codeを開き、次のプロンプトを入力して動作を確認しました。

なお、今回試した範囲では、コードを実行させるにはノートブックを開いた状態でフルページに切り替える必要がありました。ホームページからプロンプトを入力して開くのではなく、ノートブックのサイドペインから「最大化」してフルページに移行することで、ノートブックの実行コンテキストを保持したまま分析・可視化を実行できます。ゼロからスレッドを立ち上げる用途ではフルページが推奨とされていますが、コードの実行まで任せたい場合は、実行先となるノートブックを開いておくとよさそうです。

```
scikit learnで分析、可視化を行うサンプルを作って実行してください
```

![Screenshot 2026-06-09 at 14.55.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/25b5aa63-0a9c-4832-8a5e-c3b2e5fd91d0.png)


Genie Codeはスレッド内でタスクの計画を立て、scikit-learnを使った分析と可視化のサンプルコードを生成します。今回試した範囲では、新しいノートブックを作成するのではなく、開いていたノートブックにコードが書き込まれ、そのノートブックがそのまま実行されました。

![Screenshot 2026-06-09 at 14.56.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ec78937e-7492-4140-ae82-aa22a87d7d6d.png)

開いていたノートブックのセルにコードが追加・編集され、実行された結果として分析結果と可視化(グラフ)がノートブック上に出力されました。Genie Codeへの指示と、編集・実行対象のノートブックを同じフルページ画面で並べて確認できるのが、フルページならではの体験です。

![Screenshot 2026-06-09 at 14.56.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/249146d3-92ce-402d-80f8-cb465889ff20.png)
![Screenshot 2026-06-09 at 14.56.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5448c0e5-abb0-4de8-8797-8dd534c999d1.png)

このように、自然言語のプロンプトひとつで、開いていたノートブックに対する「コードの生成」「ノートブックへの書き込み」「実行」「可視化」までを一連の流れとして任せられることが確認できました。新しいノートブックを作るのではなく、あらかじめ開いておいたノートブックが編集・実行される挙動だったため、実行先となるノートブックを用意したうえでフルページに切り替えるのがポイントです。

# 料金に関する注意

ドキュメントによると、2026年7月6日より、Genie製品はユーザーあたりの無料月額許容量が付与された従量課金制の料金体系に移行する予定です。アカウント管理者は[予算とコスト管理の構成](https://docs.databricks.com/aws/ja/genie/budgets)を開始できるようになっています。詳細は[今後の予定](https://docs.databricks.com/aws/ja/release-notes/whats-coming#genie-paygo-pricing)を参照してください。

# まとめ

フルページGenie Codeは、アクティブなスレッドを主役に据え、ノートブックやファイルを横のタブで確認しながら作業できる全画面エクスペリエンスです。複数スレッドの並行実行や、スキル・カスタム指示・MCPサーバーによるパーソナライズにも対応しており、ゼロから作業を立ち上げる場面で特に力を発揮しそうです。

今回試した「scikit learnで分析、可視化を行うサンプルを作って実行してください」というシンプルなプロンプトでも、コード生成からノートブック作成、実行、可視化までをスムーズにこなしてくれました。ベータ版ではありますが、データ分析の入口として手軽に試せる機能だと感じました。まだ有効化していない方は、プレビューポータルからオンにして試してみてください。

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

---
title: Databricksデータ共有ガイド
tags:
  - Databricks
  - DeltaSharing
private: false
updated_at: '2022-08-29T15:23:39+09:00'
id: bfa1c940af3fddd3201c
organization_url_name: databricks
slide: false
ignorePublish: false
---
[Data sharing guide \| Databricks on AWS](https://docs.databricks.com/data-sharing/index.html) [2022/8/25時点]の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

このガイドでは、Databricksのデータを企業外の受信者と共有するために[Delta Sharing](https://qiita.com/taka_yayoi/items/3a53516c4434c0ee76f0)をどのように使用するかを説明します。

[Delta Sharing](https://qiita.com/taka_yayoi/items/3a53516c4434c0ee76f0)は、使用しているコンピューティングプラットフォームに関係なく、他の企業とセキュアにデータ共有するためにDatabricksによって開発されたオープンプロトコルです。

[Unity Catalog](https://qiita.com/taka_yayoi/items/15aede468bdca58ec6a3)は、Databricksによって開発されたセキュアなメタストアです。企業データのメタデータとガバナンスを集中管理します。Unity Catalogを用いることで、企業で使用しているワークスペースの数やBIツールの数に関係なしに、必要に応じてデータガバナンスのルールをスケールさせます。[Unity Catalogを使い始める](https://qiita.com/taka_yayoi/items/3f2df6ddea81521ee786)をご覧ください。

Delta Sharingを使い始めるには以下の作業を行います。

1. Unity Catalogのメタストアにデータをロードします。

    メタストアで新規テーブルを作成するか、ワークスペースローカルのHiveメタストアからUnity Catalogに既存テーブルをインポートすることができます。
1. メタストアでDelta Sharingを有効化します。
1. 共有(share)と受信者(recipient)を作成します。共有と受信者はDelta Sharingのオブジェクトです。

    - *共有*は1つ以上の受信者と共有されるテーブルとテーブルパーティションの読み取り専用のコレクションです。メタストアには複数の共有を含めることができ、どの受信者がそれぞれの共有にアクセスできるのかをコントロールすることができます。一つのメタストアには複数の共有を含めることができますが、それぞれの共有は一つのメタストアにのみ属することができます。共有を削除すると、その共有のすべての受信者はアクセスする権限を失います。
    - *受信者*は組織が一つ以上の共有にアクセスできるようにする資格情報を伴って組織と関連づけられるオブジェクトです。受信者を作成すると、当該受信者に対してダウンロード可能な資格情報が生成されます。それぞれのメタストアには、複数の受信者を含めることができますが、それぞれの受信者は一つのメタストアにのみ属することができます。受信者は複数の共有にアクセスすることができます。受信者を削除すると、これまでアクセスできていたすべての共有へのアクセス権を失います。

1. 受信者を作成し、共有への受信者のアクセスを許可した後は、受信者とコミュニケーションするためにセキュアなチャネルを用い、資格情報をダウンロードできるユニークなURLを共有します。

    資格情報は一度のみダウンロードすることができます。ダウンロードした資格情報を格納、共有するためにパスワードマネージャを使用することをお勧めします。

    また、[Delta Sharingのデータ受信者](https://qiita.com/taka_yayoi/items/f45b77984c3ed4b6a0c0)向けのドキュメントを共有します。あなたが共有したデータにアクセスするために、彼らはこのドキュメントを活用することができます。

1. 任意のタイミングで、共有のコンテンツを変更することができ、受信者がどの共有にアクセスできるのかを変更することができ、共有や受信者を削除することができます。
1. データ受信者は即座にライブかつ最新のデータに対して読み取り専用アクセスを持つことになります。
1. データ提供者は、誰が共有や受信者を作成し、どの受信者がどの共有にアクセスしているのかを理解するためにDelta Sharingの[監査ログを有効化](https://qiita.com/taka_yayoi/items/3a53516c4434c0ee76f0#delta-sharing%E3%81%AE%E3%83%AA%E3%82%BD%E3%83%BC%E3%82%B9%E3%81%AB%E5%AF%BE%E3%81%99%E3%82%8B%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%81%A8%E3%82%A2%E3%82%AF%E3%83%86%E3%82%A3%E3%83%93%E3%83%86%E3%82%A3%E3%81%AE%E7%9B%A3%E6%9F%BB)することができます。
1. Delta SharingのデータにアクセスするためにDatabricksを使用するデータ受信者は、誰がどのDelta Sharingデータにアクセスしているのかを理解するために[監査ログを有効化](https://qiita.com/taka_yayoi/items/f45b77984c3ed4b6a0c0#delta-sharing%E3%83%AA%E3%82%BD%E3%83%BC%E3%82%B9%E3%81%AB%E5%AF%BE%E3%81%99%E3%82%8B%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%81%A8%E3%82%A2%E3%82%AF%E3%83%86%E3%82%A3%E3%83%93%E3%83%86%E3%82%A3%E3%81%AE%E7%9B%A3%E6%9F%BB)することもできます。

このガイドでは以下をカバーします。

- [Delta Sharingによるデータ共有](https://qiita.com/taka_yayoi/items/3a53516c4434c0ee76f0)
- [Delta Sharingによる共有データへのアクセス](https://qiita.com/taka_yayoi/items/f53f8ca708e427227b60)
- [Delta Sharingを用いたデータの共有・アクセスのトラブルシュート](https://qiita.com/taka_yayoi/items/f1c4b3e5b45489ee6aa2)
- [Delta Sharing IP access list guide](https://docs.databricks.com/data-sharing/delta-sharing/access_list.html)
- [DatabricksマネージドのDelta Sharing](https://qiita.com/taka_yayoi/items/8bdd7feed96ac8f206fe)

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)

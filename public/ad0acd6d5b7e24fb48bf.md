---
title: Databricksワークスペースのデフォルト権限をコンシューマーアクセスに変更する際の注意点と運用設計
tags:
  - Databricks
private: false
updated_at: '2026-01-09T16:38:50+09:00'
id: ad0acd6d5b7e24fb48bf
organization_url_name: databricks
slide: false
ignorePublish: false
---
# はじめに

Databricksワークスペースでは、新規ユーザーが追加されると自動的に`users`グループのメンバーとなり、ワークスペースアクセス権限やDatabricks SQLアクセス権限が付与されます。これにより、ユーザーはノートブックやダッシュボードなどのオブジェクトを作成・編集できるようになります。

しかし、BIダッシュボードの閲覧のみを目的としたユーザーを大量にオンボードする場合、全員にデフォルトで作成権限を与えるのはセキュリティ上望ましくありません。そこで登場したのが「デフォルトのワークスペースアクセスをコンシューマーアクセスに変更する」機能です。

https://docs.databricks.com/aws/ja/security/auth/change-default-workspace-access

本記事では、この機能の仕組みと注意点、推奨される運用方法について解説します。

# コンシューマーアクセスとは

https://docs.databricks.com/aws/ja/ai-bi/consumers/

コンシューマーアクセスは、ユーザーに「閲覧専用」の体験を提供する権限レベルです。コンシューマー権限のみを持つユーザーは以下のことができます。

- 共有されたダッシュボードの閲覧・操作
- Genie spacesの利用
- Databricks Appsの利用

一方で、以下のことはできません。

- ノートブックの作成・編集
- クエリの作成
- ジョブの作成
- その他ワークスペースオブジェクトの作成

コンシューマーユーザーのランディングページは「Databricks One」となり、シンプルな消費者向けインターフェースが提供されます。

# 機能の仕組み

この機能は「グループのクローン」という手法で、既存ユーザーへの影響を最小限に抑えながらデフォルト権限を変更します。

## 変更前の状態

```
users グループ
├── 権限: ワークスペースアクセス, Databricks SQLアクセス
└── メンバー: 全ワークスペースユーザー(自動)
```

## 変更後の状態

```
users グループ
├── 権限: コンシューマーアクセスのみ
└── メンバー: 全ワークスペースユーザー(自動) ← 新規ユーザーはここに入る

workspace-contributors グループ(新規作成)
├── 権限: ワークスペースアクセス, Databricks SQLアクセス
└── メンバー: 既存ユーザー全員 ← クローン時に移動
```

## クローン処理の流れ

1. 新しいグループ(例: `workspace-contributors`)を作成
2. 元の`users`グループの権限を新グループにコピー
3. 既存ユーザー全員を新グループに追加
4. `users`グループの権限をコンシューマーのみに変更

この仕組みにより、既存ユーザーは新グループ経由で従来どおりの権限を維持し、以降の新規ユーザーのみがコンシューマー権限でスタートします。

# 設定手順

## 1. 設定画面を開く

ワークスペース管理者としてログインし、右上のユーザー名から「設定」→「詳細設定」タブを開きます。

![Screenshot 2026-01-09 at 16.00.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/6c48d61b-eedb-4473-af84-9562218cf6e0.png)

## 2. グループのクローンを実行

「アクセス制御」セクションの「デフォルトのワークスペースアクセスをコンシューマーアクセスに変更」の横にある「開く」をクリックします。

ダイアログが表示されたら、クローン先のグループ名を入力します。既存ユーザーの権限を維持するグループなので、`workspace-contributors`や`creators`など、役割がわかる名前を推奨します。

![Screenshot 2026-01-09 at 16.03.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/2af06931-ff51-43e2-8976-e0f0058bee94.png)


## 3. ネストされたグループの処理

`users`グループにネストが深いグループが含まれている場合、処理方法を選択するダイアログが表示されます。

- **すべてのグループメンバーを直接追加(推奨)**: ネストを解除してメンバーを直接追加
- **除外**: そのネストされたグループをスキップ

## 4. 完了確認

処理が完了すると、サマリーが表示されます。

![Screenshot 2026-01-09 at 16.03.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7ded0dcd-2b54-4c4d-bb12-47df9a619d96.png)
![Screenshot 2026-01-09 at 16.03.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0dc8e796-16d6-44a4-8628-5efeebe27b95.png)
![Screenshot 2026-01-09 at 16.09.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/db86711c-bf54-4107-a0df-f73434e817d4.png)

## 5. 変更の確認

「設定」→「IDとアクセス」→「グループ」で以下を確認します。

- 新しいグループが作成され、既存ユーザーが含まれている
- `users`グループの権限がコンシューマーのみになっている

![Screenshot 2026-01-09 at 16.33.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/74c68562-365d-4d40-a7fe-8b1d975f45f9.png)

![Screenshot 2026-01-09 at 16.26.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b9b118c0-927b-448c-bf02-192113c14e7e.png)
![Screenshot 2026-01-09 at 16.27.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1678faa2-2994-4a03-a091-b9ae4c2f0b43.png)

# 注意点

## 1. 新規ユーザーへの即時影響

設定変更後、ワークスペースに追加されるすべての新規ユーザーはコンシューマー権限のみとなります。作成権限が必要なユーザーは、手動でクローンしたグループに追加する必要があります。

![Screenshot 2026-01-09 at 16.26.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/734a5262-33ee-4782-8693-8898cc8f5d86.png)

新規ユーザーがDatabricksにログインすると[Databricks One](https://docs.databricks.com/aws/ja/workspace/databricks-one)の画面が表示されます。

![Screenshot 2026-01-09 at 16.25.33.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4e31f8e4-ee36-4f38-8a3e-9aa0a9dd1571.jpeg)


## 2. SCIMプロビジョニングとの連携

IdP(Okta、Azure AD等)からSCIMでユーザーを同期している場合、新規プロビジョニングされたユーザーも自動的にコンシューマー権限のみとなります。

対応策として以下のいずれかを検討してください。

- IdP側でクローンしたグループ(例: `workspace-contributors`)へのグループ割り当てを設定
- Databricks側で手動でグループメンバーシップを管理
- 自動化スクリプトでグループ割り当てを制御

## 3. 複数ワークスペース環境

複数のワークスペースがある場合、各ワークスペースで個別に設定が必要です。一貫した運用のため、Python SDKを使った自動化を検討してください(後述)。

## 4. 元に戻す場合

この設定を元に戻すには、`users`グループにワークスペースアクセスとDatabricks SQLアクセス権限を再度付与します。クローンしたグループは必要に応じて保持または削除できます。

# 推奨運用方法

## パターン1: シンプルな手動運用(小規模向け)

新規ユーザーが少ない環境では、作成権限が必要なユーザーを都度クローンしたグループに追加する運用で十分です。

**手順**:
1. 新規ユーザーがワークスペースに追加される(コンシューマー権限)
2. 作成権限が必要な場合、管理者がクローンしたグループに手動追加

**メリット**: シンプル、追加ツール不要
**デメリット**: 管理者の手間、追加漏れのリスク

## パターン2: IdPグループとの連携(中〜大規模向け)

SCIMを使用している環境では、IdP側でグループを定義し、Databricksと同期させる運用を推奨します。

**手順**:
1. IdP側で「Databricks-Contributors」などのグループを作成
2. 作成権限が必要なユーザーをIdPグループに追加
3. SCIMでDatabricksに同期
4. Databricks側でそのグループに適切な権限を付与

**メリット**: IdPでの一元管理、監査証跡
**デメリット**: IdP側の設定変更が必要

## パターン3: SDK自動化(エンタープライズ向け)

複数ワークスペースや複雑な要件がある場合、Databricks SDK for Pythonで自動化します。

ドキュメントにサンプルスクリプトが用意されています。このスクリプトをCI/CDパイプラインやInfrastructure as Codeワークフローに組み込むことで、複数ワークスペースへの一括適用が可能です。

**メリット**: 再現性、複数ワークスペース対応
**デメリット**: 初期構築コスト

## 運用設計のチェックリスト

設定前に以下を確認・決定しておくことを推奨します。

| 項目 | 確認内容 |
|------|----------|
| クローングループ名 | 命名規則の決定(例: `{workspace}-contributors`) |
| 作成権限の付与基準 | どのような役割・条件で作成権限を付与するか |
| 権限付与のフロー | 申請→承認→追加のプロセス設計 |
| SCIMとの整合性 | IdP側のグループ設計との連携方法 |
| 複数ワークスペース | 各ワークスペースでの設定方針の統一 |
| ドキュメント | ユーザー向けの権限申請手順の整備 |

# まとめ

「デフォルトのワークスペースアクセスをコンシューマーアクセスに変更する」機能は、BIコンシューマーの大規模オンボーディングを効率化する強力な機能です。

**この機能が適しているケース**:
- ダッシュボード閲覧専用ユーザーを多数オンボードしたい
- 最小権限の原則を徹底したい
- 作成権限の付与を明示的に管理したい

**設定前に検討すべきこと**:
- 既存の運用フローへの影響
- SCIMとの連携方法
- 作成権限の付与プロセス

適切な運用設計とともに導入することで、セキュリティと利便性を両立したワークスペース管理が実現できます。

# 参考リンク

- [デフォルトのワークスペースアクセスをコンシューマーアクセスに変更する](https://docs.databricks.com/aws/ja/security/auth/change-default-workspace-access)
- [コンシューマーアクセスとは何ですか?](https://docs.databricks.com/aws/ja/ai-bi/consumers/)
- [Databricks Oneとは何ですか?](https://docs.databricks.com/aws/ja/workspace/databricks-one)
- [権限の管理](https://docs.databricks.com/aws/ja/security/auth/entitlements)
- [グループの管理](https://docs.databricks.com/aws/ja/admin/users-groups/manage-groups)
- [SCIMを使用してIDプロバイダーからユーザーとグループを同期する](https://docs.databricks.com/aws/ja/admin/users-groups/scim/)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)

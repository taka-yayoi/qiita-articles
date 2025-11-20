# Qiita Articles

このリポジトリは[Qiita CLI](https://github.com/increments/qiita-cli)を使用してQiita記事を管理するためのものです。

## セットアップ

### 前提条件

- Node.js 18.18.0以上

### インストール

```bash
npm install
```

### Qiita CLIのログイン

1. [Qiitaのトークン発行ページ](https://qiita.com/settings/tokens/new?read_qiita=1&write_qiita=1&description=qiita-cli)でトークンを発行
   - `read_qiita`と`write_qiita`の権限を付与してください
2. 以下のコマンドでログイン

```bash
npx qiita login
```

## 使い方

### 新しい記事を作成

```bash
npx qiita new 記事のベースネーム
```

`public/記事のベースネーム.md`が作成されます。

### 記事をプレビュー

```bash
npx qiita preview
```

ブラウザで http://localhost:8888 にアクセスしてプレビューを確認できます。

### 記事を投稿・更新

特定の記事を投稿:
```bash
npx qiita publish 記事のベースネーム
```

全ての記事を投稿:
```bash
npx qiita publish --all
```

### Qiitaから記事を取得

```bash
npx qiita pull
```

Qiita上の記事をローカルに同期します。

## 記事の構造

記事は`public/`ディレクトリ内にMarkdown形式で保存されます。

```markdown
---
title: 記事タイトル
tags:
  - タグ1
  - タグ2
private: false
updated_at: '2021-07-06T10:22:39+09:00'
id: 記事のユニークID
organization_url_name: 組織名（任意）
slide: false
ignorePublish: false
---

ここに記事本文をMarkdownで記述します。
```

### フロントマターの項目

- `title`: 記事のタイトル
- `tags`: 記事のタグ（配列形式）
- `private`: 限定共有記事にする場合は`true`、公開記事にする場合は`false`
- `id`: QiitaのユニークID（自動生成されるので変更しない）
- `ignorePublish`: `true`にすると`publish --all`でも投稿されない

## GitHub Actionsによる自動投稿

このリポジトリは、`main`または`master`ブランチへのプッシュ時に自動的に記事を投稿・更新するGitHub Actionsワークフローを設定しています。

### セットアップ方法

1. GitHubリポジトリの Settings > Secrets and variables > Actions に移動
2. `QIITA_TOKEN`という名前でQiitaのトークンをシークレットとして追加
3. `main`または`master`ブランチにプッシュすると自動的に記事が投稿されます

## 設定ファイル

### qiita.config.json

```json
{
  "includePrivate": false,
  "host": "localhost",
  "port": 8888
}
```

- `includePrivate`: プレビューに限定共有記事を含めるか
- `host`: プレビューサーバーのホスト
- `port`: プレビューサーバーのポート

## その他のコマンド

```bash
# Qiita CLIのバージョン確認
npx qiita version

# Qiita CLIのヘルプ
npx qiita help

# Qiita CLIのアップデート
npm install @qiita/qiita-cli@latest
```

## リンク

- [Qiita CLI公式ドキュメント](https://github.com/increments/qiita-cli)
- [Markdown記法チートシート](https://qiita.com/Qiita/items/c686397e4a0f4f11683d)
- [良い記事を書くためのガイドライン](https://help.qiita.com/ja/articles/qiita-article-guideline)

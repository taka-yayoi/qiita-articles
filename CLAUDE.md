# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Qiita article management repository using Qiita CLI. It stores technical articles in Markdown format and syncs them with Qiita.com (a Japanese technical knowledge sharing platform). Articles are stored in the `public/` directory with unique ID-based filenames.

## Essential Commands

### Article Management
- `npx qiita new [basename]` - Create a new article (generates public/[basename].md)
- `npx qiita preview` - Preview articles locally in browser (served at http://localhost:8888 by default)
- `npx qiita publish <basename>` - Publish/update a specific article to Qiita
- `npx qiita publish --all` - Publish/update all articles
- `npx qiita pull` - Sync article files from Qiita to local repository

### Other Commands
- `npx qiita version` - Display Qiita CLI version
- `npx qiita login` - Authenticate with Qiita API token
- `npm install @qiita/qiita-cli@latest` - Update Qiita CLI

## Article Structure

Articles are stored in `public/` directory with frontmatter metadata:

```markdown
---
title: Article Title
tags:
  - Tag1
  - Tag2
private: false
updated_at: '2021-07-06T10:22:39+09:00'
id: [unique-hash-id]
organization_url_name: [optional-organization]
slide: false
ignorePublish: false
---
Article content in Markdown...
```

### Key Frontmatter Fields
- `title`: Article title
- `tags`: Array of tags (strings)
- `private`: Boolean (true for draft, false for public)
- `id`: Unique identifier assigned by Qiita (do not modify)
- `ignorePublish`: If true, article won't be published even with `--all` flag

## Configuration

### qiita.config.json
```json
{
  "includePrivate": false,
  "host": "localhost",
  "port": 8888
}
```

- `includePrivate`: Whether to include private articles in preview
- `host`/`port`: Local preview server configuration

## GitHub Actions Integration

The repository uses GitHub Actions for automatic publishing:
- Workflow file: `.github/workflows/publish.yml`
- Triggered on push to `main` or `master` branches
- Requires `QIITA_TOKEN` secret configured in repository settings
- Uses `increments/qiita-cli/actions/publish@v1` action

## Working with Articles

### Creating New Articles
1. Run `npx qiita new article-name` to generate template
2. Edit the generated `public/article-name.md` file
3. Preview locally with `npx qiita preview`
4. Publish with `npx qiita publish article-name` or commit to trigger GitHub Actions

### Editing Existing Articles
- Articles are named with unique hash IDs (e.g., `fa8ba7210b1e9ad0b52c.md`)
- Edit the Markdown content while preserving frontmatter metadata
- Do NOT modify the `id` field
- Update can be done via `npx qiita publish <basename>` or git push

### Synchronizing with Qiita

**重要**: 必ず `--force` オプションを使用すること

```bash
npx qiita pull --force
```

- 通常の `npx qiita pull` はローカルに変更があるファイルをスキップする
- `--force` を使うことでQiitaの内容を確実にローカルに反映できる
- Qiitaで直接編集した記事も正しく同期される
- Commit changes after pull to track in git

### Qiitaで削除された記事の対処

GitHub Actionsで `QiitaNotFoundError: Not found` エラーが発生した場合：

1. Qiitaで削除された記事がローカルに残っている可能性がある
2. 以下のスクリプトで確認：
   ```bash
   python3 << 'EOF'
   import json, os, re
   public_dir = '/Users/takaaki.yayoi/Workspace/qiita-articles/public'
   with open('article_stats.json') as f:
       api_ids = set(json.load(f).keys())
   local_ids = set()
   for fn in os.listdir(public_dir):
       if fn.endswith('.md'):
           with open(f'{public_dir}/{fn}') as f:
               m = re.search(r"^id:\s*'?([a-f0-9]+)'?$", f.read(500), re.M)
               if m: local_ids.add(m.group(1))
   missing = local_ids - api_ids
   print(f"削除済み記事: {missing}" if missing else "なし")
   EOF
   ```
3. 該当ファイルを削除するか、`ignorePublish: true` に設定

### IDフィールドの注意点

- IDはクォートなしで記載: `id: abc123def456`
- クォート付き `id: 'abc123def456'` は問題を引き起こす可能性あり

## Repository Conventions

- All articles must be in `public/` directory
- Article filenames use hash-based IDs assigned by Qiita
- Japanese language content is primary (articles appear to be in Japanese)
- Git-based workflow: changes pushed to main/master are auto-published via GitHub Actions
- 記事の末尾に以下を追加　### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
- Qiitaの記事の書き方は https://qiita.com/Qiita/items/c686397e4a0f4f11683d
- git actionsで記事を公開する前に、別経路で更新された差分を取り込むように公開記事をpullする
- 生成した記事は対象読者の観点でレビューする
- Databricks Community EditionではなくDatabricks Free Edition

## Article Formatting Rules

### Organization Attribution
- **Default organization**: `databricks`
- Unless explicitly instructed to create a personal article, always set `organization_url_name: databricks` in frontmatter
- Example:
  ```yaml
  organization_url_name: databricks
  ```

### Bold Text Formatting (Qiita-specific)
- **Issue**: Bold formatting (`**text**`) does not render correctly in Qiita when the text contains certain symbols (「」『』【】（）・:：etc.)
- **Solution**: Add half-width spaces inside the bold markers
- **Examples**:
  - ❌ Bad: `**生成AI・LLMOpsへの強い注力**`
  - ✅ Good: `** 生成AI・LLMOpsへの強い注力 **`
  - ❌ Bad: `**「最新技術の即座な実装と体系化」**`
  - ✅ Good: `**「最新技術の即座な実装と体系化」** `
- **When to apply**: Always check and fix bold text containing symbols before publishing

## まとめ記事の管理

### まとめ記事一覧
- **その1** (`c6907e2b861cb1070f4d.md`): イベント、チュートリアル、学習コンテンツ、コンセプト
- **その2** (`68fc3d67880d2dcb32bb.md`): ツール連携、Spark、Delta Lake、Unity Catalog、Lakeflow等
- **その3** (`6a39a3fc5d24780b09a0.md`): 機械学習、NLP、生成AI/LLM
- **その4** (`51498e315d95692b243a.md`): AIエージェント、LLMOps、MLflow、Apps、AI/BI

### まとめ記事の更新手順

1. **Qiitaから最新を取得**
   ```bash
   npx qiita pull --force
   ```

2. **統計情報を取得**
   ```bash
   python3 fetch_article_stats.py
   ```

3. **新記事を適切なまとめページに追加**（手動）
   - 日付順（新しい順）で追加
   - フォーマット: `- [YYYY-MM-DD] [タイトル](URL)`

4. **人気マーカーを更新**
   ```bash
   python3 add_popularity_markers.py
   ```
   - 🔥: いいね20件以上 または 閲覧数10,000以上
   - ⭐: いいね10件以上 または 閲覧数5,000以上

5. **コミット・プッシュ**
   ```bash
   git add . && git commit -m "まとめ記事を更新" && git push
   ```

### 自動更新（GitHub Actions）

毎週月曜日の日本時間9時に自動実行されます。

- ワークフロー: `.github/workflows/update-matome.yml`
- スクリプト: `scripts/update_matome.py`
- 手動実行: GitHub Actions画面から「Run workflow」

**自動更新の処理内容:**
1. Qiitaから最新記事をpull
2. 過去30日以内の新記事を検出
3. タイトル・タグからカテゴリを判定し適切なまとめに追加
4. 人気マーカーを更新
5. 自動コミット・プッシュ
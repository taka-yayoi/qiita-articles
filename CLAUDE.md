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
- Use `npx qiita pull` to fetch latest versions from Qiita.com
- This overwrites local files with remote content
- Commit changes after pull to track in git

## Repository Conventions

- All articles must be in `public/` directory
- Article filenames use hash-based IDs assigned by Qiita
- Japanese language content is primary (articles appear to be in Japanese)
- Git-based workflow: changes pushed to main/master are auto-published via GitHub Actions

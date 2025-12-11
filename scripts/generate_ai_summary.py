#!/usr/bin/env python3
"""
生成AIによるDatabricks最新記事まとめと著者傾向分析を自動生成
"""
import os
import requests
from datetime import datetime, timedelta
from openai import OpenAI

# Configuration
QIITA_USER = "taka_yayoi"
ARTICLE_ID = "2af61d3fa992a589ec26"
OUTPUT_FILE = "public/2af61d3fa992a589ec26.md"
DAYS_BACK = 30

# 除外する記事ID（まとめ記事自体など）
EXCLUDE_IDS = {
    "c6907e2b861cb1070f4d",  # まとめ1
    "68fc3d67880d2dcb32bb",  # まとめ2
    "6a39a3fc5d24780b09a0",  # まとめ3
    "51498e315d95692b243a",  # まとめ4
    "57923e2d159a65a22118",  # リリースノート
    "68452723299f90d3c3b8",  # セミナーまとめ
    "2af61d3fa992a589ec26",  # この記事自体
}


def fetch_recent_articles():
    """過去N日間の記事を取得"""
    token = os.environ.get("QIITA_TOKEN")
    if not token:
        raise ValueError("QIITA_TOKEN is not set")

    headers = {"Authorization": f"Bearer {token}"}
    cutoff_date = (datetime.now() - timedelta(days=DAYS_BACK)).isoformat()

    articles = []
    page = 1

    print(f"Fetching articles from the past {DAYS_BACK} days...")

    while True:
        url = f"https://qiita.com/api/v2/users/{QIITA_USER}/items?page={page}&per_page=100"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            break

        items = response.json()
        if not items:
            break

        for item in items:
            # 日付でフィルタ
            if item["created_at"] < cutoff_date:
                # 古い記事に到達したら終了
                print(f"Fetched {len(articles)} recent articles")
                return articles

            # 除外記事をスキップ
            if item["id"] in EXCLUDE_IDS:
                continue

            # Databricksタグでフィルタ
            tags = [tag["name"].lower() for tag in item["tags"]]
            if "databricks" not in tags:
                continue

            articles.append({
                "id": item["id"],
                "title": item["title"],
                "url": item["url"],
                "created_at": item["created_at"][:10],  # YYYY-MM-DD
                "body": item["body"][:3000],  # 最初の3000文字
                "tags": [tag["name"] for tag in item["tags"]],
            })

        page += 1

    print(f"Fetched {len(articles)} recent articles")
    return articles


def summarize_article(client, article):
    """記事を要約"""
    prompt = f"""以下のQiita記事を200文字程度で要約してください。技術的な内容を正確に、簡潔にまとめてください。

タイトル: {article['title']}
タグ: {', '.join(article['tags'])}

本文:
{article['body']}

要約:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing {article['title']}: {e}")
        return f"（要約生成エラー: {article['title']}）"


def generate_trend_analysis(client, articles):
    """著者傾向分析を生成"""
    titles_and_tags = "\n".join([
        f"- [{a['created_at']}] {a['title']} (タグ: {', '.join(a['tags'])})"
        for a in articles
    ])

    prompt = f"""以下は過去1ヶ月間に投稿されたDatabricks関連のQiita記事一覧です。
これらの記事から著者の技術的傾向、注力テーマ、特徴を分析してください。

## 記事一覧（{len(articles)}件）
{titles_and_tags}

## 出力形式
以下の形式でMarkdownで出力してください：

### 主要な注力テーマ
（3-4つのテーマを挙げ、それぞれ箇条書きで説明）

### 技術的特徴
（著者の技術的なアプローチや特徴を箇条書きで）

### 傾向分析（表形式）
| カテゴリ | 主要技術・テーマ | 具体的な取り組み |
（5行程度）

分析:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating trend analysis: {e}")
        return "（傾向分析の生成に失敗しました）"


def generate_article_content(articles, summaries, trend_analysis):
    """記事コンテンツを生成"""
    today = datetime.now().strftime("%Y-%m-%d")

    # フロントマター
    content = f"""---
title: 生成AIによるDatabricks最新記事まとめと著者傾向分析(自動生成)
tags:
  - Databricks
private: false
updated_at: '{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}+09:00'
id: {ARTICLE_ID}
organization_url_name: null
slide: false
ignorePublish: false
---
:::note
過去1ヶ月の記事{len(articles)}件をAPI経由で取得し、生成AIで要約と傾向分析を自動生成しています。すべての処理は自動で行われています。
最終更新: {today}
:::

## 最近の著者の傾向

{trend_analysis}

## 記事ごとの要約

"""

    # 各記事の要約（日付付き）
    for article, summary in zip(articles, summaries):
        content += f"""### [{article['created_at']}] [{article['title']}]({article['url']})
{summary}

"""

    return content


def main():
    # OpenAI クライアント初期化
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)

    # 1. 記事取得
    articles = fetch_recent_articles()
    if not articles:
        print("No articles found")
        return

    # 日付順にソート（新しい順）
    articles.sort(key=lambda x: x["created_at"], reverse=True)

    # 2. 各記事を要約
    print(f"Summarizing {len(articles)} articles...")
    summaries = []
    for i, article in enumerate(articles):
        print(f"  [{i+1}/{len(articles)}] {article['title'][:50]}...")
        summary = summarize_article(client, article)
        summaries.append(summary)

    # 3. 傾向分析を生成
    print("Generating trend analysis...")
    trend_analysis = generate_trend_analysis(client, articles)

    # 4. 記事コンテンツを生成
    print("Generating article content...")
    content = generate_article_content(articles, summaries, trend_analysis)

    # 5. ファイルに保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Article saved to {OUTPUT_FILE}")
    print(f"Total articles: {len(articles)}")


if __name__ == "__main__":
    main()

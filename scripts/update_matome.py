#!/usr/bin/env python3
"""
まとめ記事の自動更新スクリプト
- 新記事をまとめページに追加
- 人気マーカーを更新
"""
import os
import re
import json
import requests
from datetime import datetime, timedelta

# Configuration
QIITA_USER = "taka_yayoi"
PUBLIC_DIR = "public"

# まとめ記事の定義
MATOME_FILES = {
    "matome1": "c6907e2b861cb1070f4d.md",  # イベント、チュートリアル等
    "matome2": "68fc3d67880d2dcb32bb.md",  # Spark, Delta Lake, Unity Catalog等
    "matome3": "6a39a3fc5d24780b09a0.md",  # 機械学習、生成AI/LLM
    "matome4": "51498e315d95692b243a.md",  # AIエージェント、MLflow、Apps等
}

# カテゴリキーワード（タイトルまたはタグで判定）
CATEGORY_KEYWORDS = {
    "matome2": {
        "keywords": ["Spark", "PySpark", "Delta", "Unity Catalog", "Volume", "Lakeflow",
                     "DLT", "Delta Sharing", "SQL", "pandas", "DataFrame"],
        "section": "## Apache Spark"  # デフォルト追加先
    },
    "matome3": {
        "keywords": ["LLM", "GPT", "Claude", "Gemini", "生成AI", "言語モデル", "NLP",
                     "自然言語", "機械学習", "ML", "深層学習", "ニューラル"],
        "section": "## Databricksにおける生成AI、大規模言語モデル(LLM)"
    },
    "matome4": {
        "keywords": ["エージェント", "Agent", "MCP", "MLflow", "Apps", "AI/BI",
                     "Feature Store", "AutoML", "Mosaic", "LLMOps"],
        "section": "## DatabricksにおけるAIエージェント開発"
    },
    "matome1": {
        "keywords": ["セミナー", "ハンズオン", "イベント", "チュートリアル", "入門",
                     "はじめて", "クックブック", "ユースケース"],
        "section": "# Databricksイベント"
    },
}

# 除外するID（まとめ記事自体、リリースノート等）
EXCLUDE_IDS = set([
    "c6907e2b861cb1070f4d",  # まとめ1
    "68fc3d67880d2dcb32bb",  # まとめ2
    "6a39a3fc5d24780b09a0",  # まとめ3
    "51498e315d95692b243a",  # まとめ4
    "57923e2d159a65a22118",  # リリースノート
    "68452723299f90d3c3b8",  # セミナーまとめ
    "2af61d3fa992a589ec26",  # 自動生成まとめ
])

# 人気マーカーの閾値
FIRE_THRESHOLD_LIKES = 20
FIRE_THRESHOLD_VIEWS = 10000
STAR_THRESHOLD_LIKES = 10
STAR_THRESHOLD_VIEWS = 5000


def fetch_article_stats():
    """Qiita APIから記事統計を取得"""
    token = os.environ.get("QIITA_TOKEN")
    if not token:
        print("Warning: QIITA_TOKEN not set, skipping stats fetch")
        return {}

    headers = {"Authorization": f"Bearer {token}"}
    stats = {}
    page = 1

    print("Fetching article stats from Qiita API...")
    while True:
        url = f"https://qiita.com/api/v2/users/{QIITA_USER}/items?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            break

        articles = response.json()
        if not articles:
            break

        for article in articles:
            stats[article["id"]] = {
                "title": article["title"],
                "likes_count": article["likes_count"],
                "page_views_count": article.get("page_views_count", 0),
                "created_at": article["created_at"],
                "tags": [tag["name"] for tag in article["tags"]],
            }

        page += 1

    print(f"Fetched stats for {len(stats)} articles")

    # Save stats to file
    with open("article_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return stats


def get_existing_article_ids():
    """まとめ記事に既に含まれている記事IDを取得"""
    existing_ids = set()
    link_pattern = re.compile(r'https://qiita\.com/taka_yayoi/items/([a-f0-9]+)')

    for matome_file in MATOME_FILES.values():
        filepath = os.path.join(PUBLIC_DIR, matome_file)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            existing_ids.update(link_pattern.findall(content))

    return existing_ids


def categorize_article(title, tags):
    """記事をカテゴリに分類"""
    title_lower = title.lower()
    tags_lower = [t.lower() for t in tags]

    for matome, config in CATEGORY_KEYWORDS.items():
        for keyword in config["keywords"]:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower or keyword_lower in tags_lower:
                return matome, config["section"]

    # デフォルトはmatome3（生成AI/LLM）
    return "matome3", CATEGORY_KEYWORDS["matome3"]["section"]


def add_article_to_matome(matome_key, section, article_id, title, date):
    """まとめ記事に新記事を追加"""
    filepath = os.path.join(PUBLIC_DIR, MATOME_FILES[matome_key])

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 日付フォーマット
    date_str = date[:10]  # YYYY-MM-DD
    new_line = f"- [{date_str}] [{title}](https://qiita.com/taka_yayoi/items/{article_id})"

    # セクションを探して追加
    if section in content:
        # セクションの次の行（最初の記事リスト）を探す
        lines = content.split("\n")
        new_lines = []
        found_section = False
        inserted = False

        for i, line in enumerate(lines):
            new_lines.append(line)
            if section in line and not found_section:
                found_section = True
            elif found_section and not inserted:
                # 空行やiframeをスキップ
                if line.strip() == "" or line.startswith("<iframe") or line.startswith("["):
                    continue
                # 最初の記事リストの前に挿入
                if line.startswith("- ["):
                    new_lines.insert(len(new_lines) - 1, new_line)
                    inserted = True

        if inserted:
            content = "\n".join(new_lines)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True

    return False


def get_popularity_marker(stats):
    """人気マーカーを取得"""
    likes = stats.get("likes_count", 0)
    views = stats.get("page_views_count", 0)

    if likes >= FIRE_THRESHOLD_LIKES or views >= FIRE_THRESHOLD_VIEWS:
        return " 🔥"
    elif likes >= STAR_THRESHOLD_LIKES or views >= STAR_THRESHOLD_VIEWS:
        return " ⭐"
    return ""


def update_popularity_markers(article_stats):
    """人気マーカーを更新"""
    link_pattern = re.compile(
        r'^(- \[\d{4}-\d{2}-\d{2}\] \[.*?\]\(https://qiita\.com/taka_yayoi/items/([a-f0-9]+)\))( [🔥⭐])?(.*)$'
    )

    for matome_file in MATOME_FILES.values():
        filepath = os.path.join(PUBLIC_DIR, matome_file)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        new_lines = []

        for line in lines:
            match = link_pattern.match(line)
            if match:
                link_part = match.group(1)
                article_id = match.group(2)
                suffix = match.group(4) or ""

                if article_id in article_stats:
                    marker = get_popularity_marker(article_stats[article_id])
                    line = f"{link_part}{marker}{suffix}"

            new_lines.append(line)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))


def main():
    # 1. 記事統計を取得
    article_stats = fetch_article_stats()
    if not article_stats:
        # ローカルのファイルから読み込み
        if os.path.exists("article_stats.json"):
            with open("article_stats.json", "r", encoding="utf-8") as f:
                article_stats = json.load(f)

    # 2. 既存の記事IDを取得
    existing_ids = get_existing_article_ids()
    print(f"Existing articles in matome: {len(existing_ids)}")

    # 3. 新しい記事を特定（過去30日以内）
    cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
    new_articles = []

    for article_id, stats in article_stats.items():
        if article_id in existing_ids:
            continue
        if article_id in EXCLUDE_IDS:
            continue
        if stats["created_at"] < cutoff_date:
            continue
        new_articles.append((article_id, stats))

    print(f"New articles to add: {len(new_articles)}")

    # 4. 新記事をまとめに追加
    for article_id, stats in new_articles:
        matome_key, section = categorize_article(stats["title"], stats["tags"])
        if add_article_to_matome(matome_key, section, article_id, stats["title"], stats["created_at"]):
            print(f"Added to {matome_key}: {stats['title']}")
        else:
            print(f"Failed to add: {stats['title']}")

    # 5. 人気マーカーを更新
    print("Updating popularity markers...")
    update_popularity_markers(article_stats)

    print("Done!")


if __name__ == "__main__":
    main()

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

# タグ → カテゴリマッピング
TAG_TO_CATEGORY = {
    # matome1: イベント、チュートリアル、Free Edition
    "Databricks_Free_Edition": ("matome1", "## Databricks Free Edition"),
    "Databricksチュートリアル": ("matome1", "# Databricksチュートリアル"),
    # matome2: Spark, Delta, Unity Catalog等
    "pyspark": ("matome2", "## Apache Spark"),
    "Spark": ("matome2", "## Apache Spark"),
    "DeltaLake": ("matome2", "## Delta Lake"),
    "Delta_Lake": ("matome2", "## Delta Lake"),
    "Unity_Catalog": ("matome2", "## Unity Catalog"),
    "Lakeflow": ("matome2", "## Lakeflow"),
    "DatabricksSQL": ("matome2", "## Databricks SQL"),
    "Delta_Sharing": ("matome2", "## Delta Sharing"),
    # matome3: 機械学習、生成AI/LLM
    "LLM": ("matome3", "## Databricksにおける生成AI、大規模言語モデル(LLM)"),
    "生成AI": ("matome3", "## Databricksにおける生成AI、大規模言語モデル(LLM)"),
    "機械学習": ("matome3", "## Databricksにおける機械学習"),
    "NLP": ("matome3", "## 自然言語処理 (NLP)"),
    # matome4: AIエージェント、MLflow、Apps等
    "Databricks_AI_Agent": ("matome4", "## DatabricksにおけるAIエージェント開発"),
    "AIエージェント": ("matome4", "## DatabricksにおけるAIエージェント開発"),
    "MLflow": ("matome4", "## MLflow"),
    "Databricks_AI_BI": ("matome4", "## Databricks AI/BI"),
    "DatabricksApps": ("matome4", "## Databricks Apps"),
    "MosaicAI": ("matome4", "## Mosaic AI"),
    "FeatureStore": ("matome4", "## Databricks Feature Store"),
}

# キーワード定義（優先度付き）
# priority: 高いほど優先（技術固有名 > 一般キーワード）
KEYWORDS = [
    # 高優先度: 具体的な技術名（これらが含まれていれば他のキーワードより優先）
    {"keyword": "Lakeflow", "matome": "matome2", "section": "## Lakeflow", "priority": 100},
    {"keyword": "Unity Catalog", "matome": "matome2", "section": "## Unity Catalog", "priority": 100},
    {"keyword": "Delta Lake", "matome": "matome2", "section": "## Delta Lake", "priority": 100},
    {"keyword": "Delta Sharing", "matome": "matome2", "section": "## Delta Sharing", "priority": 100},
    {"keyword": "MLflow", "matome": "matome4", "section": "## MLflow", "priority": 100},
    {"keyword": "Feature Store", "matome": "matome4", "section": "## Databricks Feature Store", "priority": 100},
    {"keyword": "Mosaic", "matome": "matome4", "section": "## Mosaic AI", "priority": 100},
    {"keyword": "Apps", "matome": "matome4", "section": "## Databricks Apps", "priority": 90},
    {"keyword": "AI/BI", "matome": "matome4", "section": "## Databricks AI/BI", "priority": 90},
    {"keyword": "Genie", "matome": "matome4", "section": "## Databricks AI/BI", "priority": 90},
    # 中優先度: 技術カテゴリ
    {"keyword": "Spark", "matome": "matome2", "section": "## Apache Spark", "priority": 80},
    {"keyword": "PySpark", "matome": "matome2", "section": "## Apache Spark", "priority": 80},
    {"keyword": "Delta", "matome": "matome2", "section": "## Delta Lake", "priority": 80},
    {"keyword": "SQL", "matome": "matome2", "section": "## Databricks SQL", "priority": 70},
    {"keyword": "DataFrame", "matome": "matome2", "section": "## Apache Spark", "priority": 70},
    {"keyword": "pandas", "matome": "matome2", "section": "## Apache Spark", "priority": 70},
    {"keyword": "Volume", "matome": "matome2", "section": "## Unity Catalog", "priority": 70},
    {"keyword": "DLT", "matome": "matome2", "section": "## Lakeflow", "priority": 70},
    {"keyword": "LLM", "matome": "matome3", "section": "## Databricksにおける生成AI、大規模言語モデル(LLM)", "priority": 80},
    {"keyword": "生成AI", "matome": "matome3", "section": "## Databricksにおける生成AI、大規模言語モデル(LLM)", "priority": 80},
    {"keyword": "GPT", "matome": "matome3", "section": "## Databricksにおける生成AI、大規模言語モデル(LLM)", "priority": 80},
    {"keyword": "Claude", "matome": "matome3", "section": "## Databricksにおける生成AI、大規模言語モデル(LLM)", "priority": 80},
    {"keyword": "Gemini", "matome": "matome3", "section": "## Databricksにおける生成AI、大規模言語モデル(LLM)", "priority": 80},
    {"keyword": "機械学習", "matome": "matome3", "section": "## Databricksにおける機械学習", "priority": 80},
    {"keyword": "NLP", "matome": "matome3", "section": "## 自然言語処理 (NLP)", "priority": 80},
    {"keyword": "自然言語", "matome": "matome3", "section": "## 自然言語処理 (NLP)", "priority": 80},
    {"keyword": "深層学習", "matome": "matome3", "section": "## Databricksにおける機械学習", "priority": 80},
    {"keyword": "エージェント", "matome": "matome4", "section": "## DatabricksにおけるAIエージェント開発", "priority": 80},
    {"keyword": "Agent", "matome": "matome4", "section": "## DatabricksにおけるAIエージェント開発", "priority": 80},
    {"keyword": "MCP", "matome": "matome4", "section": "## DatabricksにおけるAIエージェント開発", "priority": 80},
    {"keyword": "LLMOps", "matome": "matome4", "section": "## DatabricksにおけるLLMOps", "priority": 80},
    {"keyword": "AutoML", "matome": "matome4", "section": "## Databricks AutoML", "priority": 80},
    {"keyword": "Free Edition", "matome": "matome1", "section": "## Databricks Free Edition", "priority": 80},
    {"keyword": "無料版", "matome": "matome1", "section": "## Databricks Free Edition", "priority": 80},
    # 低優先度: 一般的なキーワード（他にマッチしない場合のみ使用）
    {"keyword": "入門", "matome": "matome1", "section": "# Databricksチュートリアル", "priority": 10},
    {"keyword": "チュートリアル", "matome": "matome1", "section": "# Databricksチュートリアル", "priority": 10},
    {"keyword": "はじめて", "matome": "matome1", "section": "# Databricksチュートリアル", "priority": 10},
    {"keyword": "セミナー", "matome": "matome1", "section": "# Databricksイベント", "priority": 10},
    {"keyword": "ハンズオン", "matome": "matome1", "section": "# Databricksイベント", "priority": 10},
    {"keyword": "イベント", "matome": "matome1", "section": "# Databricksイベント", "priority": 10},
    {"keyword": "クックブック", "matome": "matome1", "section": "# 生成AIクックブック", "priority": 10},
    {"keyword": "ユースケース", "matome": "matome1", "section": "# ユースケース", "priority": 10},
]

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
    """記事をカテゴリに分類（全体を見て最適なカテゴリを選択）"""

    # 1. タグで完全一致を探す（最優先）
    for tag in tags:
        if tag in TAG_TO_CATEGORY:
            matome_key, section = TAG_TO_CATEGORY[tag]
            print(f"  -> Matched by tag '{tag}' -> {matome_key} ({section})")
            return matome_key, section

    # 2. タイトルとタグから全てのマッチを収集し、最高優先度のものを選択
    title_lower = title.lower()
    tags_str = " ".join(tags).lower()
    search_text = f"{title_lower} {tags_str}"

    matches = []
    for kw_def in KEYWORDS:
        keyword = kw_def["keyword"]
        if keyword.lower() in search_text:
            matches.append(kw_def)

    if matches:
        # 最高優先度のマッチを選択
        best_match = max(matches, key=lambda x: x["priority"])
        print(f"  -> Best match: '{best_match['keyword']}' (priority={best_match['priority']}) -> {best_match['matome']} ({best_match['section']})")
        return best_match["matome"], best_match["section"]

    # 3. デフォルトはmatome3（生成AI/LLM）
    print(f"  -> No match, defaulting to matome3")
    return "matome3", "## Databricksにおける生成AI、大規模言語モデル(LLM)"


def add_article_to_matome(matome_key, section, article_id, title, date):
    """まとめ記事に新記事を追加（日付降順で適切な位置に挿入）"""
    filepath = os.path.join(PUBLIC_DIR, MATOME_FILES[matome_key])

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 日付フォーマット
    date_str = date[:10]  # YYYY-MM-DD
    new_line = f"- [{date_str}] [{title}](https://qiita.com/taka_yayoi/items/{article_id})"

    # セクションを探して追加
    if section in content:
        lines = content.split("\n")
        new_lines = []
        found_section = False
        inserted = False
        date_pattern = re.compile(r'^- \[(\d{4}-\d{2}-\d{2})\]')

        for i, line in enumerate(lines):
            if section in line and not found_section:
                found_section = True
                new_lines.append(line)
                continue

            if found_section and not inserted:
                # 空行やiframeをスキップ
                if line.strip() == "" or line.startswith("<iframe") or line.startswith("["):
                    new_lines.append(line)
                    continue

                # 記事リスト行の場合、日付を比較して適切な位置に挿入
                if line.startswith("- ["):
                    match = date_pattern.match(line)
                    if match:
                        existing_date = match.group(1)
                        # 新しい記事の日付が既存の日付より新しい場合、ここに挿入
                        if date_str >= existing_date:
                            new_lines.append(new_line)
                            inserted = True
                    else:
                        # 日付パターンがない場合は先頭に挿入
                        new_lines.append(new_line)
                        inserted = True

                # 次のセクション（#で始まる行）に到達した場合、セクション末尾に追加
                elif line.startswith("#") and not inserted:
                    new_lines.append(new_line)
                    inserted = True

            new_lines.append(line)

        # セクションの最後まで到達した場合（ファイル末尾）
        if found_section and not inserted:
            # 最後の記事リストの後に追加
            new_lines.append(new_line)
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

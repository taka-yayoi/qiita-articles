#!/usr/bin/env python3
"""
Fetch article statistics (views, likes) from Qiita API
"""
import json
import os
import urllib.request
import urllib.parse
import time

# Qiita API token from environment or qiita-cli config
def get_qiita_token():
    # Try environment variable first
    token = os.environ.get('QIITA_TOKEN')
    if token:
        return token

    # Try qiita-cli credentials file
    credentials_path = os.path.expanduser('~/.config/qiita-cli/credentials.json')
    if os.path.exists(credentials_path):
        with open(credentials_path) as f:
            creds = json.load(f)
            default_name = creds.get('default', 'qiita')
            credentials = creds.get('credentials', [])
            for cred in credentials:
                if cred.get('name') == default_name:
                    return cred.get('accessToken')

    return None

def fetch_user_articles(username, token, page=1, per_page=100):
    """Fetch articles for a user"""
    url = f'https://qiita.com/api/v2/users/{username}/items?page={page}&per_page={per_page}'

    req = urllib.request.Request(url)
    if token:
        req.add_header('Authorization', f'Bearer {token}')

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def fetch_all_articles(username, token):
    """Fetch all articles for a user"""
    all_articles = []
    page = 1

    while True:
        print(f"Fetching page {page}...")
        articles = fetch_user_articles(username, token, page=page)
        if not articles:
            break
        all_articles.extend(articles)
        if len(articles) < 100:
            break
        page += 1
        time.sleep(0.5)  # Rate limiting

    return all_articles

def main():
    token = get_qiita_token()
    if not token:
        print("Warning: No Qiita token found. API rate limits may apply.")

    username = 'taka_yayoi'
    print(f"Fetching articles for {username}...")

    articles = fetch_all_articles(username, token)
    print(f"Fetched {len(articles)} articles")

    # Create stats dictionary: article_id -> {likes, views, title}
    stats = {}
    for article in articles:
        article_id = article['id']
        stats[article_id] = {
            'title': article['title'],
            'likes_count': article['likes_count'],
            'page_views_count': article.get('page_views_count', 0),
            'stocks_count': article.get('stocks_count', 0),
        }

    # Save to file
    with open('/Users/takaaki.yayoi/Workspace/qiita-articles/article_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"Saved stats for {len(stats)} articles to article_stats.json")

    # Show top articles by likes
    print("\n=== Top 20 by Likes ===")
    sorted_by_likes = sorted(stats.items(), key=lambda x: x[1]['likes_count'], reverse=True)[:20]
    for article_id, data in sorted_by_likes:
        print(f"  {data['likes_count']:4d} likes - {data['title'][:50]}")

    # Show top articles by views
    print("\n=== Top 20 by Views ===")
    sorted_by_views = sorted(stats.items(), key=lambda x: x[1]['page_views_count'], reverse=True)[:20]
    for article_id, data in sorted_by_views:
        print(f"  {data['page_views_count']:6d} views - {data['title'][:50]}")

if __name__ == '__main__':
    main()

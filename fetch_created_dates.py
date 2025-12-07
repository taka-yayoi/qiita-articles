#!/usr/bin/env python3
import json
import urllib.request
import time
import os

# Load Qiita token
with open(os.path.expanduser('~/.config/qiita-cli/credentials.json')) as f:
    creds = json.load(f)
    token = creds['credentials'][0]['accessToken']

# Fetch all articles with pagination
all_articles = []
page = 1
while True:
    print(f"Fetching page {page}...")
    url = f'https://qiita.com/api/v2/authenticated_user/items?per_page=100&page={page}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                print(f"Error: {resp.status}")
                break
            items = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
        break

    if not items:
        break

    all_articles.extend(items)
    print(f"  Got {len(items)} items, total: {len(all_articles)}")

    if len(items) < 100:
        break

    page += 1
    time.sleep(0.5)  # Rate limiting

# Create mapping: id -> created_at (YYYY-MM-DD)
mapping = {}
for article in all_articles:
    article_id = article['id']
    created_at = article['created_at'][:10]  # YYYY-MM-DD
    mapping[article_id] = created_at

# Save mapping
with open('/Users/takaaki.yayoi/Workspace/qiita-articles/article_dates.json', 'w') as f:
    json.dump(mapping, f, indent=2)

print(f"\nSaved {len(mapping)} article dates to article_dates.json")

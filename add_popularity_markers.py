#!/usr/bin/env python3
"""
Add popularity markers to matome articles based on likes and views.
"""
import json
import re

# Load article stats
with open('/Users/takaaki.yayoi/Workspace/qiita-articles/article_stats.json', encoding='utf-8') as f:
    article_stats = json.load(f)

print(f"Loaded stats for {len(article_stats)} articles")

# Define thresholds
FIRE_THRESHOLD_LIKES = 20  # 🔥 for 20+ likes
FIRE_THRESHOLD_VIEWS = 10000  # 🔥 for 10000+ views
STAR_THRESHOLD_LIKES = 10  # ⭐ for 10+ likes
STAR_THRESHOLD_VIEWS = 5000  # ⭐ for 5000+ views

def get_marker(article_id):
    """Get popularity marker for an article"""
    if article_id not in article_stats:
        return ''

    stats = article_stats[article_id]
    likes = stats.get('likes_count', 0)
    views = stats.get('page_views_count', 0)

    if likes >= FIRE_THRESHOLD_LIKES or views >= FIRE_THRESHOLD_VIEWS:
        return ' 🔥'
    elif likes >= STAR_THRESHOLD_LIKES or views >= STAR_THRESHOLD_VIEWS:
        return ' ⭐'
    return ''

# Pattern to match article links with date prefix
# Example: - [2024-01-01] [Title](https://qiita.com/taka_yayoi/items/abc123)
link_pattern = re.compile(r'^(- \[\d{4}-\d{2}-\d{2}\] \[.*?\]\(https://qiita\.com/taka_yayoi/items/([a-f0-9]+)\))( [🔥⭐])?(.*)$')

def process_file(filepath):
    print(f"\nProcessing {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    stats = {'fire': 0, 'star': 0}

    for line in lines:
        match = link_pattern.match(line)
        if match:
            link_part = match.group(1)
            article_id = match.group(2)
            existing_marker = match.group(3) or ''
            suffix = match.group(4) or ''

            # Get new marker
            new_marker = get_marker(article_id)

            if new_marker == ' 🔥':
                stats['fire'] += 1
            elif new_marker == ' ⭐':
                stats['star'] += 1

            # Build new line (replace existing marker)
            new_line = f"{link_part}{new_marker}{suffix}"
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print(f"  🔥 Fire: {stats['fire']}, ⭐ Star: {stats['star']}")
    return stats

# Process all matome files
files = [
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/c6907e2b861cb1070f4d.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/68fc3d67880d2dcb32bb.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/6a39a3fc5d24780b09a0.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/51498e315d95692b243a.md',
]

total_stats = {'fire': 0, 'star': 0}
for filepath in files:
    stats = process_file(filepath)
    for k in total_stats:
        total_stats[k] += stats[k]

print(f"\n=== Total ===")
print(f"🔥 Fire (20+ likes or 10000+ views): {total_stats['fire']}")
print(f"⭐ Star (10+ likes or 5000+ views): {total_stats['star']}")

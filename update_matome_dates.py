#!/usr/bin/env python3
import json
import re
import os

# Load article dates
with open('/Users/takaaki.yayoi/Workspace/qiita-articles/article_dates.json') as f:
    article_dates = json.load(f)

print(f"Loaded {len(article_dates)} article dates")

# Pattern to match article links
# - [Title](https://qiita.com/taka_yayoi/items/xxx)
link_pattern = re.compile(r'^(\s*-\s*)(\[.*?\]\(https://qiita\.com/taka_yayoi/items/([a-f0-9]+)\))(.*)$')

# Pattern to detect if already has date prefix
date_prefix_pattern = re.compile(r'^\s*-\s*\[\d{4}-\d{2}-\d{2}\]')

def process_file(filepath):
    print(f"\nProcessing {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    current_section_lines = []
    in_section = False
    section_header = None
    stats = {'updated': 0, 'not_found': 0, 'already_has_date': 0}

    def flush_section():
        nonlocal current_section_lines, section_header
        if not current_section_lines:
            return

        # Sort lines by date (descending)
        def get_date(line):
            match = re.search(r'\[(\d{4}-\d{2}-\d{2})\]', line)
            if match:
                return match.group(1)
            return '0000-00-00'

        current_section_lines.sort(key=get_date, reverse=True)
        new_lines.extend(current_section_lines)
        current_section_lines = []
        section_header = None

    for line in lines:
        # Check if this is a section header
        if line.startswith('#'):
            flush_section()
            new_lines.append(line)
            in_section = True
            section_header = line
            continue

        # Check if this is an article link line
        match = link_pattern.match(line)
        if match:
            prefix = match.group(1)  # "- " or "  - "
            link = match.group(2)    # [Title](url)
            article_id = match.group(3)
            suffix = match.group(4)  # anything after the link

            # Check if already has date
            if date_prefix_pattern.match(line):
                stats['already_has_date'] += 1
                current_section_lines.append(line)
                continue

            # Get date for this article
            if article_id in article_dates:
                date = article_dates[article_id]
                new_line = f"{prefix}[{date}] {link}{suffix}"
                stats['updated'] += 1
                current_section_lines.append(new_line)
            else:
                stats['not_found'] += 1
                current_section_lines.append(line)
        else:
            # Non-link line
            if current_section_lines:
                flush_section()
            new_lines.append(line)

    flush_section()

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print(f"  Updated: {stats['updated']}, Not found: {stats['not_found']}, Already has date: {stats['already_has_date']}")
    return stats

# Process all matome files
files = [
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/c6907e2b861cb1070f4d.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/68fc3d67880d2dcb32bb.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/6a39a3fc5d24780b09a0.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/51498e315d95692b243a.md',
]

total_stats = {'updated': 0, 'not_found': 0, 'already_has_date': 0}
for filepath in files:
    stats = process_file(filepath)
    for k in total_stats:
        total_stats[k] += stats[k]

print(f"\n=== Total ===")
print(f"Updated: {total_stats['updated']}")
print(f"Not found: {total_stats['not_found']}")
print(f"Already has date: {total_stats['already_has_date']}")

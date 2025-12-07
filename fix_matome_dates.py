#!/usr/bin/env python3
import json
import re

# Load article dates
with open('/Users/takaaki.yayoi/Workspace/qiita-articles/article_dates.json') as f:
    article_dates = json.load(f)

print(f"Loaded {len(article_dates)} article dates")

# Pattern to match article links (with or without date prefix, with any indentation)
# Matches: "- [Title](url)", "  - [Title](url)", "- [2024-01-01] [Title](url)", etc.
link_pattern = re.compile(r'^\s*-\s*(\[\d{4}-\d{2}-\d{2}\]\s*)?(\[.*?\]\(https://qiita\.com/taka_yayoi/items/([a-f0-9]+)\))(.*)$')

def process_file(filepath):
    print(f"\nProcessing {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    current_section_lines = []
    stats = {'updated': 0, 'not_found': 0}

    def flush_section():
        nonlocal current_section_lines
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
        new_lines.append('')  # Add empty line after section
        current_section_lines = []

    for line in lines:
        # Check if this is a section header
        if line.startswith('#'):
            flush_section()
            new_lines.append(line)
            new_lines.append('')  # Add empty line after header
            continue

        # Check if this is an article link line
        match = link_pattern.match(line)
        if match:
            # group(1) = existing date prefix (if any)
            # group(2) = [Title](url)
            # group(3) = article_id
            # group(4) = suffix
            link = match.group(2)
            article_id = match.group(3)
            suffix = match.group(4)

            # Get date for this article
            if article_id in article_dates:
                date = article_dates[article_id]
                # Always use "- " prefix (no indentation), add date
                new_line = f"- [{date}] {link}{suffix}"
                stats['updated'] += 1
                current_section_lines.append(new_line)
            else:
                # Keep original but normalize indentation
                stats['not_found'] += 1
                current_section_lines.append(f"- {link}{suffix}")
        else:
            # Non-link line (including empty lines)
            # Skip empty lines within sections
            if line.strip() == '':
                continue  # Skip empty lines, they will be added after sorting
            # For other non-link lines (text, iframe, etc.), flush and add
            if current_section_lines:
                flush_section()
            new_lines.append(line)
            new_lines.append('')  # Add empty line after non-link content

    flush_section()

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print(f"  Updated: {stats['updated']}, Not found: {stats['not_found']}")
    return stats

# Process all matome files
files = [
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/c6907e2b861cb1070f4d.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/68fc3d67880d2dcb32bb.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/6a39a3fc5d24780b09a0.md',
    '/Users/takaaki.yayoi/Workspace/qiita-articles/public/51498e315d95692b243a.md',
]

total_stats = {'updated': 0, 'not_found': 0}
for filepath in files:
    stats = process_file(filepath)
    for k in total_stats:
        total_stats[k] += stats[k]

print(f"\n=== Total ===")
print(f"Updated: {total_stats['updated']}")
print(f"Not found: {total_stats['not_found']}")

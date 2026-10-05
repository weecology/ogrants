#!/usr/bin/env python3
"""
Migration script to convert existing ogrants grant files from the legacy
single-author format to the new multi-author format.

Usage:
    python migrate_to_multiauthor.py [--dry-run] [--file path/to/grant.md]

Options:
    --dry-run   Show what would be changed without modifying files
    --file      Process a single file instead of all grants
"""

import os
import re
import sys
import argparse
from pathlib import Path


def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown file."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, content

    yaml_str = match.group(1)
    remainder = content[match.end():]

    # Simple YAML parser for our needs
    data = {}
    current_key = None
    current_list = None

    for line in yaml_str.split('\n'):
        # Skip empty lines
        if not line.strip():
            continue

        # Check for list item
        if line.startswith('  - '):
            if current_list is not None:
                current_list.append(line[4:].strip())
            continue
        elif line.startswith('- '):
            if current_list is not None:
                current_list.append(line[2:].strip())
            continue

        # Check for key: value
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            if value == '':
                # Start of a list or nested structure
                current_key = key
                current_list = []
                data[key] = current_list
            else:
                current_key = key
                current_list = None
                data[key] = value

    return data, remainder


def format_yaml_value(value):
    """Format a value for YAML output."""
    if isinstance(value, str):
        # Check if needs quoting
        if ':' in value or '#' in value or value.startswith('"') or '\n' in value:
            # Use double quotes and escape inner quotes
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        return value
    elif isinstance(value, list):
        return value
    return str(value)


def convert_to_multiauthor(data):
    """Convert legacy single-author format to multi-author format."""
    # Already in new format
    if 'authors' in data:
        return data, False

    # No author field
    if 'author' not in data:
        return data, False

    author_str = data['author']
    orcid_str = data.get('ORCID', '')
    institution = data.get('institution', '')

    # Parse author names
    if ' and ' in author_str:
        author_names = [a.strip() for a in author_str.split(' and ')]
    elif ', ' in author_str and not re.search(r', (?:Jr\.|Sr\.|III|IV|PhD|MD)', author_str):
        # Split on comma only if it's not part of a suffix
        author_names = [a.strip() for a in author_str.split(', ')]
    else:
        author_names = [author_str.strip()]

    # Parse ORCIDs
    orcids = []
    if orcid_str:
        # Remove any URL prefix
        orcid_str = re.sub(r'https?://orcid\.org/', '', orcid_str)

        if ' and ' in orcid_str:
            orcids = [o.strip() for o in orcid_str.split(' and ')]
        elif ';' in orcid_str:
            orcids = [o.strip().rstrip(';') for o in orcid_str.split(';') if o.strip()]
        elif ',' in orcid_str:
            orcids = [o.strip() for o in orcid_str.split(',')]
        else:
            orcids = [orcid_str.strip()]

    # Build authors array
    authors = []
    for i, name in enumerate(author_names):
        author = {'name': name}

        # First author gets the institution (for backward compatibility)
        if i == 0 and institution:
            author['institution'] = institution

        # Assign ORCID if available
        if i < len(orcids) and orcids[i]:
            orcid = orcids[i].strip()
            # Validate ORCID format (xxxx-xxxx-xxxx-xxxx)
            if re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}[X]?$', orcid):
                author['orcid'] = orcid

        authors.append(author)

    # Create new data structure
    new_data = {'layout': data.get('layout', 'grant')}
    new_data['title'] = data.get('title', '')
    new_data['authors'] = authors

    # Copy other fields
    for key in ['year', 'funder', 'program', 'discipline', 'status', 'link', 'link_name']:
        if key in data and data[key]:
            new_data[key] = data[key]

    return new_data, True


def write_yaml_frontmatter(data, remainder):
    """Generate markdown with YAML frontmatter."""
    lines = ['---']

    for key, value in data.items():
        if key == 'authors':
            lines.append('authors:')
            for author in value:
                lines.append(f'  - name: {format_yaml_value(author["name"])}')
                if 'orcid' in author:
                    lines.append(f'    orcid: {author["orcid"]}')
                if 'institution' in author:
                    lines.append(f'    institution: {format_yaml_value(author["institution"])}')
        elif isinstance(value, list):
            lines.append(f'{key}:')
            for item in value:
                lines.append(f'  - {format_yaml_value(item)}')
        else:
            lines.append(f'{key}: {format_yaml_value(value)}')

    lines.append('---')
    return '\n'.join(lines) + remainder


def migrate_file(filepath, dry_run=False):
    """Migrate a single grant file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    data, remainder = parse_yaml_frontmatter(content)
    if data is None:
        print(f"  SKIP: {filepath} - No YAML frontmatter found")
        return False

    new_data, changed = convert_to_multiauthor(data)

    if not changed:
        print(f"  SKIP: {filepath} - Already in new format or no author field")
        return False

    new_content = write_yaml_frontmatter(new_data, remainder)

    if dry_run:
        print(f"  WOULD MIGRATE: {filepath}")
        print(f"    Authors: {[a['name'] for a in new_data['authors']]}")
        return True

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  MIGRATED: {filepath}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Migrate grants to multi-author format')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')
    parser.add_argument('--file', type=str, help='Process a single file')
    args = parser.parse_args()

    # Find the _grants directory
    script_dir = Path(__file__).parent
    grants_dir = script_dir.parent / '_grants'

    if not grants_dir.exists():
        print(f"Error: _grants directory not found at {grants_dir}")
        sys.exit(1)

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        migrate_file(filepath, args.dry_run)
    else:
        print(f"Scanning {grants_dir} for grant files...")
        migrated = 0
        skipped = 0

        for filepath in sorted(grants_dir.glob('*.md')):
            # Skip test files
            if filepath.name.startswith('test_'):
                print(f"  SKIP: {filepath.name} - Test file")
                skipped += 1
                continue

            if migrate_file(filepath, args.dry_run):
                migrated += 1
            else:
                skipped += 1

        print(f"\nSummary: {migrated} files {'would be ' if args.dry_run else ''}migrated, {skipped} skipped")


if __name__ == '__main__':
    main()

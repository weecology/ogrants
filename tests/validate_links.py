import os
import pathlib
import subprocess

import requests
import yaml


def link_resolves(url):
    try:
        request = requests.head(url)
        return request.ok
    except Exception:
        return False


def load_grant_file(path):
    text = path.read_text()
    grant_info = next(yaml.safe_load_all(text))
    return grant_info


def get_changed_files():
    """
    Return pathlib.Paths for files changed in the last
    git commit.
    """
    args = ['git', 'diff', '--name-only', 'HEAD~1']
    paths = subprocess.check_output(args, text=True)
    paths = paths.splitlines()
    paths = {pathlib.Path(path) for path in paths}
    return paths


def get_grant_paths():
    paths = set(pathlib.Path('_grants').glob('*.md'))
    if os.getenv('TRAVIS_EVENT_TYPE') != 'cron':
        print('Limiting tests only to files changed')
        paths &= get_changed_files()
    return sorted(paths)


# Read links that should not be automatically validated.
# These links must be manually checked to see if they resolve.
skip_links = set(
    pathlib.Path(__file__)
    .parent.joinpath('skip-link-validation.txt')
    .read_text().splitlines()
)

grant_paths = get_grant_paths()
grant_str = '\n'.join(f"\t{path}" for path in grant_paths)
print(f"Testing {len(grant_paths):,} grants:\n{grant_str}")
broken_link_count = 0
for path in grant_paths:
    grant = load_grant_file(path)
    grant_year = grant.get('year')
    links = grant['link']
    if isinstance(links, str):
        links = [links]
    assert isinstance(links, list)
    for i, link in enumerate(links):
        if link in skip_links:
            continue
        if not link_resolves(link):
            print('---------Link Broken---------')
            print(f"Grant: {grant_year} / {grant['author']} / Link: {i + 1}\n{link}\n")
            broken_link_count += 1

assert broken_link_count == 0, f'{broken_link_count} broken links'

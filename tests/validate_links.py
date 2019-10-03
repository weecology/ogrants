import pathlib
import urllib.request

import yaml


def link_resolves(url):
    try:
        request = urllib.request.urlopen(url)
        return request.status < 400
    except Exception:
        return False


def load_grant_file(path):
    text = path.read_text()
    grant_info = next(yaml.safe_load_all(text))
    return grant_info


# Read links that should not be automatically validated.
# These links must be manually checked to see if they resolve.
skip_links = set(
    pathlib.Path(__file__)
    .parent.joinpath('skip-link-validation.txt')
    .read_text().splitlines()
)

grant_paths = sorted(pathlib.Path('_grants').glob('*.md'))
print(f"{len(grant_paths):,} grant paths detected")
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

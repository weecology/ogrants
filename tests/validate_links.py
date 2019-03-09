import yaml
import glob
import urllib.request

def link_resolves(url):
    try:
        request = urllib.request.urlopen(url)
        request.close()
        return True
    except:
        return False

def load_grant_file(grant_filename):
    with open(grant_filename, 'r') as f:
        lines = f.readlines()
        # drop the first and last line. pyyaml doesn't like them
        lines = lines[1:-1]
        grant_info = yaml.load(''.join(lines))
    return grant_info

grants = [load_grant_file(f) for f in glob.glob('_grants/*md')]

broken_link_count = 0

for grant in grants:
    try:
        grant_year = str(grant['year'])
    except:
        grant_year = ''
    
    links = grant['link']
    if isinstance(links, str):
        links = [links]

    for i, link in enumerate(links):
        if not link_resolves(link):
            print('Grant: ' + str(grant_year) + ' / ' + grant['author'] + ' / ' + 'Link: ' + str(i + 1))
            print('\---------Link Broken---------')
            print('')
            broken_link_count+=1
        else:
            pass

assert broken_link_count == 0, str(broken_link_count) + ' broken links'
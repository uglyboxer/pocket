import csv
import requests
from requests.exceptions import SSLError, ConnectionError

from tqdm import tqdm
from bs4 import BeautifulSoup

from constants import CONSUMER_KEY, CODE, ACCESS_TOKEN


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
#     if isinstance(element, Comment):
#         return False
    return True

pocket_auth = requests.post('https://getpocket.com/v3/oauth/authorize', 
    data = {'consumer_key': CONSUMER_KEY, 
            'code': CODE})

r = requests.post('https://getpocket.com/v3/get', 
                  data = {
                  "consumer_key": CONSUMER_KEY,
                  "access_token": ACCESS_TOKEN,
                  "detailType":"complete"
                  })

js = r.json()['list']

def look_for_readme(url):

    if 'github.com' not in url.lower() or 'readme.md' in url.lower():
        return url
    scrape = requests.get(url)._content
    soup = BeautifulSoup(scrape, features='html5lib')
    links = soup.findAll('a')
    if not links:
        return url
    for x in links:
        if 'readme.md' in str(x).lower():
            return 'https://github.com' + x['href']
    return url

def fetch(item):
    # Handle pdfs  TODO 
    try:
        tags = [x for x in item['tags'].keys()]
        if not tags:
            return None, None
        url = look_for_readme(item['resolved_url'])
        if '.pdf' in url:
            tqdm.write('come back later for pdf')
            return None, None
        if '.png' in url:
            tqdm.write('bailing on pic')
            return None, None
        if 'github' in url:
            return 'g', tags 

        return None, None
        tqdm.write('Sourcing {}'.format(url))
        scrape = requests.get(url)._content
        soup = BeautifulSoup(scrape, features="html5lib")
        if 'https://github.com' in url.lower():
            try:
                texts = soup.find(id="readme").find_all(text=True)
            except AttributeError:
                return None, None
        elif 'youtube.com' in url.lower():
            print('no youtube')
            return None, None
        else:
            texts = soup.findAll(text=True)
        text = ' '.join([x.strip() for x in texts if tag_visible(x)])
        if not text:
            return None, None

    except (KeyError, SSLError, ConnectionError):
        return None, None

    return text, tags

res = []
counter = 0
for item in tqdm(js.values()):
    text, tags = fetch(item)
    if text == 'g':
        tqdm.write('github: {}'.format(tags))
        counter += 1
print(counter)


# with open('results.csv', 'w') as f:
#     writer = csv.writer(f)
#     for line in res:
#         writer.writerow(line)
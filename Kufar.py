import re
import os.path
import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse

class Kufar:
    host = 'https://www.kufar.by'
    url = 'https://www.kufar.by/listings?size=42&sort=lst.d&cur=BYR&cat=8100&query=%D0%A1%D1%82%D1%80%D0%B8%D0%BF%D1%8B&ot=1&rgn=7&wss=v.or%3A8%2C7'
    lastkey = ""
    lastkey_file = ""

    def __init__(self, lastkey_file):
        self.lastkey_file = lastkey_file

        if os.path.exists(lastkey_file):
            self.lastkey = open(lastkey_file, 'r').read()
        else:
            f = open(lastkey_file, 'w')
            self.lastkey = self.get_lastkey()
            f.write(str(self.lastkey))
            f.close()

    def parse_href(self, href):
        result = re.search(r'\/item\/(\d+)', href)
        return int(result.group(1))

    def get_lastkey(self):
        items = BS(requests.get(self.url).content, 'html.parser').select('article a')
        del items[0:2]
        return max([self.parse_href(e['href'])for e in items])

    def update_lastkey(self, new_key):
        self.lastkey = new_key

        with open(self.lastkey_file, "r+") as f:
            f.read()
            f.seek(0)
            f.write(str(new_key))
            f.truncate()

        return new_key
    
    def download_image(self, url):
        r = requests.get(url, allow_redirects=True)
        
        a = urlparse(url)
        filename = os.path.basename(a.path)
        open(filename, 'wb').write(r.content)
        
        return 

    def get_ad_info(self, url):
        itemPage = BS(requests.get(url).content, 'html.parser')
        paramsBlock = itemPage.select('[data-name ~= parameters-block]')[0]
        rignht_Bar = itemPage.select("[data-name ~= 'av_right_sidebar'] span")
        info = {
            'size' : paramsBlock.select("div > div[data-name ~='women_shoes_size']")[0].find_next_sibling().text,
            'title' : itemPage.find('h1').text,
            'cost' : rignht_Bar[1].text,
            'district' : rignht_Bar[0].text,
            'image' : itemPage.select('[data-name="adview-gallery"]')[0].find('img')['src'],
            'id':self.parse_href(url)
        }

        return info

    def get_new_ads(self):
        return [i['href'] for i in self.get_items() if int(self.lastkey) < self.parse_href(i['href'])]
    
    def get_all_ads(self):
        return [e['href'] for e in self.get_items()]

    def get_items(self):
        items = BS(requests.get(self.url).content, 'html.parser').select('article a')
        del items[0:3]

        return items
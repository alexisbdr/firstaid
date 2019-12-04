# Fast Implementation of a search module
import urllib
import json
import requests
from bs4 import BeautifulSoup


class search:
    url_prefix = "https://www."
    types_mapping = {
        "definitions": {
            "medical": ["merriam-webster.com/medical/"],
            "general": ["merriam-webster.com/dictionary/"]
        },
        "images": ["google.com/search?tbm=isch&num=10&q="],
        "flash_cards": [],
        "videos": ["youtube.com/results?search_query="],
        "default": ["google.com/search?q={}&num=10&hl=en"]
    }

    def __init__(self, search_term, types, category):
        self.search_term = search_term
        if types in self.types_mapping:
            self.mappings = self.types_mapping[types]
            if category and \
                    category in self.mappings:
                self.mappings = self.mappings[category]
        else:
            self.mappings = self.types_mapping["default"]
        self.search(types)

    def search(self, types):
        results = []
        mapping = self.mappings[0]
        search_url = self.url_prefix + mapping + self.search_term
        encoded_search_url = search_url.replace(" ", '+')
        header = {
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
        page = urllib.request.urlopen(urllib.request.Request(encoded_search_url, headers=header))
        if page.getcode() == 404:
            print("could not find... ")
            return
        soup = BeautifulSoup(page, 'html.parser')
        if types == "definitions":
            # word = soup.h1.text
            dtTexts = soup.findAll('span', {'class': 'dtText'})
            for dtText in dtTexts:
                dLines = dtText.text.split("\n")
                dLine = dLines[0]
                dLine = dLine.replace(': ', '', 1)
                results.append(dLine)
        elif types == "images":
            for a in soup.find_all("div", {"class": "rg_meta"}):
                link = json.loads(a.text)["ou"]
                results.append(link)
        elif types == "videos":
            videos = soup.findAll('a', attrs={'class': 'yt-uix-tile-link'})
            for v in videos:
                tmp = 'https://www.youtube.com' + v['href']
                results.append(tmp)
        for result in results:
            print(result)
        return results


if __name__ == "__main__":
    search("bandage", "videos", "general")

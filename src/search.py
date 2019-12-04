# Fast Implementation of a search module
import urllib
import requests

class search: 
    
    url_prefix = "https://www."
    types_mapping = {
        "definitions": {
            "medical": ["merriam-webster.com/medical/"],
            "general": ["merriam-webster.com/dictionary/", "wikipedia.org/wiki/"] 
        },
        "images": ["google.com/imghp?hl=en&search={}&num=10"],
        "flash_cards": [],
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
        self.search()

    def search(self):
        for mapping in self.mappings:
            search_url = self.url_prefix + mapping + self.search_term
            resp = requests.get(search_url)
            print(search_url)
            print(resp)
            #Do response handling here... -->
            if resp.status_code == 404: 
                print("could not find....")
        

if __name__ == "__main__": 
    search("cough", "images", "general")

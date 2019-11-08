import PyPDF2
import json
import typing
from typing import List
from os import path

import boto3
from botocore.exceptions import ClientError

import nltk
from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

from utilities import punctuation, key_tags

page_offset = 11
symptom_title = "What to Look for"
search_word = "Burns"
specific_term = "Chemical"

def proto_parser(): 

    path = "../data/FA-CPR-AED-Part-Manual.pdf"
    pdf_file = open(path, "rb")
    pdf_file = PyPDF2.PdfFileReader(pdf_file)
    reference_pages = [5,6,7]
    search_word = "Burns"
    for page_num in reference_pages:
        page = pdf_file.getPage(page_num)
        page_text = page.extractText()
        search_word_index = page_text.find(search_word)
        if search_word_index != -1:
            following_text = page_text[search_word_index: search_word_index + 50].split()
            section_numbers = []
            for text in following_text:
                if text.isdigit():
                    section_numbers.append(int(text) + page_offset)
                if len(section_numbers) > 2: 
                    break
    for page_num in range(section_numbers[0], section_numbers[1]+ 1):
        page = pdf_file.getPage(page_num)
        page_text = page.extractText()
        search_term = specific_term + " " + search_word
        specific_index = page_text.find(search_term)
        if specific_index != -1:
            pass


class parser():

    bucket = "first-aid-data"
    key = "FA-CPR-AED-Part-Manual.pdf"
    download_path = '../data/'+key

    index_pages = [5,6,7]
    page_offset = 11

    def __init__(self, category: str, sub_category: str): 
        self.category = category
        self.sub_category = sub_category
        self.s3_client = boto3.client('s3')
        pdf = self.get_file()
        self.parse_pdf(pdf)
    
    def get_file(self):
        if not path.exists(self.download_path):
            self.download_path = "/tmp/" + self.key
            try:
                self.s3_client.download_file(self.bucket, self.key, self.download_path)
            except ClientError as e : 
                raise Exception("Download problem", e)
        try: 
            pdf_file = open(self.download_path, 'rb')
        except IOError as e:
            raise Exception("Failed to open file", e)
        return pdf_file

    def find_word_association(self, word: str):
        stemmer = PorterStemmer()
        return stemmer.stem(word)

    def remove_stop_words(self, text: str) -> str: 
        stop = stopwords.words('english')
        text_tokens = [t for t in text.split()]
        clean_text = text_tokens[:]
        for token in text_tokens: 
            if token in stop: 
                clean_text.remove(token)
        return " ".join(clean_text)
    
    def convert_sentence_to_step(self, sentence: str, tagged_sentence: (str, str)) -> str: 
        
        #sentence_stopped = self.remove_stop_words(sentence)
        print(sentence)
        return sentence

    def find_page_numbers_by_category(self, pdf_file):
        #get similar category word
        #stemmed = self.find_word_association(self.category)
        for page_num in self.index_pages:
            page = pdf_file.getPage(page_num)
            page_text = page.extractText()
            search_word_index = page_text.find(self.category)
            if search_word_index != -1:
                following_text = page_text[search_word_index: search_word_index + 50].split()
                section_numbers = []
                for text in following_text:
                    if text.isdigit():
                        section_numbers.append(int(text) + page_offset)
                    if len(section_numbers) == 2:
                        return section_numbers

    def find_section_in_page(self, pdf_file, pages: List[int]) -> str: 
        
        #stemmed_category = self.find_word_association(self.category)
        #stemmed_sub_category = self.find_word_association(self.sub_category)
        #search_terms = [
        #    "{} {}".format(stemmed_category, stemmed_sub_category),
        #    "{} {}".format(stemmed_sub_category, stemmed_category)
        #]

        ##TODO make better search method that iteratively goes through until we find some sort of section
        ## what does a section consist of
        search_terms = [
            "{} {}".format(self.sub_category, self.category),
            "{} {}".format(self.category, self.sub_category)
        ]
        for page_num in range(pages[0], pages[1]+ 1):
            page = pdf_file.getPage(page_num)
            page_text = page.extractText()
            for search_term in search_terms:
                section_index = page_text.find(search_term)
                if section_index != -1:
                    extracted_chunk = page_text[section_index: section_index + 2000]
                    sentences = sent_tokenize(extracted_chunk)
                    return sentences

    def check_tags(self, tag: (str, str), tag_index: int) -> bool: 

        return None
    
    def extract_steps(self, sentences: str, num_steps: int = 4):
        steps = []
        for sentence in sentences:
            words = word_tokenize(sentence)
            tagged_words = nltk.pos_tag(words)
            for tag_index in range(len(tagged_words)):
                tag = tagged_words[tag_index][1]
                if tag in key_tags \
                    and tag_index >= key_tags[tag]["start"] \
                    and tag_index <= key_tags[tag]["end"]:
                    filtered_detection = self.convert_sentence_to_step(sentence, tagged_words)
                    steps.append(filtered_detection)
        return steps

                        
            
    def parse_pdf(self, pdf):
        pdf_file = PyPDF2.PdfFileReader(pdf)
        pages = self.find_page_numbers_by_category(pdf_file)
        text_sentences = self.find_section_in_page(pdf_file, pages)
        steps = self.extract_steps(text_sentences)

        

  

                 

        
if __name__ == "__main__":
    parser("Burns", "Chemical")

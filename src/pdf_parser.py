import PyPDF2
import json
import typing
from typing import List
from os import path
from itertools import count

import boto3
from botocore.exceptions import ClientError

import nltk
from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.data.path.append("./nltk_data")

from utilities import punctuation, key_tags, LinkedList

class parser():

    bucket = "first-aid-data"
    key = {
        "default": "FA-CPR-AED-Part-Manual.pdf",
        "army": "Army-First-Aid.pdf",
        "everything": "Everything-First-Aid.pdf"
    }
    download_path = '../data/' + key["default"]

    index_pages = [5,6,7]
    page_offset = 11

    procedures_table = "First_Aid-Procedures"

    def __init__(self, category: str, sub_category: str): 
        self.category = category
        self.sub_category = sub_category
        self.s3_client = boto3.client('s3')
        self.db_client = boto3.resource('dynamodb')
        self.get_steps()
    
    def get_steps(self):
        if not self.get_steps_from_db(): 
            if not path.exists(self.download_path):
                self.download_path = "/tmp/" + self.key["default"]
                try:
                    self.s3_client.download_file(self.bucket, self.key, self.download_path)
                except ClientError as e : 
                    raise Exception("Download problem", e)
            try: 
                pdf_file = open(self.download_path, 'rb')
                self.parse_pdf(pdf_file)
            except IOError as e:
                raise Exception("Failed to open file", e)

        
    def get_steps_from_db(self) -> bool:
        try: 
            table = self.db_client.Table(self.procedures_table)
            response = table.get_item(
                Key={
                    'Name': "{} {}".format(self.sub_category, self.category)
                }
            )
        except ClientError as e: 
            return False
        else: 
            try: 
                item = response["Item"]
                print(item)
                self.steps = item["Steps"]
                print("worked")
                return True
            except ValueError as e: 
                return False
            return False

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
                        section_numbers.append(int(text) + self.page_offset)
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
        sentences = []
        for page_num in range(pages[0], pages[1]+ 1):
            page = pdf_file.getPage(page_num)
            page_text = page.extractText()
            for search_term in search_terms:
                section_index = page_text.find(search_term)
                if section_index != -1:
                    extracted_chunk = page_text[section_index: section_index + 2000]
                    sentences.extend(sent_tokenize(extracted_chunk))
                    #Then get start of next page if we didn't get enough
                    if len(extracted_chunk) < 700:
                        next_page = pdf_file.getPage(page_num + 1)
                        next_page_text = next_page.extractText()
                        next_extracted_chunk = next_page_text[0: 2000 - len(extracted_chunk)]
                        sentences.extend(sent_tokenize(next_extracted_chunk))
        return sentences

    def extract_explanations(self, tagged_words: List):
        """
        There can be multiple explanations after a question or explanations that to not relate
        to the given question, try to separate
        those out into separate nodes 
        """
        conj_separator = [i for i,tag in enumerate(tagged_words) if tag[0] == "and" and \
            tagged_words[i+1][1] == "VB"]
        if conj_separator:
            explanation_tags = [tagged_words[i+1 : j] for i, j in zip([0] + \
                conj_separator, conj_separator + [None])] 
            return [" ".join([t[0] for t in explanation]) for \
                explanation in explanation_tags]
        else:
            return [" ".join([t[0] for t in tagged_words])]

    def interrogative_to_question(self, tagged_words:List):
        """
        Given an interrogative sentence attempts to convert it to a question
        """
        #Get the VBD tagged word from the tagged words list
        aux_verbs = [i for i, tag in enumerate(tagged_words) if tag[1] == "VBD"]
        if aux_verbs: 
            tagged_words.insert(0, tagged_words.pop(aux_verbs[0]))
        else: 
            tagged_words.insert(0, ("did", "VBD"))
        print(tagged_words)
        return " ".join([t[0] for t in tagged_words])
        
    def parse_step_from_sentence(self, tagged_words: List) -> str: 
        """
        Gets a sentence string as an input and a list of tagged_words and key tags
        """
        #Check for a conditional -- any interogative inside of sentence
        for index, tag in enumerate(tagged_words): 
            if tag[0] == "If" and tag[1] == "IN":
                #Make the start of the interrogative sentence a question
                tagged_words = tagged_words[index + 1:] 
                conditional = self.interrogative_to_question(tagged_words)
                print(conditional)
                #Find first comma and stop the question there
                conditional_parts = conditional.split(",")
                question = conditional_parts[0] + "?"
                comma_index = tagged_words.index((",",","))
                print(tagged_words)
                print(comma_index)
                tagged_words = tagged_words[comma_index + 1:]
                explanation_steps = self.extract_explanations(tagged_words)
                print(explanation_steps)
                self.steps.insert_conditional(question, explanation_steps[0])
                [self.steps.insert(explanation) for explanation in explanation_steps[1:]]
                return
        sentence_list = " ".join(t[0] for t in tagged_words).replace("\n", "").replace("\r", "")
        print(sentence_list)        
        self.steps.insert(sentence_list)

        """ 
        for sentence_tag in key_tags:
            index, tag = sentence_tag[0], sentence_tag[1]
            #Special case2: if ":" take what's after
            #Special case1: Check for VB at start of se (within first 4)
            
            #Check that the tag is after a specified key and update the sentence
            for i in range(min(0,index - 8), max(index+1,len(sentence_list))):
                if tagged_words[i][1] in key_tags[tag]["after"] and i != len(sentence_list) - 1:
                    sentence_list = sentence_list[index:]
        """

    def extract_steps(self, sentences: str, num_steps: int = 4):
        """
        New Approach: 
        start adding to linked list as soon as you find a step
        """
        self.steps = LinkedList()
        step_count = count(0)

        for sentence in sentences:
            words = word_tokenize(sentence)
            tagged_words = nltk.pos_tag(words)
            for tag_index, tag in enumerate(tagged_words):
                if tag[1] in key_tags and \
                    tag_index >= key_tags[tag[1]]["start"] and \
                        tag_index <= key_tags[tag[1]]["end"]:
                    self.parse_step_from_sentence(tagged_words) #
                    #We break because once we've found a key tag we just go through regardless
                    break
            
    def parse_pdf(self, pdf):
        pdf_file = PyPDF2.PdfFileReader(pdf)
        self.pages = self.find_page_numbers_by_category(pdf_file)
        self.text_sentences = self.find_section_in_page(pdf_file, self.pages)
        self.extract_steps(self.text_sentences)

    def to_linked_list(self) -> LinkedList:
        ll = LinkedList() #Initialize with nothing in the LL
        for step in self.steps:
            ll.insert(step)
        return ll

if __name__ == "__main__":
    print(parser("Burns", "Chemical").steps.to_json())
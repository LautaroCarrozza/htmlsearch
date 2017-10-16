import sys
import os
from src.automata import *
from collections import defaultdict


def read_words(path):
    words = set()
    with open(path) as f:
        for line in f:
            if len(line) > 0:
                words.add(line)
    return words

def determinize(automata):
    eliminate_lambdas(automata)
    determinize_automata(automata)
    return automata


def build_automata(words, html_files):
    nd_automata = NDAutomata()
    for word in words:
        #TODO build lamda with html_files
        nd_automata.add_word(word) #TODO add lamda as parameter
    return nd_automata


'''
def consume_files(automata, html_files):
    result = dict()
    for html_file in html_files:
        with open(html_file) as f:
            for line in f:
 
'''


class WordCounter:

    def __init__(self):
        self.counter = defaultdict(int)

    def add_counter(self, word):

        def counter_fun():
            self.counter[word] += 1

        return counter_fun

    def reset(self):
        for key in self.counter:
            self.counter[key] = 0

    def __iter__(self):
        for word, count in self.counter.items():
            if count != 0:
                yield word, count


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) < 3:
        sys.exit('Not enough arguments given')

    DIRECTORY = arguments[1]
    SEARCH_FILE = arguments[2]

    if not SEARCH_FILE.endswith('.txt'):
        sys.exit('Invalid search file')

    html_list = []

    for root, dirs, files in os.walk(DIRECTORY):
        for file in files:
            if file.endswith('.html'):
                html_list.append(file)

    words = read_words(SEARCH_FILE)

    automata = build_automata(words)
    #TODO call method to draw nd_automata here
    automata = determinize_automata(automata)
    #TODO call method to draw automata here




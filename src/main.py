import sys
import os
from src.automata import *


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


def build_automata(words, result_dict):
    #TODO build lamda with result_dict
    nd_automata = NDAutomata()
    for word in words:
        nd_automata.add_word(word) #TODO add lamda as parameter
    return nd_automata


'''
def consume_files(automata, html_list):
    result = dict()
    for html_file in html_list:
        with open(html_list) as f:
            for line in f:

'''



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




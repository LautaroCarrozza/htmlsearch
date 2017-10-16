import sys
import os
from src.automata_util import *
from collections import defaultdict


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


def read_words(path):
    words = set()
    with open(path) as f:
        for line in f:
            if len(line) > 0:
                words.add(line)
    return words


def build_automata(words):
    nd_automata = NDAutomata()
    word_counter = WordCounter()
    for word in words:
        fun = word_counter.add_counter(word)
        nd_automata.add_word(word, fun)
    return nd_automata, word_counter


def consume_files(automata, word_counter, html_files):
    results = dict()
    for html_file in html_files:
        with open(html_file) as f:
            for line in f:
                automata.consume_stream(line)
        for word, count in word_counter:
            results[word][html_file] = count
        word_counter.reset()
        automata.reset()
    return results


def write_results(results, path):
    with open(path, 'w') as file:
        for word, html_dict in results.items():
            file.write(word)
            for html_file, count in html_dict:
                file.write(html_file)
                file.write(count)


def main():
    arguments = sys.argv
    if len(arguments) < 3:
        sys.exit('Not enough arguments given')

    directory = arguments[1]
    search_file = arguments[2]

    if not search_file.endswith('.txt'):
        sys.exit('Invalid search file')

    html_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(file)

    words = read_words(search_file)

    nd_automata, word_counter = build_automata(words)
    automata = full_determinize(nd_automata)
    results = consume_files(automata, word_counter, html_files)
    write_results(results, "index.txt")

    #TODO draw nd_automata and automata


if __name__ == '__main__':
    main()

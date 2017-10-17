import sys
import os
from automata_util import *
from file_util import *
from collections import defaultdict


class WordCounter:
    """
    Dictionary wrapper that contains words as keys and the number that word appears as values.
    When adding a word, it returns a function that adds 1 to the number that word appears.
    Can be iterated for a word - counter tuple for all words whose counter is greater than 0.
    """
    def __init__(self):
        self.counter = defaultdict(int)

    def add_counter(self, word):
        """
        Adds a word to the dictionary for counting and return a function to update the count number
        :param word: word to count
        :return: function that adds 1 to the word counter
        """
        def counter_fun():
            self.counter[word] += 1

        return counter_fun

    def reset(self):
        """
        Resets all counters to 0
        :return: 
        """
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
                words.add(line.rstrip('\n'))
    return words


def build_automata(words):
    nd_automata = NDAutomata()
    word_counter = WordCounter()
    for word in words:
        fun = word_counter.add_counter(word)
        nd_automata.add_word(word, fun)
    return nd_automata, word_counter


def consume_files(automata, word_counter, directory, html_files):
    results = defaultdict(dict)
    for html_file in html_files:
        with open(build_path(directory, html_file)) as f:
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
            file.write("{}\n".format(word))
            for html_file, count in html_dict.items():
                file.write("{}\n".format(html_file))
                file.write("{}\n".format(count))
            file.write("\n")


def build_path(directory, file):
    return "{}\{}".format(directory, file)


def main():
    arguments = sys.argv
    if len(arguments) < 3:
        sys.exit('Not enough arguments given')

    directory = arguments[1]
    search_file = build_path(directory, arguments[2])

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

    nd_states = process_states(get_automata_states(nd_automata))
    d_states = process_states(get_automata_states(automata))

    write_automata(nd_states, build_path(directory, 'nfa.dot'))
    write_automata(d_states, build_path(directory, 'dfa.dot'))

    results = consume_files(automata, word_counter, directory, html_files)
    write_results(results, build_path(directory, 'index.txt'))


if __name__ == '__main__':
    main()

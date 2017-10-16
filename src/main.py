import sys
import os

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
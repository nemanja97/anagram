#! py3
# anagram.py - A console based look up of anagrams for English words

import itertools
import pickle
from string import ascii_lowercase
from sys import argv

import requests
from bs4 import BeautifulSoup


def print_usage():
    print('''# anagram.py - USAGE:
    --------------------------------------------------------------------------------------------------------------------------------------
    \t# anagram.py                 | Script start with no parameters
    \t# anagram.py -s term         | Script start with a search for anagrams of inputed term
    \t# anagram.py -s term -n num  | Script start with a search for anagrams of inputed term and gives results consisting of up to n words
    \t# anagram.py -u              | Script start with a word library update beforehand, requires internet connection
    --------------------------------------------------------------------------------------------------------------------------------------
    ''')


def parse_parameters():
    if len(argv) == 1:
        return None
    if len(argv) == 2 and argv[1] == "-u":
        build_search_dictionary()
        return None
    if len(argv) == 3 and argv[1] == "-s":
        return (argv[2])
    if len(argv) == 5 and argv[1] == "-s":
        try:
            int(argv[4])
        except ValueError:
            print_usage()
            quit(1)
        return (argv[2], argv[4])
    else:
        print_usage()
        quit(1)


def get_soup(url):
    # Returns an object provided by bs4 module, easily searchable interpretation of an internet page
    return BeautifulSoup(requests.get(url).text, "html.parser")


def build_word_list():
    # Building a list of words attained from Dictionary.com
    # The site is scanned for <span> tags with the "word" class, HTML elements representing desired words
    # Upon being found, a word is added to a list specific to its starting letter
    # In the end, every word specific list is combined into a main file and saved afterwards in a binary form

    # A 27 element list, contains symbol 0 and letters a-z
    base_schema = [r"http://www.dictionary.com/list/"] * 27

    # Building an basic page container, pages go from
    # http://www.dictionary.com/list/0/ to http://www.dictionary.com/list/z/
    url_list = [i + j + '/' for i, j in zip(base_schema, '0'+ascii_lowercase)]

    # A container for all the words on the page
    base_word_list = [[] for _ in range(27)]
    # Counter for number of letters passed
    counter = 0

    for base_url in url_list:
        # Counter for the number of pages under a certain letter
        page_counter = 1
        while True:
            page = url_list[counter] + str(page_counter)
            print("Downloading definition from -> " + page)
            MOVE_TO_NEXT_LETTER = False
            soup = get_soup(page)
            contents = soup.find_all("span", "word")
            for content in contents:
                word = str(content.text)
                # Upon reaching the first page again, break
                # This check is performed by asking if the current word is same as the first one
                if len(base_word_list[counter]) != 0 and base_word_list[counter][0] == word:
                    MOVE_TO_NEXT_LETTER = True
                    break
                base_word_list[counter].append(word)
            # If we reached a new letter, increase the counter for that otherwise keep iterating over pages
            if MOVE_TO_NEXT_LETTER:
                counter += 1
                break
            else:
                page_counter += 1
    # Return the list:
    # [ [ list of words for symbol 0 ], [ list of words for letter a ], ... [ list of words for letter z ] ]
    return base_word_list


def build_search_dictionary():
    # Rebuilding a search dictionary where KEY - length of words and VALUE - list of words with that length
    print("Rebuilding data files, this will take some time.")
    
    base_word_list = build_word_list()

    word_dictionary = {}
    for word_list in base_word_list:
        for word in word_list:
            word_length = len(word)
            if not ' ' in word:
                if not word_length in word_dictionary:
                    word_dictionary[word_length] = [word]
                else:
                    word_dictionary[word_length].append(word)
    pickle.dump(word_dictionary, open("words.bin", "wb"))


def find_char_count(word):
    # Returns a dictionary where KEY - a unique character and VALUE - the number of times the character is represented
    # Case insensitive
    word.lower()
    charDict = {}
    for char in word:
        if not char in charDict:
            charDict[char] = 1
        else:
            charDict[char] += 1
    return charDict


def compare_words(word1, word2):
    # Returns true if words contain the same number of same characters, false if not
    char_dict1 = find_char_count(word1)
    char_dict2 = find_char_count(word2)
    if char_dict1 == char_dict2:
        return True
    else:
        return False


def get_all_substrings(input_string):
    # Using list comprehension, we return all the substrings of a given string
    length = len(input_string)
    return [input_string[i:j+1] for i in range(length) for j in range(i,length)]


def find_anagram(original, dictionary, steps = None):
    # The original phrase is made lowercase, striped of whiteline and the individual words are split and then rejoined
    original = original.lower()
    original = original.strip()
    container = original.split(" ")
    search_term = "".join(container)

    # All substrings are made and every 'proper' word and its same-length anagrams are added to a list
    substrings = get_all_substrings(search_term)
    subwords_list = []
    for substring in substrings:
        for word in dictionary[len(substring)]:
            if compare_words(word, substring):
                subwords_list.append(word)

    # If no number of desired maximum word combinations is chosen or the number is invalid, a default value is given
    if steps is None or steps == 0 or steps > len(search_term):
        steps = len(search_term)

    # Using the combination function from itertools module, all subset elements are joined into a single string,
    # compared to the original search term and printed out, if they match it.
    # Upon reaching the desired step limit, the work stops.
    for L in range(1, len(subwords_list) + 1):
        if L <= steps:
            for subset in itertools.combinations(subwords_list, L):
                string = "".join(subset)
                if (len(string) == len(search_term)):
                    if compare_words(string, search_term):
                        print(subset)
                    if len(subset) == len(search_term):
                        break
        else:
            break


def word_input():
    # Word search term input
    while True:
        word = input("Enter the word you want to find anagrams of : ")
        if len(word) > 0:
            return word


def num_input():
    # Combination size input
    while True:
        num = input("Enter a number of words results should consist of, leave it at 0 for every possible combination : ")
        try:
            num = int(num)
            if num < 0:
                pass
            else:
                return num
        except ValueError:
            print("Non-numerical value entered")


if __name__ == "__main__":
    search_term = parse_parameters()
    word_dictionary = None

    # Attempting to open required files, rebuilding if need be
    while True:
        try:
            word_dictionary = pickle.load(open("words.bin", "rb"))
            break
        except IOError:
            print("Data file not found, rebuilding")
            build_search_dictionary()

    while True:
        if search_term is not None:
            # Argument parsed search
            if len(search_term) == 2:
                find_anagram(search_term[0], word_dictionary, int(search_term[1]))
                search_term = [word_input(), num_input()]
            else:
                find_anagram(search_term[0], word_dictionary)
                search_term = [word_input(), num_input()]
        else:
            # No arguments given search
            search_term = [word_input(), num_input()]

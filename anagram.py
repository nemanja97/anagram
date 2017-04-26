LEN_DICTIONARY = {}

def fillDictionary():
    with open("WordList") as file:
        words = [line.rstrip('\n') for line in file]
    for word in words:
        word_length = len(word)
        if not word_length in LEN_DICTIONARY:
            LEN_DICTIONARY[word_length] = [word]
        else:
            LEN_DICTIONARY[word_length].append(word)

def wordInput():
    while True:
        word = input("Enter the word you want to find anagrams of : ")
        if len(word) > 0:
            return word

def findCharCount(word):
    charDict = {}
    for char in word:
        if not char in charDict:
            charDict[char] = 1
        else:
            charDict[char] += 1
    return charDict

def compareWords(word1, word2):
    charDict1 = findCharCount(word1)
    charDict2 = findCharCount(word2)
    if charDict1 == charDict2:
        return True
    else:
        return False

def findAnagram(original):
    anagrams = []
    for word in LEN_DICTIONARY[len(original)]:
        if compareWords(original, word) is True and word != original:
            anagrams.append(word)
    if len(anagrams) == 0:
        print("No anagrams were found")
    else:
        for anagram in anagrams:
            print(anagram)

if __name__ == "__main__":
    fillDictionary()
    findAnagram(wordInput())

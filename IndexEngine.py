# This program can read the latimes.gz file and stores separately each document and its
# associated metadata such that the second program can efficiently retrieve a document and its metadata

import gzip
import sys
import os
from xml.dom import minidom
import re
import json
from PorterStemmer import PorterStemmer

lexicon_str = {}
lexicon_int = {}
inv_index = {}
file_directory = ""

"""
This function reads the .gz file line by line and stores the metadata and files in their respective directories
Output: index.txt file with index maps between internal id & docno, latimes-index directory with articles separated by date
"""


def reader(path_gz, path_index):
    global lexicon_str
    global file_directory

    if not os.path.exists(path_gz):
        sys.exit(
            f'ERROR: Path {path_gz} does not exist. Please ensure your .gz file is downloaded into the root directory of the project and try again.')
    # f = open(path_gz, 'rb+')  # Sample .txt file
    f = gzip.open(path_gz, 'rb+') # .gz file
    index = open('index.txt', 'w')
    lines = f.readlines()
    internal_id = -1

    for line in lines:
        line = str(line, 'utf-8')
        if '<DOC>' in line:
            file = ""  # new file begins
            internal_id += 1
        elif '<DOCNO>' in line:
            docno = str(line[8:-10].strip())  # Extract MMDDYY to create directory
            mm = docno[2:4]
            dd = docno[4:6]
            yy = docno[6:8]
            file_directory = '/'.join([path_index, yy, mm, dd])
            if not os.path.exists(file_directory):
                os.makedirs(file_directory)
            store_index(index, internal_id, docno)  # Save internal_id with DOCNO mapping
        elif '</DOC>' in line:
            file += line
            store_files(file, docno)
            tokens = tokenize(docno, file)

            # Stemmed using PorterStemmer.py, described in the README
            tokens_stemmed = []
            stemmer = PorterStemmer() #! New
            for token in tokens:
                tokens_stemmed.append(stemmer.stem(token, 0, len(token)-1))
            token_ids = convertTokensToIds(tokens_stemmed)
            word_counts = countWords(token_ids)
            add_to_postings(word_counts, internal_id)
        file += line
    f.close()
    index.close()

    # Save inverted index & lexicons
    # f_inv_index = open(path_index + '/inverted_index.txt', 'w')
    # f_inv_index.write(json.dumps(inv_index))
    f_lexicon_str = open(path_index + '/lexicon_str_to_int.txt', 'w')
    f_lexicon_str.write(json.dumps(lexicon_str))
    f_lexicon_int = open(path_index + '/lexicon_int_to_str.txt', 'w')
    f_lexicon_int.write(json.dumps(lexicon_int))


"""
This function gets passed array of token ids and counts how many times each word appears in a doc
Output: Dict{int:int}
"""


def add_to_postings(word_counts, doc_id):
    global inv_index
    for term_id in word_counts:
        count = word_counts[term_id]
        if term_id in inv_index:  # Postings List already exists, must have at least 1 doc
            i = 0
            postings_list = inv_index[term_id]
            while i < len(postings_list):
                if postings_list[i] > doc_id:
                    i += 2
                    print("ITERATE")
                else:
                    postings_list.insert(i - 2, doc_id)
                    postings_list.insert(i - 2, count)
                    break

        else:  # First time term introduced to postings list
            inv_index[term_id] = [doc_id, count]
            inv_index[term_id] = inv_index[term_id]


"""
This function gets passed array of token ids and counts how many times each word appears in a doc
Output: Dict{int:int}
"""


def countWords(token_ids):
    word_counts = {}
    for id in token_ids:
        if id in word_counts:
            word_counts[id] += 1
        else:
            word_counts[id] = 1
    return word_counts


"""
This function gets passed array of tokens and converts it into all the integer equivalents
Output: Lexicon1: term(string)->id(int), Lexicon2: id(int)->term(string)
"""


def convertTokensToIds(tokens):
    global lexicon_str
    global lexicon_int

    token_ids = []
    for t in tokens:
        if t in lexicon_str:
            token_ids.append(lexicon_str[t])  # Find & add Id
        else:
            id = len(lexicon_str)
            lexicon_str[t] = id
            lexicon_int[id] = t
            token_ids.append(id)
    return token_ids


"""
This function gets passed giant string of file and tokenizes it
Output: array[strings] of downcased tokens
"""
def tokenize(docno, file):
    # Extract text in <TEXT>, <HEADLINE>, <GRAPHIC>
    file_xml = minidom.parseString(file)
    tokens = []

    # Extract <TEXT>
    if len(file_xml.getElementsByTagName('TEXT')) > 0:
        text = file_xml.getElementsByTagName('TEXT')[0]
        paragraphs = text.getElementsByTagName("P")

        for p in range(len(paragraphs)):
            t = paragraphs[p].firstChild.data.lower()
            # Separate contiguous alphanumeric tokens
            # Code from: http://www.learningaboutelectronics.com/Articles/How-to-extract-alphanumeric-characters-from-a-string-in-Python-using-regular-expressions.php
            patterns = [r'\w+']
            for p in patterns:
                tokens.extend(re.findall(p, t))

    # Extract <TEXT>
    headline = file_xml.getElementsByTagName('HEADLINE')
    if len(file_xml.getElementsByTagName('HEADLINE')) > 0:
        h = headline[0].getElementsByTagName("P")[0].firstChild.data.lower()

        # Separate contiguous alphanumeric tokens
        # Code from: http://www.learningaboutelectronics.com/Articles/How-to-extract-alphanumeric-characters-from-a-string-in-Python-using-regular-expressions.php
        patterns = [r'\w+']
        for p in patterns:
            tokens.extend(re.findall(p, h))

    # Extract <GRAPHIC>
    if len(file_xml.getElementsByTagName('GRAPHIC')) > 0:
        graphic = file_xml.getElementsByTagName('GRAPHIC')[0]
        g = graphic.getElementsByTagName("P")[0].firstChild.data.lower()

        # Separate contiguous alphanumeric tokens
        # Code from: http://www.learningaboutelectronics.com/Articles/How-to-extract-alphanumeric-characters-from-a-string-in-Python-using-regular-expressions.php
        patterns = [r'\w+']
        for p in patterns:
            tokens.extend(re.findall(p, g))

    # Store doc length in metadata
    doc_len = len(tokens)
    d = open(file_directory + '/' + docno + '.txt', 'a', newline='')
    d.write('\ndoc_len: ' + str(doc_len))
    d.close()

    return tokens


"""
This function stores a string of file into a unique .xml file named as the DOCNO in the date directory
Ex: LA010189-0008 would go under /latimes-index/01/01/89/LA010189-0008.txt
"""
def store_files(file, docno):
    global file_directory

    # Store document in .xml file
    f_doc = open((file_directory + '/' + docno + '.xml'), 'w', newline='')
    f_doc.write(file)
    f_doc.close()

    # Store metadata in .txt file
    f_meta = open((file_directory + '/' + docno + '.txt'), 'w', newline='')
    f = minidom.parseString(file)
    internal_id = f.getElementsByTagName('DOCID')[0].firstChild.data.strip()
    mm = docno[2:4]
    dd = docno[4:6]
    yy = docno[6:8]
    date = mm + '/' + dd + '/19' + yy
    f_meta.write('id: ' + internal_id + '\n')
    f_meta.write('date: ' + date + '\n')
    headline = f.getElementsByTagName('HEADLINE')
    if len(f.getElementsByTagName('HEADLINE')) > 0:
        h = headline[0].getElementsByTagName("P")[0].firstChild.data.strip()
        if h is not None:
            f_meta.write('headline: ' + h)
        else:
            f_meta.write('headline:')
    f_meta.close()


"""
This function stores index mapping of internal id to docno
Output: file named index.txt formatted like 0,LA010189-0008 in each row
"""


def store_index(file, internal_id, docno):
    file.write(str(internal_id) + ',' + (docno) + '\n')


"""Checks that the length of the stemmed inverted index is shorter, hence suggesting
there are less terms since they've been stemmed"""
def checker():
    f_stemmed = json.loads(open('try1/inverted_index.txt', 'r').read())
    f_orig = json.loads(open('try2/inverted_index.txt', 'r').read())
    print('STEMMED LEN: '+str(len(f_stemmed)))
    print('ORIGINAL LEN: '+str(len(f_orig)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(
            f"ERROR: Not enough arguments provided. Please run in this format: python IndexEngine.py PATH_OF_GZ_FILE PATH_OF_INDEXED_DOCUMENTS")
    elif len(sys.argv) > 3:
        sys.exit(
            f"ERROR: Too many arguments provided. Please run in this format: python IndexEngine.py PATH_OF_GZ_FILE PATH_OF_INDEXED_DOCUMENTS")
    for i, arg in enumerate(sys.argv):
        if i == 1:
            path_gz = arg
        elif i == 2:
            path_index = arg
            if os.path.exists(path_index):
                sys.exit(
                    f"ERROR: Path {path_index} already exists in root directory. Please delete the {path_index} folder before running the IndexEngine again.")
    print(f"Path to gz file: {path_gz}")
    print(f"Path to index directory: {path_index}")
    reader(path_gz, path_index)

    for term_id in inv_index:
        postings_list = inv_index[term_id]
        postings_list.insert(0, postings_list[len(postings_list) - 1])
        postings_list.insert(0, postings_list[len(postings_list) - 2])
        inv_index[term_id] = postings_list[:-2]
        f = open('inverted_index/'+str(term_id)+'.txt', 'w+')
        f.write(str(inv_index[term_id]))
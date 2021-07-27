import json
import sys
import os
import re
import random

"""
Modified function to write results
"""
def boolean_and_retrieval(path_index, path_queries, path_output, bm25):
    # Open queries file
    f_topics = open(path_queries, 'rb+')
    topics = f_topics.read().splitlines()

    # Import Lexicon
    f_lexicon = open(path_index+'/lexicon_str_to_int.txt', 'rb+')
    lexicon = json.loads(f_lexicon.readlines()[0])

    # Import Inverted Index
    f_inv_index = open(path_index+'/inverted_index.txt', 'rb+')
    inv_index = json.loads(f_inv_index.readlines()[0])

    # Import metadata
    f_index = open('index.txt', 'rb+')
    indexes = f_index.read().splitlines()
    for i in range(len(indexes)):
        indexes[i] = str(indexes[i], 'utf-8').split(',')

    # Import metadata
    f_output = open(path_output, 'a', newline='')

    run_tag = ''.join(['j623lee', ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(5))])

    result_sets = {}
    line = 1
    while line < len(topics):
        title = str(topics[line].lower(), 'utf-8')
        patterns= [r'\w+'] #tokenize
        terms = []
        for p in patterns:
            terms.extend(re.findall(p, title))

        # Use lexicon to find term id's
        query = []
        for word in terms:
            if word in lexicon:
                query.append(lexicon[word])

        doc_count = {}
        for t in query:
            postings = inv_index[str(t)]
            i = 0
            while i < len(postings):
                if postings[i] in doc_count:
                    doc_count[postings[i]] += 1 #doc_id
                else:
                    doc_count[postings[i]] = 1
                i += 2

            result_set = []
        for doc_id in doc_count:
            if doc_count[doc_id] == len(query):
                result_set.append(doc_id)

        result_sets[str(topics[line-1], 'utf-8')] = result_set
        line += 2

    for result in result_sets:
        # print(f"Topic: {result}")
        print_text = []
        for r in result_sets[result]:
            docno = indexes[r][1]
            mm = docno[2:4]
            dd = docno[4:6]
            yy = docno[6:8]
            # score = open('/'.join([path_index, yy, mm, dd, docno+'.txt']), 'r').read().splitlines()[-1][9:]
            score = bm25[result][docno]
            print_text.append((result, docno, score))
            print(print_text)

        # Rank documents by score
        print_text.sort(key=take_score, reverse=True)
        rank = 1
        for p in print_text[:999]:
            result = p[0]
            docno = p[1]
            score = p[2]
            f_output.write(f"{result} q0 {docno} {rank} {score} {run_tag}\n")
            rank += 1


def take_score(set):
    return int(float(set[2]))


if __name__ == "__main__":
    if len(sys.argv)<4:
        sys.exit(f"ERROR: Not enough arguments provided. Please run in this format: python BooleanAND.py PATH_OF_INDEX PATH_OF_QUERIES OUTPUT_FILE")
    elif len(sys.argv)>4:
        sys.exit(f"ERROR: Too many arguments provided. Please run in this format: python BooleanAND.py PATH_OF_INDEX PATH_OF_QUERIES OUTPUT_FILE")
    for i, arg in enumerate(sys.argv):
        if i==1:
            path_index = arg
            if not os.path.exists(path_index):
                sys.exit(f'ERROR: INDEX PATH {path_index} DOES NOT EXIST.')
        elif i==2:
            path_queries = arg
            if not os.path.exists(path_queries):
                sys.exit(f'ERROR: QUERY PATH {path_queries} DOES NOT EXIST.')
        elif i==3:
            path_output = arg
    print(f"Path to index file: {path_index}")
    print(f"Path to queries: {path_queries}")
    print(f"Path to output file: {path_output}")
    boolean_and_retrieval(path_index, path_queries, path_output)
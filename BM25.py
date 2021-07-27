from IndexEngine import tokenize
from PorterStemmer import PorterStemmer
from BooleanAND import boolean_and_retrieval
import math
import re
import json
import random


def fix_postings_list():
    inv_index = json.loads(open('latimes-index-stem/inverted_index.txt', 'rb+').read()) # import inverted index
    print("Inverted Index Loaded")

    for term in inv_index:
        f = open('inverted_index/'+str(term)+'.txt', 'w+')
        postings_list = inv_index[term]
        f.write(str(postings_list))
        f.close()


def calculate_avdl():
    index_file = open('index.txt', 'rb+').read().splitlines()
    index = {}
    for i in index_file:
        dup = (str(i, 'utf-8')).split(',')
        index[(dup[0])] = dup[1]
    print('Index Loaded')
    avdl = 0

    for i in index:
        docno = index[i]
        avdl += get_doclen(docno)
    avdl = avdl/len(index)

    print("AVERAGE DOC LENGTH FOUND")
    print(avdl)


def calculate_bm25():
    stemmer = PorterStemmer()
    k_1 = 1.2
    b = 0.75
    k_2 = 7

    avdl = float(open('avdl.txt', 'rb+').read()) # import average doc length
    print("Avdl Loaded")
    lexicon = json.loads(open('latimes-index-stem/lexicon_str_to_int.txt', 'rb+').read()) # import lexicon
    print("Lexicon Loaded")
    index_file = open('index.txt', 'rb+').read().splitlines()
    index = {}
    for i in index_file:
        dup = (str(i, 'utf-8')).split(',')
        index[(dup[0])] = dup[1]
    print('Index Loaded')
    N = len(index) # no of docs in collection
    inv_index = {}

    f = open('topics.txt', 'rb+')
    queries = f.read().splitlines()
    f_out = open('hw4-bm25-stem-j623lee.txt', 'a+')
    # f_out = open('hw4-bm25-stem-j623lee.txt', 'a+')
    run_tag = ''.join(['j623lee', ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(5))])

    q = 0
    while q < len(queries):
        bm25 = {}
        topic = str(queries[q], 'utf-8')
        query = str(queries[q+1], 'utf-8')
        terms = list(set(tokenize(query))) # tokenize query and extract unique words
        print('QUERY: '+ query)

        for term in terms:
            term = stemmer.stem(term, 0, len(term)-1) # Toggle for stem vs baseline version
            term_id = str(lexicon[term])
            if term_id not in inv_index: # Inverted index
                inv_index[term_id] = str(open('inverted_index-stem/'+term_id+'.txt', 'rb+').read(),'utf-8')[1:-1].split(', ')
            # print('TERM ID: '+term_id)
            # print('TERM: '+term)
            documents = inv_index[term_id] # Postings list
            n_i = len(documents)/2 # no of docs w term i in them (len of postings list)
            qf_i = query.lower().count(term) # frequency of term i in query
            tf_query = (k_2+1)*qf_i/(k_2+qf_i)
            idf = math.log10((N-n_i+0.5)/(n_i+0.5))

            d = 0
            while d < len(documents):
                # print('DOC ID: '+ str(documents[d]))
                docno = index[documents[d]]
                # print('DOCNO: ' + docno)
                dl = get_doclen(docno)
                f_i = int(documents[d+1]) # frequency of term i in document
                K = k_1*(1-b+b*dl/avdl)
                tf_doc = (k_1+1)*f_i/(K+f_i)
                print('======TESTING TESTING======')
                print('QUERY: '+query)
                print('TERM: '+term)
                print('DOCNO: ' + docno)
                print('K:',str(K))
                print('dl:',str(dl))
                print('fi:',str(f_i))
                print('qfi:',str(qf_i))
                print('ni:',str(n_i))
                if docno in bm25:
                    bm25[docno] += tf_doc*tf_query*idf
                else:
                    bm25[docno] = tf_doc*tf_query*idf
                # print('BM25: '+str(bm25[docno]))
                d += 2
        # print('TOPIC '+str(topic), str(bm25))
        print(bm25)
        bm25_sorted = dict(reversed(sorted(bm25.items(), key=lambda item: item[1])[:1000]))
        write_score_results(f_out, topic, run_tag, list(bm25_sorted.keys()), list(bm25_sorted.values()))
        q += 2


"""
Takes the results retrieved and scored by BM25 and prints it into the desired file location
"""
def write_score_results(output_file, topic, run_tag, docnos, scores):
    # Write averages to output file in readable format
    for i in range(len(scores)):
        docno = docnos[i]
        score = scores[i]
        rank = i+1
        output_file.write(f"{topic} q0 {docno} {rank} {score} {run_tag}\n")
    print('Wrote in file')


"""
This method logic was extracted from homework 3's ComputeAverages.py script, since the original did not have isolated logic
"""
def get_doclen(docno):
    mm = docno[2:4]
    dd = docno[4:6]
    yy = docno[6:8]
    path = '/'.join(['latimes-index-stem', yy, mm, dd, docno+'.txt'])
    f = open(path, 'rb+')
    metadata = f.readlines()
    f.close()
    l = int(str(metadata[-1], 'utf-8').split(' ')[1]) # Check with metadata[3] for titles on two lines
    return l


"""
This method logic was extracted from homework 1's IndexEngine.py script, since the original had extra logic such as writing the output to a specific .txt file
"""
def tokenize(words):
    words = words.lower() # Lower case
    patterns= [r'\w+']
    tokens = []
    for p in patterns:
        tokens.extend(re.findall(p, words)) # Separate tokens by alphanumerics
    return tokens


if __name__ == "__main__":
    boolean_and_retrieval('latimes-index-stem', 'topics.txt', 'hw4-bm25-stem-j623lee.txt', calculate_bm25())
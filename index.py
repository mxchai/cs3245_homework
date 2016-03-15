#!/usr/bin/python
import re
import nltk
import sys
import getopt

from os import listdir
from os.path import isfile, join

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from math import sqrt

stemmer = nltk.stem.porter.PorterStemmer()

# Convenience methods
# python index.py -i /Users/mx/nltk_data/corpora/reuters/training -d dict.txt -p postings.txt
# python index.py -i ./training -d dict.txt -p postings.txt
# python index.py -i ./small -d dict.txt -p postings.txt

def build_index(document_dir):
    """
    Builds the index
    """
    index = {}
    term_freq = {}
    files = listdir(document_dir)
    files.remove(".DS_Store")
    files.sort(key=lambda f: int(f))
    for f in files:
        path = join(document_dir, f)
        if isfile(path):
            input_file = file(path, 'r')
            for line in input_file:
                for sent in sent_tokenize(line):
                    for word in word_tokenize(sent):
                        stemmed_word = stemmer.stem(word)
                        token = stemmed_word.lower()
                        
                        # Builds the document frequency hash table
                        if token not in index:
                            index[token] = []
                        if len(index[token]) == 0 or index[token][-1] != f: # f is file name
                            index[token].append(f)

                        # Builds the term frequency hash table
                        if token not in term_freq:
                            term_freq[token] = []
                        term_freq[token].append(f)

    return (index, term_freq, files)

def write_index(output_dict_file, output_post_file, index, term_freq, doc_ids):
    """
    Writes the index to the output dictionary file and postings file
    """
    dict_file = file(output_dict_file, "w")
    post_file = file(output_post_file, "w")
    count_bytes = 0
    
    for token in index:
        postings = index[token]
        term_occurrences = term_freq[token] # a list of document id (repeats include)

        # Constructing the string to be written into the postings
        postings_string = generate_postings_string(postings, term_occurrences)

        # Constructing the string to be written into the dictionary
        dict_string = token + " " + str(count_bytes) + " " + str(len(postings)) + "\n"

        dict_file.write(dict_string)
        post_file.write(postings_string)
        
        count_bytes += len(postings_string)
    
    dict_file.close()
    post_file.close()

def generate_postings_string(postings, term_occurrences):
    """
    Generates the posting for a term
    """
    # Creates the term frequency hash table
    term_freq = {}
    for doc_id in term_occurrences:
        if doc_id not in term_freq:
            term_freq[doc_id] = 1
        else:
            term_freq[doc_id] += 1

    # Constructs the string
    string = ""
    for doc_id in postings:
        string += doc_id + " " + str(term_freq[doc_id]) + " "
    return string.strip() + "\n"

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

document_dir = output_dict_file = output_post_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        document_dir = a
    elif o == '-d':
        output_dict_file = a
    elif o == '-p':
        output_post_file = a
    else:
        assert False, "unhandled option"
if document_dir == None or output_dict_file == None or output_post_file == None:
    usage()
    sys.exit(2)

# dict and postings creation
(index, term_freq, doc_ids) = build_index(document_dir)
write_index(output_dict_file, output_post_file, index, term_freq, doc_ids)
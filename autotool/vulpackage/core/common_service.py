import os
import sys
import string

import nltk.corpus
from nltk import word_tokenize
from dotenv import load_dotenv, find_dotenv
from nltk.tokenize.treebank import TreebankWordDetokenizer

load_dotenv(find_dotenv())

sys.path.append('.')



class CommonService:

    def __init__(self):
        if os.getenv('download_stopping_words')== "True":
           nltk.download('stopwords')
           nltk.download('punkt')

        self.stopwords = nltk.corpus.stopwords.words('english')
        self.stopwords.extend(string.punctuation)
        self.stopwords.append('')

    def is_duplicate(self,a, b) :

        t_a = [t.lower().strip(string.punctuation) for t in nltk.word_tokenize(a) if t.lower().strip(string.punctuation) not in self.stopwords]
        t_b = [t.lower().strip(string.punctuation) for t in nltk.word_tokenize(b) if t.lower().strip(string.punctuation) not in self.stopwords]

        ratio = len(set(t_a).intersection(t_b)) / float(len(set(t_a).union(t_b)))
        Jcc_percentage = ratio * 100



        if os.getenv('Jaccard')=="True":
           return Jcc_percentage
        else:
            ed = nltk.edit_distance(TreebankWordDetokenizer().detokenize(t_a),
                                    TreebankWordDetokenizer().detokenize(t_b))
            ed_percentage = float(1.0 - ed / max(len(TreebankWordDetokenizer().detokenize(t_a)),
                                                 len(TreebankWordDetokenizer().detokenize(t_b)))) * 100
            return ed_percentage

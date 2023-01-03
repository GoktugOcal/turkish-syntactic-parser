from grammar_converter import GrammarConverter
from tools.morph_analyze import MorphAnalyzer

import numpy as np
import nltk
import zeyrek
from tabulate import tabulate

class Node(object):
    def __init__(self, terminal, child1, child2):
        self.terminal = terminal
        self.child1 = child1
        self.child1 = child2



class TurkishCKYParser:

    def __init__(self, filename, DEBUG=False):
        self.DEBUG = DEBUG
        cg = GrammarConverter(filename)
        cnf = np.unique(np.array(cg.convert_grammar(), dtype = object)).tolist()

        self.analyzer = MorphAnalyzer()

        self.grammar_rules = {}
        self.cky_chart = None
        self.length = 0
        self.num_of_trees = 0
        self.sentence = None
        self.tokens=[]

        for line in cnf:
            a = line[0]
            b = " ".join(line[1:])

            if b not in self.grammar_rules.keys():
                self.grammar_rules[b] = []
            self.grammar_rules[b].append(a)
        

    def get_tag(self, token):
        if token in self.grammar_rules.keys(): return self.grammar_rules[token]
        else: return None

    def tokenize(self, sentence):
        tokens = []
        org_tokens = nltk.tokenize.word_tokenize(sentence)
        for token in org_tokens:
            splitted = self.analyzer.suffix_parse(token)
            for new_token in splitted:
                tokens.append(new_token)

        return tokens
    
    def parse(self, sentence):
        self.sentence = sentence
        self.tokens = self.tokenize(sentence)
        self.pos = [self.get_tag(self.analyzer.get_lemma(token)) for token in self.tokens]
        self.sentence_length = len(self.tokens)

        self.cky_chart = [[[] for x in range(self.sentence_length)] for y in range(self.sentence_length)]
        if self.DEBUG: print("Tokens :", self.tokens)
        if self.DEBUG: print("POS Tags :", self.pos)

        self.init_chart()
        #self.fill_chart()

        
    def init_chart(self):
        # j : column
        for j in range(self.sentence_length):
            token = self.tokens[j]
            pos = self.pos[j]
            # print(token)
            if pos:
                self.cky_chart[j][j] = pos
            else:
                raise ValueError("Word", token, "not in the grammar.")


            for i in range(j-1,-1,-1): # fill row i in column j
                for k in range(i, j): # loop over possible split points k
                    tags_l = self.cky_chart[i][k]
                    tasg_r = self.cky_chart[k+1][j]

                    for l in tags_l:
                        for r in tasg_r:
                            tag = self.get_tag(str(l) + " " + str(r))
                            # print(str(l) + " " + str(r), tag)
                            if tag:
                                for t in tag:
                                    self.cky_chart[i][j].append(t)

    
    def fill_chart(self):
        for span in range(self.sentence_length-1):
            for i in range(self.sentence_length-span):
                self.fill_cell(i,i+span)

    def fill_cell(self, i, j):
        for k in range(i,j-1):
            self.combineCells(i,k,j)

    def combineCells(self, i, k, j):
        print(i,k,j)
        for Y in self.cky_chart[i][k]:
            print("Y :",  Y)
            for Z in self.cky_chart[k+1][j]:
                print(Y, Z)


    def show_cky_chart(self):
        chart = [self.tokens] + self.cky_chart
        print("\n######### CKY CHART #########")
        print(tabulate(chart))


DEBUG = True
filename = "tr_dependency_parser/grammar/grammar_all.txt"
parser = TurkishCKYParser(filename, DEBUG = DEBUG)
#parser.parse("Dün arkadaşıma bir hediye aldım")
#parser.parse("arkadaşıma hediye aldı")
#parser.parse("Dün arkadaşıma bir hediye aldım")
text = [
    "Dün arkadaşıma bir hediye aldım",
    "Tarihi romanları keyifle okuyorum",
    "Ben dün akşam yemeği için anneme yardım ettim",
    "Yüksek sesle müzik dinleme"
    ]
parser.parse(text[3])
parser.show_cky_chart()
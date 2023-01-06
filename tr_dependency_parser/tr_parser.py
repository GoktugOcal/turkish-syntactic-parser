from tr_dependency_parser.grammar_converter import GrammarConverter
from tr_dependency_parser.tools.morph_analyze import MorphAnalyzer
from tr_dependency_parser.tools.helper import *

import numpy as np
import math
import nltk
from nltk.tokenize import TreebankWordTokenizer as twt
import zeyrek
from tabulate import tabulate
# nltk.download('punkt')
import warnings
warnings.filterwarnings("ignore")
import copy

class Node(object):
    def __init__(self, tag, terminal, child1, child2, text = None, prob=None, span=None, token_range=None):
        self.terminal = terminal
        self.text = text
        self.tag = tag
        self.child1 = child1
        self.child2 = child2
        self.prob = prob
        self.span = span
        self.token_range = token_range

class TurkishCKYParser:

    def __init__(self, filename, DEBUG=False):
        self.DEBUG = DEBUG
        cg = GrammarConverter(filename)
        # cnf = np.unique(np.array(cg.convert_grammar(), dtype = object)).tolist()
        cnf = cg.convert_grammar()
        self.cnf = cnf
        self.calculate_prob(filename)
        
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

    def calculate_prob(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()

        tags = []
        for line in lines:
            if "#" in line: continue
            tags.append(line.split(" ->")[0])
        nptags = np.array(tags)
        uniq = np.array(list(set(tags)))
        probs = {}
        for tag in uniq:
            probs[tag] = round(-math.log(len(nptags[nptags == tag]) / len(tags)),2)
        self.probs = probs
        

    def get_pos(self, token):
        if token in self.grammar_rules.keys():
            return [
                Node(
                    tag, 
                    True, 
                    None, 
                    None,
                    text = token, 
                    prob=self.probs[tag], 
                    span=self.spans[token], 
                    token_range=(self.tokens.index(token),self.tokens.index(token))
                    ) for tag in self.grammar_rules[token]]
        else:
            return [
                Node(
                    tag, 
                    True, 
                    None, 
                    None, 
                    text = token, 
                    prob=self.probs[tag], 
                    span=self.spans[token], 
                    token_range=(self.tokens.index(token),self.tokens.index(token))
                    ) for tag in list(set(self.analyzer.word_parse(token)))]
    
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

        return org_tokens
    
    def parse(self, sentence):
        self.sentence = sentence
        self.tokens = self.tokenize(sentence)
        self.spans = dict(zip(self.tokens,[span for span in twt().span_tokenize(sentence)]))
        self.pos = [self.get_pos(token.lower()) for token in self.tokens] ## NEW
        self.sentence_length = len(self.tokens)
        self.cky_chart = [[[] for x in range(self.sentence_length)] for y in range(self.sentence_length)]
        
        print("Tokens :", self.tokens)
        print("POS Tags :", [[node.tag for node in nodes] for nodes in self.pos])

        self.fill_chart()

        tags = [item.tag for item in self.cky_chart[0][-1]]
        if "S" in tags:
            print("Sentence is grammatically correct.")
        else:
            # raise ValueError("Sentence is not grammatically correct...")
            print("Sentence is not grammatically correct...")


        if self.DEBUG:
            for item in self.cky_chart[0][-1]:
                if item.tag == "S":
                    print(tree_format(item), end="\t")
                    print("Score :",round(item.prob,2))

    def fill_chart(self):
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
                    tags_r = self.cky_chart[k+1][j]

                    for l in tags_l:
                        for r in tags_r:
                            tag = self.get_tag(str(l.tag) + " " + str(r.tag))
                            # print(str(l.tag) + " " + str(r.tag), tag)
                            if tag:
                                for t in tag:
                                    self.cky_chart[i][j].append(Node(t, False, l, r, prob=l.prob*r.prob*self.probs[t], span=(l.span[0],r.span[1]), token_range=(l.token_range[0],r.token_range[1])))

    def show_cky_chart(self):
        chart = copy.deepcopy(self.cky_chart)
        for i in range(len(chart)):
            for j in range(len(chart[i])):
                tags = []
                for node in chart[i][j]:
                    tags.append(node.tag)
                chart[i][j] =  tags
        chart = [self.tokens] + chart
        print("\n######### CKY CHART #########")
        print(tabulate(chart))

    def get_trees(self):
        nodes = []
        for item in self.cky_chart[0][-1]:
            if item.tag == "S":
                nodes.append(item)
        return nodes
    
    def get_tree(self):
        best_tree = None
        best_score = np.inf
        for item in self.cky_chart[0][-1]:
            if item.tag == "S":
                if item.prob < best_score:
                    best_score = item.prob
                    best_tree = item
        return best_tree

    def get_terminal_nodes(self, node):
        if node.terminal:
            return [node]
        
        return self.get_terminal_nodes(node.child1) + self.get_terminal_nodes(node.child2)
    
    def show_sentence_structure(self, get=False):
        structure = tree_format(self.get_tree())
        print(structure)
        if get: return structure


    def show_pretty(node):
        terminals = [self.cky_chart[i][i].tag for i in range(len(self.tokens))]
        print(terminals)

if __name__ == "__main__":
    DEBUG = True
    filename = "tr_dependency_parser/grammar/grammar.txt"
    parser = TurkishCKYParser(filename, DEBUG = DEBUG)

    text = [
        "Dün arkadaşıma bir hediye aldım", #0
        "Tarihi romanları keyifle okuyorum", #1
        "Ben dün akşam yemeği için anneme yardım ettim", #2
        "Yüksek sesle müzik dinleme", #3
        "Ben arkadaşıma hediye aldın", #4
        "Benim kalemim oldu", #5
        "Ben okula gittim", #6
        "Ben dün okula gittim", #7
        "Destanlar milli kültürümüzü ve tarihimizi anlatır" #8
        ]

    test = ["Dün arkadaşıma bir hediye aldım",
    "Tarihi romanları keyifle okuyorum",
    "Ben dün akşam yemeği için anneme yardım ettim", ######### !!!!!!!!!
    "Destanlar milli kültürümüzü ve tarihimizi anlatır", ######### ??
    "Yaz meyvelerinden karpuz bence en güzel meyvedir",
    "Bu akşamki toplantıya katılacak mısınız",
    "Bu ağacın altında her gece mehtabı izlerdik",  ######### !!!!!!!!!
    "Siz buraya en son ne zaman geldiniz",
    "Okul bizim köye epeyce uzaktaydı",
    "Yüksek sesle müzik dinleme"]

    false = ["Ben arkadaşıma hediye aldın",
    "Tarihi bir romanlar okudum",
    "Dün babama yardım edeceğim",
    "Ben okul gittim",
    "Ben kitap okundu",
    "Ben okulda gittim"]

    true = ["Ben arkadaşıma hediye aldım",
    "Tarihi romanlar okudum",
    "Dün babama yardım ettim",
    "Ben okula gittim",
    "Ben kitap okudum"]


    parser.parse(test[3])
    parser.show_cky_chart()
    print(tree_format(parser.get_tree()))
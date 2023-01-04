from grammar_converter import GrammarConverter
from tools.morph_analyze import MorphAnalyzer

import numpy as np
import nltk
import zeyrek
from tabulate import tabulate
# nltk.download('punkt')
import warnings
warnings.filterwarnings("ignore")

class Node(object):
    def __init__(self, tag, terminal, child1, child2, text = None):
        self.terminal = terminal
        self.text = text
        self.tag = tag
        self.child1 = child1
        self.child2 = child2


def tree_format(node):
    tag = "_" + node.tag
    
    if node.terminal != True:
        return "[" + tag + tree_format(node.child1) + tree_format(node.child2) + "]"
    else:
        return "[" + tag + " " + node.text + " ]"


class TurkishCKYParser:

    def __init__(self, filename, DEBUG=False):
        self.DEBUG = DEBUG
        cg = GrammarConverter(filename)
        # cnf = np.unique(np.array(cg.convert_grammar(), dtype = object)).tolist()
        cnf = cg.convert_grammar()
        self.cnf = cnf
        
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
        

    def get_pos(self, token):
        if token in self.grammar_rules.keys(): return [Node(tag, True, None, None, text = token) for tag in self.grammar_rules[token]]
        else: return [Node(tag, True, None, None, text = token) for tag in list(set(self.analyzer.word_parse(token)))]
    
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
        # self.pos = [self.get_tag(self.analyzer.get_lemma(token)) for token in self.tokens]

        # self.pos = [[Node(tag, True, None, None, text = token) for tag in list(set(self.analyzer.word_parse(token)))] for token in self.tokens] ## NEW
        self.pos = [self.get_pos(token.lower()) for token in self.tokens] ## NEW
        self.sentence_length = len(self.tokens)

        self.cky_chart = [[[] for x in range(self.sentence_length)] for y in range(self.sentence_length)]
        if self.DEBUG: print("Tokens :", self.tokens)
        if self.DEBUG: print("POS Tags :", [[node.tag for node in nodes] for nodes in self.pos])

        self.init_chart()

        for item in self.cky_chart[0][-1]:
            if item.tag == "S":
                print(tree_format(item))
        
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
                    tags_r = self.cky_chart[k+1][j]

                    for l in tags_l:
                        for r in tags_r:
                            tag = self.get_tag(str(l.tag) + " " + str(r.tag))
                            # print(str(l.tag) + " " + str(r.tag), tag)
                            if tag:
                                for t in tag:
                                    self.cky_chart[i][j].append(Node(t, False, l, r))
       
    
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
        chart = self.cky_chart
        for i in range(len(chart)):
            for j in range(len(chart[i])):
                tags = []
                for node in chart[i][j]:
                    tags.append(node.tag)
                chart[i][j] =  tags
        chart = [self.tokens] + chart
        print("\n######### CKY CHART #########")
        print(tabulate(chart))


DEBUG = True
filename = "tr_dependency_parser/grammar/grammar.txt"
parser = TurkishCKYParser(filename, DEBUG = DEBUG)
# print(parser.cnf)

#parser.parse("Dün arkadaşıma bir hediye aldım")
#parser.parse("arkadaşıma hediye aldı")
#parser.parse("Dün arkadaşıma bir hediye aldım")
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


parser.parse(test[7])
parser.show_cky_chart()
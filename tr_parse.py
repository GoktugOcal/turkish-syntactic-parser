import argparse
from tr_syntactic_parser.tools.helper import *
from tr_syntactic_parser.tr_parser import TurkishCKYParser

parser = argparse.ArgumentParser(
    prog="TR CKY Parser",
    description="CKY parser to parse Turkish Sentences with predefined CNF rules",
    epilog="For any purpose please connect me at goktugocal41@gmail.com")

parser.add_argument("-s", dest="sentence", type=str, required=True)

args = parser.parse_args()

sentence = args.sentence
sentence = preprocess(sentence)

filename = "tr_syntactic_parser/grammar/grammar.txt"
parser = TurkishCKYParser(filename)

parser.parse(sentence)
parser.show_cky_chart()
print("##### BEST SENTENCE STRUCTURE #####")
parser.show_sentence_structure()
print()
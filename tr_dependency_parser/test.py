import numpy as np
import pandas as pd
import conllu
import zeyrek
import nltk
from tqdm import tqdm

from tr_parser import TurkishCKYParser

DEBUG = True
filename = "tr_dependency_parser/grammar/grammar_all.txt"
parser = TurkishCKYParser(filename, DEBUG = DEBUG)

text = '''
Dün arkadaşıma bir hediye aldım
Tarihi romanları keyifle okuyorum
Ben dün akşam yemeği için anneme yardım ettim
Destanlar milli kültürümüzü ve tarihimizi anlatır
Yaz meyvelerinden karpuz bence en güzel meyvedir
Bu akşamki toplantıya katılacak mısınız
Bu ağacın altında her gece mehtabı izlerdik
Siz buraya en son ne zaman geldiniz
Okul bizim köye epeyce uzaktaydı
Yüksek sesle müzik dinleme
'''

org_tokens = nltk.tokenize.word_tokenize(text)

poses = {}
for token in org_tokens:
    for node in parser.get_pos(token.lower()):
        key = token.lower()
        value = node.tag
        if key in poses.keys(): poses[key].add(value)
        else: poses[key] = set([value])

print(poses)
from tr_dependency_parser import helper

import json
import numpy as np
import conllu
from tqdm import tqdm

data_raw = open('data/corpus/UD_Turkish-Penn/tr_penn-ud-train.conllu', 'r', encoding="utf-8").read()
sentences = conllu.parse(data_raw)
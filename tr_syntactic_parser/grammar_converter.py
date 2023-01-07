import numpy as np

class GrammarConverter:
    def __init__(self, CFG):
        with open(CFG, encoding = 'utf-8') as cfg:
            lines = cfg.readlines() # first line is dedicated for list of non-terminals
        CFG = [x.replace(" ->", "").split() for x in lines[1:]]
        CFG = np.unique(np.array(CFG, dtype = object)).tolist()

        self.CNF = [line.replace(" ->", "").split() for line in lines]

    def convert_grammar(self):
        return self.CNF
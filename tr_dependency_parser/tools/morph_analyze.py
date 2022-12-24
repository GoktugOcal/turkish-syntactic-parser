import zeyrek
import json
import numpy as np

class MorphAnalyzer:
    def __init__(self):
        self.analyzer = zeyrek.MorphAnalyzer()
        self.lemma_freq = json.loads(open("tr_dependency_parser/grammar/lemma_freq.json", "r", encoding="utf-8").read())[0]

    def find_best_parse(self, word):
        best_parse = None
        max_freq = 0
        verb_possib = False
        for parsed in self.analyzer.analyze(word)[0]:
            try:
                temp_freq = self.lemma_freq[parsed.lemma]
                if not verb_possib:
                    if temp_freq > max_freq:
                        best_parse = parsed
                        max_freq = temp_freq
                    if parsed.pos == 'Verb':
                        best_parse = parsed
                        max_freq = temp_freq
                else:
                    if parsed.pos == 'Verb':
                        if temp_freq > max_freq:
                            best_parse = parsed
                            max_freq = temp_freq

            except: continue
                
        return best_parse

    def get_lemma(self, token):
        parse = self.find_best_parse(token)
        if parse: return parse.lemma
        else: return token
    
    def suffix_parse(self, token):
        best_parse = self.find_best_parse(token)

        if best_parse:
            if best_parse.pos == "Verb":

                ret = [(part.split(":")[0],part.split(":")[-1]) for part in list(filter(lambda x: ":" in x, best_parse.formatted.split(" ")[-1].split("+")))]
                ret = np.asarray(ret)
                text, types = ret[:,0],ret[:,1]
                
                merged_type = "".join(types[1:])
                suff = "".join(text[1:])

                return [text[0], suff]
            else:
                return [best_parse.word]

        return [token]
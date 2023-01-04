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

    ############# NEW

    def get_time(self, morph_list):
        time = None
        if "Prog1" in morph_list: time =  "Present1"
        if "Prog2" in morph_list: time =  "Present2"
        if "Aor" in morph_list: time = "Present"
        if "Cop" in morph_list: time = "Present"
        if "Fut" in morph_list: time =  "Fut"
        if "Past" in morph_list: time =  "Past"
        return time

    def word_parse(self, token):
        parses = self.analyzer.analyze(token)[0]
        possible = []
        for parse in parses:
            pos = parse.pos
            suff = parse.morphemes[-1]
            time = self.get_time(parse.morphemes)
            if pos == "Verb":                    
                if time != None:
                    nonterminal = "VP"
                    if "Past" in time: nonterminal += "PAST"
                    elif "Present" in time: nonterminal += "PRE"
                    elif "Fut" in time: nonterminal += "FUT"

                    if suff == "A1pl": nonterminal += "1PL"
                    elif suff == "A1sg": nonterminal += "1"
                    elif suff == "A2pl": nonterminal += "2PL"
                    elif suff == "A2sg": nonterminal += "2"
                    elif suff == "A3pl": nonterminal += "3PL"
                    elif suff == "A3sg": nonterminal += "3"

                    possible.append(nonterminal)
                elif "Imp" in parse.morphemes:
                    possible.append("VPIMP")
                
                else: continue
            elif suff == "Gen":
                nonterminal = "GENITIVE"
                if "1pl" in parse.morphemes[-2]: nonterminal += "1PL"
                elif "1sg" in parse.morphemes[-2]: nonterminal += "1"
                elif "2pl" in parse.morphemes[-2]: nonterminal += "2PL"
                elif "2sg" in parse.morphemes[-2]: nonterminal += "2"
                elif "3pl" in parse.morphemes[-2]: nonterminal += "3PL"
                elif "3sg" in parse.morphemes[-2]: nonterminal += "3"
                possible.append(nonterminal)
                
            elif pos == "Noun":
                nonterminal = "NP"

                if "P1pl" in suff: nonterminal += "1PL"
                elif "P1sg" in suff: nonterminal += "1"
                elif "P2pl" in suff: nonterminal += "2PL"
                elif "P2sg" in suff: nonterminal += "2"
                elif "P3pl" in suff: nonterminal += "3PL"
                elif "P3sg" in suff: nonterminal += "3"
                elif "A3pl" in suff: nonterminal += "PL"
                elif suff == "Dat": nonterminal = "DAT"
                elif suff == "Loc": nonterminal = "LOC"

                possible.append(nonterminal)
            elif pos == "Pron":
            
                nonterminal = "PRO"
                if "1pl" in suff: nonterminal += "1PL"
                elif "1sg" in suff: nonterminal += "1"
                elif "2pl" in suff: nonterminal += "2PL"
                elif "2sg" in suff: nonterminal += "2"
                elif "3pl" in suff: nonterminal += "3PL"
                elif "3sg" in suff: nonterminal += "3"

                possible.append(nonterminal)
                return [nonterminal]

            elif token.endswith("le"):
                possible.append("ADV")

            elif "ADV" in pos.upper():
                possible.append("ADV")
            
            elif "ADJ" in pos.upper():
                if "Verb" in parse.morphemes: possible.append("PREQ")
                
                possible.append("ADJ")

            elif "Ques" == pos:
                possible.append("Q")
                
            else: possible.append(pos.upper())
                
        return possible 
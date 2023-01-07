import zeyrek
import json
import numpy as np

class MorphAnalyzer:
    def __init__(self):
        self.analyzer = zeyrek.MorphAnalyzer()

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
                elif "A3pl" in suff: nonterminal += "3PL"
                elif suff == "Dat": nonterminal = "DAT"
                elif suff == "Loc": nonterminal = "LOC"
                elif suff == "Abl": nonterminal = "ABL"
                elif suff == "Acc": nonterminal += "ACC"

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
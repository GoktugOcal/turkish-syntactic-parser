import zeyrek
from time import time
import json
import numpy as np
import conllu
from tqdm import tqdm

# 'data/corpus/UD_Turkish-Penn/tr_penn-ud-train.conllu'
class corpus_parser:
    def __init__(self, corpus_file_path):
        self.data_raw = open(corpus_file_path, 'r', encoding="utf-8").read()
        self.sentences = conllu.parse(self.data_raw)
        
        self.analyzer = zeyrek.MorphAnalyzer()

    def lemma_freq_calculator(self, get = False):

        if get:
            self.lemma_freq = json.loads(open(get, "r", encoding="utf-8").read())[0]
        else:
            lemmas = []
            for sent in tqdm(self.sentences):
                for token in sent:
                    lemma = token["lemma"].lower()
                    lemmas.append(lemma)
            lemmas = np.array(lemmas)

            uniq, counts = np.unique(lemmas, return_counts=True)
            counts = counts.astype("float")
            self.lemma_freq = dict(zip(uniq,counts))

            with open("tr_syntactic_parser/grammar/lemma_freq.json", "w", encoding='utf8') as f:
                f.write(json.dumps([self.lemma_freq], ensure_ascii=False))

            print("Lemma frequencies were saved to :", "tr_syntactic_parser/grammar/lemma_freq.json")
            
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

    def suffix_morpheme_combiner(self):
        sentences = self.sentences

        merged_types = {}
        for sent in tqdm(sentences):
            for token in sent:
                try:
                    word = token["form"]
                    best_parse = self.find_best_parse(word)

                    if best_parse:
                        ret = [(part.split(":")[0],part.split(":")[-1]) for part in list(filter(lambda x: ":" in x, best_parse.formatted.split(" ")[-1].split("+")))]
                        ret = np.asarray(ret)
                        text, types = ret[:,0],ret[:,1]
                        
                        merged_type = "".join(types[1:])
                        if "→" in merged_type or "|" in merged_type: continue
                        if merged_type in merged_types.keys(): merged_types[merged_type].add("".join(text[1:]))
                        else: merged_types[merged_type] = set(["".join(text[1:])])
                    
                except:
                    continue

        temp = {}
        for key in merged_types.keys():
            if "Prog" in key or "Fut" in key or "Past" in key:
                temp[key] = list(merged_types[key])
        with open('tr_syntactic_parser/grammar/combined_verb_suffix_morphemes.json', 'w') as f:
            json.dump(temp, f)
        
        print("Saved to :", "tr_syntactic_parser/grammar/combined_verb_suffix_morphemes.json")

    def get_all_suffix_classes(self):
        fixes = {}
        for sent in tqdm(self.sentences):
            for token in sent:
                word = token["form"]
                if token["upos"] == "VERB":
                    best_parse = self.find_best_parse(word)

                    if best_parse == None: continue
                    else:            
                        for item in best_parse.formatted.split(" ")[1].split("+"):
                            if ":" in item:
                                splitted = item.split(":")
                                token = splitted[0]
                                type_ = splitted[1].split("|")[0]

                                if type_ in fixes.keys(): fixes[type_].add(token)
                                else: fixes[type_] = set(token)
        temp = {}
        for key in fixes.keys():
            temp[key] = list(fixes[key])

        with open("tr_syntactic_parser/grammar/all_suffix_classes.json","w", encoding='utf-8') as f:
            json.dump(temp, f)

        print("Saved to :", "tr_syntactic_parser/grammar/all_suffix_classes.json")

        
    def verb_suffix_to_cnf(self):
        temp = json.loads(open("tr_syntactic_parser/grammar/combined_verb_suffix_morphemes.json","r").read())
        str = ""
        for key in temp.keys():
            if "Past" in key: tense = "PAST"
            elif "Prog" in key: tense = "PRE"
            elif "Fut" in key: tense = "FUT"
            else: continue
                
            if "1" in key: finalkey = tense+"1"
            elif "2" in key: finalkey = tense+"2"
            elif "3" in key: finalkey = tense+"3"
            else: finalkey = tense+"3"
                
            for suff in temp[key]:
                str += "\n" + finalkey + " -> " + suff

        with open("tr_syntactic_parser/grammar/verb_suffix_cnf.txt","w", encoding='utf-8') as f:
            f.write(str)

        print("Saved to :", "tr_syntactic_parser/grammar/verb_suffix_cnf.txt")
    
    def lexicon_builder(self):
        sentences = self.sentences
        lexicon = {}
        stems = set()
        for sent in sentences:
            for token in sent:
                upos = token["upos"]
                if upos in lexicon.keys(): lexicon[upos].add(token["lemma"].lower())
                else: lexicon[upos] = set([token["lemma"].lower()])
                stems.add(token["lemma"].lower())
        
        temp = {}
        for key in lexicon.keys():
            temp[key] = list(lexicon[key])

        with open("tr_syntactic_parser/grammar/the_lexicon_reversed.json","w", encoding='utf-8') as f:
            json.dump(temp, f)

        print("Lexicon was saved to :", "tr_syntactic_parser/grammar/the_lexicon_reversed.json")
import spacy
from spacy import displacy

class parse_visualizer:
    def __init__(self):
        with open("tr_dependency_parser/grammar/grammar.txt", "r") as f:
            lines = f.readlines()
            
        nonterm = set([line.split(" ->")[0] if "#" not in line else "" for line in lines])
        color_dict = {
            "NP" : "turquoise",
            "PRO" : "palevioletred",
            "ADJ" : "lime",
            "VP" : "lightpink",
            "ADV" : "khaki",
            "POSTP" : "cornflowerblue",
            "SG" : "tomato",
            "S" : "tomato",
            "DET" : "limegreen",
            "DAT" : "limegreen",
            "NUM" : "salmon",
            "Q" : "y",
            "GENITIVE" : "green"
        }

        colors = {}
        for nont in nonterm:
            colors[nont] = None
            for key in color_dict.keys():
                if key in nont:
                    colors[nont] = color_dict[key]
                    break
        self.colors = colors
        self.options = {"ents" : nonterm, "colors" : colors}

    
    def pos_vis(self, sentence, terminals):
        ents = []
        for terminal in terminals:
            ents.append({"start" : terminal.span[0], 
                        "end"   : terminal.span[1], 
                        "label" : terminal.tag })

        doc = {"text" : sentence, "ents" : ents}
        return displacy.render(
            doc, 
            style = "ent",
            options = self.options,
            manual = True,
        )
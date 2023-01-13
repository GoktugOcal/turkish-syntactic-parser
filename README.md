# GOKTU_NLP - TURKISH NLP SYNTACTIC PARSER /w CKY ALGORITHM

> **Note**
> This toolbox is prepared for CMPE561 Natural Language Processing course given by Prof. Dr. Tunga Gungor in Boğaziçi University.

Syntactic parsing is the process of analyzing a sentence or a piece of text and determining its grammatical structure. This includes identifying the constituent phrases and dependencies between the words, as well as determining the roles played by each word in the sentence (such as the subject, verb, and object). In this project, we have developed a Turkish Language CKY Parser which is fed from Chomsky's Normal Form (CNF) grammar rules and a lexicon. The process of parsing and the generation of CNF rules and lexicon are described.


## Installation

1- Download codes.
```shell
$ git clone https://github.com/GoktugOcal/turkish-syntactic-parser.git
```

2- Install required packages.
```shell
$ pip install -r requirements.txt
```

## Usage

### Use from CLI
```shell
$ python tr_parse.py -s [<string>]
```

```shell
$ python tr_parse.py -s "Ben okula gittim."

Tokens : ['ben', 'okula', 'gittim']
POS Tags : [['PRO1'], ['DAT'], ['VPPAST1']]
Sentence is grammatically correct.

######### CKY CHART #########
--------  -------  -----------
ben       okula    gittim
['PRO1']  []       ['S']
[]        ['DAT']  ['VPPAST1']
[]        []       ['VPPAST1']
--------  -------  -----------
##### BEST SENTENCE STRUCTURE #####
(S(PRO1 ben ) (VPPAST1(DAT okula ) (VPPAST1 gittim ) ))

```

### Use in Python

```python
from tr_syntactic_parser.tools.helper import *
from tr_syntactic_parser.tr_parser import TurkishCKYParser

sentence = "..." # put your sentence
sentence = preprocess(sentence) # preprocess the sentence

filename = "tr_syntactic_parser/grammar/grammar.txt" # specify the location of CNF grammar"
parser = TurkishCKYParser(filename) # initialize the parser

parser.parse(sentence) # parse
parser.show_cky_chart() # show filled CKY chart
print("##### BEST SENTENCE STRUCTURE #####")
parser.show_sentence_structure() # show best possible sentence structure
```

### Visualization
A parse visualizer class have been implemented with using [Plotly](https://plotly.com/) and [Spacy](https://spacy.io/). The parse visualizer has three components.


First of all, run the parser
```python
from tr_syntactic_parser.tools.helper import *
from tr_syntactic_parser.tr_parser import TurkishCKYParser
sentence = "..."
sentence = preprocess(sentence)
filename = "tr_syntactic_parser/grammar/grammar.txt"
parser = TurkishCKYParser(filename)

terminals = parser.get_terminal_nodes(parser.get_tree()) # Get terminal nodes
```
> All the visualizations can be done esily on Jupyter Notebook.

#### POS tag visualizer (powered by Spacy)

> Show on Notebook
```python
from tr_syntactic_parser.tools.visualizer import parse_visualizer

visualizer = parse_visualizer() # Initialize 
visualizer.pos_vis(sentence, terminals)
```
![POS tag visualization](/img/pos_test.png "POS tags")

#### Sentence structure visualizer (powered by Spacy)

> Show on Notebook
```python
from tr_syntactic_parser.tools.visualizer import parse_visualizer

visualizer = parse_visualizer() # Initialize 
visualizer.pos_tree_vis(sentence, parser.tokens, parser.get_tree()) # we need tokens of sentence and root of the tree in that case
```
![POS tree visualization](/img/pos_tree_test.png "Sentence Structure")

- Save Spacy output as PNG
```python
from tr_syntactic_parser.tools.visualizer import parse_visualizer

visualizer = parse_visualizer() # Initialize 


svg = visualizer.pos_vis(sentence, terminals, jupyter=False)# set jupyter=False
# or
svg = visualizer.pos_tree_vis(sentence, parser.tokens, parser.get_tree(), jupyter=False)

from tr_syntactic_parser.tools.helper import spacy_svg2png_save # import function from helpers
spacy_svg2png_save(svg, sentence, output_path = "./") # convert svg to png
```


#### Structure tree visualizer (powered by Plotly)

> Show on Notebook
```python
from tr_syntactic_parser.tools.visualizer import parse_visualizer

visualizer = parse_visualizer() # Initialize 
visualizer.tree_vis(sentence, parser.tokens, parser.get_tree()) # we need tokens of sentence and root of the tree in that case
```

![Tree visualization](/img/trees/[tree]dun_arkadasima_bir_hediye_aldim.png "Sentence Tree Structure")


> Save as
```python
output_file = "..."
visualizer.tree_vis(sentence, parser.tokens, parser.get_tree()).write_image(output_file)
```

## Acknowledgement
Some parts of this tool is created by using [Zeyrek](https://github.com/obulat/zeyrek) Morphology Analyzer and [NLTK](https://www.nltk.org).

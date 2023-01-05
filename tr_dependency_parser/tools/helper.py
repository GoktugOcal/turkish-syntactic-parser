import string

def preprocess(text):
    text = text.lower()
    for punc in string.punctuation:
        text = text.replace(punc, "")

    return text

def tree_format(node):
    tag = "_" + node.tag
    
    if node.terminal != True:
        return "[" + tag + tree_format(node.child1) + tree_format(node.child2) + "]"
    else:
        return "[" + tag + " " + node.text + " ]"
import string

def preprocess(text):
    text = text.lower()
    for punc in string.punctuation:
        text = text.replace(punc, "")

    return text

def tree_format(node):
    tag = node.tag
    
    if node.terminal != True:
        return "(" + tag + tree_format(node.child1) + tree_format(node.child2) + ")"
    else:
        return "(" + tag + " " + node.text + " ) "


def spacy_svg2png_save(svg, sentence, output_path = "./"):
    from html2image import Html2Image
    import unidecode
    import os

    hti = Html2Image(output_path = output_path)
    head = '''<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html dir="rtl" xmlns="http://www.w3.org/1999/xhtml">'''

    coded_sentence = unidecode.unidecode("_".join(sentence.split(" ")))
    open(output_path + "[ent]" + coded_sentence + ".svg", "w", encoding="utf-8").write(head + svg + "</html>")
    hti.screenshot(other_file=output_path + "[ent]" + coded_sentence + ".svg", save_as = "[ent]" + coded_sentence + ".png", size=(1080, 40))
    print("Saved to", output_path + "[ent]" + coded_sentence + ".png")
    os.remove(output_path + "[ent]" + coded_sentence + ".svg")
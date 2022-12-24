from tr_dependency_parser.misc.suffix_provider import corpus_parser
# 'data/corpus/UD_Turkish-Penn/tr_penn-ud-train.conllu'
corpus_parser = corpus_parser('data/corpus/UD_Turkish-Penn/tr_penn-ud-train.conllu')
corpus_parser.lemma_freq_calculator(get = "tr_dependency_parser/grammar/lemma_freq.json")
corpus_parser.get_all_suffix_classes()

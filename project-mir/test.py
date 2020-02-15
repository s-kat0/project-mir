import stanfordnlp

nlp = stanfordnlp.Pipeline(processors='tokenize,mwt,pos', models_dir='./data/stanfordnlp_resources')
doc = nlp("Barack Obama was born in Hawaii.")
print(*[f'word: {word.text+" "}\tupos: {word.upos}\txpos: {word.xpos}' for sent in doc.sentences for word in sent.words], sep='\n')


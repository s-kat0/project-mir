import os
from pathlib import Path
import stanfordnlp

# if system cannot load model, download model as below.
# currentPath = Path(os.getcwd())
# MODELS_DIR = os.path.join(currentPath, 'data/stanfordnlp_resources')
# stanfordnlp.download('en', resource_dir='/project-mir/data/stanfordnlp_resources')   # This downloads the English models for the neural pipeline

currentPath = Path(os.getcwd())
MODELS_DIR = os.path.join(currentPath, 'data/stanfordnlp_resources')
nlp = stanfordnlp.Pipeline(processors='tokenize,mwt,pos',#lemma,depparse', 
                           models_dir=MODELS_DIR,
                           )
doc = nlp("Barack Obama was born in Hawaii.")
# print(*[f'word: {word.text+" "}\tupos: {word.upos}\txpos: {word.xpos}' for sent in doc.sentences for word in sent.words], sep='\n')
print(*[f"index: {word.index.rjust(2)}\tword: {word.text.ljust(11)}\tgovernor index: {word.governor}\tgovernor: {(doc.sentences[0].words[word.governor-1].text if word.governor > 0 else 'root').ljust(11)}\tdeprel: {word.dependency_relation}" for word in doc.sentences[0].words], sep='\n')

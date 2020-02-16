import os
from pathlib import Path
import stanfordnlp

# Find 'stanfordmlp_resources' folder which containes models
currentPath = Path(os.getcwd())
MODELS_DIR = os.path.join(currentPath, 'data/stanfordnlp_resources')

def main():
    nlp = stanfordnlp.Pipeline(processors='tokenize,mwt,pos', models_dir=MODELS_DIR)
    doc = nlp("Barack Obama was born in Hawaii.")
    print(*[f'word: {word.text+" "}\tupos: {word.upos}\txpos: {word.xpos}' for sent in doc.sentences for word in sent.words], sep='\n')
    
if __name__=='__main__':
    main()

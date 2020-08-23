# import copy
from dataclasses import dataclass, field
from typing import List
import time
import warnings
import lxml.html
import re

import stanza
from stanza.server import CoreNLPClient

from projectmir.xmldoc_child import Identifier, Formulae, Sentence, Candidate


@dataclass
class XMLDocument:
    path: str
    title: str = ''
    namespace: str = ''
    document_id: int = 0
    text: str = ''
    body: str = ''
    identifiers: List[Identifier] = field(default_factory=list)
    formulae: List[Formulae] = field(default_factory=list)
    sentences_list: List[str] = field(default_factory=list)

    def __post_init__(self):
        start_time = time.time()
        print('loaded data.')
        print('processing data...')
        self.processor()
        print('extract identifiers...')
        self.extract_identifiers()
        print('POS tagging...')
        self.pos_tagging()
        print('extract candidate definition...')
        self.extract_candidate_definition()
        print(f'elapsed time: {(time.time() - start_time):.5f} seconds ---')

    def processor(self):
        """process a document and extract text from html.
        """
        title_regexp = re.compile(r'(?:<title>)(.*?)(?:</title>)', re.DOTALL)
        namespace_regexp = re.compile(r'(?:<ns>)(.*?)(?:</ns>)', re.DOTALL)
        id_regexp = re.compile(
            r'(?:<revision>.*?<id>)(\d+)(?:</id>)', re.DOTALL)
        text_regexp = re.compile(r'(?:<text.*?>)(.*?)(?:</text>)', re.DOTALL)
        body_regexp = re.compile(r'(?:<body.*?>)(.*?)(?:</body>)', re.DOTALL)
        annotation_xml_regexp = re.compile(
            r'(?:<annotation-xml.*?>)(.*?)(?:</annotation-xml>)', re.DOTALL)
        annotation_regexp = re.compile(
            r'(?:<annotation.*?>)(.*?)(?:</annotation>)', re.DOTALL)

        with open(self.path, 'r') as document_open:
            document_read = document_open.read()
            title = title_regexp.findall(document_read)
            namespace = namespace_regexp.findall(document_read)
            document_id = id_regexp.findall(document_read)
            text = text_regexp.findall(document_read)
            body = body_regexp.findall(document_read)

            if title:
                self.title = title[0]
            if namespace:
                self.namespace = namespace[0]
            if document_id:
                self.document_id = document_id[0]
            if text:
                self.text = text[0]
            if body:
                body = body[0]
                # remove annotation-xml tag and annotation tag
                body = annotation_xml_regexp.sub('', body)
                body = annotation_regexp.sub('', body)
                self.body = body
            print("preprocessed document")

    # TODO: 変数の定義を変更する
    # 現在：mathタグ内のタグを調べ，mi, moタグを有するものを変数としている
    # 理想：文中に登場する斜体文字．文中に登場するmathの中身で=を有さないもの．
    # こうすることで，文中に存在する連続する斜体文字を変数と認識できる．
    # さらに，数式を文中で定義された変数の関係を表すものと考え，
    # 数式に登場する変数の意味を正確に抽出することを目指す．
    def extract_identifiers(self):
        """extract identifiers from sentences.
        """
        tree = lxml.html.parse(self.path)
        html = tree.getroot()
        math_components = html.cssselect("math")
        print(f'Number of math components is {len(math_components)}')
        replaced_string_list = []
        identifiers = []

        # def is_identifier(math_component):
        #     is_mi = (math_component.tag == 'mi')
        #     is_math_component_len_1 = (len(math_component.text_content()) == 1)
        #     is_italic = (math_component.get('mathvariant') == 'italic')
        #     return is_mi and (is_math_component_len_1 or is_italic)

        def is_identifier(math_txt: str) -> bool:
            """return whether input string represents a variable.

            Args:
                math_txt (str): text that represents an identifier.

            Returns:
                bool: Is math_txt is a variable?
            """
            not_number = math_txt[0] not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            return not_number

        def tree_to_str(ml_tree):
            """identify identifiers and encode MathML to TeX-like text.

            Args:
                ml_tree (HtmlElement of list):

            Returns:
                math_txt (str): encoded TeX-like text.
            """
            if isinstance(ml_tree, lxml.html.HtmlElement):
                if ml_tree.tag in ['mi', 'mo', 'mn']:
                    math_txt = ml_tree.text_content()
                else:
                    ml_list = [tree_to_str(x) for x in ml_tree]
                    if ml_tree.tag == 'mrow':
                        math_txt = ''.join(ml_list)
                    elif ml_tree.tag == 'msubsup':
                        math_txt = ml_list[0] + '_' + ml_list[1] \
                                   + '^' + ml_list[2]
                    elif ml_tree.tag == 'msub':
                        math_txt = ml_list[0] + '_' + ml_list[1]
                    elif ml_tree.tag == 'msup':
                        math_txt = ml_list[0] + '^' + ml_list[1]
                    elif ml_tree.tag == 'munderover':
                        math_txt = r'\overset{' + ml_list[2] + '}{' + \
                                   r'\underset{' + ml_list[1] + '}{' + ml_list[0] + '}}'
                    elif ml_tree.tag == 'mover':
                        math_txt = r'\overset{' + \
                                   ml_list[1] + '}{' + ml_list[0] + '}'
                    elif ml_tree.tag == 'munder':
                        math_txt = r'\underset{' + \
                                   ml_list[1] + '}{' + ml_list[0] + '}'
                    else:
                        math_txt = ''
                        warnings.warn('unexpected tag')
                        print(f'{ml_tree}')
                        print('######################')

            elif isinstance(ml_tree, list):
                ml_list = [tree_to_str(x) for x in ml_tree]
                math_txt = ''.join(ml_list)

            else:
                math_txt = ''
                warnings.warn('unexpected tag')
                print(f'{ml_tree}')
                print('######################')

            return math_txt

        def extract_ml_component(
                html_cssselect_math,
                mltag,
                identifiers,
                replaced_string_list):
            """update identifiers.
            output 'replaced_string_list' is used to replace identifiers in original text
            to 'MATHXXXX' (XXXX means number of identifiers).

            Args:
                html_cssselect_math (lxml.html.HtmlElement): extracted text that has math tag.
                mltag (str): tag that represents a math identifier.
                identifiers (list): list containing identifier.
                replaced_string_list (list): explained above.

            Returns:
                identifiers (list): updated identifiers
                replaced_string_list (list): updated replace_string_list
            """
            identifiers_ = list(identifiers)
            replaced_string_list_ = list(replaced_string_list)
            for html_math_mltag in html_cssselect_math.cssselect(mltag):
                math_txt = tree_to_str(html_math_mltag)
                if is_identifier(math_txt) and (math_txt not in identifiers_):
                    identifiers_.append(math_txt)
                html_math_mltag.drop_tree()
                replaced_string_ = lxml.html.tostring(html_math_mltag,
                                                      encoding='unicode')
                if is_identifier(math_txt):
                    replaced_string_list_.append(
                        (math_txt,
                         replaced_string_,
                         f'MATH{(identifiers_.index(math_txt)):04d}'))
                else:
                    replaced_string_list_.append(
                        (math_txt, replaced_string_, math_txt))
            return identifiers_, replaced_string_list_

        ml_tags = ['msubsup', 'msub', 'msup',
                   'munderover', 'munder', 'mover', 'mi']

        for html_math in math_components:
            html_math_alttext = html_math.attrib['alttext']
            if '=' in html_math_alttext:
                self.formulae.append(
                    Formulae(text_tex=html_math_alttext, text_replaced=html_math_alttext))
            for ml_tag in ml_tags:
                identifiers, replaced_string_list = extract_ml_component(
                    html_math, ml_tag, identifiers, replaced_string_list)

        replaced_string_list = list(set(replaced_string_list))
        replaced_string_list = sorted(
            replaced_string_list, key=lambda x: len(x[0]), reverse=True)
        for replaced_string in replaced_string_list:
            self.body = self.body.replace(replaced_string[1], replaced_string[2])
            for i_formula, _ in enumerate(self.formulae):
                text_replaced_ = self.formulae[i_formula].text_replaced
                text_replaced_ = text_replaced_.replace(replaced_string[0], replaced_string[2])
                self.formulae[i_formula].text_replaced = text_replaced_
        self.text = lxml.html.fromstring(self.body).text_content()
        self.sentence_segmentation()

        for i, identifier_ in enumerate(identifiers):
            sentences_list_ = []
            for sentence in self.sentences_list:
                math_txt = f'MATH{i:04d}'
                if math_txt in sentence:
                    sentences_list_.append(Sentence(original=sentence))
            self.identifiers.append(Identifier(text_tex=identifier_,
                                               id=i,
                                               sentences=sentences_list_))

    def sentence_segmentation(self):
        """extract sentences which contain the identifier from the text.
        sentences are segmented using stanza.

        Returns:
            sentences (list): sentences which contain the identifier the text.
        """
        # stanza.download('en')
        nlp = stanza.Pipeline(lang='en', processors='tokenize')
        doc_sentence_segmented = nlp(self.text)
        sentences_list_ = []
        for i, sentence in enumerate(doc_sentence_segmented.sentences):
            sentence_text = ' '.join([f'{token.text}' for token in sentence.tokens])
            sentences_list_.append(sentence_text)
        self.sentences_list = sentences_list_

    def pos_tagging(self):
        """POS tags are used for pattern-based extraction.
        """
        with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos'], timeout=600000, memory='16G') as client:
            for i, identifier in enumerate(self.identifiers):
                sentences_list = identifier.sentences
                if sentences_list:
                    for j, sentence in enumerate(sentences_list):
                        # submit the request to the server.
                        ann = client.annotate(sentence.original)
                        sentence_ = ann.sentence[0]
                        word_pos = [(token.word, token.pos) for token in sentence_.token]
                        self.identifiers[i].sentences[j].tagged = word_pos

    def extract_candidate_definition(self):
        def extract_noun_phrases(_client, _text, _annotators=None):
            pattern = 'NP'
            matches = _client.tregex(_text, pattern, annotators=_annotators)
            return [sentence[match_id]['spanString'] for sentence in matches['sentences'] for match_id in sentence]

        # https://github.com/stanfordnlp/stanza/issues/288
        # get noun phrases with tregex
        with CoreNLPClient(timeout=30000, memory='16G') as client:
            noun_phrase_list = []
            for i, identifier in enumerate(self.identifiers):
                if identifier.sentences:
                    sentence = identifier.sentences[0].original
                    noun_phrase_list = extract_noun_phrases(
                        client,
                        sentence,
                        _annotators='tokenize,ssplit,pos,lemma,parse')

                    for j, noun_phrase in enumerate(noun_phrase_list):
                        noun_phrase = noun_phrase.rstrip(', ')
                        if noun_phrase[-8:-4] == 'MATH':
                            noun_phrase = noun_phrase[:-8].rstrip(', ')
                        if noun_phrase and (noun_phrase not in noun_phrase_list):
                            noun_phrase_list.append(noun_phrase)
                            self.identifiers[i].candidates.append(
                                Candidate(text=noun_phrase,
                                          included_sentence=sentence))

    def pattern_based_extract_description(self):
        """extract description based on the following pattern.

        Although original patterns are proposed by Pagel [1],
        their <description> does not include a determiner (DT).
        To simplify the pattern, we assume that <description>
        includes determiner.
        <description> can be either pattern: include determiner
        or not include determiner (proper noun).

        # 1. <description> <identifier>
        # 2. <identifier> is <description>
        # 3. let <identifier> be <description>
        # 4. <description> is|are denoted by <identifier>
        # 5. <identifier> denotes <description>

        [1]: Pagel, R. and Schubotz, M.: Mathematical Language Processing Project,
        in Joint Proceedings of the MathUI, OpenMath and ThEdu Workshops and Work
        in Progress track at CICM, No. 1186, Aachen (2014)
        """
        for math_id_, _ in enumerate(self.identifiers):
            extracted_description_list = []
            print(math_id_)
            identifier = f'MATH{math_id_:04d}'
            candidates_list = self.identifiers[math_id_].candidates
            for candidate_ in candidates_list:
                description_candidate = candidate_.text
                replace_pattern_list = ['(', ')', '[', ']', '{', '}']
                for replace_pattern_ in replace_pattern_list:
                    description_candidate = \
                        description_candidate.replace(
                            replace_pattern_,
                            '\\' + replace_pattern_)
                sentence = candidate_.included_sentence
                pattern_list = [
                    re.compile(description_candidate + ' ' + identifier),
                    re.compile(identifier + ' is ' + description_candidate),
                    re.compile('let ' + identifier + ' be ' + description_candidate),
                    re.compile(description_candidate + r' is denoted by ' + identifier),
                    re.compile(identifier + ' denotes ' + description_candidate)
                ]

                for pattern_ in pattern_list:
                    if pattern_.search(sentence):
                        extracted_description_list.append(description_candidate)

            self.identifiers[math_id_].pattern_based_candidates = extracted_description_list

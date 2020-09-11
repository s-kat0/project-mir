import copy
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
    sentences_list: List[Sentence] = field(default_factory=list)

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
        self.extract_definition_candidate()
        print('compute the properties of candidates...')
        self.compute_candidate_statistics()
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
            ml_list = []
            if isinstance(ml_tree, lxml.html.HtmlElement):
                if ml_tree.tag in ['mi', 'mo', 'mn']:
                    math_txt = ml_tree.text_content()
                    ml_list = [math_txt]
                else:
                    ml_list = [tree_to_str(x)[0] for x in ml_tree]
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
                ml_list = [tree_to_str(x)[0] for x in ml_tree]
                math_txt = ''.join(ml_list)

            else:
                math_txt = ''
                warnings.warn('unexpected tag')
                print(f'{ml_tree}')
                print('######################')

            return math_txt, ml_list

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
                math_txt, ml_list_ = tree_to_str(html_math_mltag)
                ml_list = []
                # print(ml_list_)
                # TODO: moverunderに対応する．
                for ml_ in ml_list_:
                    ml_component = re.findall(
                        '[over|under]set{(.+)}{(.+)}', ml_)
                    if ml_component:
                        ml_list.extend(
                            [ml_component[0][0], ml_component[0][1]])
                    else:
                        ml_list.append(ml_)
                if is_identifier(math_txt) and (
                        (math_txt, ml_list) not in identifiers_):
                    identifiers_.append((math_txt, ml_list))
                html_math_mltag.drop_tree()
                replaced_string_ = lxml.html.tostring(html_math_mltag,
                                                      encoding='unicode')
                if is_identifier(math_txt):
                    replaced_string_list_.append(
                        (math_txt,
                         replaced_string_,
                         f'MATH{(identifiers_.index((math_txt, ml_list))):04d}'))
                else:
                    replaced_string_list_.append(
                        (math_txt, replaced_string_, math_txt))
            return identifiers_, replaced_string_list_

        ml_tags = ['msubsup', 'msub', 'msup',
                   'munderover', 'munder', 'mover', 'mi']


        # TODO: formulaeを正しく抜き出せるようにする．
        for html_math in math_components:
            math_text_list = html_math.cssselect('math')
            for math_text_ in math_text_list:
                math_text_string = lxml.html.tostring(math_text_, encoding='unicode')
                if '>=<' in math_text_string:
                    self.formulae.append(
                        Formulae(
                            text_tex=lxml.html.fromstring(math_text_string).text_content(),
                            text_replaced=math_text_string))
            for ml_tag in ml_tags:
                identifiers, replaced_string_list = extract_ml_component(
                    html_math, ml_tag, identifiers, replaced_string_list)

        replaced_string_list = list(set(replaced_string_list))
        replaced_string_list = sorted(
            replaced_string_list, key=lambda x: len(x[0]), reverse=True)
        for replaced_string in replaced_string_list:
            self.body = self.body.replace(
                replaced_string[1], replaced_string[2])
            for i_formula, _ in enumerate(self.formulae):
                text_replaced_ = self.formulae[i_formula].text_replaced
                text_replaced_ = text_replaced_.replace(
                    replaced_string[1], replaced_string[2])
                self.formulae[i_formula].text_replaced = text_replaced_
        self.text = lxml.html.fromstring(self.body).text_content()
        self.sentence_segmentation()

        for i, identifier_ in enumerate(identifiers):
            sentences_list_ = []
            for sentence in self.sentences_list:
                math_txt = f'MATH{i:04d}'
                if math_txt in sentence.original:
                    sentences_list_.append(sentence)
            self.identifiers.append(Identifier(text_tex=identifier_[0],
                                               mi_list=identifier_[1],
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
            sentence_text = ' '.join(
                [f'{token.text}' for token in sentence.tokens])
            sentences_list_.append(Sentence(id=i, original=sentence_text))
        self.sentences_list = sentences_list_

    def pos_tagging(self):
        """POS tags are used for pattern-based extraction.
        this method is based on stanza.
        """
        nlp = stanza.Pipeline('en')
        for i, identifier in enumerate(self.identifiers):
            sentence_list = identifier.sentences
            if sentence_list:
                for j, sentence in enumerate(sentence_list):
                    doc = nlp(sentence.original)
                    for sentence_ in doc.sentences:
                        word_pos = [(word.text, word.xpos)
                                    for word in sentence_.words]
                        self.identifiers[i].sentences[j].tagged = word_pos

    def pos_tagging_corenlp(self):
        """POS tags are used for pattern-based extraction.
        this method is based on Stanford CoreNLP.
        Sometimes, the pos tagging is not correct.
        e.g. if you use the sentence "Integrating Eq. 2-x...",
        this method identify dot(.) as the end of the sentence.
        """
        with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos'], timeout=600000, memory='16G') as client:
            for i, identifier in enumerate(self.identifiers):
                sentences_list = identifier.sentences
                if sentences_list:
                    for j, sentence in enumerate(sentences_list):
                        # submit the request to the server.
                        ann = client.annotate(sentence.original)
                        sentence_ = ann.sentence[0]
                        word_pos = [(token.word, token.pos)
                                    for token in sentence_.token]
                        self.identifiers[i].sentences[j].tagged = word_pos

    def extract_definition_candidate(self):
        """extract definition candidate from candidate-included sentence.
        assumed that the definition is not a equation and does not have '=' and '≈'.
        """

        def extract_noun_phrases(_client, _text, _annotators=None):
            pattern = 'NP'
            matches = _client.tregex(_text, pattern, annotators=_annotators)
            return [sentence[match_id]['spanString']
                    for sentence in matches['sentences'] for match_id in sentence]

        # https://github.com/stanfordnlp/stanza/issues/288
        # get noun phrases with tregex
        with CoreNLPClient(timeout=30000, memory='16G') as client:
            for i, identifier_ in enumerate(self.identifiers):
                definition_candidate_list = []
                if identifier_.sentences:
                    for sentence_ in identifier_.sentences:
                        noun_phrase_list = extract_noun_phrases(
                            client,
                            sentence_.original,
                            _annotators='tokenize,ssplit,pos,lemma,parse')

                        for j, noun_phrase in enumerate(noun_phrase_list):
                            noun_phrase_ = noun_phrase.rstrip(', ')
                            if noun_phrase_[-8:] == f'MATH{i:04d}':
                                noun_phrase_ = noun_phrase_[:-8].rstrip(', ')
                            if noun_phrase_ and (
                                    noun_phrase_ not in definition_candidate_list) and (
                                    f'MATH{i:04d}' not in noun_phrase_) and not (
                                    re.search('[=|≈]', noun_phrase_)) and ('MATH' not in noun_phrase_):
                                definition_candidate_list.append(noun_phrase_)
                                included_sentence = copy.copy(sentence_)
                                included_sentence.replaced = included_sentence.original.replace(
                                    noun_phrase_, 'CANDIDATE').rstrip(',. :;')
                                self.identifiers[i].candidates.append(
                                    Candidate(text=noun_phrase_, included_sentence=included_sentence))

    def compute_candidate_statistics(self):
        """compute the following property of the candidate.
        word_count_to_variable: number of words between the candidate and the variable.
        if more than 1 candidate exists, the smallest count is applied.
        candidate_count: number of candidate appeared in the text.
        score_match_character: +1 when the initial character of the candidate matches
        with that of the identifier.
        """
        for i, identifier_ in enumerate(self.identifiers):
            for j, candidate_ in enumerate(identifier_.candidates):
                candidate_count_in_s = \
                    candidate_.included_sentence.replaced.count('CANDIDATE')
                self.identifiers[i].candidates[j].candidate_count_in_sentence = candidate_count_in_s

                score_match_character = 0
                initial_char_in_candidate = set(
                    [term[0] for term in candidate_.text.split()])
                for char_identifier in identifier_.mi_list:
                    if char_identifier[0] in initial_char_in_candidate:
                        score_match_character += 1
                score_match_character /= len(identifier_.mi_list)
                self.identifiers[i].candidates[j].score_match_character = score_match_character

                math_txt = f'MATH{i:04d}'
                sentence_list = candidate_.included_sentence.replaced.split()
                sentence_list = [s_.rstrip(',. :;') for s_ in sentence_list]
                math_txt_index = [i for i, term in enumerate(
                    sentence_list) if term == math_txt]
                candidate_index = [i for i, term in enumerate(
                    sentence_list) if term == 'CANDIDATE']
                word_count_btwn_var_cand = len(sentence_list)
                for math_txt_index_ in math_txt_index:
                    for candidate_index_ in candidate_index:
                        word_count_btwn_var_cand = \
                            min(word_count_btwn_var_cand,
                                abs(math_txt_index_ - candidate_index_) - 1)
                self.identifiers[i].candidates[j].word_count_btwn_var_cand = word_count_btwn_var_cand

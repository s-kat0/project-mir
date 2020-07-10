import lxml.html
import re
from stanza.server import CoreNLPClient
# from stanza.server import CoreNLPClient


class XMLDocument:
    def __init__(self, path=''):
        self.path = path
        self.title = ''
        self.namespace = ''
        self.document_id = 0
        self.text = ''
        self.body = ''
        # Holds all formulas found within the document.
        # The key of the HashMap is the replacement string in the document and
        # the value contains the TeX String
        self.formulae = []  # [{'hash': foo1, 'src':foo2}, ...]
        # Stores all unique identifiers found in this document
        self.identifiers = []
        self.sentences = []
        self.tagged_sentence_list = []
        self.description_candidate = []
        self.candidate_noun_phrases_list = []

    def processor(self):
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
            # remove annotation-xml tag and anntation tag
            body = annotation_xml_regexp.sub('', body)
            body = annotation_regexp.sub('', body)
            self.body = body
        print("process document")

    def extract_identifiers(self):
        tree = lxml.html.parse(self.path)
        html = tree.getroot()
        print('Number of math components is {}'.format(
            len(html.cssselect('math'))))
        reg_string_list = []
        identifiers = []

        def is_identifier(math_component):
            is_mi = (math_component.tag == 'mi')
            is_math_component_len_1 = (len(math_component.text_content()) == 1)
            is_italic = (math_component.get('mathvariant') == 'italic')
            return is_mi and (is_math_component_len_1 or is_italic)

        # TODO: this version ignores mover and munder.
        for html_math in html.cssselect('math'):
            # variable with subscript and superscript
            for html_math_msubsup in html_math.cssselect('msubsup'):
                html_math_msubsup_component = [
                    x for x in html_math_msubsup.iterchildren()]
                math_txt = [x.text_content()
                            for x in html_math_msubsup_component]
                math_txt = math_txt[0] + '_' + math_txt[1] + '^' + math_txt[2]
                if is_identifier(html_math_msubsup) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_msubsup.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_msubsup, encoding='unicode')
                if is_identifier(html_math_msubsup):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

            # variable with subscript
            for html_math_msub in html_math.cssselect('msub'):
                html_math_msub_component = [
                    x for x in html_math_msub.iterchildren()]
                math_txt = '_'.join([x.text_content()
                                     for x in html_math_msub_component])
                if is_identifier(
                        html_math_msub_component[0]) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_msub.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_msub, encoding='unicode')
                if is_identifier(html_math_msub_component[0]):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

            # variable with superscript
            for html_math_msup in html_math.cssselect('msup'):
                html_math_msup_component = [
                    x for x in html_math_msup.iterchildren()]
                math_txt = '^'.join([x.text_content()
                                     for x in html_math_msup_component])
                if is_identifier(
                        html_math_msup_component[0]) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_msup.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_msup, encoding='unicode')
                if is_identifier(html_math_msup_component[0]):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

            # variable with overscript
            for html_math_mover in html_math.cssselect('mover'):
                html_math_mover_component = [
                    x for x in html_math_mover.iterchildren()]
                math_txt = [x.text_content()
                            for x in html_math_mover_component]
                math_txt = r'\overset{' + \
                    math_txt[1] + '}{' + math_txt[0] + '}'
                if is_identifier(
                        html_math_mover_component[0]) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_mover.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_mover, encoding='unicode')
                if is_identifier(html_math_mover_component[0]):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

            # variable with underscript
            for html_math_munder in html_math.cssselect('munder'):
                html_math_munder_component = [
                    x for x in html_math_munder.iterchildren()]
                math_txt = [x.text_content()
                            for x in html_math_munder_component]
                math_txt = r'\underset{' + \
                    math_txt[1] + '}{' + math_txt[0] + '}'
                if is_identifier(
                        html_math_munder_component[0]) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_munder.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_munder, encoding='unicode')
                if is_identifier(html_math_munder_component[0]):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

            # variable with overscript and underscript
            for html_math_munderover in html_math.cssselect('munderover'):
                html_math_munderover_component = [
                    x for x in html_math_munderover.iterchildren()]
                math_txt = [x.text_content()
                            for x in html_math_munderover_component]
                math_txt = r'\overset{' + math_txt[2] + '}{' + \
                    r'\underset{' + math_txt[1] + '}{' + math_txt[0] + '}}'
                if is_identifier(
                        html_math_munderover_component[0]) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_munderover.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_munderover, encoding='unicode')
                if is_identifier(html_math_munderover_component[0]):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

            # variable without subscript and superscript
            for html_math_mi in html_math.cssselect('mi'):
                math_txt = html_math_mi.text_content()
                if is_identifier(html_math_mi) and (
                        math_txt not in identifiers):
                    identifiers.append(math_txt)
                html_math_mi.drop_tree()
                reg_string = lxml.html.tostring(
                    html_math_mi, encoding='unicode')
                if is_identifier(html_math_mi):
                    reg_string_list.append(
                        (math_txt, reg_string, 'MATH{:04d}'.format(
                            identifiers.index(math_txt))))
                else:
                    reg_string_list.append((math_txt, reg_string, math_txt))

        reg_string_list = list(set(reg_string_list))
        reg_string_list = sorted(
            reg_string_list,
            key=lambda x: x[0],
            reverse=True)
        for reg_string in reg_string_list:
            self.body = self.body.replace(reg_string[1], reg_string[2])
        self.identifiers = identifiers
        self.text = lxml.html.fromstring(self.body).text_content()

    def extract_sentences(self):
        # this extract sentences which contain identifier from text
        sentences = [[]] * len(self.identifiers)
        for i, identifier in enumerate(self.identifiers):
            sentences[i] = re.findall(
                r'.*?' + 'MATH{:04d}'.format(i) + r'.*?\.', self.text)
        self.sentences = sentences

    def POS_tagging(self):
        tagged_sentence_list = [[]] * len(self.identifiers)
        with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos'], timeout=600000, memory='16G') as client:
            for i, sentence in enumerate(self.sentences):
                if sentence:
                    tagged_sentence_list_ = []
                    for text in sentence:
                        # submit the request to the server
                        ann = client.annotate(text)
                        sentence_ = ann.sentence[0]
                        word_pos = [(token.word, token.pos)
                                    for token in sentence_.token]
                        tagged_sentence_list_.append(word_pos)
                    tagged_sentence_list[i] = tagged_sentence_list_

        self.tagged_sentence_list = tagged_sentence_list

    def extract_noun_phrases(self):
        candidate_noun_phrases_list = [[]] * len(self.identifiers)
        # TODO: Delete unnecessary annotators
        pattern = 'NP'
        with CoreNLPClient(
                annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref'],
                timeout=600000, memory='16G') as client:
            for i, sentence in enumerate(self.sentences):
                if sentence:
                    candidate_noun_phrases_list_ = []
                    for text in sentence:
                        matches = client.tregex(text, pattern)
                        matches = matches['sentences'][0]
                        candidates = [matches[match]['match'].rstrip()
                                      for match in matches]
                        candidate_noun_phrases_list_.append(candidates)
                    candidate_noun_phrases_list[i] = candidate_noun_phrases_list_
        self.candidate_noun_phrases_list = candidate_noun_phrases_list

    def pattern_based_extract_description(self):
        count_identifiers = len(self.identifiers)
        math_id = range(count_identifiers)
        description_candidate = [[]] * count_identifiers
        reg_description = re.compile(r'(NN[PS]{0,2}|NP)')
        for math_id_ in math_id:
            tagged_sentence_list_i = self.tagged_sentence_list[math_id_]
            identifier = 'MATH{:04d}'.format(
                math_id_)  # self.identifiers[math_id_]
            if not tagged_sentence_list_i:
                continue

            description_candidate_ = []
            for tagged_sentence_list_i_ in tagged_sentence_list_i:
                indexes_target = [
                    n for n, v in enumerate(tagged_sentence_list_i_) if v == (
                        identifier, 'NN')]
                for index_target in indexes_target:
                    # 1. <description> <identifier>
                    description = []
                    for i in range(index_target - 1, -1, -1):
                        (description_, pos_) = tagged_sentence_list_i_[i]
                        if ('MATH' not in description_) and reg_description.fullmatch(
                                pos_):
                            description.append(description_)
                        else:
                            break
                    if description:
                        description_candidate_.append(
                            (' '.join(description), ' '.join(description) + ' ' + identifier))

                    # 2. <identifier> is <description>
                    # 3. <identifier> is the <description>
                    description = []
                    if tagged_sentence_list_i_[index_target + 1][0] == 'is':
                        mid_pattern = ' is '
                        if tagged_sentence_list_i_[
                                index_target + 2][0] == 'the':
                            index_start = index_target + 3
                            mid_pattern += 'the '
                        else:
                            index_start = index_target + 2
                        for i in range(
                                index_start, len(tagged_sentence_list_i_)):
                            (description_, pos_) = tagged_sentence_list_i_[i]
                            if ('MATH' not in description_) and reg_description.fullmatch(
                                    pos_):
                                description.append(description_)
                            else:
                                break
                        if description:
                            description_candidate_.append(
                                (' '.join(description), identifier + mid_pattern + ' '.join(description)))

                    # 4. let <identifier> be the <description>
                    if (
                        tagged_sentence_list_i_[
                            index_target -
                            1][0] == 'let') and (
                        tagged_sentence_list_i_[
                            index_target +
                            1][0] == 'be') and (
                        tagged_sentence_list_i_[
                            index_target +
                            2][0] == 'the'):
                        for i in range(
                                index_target + 3,
                                len(tagged_sentence_list_i_)):
                            (description_, pos_) = tagged_sentence_list_i_[i]
                            if ('MATH' not in description_) and reg_description.fullmatch(
                                    pos_):
                                description.append(description_)
                            else:
                                break
                        if description:
                            description_candidate_.append(
                                (' '.join(description), 'let ' + identifier + ' be the ' + ' '.join(description)))

                    # 5. <description> is|are denoted by <identifier>
                    if (
                        tagged_sentence_list_i_[
                            index_target -
                            1][0] == 'by') and (
                        tagged_sentence_list_i_[
                            index_target -
                            2][0] == 'denoted') and (
                        tagged_sentence_list_i_[
                            index_target -
                            3][0] == (
                            'is' or 'are')):
                        for i in range(index_target - 4, -1, -1):
                            (description_, pos_) = tagged_sentence_list_i_[i]
                            if ('MATH' not in description_) and reg_description.fullmatch(
                                    pos_):
                                description.append(description_)
                            else:
                                break
                        if description:
                            description_candidate_.append((' '.join(description), ' '.join(
                                description) + ' is|are denoted by ' + identifier))
                            description = []

                    # 6. <identifier> denotes */DT <description>
                    if (
                        tagged_sentence_list_i_[
                            index_target +
                            1][0] == 'denotes') and (
                        tagged_sentence_list_i_[
                            index_target +
                            2][1] == 'DT'):
                        for i in range(
                                index_target + 3,
                                len(tagged_sentence_list_i_)):
                            (description_, pos_) = tagged_sentence_list_i_[i]
                            if ('MATH' not in description_) and reg_description.fullmatch(
                                    pos_):
                                description.append(description_)
                            else:
                                break
                        if description:
                            description_candidate_.append(
                                (' '.join(description), identifier + ' denotes */DT ' + ' '.join(description)))

            description_candidate[math_id_] = description_candidate_
        self.description_candidate = description_candidate

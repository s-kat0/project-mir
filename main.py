# %%

import lxml.html
import time
import re
from tqdm import tqdm
from stanfordnlp.server import CoreNLPClient
import pickle
from projectmir.xmldocument import XMLDocument
from projectmir.functions import find_identifier_definition

from pathlib import Path

# %%

# p_path =
# './data/resources/dataset-arXMLiv-08-2019/process-control_physical-model/'
p_path = './data/test_latexml/'
p = Path(p_path)
x = list(p.glob('*.html'))[0:1]
document_IDs = [x_.name[:-5] for x_ in x]

doc = [[]] * len(document_IDs)
for i, document_ID in tqdm(enumerate(document_IDs)):
    document_path = p_path + document_ID + '.html'
    doc_ = find_identifier_definition(document_path)
    doc[i] = doc_


tree = lxml.html.parse(x.path)
html = tree.getroot()
print('Number of math components is {}'.format(
    len(html.cssselect('math'))))
reg_string_list = []


def is_identifier(math_component):
    is_mi = (math_component.tag == 'mi')
    is_math_component_len_1 = (len(math_component.text_content()) == 1)
    is_italic = (math_component.get('mathvariant') == 'italic')
    return is_mi and (is_math_component_len_1 or is_italic)


# TODO: variable with subscript is not changed,
# because before change, the variable without subscript is changed.
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
            reg_string_list.append(
                (math_txt, reg_string, math_txt))

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
            reg_string_list.append(
                (math_txt,
                 reg_string,
                 math_txt)
            )

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
                (math_txt,
                 reg_string,
                 'MATH{:04d}'.format(identifiers.index(math_txt))
                 )
            )

        else:
            reg_string_list.append(
                (math_txt,
                 reg_string,
                 math_txt)
            )

x.identifiers = identifiers
x.text = lxml.html.fromstring(x.body).text_content()

import copy
import lxml.html
import warnings


x_text = """
<p class="ltx_p">Consequently, in the subsequent development, we assume that <math id="S1.SS1.p2.m3" class="ltx_Math" alttext="U_{\rm int}=H" display="inline"><mrow><msub><mi>U</mi><mi>int</mi></msub><mo>=</mo><mi>H</mi></mrow></math> and <math id="S1.SS1.p2.m4" class="ltx_Math" alttext=r"\hat{U}_{\rm int}=\hat{H}" display="inline"><mrow><msub><mover accent="true"><mi>U</mi><mo stretchy="false">^</mo></mover><mi>int</mi></msub><mo>=</mo><mover accent="true"><mi>H</mi><mo stretchy="false">^</mo></mover></mrow></math> where the caret (^) means per unit mass.</p>
"""
# <p class="ltx_p">Consequently, in the subsequent development, we assume that <math id="S1.SS1.p2.m3" class="ltx_Math" alttext="U_{\rm int}=H" display="inline"><mrow><msub><mi>U</mi><mi>int</mi></msub><mo>=</mo><mi>H</mi></mrow></math> and <math id="S1.SS1.p2.m4" class="ltx_Math" alttext=r"\hat{U}_{\rm int}=\hat{H}" display="inline"><mrow><msub><mover accent="true"><mi>U</mi><mo stretchy="false">^</mo></mover><mi>int</mi></msub><mo>=</mo><mover accent="true"><mi>H</mi><mo stretchy="false">^</mo></mover></mrow></math> where the caret (^) means per unit mass.</p>


def tree_to_str(ml_tree):
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
                math_txt = r'\overset{' + ml_list[2] + '}{' + r'\underset{' + \
                           ml_list[1] + '}{' + ml_list[0] + '}}'
            elif ml_tree.tag == 'mover':
                math_txt = r'\overset{' + ml_list[1] + '}{' + ml_list[0] + '}'
            elif ml_tree.tag == 'munder':
                math_txt = r'\underset{' + ml_list[1] + '}{' + ml_list[0] + '}'
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


i, r = [], []
x_tree = lxml.html.fromstring(x_text)
# print(x_tree.text_content())
mltags = ['msubsup', 'msub', 'msup', 'munderover', 'munder', 'mover', 'mi']
for x_math in copy.deepcopy(x_tree).cssselect('math'):
    for mltag in mltags:
        for x in copy.deepcopy(x_math).cssselect(mltag):
            print(tree_to_str(x))
    # print(extract_ml_component(x_math, 'mover', i, r))
# print(x_tree.text_content())

# for html_math_mltag in html_cssselect_math.cssselect(mltag):
#     if mltag == 'mi':
#         math_txt = html_math_mltag.text_content()
#         identifier_candidate = html_math_mltag
#     else:
#         html_math_mltag_component = [
#             x for x in html_math_mltag.iterchildren()]
#         identifier_candidate = html_math_mltag_component[0]
#         math_txt = [x.text_content()
#                     for x in html_math_mltag_component]
#         if mltag == 'msubsup':
#             math_txt = math_txt[0] + '_' + \
#                 math_txt[1] + '^' + math_txt[2]
#         elif mltag == 'msub':
#             math_txt = math_txt[0] + '_' + math_txt[1]
#         elif mltag == 'msup':
#             math_txt = math_txt[0] + '^' + math_txt[1]
#         elif mltag == 'mover':
#             math_txt = r'\overset{' + \
#                 math_txt[1] + '}{' + math_txt[0] + '}'
#         elif mltag == 'munder':
#             math_txt = r'\underset{' + \
#                 math_txt[1] + '}{' + math_txt[0] + '}'
#         elif mltag == 'munderover':
#             math_txt = r'\overset{' + math_txt[2] + '}{' + \
#                 r'\underset{' + math_txt[1] + '}{' + math_txt[0] + '}}'

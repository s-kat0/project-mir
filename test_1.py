import copy
import lxml.html
import warnings


x_text = """
<p class="ltx_p">Consequently, in the subsequent development, we assume that <math id="S1.SS1.p2.m3" class="ltx_Math" alttext="U_{\rm int}=H" display="inline"><mrow><msub><mi>U</mi><mi>int</mi></msub><mo>=</mo><mi>H</mi></mrow></math> and <math id="S1.SS1.p2.m4" class="ltx_Math" alttext=r"\hat{U}_{\rm int}=\hat{H}" display="inline"><mrow><msub><mover accent="true"><mi>U</mi><mo stretchy="false">^</mo></mover><mi>int</mi></msub><mo>=</mo><mover accent="true"><mi>H</mi><mo stretchy="false">^</mo></mover></mrow></math> where the caret (^) means per unit mass.</p>
"""
#<p class="ltx_p">Consequently, in the subsequent development, we assume that <math id="S1.SS1.p2.m3" class="ltx_Math" alttext="U_{\rm int}=H" display="inline"><mrow><msub><mi>U</mi><mi>int</mi></msub><mo>=</mo><mi>H</mi></mrow></math> and <math id="S1.SS1.p2.m4" class="ltx_Math" alttext=r"\hat{U}_{\rm int}=\hat{H}" display="inline"><mrow><msub><mover accent="true"><mi>U</mi><mo stretchy="false">^</mo></mover><mi>int</mi></msub><mo>=</mo><mover accent="true"><mi>H</mi><mo stretchy="false">^</mo></mover></mrow></math> where the caret (^) means per unit mass.</p>


def tree_to_str(ml_tree):
    ml_str = ''
    ml_tree_ = copy.deepcopy(ml_tree)
    if isinstance(ml_tree_, lxml.html.HtmlElement):
        if ml_tree_.tag in ['mi', 'mo', 'mn']:
            ml_str += ml_tree_.text_content()

        else:
            for ml_children in ml_tree_:
                ml_children_ = [x for x in ml_children]
                if ml_children.tag in ['mi', 'mo', 'mn']:
                    math_txt = ml_children.text_content()

                elif ml_children.tag == 'mrow':
                    math_txt = tree_to_str(ml_children)

                elif ml_children.tag == 'msubsup':
                    math_txt = tree_to_str(ml_children_[0]) + '_' + tree_to_str(ml_children_[1]) \
                               + '^' + tree_to_str(ml_children_[2])

                elif ml_children.tag == 'msub':
                    math_txt = tree_to_str(ml_children_[0]) + '_' + tree_to_str(ml_children_[1])

                elif ml_children.tag == 'msup':
                    math_txt = tree_to_str(ml_children_[0]) + '^' + tree_to_str(ml_children_[1])

                elif ml_children.tag == 'munderover':
                    math_txt = r'\overset{' + tree_to_str(ml_children_[2]) + '}{' + r'\underset{' + \
                               tree_to_str(ml_children_[1]) + '}{' + tree_to_str(ml_children_[0]) + '}}'

                elif ml_children.tag == 'mover':
                    math_txt = r'\overset{' + \
                               tree_to_str(ml_children_[1]) + '}{' + tree_to_str(ml_children_[0]) + '}'

                elif ml_children.tag == 'munder':
                    math_txt = r'\underset{' + \
                               tree_to_str(ml_children_[1]) + '}{' + tree_to_str(ml_children_[0]) + '}'

                else:
                    math_txt = ''
                    warnings.warn('unexpected tag')
                    print(f'{ml_tree}')

                ml_str += math_txt

    elif isinstance(ml_tree_, list):
        tree_to_str(ml_tree)

    else:
        warnings.warn('unexpected tag')
        print(f'{ml_tree}')

    return ml_str


i, r = [], []
x_tree = lxml.html.fromstring(x_text)
# print(x_tree.text_content())
for x_math in copy.deepcopy(x_tree).cssselect('math'):
    print(tree_to_str(x_math))
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

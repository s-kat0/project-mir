from dataclasses import dataclass, field
import math
import re
from typing import List, Dict

from projectmir.xmldoc_child import Identifier


@dataclass
class Definition:
    definition: str = ''
    score: float = 0
    params: Dict[str, int] = field(default_factory=dict)


def kato_ranking_candidates(identifier: Identifier, params=None):
    """rank candidates based on the method proposed by Kato, S. and Kano, M..
    Candidates are the noun phrases in the sentence where the identifier was appeared first.
    Args:
        identifier (Identifier)
        params (dict)
    Returns:
        Definition_list (List[Definition])
    """
    if params is None:
        params = {'sigma_d': math.sqrt(12 / math.log(2)),
                  'sigma_s': 2 / math.sqrt(math.log(2)),
                  'alpha': 1,
                  'beta': 1,
                  'gamma': 0.1,
                  'eta': 1}
    ranked_definition_list = []

    for candidate_ in identifier.candidates:
        n_sentence = len(identifier.sentences)
        delta = candidate_.word_count_btwn_var_cand + 1  # delta=1 is minimum.
        tf_candidate = candidate_.candidate_count_in_sentence / \
            len(candidate_.included_sentence.split())
        score_match_initial_char = candidate_.score_match_character
        r_sigma_d = math.exp(- 1 / 2 * (delta ** 2 - 1) /
                             params['sigma_d'] ** 2)
        r_sigma_s = math.exp(- 1 / 2 * (n_sentence ** 2 -
                                        1) / params['sigma_s'] ** 2)

        score = (params['alpha'] * r_sigma_d
                 + params['beta'] * r_sigma_s
                 + params['gamma'] * tf_candidate
                 + params['eta'] * score_match_initial_char)
        score /= (params['alpha'] + params['beta'] +
                  params['gamma'] + params['eta'])

        ranked_definition_list.append(
            Definition(
                definition=candidate_.text,
                score=score,
                params=params))

    ranked_definition_list = sorted(
        ranked_definition_list,
        key=lambda x: x.score,
        reverse=True)

    return ranked_definition_list


def pagel_ranking_candidates(identifier: Identifier, params=None):
    """rank candidates based on the method proposed by Pagel, R. and Schubotz, M..
    Candidates are the noun phrases in the sentence where the identifier was appeared first.
    Args:
        identifier (Identifier)
    Returns:
        Definition_list (List[Definition])
    """
    if params is None:
        params = {'sigma_d': math.sqrt(12 / math.log(2)),
                  'sigma_s': 2 / math.sqrt(math.log(2)),
                  'alpha': 1,
                  'beta': 1,
                  'gamma': 0.1}
    ranked_definition_list = []
    for candidate_ in identifier.candidates:
        n_sentence = len(identifier.sentences)
        delta = candidate_.word_count_btwn_var_cand
        tf_candidate = candidate_.candidate_count_in_sentence
        r_sigma_d = math.exp(- 1 / 2 * (delta ** 2 - 1) /
                             params['sigma_d'] ** 2)
        r_sigma_s = math.exp(- 1 / 2 * (n_sentence ** 2 -
                                        1) / params['sigma_s'] ** 2)

        score = (
            params['alpha'] *
            r_sigma_d +
            params['beta'] *
            r_sigma_s +
            params['gamma'] *
            tf_candidate)
        score /= (params['alpha'] + params['beta'] + params['gamma'])

        ranked_definition_list.append(
            Definition(
                definition=candidate_.text,
                score=score,
                params=params))

    ranked_definition_list = sorted(
        ranked_definition_list,
        key=lambda x: x.score,
        reverse=True)

    return ranked_definition_list


def pattern_based_extract_description(identifier: Identifier):
    """extract description based on the following pattern.

    Although original patterns are proposed by Pagel [1],
    their <description> does not include a determiner (DT).
    To simplify the pattern, we assume that <description>
    includes determiner.
    <description> can be either pattern: include determiner
    or not include determiner (proper noun).

    # 1. <description> <identifier>
    # 2. <identifier> is <description>
    # 3. <identifier> is the <description>
    # 4. let <identifier> be <description>
    # 5. <description> is|are denoted by <identifier>
    # 6. <identifier> denotes <description>

    [1]: Pagel, R. and Schubotz, M.: Mathematical Language Processing Project,
    in Joint Proceedings of the MathUI, OpenMath and ThEdu Workshops and Work
    in Progress track at CICM, No. 1186, Aachen (2014)

    ----------------------
    usage:
    # extract definitions using pattern based method.
    pattern_based_definition_list = []
    for i, identifier in enumerate(doc.identifiers):
        definition = pattern_based_extract_description(identifier)
        pattern_based_definition_list.append(definition)
    """
    reg_description = re.compile(r'(NN[PS]{0,2}|NP)')
    extracted_description_list = []
    math_id = identifier.id
    identifier_text = f'MATH{math_id:04d}'
    for sentence in identifier.sentences[:1]:
        sentence_tagged = sentence.tagged
        description_candidate_ = []
        indexes_target = [
            n for n, v in enumerate(sentence_tagged)
            if v == (identifier_text, 'NN')]
        for index_target in indexes_target:
            # 1. <description> <identifier>
            description = []
            if index_target >= 1:
                for i in range(index_target - 1, -1, -1):
                    (description_, pos_) = sentence_tagged[i]
                    if ('MATH' not in description_) \
                            and reg_description.fullmatch(pos_):
                        description.append(description_)
                    else:
                        break
                if description:
                    description = description[::-1]
                    extracted_description_list.append(' '.join(description))

            # 2. <identifier> is <description>
            # 3. <identifier> is the <description>
            description = []
            if index_target < len(sentence_tagged) - 1:
                if sentence_tagged[index_target + 1][0] == 'is':
                    mid_pattern = ' is '
                    index_start = index_target + 2
                    if index_target < len(sentence_tagged) - 3:
                        if sentence_tagged[index_target + 2][0] == 'the':
                            index_start = index_target + 3
                            mid_pattern += 'the '
                    for i in range(index_start, len(sentence_tagged)):
                        (description_, pos_) = sentence_tagged[i]
                        if ('MATH' not in description_) and reg_description.fullmatch(
                                pos_):
                            description.append(description_)
                        else:
                            break
                    if description:
                        extracted_description_list.append(
                            ' '.join(description))

            # 4. let <identifier> be the <description>
            description = []
            if 1 <= index_target < len(sentence_tagged) - 3:
                if (sentence_tagged[index_target - 1][0] == 'let') and \
                        (sentence_tagged[index_target + 1][0] == 'be') and \
                        (sentence_tagged[index_target + 2][0] == 'the'):
                    for i in range(index_target + 3, len(sentence_tagged)):
                        (description_, pos_) = sentence_tagged[i]
                        if ('MATH' not in description_) and reg_description.fullmatch(
                                pos_):
                            description.append(description_)
                        else:
                            break
                    if description:
                        extracted_description_list.append(
                            ' '.join(description))

            # 5. <description> is|are denoted by <identifier>
            description = []
            if index_target >= 4:
                if (sentence_tagged[index_target - 1][0] == 'by') and \
                        (sentence_tagged[index_target - 2][0] == 'denoted') and \
                        (sentence_tagged[index_target - 3][0] == ('is' or 'are')):
                    for i in range(index_target - 4, -1, -1):
                        (description_, pos_) = sentence_tagged[i]
                        if ('MATH' not in description_) and reg_description.fullmatch(
                                pos_):
                            description.append(description_)
                        else:
                            break
                    if description:
                        description = description[::-1]
                        extracted_description_list.append(
                            ' '.join(description))

            # 6. <identifier> denotes */DT <description>
            description = []
            if index_target < len(sentence_tagged) - 3:
                if (sentence_tagged[index_target + 1][0] == 'denotes') and \
                        (sentence_tagged[index_target + 2][1] == 'DT'):
                    for i in range(index_target + 3, len(sentence_tagged)):
                        (description_, pos_) = sentence_tagged[i]
                        if ('MATH' not in description_) and \
                                reg_description.fullmatch(pos_):
                            description.append(description_)
                        else:
                            break
                    if description:
                        extracted_description_list.append(
                            ' '.join(description))
    if not extracted_description_list:
        extracted_description_list.append(None)

    return [Definition(definition=d) for d in extracted_description_list]


# sometimes noun phrases are not extracted accurately.
# Thus, the accuracy of the following method is not so high.
def pattern_based_extract_description_using_noun_phrases(
        identifier: Identifier):
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

    -----
    usage:
    pattern_based_definition_list = []
    for i, identifier in enumerate(doc.identifiers):
        definition = pattern_based_extract_description_using_noun_phrases(identifier)
        pattern_based_definition_list.append(definition)
    """
    extracted_description_list = []
    math_id_ = identifier.id
    identifier_text = f'MATH{math_id_:04d}'
    candidates_list = identifier.candidates
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
            re.compile(
                description_candidate +
                ' ' +
                identifier_text),
            re.compile(
                identifier_text +
                ' is ' +
                description_candidate),
            re.compile(
                'let ' +
                identifier_text +
                ' be ' +
                description_candidate),
            re.compile(
                description_candidate +
                r' [is|are] denoted by ' +
                identifier_text),
            re.compile(
                identifier_text +
                ' denotes ' +
                description_candidate)]

        for pattern_ in pattern_list:
            if pattern_.search(sentence):
                extracted_description_list.append(description_candidate)
    return [Definition(definition=d) for d in extracted_description_list]

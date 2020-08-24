from dataclasses import dataclass, field
from typing import List


@dataclass
class Candidate:
    text: str
    score_pagel: float = 0.0
    score_propsed: float = 0.0
    included_sentence: str = ''
    word_count_btwn_var_cand: int = 0
    candidate_count_in_sentence: int = 0
    score_match_character: int = 0


@dataclass
class Sentence:
    original: str = ''
    tagged: str = ''


@dataclass
class Identifier:
    text_tex: str = ''
    mi_list: List[str] = field(default_factory=list)
    id: int = 0
    sentences: List[Sentence] = field(default_factory=list)
    candidates: List[Candidate] = field(default_factory=list)


@dataclass
class Formulae:
    text_replaced: str = ''
    text_tex: str=''


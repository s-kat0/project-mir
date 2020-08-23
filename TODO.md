21st, Aug, 2020
TODO:classを使いやすいように設計しなおす．


TODO:class identifierの実装
identifierは，candidatesとsentencesを子要素に持つ．
各要素を，extract_candidatesとextract_sentencesとで抽出できるようにする．

TODO:class candidateの実装
candidateは，以下の要素を含む．
- score-pagel ('float') [0, 1]
- score_propsed ('float') [0, 1]
- included_sentence ('str')
- word_count_btwn_var_cand ('int')
- candidate_count_in_sentence ('int')
- score_match_character ('int')
  変数に用いられている文字と説明文の頭文字で，等しいものの数．


TODO:extract_sentencesの修正．
stanzaでsentence segmentation -> math要素を含む文を抽出．

TODO:extract_formulaeの実装
extract_sentences内，=が含まれている場合，数式とみなすこととする．

 

TODO:パターンマッチングに基づいたidentifier-definition extracitonの実装．
TODO:Wikipediaデータを用いたパターンマッチングの手法の評価．
TODO:評価指標の算出
TODO:統計的な手法の実装 (based on project-mir)
TODO:実データに対して適用
TODO:tests/test.pyをちゃんとしたテストにする．


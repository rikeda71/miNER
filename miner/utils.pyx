from typing import List, Dict


cpdef entity_indexes(sentences, seq_label_pairs, type_select: str,
                     check_known: bool, check_unknown: bool,
                     known_words: Dict[str, List[str]]):
    """
    return named entities indexes
    :param seqs: labels list [[labels0], [labels1], ... ]
    :param type_select: NER label type
    :return: chunks of NER label type, index of begin of named entity
             and index of end of named entity
             [(type, begin index, end index),
              (type, begin index, end index), ... ]
    """

    cdef:
        str top, type_, word
        str prev_top = 'O', prev_type = ''
        int focus_idx = 0
        entities = []

    for i, (label, words) in enumerate(seq_label_pairs):
        top = label[0]
        type_ = label.split('-')[-1]
        word = ''.join(sentences[focus_idx: i])

        if is_end_of_label(prev_top, top, prev_type, type_) \
                and type_select in [prev_type, '', 'ALL'] \
                and check_add_entity(word, type_select, check_known,
                                     check_unknown, known_words):
            entities.append((prev_type, focus_idx, i - 1))

        if is_begin_of_label(top, prev_type, type_):
            focus_idx = i
        prev_top = top
        prev_type = type_

    return list(entities)

cpdef is_end_of_label(str prev_top,  str now_top,
                    str prev_type, str now_type):
    """
    check if named entity label is end
    :param prev_top: previous scheme
    :param now_top: now scheme
    :param prev_type: previous label
    :param now_type: now label
    :return: end -> True, not end -> False
    """

    if prev_top in ['E', 'S', 'L', 'U']:
        return True
    elif prev_top == 'B' and now_top in ['B', 'O']:
        return True
    elif prev_top == 'I' and now_top in ['B', 'O', 'S', 'U']:
        return True
    elif prev_top != 'O' and prev_type != now_type:
        return True
    return False

cpdef is_begin_of_label(str now_top, str prev_type, str now_type):
    """
    check if named entity label is begin
    :param now_top: now scheme
    :param prev_type: previous label
    :param now_type: now label
    :return: begin -> True, not begin -> False
    """

    if now_top in ['B', 'S', 'U']:
        return True
    elif now_top != 'O' and prev_type and prev_type != now_type:
        return True
    return False

def check_add_entity(word: str, type_: str,
                     check_known: bool, check_unknown: bool,
                     known_words: Dict[str, List[str]]) -> bool:
    """
    adding entity check
    :param word: a named entity
    :param type_: NER label type
    :return: can add entities -> True, cannot add entities -> False
    """

    if check_known and check_unknown:
        return True
    elif check_known and word in known_words[type_]:
        return True
    elif check_unknown and word not in known_words[type_]:
        return True
    return False

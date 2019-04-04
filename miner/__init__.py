from typing import List, Dict, Tuple
from collections import defaultdict


class Miner:

    def __init__(self, answers: List[List[str]],
                 predicts: List[List[str]],
                 sentences: List[List[str]],
                 known_words: Dict[str, List[str]] = {}):
        """
        :param answers: answer labels list [[labels], [labels], ...]
        :param predicts: predicrt labels list [[labels], [labels], ...]
        :param sentences: morphs list [[morphs], [morphs], ...]
        :param known_words: known words of each label
                            {'label0': [word0, word1, ... ],
                            'label1': [word0, word1, ... ],
                            ... }
        """

        self.answers = answers
        self.predicts = predicts
        self.sentences = sentences
        self.types = tuple(
            set([type_.split('-')[-1]
                 for seq in self.answers
                 for type_ in seq if type_ != 'O'
                 ]))
        self.known_words = {type_: [] for type_ in self.types}\
            if known_words == {} else known_words
        self.check_known = True
        self.check_unknown = True

    def default_report(self, print_: bool = False)\
            -> Dict[str, Dict[str, float]]:
        """
        return report of named entity recognition
        :param print_: print flag.
                       if this flag equal 'True', print report of NER result.
        :return: reports of NER result
                 {'label0': {'precision': precision param,
                             'recall': recall param,
                             'f1_score': f-measure},
                  'label1': {'precision': precision param,
                             'recall': recall param,
                             'f1_score': f-measure}, ... }
        """

        self.check_known = True
        self.check_unknown = True

        report = {type_: defaultdict(float) for type_ in self.types}

        for type_ in self.types:
            report[type_]['precision'] = self.precision(type_)
            report[type_]['recall'] = self.recall(type_)
            report[type_]['f1_score'] = self.f1_score(type_)
            report[type_]['num'] = self.num_of_ner(type_)

        for type_ in self.types:
            report[type_] = dict(report[type_])

        if print_:
            self._print_report(report)

        return report

    def known_only_report(self, print_: bool = False)\
            -> Dict[str, Dict[str, float]]:
        """
        return report of known named entity recognition
        :param print_: print flag.
                       if this flag equal 'True', print report of NER result.
        :return: reports of NER result
                 {'label0': {'precision': precision param,
                             'recall': recall param,
                             'f1_score': f-measure},
                  'label1': {'precision': precision param,
                             'recall': recall param,
                             'f1_score': f-measure}, ... }
        """

        self.check_known = True
        self.check_unknown = False

        report = {type_: defaultdict(float) for type_ in self.types}

        for type_ in self.types:
            report[type_]['precision'] = self.precision(type_)
            report[type_]['recall'] = self.recall(type_)
            report[type_]['f1_score'] = self.f1_score(type_)
            report[type_]['num'] = self.num_of_ner(type_)

        for type_ in self.types:
            report[type_] = dict(report[type_])

        if print_:
            self._print_report(report)

        return report

    def unknown_only_report(self, print_: bool = False)\
            -> Dict[str, Dict[str, float]]:
        """
        return report of unknown named entity recognition
        :param print_: print flag.
                       if this flag equal 'True', print report of NER result.
        :return: reports of NER result
                 {'label0': {'precision': precision param,
                             'recall': recall param,
                             'f1_score': f-measure},
                  'label1': {'precision': precision param,
                             'recall': recall param,
                             'f1_score': f-measure}, ... }
        """

        self.check_known = False
        self.check_unknown = True

        report = {type_: defaultdict(float) for type_ in self.types}

        for type_ in self.types:
            report[type_]['precision'] = self.precision(type_)
            report[type_]['recall'] = self.recall(type_)
            report[type_]['f1_score'] = self.f1_score(type_)
            report[type_]['num'] = self.num_of_ner(type_)

        for type_ in self.types:
            report[type_] = dict(report[type_])

        if print_:
            self._print_report(report)

        return report

    def return_miss_labelings(self) -> List[Dict[str, List[str]]]:
        """
        get miss labeling sentences, predict labels, and answer labels
        :return: miss labeling sentences, predict labels, and answer labels
                 [{'sentence': ['', '', ..., ''],
                  'predict': ['', '', ..., ''],
                  'answer': ['', '', ..., '']},
                  {'sentence': ...
                 ]
        """

        return [{'sentence': s, 'predict': p, 'answer': a}
                for p, a, s in zip(self.predicts, self.answers, self.sentences)
                if p != a]

    def return_answer_named_entities(self) -> Dict[str, Dict[str, List[str]]]:
        return self._return_named_entities(self.answers)

    def return_predict_named_entities(self) -> Dict[str, Dict[str, List[str]]]:
        return self._return_named_entities(self.predicts)

    def precision(self, type_select: str) -> float:
        """
        return precision score
        :param type_select: NER label type
        :return: precision score
        """

        ans_entities = set(self._entity_indexes(self.answers, type_select))
        pred_entities = set(self._entity_indexes(self.predicts, type_select))

        correct_num = len(ans_entities & pred_entities)
        pred_num = len(pred_entities)

        return correct_num / pred_num if pred_num > 0 else 0

    def recall(self, type_select: str) -> float:
        """
        return recall score
        :param type_select: NER label type
        :return: recall score
        """

        ans_entities = set(self._entity_indexes(self.answers, type_select))
        pred_entities = set(self._entity_indexes(self.predicts, type_select))

        correct_num = len(ans_entities & pred_entities)
        ans_num = len(ans_entities)

        return correct_num / ans_num if ans_num > 0 else 0

    def f1_score(self, type_select: str) -> float:
        """
        return f-measure score
        :param type_select: NER label type
        :return: f-measure score
        """

        p = self.precision(type_select)
        r = self.recall(type_select)
        return 2 * p * r / (p + r) if p + r > 0 else 0

    def num_of_ner(self, type_select: str) -> int:
        return len(self._entity_indexes(self.answers, type_select))

    def _entity_indexes(self, seqs: List[List[str]], type_select: str)\
            -> List[Tuple[str, int, int]]:
        """
        return named entities indexes
        :param seqs: labels list [[labels0], [labels1], ... ]
        :param type_select: NER label type
        :return: chunks of NER label type, index of begin of named entity
                 and index of end of named entity
                 [(type, begin index, end index),
                  (type, begin index, end index), ... ]
        """

        entities = []
        sequences = [label for seq in seqs for label in seq + ['O']]
        sentences = [word for sentence in self.sentences
                     for word in sentence + ['']]
        prev_top = 'O'
        prev_type = ''
        focus_idx = 0

        seq_label_pairs = zip(sequences + ['O'], sentences + [''])
        for i, (label, words) in enumerate(seq_label_pairs):
            top = label[0]
            type_ = label.split('-')[-1]
            word = ''.join(sentences[focus_idx: i])

            if self._is_end_of_label(prev_top, top, prev_type, type_) \
                and type_select in [prev_type, ''] \
                    and self._check_add_entity(word, type_select):
                entities.append((prev_type, focus_idx, i - 1))

            if self._is_begin_of_label(top, prev_type, type_):
                focus_idx = i
            prev_top = top
            prev_type = type_

        return entities

    def _return_named_entities(self, labels: List[List[str]])\
            -> Dict[str, Dict[str, List[str]]]:
        """
        return named entities
        :param labels: labels list (self.answers or self.predicts)
        :return  {'known': {type1: ['named entity', 'named entity', ... ],
                            type2: [...] },
                  'unknown': {type1: ['named entity', 'named entity', ... ],
                              type2: [...] }}
        """

        knownentities = {type_: [] for type_ in self.types}
        unknownentities = {type_: [] for type_ in self.types}
        sequences = [seq for label in labels for seq in label + ['O']]
        sentences = [word for sentence in self.sentences
                     for word in sentence + ['']]
        prev_top = 'O'
        prev_type = ''
        focus_idx = 0

        seq_label_pairs = zip(sequences + ['O'], sentences + [''])
        for i, (label, words) in enumerate(seq_label_pairs):
            top = label[0]
            type_ = label.split('-')[-1]

            if self._is_end_of_label(prev_top, top, prev_type, type_):
                word = ''.join(sentences[focus_idx: i])
                if word in self.known_words[prev_type]:
                    knownentities[prev_type].append(word)
                else:
                    unknownentities[prev_type].append(word)

            if self._is_begin_of_label(top, prev_type, type_):
                focus_idx = i
            prev_top = top
            prev_type = type_

        for type_ in self.types:
            knownentities[type_] = list(set(knownentities[type_]))
            unknownentities[type_] = list(set(unknownentities[type_]))

        return {'known': knownentities, 'unknown': unknownentities}

    def _print_report(self, result: Dict[str, Dict[str, float]]):
        """
        print report of NER result
        :param result: reports of NER result
                       {'label0': {'precision': precision param,
                                   'recall': recall param,
                                    'f1_score': f-measure},
                        'label1': {'precision': precision param,
                                   'recall': recall param,
                                   'f1_score': f-measure}, ... }
        """

        print('\n\tprecision    recall    f1_score   num')
        for type_ in self.types:
            print(type_, end='\t')
            print('{0: .3f}'.format(result[type_]['precision']), end='       ')
            print('{0: .3f}'.format(result[type_]['recall']), end='    ')
            print('{0: .3f}'.format(result[type_]['f1_score']), end='     ')
            print('{0: d}'.format(int(result[type_]['num'])), end='\n')

    def _is_end_of_label(self, prev_top: str, now_top: str,
                         prev_type: str, now_type: str) -> bool:
        """
        check if named entity label is end
        :param prev_top:
        :param now_top:
        :param prev_type:
        :param now_type:
        :return: end -> True, not end -> False
        """

        if prev_top in ['E', 'S']:
            return True
        elif prev_top == 'B' and now_top in ['B', 'O']:
            return True
        elif prev_top == 'I' and now_top in ['B', 'O', 'S']:
            return True
        elif prev_top != 'O' and prev_type != now_type:
            return True
        return False

    def _is_begin_of_label(self, now_top: str,
                           prev_type: str, now_type: str) -> bool:
        """
        check if named entity label is begin
        :param prev_top: previous scheme
        :param now_top: now scheme
        :param prev_type: previous label
        :param now_type: now label
        :return: begin -> True, not begin -> False
        """

        if now_top in ['B', 'S']:
            return True
        elif now_top != 'O' and prev_type and prev_type != now_type:
            return True
        return False

    def _check_add_entity(self, word: str, type_: str) -> bool:
        """
        adding entity check
        :param word: a named entity
        :param type_: NER label type
        :return: can add entities -> True, cannot add entities -> False
        """

        if self.check_known and self.check_unknown:
            return True
        elif self.check_known and word in self.known_words[type_]:
            return True
        elif self.check_unknown and word not in self.known_words[type_]:
            return True
        return False

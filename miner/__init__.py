from typing import List, Dict, Tuple, Union
from collections import defaultdict

from .utils import entity_indexes
from .utils import is_end_of_label
from .utils import is_begin_of_label


class Miner:

    def __init__(self, answers: List[List[str]],
                 predicts: List[List[str]],
                 sentences: List[List[str]],
                 known_words: Dict[str, List[str]] = None):
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
            if known_words is None else known_words
        self.known_words.update(
            {'ALL': [NE for k, v in self.known_words.items() for NE in v]})
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
            p, r, f1 = self.evaluations(type_)
            report[type_]['precision'] = p
            report[type_]['recall'] = r
            report[type_]['f1_score'] = f1
            report[type_]['num'] = self.num_of_ne(type_)

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
            p, r, f1 = self.evaluations(type_)
            report[type_]['precision'] = p
            report[type_]['recall'] = r
            report[type_]['f1_score'] = f1
            report[type_]['num'] = self.num_of_ne(type_)

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
            p, r, f1 = self.evaluations(type_)
            report[type_]['precision'] = p
            report[type_]['recall'] = r
            report[type_]['f1_score'] = f1
            report[type_]['num'] = self.num_of_ne(type_)

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

    def evaluations(self, type_select: str) -> Tuple[float, float, float]:
        """
        return precision score
        :param type_select: NER label type
        :return: precision score
        """

        ans_entities = set(self._entity_indexes(self.answers, type_select))
        pred_entities = set(self._entity_indexes(self.predicts, type_select))
        correct_num = len(ans_entities & pred_entities)
        pred_num = len(pred_entities)
        ans_num = len(ans_entities)
        p = correct_num / pred_num if pred_num > 0 else 0.0
        r = correct_num / ans_num if ans_num > 0 else 0.0
        f1 = 2 * p * r / (p + r) if p + r > 0 else 0
        return p, r, f1

    def num_of_ne(self, type_select: str) -> int:
        """
        return number of Named Entity
        :param type_select: NER label type
        :return:
        """

        return len(self._entity_indexes(self.answers, type_select))

    def segmentation_score(self, mode: str = 'default', print_: bool = True) \
            -> Dict[str, Union[float, int]]:
        """
        return segmentation score
        (return parcentages of matching answer and predict labels)
        :param mode: default, unknown, or known
        :param print_: print flag.
                       if this flag equal 'True', print report of NER result.
        :return segmentation score
        """

        if mode == 'unknown':
            self.check_known = False
            self.check_unknown = True
        elif mode == 'known':
            self.check_known = True
            self.check_unknown = False
        else:
            self.check_known = True
            self.check_unknown = True

        p, r, f1 = self.evaluations('ALL')
        report = {'precision': p,
                  'recall': r,
                  'f1_score': f1,
                  'num': self.num_of_ne('ALL')}

        if print_:
            print('\n\tprecision    recall    f1_score   num')
            print('SEG', end='\t')
            print('{0: .3f}'.format(report['precision']), end='       ')
            print('{0: .3f}'.format(report['recall']), end='    ')
            print('{0: .3f}'.format(report['f1_score']), end='     ')
            print('{0: d}'.format(int(report['num'])), end='\n')

        return report

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

        sequences = [label for seq in seqs for label in seq + ['O']]
        sentences = [word for sentence in self.sentences
                     for word in sentence + ['']]

        seq_label_pairs = zip(sequences + ['O'], sentences + [''])
        return entity_indexes(sentences, seq_label_pairs, type_select,
                              self.check_known, self.check_unknown,
                              self.known_words)

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

            if is_end_of_label(prev_top, top, prev_type, type_):
                word = ''.join(sentences[focus_idx: i])
                if word in self.known_words[prev_type]:
                    knownentities[prev_type].append(word)
                else:
                    unknownentities[prev_type].append(word)

            if is_begin_of_label(top, prev_type, type_):
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

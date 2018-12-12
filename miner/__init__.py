from typing import List, Dict, Tuple 
from collections import defaultdict


class Miner():

    def __init__(self, answers: List[List[str]], predicts: List[List[str]], sentences: List[List[str]], known_words: Dict[str: List[str]]):

        self.answers = answers
        self.predicts = predicts
        self.sentences = sentences
        self.known_words = known_words
        self.types = tuple(set([seq.split('-')[-1] for seq in self.answers for type_ in seq if seq != 'O']))
        self.check_known = True
        self.check_unknown = True

    def default_report(self, print_: False) -> Dict[Dict[float]]:

        self.check_known = True
        self.check_unknown = True

        report = {type_: defaultdict(float()) for type_ in self.types}

        for type_ in self.types:
            report[type_]['precision'] = self.precision(type_)
            report[type_]['recall'] = self.recall(type_)
            report[type_]['f1_score'] = self.f1_score(type_)

        for type_ in self.types:
            report[type_] = dict(report[type_])

        if print_:
            self._print_report(report)

        return report 

    def known_only_report(self, print_: False) -> Dict[Dict[float]]:


        self.check_known = True
        self.check_unknown = False

        report = {type_: defaultdict(float()) for type_ in self.types}

        for type_ in self.types:
            report[type_]['precision'] = self.precision(type_)
            report[type_]['recall'] = self.recall(type_)
            report[type_]['f1_score'] = self.f1_score(type_)

        for type_ in self.types:
            report[type_] = dict(report[type_])

        if print_:
            self._print_report(report)

        return report 

    def unknown_only_report(self, print_: False) -> Dict[Dict[float]]:

        self.check_known = False
        self.check_unknown = True

        report = {type_: defaultdict(float()) for type_ in self.types}

        for type_ in self.types:
            report[type_]['precision'] = self.precision(type_)
            report[type_]['recall'] = self.recall(type_)
            report[type_]['f1_score'] = self.f1_score(type_)

        for type_ in self.types:
            report[type_] = dict(report[type_])

        if print_:
            self._print_report(report)

        return report 

    def precision(self, type_select: str='') -> float:

        ans_entities = set(self._return_entities(self.answers, type_select))
        pred_entities = set(self._return_entities(self.predicts, type_select))

        correct_num = len(ans_entities & pred_entities)
        pred_num = len(pred_entities)

        return correct_num / pred_num if pred_num > 0 else 0

    def recall(self, type_select: str='') -> float:

        ans_entities = set(self._return_entities(self.answers, type_select))
        pred_entities = set(self._return_entities(self.predicts, type_select))

        correct_num = len(ans_entities & pred_entities)
        ans_num = len(ans_entities)

        return correct_num / ans_num if ans_num > 0 else 0

    def f1_score(self, type_select: str='') -> float:

        p = self.precision(type_select)
        r = self.recall(type_select)
        return 2 * p * r / (p + r) if p + r > 0 else 0

    def _return_entities(self, seqs: List[List[str]], type_select: str) -> List[Tuple[str, int, int]]:

        entities = [] 
        sequences = [label for seq in seqs for label in seq + ['O']]
        sentences =[word for sentence in self.sentences for word in sentence + ['']] 
        prev_top = 'O'
        prev_type =''
        focus_idx = 0

        for i, (label, words) in enumerate(zip(sequences + ['O'], sentences + [''])):
            top = label[0] 
            type_ = label.split('-')[-1]

            if self._is_end_of_label(prev_top, top, prev_type, type_) \
                and type_select in [prev_type, ''] \
                and self._check_add_entities(words[focus_idx: i - 1]):
                    entities.append([(prev_type, focus_idx, i - 1)]) 

            focus_idx if self._is_begin_of_label(prev_top, top, prev_type, type_) else focus_idx
            prev_top = top
            prev_type = type_

        return entities

    def _print_report(self, result: Dict[str, Dict[str, float]]):

        print('\tprecision\trecall\tf1_score')
        for type_ in self.types:
            print(type_, end='\t')
            print(result[type_]['precision'], end='\t')
            print(result[type_]['recall'], end='\t')
            print(result[type_]['f1_score'], end='\t')

    def _is_end_of_label(self, prev_top: str, now_top: str, prev_type: str, now_type: str) -> bool:
        
        if prev_top in ['E', 'S']:
            return True
        elif prev_top == 'B' and now_top in ['B', 'O']:
            return True
        elif prev_top == 'I' and now_top in ['B', 'O', 'S']:
            return True
        elif prev_top != 'O' and prev_type != now_type:
            return True
        return False

    def _is_begin_of_label(self, prev_top: str, now_top: str, prev_type: str, now_type: str) -> bool:

        if now_top in ['B', 'S']:
            return True
        elif now_top != 'O' and prev_type and prev_type != now_type: 
            return True
        return False

    def _check_add_entities(self, word: str) -> bool:

        if self.check_known and self.check_unknown:
            return True
        elif self.check_known and word in self.known_words:
            return True
        elif self.check_unknown and word not in self.known_words:
            return True
        return False
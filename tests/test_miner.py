import unittest
from miner import Miner


class TestMiner(unittest.TestCase):

    def setUp(self):
        # 花子さんは東京に行きました(IOB2)
        # 山田太郎くんは東京駅に向かいました(IOB2)
        # 花子さんとボブくんは東京スカイツリーに行きました(BIOES)
        self.answers = [
            'B-PSN O O B-LOC O O O O'.split(' '),
            'B-PSN I-PSN O O B-LOC I-LOC O O O O'.split(' '),
            'S-PSN O O S-PSN O O B-LOC I-LOC E-LOC O O O O'.split(' ')
        ]
        self.predicts = [
            'B-PSN O O B-LOC O O O O'.split(' '),
            'B-PSN B-PSN O O B-LOC I-LOC O O O O'.split(' '),
            'S-PSN O O O O O B-LOC I-LOC E-LOC O O O O'.split(' ')
        ]
        self.sentences = [
            '花子 さん は 東京 に 行き まし た'.split(' '),
            '山田 太郎 君 は 東京 駅 に 向かい まし た'.split(' '),
            '花子 さん と ボブ くん は 東京 スカイ ツリー に 行き まし た'.split(' '),
        ]

        self.knowns = {'PSN': ['花子'], 'LOC': ['東京']}

        self.miner = Miner(self.answers, self.predicts,
                           self.sentences, self.knowns)

    def test_initialize(self):

        self.assertEqual(self.miner.answers, self.answers)
        self.assertEqual(self.miner.predicts, self.predicts)
        self.assertEqual(self.miner.sentences, self.sentences)
        self.assertEqual(self.miner.known_words, self.knowns)
        # check no setting known words
        m = Miner(self.answers, self.predicts, self.sentences)
        self.assertEqual(m.known_words, {'PSN': [], 'LOC': []})

    def test_default_report(self):

        result = self.miner.default_report(False)
        self.assertTrue(all([k in ['PSN', 'LOC'] for k, v in result.items()]))
        self.assertEqual([k for k, v in result['PSN'].items()],
                         ['precision', 'recall', 'f1_score', 'num'])
        self.assertEqual({'PSN': {'precision': 0.5, 'recall': 0.5,
                                  'f1_score': 0.5, 'num': 4},
                          'LOC': {'precision': 1.0, 'recall': 1.0,
                                  'f1_score': 1.0, 'num': 3}},
                         result)

    def test_known_only_report(self):

        result = self.miner.known_only_report(False)
        self.assertTrue(all([k in ['PSN', 'LOC'] for k, v in result.items()]))
        self.assertEqual([k for k, v in result['PSN'].items()],
                         ['precision', 'recall', 'f1_score', 'num'])
        self.assertEqual({'PSN': {'precision': 1.0, 'recall': 1.0,
                                  'f1_score': 1.0, 'num': 2},
                          'LOC': {'precision': 1.0, 'recall': 1.0,
                                  'f1_score': 1.0, 'num': 1}},
                         result)

    def test_unknown_only_report(self):

        result = self.miner.unknown_only_report(False)
        self.assertTrue(all([k in ['PSN', 'LOC'] for k, v in result.items()]))
        self.assertEqual([k for k, v in result['PSN'].items()],
                         ['precision', 'recall', 'f1_score', 'num'])
        self.assertEqual({'PSN': {'precision': 0, 'recall': 0,
                                  'f1_score': 0, 'num': 2},
                          'LOC': {'precision': 1.0, 'recall': 1.0,
                                  'f1_score': 1.0, 'num': 2}},
                         result)

    def test__entity_indexes(self):

        result = self.miner._entity_indexes(self.answers, 'PSN')
        expect = [('PSN', 0, 0), ('PSN', 9, 10),
                  ('PSN', 20, 20), ('PSN', 23, 23)]
        self.assertEqual(result, expect)
        result = self.miner._entity_indexes(self.answers, 'LOC')
        expect = [('LOC', 3, 3), ('LOC', 13, 14),
                  ('LOC', 26, 28)]
        self.assertEqual(result, expect)

    def test__return_named_entities(self):

        result = self.miner._return_named_entities(self.answers)
        expect = {'known': {'PSN': ['花子'],
                            'LOC': ['東京']},
                  'unknown': {'PSN': ['山田太郎', 'ボブ'],
                              'LOC': ['東京スカイツリー', '東京駅']}}
        for (rk, rv), (ek, ev) in zip(result.items(), expect.items()):
            self.assertTrue(set(rv['PSN']) & set(ev['PSN']))
            self.assertTrue(set(rv['LOC']) & set(ev['LOC']))

    def test_return_answer_named_entities(self):

        result = self.miner.return_answer_named_entities()
        expect = self.miner._return_named_entities(self.answers)
        for (rk, rv), (ek, ev) in zip(result.items(), expect.items()):
            self.assertTrue(set(rv['PSN']) & set(ev['PSN']))
            self.assertTrue(set(rv['LOC']) & set(ev['LOC']))

    def test_return_predict_named_entities(self):

        result = self.miner.return_predict_named_entities()
        expect = self.miner._return_named_entities(self.predicts)
        for (rk, rv), (ek, ev) in zip(result.items(), expect.items()):
            self.assertTrue(set(rv['PSN']) & set(ev['PSN']))
            self.assertTrue(set(rv['LOC']) & set(ev['LOC']))

    def test__is_end_of_label(self):

        labels = ['B', 'I', 'O', 'S', 'B', 'I', 'I', 'E', 'O', 'O', 'B', 'B']
        self.assertFalse(self.miner._is_end_of_label(
            labels[0], labels[1], 'a', 'a'))
        self.assertTrue(self.miner._is_end_of_label(
            labels[1], labels[2], 'a', 'a'))
        self.assertFalse(self.miner._is_end_of_label(
            labels[2], labels[3], 'a', 'a'))
        self.assertTrue(self.miner._is_end_of_label(
            labels[3], labels[4], 'a', 'a'))
        self.assertFalse(self.miner._is_end_of_label(
            labels[4], labels[5], 'a', 'a'))
        self.assertFalse(self.miner._is_end_of_label(
            labels[5], labels[6], 'a', 'a'))
        self.assertFalse(self.miner._is_end_of_label(
            labels[6], labels[7], 'a', 'a'))
        self.assertTrue(self.miner._is_end_of_label(
            labels[7], labels[8], 'a', 'a'))
        self.assertFalse(self.miner._is_end_of_label(
            labels[8], labels[9], 'a', 'a'))
        self.assertFalse(self.miner._is_end_of_label(
            labels[9], labels[10], 'a', 'a'))
        self.assertTrue(self.miner._is_end_of_label(
            labels[10], labels[11], 'a', 'a'))
        self.assertTrue(self.miner._is_end_of_label(
            labels[11], '', 'a', ''))
        self.assertTrue(self.miner._is_end_of_label('B', 'I', 'a', 'b'))

    def test__is_begin_of_label(self):

        labels = ['B', 'I', 'O', 'S', 'B', 'I', 'I', 'E', 'O', 'O', 'B', 'B']
        self.assertTrue(self.miner._is_begin_of_label(
            '', labels[0], 'a', 'a'))
        self.assertFalse(self.miner._is_begin_of_label(
            labels[1], labels[2], 'a', 'a'))
        self.assertTrue(self.miner._is_begin_of_label(
            labels[2], labels[3], 'a', 'a'))
        self.assertTrue(self.miner._is_begin_of_label(
            labels[3], labels[4], 'a', 'a'))
        self.assertFalse(self.miner._is_begin_of_label(
            labels[4], labels[5], 'a', 'a'))
        self.assertFalse(self.miner._is_begin_of_label(
            labels[5], labels[6], 'a', 'a'))
        self.assertFalse(self.miner._is_begin_of_label(
            labels[6], labels[7], 'a', 'a'))
        self.assertFalse(self.miner._is_begin_of_label(
            labels[7], labels[8], 'a', 'a'))
        self.assertFalse(self.miner._is_begin_of_label(
            labels[8], labels[9], 'a', 'a'))
        self.assertTrue(self.miner._is_begin_of_label(
            labels[9], labels[10], 'a', 'a'))
        self.assertTrue(self.miner._is_begin_of_label(
            labels[10], labels[11], 'a', 'a'))
        self.assertTrue(self.miner._is_begin_of_label('B', 'I', 'a', 'b'))

    def test__check_add_entity(self):

        # assert all
        self.miner.check_known = True
        self.miner.check_unknown = True
        self.assertTrue(self.miner._check_add_entity('', ''))
        self.assertTrue(self.miner._check_add_entity('花子', 'PSN'))
        # assert known
        self.miner.check_known = True
        self.miner.check_unknown = False
        self.assertTrue(self.miner._check_add_entity('花子', 'PSN'))
        self.assertTrue(self.miner._check_add_entity('東京', 'LOC'))
        self.assertFalse(self.miner._check_add_entity('ボブ', 'PSN'))
        # assert unknown
        self.miner.check_known = False
        self.miner.check_unknown = True
        self.assertTrue(self.miner._check_add_entity('ボブ', 'PSN'))
        self.assertTrue(self.miner._check_add_entity('東京スカイツリー', 'LOC'))
        self.assertFalse(self.miner._check_add_entity('東京', 'LOC'))

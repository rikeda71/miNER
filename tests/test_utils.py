import unittest

from miner.utils import is_begin_of_label, is_end_of_label


class TestUtils(unittest.TestCase):
    def test__is_end_of_label(self):

        labels = ["B", "I", "O", "S", "B", "I", "I", "E", "O", "O", "B", "B"]
        self.assertFalse(is_end_of_label(labels[0], labels[1], "a", "a"))
        self.assertTrue(is_end_of_label(labels[1], labels[2], "a", "a"))
        self.assertFalse(is_end_of_label(labels[2], labels[3], "a", "a"))
        self.assertTrue(is_end_of_label(labels[3], labels[4], "a", "a"))
        self.assertFalse(is_end_of_label(labels[4], labels[5], "a", "a"))
        self.assertFalse(is_end_of_label(labels[5], labels[6], "a", "a"))
        self.assertFalse(is_end_of_label(labels[6], labels[7], "a", "a"))
        self.assertTrue(is_end_of_label(labels[7], labels[8], "a", "a"))
        self.assertFalse(is_end_of_label(labels[8], labels[9], "a", "a"))
        self.assertFalse(is_end_of_label(labels[9], labels[10], "a", "a"))
        self.assertTrue(is_end_of_label(labels[10], labels[11], "a", "a"))
        self.assertTrue(is_end_of_label(labels[11], "", "a", ""))
        self.assertTrue(is_end_of_label("B", "I", "a", "b"))

    def test__is_begin_of_label(self):

        labels = ["B", "I", "O", "S", "B", "I", "I", "E", "O", "O", "B", "B"]
        self.assertTrue(is_begin_of_label(labels[0], "a", "a"))
        self.assertFalse(is_begin_of_label(labels[2], "a", "a"))
        self.assertTrue(is_begin_of_label(labels[3], "a", "a"))
        self.assertTrue(is_begin_of_label(labels[4], "a", "a"))
        self.assertFalse(is_begin_of_label(labels[5], "a", "a"))
        self.assertFalse(is_begin_of_label(labels[6], "a", "a"))
        self.assertFalse(is_begin_of_label(labels[7], "a", "a"))
        self.assertFalse(is_begin_of_label(labels[8], "a", "a"))
        self.assertFalse(is_begin_of_label(labels[9], "a", "a"))
        self.assertTrue(is_begin_of_label(labels[10], "a", "a"))
        self.assertTrue(is_begin_of_label(labels[11], "a", "a"))
        self.assertTrue(is_begin_of_label("I", "a", "b"))

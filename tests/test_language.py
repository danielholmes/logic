from unittest import TestCase
from logic.language import *
from utils import data_provider

class PropositionalConstantTest(TestCase):
    valid_labels_data_provider = lambda: (
        ('raining', ),
        ('rAiNiNg', ),
        ('r32aining', ),
        ('raining_or_snowing', )
    )

    @data_provider(valid_labels_data_provider)
    def test_valid_constant_labels(self, label):
        c = PropositionalConstant(label)

        self.assertEqual(label, c.label)

    invalid_labels_data_provider = lambda: (
        ('Raining', ),
        ('324567', ),
        (123, ),
        ('', ),
        ('raining-or-snowing', )
    )

    @data_provider(invalid_labels_data_provider)
    def test_invalid_constant_names(self, label):
        with self.assertRaises(InvalidConstantLabelException):
            PropositionalConstant(label)

    def test_eq(self):
        constant_1 = PropositionalConstant("a")
        constant_2 = PropositionalConstant("a")

        self.assertEqual(True, constant_1 == constant_2)

    def test_not_eq(self):
        constant_1 = PropositionalConstant("a")
        constant_2 = PropositionalConstant("b")

        self.assertEqual(False, constant_1 == constant_2)

    def test_gt(self):
        constant_1 = PropositionalConstant("b")
        constant_2 = PropositionalConstant("a")

        self.assertEqual(True, constant_1 > constant_2)

    def test_not_gt(self):
        constant_1 = PropositionalConstant("a")
        constant_2 = PropositionalConstant("b")

        self.assertEqual(False, constant_1 > constant_2)

class TruthAssignmentTest(TestCase):
    def test_get_value_valid(self):
        constant = PropositionalConstant("hello")
        a = TruthAssignment({constant : True})

        result = a.get(constant)

        self.assertEqual(True, result)

    def test_get_value_invalid(self):
        constant = PropositionalConstant("hello")
        new_constant = PropositionalConstant("new")
        a = TruthAssignment({constant : True})

        result = a.get(new_constant)

        self.assertEqual(None, result)

    lt_data_provider = lambda: (
        (
            TruthAssignment({PropositionalConstant("a"): True,  PropositionalConstant("b"): True}),
            TruthAssignment({PropositionalConstant("a"): False, PropositionalConstant("b"): False})
        ),
        (
            TruthAssignment({PropositionalConstant("a"): True,  PropositionalConstant("b"): True}),
            TruthAssignment({PropositionalConstant("a"): True,  PropositionalConstant("b"): False})
        ),
        (
            TruthAssignment({PropositionalConstant("a"): True,  PropositionalConstant("b"): False}),
            TruthAssignment({PropositionalConstant("a"): False, PropositionalConstant("b"): False})
        )
    )

    @data_provider(lt_data_provider)
    def test_lt(self, assignment_1, assignment_2):
        result = assignment_1 < assignment_2

        self.assertEqual(True, result)

class PropositionalVocabularyTest(TestCase):
    def test_add_unique(self):
        vocab_1 = PropositionalVocabulary.from_constant_names(["a"])
        vocab_2 = PropositionalVocabulary.from_constant_names(["b"])

        result = vocab_1 + vocab_2

        self.assertEqual(PropositionalVocabulary.from_constant_names(["a", "b"]), result)

    def test_all_assignments_single(self):
        constant = PropositionalConstant("constant")
        vocab = PropositionalVocabulary([constant])

        expected = frozenset([TruthAssignment({constant : True}), TruthAssignment({constant : False})])

        self.assertEqual(expected, vocab.all_assignments)

    def test_all_assignments_multiple(self):
        c1 = PropositionalConstant("one")
        c2 = PropositionalConstant("two")
        vocab = PropositionalVocabulary([c1, c2])

        expected = frozenset([
            TruthAssignment({c1 : True, c2 : True}), 
            TruthAssignment({c1 : True, c2 : False}), 
            TruthAssignment({c1 : False, c2 : True}), 
            TruthAssignment({c1 : False, c2 : False})
        ])

        self.assertEqual(expected, vocab.all_assignments)

    def test_str(self):
        vocab = PropositionalVocabulary.from_constant_names(["a", "b"])

        result = str(vocab)

        self.assertEqual(str(["a", "b"]), result)
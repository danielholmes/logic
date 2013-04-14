import unittest.main
from unittest import TestCase
from language import PropositionalConstant, PropositionalVocabulary, TruthAssignment, InvalidConstantLabelException
from syntax import *
from unittest_data_provider import data_provider

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

        self.assertEquals(label, c.label)

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

class TruthAssignmentTest(TestCase):
    def test_get_value_valid(self):
        constant = PropositionalConstant("hello")
        a = TruthAssignment({constant : True})

        result = a.get(constant)

        self.assertEquals(True, result)

    def test_get_value_invalid(self):
        constant = PropositionalConstant("hello")
        new_constant = PropositionalConstant("new")
        a = TruthAssignment({constant : True})

        result = a.get(new_constant)

        self.assertEquals(None, result)

class SimpleSentenceTest(TestCase):
    def test_eval(self):
        constant = PropositionalConstant("hello")
        sentence = SimpleSentence(constant)
        assignment = TruthAssignment({constant : True})

        result = sentence.eval(assignment)

        self.assertEquals(True, result)

    def test_eval_not_found(self):
        constant = PropositionalConstant("hello")
        other_constant = PropositionalConstant("world")
        sentence = SimpleSentence(other_constant)
        assignment = TruthAssignment({constant : True})

        with self.assertRaises(ConstantDoesntExistException):
            sentence.eval(assignment)

    def test_all_constants(self):
        constant = PropositionalConstant("hello")
        sentence = SimpleSentence(constant)

        self.assertEquals(frozenset((constant, )), sentence.all_constants)

class NegationTest(TestCase):
    def test_eval_true(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))
        assignment = TruthAssignment({constant : True})

        result = negation.eval(assignment)

        self.assertEquals(False, result)

    def test_eval_false(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))
        assignment = TruthAssignment({constant : False})

        result = negation.eval(assignment)

        self.assertEquals(True, result)

    def test_is_logically_equivalent_self(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))

        result = negation.is_logically_equivalent(negation)

        self.assertEquals(True, result)

    def test_is_logically_equivalent_other_same(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))
        other_negation = Negation(SimpleSentence(constant))

        result = negation.is_logically_equivalent(other_negation)

        self.assertEquals(True, result)

    def test_is_logically_equivalent_other_constant(self):
        constant1 = PropositionalConstant("hello1")
        constant2 = PropositionalConstant("hello2")
        negation = Negation(SimpleSentence(constant1))
        other_negation = Negation(SimpleSentence(constant2))

        result = negation.is_logically_equivalent(other_negation)

        self.assertEquals(False, result)

class ConjunctionTest(TestCase):
    values_data_provider = lambda: (
        (True, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False)
    )

    @data_provider(values_data_provider)
    def test_eval(self, expected, conjunct_1_value, conjunct_2_value):
        conjunct_1 = PropositionalConstant("conjunct_1")
        conjunct_2 = PropositionalConstant("conjunct_2")
        conjunction = Conjunction(SimpleSentence(conjunct_1), SimpleSentence(conjunct_2))
        assignment = TruthAssignment({conjunct_1 : conjunct_1_value, conjunct_2 : conjunct_2_value})

        result = conjunction.eval(assignment)

        self.assertEquals(expected, result)

    def test_all_constants(self):
        conjunct_1 = PropositionalConstant("conjunct_1")
        conjunct_2 = PropositionalConstant("conjunct_2")
        conjunction = Conjunction(SimpleSentence(conjunct_1), SimpleSentence(conjunct_2))

        self.assertEquals(frozenset((conjunct_1, conjunct_2)), conjunction.all_constants)

class DisjunctionTest(TestCase):
    values_data_provider = lambda: (
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (False, False, False)
    )

    @data_provider(values_data_provider)
    def test_eval(self, expected, disjunct_1_value, disjunct_2_value):
        disjunct_1 = PropositionalConstant("disjunct_1")
        disjunct_2 = PropositionalConstant("disjunct_2")
        disjunction = Disjunction(SimpleSentence(disjunct_1), SimpleSentence(disjunct_2))
        assignment = TruthAssignment({disjunct_1 : disjunct_1_value, disjunct_2 : disjunct_2_value})

        result = disjunction.eval(assignment)

        self.assertEquals(expected, result)

class ImplicationTest(TestCase):
    values_data_provider = lambda: (
        (True, True, True),
        (False, True, False),
        (True, False, True),
        (True, False, False)
    )

    @data_provider(values_data_provider)
    def test_eval(self, expected, antecedent_value, consequent_value):
        antecedent = PropositionalConstant("antecedent")
        consequent = PropositionalConstant("consequent")
        implication = Implication(SimpleSentence(antecedent), SimpleSentence(consequent))
        assignment = TruthAssignment({antecedent : antecedent_value, consequent : consequent_value})

        result = implication.eval(assignment)

        self.assertEquals(expected, result)

class ReductionTest(TestCase):
    values_data_provider = lambda: (
        (True, True, True),
        (True, True, False),
        (False, False, True),
        (True, False, False)
    )

    @data_provider(values_data_provider)
    def test_eval(self, expected, consequent_value, antecedent_value):
        consequent = PropositionalConstant("consequent")
        antecedent = PropositionalConstant("antecedent")
        reduction = Reduction(SimpleSentence(consequent), SimpleSentence(antecedent))
        assignment = TruthAssignment({consequent : consequent_value, antecedent : antecedent_value})

        result = reduction.eval(assignment)

        self.assertEquals(expected, result)

class EquivalenceTest(TestCase):
    values_data_provider = lambda: (
        (True, True, True),
        (False, True, False),
        (False, False, True),
        (True, False, False)
    )

    @data_provider(values_data_provider)
    def test_eval(self, expected, target_1_value, target_2_value):
        target_1 = PropositionalConstant("target_1")
        target_2 = PropositionalConstant("target_2")
        equivalence = Equivalence(SimpleSentence(target_1), SimpleSentence(target_2))
        assignment = TruthAssignment({target_1 : target_1_value, target_2 : target_2_value})

        result = equivalence.eval(assignment)

        self.assertEquals(expected, result)

class PropositionalVocabularyTest(TestCase):
    def test_all_assignments_single(self):
        constant = PropositionalConstant("constant")
        vocab = PropositionalVocabulary([constant])

        expected = frozenset([TruthAssignment({constant : True}), TruthAssignment({constant : False})])

        self.assertEquals(expected, vocab.all_assignments)

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

        self.assertEquals(expected, vocab.all_assignments)

if __name__ == '__main__':
    unittest.main()
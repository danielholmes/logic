from abc import ABCMeta, abstractmethod, abstractproperty
from unittest import TestCase
from utils import data_provider
from logic.syntax import *
from logic.language import *

class SimpleSentenceTest(TestCase):
    def test_eval(self):
        constant = PropositionalConstant("hello")
        sentence = SimpleSentence(constant)
        assignment = TruthAssignment({constant : True})

        result = sentence.eval(assignment)

        self.assertEqual(True, result)

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

        self.assertEqual(frozenset((constant, )), sentence.all_constants)

    def test_gt(self):
        sentence_1 = SimpleSentence(PropositionalConstant("b"))
        sentence_2 = SimpleSentence(PropositionalConstant("a"))

        result = sentence_1 > sentence_2

        self.assertEqual(True, result)

class AbstractSentenceTest(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_example_sentence():
        pass

    def test_get_logical_equivalence_self(self):
        example = self.create_example_sentence()

        result = example.determine_logical_equivalence(example)
        bool_result = example.is_logically_equivalent(example)
        
        self.assertEqual(True, result.is_equivalent)
        self.assertEqual(True, bool_result)

    def test_get_logical_equivalence_negation_of_self(self):
        example = self.create_example_sentence()
        negation = Negation(example)

        result = example.determine_logical_equivalence(negation)
        bool_result = example.is_logically_equivalent(negation)

        self.assertEqual(False, result.is_equivalent)
        self.assertEqual(False, bool_result)

    def test_logically_entails_self(self):
        example = self.create_example_sentence()

        result = example.logically_entails(example)

        self.assertEqual(True, result)

    def test_not_logically_entails_negation_self(self):
        example = self.create_example_sentence()
        example_neg = Negation(example)

        result = example.logically_entails(example_neg)

        self.assertEqual(False, result)

    def test_hash(self):
        example = self.create_example_sentence()

        result = hash(example)

        self.assertEqual(int, type(result))

class SentenceSetTest(AbstractSentenceTest, TestCase):
    extract_vocabulary_data_provider = lambda: (
        (
            ["a", "b"],
            [
                SimpleSentence(PropositionalConstant("a")),
                SimpleSentence(PropositionalConstant("b"))
            ]
        ),
        (
            ["a", "b", "c"],
            [
                SimpleSentence(PropositionalConstant("a")),
                SimpleSentence(PropositionalConstant("b")),
                Conjunction(
                    SimpleSentence(PropositionalConstant("a")),
                    SimpleSentence(PropositionalConstant("c"))
                )
            ]
        )
    )

    @data_provider(extract_vocabulary_data_provider)
    def test_extract_vocabulary(self, constant_names, sentences):
        example = SentenceSet(sentences)

        vocab = example.vocabulary

        self.assertEqual(PropositionalVocabulary.from_constant_names(constant_names), vocab)

    logically_entails_data_provider = lambda: (
        (
            False,
            [SimpleSentence(PropositionalConstant("a"))],
            [SimpleSentence(PropositionalConstant("b"))]
        ),
        (
            True,
            [Negation(Negation(SimpleSentence(PropositionalConstant("a"))))],
            [SimpleSentence(PropositionalConstant("a"))]
        )
    )

    @data_provider(logically_entails_data_provider)
    def test_logically_entails(self, expected, sentences_1, sentences_2):
        set_1 = SentenceSet(sentences_1)
        set_2 = SentenceSet(sentences_2)

        result = set_1.logically_entails(set_2)

        self.assertEqual(expected, result)

    def create_example_sentence(self):
        return SentenceSet([
            SimpleSentence(PropositionalConstant("a")),
            SimpleSentence(PropositionalConstant("b"))
        ])

class NegationTest(TestCase, AbstractSentenceTest):
    def create_example_sentence(self):
        return Negation(SimpleSentence(PropositionalConstant("hello")))

    def test_eval_true(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))
        assignment = TruthAssignment({constant : True})

        result = negation.eval(assignment)

        self.assertEqual(False, result)

    def test_eval_false(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))
        assignment = TruthAssignment({constant : False})

        result = negation.eval(assignment)

        self.assertEqual(True, result)

    def test_is_logically_equivalent_other_same(self):
        constant = PropositionalConstant("hello")
        negation = Negation(SimpleSentence(constant))
        other_negation = Negation(SimpleSentence(constant))

        result = negation.determine_logical_equivalence(other_negation)
        bool_result = negation.is_logically_equivalent(other_negation)

        expected = LogicalEquivalence(frozenset([
            TruthAssignment({constant : True}),
            TruthAssignment({constant : False})
        ]), frozenset())
        self.assertEqual(expected, result)
        self.assertEqual(True, bool_result)

    def test_is_logically_equivalent_other_constant(self):
        constant1 = PropositionalConstant("hello1")
        constant2 = PropositionalConstant("hello2")
        negation = Negation(SimpleSentence(constant1))
        other_negation = Negation(SimpleSentence(constant2))

        result = negation.determine_logical_equivalence(other_negation)
        bool_result = negation.is_logically_equivalent(other_negation)

        expected = LogicalEquivalence(frozenset([
            TruthAssignment({constant1 : True, constant2 : True}),
            TruthAssignment({constant1 : False, constant2 : False})
        ]), frozenset([
            TruthAssignment({constant1 : True, constant2 : False}),
            TruthAssignment({constant1 : False, constant2 : True})
        ]))
        self.assertEqual(expected, result)
        self.assertEqual(False, bool_result)

class ConjunctionTest(TestCase, AbstractSentenceTest):
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

        self.assertEqual(expected, result)

    def test_all_constants(self):
        conjunct_1 = PropositionalConstant("conjunct_1")
        conjunct_2 = PropositionalConstant("conjunct_2")
        conjunction = Conjunction(SimpleSentence(conjunct_1), SimpleSentence(conjunct_2))

        self.assertEqual(frozenset((conjunct_1, conjunct_2)), conjunction.all_constants)

    def create_example_sentence(self):
        return Conjunction(
            SimpleSentence(PropositionalConstant("hello")),
            SimpleSentence(PropositionalConstant("world"))
        )

class DisjunctionTest(TestCase, AbstractSentenceTest):
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

        self.assertEqual(expected, result)

    def create_example_sentence(self):
        return Disjunction(
            SimpleSentence(PropositionalConstant("hello")),
            SimpleSentence(PropositionalConstant("world"))
        )

class ImplicationTest(TestCase, AbstractSentenceTest):
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

        self.assertEqual(expected, result)

    def create_example_sentence(self):
        return Implication(
            SimpleSentence(PropositionalConstant("hello")),
            SimpleSentence(PropositionalConstant("world"))
        )

class ReductionTest(TestCase, AbstractSentenceTest):
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

        self.assertEqual(expected, result)

    def create_example_sentence(self):
        return Reduction(
            SimpleSentence(PropositionalConstant("hello")),
            SimpleSentence(PropositionalConstant("world"))
        )

class EquivalenceTest(TestCase, AbstractSentenceTest):
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

        self.assertEqual(expected, result)

    def create_example_sentence(self):
        return Equivalence(
            SimpleSentence(PropositionalConstant("hello")),
            SimpleSentence(PropositionalConstant("world"))
        )
import unittest.main
from unittest import TestCase
from language import PropositionalConstant, PropositionalVocabulary, TruthAssignment, InvalidConstantLabelException
from syntax import *
from parser import Parser, ParsingError
from display import TruthTable
from abc import ABCMeta, abstractmethod, abstractproperty

def data_provider(fn_data_provider):
    """Data provider decorator, allows another callable to provide the data for the test"""
    def test_decorator(fn):
        def repl(self, *args):
            for i in fn_data_provider():
                try:
                    fn(self, *i)
                except AssertionError:
                    print("Assertion error caught with data set %s" % i)
                    raise
        return repl
    return test_decorator

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

class AbstractSentenceTest:
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

    # Unsure if this one should be used, do some more research
    #def test_get_logical_equivalence_negation_of_self(self):
    #    example = self.create_example_sentence()
    #    negation = Negation(example)

    #    result = example.determine_logical_equivalence(negation)
    #    bool_result = example.is_logically_equivalent(example)
        
    #    self.assertEqual(False, result.is_equivalent)
    #    self.assertEqual(False, bool_result)

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

class PropositionalVocabularyTest(TestCase):
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

class ParserTest(TestCase):
    valid_data_provider = lambda: (
        (SimpleSentence(PropositionalConstant("a")), "a"),
        (SimpleSentence(PropositionalConstant("a")), "a   "),
        (SimpleSentence(PropositionalConstant("a")), "   a"),
        (SimpleSentence(PropositionalConstant("abc")), "abc"),
        (SimpleSentence(PropositionalConstant("a78")), "a78"),
        (SimpleSentence(PropositionalConstant("aBC")), "aBC"),
        (SimpleSentence(PropositionalConstant("a_78")), "a_78"),
        (Negation(SimpleSentence(PropositionalConstant("var"))), "-var"),
        (Conjunction(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), "one^two"),
        (Disjunction(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), "one|two"),
        (Equivalence(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), "one<=>two"),
        (Implication(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), "one=>two"),
        (Reduction(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), "one<=two"),
        (SimpleSentence(PropositionalConstant("abc")), "(abc)"),
        (
            Conjunction(
                Conjunction(
                    SimpleSentence(PropositionalConstant("abc")), 
                    SimpleSentence(PropositionalConstant("def"))
                ),
                SimpleSentence(PropositionalConstant("ghi"))
            ), 
            "abc^def^ghi"
        ),
        (
            Conjunction(
                SimpleSentence(PropositionalConstant("abc")), 
                Conjunction(
                    SimpleSentence(PropositionalConstant("def")),
                    SimpleSentence(PropositionalConstant("ghi"))
                )
            ), 
            "abc^(def^ghi)"
        )
    )

    @data_provider(valid_data_provider)
    def test_valid_expressions(self, expected, string_input):
        parser = Parser()

        expression = parser(string_input)

        self.assertEqual(expected, expression)

    invalid_data_provider = lambda: (
        ("A", ),
        ("123", ),
        ("a*b", ),
        ("a b", ),
        ("(a", )
    )

    @data_provider(invalid_data_provider)
    def test_invalid_expressions(self, string_input):
        parser = Parser()

        with self.assertRaises(ParsingError):
            parser(string_input)

class TruthTableTest(TestCase):
    def test_basic_simple_string(self):
        vocab = PropositionalVocabulary([PropositionalConstant("a")])
        table = TruthTable(vocab)

        result = table.simple_string

        self.assertEqual("""+---+
| a |
+---+
| 1 |
| 0 |
+---+""", result)

    def test_larger_simple_string(self):
        a_constant = PropositionalConstant("a")
        vocab = PropositionalVocabulary([
            a_constant,
            PropositionalConstant("b")
        ])
        table = TruthTable(vocab, [Negation(SimpleSentence(a_constant))])

        result = table.simple_string

        self.assertEqual("""+---+---+----+
| a | b | -a |
+---+---+----+
| 1 | 1 |  0 |
| 1 | 0 |  0 |
| 0 | 1 |  1 |
| 0 | 0 |  1 |
+---+---+----+""", result)

    def test_basic_matrix(self):
        vocab = PropositionalVocabulary([PropositionalConstant("a")])
        table = TruthTable(vocab)

        result = table.matrix

        self.assertEqual([["a", True, False]], result)

    def test_larger_matrix(self):
        a_constant = PropositionalConstant("a")
        vocab = PropositionalVocabulary([
            a_constant,
            PropositionalConstant("b")
        ])
        table = TruthTable(vocab, [Negation(SimpleSentence(a_constant))])

        result = table.matrix

        self.assertEqual([
            ["a", True, True, False, False],
            ["b", True, False, True, False],
            ["-a", False, False, True, True]
        ], result)

if __name__ == '__main__':
    unittest.main()
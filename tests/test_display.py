from unittest import TestCase
from logic.language import PropositionalConstant, PropositionalVocabulary
from logic.syntax import Negation, SimpleSentence
from logic.display import TruthTable

class TruthTableTest(TestCase):
    def test_basic_simple_string(self):
        vocab = PropositionalVocabulary([PropositionalConstant("a")])
        table = TruthTable(vocab)

        result = table.simple_string

        self.assertEqual(
"""+---+
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

        self.assertEqual(
"""+---+---+----+
| a | b | -a |
+---+---+----+
| 1 | 1 | 0  |
| 1 | 0 | 0  |
| 0 | 1 | 1  |
| 0 | 0 | 1  |
+---+---+----+""", result)

    def test_basic_matrix(self):
        constant_a = PropositionalConstant("a")
        vocab = PropositionalVocabulary([constant_a])
        table = TruthTable(vocab)

        result = table.matrix

        self.assertEqual([[SimpleSentence(constant_a), True, False]], result)

    def test_larger_matrix(self):
        a_constant = PropositionalConstant("a")
        b_constant = PropositionalConstant("b")
        negation_a = Negation(SimpleSentence(a_constant))
        vocab = PropositionalVocabulary([a_constant, b_constant])
        table = TruthTable(vocab, [negation_a])

        result = table.matrix

        self.assertEqual([
            [SimpleSentence(a_constant), True, True, False, False],
            [SimpleSentence(b_constant), True, False, True, False],
            [negation_a, False, False, True, True]
        ], result)
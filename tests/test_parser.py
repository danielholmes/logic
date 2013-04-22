from unittest import TestCase
from utils import data_provider
from logic.syntax import *
from logic.language import *
from logic.parser import *

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
        ),
        (
            Equivalence(
                SimpleSentence(PropositionalConstant("a")),
                Disjunction(
                    SimpleSentence(PropositionalConstant("b")),
                    Conjunction(
                        SimpleSentence(PropositionalConstant("c")),
                        Negation(SimpleSentence(PropositionalConstant("d")))
                    )
                )
            ),
            "a <=> b | c ^ -d"
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
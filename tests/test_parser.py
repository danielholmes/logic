from unittest import TestCase
from utils import data_provider
from logic.syntax import *
from logic.language import *
from logic.parser import *

class TokeniseTest(TestCase):
    valid_data_provider = lambda: (
        ((ConstantToken("a"), EndToken()), "a"),
        ((ConstantToken("a_b"), EndToken()), "a_b"),
        ((NegationToken(), EndToken()), "-"),
        ((ConjunctionToken(), EndToken()), "^"),
        ((DisjunctionToken(), EndToken()), "|"),
        ((EquivalenceToken(), EndToken()), "<=>"),
        ((ImplicationToken(), EndToken()), "=>"),
        ((ReductionToken(), EndToken()), "<="),
        ((LeftParenthesisToken(), EndToken()), "("),
        ((RightParenthesisToken(), EndToken()), ")"),
        (
            (
                LeftParenthesisToken(),
                ConstantToken("a"),
                ConjunctionToken(),
                ConstantToken("b"),
                RightParenthesisToken(),
                EndToken()
            ),
            "(a ^ b)"
        ),
        ((ConstantToken("a"), EndToken()), "  \ta\n  ")
    )

    @data_provider(valid_data_provider)
    def test_tokenise(self, expected, program):
        result = tokenise(program)

        self.assertEqual(expected, result)

    invalid_data_provider = lambda: (
        ("&", ),
        ("   &   ", ),
        ("UpperConstant", ),
        ("4numConstant", ),
        ("123", )
    )

    @data_provider(invalid_data_provider)
    def test_tokenise_invalid(self, program):
        with self.assertRaises(TokenisationError):
            tokenise(program)

class ParseProgramTest(TestCase):
    valid_data_provider = lambda: (
        (SimpleSentence(PropositionalConstant("a")), tokenise("a")),
        (Negation(SimpleSentence(PropositionalConstant("var"))), tokenise("-var")),
        (
            Conjunction(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), 
            tokenise("one^two")
        ),
        (
            Disjunction(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), 
            tokenise("one|two")
        ),
        (
            Equivalence(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), 
            tokenise("one<=>two")
        ),
        (
            Implication(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), 
            tokenise("one=>two")
        ),
        (
            Reduction(SimpleSentence(PropositionalConstant("one")), SimpleSentence(PropositionalConstant("two"))), 
            tokenise("one<=two")
        ),
        (SimpleSentence(PropositionalConstant("abc")), tokenise("(abc)")),
        (
            Conjunction(
                Conjunction(
                    SimpleSentence(PropositionalConstant("abc")), 
                    SimpleSentence(PropositionalConstant("def"))
                ),
                SimpleSentence(PropositionalConstant("ghi"))
            ), 
            tokenise("abc^def^ghi")
        ),
        (
            Conjunction(
                SimpleSentence(PropositionalConstant("abc")), 
                Conjunction(
                    SimpleSentence(PropositionalConstant("def")),
                    SimpleSentence(PropositionalConstant("ghi"))
                )
            ), 
            tokenise("abc^(def^ghi)")
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
            tokenise("a <=> b | c ^ -d")
        )
    )

    @data_provider(valid_data_provider)
    def test_valid_expressions(self, expected, tokens):
        expression = parse_program(tokens)

        self.assertEqual(expected, expression)
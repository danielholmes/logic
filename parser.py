# With help from http://effbot.org/zone/simple-top-down-parsing.htm

from language import *
from syntax import *
import re

def parse(program):
    parser = Parser()
    return parser(program)

class ParsingError(Exception):
    pass

class SyntaxError(ParsingError):
    pass

class Parser:
    token_pat = re.compile("\s*(?:([a-z]{1}[a-zA-Z\_0-9]*)|(\-|\^|\||\<\=\>|\=\>|\<\=|\(|\)))")

    def __call__(self, program):
        self.stream = self.tokenise(program)
        self.token = next(self.stream)
        if self.token.__class__ == EndToken:
            raise ParsingError("Empty expression")
        return self.expression()

    def expression(self, rbp = 0):
        t = self.token
        self.token = next(self.stream)
        left = t.nud(self)
        while rbp < self.token.priority:
            t = self.token
            self.token = next(self.stream)
            left = t.led(self, left)
        return left

    def advance(self, token_type):
        if self.token.__class__ != token_type:
            raise SyntaxError("Expected %r" % token_type.__name__)
        self.token = next(self.stream)

    def tokenise(self, program):
        for literal_value, operator in Parser.token_pat.findall(program):
            if literal_value:
                yield ConstantToken(literal_value)
            elif operator == "-":
                yield NegationToken()
            elif operator == "^":
                yield ConjunctionToken()
            elif operator == "|":
                yield DisjunctionToken()
            elif operator == "<=>":
                yield EquivalenceToken()
            elif operator == "=>":
                yield ImplicationToken()
            elif operator == "<=":
                yield ReductionToken()
            elif operator == "(":
                yield LeftParenthesisToken()
            elif operator == ")":
                yield RightParenthesisToken()
            else:
                raise SyntaxError("Unknown operator to tokenise %s" % operator)
        yield EndToken()

class TokenPriority:
    LEVEL_1 = 100
    LEVEL_2 = 80
    LEVEL_3 = 60
    LEVEL_4 = 40
    LEVEL_5 = 20
    LEVEL_6 = 0

class AbstractToken:
    def nud(self, parser):
        raise SyntaxError(
            "Syntax error (%r)." % self
        )

    def led(self, parser, left):
        raise SyntaxError(
            "Unknown operator (%r)." % self
        )

class LeftParenthesisToken(AbstractToken):
    priority = TokenPriority.LEVEL_6

    def nud(self, parser):
        expr = parser.expression()
        parser.advance(RightParenthesisToken)
        return expr

class RightParenthesisToken(AbstractToken):
    priority = TokenPriority.LEVEL_6

class ConstantToken(AbstractToken):
    priority = TokenPriority.LEVEL_1

    def __init__(self, value):
        self.value = value

    def nud(self, parser):
        return SimpleSentence(PropositionalConstant(self.value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class EndToken(AbstractToken):
    priority = TokenPriority.LEVEL_6

class NegationToken(AbstractToken):
    priority = TokenPriority.LEVEL_2

    def nud(self, parser):
        return Negation(parser.expression(TokenPriority.LEVEL_2))

class ConjunctionToken(AbstractToken):
    priority = TokenPriority.LEVEL_3

    def led(self, parser, left):
        return Conjunction(left, parser.expression(TokenPriority.LEVEL_3))

class DisjunctionToken(AbstractToken):
    priority = TokenPriority.LEVEL_4

    def led(self, parser, left):
        return Disjunction(left, parser.expression(TokenPriority.LEVEL_4))

class EquivalenceToken(AbstractToken):
    priority = TokenPriority.LEVEL_5

    def led(self, parser, left):
        return Equivalence(left, parser.expression(TokenPriority.LEVEL_5))

class ImplicationToken(AbstractToken):
    priority = TokenPriority.LEVEL_5

    def led(self, parser, left):
        return Implication(left, parser.expression(TokenPriority.LEVEL_5))

class ReductionToken(AbstractToken):
    priority = TokenPriority.LEVEL_5

    def led(self, parser, left):
        return Reduction(left, parser.expression(TokenPriority.LEVEL_5))
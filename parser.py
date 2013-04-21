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
        self.next = self.tokenise(program).next
        self.token = self.next()
        if self.token.__class__ == EndToken:
            raise ParsingError("Empty expression")
        return self.expression()

    def expression(self, rbp = 0):
        t = self.token
        self.token = self.next()
        left = t.nud(self)
        while rbp < self.token.priority:
            t = self.token
            self.token = self.next()
            left = t.led(self, left)
        return left

    def advance(self, token_type):
        if self.token.__class__ != token_type:
            raise SyntaxError("Expected %r" % token_type.__name__)
        self.token = self.next()

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
    priority = 0

    def nud(self, parser):
        expr = parser.expression()
        parser.advance(RightParenthesisToken)
        return expr

class RightParenthesisToken(AbstractToken):
    priority = 0

class ConstantToken(AbstractToken):
    priority = 100

    def __init__(self, value):
        self.value = value

    def nud(self, parser):
        return SimpleSentence(PropositionalConstant(self.value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class EndToken(AbstractToken):
    priority = 0

class NegationToken(AbstractToken):
    priority = 50

    def nud(self, parser):
        return Negation(parser.expression(100))

class ConjunctionToken(AbstractToken):
    priority = 40

    def led(self, parser, left):
        return Conjunction(left, parser.expression(40))

class DisjunctionToken(AbstractToken):
    priority = 40

    def led(self, parser, left):
        return Disjunction(left, parser.expression(40))

class EquivalenceToken(AbstractToken):
    priority = 20

    def led(self, parser, left):
        return Equivalence(left, parser.expression(20))

class ImplicationToken(AbstractToken):
    priority = 20

    def led(self, parser, left):
        return Implication(left, parser.expression(20))

class ReductionToken(AbstractToken):
    priority = 20

    def led(self, parser, left):
        return Reduction(left, parser.expression(20))
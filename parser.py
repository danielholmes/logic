# With help from http://effbot.org/zone/simple-top-down-parsing.htm

from language import *
from syntax import *
from abc import ABCMeta, abstractproperty
import re

def parse(program):
    parser = Parser()
    return parser(program)

class ParsingError(Exception):
    pass

class SyntaxError(ParsingError):
    pass

class Parser(object):
    TOKEN_PATTERN = re.compile("\s*(?:([a-z]{1}[a-zA-Z\_0-9]*)|(\-|\^|\||\<\=\>|\=\>|\<\=|\(|\)))")

    def __call__(self, program):
        self.stream = self.tokenise(program)
        self.token = next(self.stream)
        if self.token.__class__ == EndToken:
            raise ParsingError("Empty expression")
        return self.expression()

    def expression(self, right_binding_power = 0):
        current_token = self.token
        self.token = next(self.stream)
        left = current_token.create_prefixed_expression(self)
        while right_binding_power < self.token.binding_power:
            current_token = self.token
            self.token = next(self.stream)
            left = current_token.create_inside_expression(self, left)
        return left

    def advance(self, token_type):
        if self.token.__class__ != token_type:
            raise SyntaxError("Expected %r" % token_type.__name__)
        self.token = next(self.stream)

    def tokenise(self, program):
        for literal_value, operator in Parser.TOKEN_PATTERN.findall(program):
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

class TokenBindingPower(object):
    LEVEL_1 = 100
    LEVEL_2 = 80
    LEVEL_3 = 60
    LEVEL_4 = 40
    LEVEL_5 = 20
    LEVEL_6 = 0

class AbstractToken(object):
    __metaclass__ = ABCMeta

    def create_prefixed_expression(self, parser):
        raise SyntaxError(
            "Syntax error (%r)." % self
        )

    def create_inside_expression(self, parser, left):
        raise SyntaxError(
            "Unknown operator (%r)." % self
        )

    @abstractproperty
    def binding_power(self):
        pass

class LeftParenthesisToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_6

    def create_prefixed_expression(self, parser):
        expr = parser.expression()
        parser.advance(RightParenthesisToken)
        return expr

class RightParenthesisToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_6

class ConstantToken(AbstractToken):
    def __init__(self, value):
        self.value = value

    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_1

    def create_prefixed_expression(self, parser):
        return SimpleSentence(PropositionalConstant(self.value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class NegationToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_2

    def create_prefixed_expression(self, parser):
        return Negation(parser.expression(self.binding_power))

class ConjunctionToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_3

    def create_inside_expression(self, parser, left):
        return Conjunction(left, parser.expression(self.binding_power))

class DisjunctionToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_4

    def create_inside_expression(self, parser, left):
        return Disjunction(left, parser.expression(self.binding_power))

class EquivalenceToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, left):
        return Equivalence(left, parser.expression(self.binding_power))

class ImplicationToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, left):
        return Implication(left, parser.expression(self.binding_power))

class ReductionToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, left):
        return Reduction(left, parser.expression(self.binding_power))

class EndToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_6
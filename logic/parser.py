# With help from http://effbot.org/zone/simple-top-down-parsing.htm

from abc import ABCMeta, abstractproperty
import re
from logic.language import *
from logic.syntax import *

def parse(program):
    parser = Parser()
    return parser(program)

class ParsingError(Exception):
    pass

class ParsingSyntaxError(ParsingError):
    pass

class Parser(object):
    TOKEN_PATTERN = re.compile("\s*(?:([a-z]{1}[a-zA-Z\_0-9]*)|(\-|\^|\||\<\=\>|\=\>|\<\=|\(|\)))")

    def __call__(self, program):
        stream = self.tokenise(program)
        initial_state = ParseState(stream)
        if initial_state.token.__class__ == EndToken:
            raise ParsingError("Empty expression")

        return self.expression(initial_state)

    def expression(self, previous_state, right_binding_power = 0):
        current_state = previous_state.next()

        # TODO: Remove
        self.state = current_state

        left = previous_state.token.create_prefixed_expression(self, current_state)
        while right_binding_power < self.state.binding_power:
            previous_token = self.state.token

            current_state = previous_state.next(left)

            # TODO: Remove
            self.state = current_state

            left = previous_token.create_inside_expression(self, current_state)

        return left

    def advance(self, state, token_type):
        if self.state.token.__class__ != token_type:
            raise ParsingSyntaxError("Expected %r" % token_type.__name__)
        self.state = state.next()

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
                raise ParsingSyntaxError("Unknown operator to tokenise %s" % operator)
        yield EndToken()

class ParseState(object):
    def __init__(self, stream, left = None):
        self._token = next(stream)
        self._stream = stream
        self._left = left

    @property
    def token(self):
        return self._token

    @property
    def binding_power(self):
        return self.token.binding_power

    @property
    def left(self):
        return self._left

    @property
    def stream(self):
        return self._stream

    def next(self, left = None):
        return ParseState(self._stream, left)

class TokenBindingPower(object):
    LEVEL_1 = 100
    LEVEL_2 = 80
    LEVEL_3 = 60
    LEVEL_4 = 40
    LEVEL_5 = 20
    LEVEL_6 = 0

class AbstractToken(object):
    __metaclass__ = ABCMeta

    def create_prefixed_expression(self, parser, state):
        raise ParsingSyntaxError(
            "Syntax error (%r)." % self
        )

    def create_inside_expression(self, parser, state):
        raise ParsingSyntaxError(
            "Unknown operator (%r)." % self
        )

    @abstractproperty
    def binding_power(self):
        pass

class LeftParenthesisToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_6

    def create_prefixed_expression(self, parser, state):
        expr = parser.expression(state)
        parser.advance(state, RightParenthesisToken)
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

    def create_prefixed_expression(self, parser, state):
        return SimpleSentence(PropositionalConstant(self.value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class NegationToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_2

    def create_prefixed_expression(self, parser, state):
        return Negation(parser.expression(state, self.binding_power))

class ConjunctionToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_3

    def create_inside_expression(self, parser, state):
        return Conjunction(state.left, parser.expression(state, self.binding_power))

class DisjunctionToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_4

    def create_inside_expression(self, parser, state):
        return Disjunction(state.left, parser.expression(state, self.binding_power))

class EquivalenceToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, state):
        return Equivalence(state.left, parser.expression(state, self.binding_power))

class ImplicationToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, state):
        return Implication(state.left, parser.expression(state, self.binding_power))

class ReductionToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, state):
        return Reduction(state.left, parser.expression(state, self.binding_power))

class EndToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_6
# With help from http://effbot.org/zone/simple-top-down-parsing.htm

from abc import ABCMeta, abstractproperty
import re
from collections import OrderedDict
from logic.language import *
from logic.syntax import *

def parse(text):
    return parse_program(tokenise(text))

def parse_program(tokens):
    parser = Parser()
    return parser(tokens)

def tokenise(text):
    token_pattern = r"""
(?P<constant>[a-z]{1}[a-zA-Z0-9\_]*)
|(?P<negation>\-{1})
|(?P<conjunction>\^{1})
|(?P<disjunction>\|{1})
|(?P<equivalence>\<\=\>{1})
|(?P<implication>\=\>{1})
|(?P<reduction>\<\={1})
|(?P<left_parenthesis>\({1})
|(?P<right_parenthesis>\){1})
|(?P<invalid>[^\s]+)
"""

    token_re = re.compile(token_pattern, re.VERBOSE)
    return tuple([
        create_token(m.lastgroup, m.group(m.lastgroup), m.start(m.lastgroup))
        for m in re.finditer(token_pattern, text, re.VERBOSE)
    ] + [EndToken()])

def create_token(token_type, value, position):
    if token_type == 'constant':
        return ConstantToken(value)
    elif token_type == 'negation':
        return NegationToken()
    elif token_type == 'conjunction':
        return ConjunctionToken()
    elif token_type == 'disjunction':
        return DisjunctionToken()
    elif token_type == 'equivalence':
        return EquivalenceToken()
    elif token_type == 'implication':
        return ImplicationToken()
    elif token_type == 'reduction':
        return ReductionToken()
    elif token_type == 'left_parenthesis':
        return LeftParenthesisToken()
    elif token_type == 'right_parenthesis':
        return RightParenthesisToken()
    else:
        raise TokenisationError("Unrecognised token: %s > %r at position %s" % (token_type, value, position))

class ParsingError(Exception): pass

class TokenisationError(ParsingError): pass

class ParsingSyntaxError(ParsingError): pass

class Parser(object):
    def __call__(self, tokens):
        initial_state = ParseState(tokens)
        if initial_state.is_end:
            raise ParsingError("Empty expression")

        return self.expression(initial_state)

    def expression(self, previous_state, right_binding_power = 0):
        current_state = previous_state.next()

        # TODO: Remove
        self.state = current_state

        prefixed_state = previous_state.token.create_prefixed_expression(self, current_state)
        left = prefixed_state.left

        while right_binding_power < self.state.binding_power:
            previous_state = self.state

            current_state = previous_state.next(left)

            # TODO: Remove
            self.state = current_state

            left = previous_state.token.create_inside_expression(self, current_state)

        return left

class ParseState(object):
    def __init__(self, tokens, left = None):
        self._left = left
        self._token = tokens[0]
        self._remaining_tokens = tokens[1:]

    @property
    def token(self):
        return self._token

    def has_token_type(self, token_type):
        return self._token.__class__ == token_type

    @property
    def is_end(self):
        return self.has_token_type(EndToken)

    @property
    def binding_power(self):
        return self._token.binding_power

    @property
    def left(self):
        return self._left

    def next(self, left = None):
        if len(self._remaining_tokens) == 0:
            # A massive hack, to be removed when parsing sorted out
            # raise ParsingSyntaxError("No more tokens")
            return ParseState(tuple([EndToken()]), left)
        else:
            return ParseState(self._remaining_tokens, left)

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self._token, self._remaining_tokens, self.left)

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

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    def __eq__(self, other):
        return self.__class__ == other.__class__

class LeftParenthesisToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_6

    def create_prefixed_expression(self, parser, state):
        expr = parser.expression(state)
        if not parser.state.has_token_type(RightParenthesisToken):
            raise ParsingSyntaxError("Expected %s" % RightParenthesisToken.__name__)
        
        # NOTE: parser.expression could do all sorts of parser.state transformations, 
        # so using state argument from above is really unreliable
        # TODO: Should be returning this state
        parser.state = parser.state.next()
        #print("\nLEFTR")
        #print(parser.state)
        #print(state.next().next(expr))

        return state.next(expr)

    def __str__(self):
        return "("

class RightParenthesisToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_6

    def __str__(self):
        return ")"

class ConstantToken(AbstractToken):
    def __init__(self, value):
        self._value = value

    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_1

    @property
    def value(self):
        return self._value

    def create_prefixed_expression(self, parser, state):
        return state.next(SimpleSentence(PropositionalConstant(self.value)))

    def __eq__(self, other):
        return super(self.__class__, self).__eq__(other) and self.value == other.value

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class NegationToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_2

    def create_prefixed_expression(self, parser, state):
        return state.next(Negation(parser.expression(state, self.binding_power)))

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

    def __str__(self):
        return "<=>"

class ImplicationToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, state):
        return Implication(state.left, parser.expression(state, self.binding_power))

    def __str__(self):
        return "=>"

class ReductionToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_inside_expression(self, parser, state):
        return Reduction(state.left, parser.expression(state, self.binding_power))

    def __str__(self):
        return "<="

class EndToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_6

    def __str__(self):
        return "(end)"
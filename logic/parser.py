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
        raw_tokens = Parser.TOKEN_PATTERN.findall(program)
        initial_state = ParseState(raw_tokens)
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
        self._remaining_tokens = tokens[1:]

        parsed_token = None
        if len(tokens) == 0:
            self._token = EndToken()
        else:
            self._token = self.create_token(tokens[0])

    def create_token(self, raw_token):
        literal_value, operator = raw_token
        if literal_value:
            return ConstantToken(literal_value)
        elif operator == "-":
            return NegationToken()
        elif operator == "^":
            return ConjunctionToken()
        elif operator == "|":
            return DisjunctionToken()
        elif operator == "<=>":
            return EquivalenceToken()
        elif operator == "=>":
            return ImplicationToken()
        elif operator == "<=":
            return ReductionToken()
        elif operator == "(":
            return LeftParenthesisToken()
        elif operator == ")":
            return RightParenthesisToken()
        else:
            raise ParsingSyntaxError("Unknown operator to tokenise %s" % operator)

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
        return super.__eq__(self, other) and self.value == other.value

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
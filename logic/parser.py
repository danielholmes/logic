# Main help from http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
# also see http://effbot.org/zone/simple-top-down-parsing.htm

from abc import ABCMeta, abstractproperty, abstractmethod
import re
from logic.language import PropositionalConstant
from logic.syntax import SimpleSentence, Negation, Conjunction, Disjunction, \
    Equivalence, Implication, Reduction

def parse(text):
    return parse_program(tokenise(text))

def parse_program(tokens):
    initial_state = ParseState(tokens, [SentinelToken()], [])
    if initial_state.next_token == EndToken():
        raise ParsingError("Empty expression")
    expression_state = expression(initial_state)
    completed_state = expect(expression_state, EndToken()) 
    return completed_state.next_operand

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
    return tuple([
        create_token(m.lastgroup, m.group(m.lastgroup), m.start(m.lastgroup))
        for m in re.finditer(token_pattern, text, re.VERBOSE)
    ] + [EndToken()])

def create_token(token_type, value, position):
    simple_type_map = {
        "negation": NegationToken,
        "conjunction": ConjunctionToken,
        "disjunction": DisjunctionToken,
        "equivalence": EquivalenceToken,
        "implication": ImplicationToken,
        "reduction": ReductionToken,
        "left_parenthesis": ImplicationToken,
        "right_parenthesis": RightParenthesisToken
    }

    constructor = simple_type_map.get(token_type)
    if constructor is not None:
        return constructor()
    elif token_type == 'constant':
        return ConstantToken(value)
    else:
        raise TokenisationError(
            "Unrecognised token: %s > %r at position %s" % 
            (token_type, value, position)
        )

class ParsingError(Exception):
    pass

class TokenisationError(ParsingError):
    pass

class ParsingSyntaxError(ParsingError):
    pass

class ParseState(object):
    def __init__(self, tokens, operators, operands):
        self._tokens = tuple(tokens)
        self._operators = tuple(operators)
        self._operands = tuple(operands)

    @property
    def next_token(self):
        assert len(self._tokens) > 0, "No tokens left"
        return self._tokens[0]

    @property
    def next_operand(self):
        assert len(self._operands) > 0, "No operands left"
        return self._operands[0]

    @property
    def next_operator(self):
        assert len(self._operators) > 0, "No operators left"
        return self._operators[0]

    def next_operands(self, amount):
        return tuple(self._operands)[:amount]

    def pop_operand(self):
        return self.pop_operands(1)

    def pop_operands(self, amount):
        new_operands = self._operands[amount:]
        return ParseState(self._tokens, self._operators, new_operands)

    def pop_operator(self):
        return ParseState(self._tokens, self._operators[1:], self._operands)

    def push_operator(self, operator):
        new_operators = (operator, ) + self._operators
        return ParseState(self._tokens, new_operators, self._operands)

    def push_operand(self, operand):
        new_operands = (operand, ) + self._operands
        return ParseState(self._tokens, self._operators, new_operands)

    def consume_token(self):
        return ParseState(self._tokens[1:], self._operators, self._operands)

def expression(state):
    state = progress(state)
    while state.next_token.is_binary:
        state = push_operator(state.next_token, state)
        state = progress(state.consume_token())

    more_tokens = True
    while more_tokens:
        if state.next_operator == SentinelToken():
            more_tokens = False
        else:
            state = pop_operator(state)

    return state

def progress(state):
    if "create_value_sentence" in dir(state.next_token):
        state = state.push_operand(state.next_token.create_value_sentence())
        state = state.consume_token()
    elif state.next_token == LeftParenthesisToken():
        state = state.consume_token()
        state = state.push_operator(SentinelToken())
        state = expression(state)
        state = expect(state, RightParenthesisToken())
        state = state.pop_operator()
    elif state.next_token.is_unary:
        state = push_operator(state.next_token, state)
        state = state.consume_token()
        state = progress(state)
    else:
        raise Exception("Parsing issue with token %r" % state.next_token)

    return state

def expect(state, token):
    if state.next_token != token:
        raise Exception("Expected %r got %r" % (token, state.next_token))
    return state.consume_token()

def pop_operator(state):
    operator = state.next_operator
    state = state.pop_operator()
    if operator.is_binary:
        right, left = state.next_operands(2)
        state = state.pop_operands(2)
        state = state.push_operand(operator.create_binary_sentence(left, right))
    elif operator.is_unary:
        next_operand = state.next_operand
        state = state.pop_operand()
        state = state.push_operand(operator.create_unary_sentence(next_operand))
    else:
        raise Exception("Request a pop of a non-operator %r" % operator)
    return state

def push_operator(operator, state):
    while state.next_operator.binding_power >= operator.binding_power:
        state = pop_operator(state)
    return state.push_operator(operator)

class TokenBindingPower(object):
    LEVEL_1 = 100
    LEVEL_2 = 80
    LEVEL_3 = 60
    LEVEL_4 = 40
    LEVEL_5 = 20
    LEVEL_6 = 0
    LEVEL_LOWEST = -9999

class AbstractToken(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def binding_power(self):
        pass

    @property
    def is_binary(self):
        return False

    @property
    def is_unary(self):
        return False

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

class SentinelToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_LOWEST

class LeftParenthesisToken(AbstractToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_6

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

    def create_value_sentence(self):
        return SimpleSentence(PropositionalConstant(self._value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._value)

class NegationToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_2

    def create_unary_sentence(self, target):
        return Negation(target)

    @property
    def is_unary(self):
        return True

class BinaryOperationToken(AbstractToken):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_binary_sentence(self, left, right):
        pass

    @property
    def is_binary(self):
        return True

class ConjunctionToken(BinaryOperationToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_3

    def create_binary_sentence(self, left, right):
        return Conjunction(left, right)

class DisjunctionToken(BinaryOperationToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_4

    def create_binary_sentence(self, left, right):
        return Disjunction(left, right)

class EquivalenceToken(BinaryOperationToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_binary_sentence(self, left, right):
        return Equivalence(left, right)

    def __str__(self):
        return "<=>"

class ImplicationToken(BinaryOperationToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_binary_sentence(self, left, right):
        return Implication(left, right)

    def __str__(self):
        return "=>"

class ReductionToken(BinaryOperationToken):
    @property
    def binding_power(self):
        return TokenBindingPower.LEVEL_5

    def create_binary_sentence(self, left, right):
        return Reduction(left, right)

    def __str__(self):
        return "<="

class EndToken(AbstractToken):
    @property
    def binding_power(self):
        return  TokenBindingPower.LEVEL_6

    def __str__(self):
        return "(end)"
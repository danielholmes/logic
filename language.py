import re

class PropositionalVocabulary:
    def __init__(self, constants):
        self._constants = frozenset(constants)

    @property
    def all_assignments(self):
        def get_next(remaining_constants, accu):
            if len(remaining_constants) == 0:
                return accu
            else:
                head = remaining_constants[0]
                tail = remaining_constants[1:]
                true_ass = TruthAssignment({head : True})
                false_ass = TruthAssignment({head : False})
                if len(accu) == 0:
                    return get_next(tail, frozenset([true_ass, false_ass]))
                else:
                    return get_next(tail, append_new(accu, true_ass, false_ass, frozenset()))

        def append_new(current, add_1, add_2, accu):
            if len(current) == 0:
                return accu
            else:
                current_list = list(current)
                head = current_list[0]
                tail = frozenset(current_list[1:])
                new_accu = accu.union((head + add_1, head + add_2))
                return append_new(tail, add_1, add_2, new_accu)

        return get_next(tuple(self._constants), frozenset())

    @property
    def constants(self):
        return self._constants

    @staticmethod
    def from_constant_names(names):
        constants = map(PropositionalConstant, names)
        return PropositionalVocabulary(constants)

    def __add__(self, other):
        return PropositionalVocabulary(self.constants.union(other.constants))

    def __eq__(self, other):
        return self.constants == other.constants

    def __str__(self):
        return str(sorted(self.constants.keys()))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, map(repr, self.constants))

class PropositionalConstant:
    def __init__(self, label):
        if not isinstance(label, str):
            raise InvalidConstantLabelException('Must be a string')

        if len(label) == 0:
            raise InvalidConstantLabelException('Empty label')

        if not label[0].islower():
            raise InvalidConstantLabelException('First letter must be lower case')

        if not re.match('^[a-zA-Z\_0-9]+$', label):
            raise InvalidConstantLabelException('Can only be letters, numbers and _')

        self._label = label

    @property
    def label(self):
        return self._label

    def __eq__(self, other):
        return self.label == other.label

    def __gt__(self, other):
        return self.label > other.label

    def __hash__(self):
        return hash(self.label)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._label)

    def __str__(self):
        return self.label

class InvalidConstantLabelException(BaseException):
    pass

class TruthAssignment:
    def __init__(self, constants_to_value):
        # TODO: assert values are boolean
        self._constants_to_value = constants_to_value

    @property
    def constants_to_value(self):
        return self._constants_to_value

    @property
    def constants(self):
        return self.constants_to_value.keys()

    def get(self, constant):
        return self._constants_to_value.get(constant)

    def __add__(self, other):
        combined = self._constants_to_value.copy()
        combined.update(other.constants_to_value)
        return TruthAssignment(combined)

    def __delitem__(self, constant):
        self._constants_to_value.__delattr__(constant)

    def __getitem__(self, constant):
        self._constants_to_value.__getattribute__(constant)

    def __setitem__(self, constant, value):
        if not isinstance(value, bool):
            raise Exception('Value must be a boolean')
        self._constants_to_value.__setattr__(constant, value)

    def __eq__(self, other):
        return self.constants_to_value == other.constants_to_value

    def __gt__(self, other):
        keys = sorted(self.constants)
        other_keys = sorted(other.constants)
        values = [self.get(i) for i in keys]
        other_values = [other.get(i) for i in other_keys]
        return keys < other_keys or (keys == other_keys and values < other_values)

    def __repr__(self):
        return 'TruthAssignment(%r)' % self._constants_to_value

    def __hash__(self):
        return hash(frozenset(self._constants_to_value.items()))
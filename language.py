import re

class PropositionalVocabulary:
    def __init__(self, constants):
        self._constants = constants

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

class InvalidConstantLabelException(BaseException):
    pass
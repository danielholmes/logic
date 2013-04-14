from abc import ABCMeta, abstractmethod, abstractproperty
from language import PropositionalVocabulary

class Sentence:
    __metaclass__ = ABCMeta

    def is_logically_equivalent(self, other):
    	all_constants = other.all_constants.union(self.all_constants)
        vocab = PropositionalVocabulary(all_constants)
        for assignment in vocab.all_assignments:
        	if self.eval(assignment) != other.eval(assignment):
        		return False
        return True

    @property
    def all_constants(self):
        return frozenset([constant for constant in sub_sentence.all_constants for sub_sentence in self.sub_sentences])

    @abstractmethod
    def eval(self, assignment):
        pass

class SimpleSentence(Sentence):
    def __init__(self, constant):
        self._constant = constant

    @property
    def all_constants(self):
        return frozenset((self._constant, ))

    def eval(self, assignment):
        value = assignment.get(self._constant)
        if value is None:
            raise ConstantDoesntExistException('Constant %s not assigned' % self._constant.label)
        return value

class ConstantDoesntExistException(Exception):
    pass

class CompoundSentence(Sentence):
    __metaclass__ = ABCMeta

    @property
    def sub_sentences(self):
        return frozenset()

    @property
    def all_constants(self):
        return frozenset([constant for sub_sentence in self.sub_sentences for constant in sub_sentence.all_constants])

    @property
    def symbol(self):
        pass

class Negation(CompoundSentence):
    def __init__(self, target):
        self._target = target

    def eval(self, assignment):
        return not self._target.eval(assignment)

    @property
    def sub_sentences(self):
        return frozenset((self._target, ))

    @property
    def symbol(self):
        return '-'

class Conjunction(CompoundSentence):
    def __init__(self, conjunct_1, conjunct_2):
        self._conjunct_1 = conjunct_1
        self._conjunct_2 = conjunct_2

    def eval(self, assignment):
        return self._conjunct_1.eval(assignment) and self._conjunct_2.eval(assignment)
    
    @property
    def sub_sentences(self):
        return frozenset((self._conjunct_1, self._conjunct_2))

    @property
    def symbol(self):
        return '^'

class Disjunction(CompoundSentence):
    def __init__(self, disjunct_1, disjunct_2):
        self._disjunct_1 = disjunct_1
        self._disjunct_2 = disjunct_2

    def eval(self, assignment):
        return self._disjunct_1.eval(assignment) or self._disjunct_2.eval(assignment)
    
    @property
    def sub_sentences(self):
        return frozenset((self._disjunct_1, self._disjunct_2))

    @property
    def symbol(self):
        return 'v'

class Implication(CompoundSentence):
    def __init__(self, antecedent, consequent):
        self._antecedent = antecedent
        self._consequent = consequent

    def eval(self, assignment):
        return not self._antecedent.eval(assignment) or self._consequent.eval(assignment)
    
    @property
    def sub_sentences(self):
        return frozenset((self._antecedent, self._consequent))

    @property
    def symbol(self):
        return '=>'

class Reduction(CompoundSentence):
    def __init__(self, consequent, antecedent):
        self._consequent = consequent
        self._antecedent = antecedent

    def eval(self, assignment):
        return self._consequent.eval(assignment) or not self._antecedent.eval(assignment)
    
    @property
    def sub_sentences(self):
        return frozenset((self._consequent, self._antecedent))

    @property
    def symbol(self):
        return '<='

class Equivalence(CompoundSentence):
    def __init__(self, target_1, target_2):
        self._target_1 = target_1
        self._target_2 = target_2

    def eval(self, assignment):
        return self._target_1.eval(assignment) == self._target_2.eval(assignment)
    
    @property
    def sub_sentences(self):
        return frozenset((self._target_1, self._target_2))

    @property
    def symbol(self):
        return '<=>'
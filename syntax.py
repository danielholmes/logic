class Sentence:
    pass

class SimpleSentence(Sentence):
    def __init__(self, constant):
        self._constant = constant

class CompoundSentence(Sentence):
    @property
    def symbol(self):
        pass

class Negation(CompoundSentence):
    def __init__(self, target):
        self._target = target

    @property
    def symbol(self):
        return '-'

class Conjunction(CompoundSentence):
    def __init__(self, conjunct1, conjunct2):
        self._conjunct1 = conjunct1
        self._conjunct2 = conjunct2

    @property
    def symbol(self):
        return '^'

class Disjunction(CompoundSentence):
    def __init__(self, disjunct1, disjunct2):
        self._disjunct1 = disjunct1
        self._disjunct2 = disjunct2

    @property
    def symbol(self):
        return 'v'

class Implication(CompoundSentence):
    def __init__(self, antecedent, consequent):
        self._antecedent = antecedent
        self._consequent = consequent

    @property
    def symbol(self):
        return '=>'

class Reduction(CompoundSentence):
    def __init__(self, consequent, antecedent):
        self._consequent = consequent
        self._antecedent = antecedent

    @property
    def symbol(self):
        return '<='

class Equivalence(CompoundSentence):
    def __init__(self, target1, target2):
        self._target1 = target1
        self._target2 = target2

    @property
    def symbol(self):
        return '<=>'
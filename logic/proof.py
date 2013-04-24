from logic.syntax import Implication, Negation, SimpleSentence

class ImplicationElimination(object):
    def __init__(self, implication):
        self._implication = implication

    @property
    def implication(self):
        return self._implication

    @property
    def resulting_premise(self):
        return self.implication.consequent

    def __eq__(self, other):
        return (isinstance(other, type(self)) and 
            self._implication == other.implication)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.implication)

class ProofProblem(object):
    def __init__(self, premises, conclusion):
        self._premises = tuple(premises)
        self._conclusion = conclusion

    @property
    def conclusion(self):
        return self._conclusion

    @property
    def premises(self):
        return self._premises

class BruteForceMendelsonProver(object):
    def __call__(self, problem):
        if not self.is_valid_mendelson_sentence(problem.conclusion):
            raise InvalidMendelsonProblem(
                'Invalid Mendelson sentence in conclusion: %r' % problem.conclusion
            )
        
        for premise in problem.premises:
            if not self.is_valid_mendelson_sentence(premise):
                raise InvalidMendelsonProblem(
                    'Invalid Mendelson sentence in premise: %r' % premise
                )

        if problem.conclusion in problem.premises:
            return tuple()
        else:
            return self.find_best_solution(problem)

    def find_best_solution(self, problem):
        test_eliminations = [
            ImplicationElimination(p) 
            for p in problem.premises 
            if isinstance(p, Implication)
        ]

        return next((
            tuple([e])
            for e in test_eliminations 
            if e.resulting_premise == problem.conclusion
        ), tuple())

    def is_valid_mendelson_sentence(self, sentence):
        if sentence.__class__ not in (Implication, Negation, SimpleSentence):
            return False
        else:
            return all([
                self.is_valid_mendelson_sentence(sub_sentence) 
                for sub_sentence in sentence.sub_sentences
            ])

class InvalidMendelsonProblem(Exception):
    pass
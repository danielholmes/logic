from unittest import TestCase
from logic.syntax import Implication, SimpleSentence, Conjunction, Negation
from logic.language import PropositionalConstant
from logic.proof import BruteForceMendelsonProver, ProofProblem, \
    InvalidMendelsonProblem, ImplicationElimination, ImplicationCreation, \
    ImplicationDistribution, ContradictionRealisation
from utils import data_provider

class ContradictionRealisationTest(TestCase):
    def test_resulting_premise(self):
        sentence_a = SimpleSentence(PropositionalConstant("a"))
        sentence_b = SimpleSentence(PropositionalConstant("b"))
        creation = ContradictionRealisation(sentence_a, sentence_b)

        result = creation.resulting_premise

        expected = Implication(
            Implication(Negation(sentence_a), sentence_b),
            Implication(
                Implication(Negation(sentence_a), Negation(sentence_b)),
                sentence_a
            )
        )
        self.assertEqual(expected, result)

class ImplicationCreationTest(TestCase):
    def test_resulting_premise(self):
        sentence_a = SimpleSentence(PropositionalConstant("a"))
        sentence_b = SimpleSentence(PropositionalConstant("b"))
        creation = ImplicationCreation(sentence_a, sentence_b)

        result = creation.resulting_premise

        expected = Implication(
            sentence_a,
            Implication(sentence_b, sentence_a)
        )
        self.assertEqual(expected, result)

class ImplicationDistributionTest(TestCase):
    def test_resulting_premise(self):
        sentence_a = SimpleSentence(PropositionalConstant("a"))
        sentence_b = SimpleSentence(PropositionalConstant("b"))
        sentence_c = SimpleSentence(PropositionalConstant("c"))
        distribution = ImplicationDistribution(sentence_a, sentence_b, sentence_c)

        result = distribution.resulting_premise

        expected = Implication(
            Implication(sentence_a, Implication(sentence_b, sentence_c)),
            Implication(
                Implication(sentence_a, sentence_b),
                Implication(sentence_a, sentence_c)
            )
        )
        self.assertEqual(expected, result)

class BruteForceMendelsonProverTest(TestCase):
    def test_prove_already_proven(self):
        prover = BruteForceMendelsonProver()

        problem = ProofProblem(
            [SimpleSentence(PropositionalConstant("p"))], 
            SimpleSentence(PropositionalConstant("p"))
        )
        solution = prover(problem)

        self.assertEqual(tuple(), solution)

    invalid_mendelson_problem_data_provider = lambda: (
        (
            ProofProblem([
                    Conjunction(
                        SimpleSentence(PropositionalConstant("p")),
                        SimpleSentence(PropositionalConstant("q"))
                    )
                ], 
                SimpleSentence(PropositionalConstant("p"))
            ), 
        ),
        (
            ProofProblem([
                    Implication(
                        Conjunction(
                            SimpleSentence(PropositionalConstant("p")),
                            SimpleSentence(PropositionalConstant("q"))
                        ),
                        SimpleSentence(PropositionalConstant("p"))
                    )
                ], 
                SimpleSentence(PropositionalConstant("p"))
            ), 
        ),
        (
            ProofProblem(
                [SimpleSentence(PropositionalConstant("p"))], 
                Conjunction(
                    SimpleSentence(PropositionalConstant("p")),
                    SimpleSentence(PropositionalConstant("q"))
                )
            ), 
        )
    )

    @data_provider(invalid_mendelson_problem_data_provider)
    def test_prove_invalid_mendelson(self, problem):
        prover = BruteForceMendelsonProver()

        with self.assertRaises(InvalidMendelsonProblem):
            prover(problem)

    def test_prove_simple_implication_elimination(self):
        prover = BruteForceMendelsonProver()

        sentence_p = SimpleSentence(PropositionalConstant("p"))
        sentence_q = SimpleSentence(PropositionalConstant("q"))
        implication = Implication(sentence_p, sentence_q)
        problem = ProofProblem(
            [implication, sentence_p],
            sentence_q
        )
        solution = prover(problem)

        self.assertEqual(tuple([ImplicationElimination(implication)]), solution)

    def test_prove_medium_implication_elimination(self):
        prover = BruteForceMendelsonProver()

        sentence_p = SimpleSentence(PropositionalConstant("p"))
        sentence_q = SimpleSentence(PropositionalConstant("q"))
        implication = Implication(sentence_p, sentence_q)
        problem = ProofProblem(
            [
                Implication(sentence_q, sentence_p),
                Implication(sentence_q, Negation(sentence_p)),
                implication, 
                sentence_p
            ],
            sentence_q
        )
        solution = prover(problem)

        self.assertEqual(tuple([ImplicationElimination(implication)]), solution)
from language import PropositionalVocabulary, PropositionalConstant
from display import TruthTable
from parser import Parser

parser = Parser()
conjunction = parser("a^b")
disjunction = parser("a|b")

vocabulary = PropositionalVocabulary([
    PropositionalConstant("a"),
    PropositionalConstant("b")
])
table = TruthTable(vocabulary, [conjunction, disjunction])
print(table.simple_string)
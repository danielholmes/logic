from language import PropositionalVocabulary, PropositionalConstant
from display import TruthTable
from parser import parse

conjunction = parse("a^b")
disjunction = parse("a|b")

vocabulary = PropositionalVocabulary.from_constant_names(["a", "b"])
table = TruthTable(vocabulary, [conjunction, disjunction])
print(table.simple_string)
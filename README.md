Logic Formalisation
===================

[![Build Status](https://api.travis-ci.org/danielholmes/logic.png)](http://travis-ci.org/danielholmes/logic)

A library that formalises logic. I'm building this while undertaking an [Introduction to Logic](https://www.coursera.org/course/intrologic), 
so the implementation and understanding is a work in progress.

Running Tests
-------------
While the virtual environment is active:
``` python ./tests ```

Simple Example
--------------
```python
from logic.display import TruthTable
from logic.parser import parse

conjunction = parse("a^b")

table = TruthTable.for_sentences([conjunction])

print(table.simple_string)
```
Outputs:
```
+---+---+---------+
| a | b | (a ^ b) |
+---+---+---------+
| 1 | 1 |    1    |
| 1 | 0 |    0    |
| 0 | 1 |    0    |
| 0 | 0 |    0    |
+---+---+---------+
```

More Complex Example
--------------------
```python
from logic.display import TruthTable
from logic.parser import parse

conjunction = parse("a ^ b")
complex_expr = parse("d => (a ^ (b | c))")

logically_entails = conjunction.logically_entails(complex_expr)
logically_equivalent = conjunction.is_logically_equivalent(complex_expr)
table = TruthTable.for_sentences([conjunction, complex_expr])

print("Conjunction logically entails complex: %s" % logically_entails)
print("Conjunction is logically equivalent to complex: %s" % logically_equivalent)
print(table.simple_string)
```
Outputs:
```
Conjunction logically entails complex: True
Conjunction is logically equivalent to complex: False
+---+---+---+---+---------+----------------------+
| a | b | c | d | (a ^ b) | (d => (a ^ (b | c))) |
+---+---+---+---+---------+----------------------+
| 1 | 1 | 1 | 1 |    1    |          1           |
| 1 | 1 | 1 | 0 |    1    |          1           |
| 1 | 1 | 0 | 1 |    1    |          1           |
| 1 | 1 | 0 | 0 |    1    |          1           |
| 1 | 0 | 1 | 1 |    0    |          1           |
| 1 | 0 | 1 | 0 |    0    |          1           |
| 1 | 0 | 0 | 1 |    0    |          0           |
| 1 | 0 | 0 | 0 |    0    |          1           |
| 0 | 1 | 1 | 1 |    0    |          0           |
| 0 | 1 | 1 | 0 |    0    |          1           |
| 0 | 1 | 0 | 1 |    0    |          0           |
| 0 | 1 | 0 | 0 |    0    |          1           |
| 0 | 0 | 1 | 1 |    0    |          0           |
| 0 | 0 | 1 | 0 |    0    |          1           |
| 0 | 0 | 0 | 1 |    0    |          0           |
| 0 | 0 | 0 | 0 |    0    |          1           |
+---+---+---+---+---------+----------------------+
```

Todo
----
- Add properties of sentences: valid, contingent, unsatisfiable. Satisfiable, falsifiable
- Linear proofs - Mendelson System
    - brute force solver configurable for levels to search, etc
    - solver runs 4 rules in a brute force way, using a certain limit, then provides shortest proofs
    - Brute force solver is perhaps configurable by system
- Fitch System
- Structured proof solver (including Implication Introduction). Do structured proofs only have I.E. and I.I.?
- Linear proof renderer. Displays text list of premises to conclusion and the applied rule on the right
- An "efficient" renderer - showing parenthesis only where needed considering order of precedence
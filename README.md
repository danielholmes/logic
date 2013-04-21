Logic Formalisation
===================

[![Build Status](https://api.travis-ci.org/danielholmes/logic.png)](http://travis-ci.org/danielholmes/logic)

A library that formalises logic. I'm building this while undertaking an [Introduction to Logic](https://www.coursera.org/course/intrologic), 
so the implementation and understanding is a work in progress.

Running Tests
-------------
While the virtual environment is active:
``` python ./tests.py ```

Simple Example
--------------
```python
from display import TruthTable
from parser import parse

conjunction = parse("a^b")

table = TruthTable.from_sentences([conjunction])
print(table.simple_string)
```
Outputs:
```
+---+---+-------+
| a | b | a ^ b |
+---+---+-------+
| 1 | 1 |   1   |
| 1 | 0 |   0   |
| 0 | 1 |   0   |
| 0 | 0 |   0   |
+---+---+-------+
```

More Complex Example
--------------------
```python
from display import TruthTable
from parser import parse

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
+---+---+---+---+-------+----------------+
| a | b | c | d | a ^ b | d => a ^ b | c |
+---+---+---+---+-------+----------------+
| 1 | 1 | 1 | 1 |   1   |        1       |
| 1 | 1 | 1 | 0 |   1   |        1       |
| 1 | 1 | 0 | 1 |   1   |        1       |
| 1 | 1 | 0 | 0 |   1   |        1       |
| 1 | 0 | 1 | 1 |   0   |        1       |
| 1 | 0 | 1 | 0 |   0   |        1       |
| 1 | 0 | 0 | 1 |   0   |        0       |
| 1 | 0 | 0 | 0 |   0   |        1       |
| 0 | 1 | 1 | 1 |   0   |        0       |
| 0 | 1 | 1 | 0 |   0   |        1       |
| 0 | 1 | 0 | 1 |   0   |        0       |
| 0 | 1 | 0 | 0 |   0   |        1       |
| 0 | 0 | 1 | 1 |   0   |        0       |
| 0 | 0 | 1 | 0 |   0   |        1       |
| 0 | 0 | 0 | 1 |   0   |        0       |
| 0 | 0 | 0 | 0 |   0   |        1       |
+---+---+---+---+-------+----------------+
```
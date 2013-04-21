Logic Formalisation
===================

[![Build Status](https://api.travis-ci.org/danielholmes/logic.png)](http://travis-ci.org/danielholmes/logic)

A library that formalises logic. I'm building this while undertaking an [Introduction to Logic](https://www.coursera.org/course/intrologic), 
so the implementation and understanding is a work in progress.

Example Usage
-------------
See ``` example.py ```
```python
from language import PropositionalVocabulary, PropositionalConstant
from display import TruthTable
from parser import parse

conjunction = parse("a^b")
disjunction = parse("a|b")

vocabulary = PropositionalVocabulary.from_constant_names(["a", "b"])
table = TruthTable(vocabulary, [conjunction, disjunction])
print(table.simple_string)
```
Outputs:
```
+---+---+-------+-------+
| a | b | a ^ b | a | b |
+---+---+-------+-------+
| 1 | 1 |   1   |   1   |
| 1 | 0 |   0   |   1   |
| 0 | 1 |   0   |   1   |
| 0 | 0 |   0   |   0   |
+---+---+-------+-------+
```

Running Tests
-------------
While the virtual environment is active:
``` python ./tests.py ```

Todo
----
Sets of premises
Logical Entailment - set of premises logically entails a conclusion if every truth that satisfies the premise also satisfies the conclusion
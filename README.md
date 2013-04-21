Logic Formalisation
===================

[![Build Status](https://api.travis-ci.org/danielholmes/logic.png)](http://travis-ci.org/danielholmes/logic)

A library that formalises logic. I'm building this while undertaking an [Introduction to Logic](https://www.coursera.org/course/intrologic), 
so the implementation and understanding is a work in progress.

Example Usage
-------------
See ``` example1.py ```
```python
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
```
Outputs:
```
+---+---+-------+-------+
| a | b | a ^ b | a | b |
+---+---+-------+-------+
| 1 | 1 | 1     | 1     |
| 1 | 0 | 0     | 1     |
| 0 | 1 | 0     | 1     |
| 0 | 0 | 0     | 0     |
+---+---+-------+-------+
```

Development Environment
-----------------------
1. Create a virtual environment under the directory "env":
``` virtualenv env ```
2. Activate the environment
``` source env/bin/activate ```
3. Install the dependencies
``` pip install -r ./requirements.txt ```

Running Tests
-------------
While the virtual environment is active:
``` python ./tests.py ```
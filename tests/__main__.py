import sys
from os.path import realpath, abspath, dirname, join

sys.path = [realpath(join(dirname(abspath(__file__)), '..'))] + sys.path

import unittest
from test_language import *
from test_syntax import *
from test_parser import *
from test_display import *
from test_proof import *

if __name__ == '__main__':
    unittest.main()

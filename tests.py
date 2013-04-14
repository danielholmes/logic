import unittest
from language import PropositionalConstant, InvalidConstantLabelException
from unittest_data_provider import data_provider

class PropositionalConstantTest(unittest.TestCase):
    valid_labels_data_provider = lambda: (
        ('raining', ),
        ('rAiNiNg', ),
        ('r32aining', ),
        ('raining_or_snowing', )
    )

    @data_provider(valid_labels_data_provider)
    def test_valid_constant_labels(self, label):
        c = PropositionalConstant(label)

        self.assertEquals(label, c.label)

    invalid_labels_data_provider = lambda: (
        ('Raining', ),
        ('324567', ),
        (123, ),
        ('', ),
        ('raining-or-snowing', )
    )

    @data_provider(invalid_labels_data_provider)
    def test_invalid_constant_names(self, label):
        with self.assertRaises(InvalidConstantLabelException):
            PropositionalConstant(label)

if __name__ == '__main__':
    unittest.main()
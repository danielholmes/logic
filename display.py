from syntax import SimpleSentence, SentenceSet
from language import PropositionalVocabulary
from math import ceil, floor

class TruthTable:
    def __init__(self, vocabulary, sentences = []):
        self._vocabulary = vocabulary
        self._sentences = tuple(sentences)

    @property
    def simple_string(self):
        display_matrix = self.string_matrix

        col_sizes = [
            max(map(len, display_column))
            for display_column in display_matrix
        ]

        row_divider = "+"
        for col_size in col_sizes:
            row_divider += "-" + ("-" * col_size) + "-+"

        rows = [row_divider]
        num_rows = len(display_matrix[0])
        for row_num in range(0, num_rows):
            row_values = [display_column[row_num] for display_column in display_matrix]
            row_values_and_sizes = zip(row_values, col_sizes)
            padded_row_values = map(lambda x: x[0].center(x[1], " "), row_values_and_sizes)
            rows.append("| " + " | ".join(padded_row_values) + " |")
            if row_num == 0:
                rows.append(row_divider)
        rows.append(row_divider)
        return "\n".join(rows)

    @property
    def string_matrix(self):
        display_map = {True : '1', False : '0'}

        matrix = self.matrix
        headings = [str(column[0]) for column in matrix]
        all_raw_column_values = [column[1:] for column in matrix]
        all_display_column_values = [
            [display_map[raw_value] for raw_value in raw_column_values]
            for raw_column_values in all_raw_column_values
        ]
        return [
            [headings[i]] + all_display_column_values[i]
            for i in range(0, len(matrix))
        ]

    @property
    def matrix(self):
        constant_sentences = map(SimpleSentence, self._vocabulary.constants)
        all_sentences = sorted(constant_sentences) + list(self._sentences)
        table = [""] * len(all_sentences)

        sorted_assignments = sorted(self._vocabulary.all_assignments)
        for index, sentence in enumerate(all_sentences):
            assignment_column = [sentence.eval(assignment) for assignment in sorted_assignments]
            column = [sentence] + assignment_column
            table[index] = column

        return table

    @staticmethod
    def for_sentence_set(sentence_set):
        return TruthTable(sentence_set.vocabulary, sentence_set.sentences)

    @staticmethod
    def for_sentences(sentences):
        vocab = PropositionalVocabulary(SentenceSet(sentences).all_constants)
        return TruthTable(vocab, sentences)
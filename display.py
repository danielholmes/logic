from syntax import *

class TruthTable:
    def __init__(self, vocabulary, sentences = []):
        self._vocabulary = vocabulary
        self._sentences = frozenset(sentences)

    @property
    def simple_string(self):
        display_matrix = self.string_matrix

        col_sizes = [
            max(map(len, display_column))
            for display_column in display_matrix
        ]

        row_divider = reduce(lambda accu, x: accu + "-" + ("-" * x) + "-+", col_sizes, "+")

        rows = [row_divider]
        num_rows = len(display_matrix[0])
        for row_num in range(0, num_rows):
            row_values = [display_column[row_num] for display_column in display_matrix]
            padded_row_values = map(
                lambda x_enum: x_enum[1] + (" " * (col_sizes[x_enum[0]] - len(x_enum[1]))),
                enumerate(row_values)
            )
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
            map(display_map.get, raw_column_values)
            for raw_column_values in all_raw_column_values
        ]
        return [
            [headings[i]] + all_display_column_values[i]
            for i in range(0, len(matrix))
        ]

    @property
    def matrix(self):
        constant_sentences = frozenset(map(SimpleSentence, self._vocabulary.constants))
        all_sentences = sorted(constant_sentences) + list(self._sentences)
        table = [""] * len(all_sentences)

        for index, sentence in enumerate(all_sentences):
            assignment_column = [sentence.eval(assignment) for assignment in sorted(self._vocabulary.all_assignments)]
            column = [str(sentence)] + assignment_column
            table[index] = column

        return table
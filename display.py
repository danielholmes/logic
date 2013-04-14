from syntax import *

class TruthTable:
    def __init__(self, vocabulary, sentences = []):
        self._vocabulary = vocabulary
        self._sentences = frozenset(sentences)

    def simple_string(self):
        constant_sentences = frozenset(map(SimpleSentence, self._vocabulary.constants))
        all_sentences = sorted(constant_sentences) + list(self._sentences)
        rows = []
        display_map = {True : '1', False : '0'}
        for assignment in sorted(self._vocabulary.all_assignments):
            rows.append(' | '.join([display_map[sentence.eval(assignment)] for sentence in all_sentences]))
        return ' | '.join(map(str, all_sentences)) + "\n" + "\n".join(rows)
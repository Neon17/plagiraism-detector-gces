"""Tests for the TF-IDF baseline and the chunking helper.

The Sentence-BERT engine is not exercised here because loading the model needs the
downloaded weights; it is covered by the notebook and by manual testing instead.
"""
import unittest

from detector.services import similarity
from detector.services.preprocess import tokenize


def _matrix(*texts):
    return similarity.all_pairs_matrix(list(texts), method='tfidf')


class TfidfMatrixTest(unittest.TestCase):
    def test_document_is_identical_to_itself(self):
        matrix = _matrix('the student copied the report', 'a completely different text')
        self.assertAlmostEqual(matrix[0][0], 1.0, places=3)
        self.assertAlmostEqual(matrix[1][1], 1.0, places=3)

    def test_matrix_is_symmetric(self):
        matrix = _matrix('first document about plagiarism', 'second document about detection')
        self.assertAlmostEqual(matrix[0][1], matrix[1][0], places=6)

    def test_copied_text_scores_higher_than_unrelated_text(self):
        original = 'plagiarism detection compares documents and reports copied sentences'
        copied = 'plagiarism detection compares documents and reports copied sentences today'
        unrelated = 'the football match was postponed because of heavy rain'
        matrix = _matrix(original, copied, unrelated)
        self.assertGreater(matrix[0][1], matrix[0][2])

    def test_empty_documents_do_not_crash(self):
        matrix = _matrix('', '')
        self.assertEqual(len(matrix), 2)


class TokenizeForTfidfTest(unittest.TestCase):
    def test_engine_uses_preprocessed_tokens(self):
        engine = similarity.TfidfEngine([tokenize('copied report'), tokenize('copied report')])
        matrix = engine.matrix()
        self.assertAlmostEqual(matrix[0][1], 1.0, places=3)


class ChunkTextTest(unittest.TestCase):
    def test_long_document_is_split_into_chunks_of_five_sentences(self):
        text = ' '.join(f'This is sentence number {i} of the document.' for i in range(12))
        chunks = similarity.chunk_text(text)
        self.assertEqual(len(chunks), 3)          # 12 sentences -> 5 + 5 + 2

    def test_short_document_stays_in_one_chunk(self):
        self.assertEqual(len(similarity.chunk_text('One short sentence here.')), 1)

    def test_empty_document_gives_no_chunk(self):
        self.assertEqual(similarity.chunk_text('   '), [])


if __name__ == '__main__':
    unittest.main()

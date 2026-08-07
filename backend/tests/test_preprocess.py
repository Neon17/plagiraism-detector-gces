import unittest

from detector.services import preprocess


class CleanAndTokenizeTest(unittest.TestCase):
    def test_clean_lowercases_and_collapses_whitespace(self):
        self.assertEqual(preprocess.clean('  The   QUICK\n brown  '), 'the quick brown')

    def test_tokenize_drops_stopwords_and_single_characters(self):
        tokens = preprocess.tokenize('The student copied the whole report from a website')
        self.assertNotIn('the', tokens)
        self.assertNotIn('a', tokens)
        self.assertIn('student', tokens)
        self.assertIn('website', tokens)

    def test_tokenize_keeps_devanagari_words(self):
        tokens = preprocess.tokenize('विद्यार्थीले रिपोर्ट सारेको हो')
        self.assertIn('विद्यार्थीले', tokens)
        self.assertIn('रिपोर्ट', tokens)
        self.assertNotIn('हो', tokens)      # Nepali stopword


class SplitSentencesTest(unittest.TestCase):
    def test_splits_english_sentences(self):
        text = 'This is the first sentence. Here comes the second one! And a third one?'
        self.assertEqual(len(preprocess.split_sentences(text)), 3)

    def test_ignores_very_short_fragments(self):
        self.assertEqual(preprocess.split_sentences('Ok. Fine.'), [])

    def test_danda_ends_a_sentence_even_without_a_space(self):
        text = 'यो पहिलो वाक्य हो।यो दोस्रो वाक्य हो।'
        self.assertEqual(len(preprocess.split_sentences(text)), 2)

    def test_danda_with_a_space_also_works(self):
        text = 'यो पहिलो वाक्य हो। यो दोस्रो वाक्य हो।'
        self.assertEqual(len(preprocess.split_sentences(text)), 2)


class KeywordsTest(unittest.TestCase):
    def test_returns_the_most_frequent_content_words(self):
        text = ('plagiarism plagiarism plagiarism detection detection semantic '
                'the the the of of a an')
        found = preprocess.keywords(text, k=2)
        self.assertEqual(found[0], 'plagiarism')
        self.assertIn('detection', found)

    def test_respects_the_requested_count(self):
        self.assertLessEqual(len(preprocess.keywords('one two three four five six seven', k=3)), 3)


if __name__ == '__main__':
    unittest.main()

import unittest

from detector.services.text_extraction import extract_text, ocr_lang


class ExtractTextTest(unittest.TestCase):
    def test_reads_a_plain_text_file(self):
        text = extract_text('notes.txt', b'Hello from a text file.')
        self.assertEqual(text, 'Hello from a text file.')

    def test_reads_utf8_devanagari(self):
        text = extract_text('nepali.txt', 'यो नेपाली वाक्य हो।'.encode('utf-8'))
        self.assertIn('नेपाली', text)

    def test_empty_file_is_reported(self):
        with self.assertRaises(ValueError) as ctx:
            extract_text('empty.txt', b'')
        self.assertIn('empty', str(ctx.exception).lower())

    def test_unsupported_extension_is_reported(self):
        with self.assertRaises(ValueError) as ctx:
            extract_text('archive.zip', b'PK\x03\x04')
        self.assertIn('Unsupported', str(ctx.exception))

    def test_file_without_readable_text_is_reported(self):
        with self.assertRaises(ValueError) as ctx:
            extract_text('blank.txt', b'   \n  ')
        self.assertIn('No text', str(ctx.exception))

    def test_corrupt_file_does_not_raise_a_raw_exception(self):
        with self.assertRaises(ValueError):
            extract_text('broken.docx', b'this is not really a docx')


class OcrLanguageTest(unittest.TestCase):
    def test_language_string_is_english_or_english_plus_nepali(self):
        self.assertIn(ocr_lang(), ('eng', 'eng+nep'))


if __name__ == '__main__':
    unittest.main()

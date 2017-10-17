from unittest import TestCase
from unittest.mock import patch

from markovchain.text.util import (
    ispunct, lstrip_ws_and_chars, capitalize,
    format_sentence_string, format_sentence
)


class TestTextUtils(TestCase):
    def test_ispunct(self):
        self.assertTrue(ispunct('\'"?,+-.[]{}()<>'))
        self.assertFalse(ispunct('\'"?,+-x.[]{}()<>'))
        self.assertFalse(ispunct(''))

    def test_capitalize(self):
        self.assertEqual(capitalize('worD WORD WoRd'), 'Word word word')
        self.assertEqual(capitalize('x'), 'X')
        self.assertEqual(capitalize(''), '')

    def test_lstrip_ws_and_chars(self):
        self.assertEqual(lstrip_ws_and_chars('', ''), '')
        self.assertEqual(lstrip_ws_and_chars('     ', ''), '')
        self.assertEqual(lstrip_ws_and_chars('  x  ', 'xy'), '')
        self.assertEqual(lstrip_ws_and_chars(' \t.\n , .x. ', '.,?!'), 'x. ')

    def test_format_sentence_string(self):
        fmt = format_sentence_string
        self.assertEqual(fmt(''), '')
        self.assertEqual(fmt('  '), '')
        self.assertEqual(fmt('  ...'), '')
        self.assertEqual(fmt('.?!word'), 'Word.')
        self.assertEqual(fmt('word', default_end='/'), 'Word/')
        self.assertEqual(fmt('word', end_chars='d'), 'Word')
        self.assertEqual(fmt('word  ,  (word)..  word'), 'Word, (word).. word.')
        self.assertEqual(fmt('word,wo[rd..wo]rd'), 'Word, wo [rd.. wo] rd.')
        self.assertEqual(fmt('wo--*--rd'), 'Wo --*-- rd.')

    @patch('markovchain.text.util.format_sentence_string', return_value=1)
    def test_format_sentence(self, fmt):
        self.assertEqual(format_sentence('word'), 1)
        fmt.assert_called_with('word', '.?!', '.')
        fmt.reset_mock()

        self.assertEqual(
            format_sentence((str(x) for x in range(3)),
                            end_chars='/[', default_end='/'),
            1
        )
        fmt.assert_called_with('0 1 2', '/[', '/')
        fmt.reset_mock()

        self.assertEqual(
            format_sentence(['a', 'b', 'c'], join_with='.'),
            1
        )
        fmt.assert_called_with('a.b.c', '.?!', '.')
        fmt.reset_mock()

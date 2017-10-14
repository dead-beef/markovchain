from unittest import TestCase

from markovchain import Parser, LevelParser, Scanner
from markovchain.parser import ParserBase


class TestParser(TestCase):
    @staticmethod
    def parse(parser, scanner, data, part=False, separator=' '):
        return [(separator.join(src), dst)
                for src, dst in parser(scanner(data, part), part)]

    def test_properties(self):
        parser = Parser()

        with self.assertRaises(ValueError):
            parser.state_sizes = [1, 0, 2]
        with self.assertRaises(ValueError):
            parser.state_sizes = []
        self.assertEqual(parser.state_sizes, [1])
        self.assertEqual(parser.state_size, 1)

        parser.state_sizes = [2, 1]
        self.assertEqual(parser.state_sizes, [2, 1])
        self.assertEqual(parser.state_size, 2)
        self.assertEqual(parser.state.maxlen, 2)
        self.assertEqual(list(parser.state), ['', ''])

        parser.state.append('test')
        parser.state_size = parser.state_size
        self.assertEqual(list(parser.state), ['', 'test'])

        parser.state_sizes = [3]
        self.assertEqual(list(parser.state), ['', '', ''])

    def test_properties_parse(self):
        scanner = Scanner(lambda x: x)
        parser = Parser(state_sizes=[2],
                        reset_on_sentence_end=False)
        self.assertEqual(self.parse(parser, scanner, ['a', scanner.END, 'b'],
                                    True, '::'),
                         [('::', 'a'), ('::a', 'b')])
        self.assertEqual(self.parse(parser, scanner, 'c', separator='::'),
                         [('a::b', 'c')])

    def test_default_parse(self):
        scanner = Scanner(lambda x: x)
        parser = Parser()

        self.assertEqual(self.parse(parser, scanner, ''), [])

        self.assertEqual(self.parse(parser, scanner, 'abc', True),
                         [('', 'a'), ('a', 'b'), ('b', 'c')])
        self.assertEqual(self.parse(parser, scanner,
                                    ['a', 'b', scanner.END, 'c']),
                         [('c', 'a'), ('a', 'b'), ('', 'c')])
        self.assertEqual(self.parse(parser, scanner,
                                    ['a', Scanner.END, Scanner.END, 'c']),
                         [('', 'a'), ('', 'c')])
        self.assertEqual(self.parse(parser, scanner, [Scanner.END] * 4), [])

    def test_state_size(self):
        scanner = Scanner(lambda x: x)
        parser = Parser(state_sizes=[3])

        self.assertEqual(self.parse(parser, scanner, 'abcde'),
                         [('  ', 'a'), ('  a', 'b'), (' a b', 'c'),
                          ('a b c', 'd'), ('b c d', 'e')])
        self.assertEqual(self.parse(parser, scanner,
                                    ['a', 'b', 'c', Scanner.END, 'd', 'e']),
                         [('  ', 'a'), ('  a', 'b'), (' a b', 'c'),
                          ('  ', 'd'), ('  d', 'e')])
        self.assertEqual(self.parse(parser, scanner,
                                    ['a', 'b', 'c', (Scanner.START, 'd'), 'e']),
                         [('  ', 'a'), ('  a', 'b'), (' a b', 'c'),
                          ('  d', 'e')])

    def test_save_load(self):
        parser = Parser(state_sizes=[1, 2, 3],
                        reset_on_sentence_end=False)
        saved = parser.save()
        loaded = Parser.load(saved)
        self.assertEqual(parser, loaded)


class TestLevelParser(TestCase):
    class ParserTest(ParserBase):
        def __init__(self, parse=None):
            super().__init__(parse)
            self.is_reset = False

        def reset(self):
            self.is_reset = True

    def test_properties(self):
        parser = LevelParser()
        self.assertEqual(parser.levels, 1)
        self.assertEqual(parser.parsers, [Parser()])

        with self.assertRaises(ValueError):
            parser.levels = 0
        with self.assertRaises(ValueError):
            parser.levels = -1
        self.assertEqual(parser.levels, 1)

        parser.levels = 2
        self.assertEqual(parser.parsers, [Parser(), Parser()])

        level = Parser(state_sizes=[2, 3])
        parser.parsers = level
        self.assertEqual(parser.parsers, [level, level])

        parser.parsers = [Parser(), level, Parser()]
        self.assertEqual(parser.parsers, [Parser(), level])

        parser.levels = 1
        self.assertEqual(parser.parsers, [Parser()])

        parser.levels = 2
        self.assertIs(parser.parsers[1], level)

    def test_reset(self):
        parser = LevelParser(levels=2,
                             parsers=[self.ParserTest(), self.ParserTest()])
        self.assertEqual([x.is_reset for x in parser.parsers], [False, False]) # pylint:disable=no-member
        parser.reset()
        self.assertEqual([x.is_reset for x in parser.parsers], [True, True]) # pylint:disable=no-member

    def test_parse(self):
        parser = LevelParser(
            levels=2,
            parsers=[self.ParserTest(lambda x: [0]),
                     self.ParserTest(lambda x: [1])]
        )
        self.assertEqual(list(parser([[0], [1]])), [0, 1])
        self.assertEqual(list(parser([[0]] * 5)), [0, 1])
        self.assertEqual(list(parser([])), [])

    def test_save_load(self):
        level = Parser(state_sizes=[2, 3])
        parser = LevelParser(levels=3, parsers=[level, Parser()])
        saved = parser.save()
        loaded = Parser.load(saved)
        self.assertEqual(parser, loaded)

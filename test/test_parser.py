from unittest import TestCase

from markovchain import Parser, LevelParser, Scanner
from markovchain.parser import ParserBase


class TestParser(TestCase):
    @staticmethod
    def parse(parser, scanner, data, part=False, separator=' '):
        return [(separator.join(src), dst)
                for src, dst in parser(scanner(data, part), part)]

    def testProperties(self):
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

    def testProperties2(self):
        scanner = Scanner(lambda x: x)
        parser = Parser(state_sizes=[2],
                        reset_on_sentence_end=False)
        self.assertEqual(self.parse(parser, scanner, ['a', scanner.END, 'b'],
                                    True, '::'),
                         [('::', 'a'), ('::a', 'b')])
        self.assertEqual(self.parse(parser, scanner, 'c', separator='::'),
                         [('a::b', 'c')])

    def testDefault(self):
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

    def testStateSize(self):
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

    def testSaveLoad(self):
        parser = Parser(state_sizes=[1, 2, 3],
                        reset_on_sentence_end=False)
        saved = parser.save()
        loaded = Parser.load(saved)
        self.assertEqual(parser, loaded)


class TestLevelParser(TestCase):
    class Parser(ParserBase):
        def __init__(self, parse=None):
            super().__init__(parse)
            self.is_reset = False

        def reset(self):
            self.is_reset = True

    def testProperties(self):
        p = LevelParser()
        self.assertEqual(p.levels, 1)
        self.assertEqual(p.parsers, [Parser()])

        with self.assertRaises(ValueError):
            p.levels = 0
        with self.assertRaises(ValueError):
            p.levels = -1
        self.assertEqual(p.levels, 1)

        p.levels = 2
        self.assertEqual(p.parsers, [Parser(), Parser()])

        pp = Parser(state_sizes=[2, 3])
        p.parsers = pp
        self.assertEqual(p.parsers, [pp, pp])

        p.parsers = [Parser(), pp, Parser()]
        self.assertEqual(p.parsers, [Parser(), pp])

        p.levels = 1
        self.assertEqual(p.parsers, [Parser()])

        p.levels = 2
        self.assertIs(p.parsers[1], pp)

    def testReset(self):
        p = LevelParser(levels=2, parsers=[self.Parser(), self.Parser()])
        self.assertEqual([pp.is_reset for pp in p.parsers], [False, False])
        p.reset()
        self.assertEqual([pp.is_reset for pp in p.parsers], [True, True])

    def testParse(self):
        p = LevelParser(
            levels=2,
            parsers=[self.Parser(lambda x: [0]), self.Parser(lambda x: [1])]
        )
        self.assertEqual(list(p([[0], [1]])), [0, 1])
        self.assertEqual(list(p([[0]] * 5)), [0, 1])
        self.assertEqual(list(p([])), [])

    def testSaveLoad(self):
        pp = Parser(state_sizes=[2, 3])
        p = LevelParser(levels=3, parsers=[pp, Parser()])
        saved = p.save()
        loaded = Parser.load(saved)
        self.assertEqual(p, loaded)

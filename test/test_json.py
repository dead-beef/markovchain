from unittest import TestCase
from io import StringIO, BytesIO

from markovchain import (MarkovBase, MarkovJsonMixin,
                         Scanner, CharScanner, Parser)


class TestMarkovJson(TestCase):
    class Markov(MarkovJsonMixin, MarkovBase):
        pass

    def testEmpty(self):
        m = self.Markov()
        self.assertFalse(m.nodes)

    def testProperties(self):
        m = self.Markov(scanner=Scanner(lambda x: x))
        m.links([(('x', 'y'), 'z')])
        m.separator = '::'
        self.assertEqual(list(m.nodes.keys()), ['x::y'])

    def testAddLinks(self):
        m = self.Markov()
        m.links([(('x',), 'y'), (('y',), 'z'), (('x',), 'y')])
        self.assertEqual(
            m.nodes,
            {
                'x': ['y', 2],
                'y': ['z', 1]
            }
        )
        m.links([(('z',), 'x'), (('x',), 'z')])
        self.assertEqual(
            m.nodes,
            {
                'x': [['y', 'z'], [2, 1]],
                'y': ['z', 1],
                'z': ['x', 1]
            }
        )

    def testGenerateEmpty(self):
        m = self.Markov()
        self.assertEqual(''.join(m.generate(10)), '')
        m = self.Markov()
        m.links([(('x',), 'y')])
        self.assertEqual(''.join(m.generate(-1, start='x')), '')
        self.assertEqual(''.join(m.generate(0, start='x')), '')
        m.parser = None
        self.assertEqual(''.join(m.generate(10, state_size=4)), '')

    def testGenerate(self):
        m = self.Markov(scanner=Scanner(lambda x: x))
        m.data(['x', 'y'])
        self.assertEqual(''.join(m.generate(1, start='')), 'x')
        self.assertEqual(''.join(m.generate(10, start='x')), 'y')
        self.assertEqual(''.join(m.generate(10, start='y')), '')
        self.assertIn(''.join(m.generate(10)), ['y', 'xy'])

    def testGenerateStateSize(self):
        m = self.Markov(separator=':',
                        parser=Parser(state_sizes=[2, 3]),
                        scanner=Scanner(lambda x: x))
        m.data(['x', 'y', 'z'])
        self.assertEqual(''.join(m.generate(10, state_size=2)), 'xyz')
        self.assertEqual(''.join(m.generate(10, state_size=3)), 'xyz')

    def testSaveLoad(self):
        m = self.Markov(separator=':',
                        parser=Parser(state_sizes=[2, 3]),
                        scanner=Scanner(lambda x: x))
        m.data(['', 'x', 'y', 'z', None])
        m.scanner = CharScanner()

        fp = StringIO()
        m.save(fp)
        fp.seek(0)
        loaded = self.Markov.load(fp)
        self.assertEqual(m, loaded)

        fp.seek(0)
        fp1 = BytesIO()
        fp1.write(fp.read().encode('utf-8'))
        fp1.seek(0)
        loaded = self.Markov.load(fp1)
        self.assertEqual(m, loaded)

        fp.seek(0)
        loaded = self.Markov.load(fp, {'separator': ''})
        self.assertNotEqual(m, loaded)
        self.assertEqual(loaded.separator, '')

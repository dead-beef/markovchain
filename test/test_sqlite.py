from unittest import TestCase
from tempfile import TemporaryDirectory
from collections import Counter
from itertools import chain, repeat
import os

from markovchain import (MarkovBase, MarkovSqliteMixin,
                         Scanner, CharScanner, Parser)


class TestMarkovSqlite(TestCase):
    class Markov(MarkovSqliteMixin, MarkovBase):
        pass

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def test_empty(self):
        m = self.Markov()
        m.save()
        self.assertTrue(m.db)
        self.assertTrue(m.cursor)
        tables = m.get_tables()
        self.assertIn('main', tables)
        self.assertIn('nodes', tables)
        self.assertIn('links', tables)

    def test_properties(self):
        m = self.Markov(scanner=Scanner(lambda x: x))
        m.links([(('x', 'y'), 'z')])
        m.separator = '::'
        m.cursor.execute('SELECT value FROM nodes')
        nodes = m.cursor.fetchall()
        self.assertEqual(nodes, [('x::y',), ('y::z',)])

    def test_add_links(self):
        m = self.Markov()
        m.links([(('x',), 'y'), (('y',), 'z'), (('x',), 'y')])

        m.cursor.execute('SELECT id, value FROM nodes')
        nodes = m.cursor.fetchall()
        self.assertEqual(nodes, [(1, 'x'), (2, 'y'), (3, 'z')])

        node = m.get_node('z')
        m.cursor.execute('SELECT value FROM links WHERE source=?', (node,))
        nodes = m.cursor.fetchall()
        self.assertEqual(nodes, [])

        node = m.get_node('y')
        m.cursor.execute(
            'SELECT value, count FROM links WHERE source=?',
            (node,)
        )
        nodes = m.cursor.fetchall()
        self.assertCountEqual(nodes, [('z', 1)])

        node = m.get_node('x')
        m.cursor.execute(
            'SELECT value, count FROM links WHERE source=?',
            (node,)
        )
        nodes = m.cursor.fetchall()
        self.assertCountEqual(nodes, [('y', 2)])

        m.links([(('x',), 'z'), (('x',), 'y')])

        m.cursor.execute(
            'SELECT value, count FROM links WHERE source=?',
            (node,)
        )
        nodes = m.cursor.fetchall()
        self.assertCountEqual(nodes, [('y', 3), ('z', 1)])

    def test_random_link(self):
        m = self.Markov()
        values = list(str(x) for x in range(4))
        m.links(('', y) for y in values)
        counter = Counter(m.random_link(('',))[0]
                          for _ in range(10 * len(values)))
        self.assertEqual(len(counter.items()), len(values))
        self.assertTrue(
            all(count and item in values for item, count in counter.items())
        )

    def test_random_link_frequency(self):
        m = self.Markov()
        values = list(range(4))
        counts = (x * x for x in values)
        m.links(chain(*(
            repeat(('', str(v)), n) for v, n in zip(values, counts)
        )))
        counter = Counter(m.random_link('')[0]
                          for _ in range(20 * len(values)))
        common = [value for value, count in counter.most_common()]
        values.sort(key=lambda x: -x)
        values = [str(value) for value in values]
        self.assertGreater(len(common), 1)
        self.assertEqual(common, values[:len(common)])

    def test_generate_empty(self):
        m = self.Markov()
        self.assertEqual(''.join(m.generate(10)), '')
        m = self.Markov()
        m.links([('x', 'y')])
        self.assertEqual(''.join(m.generate(-1, start='x')), '')
        self.assertEqual(''.join(m.generate(0, start='x')), '')
        m.parser = None
        self.assertEqual(''.join(m.generate(10, state_size=4)), '')

    def test_generate(self):
        m = self.Markov(scanner=Scanner(lambda x: x))
        m.data(['x', 'y'])
        self.assertEqual(''.join(m.generate(1, start='')), 'x')
        self.assertEqual(''.join(m.generate(10, start='x')), 'y')
        self.assertEqual(''.join(m.generate(10, start='y')), '')
        self.assertIn(''.join(m.generate(10)), ['y', 'xy'])

    def test_generate_state_size(self):
        m = self.Markov(separator=':',
                        parser=Parser(state_sizes=[2, 3]),
                        scanner=Scanner(lambda x: x))
        m.data(['x', 'y', 'z'])
        self.assertEqual(''.join(m.generate(10, state_size=2)), 'xyz')
        self.assertEqual(''.join(m.generate(10, state_size=3)), 'xyz')

    def test_save_load(self):
        db = os.path.join(self.tmpdir.name, 'test.db')
        m = self.Markov(db=db,
                        separator=':',
                        parser=Parser(state_sizes=[2, 3]),
                        scanner=Scanner(lambda x: x))
        m.data(['x', 'y', 'z'])
        m.scanner = CharScanner()
        m.save()

        loaded = self.Markov.load(db)
        self.assertEqual(m, loaded)
        self.assertEqual(''.join(loaded.generate(10, state_size=2)), 'xyz')

        loaded = self.Markov.load(db, {'separator': ''})
        self.assertNotEqual(m, loaded)
        self.assertEqual(loaded.separator, '')

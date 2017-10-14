from unittest import TestCase

from markovchain import MarkovBase, Parser


class TestMarkovBase(TestCase):
    class Scanner:
        def reset(self):
            pass
        def __call__(self, data, part):
            pass

    class Markov(MarkovBase): # pylint:disable=abstract-method
        def links(self, links):
            pass

    def test_properties(self):
        m = self.Markov()
        self.assertIsInstance(m.parser, Parser)
        self.assertIsNotNone(m.separator)

    def test_generate_error(self):
        m = self.Markov()
        m.parser = None
        with self.assertRaises(ValueError):
            list(m.generate(10))

    def test_save_load(self):
        m = self.Markov(separator=':', parser=Parser())
        saved = m.get_save_data()
        loaded = self.Markov(**saved)
        self.assertEqual(m, loaded)

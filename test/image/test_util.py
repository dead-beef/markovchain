from unittest import TestCase
from collections import Counter
from itertools import islice

from markovchain.image.util import palette


class TestPalette(TestCase):
    def testErrors(self):
        tests = [
            (8, 8, 5),
            (0, 4, 4),
            (4, 0, 4),
            (4, 4, 0),
            (8, -4, 8),
            (-8, 4, -8)
        ]
        for test in tests:
            with self.assertRaises(ValueError):
                palette(*test)

    def testGenerate(self):
        tests = [
            (8, 4, 8),
            (2, 2, 2),
            (16, 1, 1)
        ]
        for test in tests:
            p = palette(*test)
            self.assertEqual(len(p), 768)
            p = list(zip(islice(p, 0, None, 3),
                         islice(p, 1, None, 3),
                         islice(p, 2, None, 3)))
            c = Counter(p)
            size = test[0] * test[1] * test[2]
            self.assertEqual(len(c.items()), min(256, size + 1))
            self.assertEqual(c[(0, 0, 0)], 256 - size)

    def testGrayscale(self):
        tests = [
            (1, 1, 1),
            (1, 1, 2),
            (1, 1, 256)
        ]
        for test in tests:
            p = palette(*test)
            self.assertEqual(len(p), 768)
            p = list(zip(islice(p, 0, None, 3),
                         islice(p, 1, None, 3),
                         islice(p, 2, None, 3)))
            self.assertTrue(all(r == g and g == b for r, g, b in p))
            c = Counter(p)
            size = test[0] * test[1] * test[2]
            self.assertEqual(len(c.items()), size)
            self.assertEqual(c[(0, 0, 0)], 256 - size + 1)
            if size > 1:
                self.assertEqual(c[(255, 255, 255)], 1)

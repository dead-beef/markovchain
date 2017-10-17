from unittest import TestCase
from collections import Counter
from itertools import islice

from markovchain.image.util import palette


class TestPalette(TestCase):
    def test_errors(self):
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

    def test_generate(self):
        tests = [
            (8, 4, 8),
            (2, 2, 2),
            (16, 1, 1)
        ]
        for test in tests:
            res = palette(*test)
            self.assertEqual(len(res), 768)
            res = list(zip(islice(res, 0, None, 3),
                           islice(res, 1, None, 3),
                           islice(res, 2, None, 3)))
            counter = Counter(res)
            size = test[0] * test[1] * test[2]
            self.assertEqual(len(counter.items()), min(256, size + 1))
            self.assertEqual(counter[(0, 0, 0)], 256 - size)

    def test_grayscale(self):
        tests = [
            (1, 1, 1),
            (1, 1, 2),
            (1, 1, 256)
        ]
        for test in tests:
            res = palette(*test)
            self.assertEqual(len(res), 768)
            res = list(zip(islice(res, 0, None, 3),
                           islice(res, 1, None, 3),
                           islice(res, 2, None, 3)))
            self.assertTrue(all(r == g and g == b for r, g, b in res))
            counter = Counter(res)
            size = test[0] * test[1] * test[2]
            self.assertEqual(len(counter.items()), size)
            self.assertEqual(counter[(0, 0, 0)], 256 - size + 1)
            if size > 1:
                self.assertEqual(counter[(255, 255, 255)], 1)

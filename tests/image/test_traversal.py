from unittest import TestCase
from itertools import product

from markovchain.image.traversal import (
    Traversal, Lines, HLines, VLines, Spiral, Hilbert, Blocks
)


class TestLines(TestCase):
    def setUp(self):
        Traversal.add_class(Lines)

    def tearDown(self):
        Traversal.remove_class(Lines)

    def test_save_load(self):
        tests = [(0, False), (2, True)]
        for test in tests:
            test = Lines(*test)
            saved = test.save()
            loaded = Traversal.load(saved)
            self.assertEqual(test, loaded)


class TestHLines(TestCase):
    def test_traverse(self):
        test = HLines()

        test.reverse = 0
        self.assertEqual(list(test(2, 3, False)),
                         [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)])
        self.assertEqual(list(test(2, 3, True)),
                         [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)])
        test.reverse = 1
        self.assertEqual(list(test(2, 3)),
                         [(1, 0), (0, 0), (1, 1), (0, 1), (1, 2), (0, 2)])
        test.reverse = 2
        self.assertEqual(list(test(2, 3)),
                         [(1, 0), (0, 0), (0, 1), (1, 1), (1, 2), (0, 2)])
        test.reverse = 0
        test.line_sentences = True
        self.assertEqual(list(test(2, 3, True)),
                         [(0, 0), (1, 0), None,
                          (0, 1), (1, 1), None,
                          (0, 2), (1, 2), None])
        self.assertEqual(list(test(2, 3, False)),
                         [(0, 0), (1, 0), (0, 1),
                          (1, 1), (0, 2), (1, 2)])

    def test_save_load(self):
        tests = [(0, False), (2, True)]
        for test in tests:
            test = HLines(*test)
            saved = test.save()
            loaded = Traversal.load(saved)
            self.assertEqual(test, loaded)


class TestVLines(TestCase):
    def test_traverse(self):
        test = VLines()

        test.reverse = 0
        self.assertEqual(list(test(2, 3)),
                         [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)])
        test.reverse = 1
        self.assertEqual(list(test(2, 3)),
                         [(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)])
        test.reverse = 2
        self.assertEqual(list(test(2, 3)),
                         [(0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2)])
        test.reverse = 0
        test.line_sentences = True
        self.assertEqual(list(test(2, 3)),
                         [(0, 0), (0, 1), (0, 2), None,
                          (1, 0), (1, 1), (1, 2), None])
        self.assertEqual(list(test(2, 3, False)),
                         [(0, 0), (0, 1), (0, 2),
                          (1, 0), (1, 1), (1, 2)])

    def test_save_load(self):
        tests = [(0, False), (2, True)]
        for test in tests:
            test = VLines(*test)
            saved = test.save()
            loaded = Traversal.load(saved)
            self.assertEqual(test, loaded)


class TestSpiral(TestCase):
    def test_traverse(self):
        test = Spiral()
        tests = product(range(1, 7), range(1, 7))
        for width, height in tests:
            test.reverse = False
            res = list(test(width, height, False))
            self.assertCountEqual(res, product(range(width), range(height)))
            test.reverse = True
            res2 = list(test(width, height, False))
            res.reverse()
            self.assertEqual(res2, res)

    def test_save_load(self):
        tests = [(False,), (True,)]
        for test in tests:
            test = Spiral(*test)
            saved = test.save()
            loaded = Traversal.load(saved)
            self.assertEqual(test, loaded)


class TestHilbert(TestCase):
    def test_traverse(self):
        test = Hilbert()
        tests = product(range(1, 7), range(1, 7))
        for width, height in tests:
            res = list(test(width, height))
            self.assertCountEqual(res, product(range(width), range(height)))

    def test_save_load(self):
        test = Hilbert()
        saved = test.save()
        loaded = Traversal.load(saved)
        self.assertEqual(test, loaded)


class TestBlocks(TestCase):
    def test_traverse(self):
        def hline(width, height, ends): # pylint: disable=unused-argument
            for x in range(width):
                yield (x, 0)
                if ends and x == 0:
                    yield None

        def vline(width, height, ends): # pylint: disable=unused-argument
            for y in range(height):
                yield (0, y)
                if ends:
                    yield None

        traverse = Blocks(block_size=(2, 2),
                          block_sentences=False,
                          traverse_image=hline,
                          traverse_block=vline)

        tests = [
            ((4, 4, False), [(0, 0), (0, 1), (2, 0), (2, 1)]),
            ((3, 3, False), [(0, 0), (0, 1)]),
            ((4, 4, True), [(0, 0), (0, 1), None, (2, 0), (2, 1)])
        ]

        for test, res in tests:
            self.assertEqual(list(traverse(*test)), res)

        traverse.block_sentences = True

        tests = [
            ((4, 4, False), [(0, 0), (0, 1), (2, 0), (2, 1)]),
            ((3, 3, True), [(0, 0), (0, 1), None, None]),
            ((4, 4, True), [(0, 0), (0, 1), None, None, (2, 0), (2, 1), None])
        ]

        for test, res in tests:
            self.assertEqual(list(traverse(*test)), res)

    def test_save_load(self):
        tests = [
            ((8, 8), True,
             HLines(reverse=1, line_sentences=True),
             VLines(reverse=2, line_sentences=False))
        ]
        for test in tests:
            test = Blocks(*test)
            saved = test.save()
            loaded = Traversal.load(saved)
            self.assertEqual(test, loaded)

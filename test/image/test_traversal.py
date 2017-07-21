from unittest import TestCase
from itertools import product

from markovchain.image.traversal import (
    Traversal, Lines, HLines, VLines, Spiral, Blocks
)


class TestLines(TestCase):
    def setUp(self):
        Traversal.add_class(Lines)

    def tearDown(self):
        Traversal.remove_class(Lines)

    def testSaveLoad(self):
        tests = [(0, False), (2, True)]
        for test in tests:
            t = Lines(*test)
            saved = t.save()
            loaded = Traversal.load(saved)
            self.assertEqual(t, loaded)


class TestHLines(TestCase):
    def testTraverse(self):
        t = HLines()

        t.reverse = 0
        self.assertEqual(list(t(2, 3, False)),
                         [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)])
        self.assertEqual(list(t(2, 3, True)),
                         [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)])
        t.reverse = 1
        self.assertEqual(list(t(2, 3)),
                         [(1, 0), (0, 0), (1, 1), (0, 1), (1, 2), (0, 2)])
        t.reverse = 2
        self.assertEqual(list(t(2, 3)),
                         [(1, 0), (0, 0), (0, 1), (1, 1), (1, 2), (0, 2)])
        t.reverse = 0
        t.line_sentences = True
        self.assertEqual(list(t(2, 3, True)),
                         [(0, 0), (1, 0), None,
                          (0, 1), (1, 1), None,
                          (0, 2), (1, 2), None])
        self.assertEqual(list(t(2, 3, False)),
                         [(0, 0), (1, 0), (0, 1),
                          (1, 1), (0, 2), (1, 2)])

    def testSaveLoad(self):
        tests = [(0, False), (2, True)]
        for test in tests:
            t = HLines(*test)
            saved = t.save()
            loaded = Traversal.load(saved)
            self.assertEqual(t, loaded)


class TestVLines(TestCase):
    def testTraverse(self):
        t = VLines()

        t.reverse = 0
        self.assertEqual(list(t(2, 3)),
                         [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)])
        t.reverse = 1
        self.assertEqual(list(t(2, 3)),
                         [(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)])
        t.reverse = 2
        self.assertEqual(list(t(2, 3)),
                         [(0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2)])
        t.reverse = 0
        t.line_sentences = True
        self.assertEqual(list(t(2, 3)),
                         [(0, 0), (0, 1), (0, 2), None,
                          (1, 0), (1, 1), (1, 2), None])
        self.assertEqual(list(t(2, 3, False)),
                         [(0, 0), (0, 1), (0, 2),
                          (1, 0), (1, 1), (1, 2)])

    def testSaveLoad(self):
        tests = [(0, False), (2, True)]
        for test in tests:
            t = VLines(*test)
            saved = t.save()
            loaded = Traversal.load(saved)
            self.assertEqual(t, loaded)


class TestSpiral(TestCase):
    def testTraverse(self):
        t = Spiral()
        tests = product(range(1, 7), range(1, 7))
        for w, h in tests:
            t.reverse = False
            res = list(t(w, h, False))
            self.assertCountEqual(res, product(range(w), range(h)))
            t.reverse = True
            res2 = list(t(w, h, False))
            res.reverse()
            self.assertEqual(res2, res)

    def testSaveLoad(self):
        tests = [(False,), (True,)]
        for test in tests:
            t = Spiral(*test)
            saved = t.save()
            loaded = Traversal.load(saved)
            self.assertEqual(t, loaded)


class TestBlocks(TestCase):
    def testTraverse(self):
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

        tr = Blocks(block_size=(2, 2),
                    block_sentences=False,
                    traverse_image=hline,
                    traverse_block=vline)

        tests = [
            ((4, 4, False), [(0, 0), (0, 1), (2, 0), (2, 1)]),
            ((3, 3, False), [(0, 0), (0, 1)]),
            ((4, 4, True), [(0, 0), (0, 1), None, (2, 0), (2, 1)])
        ]

        for test, res in tests:
            self.assertEqual(list(tr(*test)), res)

        tr.block_sentences = True

        tests = [
            ((4, 4, False), [(0, 0), (0, 1), (2, 0), (2, 1)]),
            ((3, 3, True), [(0, 0), (0, 1), None, None]),
            ((4, 4, True), [(0, 0), (0, 1), None, None, (2, 0), (2, 1), None])
        ]

        for test, res in tests:
            self.assertEqual(list(tr(*test)), res)

    def testSaveLoad(self):
        tests = [
            ((8, 8), True,
             HLines(reverse=1, line_sentences=True),
             VLines(reverse=2, line_sentences=False))
        ]
        for test in tests:
            t = Blocks(*test)
            saved = t.save()
            loaded = Traversal.load(saved)
            self.assertEqual(t, loaded)

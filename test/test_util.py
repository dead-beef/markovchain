from unittest import TestCase

from markovchain.util import SaveLoad, fill, load, extend, to_list, truncate


class TestSaveLoad(TestCase):
    class SaveLoadTest(SaveLoad):
        classes = {}

        def __init__(self, value):
            self.value = value

        def __eq__(self, test):
            return self.value == test.value

        def save(self):
            data = super().save()
            data['value'] = self.value
            return data

    def testAddRemove(self):
        self.SaveLoadTest.add_class(self.SaveLoadTest)
        self.assertIs(self.SaveLoadTest.classes['SaveLoadTest'],
                      self.SaveLoadTest)
        self.SaveLoadTest.remove_class(self.SaveLoadTest)
        self.SaveLoadTest.remove_class(self.SaveLoadTest)
        with self.assertRaises(KeyError):
            raise AssertionError(self.SaveLoadTest.classes['SaveLoadTest'])

    def testSaveLoad(self):
        self.SaveLoadTest.add_class(self.SaveLoadTest)
        test = self.SaveLoadTest(0)
        saved = test.save()
        loaded = self.SaveLoadTest.load(saved)
        self.assertIsInstance(loaded, self.SaveLoadTest)
        self.assertEqual(loaded, test)


class TestToList(TestCase):
    def test(self):
        tests = [
            ([], []),
            (range(3), list(range(3))),
            (0, [0]),
            ({'x': 0}, [{'x': 0}])
        ]
        for test, res in tests:
            self.assertEqual(to_list(test), res)


class TestFill(TestCase):
    def testEmpty(self):
        tests = [
            (None, -1),
            ([], 0),
            (0, 0)
        ]
        for test in tests:
            self.assertEqual(fill(*test), [])
        with self.assertRaises(ValueError):
            fill([], 1)

    def testSingle(self):
        tests = [
            ((1, 1), [1]),
            ((1, 5), [1] * 5)
        ]
        for test, res in tests:
            self.assertEqual(fill(*test), res)

    def testMultiple(self):
        tests = [
            ((range(10), 2), [0, 1]),
            ((range(3), 5), [0, 1, 2, 2, 2])
        ]
        for test, res in tests:
            self.assertEqual(fill(*test), res)

    def testNoCopy(self):
        tests = [
            ([], 0),
            (list(range(3)), 3)
        ]
        for lst, sz in tests:
            self.assertIs(fill(lst, sz), lst)

    def testCopy(self):
        tests = [
            ([[0], [1]], 4)
        ]
        for test in tests:
            res = fill(*test, copy=False)
            self.assertIs(res[-1], test[0][-1])
            res = fill(*test, copy=True)
            self.assertIsNot(res[-1], test[0][-1])
            self.assertEqual(res[-1], test[0][-1])


class TestLoad(TestCase):
    class LoadTest:
        @staticmethod
        def load(d):
            return d['x']

    def testDefault(self):
        x = load(None, self.LoadTest, lambda: 0)
        self.assertEqual(x, 0)

    def testLoadClass(self):
        x = load({'x': 1}, self.LoadTest, lambda: 0)
        self.assertEqual(x, 1)

    def testLoadObject(self):
        obj = object()
        x = load(obj, self.LoadTest, lambda: 0)
        self.assertIs(x, obj)


class TestExtend(TestCase):
    def test(self):
        tests = [
            (({'x': 0}, {'y': 1}), {'x': 0, 'y': 1}),
            (({'x': 0}, {'y': 1}, {'x': 1}), {'x': 1, 'y': 1}),
            (({'x': {'y': 0}}, {'x': {'z': 1}}), {'x': {'y': 0, 'z': 1}}),
            (({'x': {'y': 0}}, {'x': 1}), {'x': 1}),
        ]
        for test, res in tests:
            self.assertEqual(extend(*test), res)


class TestTruncate(TestCase):
    def testError(self):
        tests = [
            ('', 3, True),
            ('0', -1, False)
        ]
        for test in tests:
            with self.assertRaises(ValueError):
                truncate(*test)

    def testNoTruncate(self):
        tests = [
            ('0', 4, True),
            ('1234', 4, False)
        ]
        for test in tests:
            self.assertIs(truncate(*test), test[0])

    def testTruncate(self):
        tests = [
            (('1234567', 5), '12...'),
            (('1234567', 5, True), '12...'),
            (('1234567', 5, False), '...67')
        ]
        for test, res in tests:
            self.assertEqual(truncate(*test), res)

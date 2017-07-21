from unittest import TestCase

from markovchain.scanner import Scanner, CharScanner, RegExpScanner


class TestScanner(TestCase):
    def testId(self):
        scan = Scanner(lambda x: x)
        test = 'ab c.d'
        self.assertEqual(''.join(scan(test)), test)


class TestCharScanner(TestCase):
    @staticmethod
    def scanStr(scan, data, part=False, sep=''):
        return sep.join(word for word in scan(data, part) if word is not None)

    def testId(self):
        scan = CharScanner(None, None)
        test = 'ab c.d'
        self.assertEqual(list(scan('', True)), [])
        self.assertEqual(list(scan('', False)), [])
        self.assertEqual(list(scan(test, True)), list(test))
        self.assertEqual(list(scan(test, False)), list(test) + [None])

    def testDefault(self):
        scan = CharScanner()

        self.assertEqual(list(scan('ab..c')),
                         ['a', 'b', '.', '.', scan.END, 'c', '.', scan.END])

        self.assertEqual(list(scan('a b..c', True)),
                         ['a', ' ', 'b', '.', '.', scan.END, 'c'])
        self.assertEqual(list(scan('.', True)), ['.'])
        self.assertEqual(list(scan('', False)), [scan.END])

        self.assertEqual(list(scan('abc', True)), ['a', 'b', 'c'])
        self.assertEqual(list(scan('', False)), ['.', scan.END])

        self.assertEqual(list(scan('...')), [])

        self.assertEqual(self.scanStr(scan, 'abc.de?!f'), 'abc.de?!f.')
        self.assertEqual(self.scanStr(scan, '.?!.a'), 'a.')
        self.assertEqual(self.scanStr(scan, '.?!.a', True), 'a')
        self.assertEqual(self.scanStr(scan, 'a.'), 'a.')

    def testSaveLoad(self):
        tests = [(), (None, None), ('ab', 'cd')]
        for test in tests:
            scanner = CharScanner(*test)
            saved = scanner.save()
            loaded = Scanner.load(saved)
            self.assertEqual(scanner, loaded)


class TestRegExp(TestCase):
    @staticmethod
    def scanStr(scan, data, part=False, sep=''):
        return sep.join(word for word in scan(data, part) if word != scan.END)

    def testId(self):
        scan = RegExpScanner('.', None)
        test = 'ab c.d'
        self.assertEqual(list(scan('', True)), [])
        self.assertEqual(list(scan('', False)), [])
        self.assertEqual(list(scan(test, True)), list(test))
        self.assertEqual(list(scan(test, False)), list(test) + [scan.END])

    def testDefault(self):
        scan = RegExpScanner()

        self.assertEqual(list(scan('ab..c')),
                         ['ab', '..', scan.END, 'c', '.', scan.END])

        self.assertEqual(list(scan('a \n b?!. .. !! ??c', True)),
                         ['a', 'b', '?!.', scan.END, 'c'])
        self.assertEqual(list(scan('.', True)), ['.', scan.END])
        self.assertEqual(list(scan('', False)), [])

        self.assertEqual(list(scan('... .. . ! \n ? ?!  ')), [])

        self.assertEqual(self.scanStr(scan, 'a\t\nb\nc.d   e ?!f'),
                         'abc.de?!f.')
        self.assertEqual(self.scanStr(scan, '.?!.a', True), 'a')
        self.assertEqual(self.scanStr(scan, 'a.'), 'a.')

    def testSaveLoad(self):
        tests = [(), ('.*', None)]
        for test in tests:
            scanner = RegExpScanner(*test)
            saved = scanner.save()
            loaded = Scanner.load(saved)
            self.assertEqual(scanner, loaded)

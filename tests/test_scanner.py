from unittest import TestCase

from markovchain.scanner import Scanner, CharScanner, RegExpScanner


class TestScanner(TestCase):
    def test_id(self):
        scan = Scanner(lambda x: x)
        test = 'ab c.d'
        self.assertEqual(''.join(scan(test)), test)


class ScannerTestCase(TestCase):
    @staticmethod
    def scan_str(scanner, data, part=False, sep=''):
        return sep.join(word
                        for word in scanner(data, part)
                        if word != scanner.END)


class TestCharScanner(ScannerTestCase):
    def test_id(self):
        scan = CharScanner(None, None)
        test = 'ab c.d'
        self.assertEqual(list(scan('', True)), [])
        self.assertEqual(list(scan('', False)), [])
        self.assertEqual(list(scan(test, True)), list(test))
        self.assertEqual(list(scan(test, False)), list(test) + [None])

    def test_default(self):
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

        self.assertEqual(self.scan_str(scan, 'abc.de?!f'), 'abc.de?!f.')
        self.assertEqual(self.scan_str(scan, '.?!.a'), 'a.')
        self.assertEqual(self.scan_str(scan, '.?!.a', True), 'a')
        self.assertEqual(self.scan_str(scan, 'a.'), 'a.')

    def test_save_load(self):
        tests = [(), (None, None), ('ab', 'cd')]
        for test in tests:
            scanner = CharScanner(*test)
            saved = scanner.save()
            loaded = Scanner.load(saved)
            self.assertEqual(scanner, loaded)


class TestRegExp(ScannerTestCase):
    def test_id(self):
        scan = RegExpScanner('.', None)
        test = 'ab c.d'
        self.assertEqual(list(scan('', True)), [])
        self.assertEqual(list(scan('', False)), [])
        self.assertEqual(list(scan(test, True)), list(test))
        self.assertEqual(list(scan(test, False)), list(test) + [scan.END])

    def test_default(self):
        scan = RegExpScanner()

        self.assertEqual(list(scan('ab..c')),
                         ['ab', '..', scan.END, 'c', '.', scan.END])

        self.assertEqual(list(scan('a \n b?!. .. !! ??c', True)),
                         ['a', 'b', '?!.', scan.END, 'c'])
        self.assertEqual(list(scan('.', True)), ['.', scan.END])
        self.assertEqual(list(scan('', False)), [])

        self.assertEqual(list(scan('... .. . ! \n ? ?!  ')), [])

        self.assertEqual(self.scan_str(scan, 'a\t\nb\nc.d   e ?!f'),
                         'abc.de?!f.')
        self.assertEqual(self.scan_str(scan, '.?!.a', True), 'a')
        self.assertEqual(self.scan_str(scan, 'a.'), 'a.')

    def test_save_load(self):
        tests = [(), ('.*', None)]
        for test in tests:
            scanner = RegExpScanner(*test)
            saved = scanner.save()
            loaded = Scanner.load(saved)
            self.assertEqual(scanner, loaded)

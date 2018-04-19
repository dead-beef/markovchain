import pytest

from markovchain.scanner import Scanner
from markovchain.text.scanner import CharScanner, RegExpScanner


def scan_str(scanner, data, part=False, sep=''):
    return sep.join(word for word in scanner(data, part) if word != scanner.END)


@pytest.mark.parametrize('test,res', [
    (('', True), []),
    (('', False), []),
    (('ab c.d', True), list('ab c.d')),
    (('ab c.d', False), list('ab c.d') + [Scanner.END])
])
def test_char_scanner_id(test, res):
    scan = CharScanner(None, None)
    assert list(scan(*test)) == res

def test_char_scanner_default():
    scan = CharScanner()

    assert list(scan('ab..c')) == [
        'a', 'b', '.', '.', scan.END, 'c', '.', scan.END
    ]
    assert list(scan('a b..c', True)) == [
        'a', ' ', 'b', '.', '.', scan.END, 'c'
    ]
    assert list(scan('.', True)) == ['.']
    assert list(scan('', False)) == [scan.END]

    assert list(scan('abc', True)) == ['a', 'b', 'c']
    assert list(scan('', False)) == ['.', scan.END]

    assert list(scan('...')) == []

@pytest.mark.parametrize('test,res', [
    (('abc.de?!f',), 'abc.de?!f.'),
    (('.?!.a',), 'a.'),
    (('.?!.a', True), 'a'),
    (('a.',), 'a.')
])
def test_char_scanner_default_str(test, res):
    scan = CharScanner()
    assert scan_str(scan, *test) == res

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((None, None), (None, None), True),
    (('x', 'y'), ('x', 'y'), True),
    (('x', 'y'), ('x', 'y', 'upper'), False),
    (('x', 'y'), ('x', 'x'), False),
    (('x', 'y'), ('y', 'y'), False)
])
def test_char_scanner_eq(test, test2, res):
    scan = CharScanner(*test)
    scan2 = CharScanner(*test2)
    assert (scan == scan2) == res

@pytest.mark.parametrize('test', [
    (), (None, None), ('ab', 'cd', 'upper')
])
def test_char_scanner_save_load(test):
    scanner = CharScanner(*test)
    saved = scanner.save()
    loaded = Scanner.load(saved)
    assert scanner == loaded


@pytest.mark.parametrize('test,res', [
    (('', True), []),
    (('', False), []),
    (('ab c.d', True), list('ab c.d')),
    (('ab c.d', False), list('ab c.d') + [Scanner.END])
])
def test_regexp_scanner_id(test, res):
    scan = RegExpScanner('.', None)
    assert list(scan(*test)) == res

def test_regexp_scanner_default():
    scan = RegExpScanner()

    assert list(scan('ab..c')) == [
        'ab', '..', scan.END, 'c', '.', scan.END
    ]
    assert list(scan('a \n b?!. .. !! ??c', True)) == [
        'a', 'b', '?!.', scan.END, 'c'
    ]
    assert list(scan('.', True)) == ['.', scan.END]
    assert list(scan('', False)) == []
    assert list(scan('... .. . ! \n ? ?!  ')) == []

@pytest.mark.parametrize('test,res', [
    (('a\t\nb\nc.d   e ?!f',), 'abc.de?!f.'),
    (('.?!.a', True), 'a'),
    (('a.',), 'a.')
])
def test_regexp_scanner_default_str(test, res):
    scan = RegExpScanner()
    assert scan_str(scan, *test) == res

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    (('.', None), ('.', None), True),
    (('.', None), ('.', '.'), False),
    (('.', 'x'), ('.', 'x'), True),
    (('.', 'x'), ('.', 'x', 'upper'), False),
    (('x', '.'), ('.', '.'), False),
    (('x', '.'), ('x', 'x'), False)
])
def test_regexp_scanner_eq(test, test2, res):
    scan = RegExpScanner(*test)
    scan2 = RegExpScanner(*test2)
    assert (scan == scan2) == res

@pytest.mark.parametrize('test', [
    (), ('.*', ',', 'upper')
])
def test_regexp_scanner_save_load(test):
    scanner = RegExpScanner(*test)
    saved = scanner.save()
    loaded = Scanner.load(saved)
    assert scanner == loaded

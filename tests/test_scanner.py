import pytest

from markovchain.scanner import Scanner


def test_scanner_id():
    scan = Scanner(lambda x: x)
    test = 'ab c.d'
    assert ''.join(scan(test)) == test

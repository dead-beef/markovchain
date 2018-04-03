import pytest

from markovchain.text.util import (
    CharCase, ispunct, capitalize, lstrip_ws_and_chars
)


@pytest.mark.parametrize('test,res', [
    ('\'"?,+-.[]{}()<>', True),
    ('\'"?,+-x.[]{}()<>', False),
    ('', False)
])
def test_ispunct(test, res):
    assert ispunct(test) == res


@pytest.mark.parametrize('test,res', [
    ('worD WORD WoRd', 'Word word word'),
    ('x', 'X'),
    ('', '')
])
def test_capitalize(test, res):
    assert capitalize(test) == res


@pytest.mark.parametrize('test,res', [
    (('', ''), ''),
    (('     ', ''), ''),
    (('  x  ', 'xy'), ''),
    ((' \t.\n , .x. ', '.,?!'), 'x. ')
])
def test_lstrip_ws_and_chars(test, res):
    assert lstrip_ws_and_chars(*test) == res


@pytest.mark.parametrize('case,string,res', [
    (CharCase.PRESERVE, 'a B c', 'a B c'),
    (CharCase.TITLE, 'a B c', 'A b c'),
    (CharCase.UPPER, 'a B c', 'A B C'),
    (CharCase.LOWER, 'a B c', 'a b c')
])
def test_char_case_convert(case, string, res):
    case = CharCase(case)
    assert case.convert(string) == res

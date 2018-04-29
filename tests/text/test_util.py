import re
import pytest

from markovchain.text.util import (
    CharCase, ispunct, capitalize, lstrip_ws_and_chars,
    re_flags, re_flags_str, re_sub, get_words, ReFlags
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


@pytest.mark.parametrize('test,res', [
    ('ab,cd', ['ab', 'cd']),
    ('ab cd..\n,ef', ['ab', 'cd', 'ef'])
])
def test_get_words(test, res):
    assert get_words(test) == res


@pytest.mark.parametrize('test,res', [
    (('uiM',), (re.U | re.I | re.M, 0)),
    (('UO',), (re.U, ReFlags.O)),
    (('O', None), ValueError),
    (('-',), ValueError)
])
def test_re_flags(test, res):
    if isinstance(res, type):
        with pytest.raises(res):
            re_flags(*test)
    else:
        assert re_flags(*test) == res


@pytest.mark.parametrize('test,res', [
    ((re.U | re.I | re.M, 0), 'UIM'),
    ((re.U, ReFlags.O), 'UO')
])
def test_re_flags_str(test, res):
    assert sorted(re_flags_str(*test)) == sorted(res)


@pytest.mark.parametrize('test,res', [
    (('x+', 'y', 'xxzxxx'), 'yzy'),
    (('x+', 'y', 'xxzxxx', 1), 'yzxxx'),
    (('xx', 'y', 'xxzXXX', 0, re.I), 'yzyX'),
    (('xx', 'x', 'xxzXXX', 0, re.I, ReFlags.O), 'xzx')
])
def test_re_sub(test, res):
    assert re_sub(*test) == res

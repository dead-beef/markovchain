import pytest

from markovchain.text.util import (
    ispunct, lstrip_ws_and_chars, capitalize,
    format_sentence_string, format_sentence
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

@pytest.mark.parametrize('arg,kwargs,res', [
    ('', {}, ''),
    ('  ', {}, ''),
    ('  ...', {}, ''),
    ('.?!word', {}, 'Word.'),
    ('word', {'default_end': '/'}, 'Word/'),
    ('word', {'end_chars': 'd'}, 'Word'),
    ('word  ,  (word)..  word', {}, 'Word, (word).. word.'),
    ('word,wo[rd..wo]rd', {}, 'Word, wo [rd.. wo] rd.'),
    ('wo--*--rd', {}, 'Wo --*-- rd.')
])
def test_format_sentence_string(arg, kwargs, res):
    assert format_sentence_string(arg, **kwargs) == res

@pytest.mark.parametrize('arg,kwargs,call', [
    ('word', {}, ('word', '.?!', '.')),
    (
        (str(x) for x in range(3)),
        {'end_chars': '/[', 'default_end': '/'},
        ('0 1 2', '/[', '/')
    ),
    (['a', 'b', 'c'], {'join_with': '.'}, ('a.b.c', '.?!', '.'))
])
def test_format_sentence(mocker, arg, kwargs, call):
    fmt = mocker.patch(
        'markovchain.text.util.format_sentence_string',
        return_value=1
    )
    assert format_sentence(arg, **kwargs) == 1
    fmt.assert_called_once_with(*call)

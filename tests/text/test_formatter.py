import pytest

from markovchain.text.formatter import Noop, Formatter


@pytest.mark.parametrize('test', [
    'woRd WORD word'
])
def test_noop_formatter(test):
    assert Noop()(test) is test


@pytest.mark.parametrize('kwargs,kwargs2,res', [
    ({}, {}, True),
    ({'default_end': '/'}, {}, False),
    ({'default_end': '/'}, {'default_end': '/'}, True),
    ({'end_chars': 'd'}, {}, False),
    ({'end_chars': 'd'}, {'end_chars': 'd'}, True),
    ({'case': 'upper'}, {}, False),
    ({'case': 'upper'}, {'case': 'upper'}, True),
    ({'replace': [('.', '')]}, {}, False),
    ({'replace': [('.', '')]}, {'replace': [('.', '')]}, True)
])
def test_formatter_eq(kwargs, kwargs2, res):
    assert (Formatter(**kwargs) == Formatter(**kwargs2)) == res


@pytest.mark.parametrize('kwargs', [
    {},
    {'default_end': '/'},
    {'end_chars': 'd'},
    {'case': 'upper'},
    {'replace': [('.', '')]}
])
def test_formatter_save_load(kwargs):
    fmt = Formatter(**kwargs)
    saved = fmt.save()
    loaded = Formatter.load(saved)
    assert fmt == loaded


@pytest.mark.parametrize('kwargs,test,res', [
    ({}, '', ''),
    ({}, '  ', ''),
    ({}, '  ...', ''),
    ({}, '.?!word', 'Word.'),
    ({}, 'word  ,  (word)..  word', 'Word, (word).. word.'),
    ({}, 'word,wo[rd..wo]rd', 'Word, wo [rd.. wo] rd.'),
    ({}, 'wo--*--rd', 'Wo --*-- rd.'),
    ({'default_end': '/'}, 'word', 'Word/'),
    ({'default_end': None}, 'word', 'Word'),
    ({'end_chars': 'd'}, 'word', 'Word'),
    ({'case': 'upper'}, 'word', 'WORD.'),
    ({'case': 'lower'}, 'woRd', 'word.'),
    ({'case': 'preserve'}, 'woRd', 'woRd.'),
    ({'case': 'xxx'}, 'woRd', ValueError),
    ({'replace': [(r'(x+)', r'_\1_')]}, 'axxb', 'A_xx_b.')
])
def test_formatter_format(kwargs, test, res):
    if isinstance(res, str):
        assert Formatter(**kwargs)(test) == res
    else:
        with pytest.raises(res):
            Formatter(**kwargs)(test)

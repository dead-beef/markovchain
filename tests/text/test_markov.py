from unittest.mock import Mock
import pytest

from markovchain.text import MarkovText
from markovchain.scanner import Scanner, CharScanner


def test_markov_text_data(mocker):
    mock = mocker.patch('markovchain.Markov.data', return_value=1)
    markov = MarkovText()
    assert markov.data([1, 2], True) == 1
    mock.assert_called_once_with([1, 2], True)

@pytest.mark.parametrize('test,scanner,join_with', [
    (['1', '2', '3'], CharScanner(), ''),
    (['1', '2', '3'], None, ' ')
])
def test_markov_text_format(test, scanner, join_with):
    fmt = Mock(return_value=2)
    markov = MarkovText(scanner=scanner, formatter=fmt)
    assert markov.format(test) == 2
    fmt.assert_called_with(join_with.join(test))

@pytest.mark.parametrize('data,args,res', [
    ([], (), KeyError),
    ('xy', (), ['x', 'y']),
    ('xy', (None, None, 'z'), ['z']),
    ('xy', (None, None, 'xyx'), ['xyx', 'y']),
    ('xy', (None, None, (x for x in 'xyx')), ['x', 'y', 'x', 'y']),
    ('xxxxx', (2,), ['x', 'x']),
    ('xxxxx', (-10,), []),
    ('xxxxx', (0,), [])
])
def test_markov_text_generate(mocker, data, args, res):
    fmt = mocker.patch(
        'markovchain.MarkovText.format',
        wraps=list
    )
    markov = MarkovText(scanner=Scanner(lambda x: x))
    markov.data(data)
    if isinstance(res, type):
        with pytest.raises(res):
            markov(*args)
    else:
        assert markov(*args) == res
        assert fmt.call_count == 1

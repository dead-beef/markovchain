from unittest.mock import Mock
import pytest

from markovchain.text import MarkovText, ReplyMode
from markovchain.scanner import Scanner
from markovchain.parser import Parser
from markovchain.storage import JsonStorage


def test_markov_text_data(mocker):
    mock = mocker.patch('markovchain.Markov.data', return_value=1)
    markov = MarkovText()
    assert markov.data([1, 2], True) == 1
    mock.assert_called_once_with([1, 2], True)

@pytest.mark.parametrize('test,join_with', [
    (['1', '2', '3'], ''),
    (['1', '2', '3'], ' ')
])
def test_markov_text_format(test, join_with):
    fmt = Mock(return_value=2)
    markov = MarkovText(formatter=fmt)
    markov.storage.state_separator = join_with
    assert markov.format(test) == 2
    fmt.assert_called_with(join_with.join(test))

@pytest.mark.parametrize('ss,data,args,res', [
    (1, [], (), KeyError),
    (1, 'xy', (), ['x', 'y']),
    (1, 'xy', (None, None, 'z'), ['z']),
    (1, 'xy', (None, None, 'xyx'), ['xyx', 'y']),
    (1, 'xy', (None, None, 'xyx', ReplyMode.START), ['xyx']),
    (1, 'zxy', (None, None, 'yxy', ReplyMode.START), ['z', 'x', 'yxy']),
    (2, ['u', 'x', 'xz', 'v'], (None, None, 'y z w', ReplyMode.REPLY), ['u', 'x xz', 'v']),
    (1, 'xxxxx', (2,), ['x', 'x']),
    (1, 'xxxxx', (-10,), []),
    (1, 'xxxxx', (0,), [])
])
def test_markov_text_generate(mocker, ss, data, args, res):
    fmt = mocker.patch(
        'markovchain.text.MarkovText.format',
        wraps=list
    )
    markov = MarkovText(
        parser=Parser(state_sizes=[ss]),
        scanner=Scanner(lambda x: x),
        storage=JsonStorage(backward=True)
    )
    markov.data(data)
    if isinstance(res, type):
        with pytest.raises(res):
            markov(*args)
    else:
        assert markov(*args) == res
        assert fmt.call_count == 1
